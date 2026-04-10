# /login 랜딩 페이지 완전 리디자인

## Context
현재 디자인이 전문적이지 않다는 피드백. flex.team 수준의 프로덕트 가이드 스타일로 완전히 새로 만든다. Before/After 섹션 제거, 대형 스크린샷 중심 히어로, 깔끔한 화이트 톤.

## 디자인 방향
- **Hero**: Linear/Vercel 스타일 — 중앙 정렬 헤드라인 + 전체 너비 대시보드 스크린샷
- **톤**: 깔끔한 화이트 배경, 미니멀
- **구성**: Hero → Feature 탭 (3섹션) → Workflow → CTA → Footer
- **Before/After 섹션 제거**

## 페이지 구조

### 1. LandingNav (수정)
- 현재 유지, max-width를 1400px로 통일

### 2. HeroSection (완전 재작성)
```
[Badge: 사내 구매관리 시스템]
[H1: 엑셀 없이, 더 빠르게]
[Subtitle: 1-2줄]
[CTA: Google로 계속하기]
[────── 전체 너비 대시보드 스크린샷 ──────]
[하단 gradient fade to white]
```
- 중앙 정렬 (DESIGN_VARIANCE=8이지만 사용자가 이 스타일 선택)
- `/screenshots/dashboard-full.png` 사용
- 3D perspective tilt + 미묘한 그림자
- framer-motion 순차 등장

### 3. FeatureGrid (완전 재작성 — flex.team 탭 패턴)
3개 카테고리, 각각 탭 + 스크린샷:

**섹션 A: "구매 문서 관리"**
- 탭: 품의서 작성 (`ordify-create.png`), 엑셀 파싱 (placeholder), 영수증 (placeholder)

**섹션 B: "승인과 추적"**
- 탭: 품의서 목록 (`ordify-procurements.png`), 입고 예정일 (`ordify-delivery.png`)

**섹션 C: "데이터 분석"**
- 탭: 대시보드 (`dashboard-full.png`), 마스터 데이터 (placeholder), 사용자 권한 (placeholder)

각 섹션: 좌/우 지그재그, 좌측=텍스트+탭버튼, 우측=스크린샷

### 4. WorkflowTimeline (유지)
- 현재 수평 4단계 디자인 유지

### 5. LandingFooter (유지)
- CTA 섹션 + 미니멀 푸터 유지

## 수정 파일
| 파일 | 작업 |
|------|------|
| `components/HeroSection.tsx` | 완전 재작성 |
| `components/FeatureGrid.tsx` | 탭 데이터 재구성 (품의서 목록을 승인과 추적으로 이동) |
| `components/ExcelToOrdifySection.tsx` | 삭제 (import 제거) |
| `page.tsx` | ExcelToOrdifySection import/render 제거 |
| `components/WorkflowTimeline.tsx` | 유지 |
| `components/LandingFooter.tsx` | 유지 |
| `components/LandingNav.tsx` | 유지 |

## 핵심 디자인 규칙 (design-taste-frontend)
- Geist 폰트 사용 (Inter 금지)
- `min-h-[100dvh]` (h-screen 금지)
- 최대 1 accent color (primary = Deep Indigo)
- framer-motion spring physics
- 순차 stagger 애니메이션
- 플레이스홀더: dashed border + 아이콘 + "스크린샷 추가 예정"

## 검증
1. `tsc --noEmit` 통과 확인
2. Playwright로 localhost:3001/login 접속해서 각 섹션 스크린샷 확인
3. 스크롤하며 전체 페이지 흐름 확인
