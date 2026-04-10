# PriceSearchPalette 전체 DB 검색 전환

## Context
현재 Ctrl+F 금액/거래처 검색이 **선택된 품의서 1건의 품목만** 검색함.
`activeProcurement?.items`를 데이터 소스로 사용하기 때문.
→ 전체 DB를 대상으로 검색하도록 서버 RPC + React Query 방식으로 전환.

## 변경 파일

### 1. SQL RPC 생성 (수동 실행)
**`supabase/migrations/20260402_create_rpc_search_price_items.sql`**

```sql
CREATE OR REPLACE FUNCTION search_price_items(
  p_query TEXT,
  p_limit INT DEFAULT 50
) RETURNS TABLE(...)
```

- `procurement_items` + `procurements` + `procurement_statements` JOIN
- 숫자 입력 → `actual_supply_amount::text LIKE '%' || p_query || '%'`
- 텍스트 입력 → `supplier_name ILIKE '%' || p_query || '%'`
- `actual_supply_amount IS NOT NULL` 필터 (기존 로직 유지)
- `is_confirmed` = `procurement_statements.is_confirmed` LEFT JOIN
- 미확인 항목 우선 정렬 + LIMIT 50
- 기존 패턴: `SECURITY DEFINER`, `GRANT EXECUTE TO authenticated`

### 2. React Query 훅
**`frontend/src/lib/queries/procurements.ts`** 에 추가

```typescript
export function usePriceSearch(query: string, enabled: boolean) {
  return useQuery({
    queryKey: queryKeys.procurements.priceSearch(query),
    queryFn: () => fetchPriceSearch(query),
    enabled: enabled && query.length > 0,
    staleTime: 30_000,
    placeholderData: keepPreviousData, // 결과 전환 시 깜빡임 방지
  });
}
```

### 3. PriceSearchPalette 수정
**`frontend/src/components/shared/PriceSearchPalette.tsx`**

- 새 prop: `onQueryChange: (query: string) => void` 추가
- 디바운스 300ms (150→300) 후 `onQueryChange(debouncedQuery)` 호출
- 기존 클라이언트 필터링 로직 제거 → `data`를 그대로 렌더링
- `isLoading` prop 추가 → 로딩 스피너 표시

### 4. ProcurementsClient 수정
**`frontend/src/app/procurements/ProcurementsClient.tsx`**

- `priceSearchData` useMemo 제거
- `usePriceSearch(priceQuery, showPriceSearch)` 훅 사용
- `PriceSearchPalette`에 `onQueryChange`, `isLoading`, 서버 결과 `data` 전달

### 5. queryKeys 추가
**`frontend/src/lib/queries/queryKeys.ts`**

- `procurements.priceSearch(query)` 키 추가

## 성능 최적화 전략

| 기법 | 설명 |
|------|------|
| 디바운스 300ms | 빠른 타이핑 시 마지막 입력만 요청 |
| `placeholderData: keepPreviousData` | 새 결과 올 때까지 이전 결과 유지 (깜빡임 없음) |
| `enabled: query.length > 0` | 빈 쿼리는 요청 안 함 |
| DB 인덱스 | `actual_supply_amount`에 btree 인덱스 |
| LIMIT 50 | 결과셋 제한 |
| `staleTime: 30s` | 같은 쿼리 30초간 캐시 |

## 검증 방법
1. `tsc --noEmit` — 타입 체크
2. SQL Editor에서 RPC 직접 호출 테스트: `SELECT * FROM search_price_items('10000')`
3. UI: Ctrl+F → 금액 입력 → 전체 품의서에서 결과 반환 확인
4. 빠른 타이핑 → 마지막 결과만 표시, 깜빡임 없음 확인
