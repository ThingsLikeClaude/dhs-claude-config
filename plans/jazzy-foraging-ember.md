# Performance Optimization + Dashboard Skeleton 재설계

## Context
Ordify가 Vercel에 배포된 상태에서 페이지 진입 시 초기 데이터 로딩이 느림.
- 품의서: `get_procurement_list()` RPC가 769행/905KB를 한번에 반환 (서버 prefetch)
- Vercel cold start(1~3초) + 해외 레이턴시
- 대시보드 스켈레톤이 실제 레이아웃과 불일치

## 변경 사항 (4개)

### 1. 품의서 RPC 날짜 필터 (가장 큰 효과)
**파일들**:
- `supabase/migrations/새파일` — RPC에 `p_start_date date DEFAULT NULL` 파라미터 추가
- `frontend/src/app/actions/prefetch.ts` — prefetch 시 6개월 전 날짜 전달
- `frontend/src/lib/queries/procurements.ts` — 훅에 날짜 파라미터 추가, queryKey에 포함
- `frontend/src/app/procurements/ProcurementsClient.tsx` — "전체 보기" 토글 추가

### 2. Vercel 서울 리전 설정
**파일**: `frontend/vercel.json` (신규 생성)
- `"regions": ["icn1"]` → Serverless Function 서울 실행

### 3. 대시보드 쿼리 병렬화 (프로젝트 선택 후)
**파일**: `frontend/src/app/actions/dashboard.ts` (`getProjectDashboardData`)
- Phase 1: project+equipment, financials 병렬
- Phase 2: siblings 체크
- Phase 3: procs, receipts 병렬
- Phase 4: items, delivery 병렬 (기존 유지)

### 4. 대시보드 스켈레톤 재설계
**파일**: `frontend/src/components/skeletons/DashboardSkeleton.tsx`
- DashboardShell Hero Card + 탭 반영
- CascadeChipFilter 스켈레톤
- 상단 grid [1fr_2fr] + 하단 grid [14fr_5fr_5fr_5fr] 실제 레이아웃 반영

## 검증
1. `tsc --noEmit` 타입 체크
2. Supabase에서 RPC 날짜 파라미터 테스트
3. 브라우저에서 체감 확인
