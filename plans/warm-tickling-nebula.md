# Phase 4B: UI 리디자인 + ActiveRunPanel 확장 — Implementation Plan

> **Source**: Interview 03 (50Q, 41 decisions) — `docs/interviews/03-badge-ui-redesign.md`
> **Supersedes**: Phase 4 Batch 2~4 UI 구현 (뱃지 형태 → 테이블 행 전환)

## Context

Phase 4A(Batch 1~4)에서 파이프라인 최적화, 컬러 토큰, 애니메이션을 구현했으나,
인터뷰 03에서 뱃지 UI의 근본적 문제(레이아웃 들쑥날쑥, 라벨 가독성, 정보 구성)가 확인됨.
TorchTracker/TTD 분석을 통해 메트릭 표시, ActiveRunPanel, 차트를 전면 재설계하기로 결정.

## Executive Summary

| Perspective | Content |
|-------------|---------|
| **Problem** | shields.io 뱃지가 크기 불균일하고 정보 구성이 비효율적. ActiveRunPanel이 한 줄 상태바에 불과하며 현재 런 드롭/한글 맵/계약 정보 미표시. 차트가 근사 누적 선 그래프라 유용성 낮음. 윈도우가 1200px로 게임 옆에 두기 어려움 |
| **Solution** | 3×3 컬럼 그리드 메트릭 + TorchTracker 스타일 ActiveRunPanel(드롭 테이블+최근 런) + 바 차트(판별/시간별) + 520×860 윈도우 |
| **Function/UX Effect** | 한눈에 9개 핵심 지표 비교, 현재 판 드롭 실시간 확인, 한글 맵 이름+계약 프리셋 표시, 판별 수익을 직관적 바 차트로 확인 |
| **Core Value** | "게임 옆에 놓고 쓰는 컴팩트 트래커" — TorchTracker의 정보 밀도를 Electron 네이티브 퀄리티로 |

---

## Batch 구조 (5 Batches)

### Batch 1: 윈도우 + 기반 정리
**공수**: 소 | **의존성**: 없음

| Task | File | 변경 |
|------|------|------|
| 윈도우 기본 크기 520×860, minWidth 400 | `src/shared/constants.ts` | `WINDOW_DEFAULT_WIDTH=520, HEIGHT=860, MIN_WIDTH=400` |
| DevTools 개발 모드에서만 | `electron/windows.ts` | `if (process.env.NODE_ENV === 'development')` 조건 |
| CSS max-width 제한 | `src/index.css` | `#root { max-width: 800px; margin: 0 auto; }` |
| MetricBadge/MetricGroup/MetricCell 삭제 | `src/ui/components/` | 신규 MetricGrid 컴포넌트로 교체 후 삭제 |

### Batch 2: 메트릭 그리드 재설계
**공수**: 중 | **의존성**: Batch 1

**현재**: 4그룹 × shields.io 뱃지 (flex-wrap)
**목표**: 3×3 컬럼 그리드 (시간/효율/결정), 테이블 행 스타일, 컬럼별 배경 fill

```
     시간               효율              결정
  ──────────        ──────────        ──────────
  전체  0:32:15      전체 FE/h +8,100   판수    12판
  파밍  0:28:00      파밍 FE/h +4,260   순수익  +4,230
  평균  0:02:11      분당     +71/m     입장비  -320
```

| Task | File | 변경 |
|------|------|------|
| MetricsGrid 전면 재작성 | `src/ui/dashboard/MetricsGrid.tsx` | 3컬럼 CSS Grid, 행당 라벨+값 가로 배치, 컬럼별 bg-bg-surface rounded |
| 타이머 컨트롤 + 정산 유지 | 동일 파일 하단 | Play/Pause + Settle 버튼 (현재 구현 유지) |
| i18n 키 업데이트 | `src/i18n/ko.json` | "전체"/"파밍"/"평균" 라벨, "전체 FE/h"/"파밍 FE/h" 등 |
| useAnimatedNumber 재연결 | MetricsGrid 내부 | 통화 값에 애니메이션 유지 |

**핵심 설계**:
- `display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px`
- 각 컬럼: `bg-bg-surface rounded-md p-2` — 3개 행이 같은 배경 안에
- 행: `flex justify-between` — 라벨 왼쪽, 값 오른쪽
- 전체/파밍 색상 구분: 텍스트 라벨만 (색상 보류)
- 520px 너비에서 3컬럼 150px씩 + gap = 466px (여유 있음)

### Batch 3: ActiveRunPanel 확장 + 탭 구조
**공수**: 대 | **의존성**: Batch 2

**3-A: 한글 맵 이름 + 계약 파싱**

| Task | File | 변경 |
|------|------|------|
| zones.ts 데이터 파일 생성 | `src/data/zones.ts` (NEW) | TorchTracker zones.py → TS 포팅: ZONE_NAMES(97개), LEVEL_ID_ZONES(6개), AMBIGUOUS_ZONES(3개), getZoneDisplayName() |
| 계약 이벤트 처리 연결 | `src/core/session-manager.ts` | `handleContractEvent()` 추가 — 인메모리 `currentContractSetting` 저장 |
| AppState에 contractSetting 추가 | `src/models.ts` | `readonly contractSetting: string \| null` |
| buildState()에 포함 | `src/core/session-manager.ts` | `contractSetting` 필드 추가 |
| log-parser에서 contract 이벤트 emit | `src/parser/log-parser.ts` | CONTRACT_SETTING_PATTERN 매칭 시 `{ type: 'contract', contractName }` 반환 |

**3-B: 런 단위 드롭 추적**

| Task | File | 변경 |
|------|------|------|
| runDeltaAccumulator 추가 | `src/core/session-manager.ts` | 기존 deltaAccumulator와 별도로 현재 런 전용 accumulator. 맵 진입 시 초기화, 맵 퇴장 시 리셋 |
| AppState에 currentRunDeltas 추가 | `src/models.ts` | `readonly currentRunDeltas: readonly DeltaSummary[]` |
| buildState()에 포함 | `src/core/session-manager.ts` | `currentRunDeltas: snapshotRunDeltas()` |
| app-store에서 즉시 set | `src/store/app-store.ts` | `_setFromIpc`에서 `currentRunDeltas` 추가 |

**3-C: ActiveRunPanel 재작성**

| Task | File | 변경 |
|------|------|------|
| ActiveRunPanel 전면 재작성 | `src/ui/dashboard/ActiveRunPanel.tsx` | TorchTracker 스타일: 맵이름 메인, 펄스 보더, 그라데이션(파밍/대기), 2행 헤더(맵+계약+시간 / 입장+드롭+순수익), 드롭 테이블(150px scroll) |
| 최근 런 패널 | `src/ui/dashboard/RecentRuns.tsx` (NEW) | DB runs 조회, 맵이름+순수익+시간 표시, flex-1 스크롤 |
| getRecentRuns IPC | `src/db/repository.ts` + `ipc-types.ts` + `electron/ipc-handlers.ts` | `SELECT * FROM runs WHERE segment_id = ? ORDER BY id DESC LIMIT 20` |

**3-D: 탭 구조**

| Task | File | 변경 |
|------|------|------|
| 탭 컴포넌트 | `src/ui/dashboard/DashboardTabs.tsx` (NEW) | [판 기록] / [세션 아이템] 2탭, 자동전환(맵진입→판기록, 대기→세션아이템), 수동전환 가능 |
| DashboardPage 재구성 | `src/ui/dashboard/DashboardPage.tsx` | MetricsGrid → ProfitChart → DashboardTabs |

### Batch 4: 차트 전환 (BarChart)
**공수**: 중 | **의존성**: Batch 2 (메트릭 확정 후)

| Task | File | 변경 |
|------|------|------|
| ProfitChart → BarChart | `src/ui/dashboard/ProfitChart.tsx` | LineChart → BarChart, 양수=민트/음수=코랄, 0선 없음 |
| 판별/시간별 토글 | 동일 | 우상단 세그먼트 버튼 `[판 \| 시간]` |
| 차트 높이 200px | 동일 | ResponsiveContainer height=200 |
| 판별 데이터 쿼리 | `src/db/repository.ts` | `getRoundProfits(segmentId)` — runs + item_deltas JOIN |
| 시간별 데이터 쿼리 | `src/db/repository.ts` | `getTimeProfits(segmentId, intervalMin)` — 5분 버킷 |
| IPC 채널 추가 | `ipc-types.ts` + `ipc-handlers.ts` + `preload.ts` | `chart:get-round-profits`, `chart:get-time-profits` |

### Batch 5: 정리 + 검증
**공수**: 소 | **의존성**: 전체

| Task | File | 변경 |
|------|------|------|
| 미사용 파일 삭제 | `MetricBadge.tsx`, `MetricGroup.tsx`, `MetricCell.tsx`, `MetricRow.tsx` | 삭제 |
| InfoHeader 제거 또는 통합 | `src/ui/layout/InfoHeader.tsx` | TitleBar에 플레이어 정보 이미 있으므로 삭제 검토 |
| components/index.ts 정리 | `src/ui/components/index.ts` | 삭제된 컴포넌트 export 제거 |
| i18n 미사용 키 정리 | `src/i18n/ko.json` | metricGroup.* 등 구 키 제거 |
| 컬러 audit | grep | 5계통 외 색상 없는지 확인 |
| tsc --noEmit | - | 빌드 검증 |
| 520px 레이아웃 검증 | Playwright | 최소 너비에서 깨지지 않는지 확인 |

---

## 주요 파일 변경 요약

| Action | File | Batch |
|--------|------|-------|
| **NEW** | `src/data/zones.ts` | 3-A |
| **NEW** | `src/ui/dashboard/RecentRuns.tsx` | 3-C |
| **NEW** | `src/ui/dashboard/DashboardTabs.tsx` | 3-D |
| **REWRITE** | `src/ui/dashboard/MetricsGrid.tsx` | 2 |
| **REWRITE** | `src/ui/dashboard/ActiveRunPanel.tsx` | 3-C |
| **REWRITE** | `src/ui/dashboard/ProfitChart.tsx` | 4 |
| **REWRITE** | `src/ui/dashboard/DashboardPage.tsx` | 3-D |
| **MODIFY** | `src/shared/constants.ts` | 1 |
| **MODIFY** | `electron/windows.ts` | 1 |
| **MODIFY** | `src/index.css` | 1 |
| **MODIFY** | `src/core/session-manager.ts` | 3-A, 3-B |
| **MODIFY** | `src/models.ts` | 3-A, 3-B |
| **MODIFY** | `src/store/app-store.ts` | 3-B |
| **MODIFY** | `src/parser/log-parser.ts` | 3-A |
| **MODIFY** | `src/db/repository.ts` | 3-C, 4 |
| **MODIFY** | `src/shared/ipc-types.ts` | 3-C, 4 |
| **MODIFY** | `electron/ipc-handlers.ts` | 3-C, 4 |
| **MODIFY** | `src/preload.ts` | 3-C, 4 |
| **MODIFY** | `src/i18n/ko.json` | 2, 3, 5 |
| **DELETE** | `MetricBadge.tsx`, `MetricGroup.tsx`, `MetricCell.tsx`, `MetricRow.tsx` | 5 |

---

## UX 설계 원칙 (Interview 03 확정)

1. **맵 이름이 주인공** — ActiveRunPanel에서 가장 큰 텍스트
2. **상태는 시각으로** — 텍스트("파밍 중") 대신 펄스 보더+인디케이터
3. **같은 단위는 같은 컬럼** — 시간끼리, FE끼리 세로 정렬
4. **입장비 = 일반 아이템 소모** — 별도 표시 아닌 드롭 테이블에 음수로
5. **컴팩트 우선** — 520px 기본, 게임 옆에 두는 것이 주 사용 시나리오
6. **자동 + 수동** — 탭 자동전환(맵 진입/퇴장)하되 수동 오버라이드 가능
7. **바 차트** — 판별 개별 수익이 핵심, 잭팟 시각화

---

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| 3×3 그리드가 400px에서 깨짐 | High | 400px 기준 최소 컬럼 너비 120px 확보, font-size 축소 fallback |
| zones.py 97개 맵 이름 번역 누락 | Medium | TorchTracker에서 검증된 데이터 그대로 포팅, fallback = 영문 경로 |
| 런 단위 드롭 accumulator 누수 | Medium | 맵 퇴장(hub 진입) 시 반드시 리셋, settle()에서도 리셋 |
| 자동 탭 전환이 사용자 의도와 충돌 | Low | 수동 전환 시 자동전환 일시 비활성 (5초 후 재활성) |
| 차트 IPC 쿼리 느림 | Low | 디바운스 적용, 차트 탭 활성 시에만 쿼리 |

---

## Verification

1. `tsc --noEmit` — 타입 에러 0
2. 520px 너비에서 모든 컴포넌트 깨지지 않음 확인
3. 400px 최소 너비에서 스크롤 없이 표시
4. 맵 진입 시: 한글 맵 이름 + 계약 프리셋 + 드롭 테이블 표시
5. 맵 퇴장 시: 최근 런 목록에 완료된 판 추가
6. 탭 자동전환: 맵 진입 → "판 기록", 허브 복귀 → "세션 아이템"
7. 바 차트: 판별/시간별 토글, 양수=민트 음수=코랄
8. Play/Pause: 일시정지 시 시간당 계산 멈춤 확인
9. DevTools: production 빌드에서 열리지 않음
