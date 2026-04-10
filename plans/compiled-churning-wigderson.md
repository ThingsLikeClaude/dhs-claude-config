# STALAB 템플릿 개선 계획 — make-slide 장점 통합

## Context
STALAB `slide-template.html`은 기업 브랜딩(헤더/푸터, 챕터 네비게이션, 1920×1080 스케일링, 프래그먼트 시스템, 차트 애니메이션)이 강점이지만, **레이아웃 다양성, 코드 블록 syntax highlighting, 발표자 노트 UX, 이미지 placeholder, PDF 인쇄, 다이어그램 자동 생성** 등에서 make-slide 스킬 대비 부족한 부분이 있다. 유저가 7개 개선 항목 전체 적용을 요청.

## 수정 대상 파일
1. **`references/slide-template.html`** — 메인 템플릿 (CSS + HTML 데모 + JS)
2. **`.claude/commands/stalab-ppt-make/SKILL.md`** — 스킬 문서에 새 기능 반영
3. **`.claude/commands/stalab-ppt-make/references/layouts-core.md`** — 레이아웃 가이드 업데이트

## 변경 사항 (7개)

### 1. 발표자 노트 → 팝업 방식
**현재**: 하단 30vh 인라인 패널 (`.show-notes aside.notes`)  
**변경**: `window.open()` 팝업 (make-slide core-features.md 패턴)

- CSS: `.show-notes aside.notes` 블록 제거
- JS: `toggleNotes()` / `updateNotes()` 함수 추가 — `S` 키 핸들러에서 팝업 토글
- 팝업 스타일: 다크 배경, 현재 슬라이드 번호 + 노트 텍스트 + 다음 슬라이드 프리뷰
- 슬라이드 전환 시 자동 업데이트 (`goToSlide` 내 `updateNotes()` 호출)
- HTML 데모: `<aside class="notes">` 대신 `data-notes` 속성으로 변환

### 2. CSS 커스텀 프로퍼티 전환
**현재**: `#2d2d8e`, `#1a1a2e`, `#e0e0e0` 등 하드코딩 (~70+ 곳)  
**변경**: `:root` 변수 선언 후 전체 치환

```css
:root {
  --c-primary: #2d2d8e;
  --c-heading: #1a1a2e;
  --c-body: #444;
  --c-muted: #666;
  --c-light: #888;
  --c-bg: #f0f0f0;
  --c-card: #fff;
  --c-border: #e0e0e0;
  --c-positive: #059669;
  --c-negative: #e11d48;
  --c-primary-10: rgba(45,45,142,0.1);
  --c-primary-15: rgba(45,45,142,0.15);
}
```

- 모든 색상 리터럴 → `var(--c-*)` 치환
- pyramid-tier 개별 색상은 `opacity` 기반으로 전환
- SVG `fill`/`stroke`는 `currentColor` 또는 인라인 `var()` 사용 (SVG 내 var() 지원됨)

### 3. 레이아웃 모드 추가 (Wide / Split / Editorial)
**현재**: 모든 콘텐츠가 `.slide--light` (중앙 정렬, padding 40px 120px)  
**변경**: 3개 레이아웃 클래스 추가

```css
/* Wide: 풀폭, 좌정렬 */
.slide--wide {
  align-items: flex-start;
  text-align: left;
  padding: 40px 80px;
}
.slide--wide .content { width: 100%; max-width: 100%; }

/* Split: 2열 그리드 (텍스트 + 비주얼) */
.slide--split {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
  align-items: center;
  padding: 40px 60px;
  text-align: left;
}

/* Editorial: 매거진 스타일, 비대칭 */
.slide--editorial {
  justify-content: flex-end;
  align-items: flex-start;
  text-align: left;
  padding: 60px 80px 80px;
}
.slide--editorial h2 {
  font-size: clamp(2.5rem, 5vw, 4rem);
  font-weight: 900;
  max-width: 70%;
}
.slide--editorial p { max-width: 50%; }
```

- 기존 `.slide--light` 유지 (기본 Centered)
- 데모 HTML에 각 레이아웃 예시 슬라이드 1개씩 추가
- SKILL.md에 레이아웃 선택 가이드 추가

### 4. Prism.js 조건부 로드
**현재**: 수동 `.kw`, `.fn`, `.str` 클래스  
**변경**: Prism.js CDN 조건부 사용

- `<head>`에 조건부 CDN 링크 (주석으로 "코드 블록이 있을 때만 포함"):
  ```html
  <!-- Include only when code blocks exist -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
  ```
- `.code-block` 내부를 `<pre><code class="language-*">` 구조로 변경
- 기존 `.kw`, `.fn`, `.str` CSS 유지 (Prism 미로드 시 fallback)
- JetBrains Mono CDN 추가 (코드 폰트)
- 데모 코드 블록을 Prism 호환 마크업으로 교체

### 5. 이미지 Placeholder 개선
**현재**: `#e8e8e8` + `2px dashed #ccc` (조잡)  
**변경**: gradient 배경 + 아이콘 방식

```css
.image-placeholder {
  background: linear-gradient(135deg, var(--c-bg) 0%, #e8e8f0 100%);
  border: none;
  border-radius: 16px;
  box-shadow: inset 0 2px 8px rgba(0,0,0,0.06);
}
.placeholder-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 12px;
}
.placeholder-label {
  font-size: 16px;
  color: var(--c-light);
  letter-spacing: 1px;
  text-transform: uppercase;
}
```

### 6. PDF Print CSS
**현재**: 없음  
**변경**: `@media print` 블록 추가

```css
@media print {
  .progress-container, .persistent-header, .persistent-footer,
  .chapter-nav, #gridCanvas, [class*="btn"] { display: none !important; }
  
  .deck { display: block; width: auto; height: auto; overflow: visible; }
  .slides { transform: none !important; width: 100%; height: auto; }
  .slide-area { position: static; overflow: visible; }
  
  .slide {
    position: relative !important;
    opacity: 1 !important;
    pointer-events: auto !important;
    page-break-after: always;
    display: flex !important;
    width: 100vw;
    height: 100vh;
  }
  
  .fragment { opacity: 1 !important; visibility: visible !important;
    transform: none !important; filter: none !important; }
  
  @page { size: landscape; margin: 0; }
}
```

### 7. Mermaid.js CDN 통합
**현재**: SVG 수동 작성  
**변경**: Mermaid.js 조건부 로드 + 자동 렌더링

- CDN 추가 (조건부):
  ```html
  <!-- Include only when mermaid diagrams exist -->
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
  ```
- 슬라이드 내 Mermaid 블록 구조:
  ```html
  <div class="mermaid-wrapper fragment fade-up" data-step="0">
    <pre class="mermaid">
      graph LR
        A[Client] --> B[API Gateway]
        B --> C[Service A]
        B --> D[Service B]
    </pre>
  </div>
  ```
- JS 초기화: `mermaid.initialize({ theme: 'neutral', fontFamily: 'Freesentation' })`
- STALAB 색상 커스텀:
  ```js
  mermaid.initialize({
    theme: 'base',
    themeVariables: {
      primaryColor: '#2d2d8e',
      primaryTextColor: '#fff',
      lineColor: '#2d2d8e',
      secondaryColor: '#f0f0f0'
    }
  });
  ```
- 데모 HTML에 Mermaid 다이어그램 슬라이드 1개 추가
- 기존 SVG 템플릿은 유지 (Mermaid 미사용 시 fallback)

## 작업 순서
1. CSS 커스텀 프로퍼티 전환 (#2) — 다른 변경의 기반
2. 발표자 노트 팝업 (#1) — JS 변경
3. 레이아웃 모드 추가 (#3) — CSS + 데모 HTML
4. Prism.js 조건부 로드 (#4) — CDN + 코드 블록 마크업
5. 이미지 Placeholder 개선 (#5) — CSS만
6. PDF Print CSS (#6) — CSS만
7. Mermaid.js 통합 (#7) — CDN + JS + 데모 슬라이드
8. SKILL.md / layouts-core.md 문서 업데이트

## 검증
- 브라우저에서 `slide-template.html` 열어 모든 슬라이드 네비게이션 확인
- `S` 키로 팝업 노트 토글 확인
- 각 레이아웃 모드 데모 슬라이드 시각 확인
- 코드 블록 syntax highlighting 확인
- `Ctrl+P`로 PDF 인쇄 프리뷰 확인
- Mermaid 다이어그램 렌더링 확인
- 기존 기능 유지: 챕터 네비게이션, 프래그먼트, 차트 애니메이션, 커버 스크램블
