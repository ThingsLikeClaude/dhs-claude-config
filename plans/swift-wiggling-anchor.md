# 대시보드 헤더 탭 전환 기능 구현 계획

## Context

현재 대시보드 페이지는 `PageHeader` (단순 텍스트)를 사용한다.
헤더를 품의서 페이지의 Hero Card 패턴으로 전환하고, 탭 인프라를 구축한다.
현재는 "프로젝트 현황" 탭 1개만 두고, 이후 점진적으로 탭을 추가할 예정.

## 변경 사항

### 1. 신규: `frontend/src/app/dashboard/DashboardShell.tsx` (~40줄)

Hero Card 패널 + shadcn Tabs 클라이언트 컴포넌트.

```
┌──────────────────────────────────────────────────┐
│  대시보드                       [프로젝트 현황]    │  ← Hero Card 헤더
└──────────────────────────────────────────────────┘
  (탭 콘텐츠: ProjectDashboard)
```

- 외부: `rounded-md border border-border/40 shrink-0` (품의서 Hero Card 패턴)
- 헤더: `bg-muted/20 border-b border-border/30` + 타이틀 좌측 + `TabsList` 우측
- `TabsContent "project"` → `<ProjectDashboard />`
- 추후 탭 추가: `TabsTrigger` + `TabsContent` 한 쌍만 추가하면 됨

### 2. 수정: `frontend/src/app/dashboard/page.tsx` (3줄 변경)

- `PageHeader`, `ProjectDashboard` import → `DashboardShell` import으로 교체
- JSX: `<PageHeader />` + `<ProjectDashboard />` → `<DashboardShell />`

### 3. 변경 없음

- `ProjectDashboard.tsx` — 그대로 사용 (탭 콘텐츠로 들어감)
- `PageHeader.tsx` — 공유 컴포넌트, 다른 페이지에서 계속 사용

## 핵심 파일

| 파일 | 역할 |
|------|------|
| `frontend/src/app/dashboard/DashboardShell.tsx` | **신규** - Hero Card + 탭 쉘 |
| `frontend/src/app/dashboard/page.tsx` | **수정** - DashboardShell로 교체 |
| `frontend/src/components/ui/tabs.tsx` | 참조 - 기존 shadcn Tabs |
| `frontend/src/app/dashboard/ProjectDashboard.tsx` | 참조 - 탭 콘텐츠 (변경 없음) |

## 검증

1. `pnpm build` — 빌드 성공
2. 브라우저: Hero Card 패널 스타일 확인
3. "프로젝트 현황" 탭 활성 상태에서 기존 대시보드 동일 동작
4. 뷰포트 높이 채우기 (스크롤바 없음) 확인
