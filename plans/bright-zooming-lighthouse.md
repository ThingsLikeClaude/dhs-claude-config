# Plan: UI 4대 개선 (각진 디자인 + 편집모달 + 열고정 + 사이드바 제거)

## Context

사용자 피드백: 둥근 모서리가 게임 트래커 느낌이 안 남, 편집모드 인라인이 불편, 열 고정이 반응형에 영향받음, 오른쪽 자산 사이드바 불필요.

## 1. 둥근 모서리 제거 (각진 디자인)

**CSS 변수 변경** (`src/index.css`):
```css
--radius-sm: 1px;
--radius-md: 2px;
--radius-lg: 3px;
--radius-xl: 4px;
```

이렇게 하면 `rounded-md`를 쓰는 모든 컴포넌트가 자동으로 각져짐.
개별 파일 수정 불필요 — CSS 변수 4개만 변경.

**`widget-grid.css`**: `var(--radius-md)` 이미 사용 중이므로 자동 적용.

## 2. 편집모드를 모달로 변경

**현재**: `EditModeBar`가 AppHeader에 인라인 표시, 위젯 위에서 직접 드래그.

**변경**: 편집 버튼 클릭 시 풀스크린 모달이 열리고, 모달 안에서:
- 섹션 1: Stat 카드 선택 (체크박스 그리드 + 열 수 선택)
- 섹션 2: 콘텐츠 위젯 선택 (체크박스 리스트)
- 섹션 3: 프리셋 선택
- 하단: 완료 버튼

**파일 변경**:
- **새 파일**: `src/ui/widgets/EditModal.tsx` — 편집 모달 컴포넌트
- **수정**: `src/ui/widgets/EditModeBar.tsx` → 삭제 또는 모달 트리거로 축소
- **수정**: `src/ui/widgets/WidgetGrid.tsx` — `isDraggable`/`isResizable` 항상 false (모달에서만 편집)
- **삭제**: `src/ui/widgets/WidgetPicker.tsx` — 모달에 통합
- **삭제**: `src/ui/widgets/PresetSelector.tsx` — 모달에 통합
- **삭제**: `src/ui/widgets/StatColumnPicker.tsx` — 모달에 통합
- **수정**: `src/ui/widgets/WidgetShell.tsx` — 드래그 핸들/X 버튼 제거 (더이상 인라인 편집 없음)

**EditModal 구조**:
```tsx
<dialog> (또는 portal div)
  <header> "레이아웃 편집" + X 닫기 </header>
  <section> "통계 카드"
    열 선택: [2] [3] [4]
    14개 stat 체크박스 그리드 (현재 visible 표시)
  </section>
  <section> "위젯"
    콘텐츠 위젯 체크박스 리스트 (profit-chart, active-run, etc.)
  </section>
  <section> "프리셋"
    4개 프리셋 버튼
  </section>
  <footer> "완료" 버튼 </footer>
</dialog>
```

## 3. 열 고정을 반응형과 무관하게

**현재**: `WidgetGrid.tsx`에서 `BREAKPOINTS = { lg: 950, sm: 0 }`, `COLS = { lg: 12, sm: 6 }`.
sm에서 12→6칸이 되면서 stat 카드 w:3이 꽉 차버림.

**변경**: breakpoint를 제거하고 항상 12칸 그리드 사용.

```tsx
// WidgetGrid.tsx — Responsive → 단순 GridLayout으로 변경
const COLS = 12;
```

`react-grid-layout`에서 `Responsive` 대신 기본 `GridLayout` + `WidthProvider` 사용.
sm 레이아웃 관련 코드 모두 제거 (presets, widget-store, types).

**영향받는 파일**:
- `src/ui/widgets/WidgetGrid.tsx` — Responsive → ReactGridLayout
- `src/ui/widgets/types.ts` — `SiftBreakpoint` 타입 제거, `SiftLayouts`를 단일 배열로
- `src/store/widget-store.ts` — sm 관련 로직 제거
- `src/ui/widgets/presets.ts` — sm 레이아웃 제거

**SiftLayouts 변경**:
```ts
// Before: Record<'lg'|'sm', LayoutItem[]>
// After: readonly LayoutItem[]
export type SiftLayouts = readonly LayoutItem[];
```

## 4. 오른쪽 자산 사이드바 제거

**수정**: `src/ui/dashboard/FarmingLayout.tsx`
- `grid-cols-[1fr_300px]` → 단일 컬럼
- `InventorySidebar` import/렌더링 제거
- `InventoryBottomSheet` import/렌더링 제거
- 하단 인벤토리 버튼 제거

인벤토리는 이미 `inventory` 위젯으로 존재하므로 사이드바 없이도 접근 가능.

**삭제 가능**:
- `src/ui/dashboard/InventorySidebar.tsx`
- `src/ui/dashboard/InventoryBottomSheet.tsx`

## 구현 순서

1. **CSS 변수** (radius) — 1분, 영향범위 가장 넓지만 변경은 4줄
2. **SiftLayouts 단일화** — types.ts, widget-store.ts, presets.ts, WidgetGrid.tsx에서 sm 제거
3. **FarmingLayout 사이드바 제거** — 단순 삭제
4. **EditModal 생성 + 기존 인라인 편집 제거** — 가장 큰 변경

## 검증

1. `npx tsc --noEmit` — 타입 에러 없음
2. `pnpm dev` 실행 후:
   - 모서리가 각져 있는지 확인
   - 사이드바 없이 풀 그리드로 표시
   - 편집 버튼 → 모달 열림, stat/위젯 선택, 열 변경 동작
   - 창 크기 줄여도 열 수 고정 (12칸 유지, 카드 w 고정)
