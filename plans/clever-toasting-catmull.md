# Plan: 한국수출입은행 환율 API 연동 + "오늘 환율" 참고 버튼

## Context

CostRateInfoDialog 편집 모드에서 환율을 수동 입력해야 함. 한국수출입은행 API로 오늘의 매매기준율을 조회하여 참고 정보로 표시하고, [적용] 버튼으로 입력 필드에 채울 수 있게 함.

## 수정 파일

| 파일 | 변경 |
|------|------|
| `frontend/src/app/actions/exchange-rate.ts` | **신규** — Server Action: 한국수출입은행 API 호출 |
| `frontend/src/app/dashboard/sections/CostRateInfoDialog.tsx` | "오늘 환율" 참고 표시 + [적용] 버튼 |
| `frontend/.env.local` | `KOEXIM_API_KEY` 추가 |
| `frontend/.env.example` | `KOEXIM_API_KEY` 플레이스홀더 추가 |

## 1. Server Action: `exchange-rate.ts`

```typescript
'use server';

// 한국수출입은행 현재환율 API
// GET https://www.koreaexim.go.kr/site/program/financial/exchangeJSON
//   ?authkey=API_KEY&searchdate=YYYYMMDD&data=AP01

interface ExchangeRateResult {
  usd: number | null;
  cny: number | null;
  date: string; // YYYY-MM-DD
}

export async function getTodayExchangeRates(): Promise<ExchangeRateResult>
```

- 환경변수 `KOEXIM_API_KEY`로 인증
- `data=AP01` (매매기준율)
- `cur_unit` === `'USD'` / `'CNY'` 필터
- `deal_bas_r` (매매기준율) 파싱 — 콤마 제거 후 parseFloat
- 주말/공휴일에는 직전 영업일 데이터가 반환됨 (API 특성)
- API 키 없거나 실패 시 `{ usd: null, cny: null }` 반환 (참고 기능이므로 에러 무시)

## 2. CostRateInfoDialog UI 변경

편집 모드 환율 입력 필드 아래에:

```
┌─ 기준 환율 (원/$) ──────────────────┐
│ 1,300                                │
└──────────────────────────────────────┘
  📌 오늘 매매기준율: 1,382원  [적용]
```

### 구현 상세
- 편집 모드 진입 시 `getTodayExchangeRates()` 1회 호출 (useEffect)
- `todayRates` state에 저장 (`{ usd, cny, date }`)
- 로딩 중: `불러오는 중...` 텍스트
- 실패/null: 해당 줄 숨김
- [적용] 클릭 → `setEditRate(formatWithCommas(String(todayRate)))` 호출
- KRW 탭에서는 표시 안 함 (환율 고정 1)

## 3. 환경변수

```env
# 한국수출입은행 환율 API
KOEXIM_API_KEY=
```

## 검증

1. `tsc --noEmit` — 타입 에러 없음
2. 브라우저: 편집 모드 → USD 탭 → 환율 필드 아래 "오늘 매매기준율: X원 [적용]" 표시
3. [적용] 클릭 → 환율 필드에 값 채워지고 인라인 환산 즉시 반영
4. API 키 없을 때: 해당 줄 숨김, 기존 기능 정상 동작
