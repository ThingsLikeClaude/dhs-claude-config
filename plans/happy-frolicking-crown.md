# 로그인 랜딩페이지 라이트모드 리디자인

## Context
현재 로그인 랜딩페이지는 `dark` 클래스가 하드코딩되어 항상 다크모드로 표시됨.
문제점: Feature Detail 4개 섹션이 거의 보이지 않는 검은 공백, AI 전형적 블루→시안 그라디언트, 동일 레이아웃 반복, 코드 모킹업 신뢰도 부족.

**방향**: 라이트 모드 전환 + 브랜드 컬러(#2E3976) 중심 + 실제 스크린샷 활용 + Supanova 진단 항목 개선

## 변경 파일 목록

### Step 1: 라이트 모드 전환 + 타이포그래피
| 파일 | 변경 내용 |
|------|----------|
| `login/page.tsx` | `dark` 클래스 제거 → 라이트 모드 적용 |
| `login/components/LandingNav.tsx` | 배경색 `rgba(8,9,10,0.9)` → 라이트용 `rgba(255,255,255,0.9)` |
| `login/components/HeroSection.tsx` | 그라디언트 블루→시안 제거, aurora 블롭/그리드 라이트화, hero glow 조정 |

### Step 2: 실제 스크린샷 적용
| 파일 | 변경 내용 |
|------|----------|
| `login/page.tsx` | mockupMap을 스크린샷 이미지로 교체 |
| `login/components/FeatureDetail.tsx` | mockup 영역에 브라우저 프레임 + 이미지 표시 패턴 추가 |
| `login/components/mockups/` | 4개 모킹업 컴포넌트 대신 ScreenshotFrame 컴포넌트 1개로 대체 |

기존 스크린샷 위치: `frontend/screenshots/` (dashboard, delivery, procurements, receipts 등 light/dark 쌍 존재)
→ `public/screenshots/landing/` 으로 복사하여 Next.js Image 사용

**스크린샷 매핑**:
- excel 섹션 → procurements 스크린샷 (품의서 목록이 가장 적합)
- workflow 섹션 → procurements 스크린샷 (상태 컬럼 포커스)
- dashboard 섹션 → dashboard 스크린샷
- delivery 섹션 → delivery 스크린샷

### Step 3: 섹션별 라이트 모드 조정
| 파일 | 변경 내용 |
|------|----------|
| `login/components/FeatureGrid.tsx` | 카드 배경/보더 라이트 조정 (이미 CSS변수 사용 중이라 대부분 자동) |
| `login/components/HowItWorks.tsx` | bg-card 영역 → 라이트에서 자연스럽게 보이도록 확인 |
| `login/components/Statistics.tsx` | 동일 |
| `login/components/CtaSection.tsx` | "혁신하세요" 카피 수정 + 라이트 배경 조정, blobs 라이트화 |
| `login/components/LandingFooter.tsx` | 라이트 모드 색상 확인 |
| `login/data.tsx` | AI 카피 수정: "혁신하세요" → 자연스러운 한국어 |

### Step 4: 애니메이션 & 마감
| 파일 | 변경 내용 |
|------|----------|
| `login/animations.css` | aurora 블롭 색상 라이트화, hero glow 밝은 톤 |

## 핵심 기술 사항

1. **라이트 전환이 간단한 이유**: 모든 컴포넌트가 `bg-background`, `text-foreground` 등 CSS 변수 기반 Tailwind 클래스 사용 중. `dark` 클래스만 제거하면 `:root`(라이트) 값이 자동 적용됨.

2. **수동 수정이 필요한 부분**:
   - HeroSection의 인라인 스타일 (rgba 하드코딩된 glow/gradient)
   - LandingNav의 `rgba(8,9,10,0.9)` 배경
   - CtaSection의 `bg-foreground/[0.05]` blob 색상
   - animations.css의 aurora 블롭 색상
   - HeroSection의 CTA 버튼 스타일 (`background-color: white` → 반전 필요)

3. **ProductScreenshot.tsx**: Hero 영역의 제품 목업. 이것도 라이트 모드에서 잘 보이도록 조정 필요.

## 검증 방법

1. `http://localhost:3000/login` 에서 전체 페이지 시각 확인 (Playwright 스크린샷)
2. 모든 섹션 가시성 확인 (특히 Feature Detail 영역)
3. 스크롤 애니메이션 동작 확인
4. 모바일 반응형 확인
5. `tsc --noEmit`으로 타입 체크
