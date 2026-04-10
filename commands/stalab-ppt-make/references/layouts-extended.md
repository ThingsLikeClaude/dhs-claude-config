# 슬라이드 레이아웃 확장 (16종)

> layouts-core.md(8종)에 이어지는 확장 레이아웃. 번호 9~24.
> CSS는 slide-template.html에 이미 정의됨. 이 파일은 **HTML 마크업 명세만** 기술한다.
> 모든 레이아웃은 fragment 시스템 지원: `class="fragment fade-up" data-step="N"`

모든 콘텐츠 슬라이드는 `class="slide slide--light"`를 사용한다.
(예외: Section Divider는 `class="slide slide--divider"`)

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

## 9. Timeline (수평 타임라인)

```html
<section class="slide slide--light">
  <h2>프로젝트 타임라인</h2>
  <div class="timeline">
    <div class="timeline-item fragment fade-up" data-step="0">
      <div class="timeline-dot"></div>
      <div class="timeline-date">2026 Q1</div>
      <div class="timeline-content">
        <h3>기획 완료</h3>
        <p>요구사항 분석 및 설계</p>
      </div>
    </div>
    <div class="timeline-item fragment fade-up" data-step="1">
      <div class="timeline-dot"></div>
      <div class="timeline-date">2026 Q2</div>
      <div class="timeline-content">
        <h3>개발 착수</h3>
        <p>핵심 모듈 구현 시작</p>
      </div>
    </div>
    <div class="timeline-item fragment fade-up" data-step="2">
      <div class="timeline-dot"></div>
      <div class="timeline-date">2026 Q3</div>
      <div class="timeline-content">
        <h3>베타 출시</h3>
        <p>내부 테스트 및 피드백</p>
      </div>
    </div>
  </div>
</section>
```

- `.timeline`: 수평 flex 컨테이너, 노드 사이 연결선 자동 생성
- `.timeline-dot`: 원형 마커 (`#2d2d8e`)
- `.timeline-date`: 날짜/시기 라벨 (상단)
- `.timeline-content`: 제목 + 설명 (하단)
- **분량**: 3~6개 노드. 노드당 제목 8자 + 설명 1줄. 초과 시 슬라이드 분할

---

## 10. Step-by-Step (단계별 프로세스)

```html
<section class="slide slide--light">
  <h2>도입 프로세스</h2>
  <div class="step-flow">
    <div class="step-item fragment fade-up" data-step="0">
      <div class="step-number">1</div>
      <h3>요구 분석</h3>
      <p>현황 파악 및 목표 설정</p>
    </div>
    <div class="step-arrow fragment fade-up" data-step="0"></div>
    <div class="step-item fragment fade-up" data-step="1">
      <div class="step-number">2</div>
      <h3>설계</h3>
      <p>아키텍처 및 UI 설계</p>
    </div>
    <div class="step-arrow fragment fade-up" data-step="1"></div>
    <div class="step-item fragment fade-up" data-step="2">
      <div class="step-number">3</div>
      <h3>구현</h3>
      <p>개발 및 단위 테스트</p>
    </div>
    <div class="step-arrow fragment fade-up" data-step="2"></div>
    <div class="step-item fragment fade-up" data-step="3">
      <div class="step-number">4</div>
      <h3>검증</h3>
      <p>통합 테스트 및 배포</p>
    </div>
  </div>
</section>
```

- `.step-flow`: 수평 flex, 단계 사이 화살표 배치
- `.step-item`: 번호 + 제목 + 설명 카드
- `.step-number`: 원형 번호 배지 (`#2d2d8e` 배경, 흰 텍스트)
- `.step-arrow`: CSS `→` 화살표 (단계 사이 자동 배치)
- **분량**: 3~5단계. 단계당 제목 10자 + 설명 1줄. 초과 시 슬라이드 분할

---

## 11. Funnel (깔때기)

```html
<section class="slide slide--light">
  <h2>전환 퍼널</h2>
  <div class="funnel">
    <div class="funnel-stage fragment fade-up" data-step="0" style="--funnel-width:100%">
      <div class="funnel-bar">
        <span class="funnel-label">유입</span>
        <span class="funnel-value">10,000</span>
      </div>
    </div>
    <div class="funnel-stage fragment fade-up" data-step="1" style="--funnel-width:60%">
      <div class="funnel-bar">
        <span class="funnel-label">가입</span>
        <span class="funnel-value">6,000</span>
      </div>
    </div>
    <div class="funnel-stage fragment fade-up" data-step="2" style="--funnel-width:30%">
      <div class="funnel-bar">
        <span class="funnel-label">결제</span>
        <span class="funnel-value">3,000</span>
      </div>
    </div>
    <div class="funnel-stage fragment fade-up" data-step="3" style="--funnel-width:12%">
      <div class="funnel-bar">
        <span class="funnel-label">재구매</span>
        <span class="funnel-value">1,200</span>
      </div>
    </div>
  </div>
</section>
```

- `.funnel`: 수직 flex, 중앙 정렬
- `.funnel-stage`: 각 단계 컨테이너
- `.funnel-bar`: `--funnel-width` CSS 변수로 너비 제어 (100%→60%→30%→12% 등)
- `.funnel-label`: 단계명 (좌측), `.funnel-value`: 수치 (우측)
- **분량**: 3~6단계. 초과 시 슬라이드 분할

---

## 12. Cycle (순환 다이어그램)

```html
<section class="slide slide--light">
  <h2>개발 사이클</h2>
  <div class="image-container fragment fade-up" data-step="0">
    <!-- svg-templates.md의 Cycle 템플릿 사용 -->
    <svg viewBox="0 0 800 800" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-height:580px">
      <!-- Cycle SVG: 원형 배치 노드 + 곡선 화살표 -->
      <!-- svg-templates.md 참조 -->
    </svg>
  </div>
  <p class="image-caption fragment fade-up" data-step="1">Figure 1. 지속적 개선 사이클</p>
</section>
```

- `.image-container`를 사용하며 SVG 인라인 삽입. **반드시** `style="flex:none;margin-top:12px;"` 적용
- SVG에 `style="width:60%;max-height:520px"` 적용 (전체 너비 사용 시 헤더 쏠림 발생)
- svg-templates.md의 Cycle 템플릿에서 노드 수/라벨만 교체
- **분량**: 3~6노드. 노드당 라벨 8자 이내. 초과 시 계층 분리

---

## 13. Roadmap (로드맵)

```html
<section class="slide slide--light">
  <h2>제품 로드맵</h2>
  <div class="roadmap">
    <div class="roadmap-header">
      <div class="roadmap-label"></div>
      <div>Q1</div>
      <div>Q2</div>
      <div>Q3</div>
      <div>Q4</div>
    </div>
    <div class="roadmap-row fragment fade-up" data-step="0">
      <div class="roadmap-label">프론트엔드</div>
      <div class="roadmap-bar" style="grid-column:2/4;background:#2d2d8e;">v1.0 개발</div>
    </div>
    <div class="roadmap-row fragment fade-up" data-step="1">
      <div class="roadmap-label">백엔드</div>
      <div class="roadmap-bar" style="grid-column:2/5;background:#4a4abf;">API 구축</div>
    </div>
    <div class="roadmap-row fragment fade-up" data-step="2">
      <div class="roadmap-label">인프라</div>
      <div class="roadmap-bar" style="grid-column:3/5;background:#6b6bd0;">클라우드 이전</div>
    </div>
  </div>
</section>
```

- `.roadmap`: CSS Grid 컨테이너
- `.roadmap-header`: 헤더 행 (라벨 열 160px + 분기 열)
- `.roadmap-row`: 각 행, CSS Grid 공유
- `.roadmap-label`: 행 이름 (160px 고정 열)
- `.roadmap-bar`: `grid-column` inline style로 시작/끝 지정 + `background` 색상
- **분량**: 3~6행. 열: 4~6개. 초과 시 슬라이드 분할

---

## 14. Before/After (전후 비교)

```html
<section class="slide slide--light">
  <h2>도입 전후 비교</h2>
  <div class="before-after">
    <div class="ba-panel ba-before fragment fade-up" data-step="0">
      <div class="ba-badge">Before</div>
      <h3>기존 방식</h3>
      <ul>
        <li>수작업 데이터 입력</li>
        <li>엑셀 기반 관리</li>
        <li>주 1회 보고서 작성</li>
      </ul>
    </div>
    <div class="ba-panel ba-after fragment fade-up" data-step="1">
      <div class="ba-badge">After</div>
      <h3>개선 방식</h3>
      <ul>
        <li>자동 데이터 수집</li>
        <li>실시간 대시보드</li>
        <li>자동 리포트 생성</li>
      </ul>
    </div>
  </div>
</section>
```

- `.before-after`: 2열 flex/grid 컨테이너
- `.ba-panel`: 패널 공통 스타일 (흰 배경, 라운드 카드)
- `.ba-before`: 상단 빨간 보더 (`border-top: 4px solid #e74c3c`)
- `.ba-after`: 상단 초록 보더 (`border-top: 4px solid #2ecc71`)
- `.ba-badge`: "Before"/"After" 대문자 라벨 배지
- **분량**: 패널당 제목 + 3~5 불릿. 초과 시 슬라이드 분할

---

## 15. Pros/Cons (장단점)

```html
<section class="slide slide--light">
  <h2>클라우드 전환 장단점</h2>
  <div class="pros-cons">
    <div class="pros-col fragment fade-up" data-step="0">
      <h3>장점</h3>
      <ul>
        <li>확장성 및 유연성 확보</li>
        <li>초기 투자 비용 절감</li>
        <li>글로벌 배포 용이</li>
        <li>자동 백업 및 복구</li>
      </ul>
    </div>
    <div class="cons-col fragment fade-up" data-step="1">
      <h3>단점</h3>
      <ul>
        <li>월간 운영 비용 발생</li>
        <li>데이터 주권 이슈</li>
        <li>벤더 종속 위험</li>
        <li>마이그레이션 복잡도</li>
      </ul>
    </div>
  </div>
</section>
```

- `.pros-cons`: 2열 flex/grid 컨테이너
- `.pros-col`: 초록 계열 스타일 (좌측), CSS `::before`로 ✓ 자동 삽입 — **HTML에 체크마크 넣지 말 것**
- `.cons-col`: 빨간 계열 스타일 (우측), CSS `::before`로 ✗ 자동 삽입 — **HTML에 엑스 넣지 말 것**
- **분량**: 열당 3~5항목. 초과 시 슬라이드 분할

---

## 16. Comparison Matrix (비교표)

```html
<section class="slide slide--light">
  <h2>솔루션 비교</h2>
  <div class="compare-matrix">
    <table>
      <thead>
        <tr>
          <th>항목</th>
          <th>A사</th>
          <th class="highlight-col">STALAB</th>
          <th>C사</th>
        </tr>
      </thead>
      <tbody>
        <tr class="fragment fade-up" data-step="0">
          <td>가격</td>
          <td>₩50M</td>
          <td class="highlight-col">₩35M</td>
          <td>₩45M</td>
        </tr>
        <tr class="fragment fade-up" data-step="1">
          <td>성능</td>
          <td>보통</td>
          <td class="highlight-col">우수</td>
          <td>양호</td>
        </tr>
        <tr class="fragment fade-up" data-step="2">
          <td>지원</td>
          <td>이메일</td>
          <td class="highlight-col">24/7 전담</td>
          <td>업무시간</td>
        </tr>
      </tbody>
    </table>
  </div>
</section>
```

- `.compare-matrix`: 테이블 래퍼 (스크롤 방지, 폰트 조정)
- `.highlight-col`: 추천 열 강조 (배경색 `#2d2d8e` 반투명 + 볼드)
- `<thead>`: 헤더 행 (고정), `<tbody>`: 데이터 행
- **분량**: 3~4열 x 5~8행. 초과 시 슬라이드 분할

---

## 17. Data Table (데이터 테이블)

```html
<section class="slide slide--light">
  <h2>분기별 실적</h2>
  <div class="data-table">
    <table>
      <thead>
        <tr>
          <th>분기</th>
          <th>매출</th>
          <th>영업이익</th>
          <th>성장률</th>
        </tr>
      </thead>
      <tbody>
        <tr class="fragment fade-up" data-step="0">
          <td>2025 Q1</td>
          <td>₩12.5B</td>
          <td>₩2.1B</td>
          <td>+15%</td>
        </tr>
        <tr class="fragment fade-up" data-step="1">
          <td>2025 Q2</td>
          <td>₩14.2B</td>
          <td>₩2.8B</td>
          <td>+13.6%</td>
        </tr>
        <tr class="fragment fade-up" data-step="2">
          <td>2025 Q3</td>
          <td>₩15.8B</td>
          <td>₩3.2B</td>
          <td>+11.3%</td>
        </tr>
        <tr class="fragment fade-up" data-step="3">
          <td>2025 Q4</td>
          <td>₩18.1B</td>
          <td>₩4.0B</td>
          <td>+14.6%</td>
        </tr>
      </tbody>
    </table>
  </div>
</section>
```

- `.data-table`: 테이블 래퍼, 홀짝 행 줄무늬(alternating stripes) 자동 적용
- 단순 `<table>` + `<thead>` / `<tbody>` 구조
- **분량**: 4~6열 x 6~10행. 초과 시 슬라이드 분할

---

## 18. Icon Grid (아이콘 그리드)

```html
<section class="slide slide--light">
  <h2>핵심 서비스</h2>
  <div class="icon-grid">
    <div class="icon-item fragment fade-up" data-step="0">
      <div class="icon-circle">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="3" y="3" width="18" height="18" rx="3" stroke="#2d2d8e" stroke-width="2"/>
          <path d="M8 12h8M12 8v8" stroke="#2d2d8e" stroke-width="2"/>
        </svg>
      </div>
      <h3>데이터 수집</h3>
      <p>실시간 센서 데이터 자동 수집</p>
    </div>
    <div class="icon-item fragment fade-up" data-step="1">
      <div class="icon-circle">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="12" cy="12" r="9" stroke="#2d2d8e" stroke-width="2"/>
          <path d="M12 7v5l3 3" stroke="#2d2d8e" stroke-width="2"/>
        </svg>
      </div>
      <h3>실시간 분석</h3>
      <p>AI 기반 실시간 이상 탐지</p>
    </div>
    <div class="icon-item fragment fade-up" data-step="2">
      <div class="icon-circle">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M3 17l6-6 4 4 8-8" stroke="#2d2d8e" stroke-width="2"/>
          <path d="M17 3h4v4" stroke="#2d2d8e" stroke-width="2"/>
        </svg>
      </div>
      <h3>리포트 생성</h3>
      <p>맞춤형 자동 보고서 생성</p>
    </div>
  </div>
</section>
```

- `.icon-grid`: 3열 CSS Grid (gap: 40px)
- `.icon-item`: 아이콘 + 제목 + 설명 수직 배치
- `.icon-circle`: 원형 배경 (연한 `#2d2d8e` 반투명) 안에 SVG 아이콘
- **아이콘 생성 규칙**: 24x24 기하학 SVG (rect, circle, path). 없으면 텍스트 이니셜 fallback
- **분량**: 1행(3개) 또는 2행(6개). 초과 시 슬라이드 분할

---

## 19. Bento Grid (벤토 그리드)

```html
<section class="slide slide--light">
  <h2>플랫폼 구성</h2>
  <div class="bento-grid">
    <div class="bento-item bento-wide bento-accent fragment fade-up" data-step="0">
      <h3>통합 대시보드</h3>
      <p>전체 시스템 상태를 한눈에 모니터링</p>
    </div>
    <div class="bento-item fragment fade-up" data-step="1">
      <h3>알림 시스템</h3>
      <p>실시간 이상 감지 알림</p>
    </div>
    <div class="bento-item fragment fade-up" data-step="2">
      <h3>리포트</h3>
      <p>맞춤형 자동 보고서</p>
    </div>
    <div class="bento-item fragment fade-up" data-step="3">
      <h3>API 연동</h3>
      <p>외부 시스템 통합</p>
    </div>
    <div class="bento-item bento-tall fragment fade-up" data-step="4">
      <h3>데이터 저장소</h3>
      <p>안전한 클라우드 스토리지</p>
    </div>
  </div>
</section>
```

- `.bento-grid`: CSS Grid (비대칭 레이아웃)
- `.bento-item`: 기본 셀 (흰 배경, 라운드 카드)
- `.bento-wide`: `grid-column: span 2` (가로 2칸 차지)
- `.bento-tall`: `grid-row: span 2` (세로 2칸 차지)
- `.bento-accent`: 강조 셀 (`#2d2d8e` 배경, 흰 텍스트)
- **분량**: 4~6셀. 초과 시 슬라이드 분할

---

## 20. Quote (인용)

```html
<section class="slide slide--light">
  <div class="quote-slide">
    <div class="quote-mark fragment fade-up" data-step="0">&ldquo;</div>
    <blockquote class="fragment fade-up" data-step="0">
      기술은 도구일 뿐이다. 중요한 것은 그 도구를
      어떻게 활용하느냐에 달려 있다.
    </blockquote>
    <div class="quote-author fragment fade-up" data-step="1">
      <span class="author-name">홍길동</span>
      <span class="author-title">STALAB 대표이사</span>
    </div>
  </div>
</section>
```

- `.quote-slide`: 전체 중앙 정렬 컨테이너
- `.quote-mark`: 대형 장식 따옴표 (160px, `#2d2d8e` 반투명)
- `<blockquote>`: 인용문 본문 (큰 글씨, 중앙 정렬)
- `.quote-author`: 저자 정보 컨테이너
- `.author-name`: 이름 (볼드), `.author-title`: 직함/소속
- **h2 제목 불필요**: 인용문 자체가 콘텐츠
- **분량**: 인용문 3줄 이내. 초과 시 문장 축약

---

## 21. Section Divider (섹션 구분)

```html
<section class="slide slide--divider">
  <div class="divider-number fragment fade-up" data-step="0">02</div>
  <h2 class="fragment fade-up" data-step="1">핵심 기술</h2>
  <p class="divider-subtitle fragment fade-up" data-step="2">AI 기반 스마트 팩토리 솔루션</p>
</section>
```

- **`slide--divider`** 사용 (라이트 배경 — `.slide--light`와 동일 배경)
- `.divider-number`: 대형 섹션 번호 (160px, `rgba(45,45,142,0.1)` 투명 Primary)
- `<h2>`: 섹션 제목 (`#1a1a2e` Heading 색상)
- `.divider-subtitle`: 부제 (`#888` 라이트 회색)
- **분량**: 번호 + 제목 + 부제 1줄. 최소한의 텍스트로 구성
- **주의**: `<p>`에 반드시 `class="divider-subtitle"` 추가 (CSS 셀렉터 매칭 필요)

---

## 22. Pyramid (피라미드 계층)

```html
<section class="slide slide--light">
  <h2>역량 피라미드</h2>
  <div class="pyramid">
    <div class="pyramid-tier fragment fade-up" data-step="0" style="--tier-width:30%">
      <h3>전략</h3>
      <p>비전과 방향 설정</p>
    </div>
    <div class="pyramid-tier fragment fade-up" data-step="1" style="--tier-width:55%">
      <h3>운영 관리</h3>
      <p>프로세스 최적화</p>
    </div>
    <div class="pyramid-tier fragment fade-up" data-step="2" style="--tier-width:80%">
      <h3>기술 인프라</h3>
      <p>시스템 기반 구축</p>
    </div>
  </div>
</section>
```

- `.pyramid`: 수직 flex, 중앙 정렬 (위→아래 좁음→넓음)
- `.pyramid-tier`: `--tier-width` CSS 변수로 너비 제어 (30%→55%→80% 등)
- 색상 그라데이션: 1단계 `#1a1a5e`, 2단계 `#2d2d8e`, 3단계 `#4a4abf`, ...
- **텍스트 색상**: `h3`, `p` 모두 흰색 계열 (CSS에서 자동 적용). **HTML에서 별도 색상 지정 불필요**
- **마크업**: `<h3>제목</h3><p>설명</p>` 구조 사용 (plain text 아닌 구조화 마크업)
- **분량**: 3~5단계. 제목 12자 + 설명 20자 이내. 초과 시 축약

---

## 23. Agenda/TOC (목차)

```html
<section class="slide slide--light">
  <h2>목차</h2>
  <div class="agenda-list">
    <div class="agenda-item fragment fade-up" data-step="0">
      <span class="agenda-num">01</span>
      <span class="agenda-title">회사 소개</span>
    </div>
    <div class="agenda-item active fragment fade-up" data-step="1">
      <span class="agenda-num">02</span>
      <span class="agenda-title">핵심 기술</span>
    </div>
    <div class="agenda-item fragment fade-up" data-step="2">
      <span class="agenda-num">03</span>
      <span class="agenda-title">사업 실적</span>
    </div>
    <div class="agenda-item fragment fade-up" data-step="3">
      <span class="agenda-num">04</span>
      <span class="agenda-title">향후 계획</span>
    </div>
  </div>
</section>
```

- `.agenda-list`: 수직 리스트 컨테이너
- `.agenda-item`: 번호 + 제목 행 (hover 효과)
- `.agenda-num`: 2자리 섹션 번호 (`#2d2d8e`, 볼드)
- `.agenda-title`: 섹션 제목
- `.active`: 현재 섹션 강조 (배경색 + 볼드 + `#2d2d8e` 좌측 보더)
- **분량**: 3~6개 항목. 초과 시 슬라이드 분할

---

## 24. Venn Diagram (벤 다이어그램)

```html
<section class="slide slide--light">
  <h2>기술 융합 영역</h2>
  <div class="image-container fragment fade-up" data-step="0">
    <!-- svg-templates.md의 Venn 템플릿 사용 -->
    <svg viewBox="0 0 1000 700" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-height:580px">
      <!-- Venn SVG: 겹치는 원 + 라벨 -->
      <!-- svg-templates.md 참조 -->
    </svg>
  </div>
  <p class="image-caption fragment fade-up" data-step="1">Figure 1. AI-IoT-Cloud 융합 영역</p>
</section>
```

- `.image-container`를 사용하며 SVG 인라인 삽입. **반드시** `style="flex:none;margin-top:12px;"` 적용
- SVG에 `style="width:70%;max-height:480px"` 적용 (전체 너비 사용 시 헤더 쏠림 발생)
- svg-templates.md의 Venn 템플릿에서 원 수/라벨만 교체
- **분량**: 2~3원. 원당 라벨 8자 이내. 교집합 영역 라벨 포함

---

## 레이아웃 선택 가이드

| 콘텐츠 유형 | 추천 레이아웃 |
|-------------|--------------|
| 시간 흐름/일정 | Timeline (9), Roadmap (13) |
| 절차/방법론 | Step-by-Step (10), Cycle (12) |
| 수치 변환 | Funnel (11), Pyramid (22) |
| 비교/분석 | Before/After (14), Pros/Cons (15), Comparison Matrix (16) |
| 데이터 나열 | Data Table (17), Comparison Matrix (16) |
| 기능/서비스 소개 | Icon Grid (18), Bento Grid (19) |
| 인용/강조 | Quote (20), Section Divider (21) |
| 구조/목차 | Agenda/TOC (23) |
| 관계/교집합 | Venn Diagram (24), Cycle (12) |
