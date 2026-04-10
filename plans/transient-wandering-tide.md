# Supanova Redesign Plan — /login Landing Page

## Context
현재 /login 랜딩 페이지는 기능적으로 잘 작동하지만, Supanova 디자인 감사 기준에서 여러 개선점이 발견됨.
목표: **"$150k 에이전시가 만든 듯한" 프리미엄 퀄리티**로 업그레이드하되, 기존 구조는 유지.

## Supanova 진단 결과

### 이미 잘 되어 있는 것 (건드리지 않음)
- Pretendard + Geist 폰트 조합
- OKLCH 기반 디자인 시스템 (Deep Indigo 브랜드)
- Noise texture overlay
- `word-break: keep-all`, `text-wrap: balance`
- ExcelToOrdify 스크롤 와이프 (핵심 인터랙션)
- LandingNav (깔끔한 미니멀 네비)
- LandingFooter (적절히 미니멀)

### 수정 대상 (우선순위 순)

| # | 문제 | 파일 | 수정 내용 |
|---|------|------|-----------|
| 1 | 영어 뱃지 라벨 | FeatureGrid, WorkflowTimeline, ExcelToOrdify | "Features"→"핵심 기능", "Workflow"→"업무 흐름", "Before & After"→"변환 과정" |
| 2 | Hero 헤드라인 임팩트 부족 | HeroSection | 폰트 크기 키우기, 서브타이틀 개선 |
| 3 | Feature 섹션 제네릭 3열 | FeatureGrid | 좌우 지그재그 레이아웃으로 변경 — 각 feature에 목업 이미지 영역 추가 |
| 4 | Workflow 4등분 제네릭 | WorkflowTimeline | 수직 타임라인 + 좌우 교차 레이아웃으로 변경 |
| 5 | 호버/액티브 부족 | FeatureGrid, animations.css | 카드 호버 시 border glow + 미묘한 scale, spring-based transition |
| 6 | 섹션 간 단조로움 | animations.css, 각 섹션 | 섹션별 다른 배경 처리 (gradient, subtle pattern) |
| 7 | CTA 버튼 존재감 약함 | HeroSection | 더 큰 패딩, primary 배경색으로 변경, 호버 glow 효과 |

## 구현 계획

### 1. HeroSection.tsx 개선
- 헤드라인: `text-[4rem] md:text-[5.5rem]`으로 크기 업
- 서브타이틀 카피 개선: 더 자연스러운 한국어
- CTA: `variant="outline"` → primary filled 스타일, `px-12 py-5` 크기 업
- 배경 대시보드 이미지 opacity `0.07` → `0.10`으로 약간 더 보이게
- Scroll indicator 유지

### 2. FeatureGrid.tsx 리디자인
- 현재: 7개 카드 3열 bento
- 변경: 상위 3개 feature는 **좌우 교차 2열** (텍스트 + 아이콘 큰 영역), 나머지 4개는 **2x2 그리드** 하단 배치
- 뱃지: "Features" → "핵심 기능"
- 카드 호버: `hover:border-primary/20 hover:shadow-lg hover:shadow-primary/5`
- Spring transition: `transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1)`

### 3. WorkflowTimeline.tsx 리디자인
- 현재: 4열 수평 레이아웃
- 변경: **세로 타임라인** — 중앙 수직 라인 + 좌우 교차 카드
- 뱃지: "Workflow" → "업무 흐름"
- 각 스텝 카드에 미묘한 배경색 변화 (1→4로 점점 밝아짐)
- 연결 라인에 gradient 애니메이션

### 4. ExcelToOrdifySection.tsx (최소 수정)
- 뱃지: "Before & After" → "변환 과정"
- 나머지는 현재 스크롤 와이프가 잘 작동하므로 유지

### 5. animations.css 보강
- Spring-based hover transition 유틸리티 클래스 추가
- 섹션별 배경 gradient 추가 (Feature → subtle gray, Workflow → subtle primary tint)
- Staggered cascade 변수 (`--index`) 기반 지연

### 6. data.tsx 카피 개선
- Feature 설명문 더 자연스러운 한국어로
- "혁신적인", "원활한" 같은 AI 클리셰 제거 (현재는 없지만 확인)

## 수정 파일 목록
1. `frontend/src/app/login/components/HeroSection.tsx` — 헤드라인 + CTA 개선
2. `frontend/src/app/login/components/FeatureGrid.tsx` — 레이아웃 변경
3. `frontend/src/app/login/components/WorkflowTimeline.tsx` — 세로 타임라인
4. `frontend/src/app/login/components/ExcelToOrdifySection.tsx` — 뱃지 텍스트만
5. `frontend/src/app/login/animations.css` — 호버/배경 유틸리티
6. `frontend/src/app/login/data.tsx` — 카피 다듬기 (필요시)

## 검증 방법
- `tsc --noEmit` 타입 체크 통과
- 브라우저에서 localhost:3000/login 열어 시각적 확인 (dev 서버는 사용자가 관리)
- 스크롤 시 각 섹션 애니메이션 트리거 확인
- 모바일 반응형 깨짐 없는지 확인 (md 브레이크포인트)
