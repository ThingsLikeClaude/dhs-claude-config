# Header & Navigation Redesign 구현 계획

## Context

SIFT 앱의 Sidebar + TitleBar 구조가 좌우 균형을 망가뜨리고, 타이틀바와 콘텐츠의 분리감이 강하며, 로고가 중복되는 문제가 있다. 인터뷰(04-header-nav-redesign.md)에서 13개 Q&A를 통해 사이드바 제거 + 통합 헤더 + 글래스모피즘 설정 패널로 재설계하기로 결정.

## 목표 레이아웃

```
┌──────────────────────────────────────────────────────┐
│ SIFT                    ···드래그···          [—][✕]  │  Row1: TitleBar
│ [📊][🎒][📜][📈]              [●추적중]       [⚙️]   │  Row2: NavBar
├──── 동일 배경(bg-bg-surface), 구분선 없음 ─────────────┤
│                                                      │
│                     콘텐츠 (전체 너비)                  │
│                                                      │
├──────────────────────────────────────────────────────┤
│ Footer (LogStatus)                                   │
└──────────────────────────────────────────────────────┘

⚙️ → 오른쪽 글래스모피즘 패널 → "모든 설정" → 모달
```

## 구현 단계

### Step 1: TitleBar 단순화
**파일:** `src/ui/layout/TitleBar.tsx`

변경:
- 플레이어 정보 제거 (센터 드래그 영역)
- 좌측: "SIFT" 로고 텍스트 (기존 "S" → "SIFT")
- 최대화 버튼 제거 (Square 아이콘 + onClick 삭제)
- 높이 h-9 유지, border-b 제거 (NavBar와 통합 시각)
- 전체 배경 `bg-bg-surface` 유지

### Step 2: NavBar 신규 생성
**파일:** `src/ui/layout/NavBar.tsx` (신규)

구조:
```tsx
<nav className="flex h-9 items-center bg-bg-surface border-b border-border-default px-2">
  {/* 좌: 탭 버튼들 */}
  <div className="flex items-center gap-1">
    {MAIN_TABS.map(tab => <TabButton ... />)}
  </div>

  {/* 우: 상태 인디케이터 + 설정 버튼 */}
  <div className="ml-auto flex items-center gap-2">
    <StatusIndicator />
    <SettingsButton onClick={openPanel} />
  </div>
</nav>
```

탭 정의 (settings 제외):
```typescript
const MAIN_TABS = [
  { id: 'farming', icon: LayoutDashboard, i18nKey: 'navbar.dashboard' },
  { id: 'inventory', icon: Backpack, i18nKey: 'navbar.inventory' },
  { id: 'history', icon: Clock, i18nKey: 'navbar.history', disabled: true },
  { id: 'prices', icon: LineChart, i18nKey: 'navbar.prices', disabled: true },
];
```

반응형:
- 기본: 아이콘 + 텍스트
- `@container` 또는 `min-width` 체크로 좁으면 아이콘만 표시
- Tailwind `hidden` + breakpoint 또는 container query 활용

### Step 3: AppShell 구조 변경
**파일:** `src/ui/layout/AppShell.tsx`

변경:
- `flex-row` → `flex-col` (사이드바 제거로 수직 레이아웃)
- Sidebar import/렌더링 제거
- NavBar import 추가
- 설정 패널/모달 상태 관리 추가

```tsx
<div className="flex h-screen flex-col bg-bg-base text-text-primary">
  <TitleBar />
  <NavBar activeTab={activeTab} onTabChange={setActiveTab} />
  <main className="flex-1 overflow-hidden">
    {/* 기존 탭별 콘텐츠 동일 */}
  </main>
  <footer className="shrink-0"><LogStatus ... /></footer>
  <SettingsPanel />
  <ReportOverlay ... />
</div>
```

settings 탭 콘텐츠:
- `activeTab === 'settings'` 분기 제거 (settings는 이제 모달)
- settings 관련 콘텐츠는 SettingsModal로 이동

### Step 4: SettingsPanel 글래스모피즘 오버레이
**파일:** `src/ui/layout/SettingsPanel.tsx` (신규)

구조:
- 오른쪽에서 슬라이드 인 (`transform: translateX(100%) → 0`)
- 백드롭: `bg-black/50` (클릭 시 닫힘)
- 패널: `bg-[rgba(10,10,15,0.85)] backdrop-blur-[12px]` + `border-l border-white/10`
- 너비: `w-64` (256px)
- 트랜지션: `duration-200 ease-out`
- ESC 키 닫힘: `useEffect` with keydown listener

토글 항목 4개:
```
[항상 위        ◉]  → window.sift.setSetting('alwaysOnTop', ...)
[클라우드 동기화  ◉]  → 미구현 placeholder
[자동 추적      ◉]  → 미구현 placeholder
[한/영 전환     ◉]  → i18n.changeLanguage(...)
```

하단: "모든 설정" 버튼 → SettingsModal 열기

reduced-motion 대응:
```css
@media (prefers-reduced-motion: reduce) {
  backdrop-filter: none;
  background: rgba(10, 10, 15, 0.95);
  transition: none;
}
```

### Step 5: SettingsModal (Placeholder)
**파일:** `src/ui/layout/SettingsModal.tsx` (신규)

- ReportOverlay와 동일한 모달 패턴 사용 (fixed inset-0 z-50)
- 내부 섹션은 placeholder로 시작
- "닫기" 버튼 + 바깥 클릭 + ESC 닫힘

### Step 6: Sidebar 삭제 + IPC 정리
**파일들:**
- `src/ui/layout/Sidebar.tsx` → 삭제
- `src/preload.ts` → `maximizeWindow()` 제거
- `src/shared/ipc-types.ts` → `SiftApi`에서 `maximizeWindow()` 제거
- `electron/ipc-handlers.ts` → `window:maximize` 핸들러 제거

### Step 7: i18n 키 추가
**파일:** `src/i18n/ko.json`

```json
"navbar": {
  "dashboard": "대시보드",
  "inventory": "인벤토리",
  "history": "히스토리",
  "prices": "시세",
  "tracking": "추적중",
  "waiting": "대기",
  "settings": "설정"
},
"settingsPanel": {
  "title": "빠른 설정",
  "alwaysOnTop": "항상 위",
  "cloudSync": "클라우드 동기화",
  "autoTracking": "자동 추적",
  "language": "한/영 전환",
  "allSettings": "모든 설정"
}
```

기존 `sidebar.*` 키는 NavBar로 대체되므로 제거 가능 (하지만 안전을 위해 유지).

## 파일 변경 요약

| 파일 | 액션 | 내용 |
|------|------|------|
| `src/ui/layout/TitleBar.tsx` | 수정 | 단순화 (플레이어정보/최대화 제거) |
| `src/ui/layout/NavBar.tsx` | **신규** | 탭 + 상태 + 설정 버튼 |
| `src/ui/layout/SettingsPanel.tsx` | **신규** | 글래스모피즘 빠른 설정 |
| `src/ui/layout/SettingsModal.tsx` | **신규** | 풀 설정 모달 (placeholder) |
| `src/ui/layout/AppShell.tsx` | 수정 | flex-col, Sidebar 제거, NavBar/Panel 추가 |
| `src/ui/layout/Sidebar.tsx` | **삭제** | 사이드바 제거 |
| `src/preload.ts` | 수정 | maximizeWindow 제거 |
| `src/shared/ipc-types.ts` | 수정 | SiftApi에서 maximizeWindow 제거 |
| `electron/ipc-handlers.ts` | 수정 | window:maximize 핸들러 제거 |
| `src/i18n/ko.json` | 수정 | navbar/settingsPanel 키 추가 |
| `src/index.css` | 수정 | 글래스모피즘 유틸리티 (필요 시) |

## 재사용할 기존 패턴

- **오버레이**: `ReportOverlay.tsx`의 `fixed inset-0 z-50 bg-black/70` + stopPropagation 패턴
- **탭 스타일**: `Sidebar.tsx`의 active/inactive/disabled 스타일 (수평으로 변환)
- **접근성**: `Sidebar.tsx`의 `role="tab"`, `aria-selected`, 키보드 핸들러
- **스토어**: `useAppStore`의 `activeTab`/`setActiveTab` 그대로 사용
- **i18n**: `useTranslation()` + t() 패턴
- **아이콘**: Lucide React (LayoutDashboard, Backpack, Clock, LineChart, Settings)

## 리스크 & 대응

| 리스크 | 영향 | 대응 |
|--------|------|------|
| 400px에서 탭 4개 + 우측 요소 빡빡 | 레이아웃 깨짐 | 아이콘 전용 모드, gap 축소, 텍스트 숨기기 |
| blur() GPU 부담 | 게임 프레임 드롭 | rgba 높은 opacity 기본, blur는 조건부 |
| settings 탭 제거 시 기존 코드 참조 | 타입 에러 | TabId 타입은 유지, AppShell 분기만 제거 |
| Sidebar 삭제 시 import 누락 | 빌드 실패 | tsc --noEmit으로 즉시 검증 |

## 검증 방법

1. `npx tsc --noEmit` — 타입 에러 없음 확인
2. `pnpm dev` — 앱 실행 후 시각적 확인
   - 통합 헤더 2줄 표시 확인
   - 탭 클릭으로 페이지 전환 확인
   - ⚙️ 클릭 → 글래스모피즘 패널 슬라이드 확인
   - 패널 바깥 클릭 / ESC로 닫힘 확인
   - "모든 설정" 클릭 → 모달 열림 확인
   - 최소화/닫기 버튼 동작 확인
3. 창 크기 400px으로 축소 → 아이콘 전용 모드 확인
4. 키보드 Tab 키로 탭 네비게이션 확인
