# Plan: MetricsGrid를 TorchTracker 스타일로 계승

## Context

현재 SIFT 대시보드의 MetricsGrid가 플랫 텍스트 8개 나열이라 밋밋함.
TorchTracker의 대시보드 섹션(colored time cards + perf rows + gradient dividers)을
SIFT에 맞게 계승하여 시각적 완성도를 높인다.

**범위**: MetricsGrid + DashboardPage divider 스타일만. NavBar/탭/차트는 그대로.

## TorchTracker 원본 구조 (참고)

```
T시간측정 ▶
[총플레이시간(밝은)] [맵핑시간(핑크)] [평균수술(어두운)] [수술횟수(어두운)]
──── gradient divider ────
[██ 분당평균  시간당평균 ██ (흰배경)]  [런횟수] [평균런시간]
[██ 분당평균  시간당평균 ██ (핑크)]    [총입장비] [총순수익]
```

## SIFT 적용 설계

### 전체 레이아웃 (MetricsGrid 영역)

```
──── gradient divider ──── (InfoHeader ↔ Metrics 구분)
T 시간측정  ▶ ⏸
[파밍시간] [총시간] [판당평균] [판수]          ← colored time cards
──── gradient divider ────
[██ 순수익    시급(총)  ██  흰배경/검은글씨]   ← perf-row total
[██ 입장비   시급(파밍) ██  핑크배경/흰글씨]   ← perf-row farming
──── gradient divider ────
▶ 재생중     ─────────────────  [정산]        ← timer controls
```

### Step 1: Gradient Divider 컴포넌트

`src/ui/components/GradientDivider.tsx` (신규)

```tsx
export const GradientDivider = () => (
  <div className="h-px mx-3 my-1"
    style={{ background: 'linear-gradient(to right, rgb(var(--border-base)), transparent)' }}
  />
);
```

### Step 2: Time Cards 섹션 (4개 colored boxes)

TorchTracker의 `.time-card` 패턴을 React로:

| 카드 | 배경색 | 글자색 |
|---|---|---|
| 파밍시간 | `bg-bg-elevated` (#0f3460) | white |
| 총시간 | `bg-bg-elevated` | white |
| 판당평균 | `bg-bg-elevated` | white |
| 판수 | `bg-bg-elevated` | white |

- 각 카드: `rounded px-3 py-1.5`, label(0.8rem, bold, opacity-65) 위 + value(0.9rem, bold) 아래
- 레이블과 값이 같은 행(가로 배치, 넓을 때) or 세로 배치(좁을 때)
- 섹션 헤더: "T 시간측정" + Play/Pause 버튼 (현재 timer controls에서 분리)

### Step 3: Perf Rows (2개 colored bars)

TorchTracker의 `.perf-row` 패턴:

| 행 | 배경 | 내용 |
|---|---|---|
| 총 (total) | `rgba(255,255,255,0.87)` 흰색 | 순수익 \| 시급(총) |
| 파밍 (mapping) | `rgba(233,69,96,0.87)` 핑크 | 입장비 \| 시급(파밍) |

- 각 행: `rounded h-10 px-3 flex items-center`
- 내부에 perf-card 2개: label(작은, 위) + value(큰, bold, 아래)
- 총 행: 검은 글씨, 파밍 행: 흰 글씨

### Step 4: Timer Controls 정리

- Play/Pause 버튼을 Step 2 헤더로 이동
- Settle 버튼만 하단에 남기거나 gradient divider 아래 배치

### Step 5: DashboardPage에 divider 삽입

InfoHeader와 MetricsGrid 사이, 차트 위에 `<GradientDivider />` 삽입.
기존 `border-t` 제거.

## 수정 파일 목록

| 파일 | 변경 |
|---|---|
| `src/ui/components/GradientDivider.tsx` | **신규** — gradient divider |
| `src/ui/dashboard/MetricsGrid.tsx` | **대폭 변경** — time cards + perf rows 구조로 |
| `src/ui/dashboard/DashboardPage.tsx` | divider 삽입 |

## 검증

1. `npx tsc --noEmit` — 타입 에러 없음
2. 앱 실행하여 시각적 확인:
   - Time cards가 네이비 배경으로 표시되는지
   - Perf row 총이 흰 배경인지
   - Perf row 파밍이 핑크 배경인지
   - Gradient divider가 왼→오 fade인지
