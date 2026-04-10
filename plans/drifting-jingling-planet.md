# 데이터시트 페이지 재설계 계획

## Context

현재 데이터시트 페이지는 품의서 아이템 + 영수증을 병합하여 19개 컬럼으로 보여주는 **읽기 전용** 테이블.
엑셀 원본은 26개 컬럼으로 정보가 과다. 엑셀의 가장 큰 문제는 **실시간 연동 불가**.

**목표**: 12~14개 핵심 컬럼으로 압축 + 인라인 상태 변경 + 확인 체크 + 사이드 패널 미리보기.
구매팀과 경영진이 **같은 뷰**를 공유하며, 필터만 다르게 사용.
핵심 워크플로우: **품목 진행 상태 추적** (승인/발주/입고 등 모든 상태 전이).

---

## Deep Interview 결과

| 항목 | 답변 |
|------|------|
| 주 사용자 | 구매팀 + 경영진 (같은 뷰, 필터만 다르게) |
| 핵심 페인 | 엑셀 실시간 연동 불가 |
| 핵심 워크플로우 | 특정 품목의 진행 상태 추적 |
| 상태 표시 | 컬러 듣 인디케이터 (StatusBadge) |
| 상태 전이 | 복합적 (모든 상태 전이 필요) |
| 상세 보기 | 사이드 패널 미리보기 |
| 역할별 뷰 | 같은 뷰, 필터만 다르게 |

---

## 핵심 컬럼 구성 (13개)

| # | 컬럼 | 키 | 너비 | 비고 |
|---|------|----|------|------|
| 1 | 유형 | type | 60 | 품의/영수 뱃지 |
| 2 | 상태 | status | 90 | InlineStatusChanger (품의) / 확인 체크 (영수증) |
| 3 | 날짜 | date | 90 | 품의일/발행일 |
| 4 | 품의번호 | doc_number | 100 | 클릭시 사이드 패널 열기 |
| 5 | 고객사·설비 | client_equipment | 140 | `{고객사} · {설비명}` 통합 1열 |
| 6 | 카테고리 | category | 120 | `대 > 중 > 소` breadcrumb 형식 통합 |
| 7 | 규격 | specification | 180 | 주요 식별 정보 |
| 8 | 업체 | supplier_name | 120 | |
| 9 | 담당 | user_name | 70 | 팀·담당 통합 (tooltip에 팀 표시) |
| 10 | 견적가액 | estimate_amount | 90 | 품의만, 영수증은 `-` |
| 11 | 공급가액 | supply_amount | 90 | |
| 12 | 총액 | total_amount | 100 | 볼드 |
| 13 | 노트 | notes | 60 | 아이콘 + tooltip, 있을 때만 표시 |

**압축 전략**:
- 고객사 + 설비 → 1열 (`·` 구분)
- 대/중/소분류 3열 → 1열 (breadcrumb `>` 구분)
- 팀 + 담당 → 담당 1열 (팀은 tooltip)
- 세액, 차액, 백분율, 카드번호 → 제거 (필요시 2단계에서 컬럼 피커로 복원)

---

## 상호작용 기능

### 1. 인라인 상태 변경 (품의서)
- 기존 `InlineStatusChanger` 컴포넌트 재사용
- 데이터시트에서 직접 모든 상태 전이 가능 (승인, 반려, 발주, 입고 등)
- `procurement_id`와 `status` 필드가 이미 DatasheetRow에 존재

### 2. 확인 체크 (영수증)
- 영수증 행에 체크박스 표시
- 체크 시 서버 액션 호출 (receipts.is_confirmed 토글)
- 낙관적 업데이트로 즉시 UI 반영
- **DB 변경 불필요**: receipts 테이블에 `is_confirmed`, `confirmed_by`, `confirmed_at` 이미 존재

### 3. 사이드 패널 미리보기
- 행 클릭 시 오른쪽 사이드 패널 열림 (페이지 이탈 없음)
- 품의서: procurement 상세 (전체 품목 목록, 상태 이력, 거래명세서 정보)
- 영수증: receipt 상세 (금액, 카드번호, 첨부파일 등 전체 정보)
- DataGrid의 `activeRowId` + `onActiveRowChange` 기존 기능 활용
- 기존 `ProcurementModal` 컴포넌트 참고하여 패널 구성

---

## 구현 순서

### Step 1: 타입 + 서버 액션 수정
**파일**: `frontend/src/types/datasheet.types.ts`, `frontend/src/app/actions/datasheet.ts`
- DatasheetRow에 `notes`, `is_confirmed`, `user_id` 필드 추가
- 불필요 필드(difference, percentage) 유지하되 컬럼에서만 제거
- 서버 쿼리에 notes, is_confirmed 포함
- 영수증 확인 토글 서버 액션 `toggleReceiptConfirmedAction` 추가

### Step 2: React Query 전환
**파일**: `frontend/src/lib/queries/datasheet.ts`, `frontend/src/app/datasheet/page.tsx`
- useState 기반 → React Query 전환 (품의서 페이지 패턴)
- `useDatasheet(filters)` 훅 생성
- page.tsx에 `prefetchQuery` + `HydrationBoundary` 추가
- Supabase Realtime 구독 (procurements, receipts, procurement_statements 변경 감지)

### Step 3: DatasheetClient 전면 재작성 (/ui-ux-pro-max 스킬 사용)
**파일**: `frontend/src/app/datasheet/DatasheetClient.tsx`
- 13개 컬럼 정의 (통합 셀 렌더러)
- InlineStatusChanger 연동 (import 경로 조정)
- 영수증 확인 체크박스 셀
- 고객사·설비 통합 셀, 카테고리 breadcrumb 셀
- useSlicerUrl 적용 (URL 기반 필터 동기화)
- 상태 필터 추가 (SlicerBar에 status multiSelect)

### Step 4: 사이드 패널 구현
**파일**: `frontend/src/app/datasheet/DatasheetDetailPanel.tsx` (신규)
- 품의서 상세: procurement 정보 + 품목 목록 + 거래명세서
- 영수증 상세: 전체 정보 (카드번호, 첨부 등)
- DataGrid `activeRowId` 연동
- 닫기/ESC 지원, 반응형 (모바일에서는 전체 너비)

### Step 5: UI 마감
- 합계 섹션 유지
- 페이지네이션 유지
- 빈 상태, 로딩 스켈레톤 유지

---

## 수정/생성 대상 파일

| 파일 | 상태 | 변경 내용 |
|------|------|-----------|
| `frontend/src/types/datasheet.types.ts` | 수정 | notes, is_confirmed, user_id 필드 추가 |
| `frontend/src/app/actions/datasheet.ts` | 수정 | 쿼리 확장 + 영수증 확인 토글 액션 추가 |
| `frontend/src/app/datasheet/DatasheetClient.tsx` | **전면 재작성** | 컬럼 재정의, React Query, 상호작용, 사이드 패널 연동 |
| `frontend/src/app/datasheet/page.tsx` | 수정 | React Query prefetch 추가 |
| `frontend/src/app/datasheet/DatasheetDetailPanel.tsx` | **신규** | 사이드 패널 미리보기 컴포넌트 |
| `frontend/src/lib/queries/datasheet.ts` | 수정 | useDatasheet 훅, Realtime 구독 |

## 재사용 컴포넌트 (새로 만들지 않음)

- `InlineStatusChanger` → `frontend/src/app/procurements/InlineStatusChanger.tsx`
- `StatusBadge` → `frontend/src/components/shared/StatusBadge.tsx`
- `DataGrid` (activeRowId 기능 포함) → `frontend/src/components/data-grid/`
- `SlicerBar` + `useSlicerUrl` → `frontend/src/components/slicer/`
- `SearchInput`, `FilterTabs`, `PageHeader` → `frontend/src/components/shared/`
- `ProcurementModal` (패널 참고) → `frontend/src/components/procurement/ProcurementModal.tsx`

---

## 검증 방법

1. `npx tsc --noEmit` — 타입 에러 없음 확인
2. 브라우저에서 `/datasheet` 접속하여 확인:
   - 13개 컬럼 정상 렌더링
   - 품의 행: 상태 뱃지 클릭 → 상태 전이 Popover 동작
   - 영수증 행: 확인 체크박스 토글 동작
   - 행 클릭 → 사이드 패널 열림 (품의/영수증 상세)
   - 필터(유형/팀/기간/상태) 정상 동작
   - Supabase Realtime 동기화 (다른 탭에서 변경 시 반영)
   - 가상 스크롤, 페이지네이션 유지
3. Playwright로 UI 스냅샷 검증 (구현 후)
