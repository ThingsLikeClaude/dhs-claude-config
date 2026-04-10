# CostRateDashboard 폰트 확대 + PO/환율 설정 모달 레이아웃

## Context

원가율 계산 패널의 금액/라벨 폰트가 작아서 대시보드 내 다른 패널 대비 밀도가 낮아 보임.
추가로, 디바이더 아래에 "프로젝트 정보 확인" / "PO·환율 수정" 버튼 2개를 배치하고,
모달로 PO 금액과 기준환율을 관리할 수 있게 레이아웃을 잡는다.

## 변경 파일

### 1. `frontend/src/app/dashboard/sections/CostRateDashboard.tsx`

**폰트 크기 변경:**
- 라벨 (PO, 진행 공급가액, 견적가액): `text-base` → `text-lg`
- 금액 (원화): `text-2xl` → `text-3xl` (30px)
- 프로그레스바 라벨: `text-sm` → `text-base`
- 프로그레스바 퍼센트: `text-2xl` 유지

**레이아웃 추가 — 디바이더 아래 액션 버튼 행:**
```
헤더: "원가율 계산" ──────────── [USD 1,300원]
────────────────── 디바이더 ──────────────────
[📋 프로젝트 정보]  [✏️ PO·환율 설정]   ← 새로 추가
────────────────────────────────────────────────
PO                        5,460만원 │ $42,000
진행 공급가액               1,414만원 │ $10,874
견적가액                   1,278만원 │ $9,831
────────────────── 구분선 ──────────────────
진행 원가율                          26%
[████░░░░░░░░░░░│░░░]
PO 대비 견적가액                      23%
[███░░░░░░░░░░░░░░░]
```

- 버튼 2개: `variant="outline" size="sm"` — 작은 아이콘+텍스트
- `'use client'` 추가 필요 (모달 state 관리)

### 2. `frontend/src/app/dashboard/sections/CostRateSettingsDialog.tsx` (신규)

PO·환율 설정 모달 (레이아웃만 먼저):
- shadcn Dialog 사용 (기존 `ProjectDialog.tsx` 패턴 참고)
- 폼 필드:
  - PO 금액 (KRW) — `Input type="number"`
  - PO 금액 (USD) — `Input type="number"`
  - PO 금액 (CNY) — `Input type="number"`
  - USD 환율 — `Input type="number" step="0.01"`
  - CNY 환율 — `Input type="number" step="0.01"`
- 저장 로직은 **레이아웃 단계에서는 미구현** — 버튼만 배치
- `project_financials` 테이블에 upsert하는 Server Action은 추후 구현

### 3. `frontend/src/app/dashboard/sections/CostRateInfoDialog.tsx` (신규)

프로젝트 정보 확인 모달 (읽기 전용):
- 현재 선택된 프로젝트의 PO, 환율, 견적가액, 진행공급가액 등 요약 표시
- 테이블 형태로 깔끔하게

## 구현 순서

1. CostRateDashboard 폰트 크기 확대
2. `'use client'` 전환 + 모달 open state 추가
3. CostRateSettingsDialog 레이아웃 생성 (저장 미연결)
4. CostRateInfoDialog 레이아웃 생성
5. CostRateDashboard에 버튼 2개 + Dialog 연결
6. `tsc --noEmit` 검증

## 검증

- `pnpm exec tsc --noEmit` 통과
- 브라우저에서 폰트 크기 확인, 버튼 클릭 시 모달 오픈 확인
