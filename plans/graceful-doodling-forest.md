# 대시보드 모달 헤더 디테일 개선

## Context

대시보드 모달 4개의 info row(타이틀바 아래 영역)가 "성의없어" 보이는 문제.
macOS 28px 타이틀바 + 12px 빨간 닫기 점은 유지하면서, info row의 배경/간격/정렬을 정리하여 완성도를 높인다.

## 수정 대상 (4개 파일)

- `frontend/src/app/dashboard/sections/SupplierDetailDialog.tsx`
- `frontend/src/app/dashboard/sections/CategoryDetailDialog.tsx`
- `frontend/src/app/dashboard/sections/TimelineDetailDialog.tsx`
- `frontend/src/app/dashboard/sections/CostReductionDetailDialog.tsx`

## 변경 내용

### 1. info row 배경 처리
- `bg-muted/20` 추가 → 타이틀바/테이블과 시각적 분리
- 하단에 `border-b border-border/40` 구분선

### 2. 세로 간격 통일 (ProcurementModal 기준)
- Before: `pt-3 pb-2.5` (불균형)
- After: `pt-3.5 pb-3` (ProcurementModal과 동일)

### 3. 좌측 들여쓰기 정렬
- Before: `px-5` (좌우 균등)
- After: `pl-[30px] pr-5` → 닫기 버튼(12px) 하단에 텍스트 시작점 정렬

### 4. 요약 텍스트 크기
- Before: `text-sm` (14px)
- After: `text-[13px]` → 제목(15px)과의 시각적 위계 강화

## 파일별 적용

### SupplierDetailDialog / CategoryDetailDialog / TimelineDetailDialog
info row div 클래스 변경:
```
Before: "px-5 pt-3 pb-2.5 shrink-0"
After:  "pl-[30px] pr-5 pt-3.5 pb-3 shrink-0 bg-muted/20 border-b border-border/40"
```
요약 텍스트: `text-sm` → `text-[13px]`

### CostReductionDetailDialog
info row div 클래스 변경:
```
Before: "px-5 pt-3.5 pb-3"
After:  "pl-[30px] pr-5 pt-3.5 pb-3 bg-muted/20 border-b border-border/40"
```

## 검증

- `tsc --noEmit` 타입 체크
- dev 서버에서 4개 모달 각각 열어서 확인:
  - 타이틀바 → info row → 테이블 영역 3단 구분 명확한지
  - info row 좌측 텍스트가 닫기 버튼 아래 정렬인지
  - 다크모드에서 bg-muted/20이 자연스러운지
