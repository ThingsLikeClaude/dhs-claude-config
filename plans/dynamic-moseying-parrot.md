# 품의서 목록 RPC 최적화

## Context

품의서 페이지 네비게이션이 **1.6초**(487KB)로 느림. 원인: 769건 × 6 JOIN으로 items(2823), delivery_items(2812), statements(2824)까지 전부 한 번에 로드. 목록 테이블에서는 집계값(총액, 상태)만 필요한데 개별 레코드를 모두 전송 중.

**목표**: 487KB → ~50KB, 1.6초 → ~300ms

## 접근: Two-tier 데이터 로딩

- **목록 RPC**: `get_procurement_list()` — 집계된 flat 데이터 반환 (items/statements/delivery 안 포함)
- **상세 쿼리**: 행 클릭 시 1건만 기존 방식으로 fetch (즉시 ~50ms)

## 단점 커버

| 단점 | 커버 방법 |
|------|----------|
| 상세 패널 로딩 | `useProcurementDetail(activeId)` 별도 fetch — 1건이라 ~50ms |
| 엑셀 내보내기 | 이미 `/api/procurements/[id]/export`에서 개별 fetch — 변경 없음 |
| 타입 안전성 | `ProcurementListRow` 타입 정의 |
| RPC 유지보수 | 마이그레이션 파일로 관리 |

---

## 구현 단계

### 1. SQL 마이그레이션 — RPC 함수 생성

**파일**: `supabase/migrations/YYYYMMDDHHMMSS_procurement_list_rpc.sql`

```sql
CREATE OR REPLACE FUNCTION get_procurement_list()
RETURNS TABLE(
  id uuid, procurement_number text, procurement_date date,
  title text, client_name text, equipment_name text,
  status text, is_confirmed boolean, is_pre_order boolean,
  custom_filename text, notes text, created_at timestamptz,
  user_id uuid, requester_id uuid, assignee_id uuid,
  team_id uuid, project_id uuid,
  -- Flat user/team/project names
  user_name text, requester_name text, assignee_name text,
  team_name text, team_code text,
  project_name text, project_code text,
  -- Aggregated fields
  item_count int, supply_total numeric, tax_total numeric, total_amount numeric,
  estimate_total numeric,
  delivery_count int, delivery_received_count int,
  statement_count int, statement_confirmed_count int,
  -- Computed
  computed_status text, all_workflow_done boolean
)
```

- 3개 CTE: items 집계, delivery 집계, statements 집계
- `computed_status`: `getStatus()` 로직 그대로 SQL로
- `all_workflow_done`: 선발주 워크플로우 체크

### 2. 타입 추가

**파일**: `frontend/src/app/procurements/types.ts`

```typescript
export type ProcurementListRow = {
  id: string;
  procurement_number: string;
  // ... flat fields
  supply_total: number;
  tax_total: number;
  total_amount: number;
  computed_status: string;
  all_workflow_done: boolean;
  // ... user/team/project names as flat strings
};
```

### 3. 쿼리 레이어

**파일**: `frontend/src/lib/queries/procurements.ts`

- `fetchProcurementList()` — `supabase.rpc('get_procurement_list')`
- `useProcurementList()` — 목록용 React Query hook
- `useProcurementDetail(id)` — 상세 패널용 (기존 JOIN 쿼리, 1건)

**파일**: `frontend/src/app/actions/prefetch.ts`

- `prefetchProcurements()` → RPC 호출로 변경

### 4. ProcurementsClient 적응 (가장 큰 변경)

**파일**: `frontend/src/app/procurements/ProcurementsClient.tsx`

| 변경점 | Before | After |
|--------|--------|-------|
| 데이터 소스 | `useProcurements()` | `useProcurementList()` |
| 상세 패널 | `filtered.find(p => p.id)` | `useProcurementDetail(activeId)` |
| 공급가액 컬럼 | `row.items.reduce(...)` | `row.supply_total` |
| 세액 컬럼 | `row.items.reduce(...)` | `row.tax_total` |
| 총액 컬럼 | `row.items.reduce(...)` | `row.total_amount` |
| 상태 | `getStatus(p)` | `p.computed_status` |
| 워크플로우 뱃지 | `p.items?.every(...)` | `p.all_workflow_done` |
| 슬라이서 | `'team.name'`, `'requester_user.name'` | `'team_name'`, `'requester_name'` |
| InlineStatusChanger | `getStatus(procurement)` | `computedStatus` prop 추가 |

### 5. 서브 컴포넌트

- `InlineStatusChanger.tsx` — `computedStatus` prop 추가
- `MobileProcurementCard.tsx` — 동일

---

## 검증

1. **SQL 검증**: `SELECT count(*) FROM get_procurement_list()` = 769
2. **상태 일치 검증**: 임시 디버그 코드로 `computed_status` vs `getStatus()` 비교
3. **페이로드 크기**: Network 탭에서 487KB → ~50KB 확인
4. **빌드**: `pnpm build` 성공
5. **기능 테스트**: 목록 표시, 필터, 정렬, 상세 패널, 인라인 편집, 벌크 액션

## 핵심 파일

- `supabase/migrations/XXXXXX_procurement_list_rpc.sql` — 신규
- `frontend/src/app/procurements/types.ts` — 수정
- `frontend/src/lib/queries/procurements.ts` — 수정
- `frontend/src/app/actions/prefetch.ts` — 수정
- `frontend/src/app/procurements/ProcurementsClient.tsx` — 수정
- `frontend/src/app/procurements/InlineStatusChanger.tsx` — 수정
- `frontend/src/app/procurements/MobileProcurementCard.tsx` — 수정
