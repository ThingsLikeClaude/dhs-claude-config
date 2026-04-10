# SIFT UI 리디자인 — 재구현 계획

## Context

인터뷰 05 기반 UI 리디자인이 이전 PDCA 사이클에서 진행되었으나, **핵심 변경(위젯 시스템)이 화면에 반영되지 않았다**.

현재 상태:
- 디자인 시스템(색상/폰트/간격): ✅ 적용됨 (theme.css, fonts.css, index.css)
- AppHeader(통합 타이틀바+네비): ✅ 적용됨
- InventorySidebar(우측 2컬럼): ✅ 적용됨
- SettingsModal(5탭): ✅ 적용됨
- **위젯 시스템**: ❌ 파일만 존재하고 FarmingLayout에서 미사용
- **FarmingLayout**: 기존 MetricsGrid → ProfitChart → DashboardTabs를 그대로 렌더링

**사용자 요청**: "인터뷰 SSOT로 처음부터 다시, 아예 갈아엎어야됨"

## SSOT: 인터뷰 결정사항 (24개)

| # | 결정 | 현재 상태 | 필요 작업 |
|---|------|----------|----------|
| 1-5 | Discord 차콜 + 블루퍼플 + 시맨틱 | ✅ 완료 | 유지 |
| 6 | 한 화면 2컬럼 | ⚠️ 2컬럼은 됐으나 좌측이 old | **위젯으로 교체** |
| 7 | 반응형 950px | ✅ 완료 | 유지 |
| 8 | 메트릭스 커스터마이징 (드래그+프리셋) | ❌ WidgetGrid 고아 | **핵심: 연결** |
| 9 | 차트 위젯화 | ❌ registry만 | **위젯 연결** |
| 10 | 인벤토리 파밍 통합 | ✅ 완료 | 유지 |
| 11 | 현재 런 TT방식 | ✅ ActiveRunPanel | 유지 |
| 12 | 컨트롤 바 | ⚠️ 파일만 존재 | **위젯+header 연결** |
| 13 | 3탭 (파밍/세션/시세) | ✅ 완료 | 유지 |
| 14 | 타이틀바 통합 | ✅ AppHeader | 유지 |
| 15-16 | Freesentation + 조밀 간격 | ✅ 완료 | 유지 |
| 17-19 | 오버레이 커스텀 | ✅ 완료 | 유지 |
| 20-21 | 리포트 모달 + 캡처 | ✅ 완료 | 유지 |
| 22 | 설정 모달+탭 | ✅ 완료 | 유지 |
| 23-24 | 950x700, 최소 450 | ✅ 완료 | 유지 |

**결론**: 이미 완료된 디자인 시스템/레이아웃 구조는 유지. 핵심 작업은 **FarmingLayout을 위젯 시스템으로 전환**하는 것.

## 구현 계획

### Phase 1: FarmingLayout을 WidgetGrid로 교체

**파일**: `src/ui/dashboard/FarmingLayout.tsx`

현재:
```
InfoHeader → GradientDivider → MetricsGrid → ProfitChart → DashboardTabs
```

변경 후:
```
WidgetGrid (드래그 가능한 위젯 그리드, 모든 컴포넌트 위젯으로)
```

구체적 변경:
1. MetricsGrid, ProfitChart, DashboardTabs 직접 임포트 **제거**
2. GradientDivider 임포트 **제거** (위젯 사이 구분선 불필요)
3. InfoHeader **유지** (위젯 그리드 위에 고정)
4. `WidgetGrid` 임포트 및 렌더링
5. widget-store `loadLayout()` 초기화 호출

변경 후 FarmingLayout 구조:
```tsx
<div className="grid h-full grid-cols-1 overflow-hidden 2col:grid-cols-[1fr_300px]">
  <div className="flex min-w-0 flex-col overflow-hidden">
    <InfoHeader />
    <div className="flex min-h-0 flex-1 flex-col overflow-y-auto px-1">
      <WidgetGrid />
    </div>
    <button ... 2col:hidden>인벤토리 ▲</button>
  </div>
  <div className="hidden 2col:flex 2col:flex-col">
    <InventorySidebar />
  </div>
  <InventoryBottomSheet ... />
</div>
```

### Phase 2: 위젯 래퍼 검증 및 수정

각 위젯 래퍼가 독립 실행 가능한지 확인:

| 위젯 | 래퍼 파일 | 상태 | 작업 |
|------|----------|------|------|
| control-bar | `wrappers/ControlBarWidget.tsx` | ✅ 독립 | 유지 |
| metrics-time | `wrappers/MetricsTimeWidget.tsx` | ⚠️ 확인 | MetricsGrid의 시간부 추출 검증 |
| metrics-perf | `wrappers/MetricsPerfWidget.tsx` | ⚠️ 확인 | MetricsGrid의 수익부 추출 검증 |
| profit-chart | registry에서 직접 import | ✅ | ProfitChart 직접 사용 |
| active-run | registry에서 직접 import | ✅ | ActiveRunPanel 직접 사용 |
| recent-runs | registry에서 직접 import | ✅ | RecentRuns 직접 사용 |
| item-table | `wrappers/ItemTableWidget.tsx` | ⚠️ 확인 | ItemTable 래핑 검증 |
| inventory | `wrappers/InventoryWidget.tsx` | ⚠️ 확인 | 인라인 테이블 검증 |
| segment-summary | `wrappers/SegmentSummaryWidget.tsx` | ⚠️ 확인 | RoundList 래핑 검증 |

### Phase 3: 위젯 store 초기화 연결

**파일**: `src/ui/layout/AppShell.tsx`

widget-store의 `loadLayout()`이 앱 시작 시 호출되어야 함:
```tsx
const loadWidgetLayout = useWidgetStore((s) => s.loadLayout);
useEffect(() => { loadWidgetLayout(); }, [loadWidgetLayout]);
```

### Phase 4: 고아 파일 정리

삭제 대상 (위젯 시스템으로 대체되어 더 이상 직접 사용 안 됨):
- `src/ui/dashboard/DashboardTabs.tsx` — active-run, recent-runs, item-table 위젯으로 분리됨
- `src/ui/components/GradientDivider.tsx` — 위젯 그리드에서 불필요
- `src/ui/dashboard/DashboardPage.tsx` — 이미 고아 (FarmingLayout으로 대체됨)

**확인 후 삭제**: MetricsGrid.tsx는 MetricsTimeWidget/MetricsPerfWidget으로 대체되었는지 내용 비교 후 삭제

### Phase 5: TypeScript 검증

```bash
pnpm typecheck
```

모든 import 경로가 유효하고, 삭제된 파일에 대한 참조가 없는지 확인.

## 수정 파일 목록

| 작업 | 파일 |
|------|------|
| **수정** | `src/ui/dashboard/FarmingLayout.tsx` |
| **수정** | `src/ui/layout/AppShell.tsx` (widget store 초기화) |
| **검증** | `src/ui/widgets/wrappers/MetricsTimeWidget.tsx` |
| **검증** | `src/ui/widgets/wrappers/MetricsPerfWidget.tsx` |
| **검증** | `src/ui/widgets/wrappers/ItemTableWidget.tsx` |
| **검증** | `src/ui/widgets/wrappers/InventoryWidget.tsx` |
| **검증** | `src/ui/widgets/wrappers/SegmentSummaryWidget.tsx` |
| **삭제** | `src/ui/dashboard/DashboardTabs.tsx` |
| **삭제** | `src/ui/components/GradientDivider.tsx` |
| **삭제** | `src/ui/dashboard/DashboardPage.tsx` |
| **삭제 후보** | `src/ui/dashboard/MetricsGrid.tsx` |

## 검증 방법

1. `pnpm typecheck` — 0 errors
2. `pnpm dev` — 앱 실행 후 파밍 탭에서 위젯 그리드 렌더링 확인
3. 위젯 편집 모드 진입 (Ctrl+E) → 드래그/리사이즈 동작 확인
4. 프리셋 전환 (미니멀/기본/풀/TTD호환) 동작 확인
5. 950px 이하 반응형 레이아웃 확인
6. 위젯 추가/제거 동작 확인

## 유지하는 것 (이미 완료)

- theme.css, fonts.css, index.css (디자인 시스템)
- AppHeader.tsx (통합 헤더)
- SettingsModal.tsx (5탭 설정)
- InventorySidebar.tsx, InventoryBottomSheet.tsx
- overlay-config.ts, 오버레이 관련 변경
- widget-store.ts, WidgetGrid.tsx, WidgetShell.tsx, presets.ts, registry.ts
- ipc-types.ts 변경 (screenshot, widget-layout IPC)
- constants.ts (950x700)
