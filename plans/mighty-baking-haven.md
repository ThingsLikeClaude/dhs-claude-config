# 타임라인 차트 툴팁 개선 + 기본값/누적 표시 강화

## Context

타임라인 차트의 툴팁이 품의/영수 건수를 합산으로만 보여주고, 금액이 원 단위로 표시되어 가독성이 떨어짐. 또한 "소액 제외"가 기본값이지만 사용자는 "전체"를 기본으로 원하며, 누적 라인이 점선으로 너무 약하게 표시됨.

## 변경 파일

1. `frontend/src/app/dashboard/utils/timeline.ts` — BucketData 확장 + 집계 로직
2. `frontend/src/app/dashboard/charts/AmountTimelineChart.tsx` — 툴팁 리디자인 + 누적 라인 강화
3. `frontend/src/app/dashboard/sections/TimelineChartSection.tsx` — 기본값 변경

## Step 1: BucketData 인터페이스 확장 (`timeline.ts`)

```
추가 필드:
  procCount: number      // 해당 주간 품의 건수
  receiptCount: number   // 해당 주간 영수 건수
  cumProcAmount: number  // 누적 품의 금액
  cumReceiptAmount: number // 누적 영수 금액
  cumProcCount: number   // 누적 품의 건수
  cumReceiptCount: number // 누적 영수 건수
```

## Step 2: buildTimeline 집계 로직 수정 (`timeline.ts`)

- 버킷 맵: `{ procAmt, recAmt, procCnt, recCnt }` 로 확장
- 품의 루프: `procCnt += 1`
- 영수 루프: `recCnt += 1`
- 누적 계산: cumProcAmount, cumReceiptAmount, cumProcCount, cumReceiptCount 각각 추적

## Step 3: 툴팁 금액 포맷 변경 (`timeline.ts`)

`formatKRW` 함수를 만원 단위로 변경:
- ≥ 1억: `X.X억 원`
- ≥ 1만: `X만 원` (또는 `X,XXX만 원`)
- < 1만: `X,XXX 원`

## Step 4: 툴팁 리디자인 (`AmountTimelineChart.tsx`)

```
┌─────────────────────────────┐
│ 25.1/6 ~ 1/12               │  ← 주간 범위
├─────────────────────────────┤
│ ■ 품의  3건    4,200만 원   │  ← 인디고 dot
│ ■ 영수  2건    1,800만 원   │  ← 에메랄드 dot
│ 합계    5건    6,000만 원   │  ← bold
├─────────────────────────────┤
│ 누적 품의  12건  1.2억 원   │
│ 누적 영수   8건  8,400만 원 │
│ 누적 합계  20건  2.0억 원   │  ← bold
└─────────────────────────────┘
```

## Step 5: 기본값 + 토글 순서 변경 (`TimelineChartSection.tsx`)

- `useState(false)` → `useState(true)` (전체 보기가 기본)
- 세그먼트 컨트롤 버튼 순서: "전체" → "소액 제외" (전체가 왼쪽/첫번째)

## Step 6: 누적 라인 시각적 강화 (`AmountTimelineChart.tsx`)

- 점선(`strokeDasharray="4 2"`) → 실선
- `strokeWidth: 1.5` → `2`
- `dot: false` → 작은 dot 표시 (`dot={{ r: 2 }}`)
- 누적 Y축: `hide` 제거하고 오른쪽에 축 라벨 표시

## 검증

1. `tsc --noEmit` — 타입 에러 없음 확인
2. 브라우저에서 차트 호버 → 툴팁에 품의/영수 건수·금액 분리 표시 확인
3. 누적 라인이 바와 동등한 시각적 존재감으로 표시되는지 확인
4. 페이지 진입 시 "전체" 모드가 기본 선택인지 확인
