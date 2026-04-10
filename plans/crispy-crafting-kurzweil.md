# 애니메이션 개선 + 헤더/푸터 간격 통일 계획

## Context
현재 프레젠테이션(139장)의 UX 문제 3가지:
1. **Fragment 과다**: 매 슬라이드에서 Space를 4~7회 눌러야 모든 콘텐츠 표시. 발표 리듬 끊김
2. **애니메이션 단조로움**: 139장 전체가 `fade-up` 한 가지만 사용. `zoom-in`은 CSS 정의만 있고 미사용
3. **헤더/푸터 간격 비대칭**: 헤더 `padding: 52px 60px 16px`, 푸터 `padding: 20px 40px` — Copyright/페이지수가 하단에 달라붙음

## 수정 파일
- `C:/Users/f4u12/Downloads/claude-code-guide.html` — 현재 프레젠테이션 (CSS + 139장 HTML)
- `references/slide-template.html` — 템플릿 (CSS만)
- `SKILL.md` — 규칙 업데이트

---

## Part 1: Fragment 스텝 축소 (Space 0~2회로 제한)

### 원칙
- h2 제목: fragment 없이 즉시 표시
- 메인 콘텐츠 (카드, 불릿, 아이콘 등): `data-step="0"` + `auto-stagger`로 1회에 순차 등장
- 보충 설명/부연: `data-step="1"` (선택적)

### 적용 패턴

| 레이아웃 | Before (Space 횟수) | After (Space 횟수) |
|---------|-------------------|-------------------|
| Text (불릿 4개) | p(0)→li(1)→li(2)→li(3)→li(4) = 5회 | ul 전체(0) + 부연p(1) = 1~2회 |
| Card Grid 3장 | subtitle(0)→cards(1,1,1) = 2회 | cards auto-stagger(0) = 1회 |
| Two-Column | left-h3(0)→left-ul(1)→right-h3(2)→right-ul(3) = 4회 | left(0)→right(1) = 2회 |
| Icon Grid 4개 | subtitle(0)→items(1,1,1,1) = 2회 | items auto-stagger(0) = 1회 |
| Quote | quote(0)→부연(1) = 2회 | 유지 2회 |

### 구현 방법
1. 개별 `<li>` fragment 제거 → 부모 `<ul>` 또는 `<ul>` 전체에 fragment 1개
2. Card Grid, Icon Grid: 이미 `auto-stagger` 사용 중 → `data-step` 통합만
3. Two-Column: 좌측 전체(0), 우측 전체(1)로 통합
4. `data-step` 최대값을 1로 제한 (특수 케이스만 2 허용)

---

## Part 2: 애니메이션 다양화 (4종 추가)

### 추가 CSS (기존 2종 → 6종)

```css
/* 기존 */
.fragment.fade-up    → translateY(30px)     /* ↑ 아래→위 */
.fragment.zoom-in    → scale(0.9)           /* ⊕ 확대 등장 */

/* 신규 4종 */
.fragment.fade-left  → translateX(40px)     /* ← 우→좌 슬라이드 */
.fragment.fade-right → translateX(-40px)    /* → 좌→우 슬라이드 */
.fragment.fade-down  → translateY(-30px)    /* ↓ 위→아래 */
.fragment.blur-in    → filter:blur(8px) + scale(0.95) /* 블러→선명 */
```

### 레이아웃별 기본 애니메이션 매핑

| 레이아웃 | 애니메이션 | 이유 |
|---------|----------|------|
| Text (불릿) | `fade-up` | 가독성 기본 |
| Card Grid | `zoom-in` | 카드 팝업 느낌 |
| Two-Column 좌 | `fade-right` | 좌에서 진입 |
| Two-Column 우 | `fade-left` | 우에서 진입 |
| Code Block | `fade-up` | 안정적 |
| Quote | `blur-in` | 드라마틱 강조 |
| Icon Grid | `zoom-in` | 아이콘 팝업 |
| Step-by-Step | `fade-right` | 좌→우 진행감 |
| KPI | `zoom-in` | 숫자 강조 |
| Before/After | `fade-right`/`fade-left` | 비교감 |
| Data Table | `fade-up` | 안정적 |
| SVG Diagram | `fade-up` | 안정적 |

---

## Part 3: 헤더/푸터 간격 통일

### 현재 (비대칭)
```
Header: padding: 52px 60px 16px  → 위52, 좌우60, 아래16
Footer: padding: 20px 40px       → 위아래20, 좌우40
→ Copyright가 하단에 너무 달라붙음. 좌우도 40 vs 60 불일치
```

### 변경 (대칭)
```
Header: padding: 40px 60px 12px  → 위40, 좌우60, 아래12
Footer: padding: 12px 60px 40px  → 위12, 좌우60, 아래40
```

핵심: 좌우 60px 통일 + 외측 40px / 내측 12px 대칭 → 4모서리 도달 거리 동일

---

## 구현 순서

1. **CSS 추가**: 4종 새 애니메이션 클래스 (`fade-left`, `fade-right`, `fade-down`, `blur-in`)
2. **CSS 수정**: 헤더/푸터 padding 통일
3. **HTML 일괄 수정**: 139장의 fragment `data-step` 재매핑 + 애니메이션 클래스 교체
4. **템플릿 동기화**: `slide-template.html` CSS 동일하게 반영
5. **SKILL.md 규칙 추가**: 애니메이션 매핑 테이블 + fragment 최대 2스텝 규칙

## 검증
1. 브라우저에서 전체 슬라이드 넘기며 Space 횟수 확인 (0~2회)
2. 각 레이아웃별 다른 애니메이션 동작 확인
3. 전체화면에서 헤더/푸터 4모서리 간격 대칭 확인
