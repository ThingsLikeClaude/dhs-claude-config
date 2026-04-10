# Sidebar 전면 재설계 Plan

## Context

현재 Ordify 사이드바는 UX 분석 결과 정보 아키텍처(4/10), 스케일/밀도(5/10), 시각 계층(5/10), 검색바(3/10) 등 대부분 영역에서 개선이 필요. 유저 프로필 영역(8/10)만 양호. Linear 스타일로 전면 재설계하여 v3 디자인 가이드("Linear/Vercel 수준")에 맞춘다.

### 디자인 결정사항
- **스타일**: Linear — 불투명 배경, 미니멀 아이콘+텍스트, 섹션 여백 구분
- **Collapsed**: 유지 + Tooltip 추가, 마스터 접근 개선
- **검색**: 아이콘 버튼으로 축소 (CommandPalette 활용)

---

## 변경 파일

| 파일 | 변경 내용 |
|------|-----------|
| `frontend/src/components/layout/Sidebar.tsx` | **전면 재작성** |
| `frontend/src/components/layout/sectionConfig.ts` | 정보 아키텍처 재구조화 |
| `frontend/src/components/layout/MainLayout.tsx` | 사이드바 너비 토큰화 |

---

## Phase 1: 정보 아키텍처 재구조화

### sectionConfig.ts 변경

**Before** (현재):
```
알림 (독립)
경영지원 → 대시보드
구매관리 → 품의서, 입고예정, 영수증, 거래명세서, 데이터시트, 마스터▸
팀관리 → Coming Soon
기타 → 설정, 사용자관리
```

**After** (Linear 스타일):
```
GENERAL
  대시보드
  알림

구매관리
  품의서
  입고예정
  영수증
  거래명세서
  데이터시트

마스터
  업체
  팀
  고객사
  프로젝트
  설비

───── (separator) ─────
설정
사용자 관리 (admin only)
```

핵심 변경:
- 대시보드를 최상단 "General" 그룹으로 승격
- 알림을 General 아래로 이동 (독립 → 소속 부여)
- 마스터를 별도 섹션으로 분리 (드롭다운 제거)
- "팀관리 Coming Soon" 제거
- 설정/사용자관리를 하단 유틸리티 영역으로 이동 (separator 아래)

---

## Phase 2: Sidebar.tsx 전면 재작성

### 2.1 배경 — 글래스모피즘 → 불투명

```diff
- bg-white/60 dark:bg-zinc-950/60 backdrop-blur-2xl backdrop-saturate-150
- border-r border-white/50 dark:border-white/10
- shadow-[4px_0_24px_-2px_rgba(0,0,0,0.06)]
+ bg-sidebar border-r border-sidebar-border
```

`--color-sidebar` 토큰 활용 (globals.css에 이미 정의됨).

### 2.2 로고 — OrdifyLogo 컴포넌트 재사용

```diff
- <span className="text-[26px] font-bold tracking-tight">Ordify</span>
- <span className="text-[10px] text-muted-foreground/40">by STALAB</span>
+ <OrdifyLogo /> (기존 컴포넌트 활용)
```

Collapsed 시 "O" 대신 `<OrdifyLogo size="sm" />` 사용.

### 2.3 검색 → 아이콘 버튼

검색바를 로고 오른쪽에 작은 아이콘 버튼으로:

```tsx
// 로고 영역 우측
<button onClick={onCommandOpen} title="검색 (Ctrl+K)">
  <Search className="size-4" />
</button>
```

Collapsed 시에도 동일한 아이콘 유지.

### 2.4 아이콘 크기 + 아이템 높이

```diff
- size-[16px]     →  size-[18px]   (아이콘)
- py-[7px]        →  py-2          (8px, 4px 그리드 정합)
- gap-2.5         →  gap-3         (12px)
```

아이템 총 높이: 18px(아이콘) + 16px(패딩) + line-height ≈ 36px (터치 친화적)

### 2.5 Active 상태 — 단순화

```diff
- bg-white/50 dark:bg-primary/40 text-primary dark:text-white
-   font-medium dark:font-semibold shadow-[...] backdrop-blur-sm
-   ring-1 ring-black/[0.04] dark:ring-primary/25
+ bg-sidebar-accent text-sidebar-accent-foreground font-medium
```

비활성: `text-sidebar-foreground/70` → hover: `text-sidebar-foreground bg-sidebar-accent/50`

### 2.6 섹션 라벨

```diff
- text-[11px] font-semibold uppercase tracking-wider text-foreground/45
+ text-[11px] font-medium text-sidebar-muted tracking-wide
```

`uppercase` 제거 (한글에 무의미).

### 2.7 하단 유틸리티 (설정)

설정/사용자관리를 nav 스크롤 영역이 아닌 하단 고정 영역으로:

```
  ...nav items...

  ─── separator ───
  설정              ← 하단 고정
  사용자 관리        ← admin only
├──────────────────┤
│ [Avatar] 이름  ⋯ │  ← 유저 프로필 (기존 유지)
└──────────────────┘
```

### 2.8 알림 뱃지

```diff
- <span className="text-[11px] text-foreground/40 tabular-nums">2</span>
+ <Badge variant="secondary" className="h-5 min-w-5 px-1 text-[11px]">2</Badge>
```

또는 작은 원형 숫자 뱃지로 가시성 확보.

### 2.9 Collapsed 모드 개선

- **Tooltip 추가**: 모든 아이콘에 shadcn Tooltip 래핑
- **마스터 접근**: Collapsed 시 Database 아이콘 클릭 → DropdownMenu로 하위 5개 표시
- **섹션 구분**: `h-px` → `Separator` 컴포넌트 사용
- **collapse 버튼**: hover 시만 보이는 것 유지 (현재 UX OK)

### 2.10 유저 프로필 — 미세 개선만

- MoreHorizontal 버튼 탭 타겟: `p-1` → `p-1.5` (32px 확보)
- 관리자모드 뱃지: `destructive` → `default` + Shield 아이콘
- 기존 DropdownMenu 구조 유지

---

## Phase 3: MainLayout.tsx 조정

```diff
- collapsed ? 'w-14' : 'w-[220px]'
+ collapsed ? 'w-[52px]' : 'w-[220px]'
```

52px = 아이콘 18px + padding 34px로 더 자연스러운 collapsed 너비.

---

## 구현 순서

1. `sectionConfig.ts` — 새 구조 정의
2. `Sidebar.tsx` — 전면 재작성 (위 Phase 2 전체)
3. `MainLayout.tsx` — 너비 조정
4. 브라우저에서 Light/Dark 모드 모두 확인

## 검증

1. `tsc --noEmit` — 타입 에러 없음
2. 브라우저에서 http://localhost:6000 확인:
   - Light/Dark 모드 전환
   - Collapsed/Expanded 전환
   - 각 네비 아이템 클릭 → 활성 상태
   - 마스터 Collapsed 접근
   - Tooltip 표시
   - 유저 메뉴 DropdownMenu
   - 모바일 Sheet 동작
