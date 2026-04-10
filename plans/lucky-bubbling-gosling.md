# 대시보드 요청 최적화 — debounce + abort

## Context

대시보드에서 프로젝트를 빠르게 전환하면 POST /dashboard 요청이 38건 이상 누적됨.
브라우저 동시 요청 제한(6개)으로 인해, 페이지 이동 시 새 GET 요청이 큐에 밀려 7초+ 소요.

사이드바에 `router.prefetch(href)` hover prefetch가 이미 적용되어 있고,
각 페이지도 Server prefetch + HydrationBoundary + loading.tsx 스켈레톤이 구현되어 있음.
따라서 **대시보드 요청 폭주만 해결하면 됨**.

## 변경 1: 프로젝트 선택 debounce (200ms)

**파일**: `frontend/src/app/dashboard/ProjectDashboard.tsx`

`handleProjectSelect` 콜백에 200ms debounce 적용:

```tsx
const debounceRef = useRef<ReturnType<typeof setTimeout>>();

const handleProjectSelect = useCallback((projectId: string) => {
  clearTimeout(debounceRef.current);
  debounceRef.current = setTimeout(() => {
    setSelectedProjectId(projectId);
  }, 200);
}, []);
```

- 빠르게 5개 프로젝트를 클릭해도 마지막 1개만 요청
- `keepPreviousData` 설정이 이미 있어 debounce 중에도 이전 데이터가 표시됨
- cleanup: `useEffect(() => () => clearTimeout(debounceRef.current), [])` 추가

## 변경 2: React Query queryFn에 abort signal 전달

**파일**: `frontend/src/lib/queries/dashboard.ts` (`useProjectDashboardData`)

React Query v5는 `queryFn`에 `{ signal }` 인자를 자동 전달.
queryKey가 바뀌면 이전 쿼리의 AbortController를 자동 abort.

Server Action은 abort를 직접 지원하지 않지만, signal.aborted 체크로 결과 무시 가능:

```tsx
queryFn: async ({ signal }) => {
  const result = await getProjectDashboardData(projectId!);
  if (signal?.aborted) throw new DOMException('Aborted', 'AbortError');
  if (result.error) throw new Error(result.error);
  return result.data!;
},
```

이렇게 하면 React Query가 stale 응답을 캐시에 넣지 않음.

## 변경 파일

1. `frontend/src/app/dashboard/ProjectDashboard.tsx` — debounce 추가
2. `frontend/src/lib/queries/dashboard.ts` — abort signal 체크

## 검증

1. 대시보드에서 프로젝트 빠르게 5개 이상 클릭 → dev server 로그에서 POST /dashboard 요청이 1~2개만 발생하는지 확인
2. 대시보드 조작 후 /procurements 클릭 → 이전 7초 → 2초 이내 전환
3. debounce 중 이전 프로젝트 데이터가 유지되는지 (keepPreviousData)
