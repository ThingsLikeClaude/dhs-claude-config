---
name: stalab-ppt-make
description: >
  STALAB 기업 프레젠테이션 HTML 생성 스킬.
  사용자의 콘텐츠를 받아 STALAB 브랜드 템플릿 기반의 단일 HTML 프레젠테이션 파일을 생성한다.
  트리거: "ppt 만들어", "프레젠테이션", "슬라이드", "발표자료", "presentation", "slide deck",
  "make a ppt", "create slides", "STALAB presentation"
---

# STALAB PPT Make

STALAB 브랜드 기업 프레젠테이션을 단일 HTML 파일로 생성한다.

## 레퍼런스 파일 (On-demand Read)

스킬 실행 시 **필요한 시점에** 아래 파일들을 Read한다:

| 파일 | 용도 | 언제 Read |
|------|------|-----------|
| `references/slide-template.html` | 템플릿 소스 (복사 원본) | **Step 3**: HTML 생성 시 |
| `references/layouts-core.md` | 기존 8종 레이아웃 HTML + 분량 제한 + SVG 가이드 | **Step 3**: 슬라이드 마크업 작성 시 |
| `references/layouts-extended.md` | 16종 확장 레이아웃 HTML | **Step 3**: 신규 레이아웃 사용 시 |
| `references/svg-templates.md` | SVG 다이어그램 템플릿 4종 | **Step 3**: 다이어그램 슬라이드 시 |
| `references/decision.md` | Decision Tree + 항목수 판단 + 흐름 패턴 | **Step 2**: 슬라이드 구성 설계 시 |
| `references/chunk.md` | 청크 생성 모드 워크플로우 | **Step 1**: 10장 초과 판단 시 |
| `references/research.md` | 리서치 Phase + Agent Team 워크플로우 | **Step 0**: 주제만 제공 시 |

> `references/slide-template-spec.md`, `references/slide-research-report.md`는 아카이브. 스킬 실행 시 참조하지 않는다.

---

## 아키텍처 요약

```
.deck (viewport — 100vw x 100dvh)
  ├── #gridCanvas (커버 전용 인터랙티브 그리드)
  └── .slides (1920x1080 고정, transform:scale — Math.max로 화면 꽉 채움)
        ├── .slides::before (24px 그리드 배경)
        ├── .persistent-header
        ├── .slide-area (슬라이드 전환 영역)
        │     └── section.slide ...
        └── .persistent-footer
```

> **스케일링**: `Math.max(vw/1920, vh/1080)` — 화면을 꽉 채움. 16:9가 아닌 화면에서는 가장자리가 약간 잘릴 수 있으나 공백 없음.

## 키보드 조작 & 네비게이션

| 키 | 동작 |
|----|------|
| `←` `→` `Space` `PageUp/Down` | 슬라이드 이동 |
| `F` | 전체화면 토글 (Fullscreen API) |
| `Ctrl+Shift+F` | 2단계 챕터 네비게이션 열기 |
| `Escape` | 네비게이션 닫기 / 전체화면 해제 |
| `S` | 발표자 노트 토글 |
| 마우스 휠 | 슬라이드 이동 (400ms 디바운스) |

### 챕터 네비게이션 (2단계 드릴다운)

Section Divider 슬라이드(`.slide--divider`)를 기준으로 자동 구축:

1. **1단계 — 챕터 목록**: 번호, 제목, 부제, 소속 슬라이드 수 표시
2. **2단계 — 슬라이드 목록**: 챕터 클릭 시 해당 챕터 내 모든 슬라이드 제목 + 번호 표시
3. 슬라이드 클릭 → 해당 슬라이드로 즉시 이동
4. "← 챕터 목록으로" 뒤로가기 지원
5. 현재 슬라이드 `.active` 하이라이트

> 템플릿에 CSS(`.chapter-nav` 계열)와 JS(`buildChapterNav`, `renderChapterList`, `renderSlideList`)가 포함되어 있음.

---

## 브랜딩

**폰트**: `'Freesentation', 'Pretendard', system-ui, sans-serif` / `letter-spacing: -0.3px`
CDN: `https://cdn.jsdelivr.net/gh/fontbee/font@main/Freesentation/` (300/500/700)

**색상 체계**:

| 토큰 | 값 | 용도 |
|------|-----|------|
| Primary | `#2d2d8e` | 로고, 차트, 언더라인, KPI, 프로그레스 |
| Heading | `#1a1a2e` | 제목, 불릿, 코드 배경 |
| Body | `#444` | 본문 |
| Muted | `#666` | 서브타이틀, 카드 설명 |
| Light | `#888` / `#999` | 헤더/푸터, 라벨 |
| Background | `#f0f0f0` | 전체 배경 |
| Card BG | `#fff` | 카드, 차트 박스 |
| Border | `#e0e0e0` | 카드, 차트 테두리 |
| Positive/Negative | `#059669` / `#e11d48` | KPI 증감 |

**로고**: STALAB 워드마크 SVG 인라인. `fill="#2d2d8e"`, `height="22"`, `viewBox="0 0 4510 900"`.

**텍스트 크기 계층**: 52px(h2) → 34px(h3) → 28px(본문) → 22px(보조) → 18px(라벨)

---

## 슬라이드 레이아웃 (24종 요약)

> HTML 마크업 상세는 `references/layouts-core.md` (기존 8종) 또는 `references/layouts-extended.md` (신규 16종)를 Read.

| # | 레이아웃 | 용도 | 핵심 클래스 |
|---|----------|------|------------|
| 1 | Cover | 인터랙티브 커버 | `.slide--cover` + `data-type="cover"` + `data-scramble` |
| 2 | Text | 본문 + 불릿 | `.slide--light` + `<ul>` |
| 3 | Two-Column | 좌우 비교 | `.two-col` |
| 4 | Card Grid | 3열 카드 | `.card-grid` + `.light-card` |
| 5 | Chart | CSS bar + SVG line | `.chart-row` + `.chart-box` |
| 6 | KPI | 핵심 지표 4열 | `.kpi-grid` + `.kpi-card` + `data-count` |
| 7 | Code Block | 코드 시연 | `.code-block` + `.kw/.fn/.str/.cm/.num` |
| 8 | Image/SVG | 다이어그램 | `.image-container` + 인라인 SVG |
| 9 | Timeline | 연혁, 마일스톤 | `.timeline` + `.timeline-item` |
| 10 | Step-by-Step | 단계별 과정 | `.step-flow` + `.step-item` |
| 11 | Funnel | 전환률/파이프라인 | `.funnel` + `.funnel-stage` |
| 12 | Cycle | 순환 프로세스 | SVG 템플릿 (svg-templates.md) |
| 13 | Roadmap | 분기별 계획 | `.roadmap` + `.roadmap-row` |
| 14 | Before/After | 전후 비교 | `.before-after` + `.ba-panel` |
| 15 | Pros/Cons | 장단점 | `.pros-cons` + `.pros-col` / `.cons-col` |
| 16 | Comparison Matrix | 다중 비교표 | `.compare-matrix` + `<table>` |
| 17 | Data Table | 정형 데이터 | `.data-table` + `<table>` |
| 18 | Icon Grid | 기능/특징 나열 | `.icon-grid` + `.icon-item` |
| 19 | Bento Grid | 비대칭 하이라이트 | `.bento-grid` + `.bento-wide` |
| 20 | Quote | 인용/강조 | `.quote-slide` + `.quote-mark` |
| 21 | Section Divider | 섹션 전환 | `.slide--divider` + `.divider-number` |
| 22 | Pyramid | 계층 구조 | `.pyramid` + `.pyramid-tier` |
| 23 | Agenda/TOC | 목차 | `.agenda-list` + `.agenda-item` |
| 24 | Venn Diagram | 관계/겹침 | SVG 템플릿 (svg-templates.md) |

**Fragment 시스템**: `class="fragment fade-up" data-step="0"`. `auto-stagger`로 순차 등장.

---

## Critical 제약사항

### MUST
1. **`references/slide-template.html`을 복사하여 시작** — 처음부터 HTML 작성 금지
2. **CSS-only 차트만 사용** — Canvas 차트 라이브러리 금지 (transform:scale 비호환)
3. **커버에 `data-type="cover"` 필수**
4. **단일 HTML 파일** — 외부 JS/CSS 없음 (폰트 CDN만 예외)
5. **그리드 배경은 `.slides::before`** — 전체화면에서도 표시
6. **색상 체계 + 텍스트 크기 계층 준수**

### MUST
7. **Two-Column `.two-col > div`는 자동 카드 스타일** — 흰 배경 + `#e0e0e0` 테두리 + `border-radius: 12px` + padding 36px (템플릿 CSS에 포함)
8. **Pros/Cons `<li>` 텍스트에 체크마크/엑스 금지** — CSS `::before`가 자동 삽입. HTML에 `✓`, `✗`, `&#10003;`, `&#10007;` 넣으면 중복
9. **SVG 다이어그램 슬라이드의 `.image-container`에 `style="flex:none;margin-top:12px;"` 필수** — 미적용 시 헤더가 상단 쏠림
10. **Cycle SVG: `width:60%;max-height:520px`** / **Venn SVG: `width:70%;max-height:480px`** — 전체 너비 사용 시 레이아웃 깨짐
11. **Section Divider는 라이트 배경** — `slide--divider` 클래스만 사용, 다크 배경(`background: #1a1a2e`) 금지. 부제에 `class="divider-subtitle"` 필수
12. **Pyramid `.pyramid-tier`에 `<h3>` + `<p>` 구조 사용** — plain text 금지. CSS가 자동으로 흰색 텍스트 적용

### MUST
13. **SVG/도식과 스크린샷을 같은 슬라이드에 넣지 않기** — 높이 초과로 헤더 잘림 발생. SVG 슬라이드와 스크린샷 슬라이드를 분리
14. **그래픽 요소(SVG, CSS 차트, 터미널 목업)가 있는 슬라이드에 스크린샷 placeholder를 강제 삽입하지 않기** — 도식 자체가 시각 요소이므로 스크린샷은 별도 슬라이드로 분리하거나 생략
15. **터미널 목업(`.code-block` 또는 인라인 dark-bg div)에 `overflow:hidden` 적용** — 스크롤바 발생 금지. 내용이 길면 줄 수를 줄이거나 슬라이드 분할
16. **Agenda/TOC 항목 6개 초과 시 슬라이드 분할** — 항목이 많으면 높이 초과로 헤더 잘림. 5-6개씩 나눠서 (1/2), (2/2)로 분리

### MUST NOT
1. Chart.js / D3.js / Canvas 라이브러리 금지 (transform:scale 비호환)
2. `pushState` 금지 → `replaceState`만
3. `will-change: transform` 상시 적용 금지
4. fragment에 inline `transition-delay` 금지 → `auto-stagger` 사용
5. `.compare-matrix`, `.data-table`에 `overflow-x: auto` 금지 — 불필요한 스크롤바 발생
6. **포인터 스와이프 네비게이션 금지** — 텍스트 드래그 시 슬라이드 역방향 이동 유발
7. **스케일링에 `Math.min` 사용 금지** — 화면 공백 발생. `Math.max` 사용
8. **달러 금액 단독 표기 금지** — 한국어 프레젠테이션에서는 원화 환산 병기 (예: $2B → $2B (약 2.8조 원))

---

## 생성 워크플로우

### 모드 분기

| 조건 | 모드 | 동작 |
|------|------|------|
| 예상 슬라이드 ≤ 10장 | **단일 생성** | 한 번에 전체 HTML 생성 |
| 예상 슬라이드 > 10장 | **청크 생성** | → `references/chunk.md` Read 후 진행 |

### Step 0: Research Phase (선택)

→ `references/research.md` Read → Agent Team 워크플로우

| 사용자 입력 | 예시 | 라우팅 |
|-------------|------|--------|
| 주제/질문만 | "AI 반도체 시장 분석 PPT" | → Step 0 (리서치, 검토 모드) |
| 주제 + "알아서" | "AI 반도체 PPT 알아서 만들어줘" | → Step 0 (리서치, 자동 모드) |
| 완성 콘텐츠 | 불릿, 데이터, 구조화된 텍스트 | → Step 1 (바로 생성) |
| 주제 + 부분 데이터 | "STALAB 소개. 매출은 이거야..." | → Step 0 (갭만 리서치) |

- **검토 모드** (기본): 리서치 후 + 아웃라인 후 사용자 체크포인트 2회
- **자동 모드**: "알아서", "자동으로", "auto" 키워드 감지 시 체크포인트 없이 끝까지 진행
- Agent Team: mina(리서처) → seo(에디터) → hana(PPT빌더)
- 순차 폴백: Agent Team 미지원 시 단일 세션에서 동일 워크플로우 실행

---

### Step 1: 콘텐츠 분석

사용자 입력에서 파악:
- **주제/서브타이틀**, **슬라이드 수**, **데이터 유무**, **코드 유무**, **다이어그램 유무**
- 10장 초과 → `references/chunk.md` Read → 청크 모드

### Step 2: 슬라이드 구성 설계

→ `references/decision.md` Read → Decision Tree로 레이아웃 배정
- 같은 레이아웃 3연속 금지
- 청크 모드: 아웃라인 출력 → 사용자 확인

### Step 3: 템플릿 복사 + 콘텐츠 삽입

→ `references/slide-template.html` Read (복사 원본)
→ `references/layouts-core.md` + `references/layouts-extended.md` Read (레이아웃별 HTML 마크업)

1. 템플릿 복사 (`Bash cp` 명령으로 파일 복사)
2. `<title>`, `.persistent-header__left`, `.persistent-footer__copyright` 수정
3. `.slide-area` 내 기존 예시 삭제 → 새 콘텐츠로 교체
4. 커버 `data-scramble` 값 수정
5. 청크 모드: **5장씩** 배치 생성 (Edit 도구로 삽입)

### Step 4: 파일 저장 + 열기

```
출력 경로: ~/Downloads/{kebab-case-title}.html
```

```bash
start ~/Downloads/{filename}.html
```

### Step 5: 사용자에게 응답

**단일 모드:**
```
프레젠테이션을 생성했습니다!
📄 file:///C:/Users/{user}/Downloads/{filename}.html

슬라이드 구성:
1. Cover — {제목}
2. {레이아웃} — {내용}
...

조작법: →/← 이동, Space 다음, F 전체화면, Ctrl+Shift+F 챕터 네비게이션, S 발표자 노트
```

**청크 모드:**
```
✅ Chunk {N} 완료 (슬라이드 {시작}~{끝} / 총 {전체}장)
📄 file:///C:/Users/{user}/Downloads/{filename}.html

다음 청크로 진행할까요?
```

---

## FAQ

| 질문 | 답변 |
|------|------|
| 슬라이드 수 제한? | 없음. 10장 이하 단일, 초과 시 청크 모드 |
| 오프라인 동작? | 폰트 CDN 외 의존성 없음 |
| 레이아웃 직접 지정? | 가능. 미지정 시 Decision Tree 자동 판단 |
| 콘텐츠 넘침? | 분량 상한 초과 시 자동 분할 (layouts.md 참조) |
| 청크 중간 수정? | 각 청크 완료 후 수정 기회 제공 |
| 기존 파일에 추가? | `.slide-area`에 `<section>` 추가. JS 수정 불필요 |
