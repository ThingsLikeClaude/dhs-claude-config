# 슬라이드 레이아웃 상세 (8종)

> 이 파일은 슬라이드 생성 시 Read로 참조한다. SKILL.md에서 직접 로드하지 않음.

모든 콘텐츠 슬라이드는 `class="slide slide--light"`를 사용한다.

---

## 1. Cover (커버)

```html
<section class="slide slide--cover active" data-type="cover">
  <div class="cover-content">
    <h1 data-scramble="Title Line 1|Line 2"></h1>
    <div class="cover-underline"></div>
    <p class="cover-subtitle" data-scramble="Subtitle here"></p>
  </div>
</section>
```

- `data-scramble`: 텍스트 스크램블 애니메이션 (자동 실행)
- `|` → 줄바꿈 변환
- h1: 100px/bold, subtitle: 30px/light, underline: `#2d2d8e`
- 인터랙티브 그리드: 마우스 반경 200px 내 도트 push/repel
- **분량**: 제목 2줄 + 부제 1줄. 초과 시 제목 줄이거나 부제로 이동

## 2. Text (텍스트)

```html
<section class="slide slide--light">
  <h2>Title</h2>
  <p class="fragment fade-up" data-step="0">Body text</p>
  <ul>
    <li class="fragment fade-up" data-step="1">Point 1</li>
    <li class="fragment fade-up" data-step="2">Point 2</li>
  </ul>
</section>
```

- **분량**: 본문 4줄 + 불릿 5개, 또는 본문 2단락(각 3줄) + 불릿 3개
- 초과 시 슬라이드 분할

## 3. Two-Column (2열)

```html
<section class="slide slide--light">
  <h2>Title</h2>
  <div class="two-col">
    <div>
      <h3 class="fragment fade-up" data-step="0">Left</h3>
      <p class="fragment fade-up" data-step="0">Content</p>
    </div>
    <div>
      <h3 class="fragment fade-up" data-step="1">Right</h3>
      <p class="fragment fade-up" data-step="1">Content</p>
    </div>
  </div>
</section>
```

- `.two-col > div`: 자동 카드 스타일 (흰 배경 + `#e0e0e0` 테두리 + `border-radius: 12px` + padding 36px)
- **분량**: 열당 소제목 + 본문 5줄, 또는 소제목 + 불릿 4개
- 초과 시 슬라이드 분할

## 4. Card Grid (3열 카드)

```html
<section class="slide slide--light">
  <h2>Title</h2>
  <div class="card-grid auto-stagger">
    <div class="light-card fragment fade-up" data-step="0">
      <h3>Card A</h3>
      <p>Description</p>
    </div>
    <!-- 카드 B, C -->
  </div>
</section>
```

- **분량**: 1행(3장) 제목 10자 + 설명 2줄. 2행(6장) 제목 8자 + 설명 1줄
- 초과 시 2장 슬라이드로 분할

## 5. Chart (CSS-only)

**Bar chart** (CSS div 기반):
```html
<div class="chart-box">
  <h3>Chart Title</h3>
  <div class="css-bar-chart">
    <div class="bar-col">
      <span class="bar-value">32</span>
      <div class="bar" style="height:53%"></div>
      <span class="bar-label">Jan</span>
    </div>
    <!-- 추가 bar-col -->
  </div>
</div>
```

**Line chart** (SVG polyline 기반):
```html
<div class="chart-box">
  <h3>Chart Title</h3>
  <div class="css-line-chart">
    <svg viewBox="0 0 500 280" preserveAspectRatio="none">
      <defs>
        <linearGradient id="lineGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#2d2d8e" stop-opacity="0.2"/>
          <stop offset="100%" stop-color="#2d2d8e" stop-opacity="0.02"/>
        </linearGradient>
      </defs>
      <polygon points="..." fill="url(#lineGrad)"/>
      <polyline points="..." fill="none" stroke="#2d2d8e" stroke-width="3"/>
      <circle cx="..." cy="..." r="5" fill="#2d2d8e"/>
    </svg>
  </div>
  <div class="css-line-labels"><span>Jan</span>...</div>
</div>
```

두 차트는 `.chart-row` (2열 그리드)로 나란히 배치.

- **분량**: 바 차트 6~12개 bar. 라인 차트 4~8개 포인트. 차트 2개/슬라이드
- 초과 시 차트 분리

**데이터 변환 규칙:**
- Bar: `height = (value / maxValue) * 100 + '%'`
- Line: SVG viewBox `0 0 500 280`. X를 0~500 등분, Y를 280~0 역매핑. polygon은 polyline + 우하단(500,280) + 좌하단(0,280)
- 청크 모드: `linearGradient id` → `lineGrad-{슬라이드번호}`

## 5a. Donut Chart (도넛/파이)

```html
<div class="chart-box">
  <h3>Chart Title</h3>
  <div class="css-donut-chart">
    <div class="donut-ring">
      <svg viewBox="0 0 240 240">
        <circle class="donut-bg" />
        <circle class="donut-fill" style="stroke-dasharray:{seg1len} 628;stroke-dashoffset:0" />
        <circle class="donut-fill s2" style="stroke-dasharray:{seg2len} 628;stroke-dashoffset:-{seg1len}" />
        <circle class="donut-fill s3" style="stroke-dasharray:{seg3len} 628;stroke-dashoffset:-{seg1+seg2}" />
      </svg>
      <div class="donut-center">
        <span class="donut-value">$4.2M</span>
        <span class="donut-label">Total</span>
      </div>
    </div>
    <div class="donut-legend">
      <div class="donut-legend-item"><div class="donut-legend-dot" style="background:#2d2d8e"></div>Label 60%</div>
      <div class="donut-legend-item"><div class="donut-legend-dot" style="background:#4a4abf"></div>Label 25%</div>
      <div class="donut-legend-item"><div class="donut-legend-dot" style="background:#7878d6"></div>Label 15%</div>
    </div>
  </div>
</div>
```

- 원둘레 = `2π × 100 ≈ 628`. `stroke-dasharray`의 첫 값 = 비율 × 628
- 색상 순서: `#2d2d8e` → `.s2` `#4a4abf` → `.s3` `#7878d6` → `.s4` `#a5a5e8`
- **분량**: 세그먼트 2~5개. 범례 포함 시 차트박스 1개/슬라이드 권장
- 슬라이드 진입 시 stroke-dashoffset 애니메이션 자동 적용

## 5b. Gauge (게이지)

```html
<div class="chart-box">
  <h3>Metric Name</h3>
  <div class="css-gauge">
    <div class="gauge-ring">
      <svg viewBox="0 0 280 160">
        <path class="gauge-bg" d="M 30,150 A 120,120 0 0,1 250,150" />
        <path class="gauge-fill" d="M 30,150 A 120,120 0 0,1 250,150"
              style="stroke-dasharray:{fillLen} 377;stroke-dashoffset:0" />
      </svg>
      <div class="gauge-needle" style="transform:rotate({angle}deg)"></div>
      <div class="gauge-center-dot"></div>
      <div class="gauge-value">67%</div>
      <div class="gauge-labels"><span>0%</span><span>100%</span></div>
    </div>
  </div>
</div>
```

- 반원 arc 전체 길이 ≈ 377. `stroke-dasharray` 첫 값 = 비율 × 377
- 바늘 각도: -90deg(0%) → 0deg(50%) → 90deg(100%). 공식: `(비율 - 0.5) × 180`
- 슬라이드 진입 시 바늘 회전 + arc fill 애니메이션 자동 적용

## 5c. Progress List (프로그레스바)

```html
<div class="chart-box">
  <h3>Progress Title</h3>
  <div class="css-progress-list">
    <div class="progress-item">
      <span class="progress-label">Label</span>
      <div class="progress-track"><div class="progress-fill" style="width:92%"></div></div>
      <span class="progress-value">92%</span>
    </div>
    <!-- 추가 항목 -->
  </div>
</div>
```

- 색상 변형: `.green` `#059669`, `.red` `#e11d48`, `.purple` `#7c3aed`, 기본 `#2d2d8e`
- **분량**: 3~6개 항목. 초과 시 분할
- 슬라이드 진입 시 width 0→목표% 순차 애니메이션

## 5d. Waterfall Chart (워터폴)

```html
<div class="chart-box">
  <h3>Chart Title</h3>
  <div class="css-waterfall-chart">
    <div class="waterfall-col">
      <div class="waterfall-bar total" style="height:60%;bottom:0">
        <span class="waterfall-value above">100</span>
      </div>
      <span class="waterfall-label">Start</span>
    </div>
    <div class="waterfall-col">
      <div class="waterfall-bar positive" style="height:15%;bottom:45%">
        <span class="waterfall-value above">+25</span>
      </div>
      <span class="waterfall-label">Growth</span>
    </div>
    <div class="waterfall-col">
      <div class="waterfall-bar negative" style="height:10%;bottom:50%">
        <span class="waterfall-value above">-15</span>
      </div>
      <span class="waterfall-label">Loss</span>
    </div>
    <!-- 추가 bar -->
  </div>
</div>
```

- `.positive` 녹색, `.negative` 빨강, `.total` primary
- `bottom`으로 floating 위치 조절. 이전 바의 top = 다음 바의 bottom 기준점
- **분량**: 4~8개 bar. 초과 시 분할

## 5e. Area Chart (영역차트)

```html
<div class="chart-box">
  <h3>Chart Title</h3>
  <div class="css-area-chart">
    <svg viewBox="0 0 500 280" preserveAspectRatio="none">
      <defs>
        <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#2d2d8e" stop-opacity="0.3"/>
          <stop offset="100%" stop-color="#2d2d8e" stop-opacity="0.02"/>
        </linearGradient>
      </defs>
      <polygon class="area-fill" points="0,250 80,200 160,220 240,150 320,170 400,100 500,60 500,280 0,280" fill="url(#areaGrad)" />
      <polyline class="area-line" points="0,250 80,200 160,220 240,150 320,170 400,100 500,60" stroke="#2d2d8e" />
      <circle class="area-dot" cx="0" cy="250" fill="#2d2d8e" />
      <!-- 추가 dot -->
    </svg>
  </div>
  <div class="area-labels"><span>Jan</span><span>Feb</span>...</div>
</div>
```

- 라인 차트와 유사하나 `area-fill` polygon으로 영역 채움
- 다중 시리즈: 각 시리즈별 별도 gradient id 사용
- 청크 모드: `areaGrad-{슬라이드번호}`
- 슬라이드 진입 시 stroke-dashoffset 드로우 애니메이션

## 5f. Heatmap (히트맵)

```html
<div class="chart-box">
  <h3>Chart Title</h3>
  <div class="css-heatmap">
    <div class="heatmap-grid" style="--cols:7">
      <div class="heatmap-row-label">Mon</div>
      <div class="heatmap-cell" data-level="3"></div>
      <div class="heatmap-cell" data-level="5"></div>
      <!-- 행당 cols개 셀 -->
      <div class="heatmap-row-label">Tue</div>
      <!-- ... -->
    </div>
    <div class="heatmap-legend">
      <span>Less</span>
      <div class="heatmap-legend-cell" style="opacity:0.1"></div>
      <div class="heatmap-legend-cell" style="opacity:0.3"></div>
      <div class="heatmap-legend-cell" style="opacity:0.5"></div>
      <div class="heatmap-legend-cell" style="opacity:0.7"></div>
      <div class="heatmap-legend-cell" style="opacity:1"></div>
      <span>More</span>
    </div>
  </div>
</div>
```

- `data-level`: 0~5 (opacity 0.05~1.0)
- `--cols`: 열 수 설정 (CSS grid)
- **분량**: 5~7행 × 5~12열. 초과 시 분할
- 슬라이드 진입 시 scale(0)→scale(1) 순차 애니메이션

## 5g. Sparkline (스파크라인, KPI 내장)

```html
<div class="kpi-card">
  <div class="kpi-value" data-count="3842">0</div>
  <div class="kpi-label">Label</div>
  <div class="kpi-change positive">+18%</div>
  <div class="sparkline positive">
    <svg viewBox="0 0 100 40" preserveAspectRatio="none">
      <polygon points="0,35 25,28 50,20 75,15 100,10 100,40 0,40" />
      <polyline points="0,35 25,28 50,20 75,15 100,10" />
    </svg>
  </div>
</div>
```

- KPI 카드 하단에 삽입하는 미니 트렌드 차트
- `.positive` 녹색, `.negative` 빨강, 기본 primary
- viewBox `0 0 100 40`. Y축: 0(상단)~40(하단)
- 슬라이드 진입 시 stroke 드로우 애니메이션

## 5h. Treemap (트리맵)

```html
<div class="chart-box">
  <h3>Chart Title</h3>
  <div class="css-treemap">
    <div class="treemap-item" style="flex:3;background:#2d2d8e">
      <h4>Category A</h4>
      <span>45%</span>
      <p>Description</p>
    </div>
    <div class="treemap-item" style="flex:2;background:#4a4abf">
      <h4>Category B</h4>
      <span>30%</span>
    </div>
    <div class="treemap-item" style="flex:1;background:#7878d6">
      <h4>Category C</h4>
      <span>15%</span>
    </div>
    <div class="treemap-item" style="flex:0.7;background:#a5a5e8">
      <h4>Category D</h4>
      <span>10%</span>
    </div>
  </div>
</div>
```

- `flex` 값으로 면적 비율 결정
- 색상: primary 계열 그라데이션 (`#2d2d8e` → `#4a4abf` → `#7878d6` → `#a5a5e8`)
- 텍스트 자동 흰색. hover 시 scale + shadow 효과
- **분량**: 3~7개 항목. 작은 항목은 h4만 표시
- 슬라이드 진입 시 scale(0)→scale(1) 순차 애니메이션

## 5i. Radar Chart (레이더)

```html
<div class="css-radar-chart">
  <div class="radar-ring">
    <svg viewBox="0 0 400 400">
      <g class="radar-grid">
        <!-- 동심 다각형 4개 (가장 큰 것부터) -->
        <polygon points="200,40 344,120 344,280 200,360 56,280 56,120" />
        <polygon points="200,80 312,140 312,260 200,320 88,260 88,140" />
        <polygon points="200,120 280,160 280,240 200,280 120,240 120,160" />
        <polygon points="200,160 248,180 248,220 200,240 152,220 152,180" />
        <!-- 축 선 -->
        <line x1="200" y1="40" x2="200" y2="360" />
        <line x1="56" y1="120" x2="344" y2="280" />
        <line x1="344" y1="120" x2="56" y2="280" />
      </g>
      <!-- 데이터 다각형 -->
      <polygon class="radar-data" points="..." />
      <polygon class="radar-data s2" points="..." />
      <!-- 데이터 점 -->
      <circle class="radar-dot" cx="..." cy="..." />
      <!-- 축 라벨 -->
      <text class="radar-label" x="200" y="25">Label</text>
    </svg>
  </div>
  <div class="radar-legend">
    <div class="radar-legend-item"><div class="radar-legend-line" style="background:#2d2d8e"></div>Series A</div>
    <div class="radar-legend-item"><div class="radar-legend-line" style="background:#e11d48"></div>Series B</div>
  </div>
</div>
```

- 중심: (200,200), 반경: 160 (40~360 범위)
- 축 수: 3~8개 (정다각형). 6각형 기본. 꼭짓점 좌표 계산:
  - `x = 200 + 160 × sin(i × 2π/n)`, `y = 200 - 160 × cos(i × 2π/n)`
- 데이터 점: 비율(0~1) × 160으로 반경 계산
- 색상: `.radar-data` primary, `.s2` 빨강, `.s3` 녹색
- **분량**: 시리즈 1~3개. 축 3~8개
- 슬라이드 진입 시 polygon stroke 드로우 애니메이션

---

## 6. KPI (핵심 지표)

```html
<section class="slide slide--light">
  <h2>Key Metrics</h2>
  <div class="kpi-grid">
    <div class="kpi-card fragment fade-up" data-step="0">
      <div class="kpi-value" data-count="1247">0</div>
      <div class="kpi-label">Total Users</div>
      <div class="kpi-change positive">+12.5%</div>
    </div>
    <!-- 최대 4열 -->
  </div>
</section>
```

- `data-count`: 카운트업 애니메이션 목표값
- `data-prefix` / `data-suffix`: 접두사/접미사 (`$`, `K`, `%`)
- `.positive` / `.negative`: 증감 색상
- 초기 텍스트: prefix + "0" + suffix
- **분량**: 1행 4개. 2행 8개 (change 텍스트 짧게). 초과 시 2장 분할

## 7. Code Block (코드)

```html
<section class="slide slide--light">
  <h2>Code Example</h2>
  <div class="code-block fragment fade-up" data-step="0">
    <span class="code-line"><span class="cm">// Comment</span></span>
    <span class="code-line"><span class="kw">function</span> <span class="fn">name</span>() {</span>
    <span class="code-line">  <span class="kw">return</span> <span class="str">'value'</span>;</span>
    <span class="code-line">}</span>
  </div>
</section>
```

구문 하이라이팅: `.kw`(보라), `.fn`(파랑), `.str`(녹색), `.cm`(회색), `.num`(주황)

- **분량**: 15~20줄 (max-height 520px 확보). 초과 시 분할 또는 핵심 발췌
- **주의**: `.code-line`은 `display: block`으로 줄바꿈 보장. 빈 줄은 `<span class="code-line"></span>`

## 8. Image / SVG Diagram (이미지)

```html
<section class="slide slide--light">
  <h2>Diagram</h2>
  <div class="image-container fragment fade-up" data-step="0">
    <svg viewBox="..." style="width:100%;max-height:580px">
      <!-- SVG diagram -->
    </svg>
  </div>
  <p class="image-caption fragment fade-up" data-step="1">Figure 1. Caption</p>
</section>
```

- **분량**: max-height 580px. 노드 8~12개 + 화살표. 초과 시 계층 분리
- 청크 모드: `marker id` → `arrowhead-{슬라이드번호}`

---

## SVG 다이어그램 생성 가이드

```html
<svg viewBox="0 0 1600 500" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-height:580px">
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#2d2d8e"/>
    </marker>
  </defs>

  <!-- Box: 기본 -->
  <rect x="50" y="40" width="280" height="100" rx="12" fill="#fff" stroke="#e0e0e0" stroke-width="2"/>
  <text x="190" y="80" text-anchor="middle" fill="#1a1a2e" font-size="22" font-weight="700">Title</text>
  <text x="190" y="110" text-anchor="middle" fill="#888" font-size="16">Subtitle</text>

  <!-- Arrow -->
  <line x1="..." y1="..." x2="..." y2="..." stroke="#2d2d8e" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="..." y="..." text-anchor="middle" fill="#888" font-size="13">Label</text>
</svg>
```

### 박스 유형

| 유형 | fill | stroke | 용도 |
|------|------|--------|------|
| 기본 | `#fff` | `#e0e0e0` | 클라이언트, 일반 컴포넌트 |
| 강조 | `#2d2d8e` | none | API Gateway, 핵심 서비스 |
| 서비스 | `#fff` | `#2d2d8e` | 마이크로서비스, 모듈 |
| 인프라 | `#f0f0f0` | `#ccc` | DB, 스토리지, 캐시 |

---

## 글자수 기준 (한국어)

| 요소 | 권장 | 하드 리밋 |
|------|------|-----------|
| h2 제목 | 10~15자 | 20자 |
| h3 소제목 | 8~12자 | 18자 |
| 본문 1줄 | 35~40자 | 50자 |
| 불릿 1개 | 25~35자 | 45자 |
| 카드 제목 | 6~10자 | 12자 |
| 카드 설명 | 20~30자/줄, 최대 2줄 | 3줄 |
| KPI 라벨 | 6~10자 | 14자 |

---

## 커스텀 레이아웃 확장

`.slide--light` 내부에서 새 CSS 클래스로 확장 가능.

**규칙:**
1. 색상 체계 준수 (Primary, Heading, Body 등)
2. 카드/박스: 흰 배경 + `#e0e0e0` 테두리 + `border-radius: 12px`
3. 텍스트 크기 계층: h2(52px) → h3(34px) → p(28px) → small(22px) → label(18px)
4. 간격: gap 28~60px, padding 28~40px

**확장 예시 — Timeline:**
```html
<section class="slide slide--light">
  <h2>Project Timeline</h2>
  <div style="display:flex;gap:24px;margin-top:32px;">
    <div class="light-card fragment fade-up" data-step="0" style="flex:1;border-top:4px solid #2d2d8e;">
      <h3>Phase 1</h3>
      <p>Description</p>
    </div>
  </div>
</section>
```

---

## 발표자 노트

```html
<aside class="notes">발표 가이드 텍스트</aside>
```

- 기본: 숨김. `S` 키로 하단 패널 토글. 인쇄 시 숨김.
