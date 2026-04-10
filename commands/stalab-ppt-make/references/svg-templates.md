# SVG 다이어그램 템플릿

## 사용법

1. 원하는 템플릿의 SVG 코드를 슬라이드 HTML에 복사
2. `<!-- LABEL: identifier -->` 주석을 검색하여 바로 아래 `<text>` 요소의 내용을 교체
3. `arrow-{N}` 마커의 `{N}`을 슬라이드 번호로 치환 (chunk 모드에서 id 충돌 방지)
4. 노드 수 변경 시 각 템플릿 하단의 "조정 가이드" 참고

### 공통 스타일 규칙
- Primary: `#2d2d8e` / Text: `#1a1a2e` / Border: `#e0e0e0` / BG: `#f0f0f0` / Muted: `#888`
- 박스 모서리: `rx="12"`
- 폰트: `Freesentation, system-ui, sans-serif`
- 모든 SVG에 `style="width:100%;max-height:580px"` 적용

---

## 템플릿 1: 아키텍처 (3-tier)

```svg
<svg viewBox="0 0 1600 500" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-height:580px">
  <defs>
    <marker id="arrow-{N}" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#2d2d8e"/>
    </marker>
    <style>
      text { font-family: Freesentation, system-ui, sans-serif; }
    </style>
  </defs>

  <!-- Tier 1: 메인 시스템 -->
  <!-- LABEL: main-system -->
  <rect x="600" y="20" width="400" height="70" rx="12" fill="#2d2d8e"/>
  <text x="800" y="63" text-anchor="middle" fill="#fff" font-size="22" font-weight="700">메인 시스템</text>

  <!-- 화살표: Tier 1 → Tier 2 -->
  <line x1="800" y1="90" x2="800" y2="170" stroke="#2d2d8e" stroke-width="2" marker-end="url(#arrow-{N})"/>

  <!-- Tier 2: 프로토콜/브릿지 바 -->
  <!-- LABEL: bridge -->
  <rect x="200" y="180" width="1200" height="50" rx="12" fill="#f0f0f0" stroke="#ccc" stroke-width="2"/>
  <text x="800" y="212" text-anchor="middle" fill="#1a1a2e" font-size="18" font-weight="500">프로토콜 / 브릿지</text>

  <!-- 화살표: Tier 2 → Tier 3 (3개) -->
  <line x1="400" y1="230" x2="400" y2="310" stroke="#2d2d8e" stroke-width="2" marker-end="url(#arrow-{N})"/>
  <line x1="800" y1="230" x2="800" y2="310" stroke="#2d2d8e" stroke-width="2" marker-end="url(#arrow-{N})"/>
  <line x1="1200" y1="230" x2="1200" y2="310" stroke="#2d2d8e" stroke-width="2" marker-end="url(#arrow-{N})"/>

  <!-- Tier 3: 서비스 노드 3개 -->
  <!-- LABEL: service-1 -->
  <rect x="250" y="320" width="300" height="70" rx="12" fill="#fff" stroke="#2d2d8e" stroke-width="2"/>
  <text x="400" y="363" text-anchor="middle" fill="#1a1a2e" font-size="18" font-weight="500">서비스 A</text>

  <!-- LABEL: service-2 -->
  <rect x="650" y="320" width="300" height="70" rx="12" fill="#fff" stroke="#2d2d8e" stroke-width="2"/>
  <text x="800" y="363" text-anchor="middle" fill="#1a1a2e" font-size="18" font-weight="500">서비스 B</text>

  <!-- LABEL: service-3 -->
  <rect x="1050" y="320" width="300" height="70" rx="12" fill="#fff" stroke="#2d2d8e" stroke-width="2"/>
  <text x="1200" y="363" text-anchor="middle" fill="#1a1a2e" font-size="18" font-weight="500">서비스 C</text>
</svg>
```

### 노드 수 조정 가이드

하단 서비스 노드 수를 변경할 때 X 좌표 공식:

```
centerX(i) = 1600 / (n + 1) * i     (i = 1 ~ n)
rectX(i)   = centerX(i) - 150       (박스 폭 300 기준)
```

| 노드 수 (n) | X 중심 좌표                        |
|-------------|-----------------------------------|
| 3           | 400, 800, 1200                    |
| 4           | 320, 640, 960, 1280               |
| 5           | 267, 533, 800, 1067, 1333         |

화살표 `x1`/`x2`도 동일한 centerX 값으로 맞춘다.

---

## 템플릿 2: 플로우 (좌 -> 우 프로세스)

```svg
<svg viewBox="0 0 1600 400" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-height:580px">
  <defs>
    <marker id="arrow-{N}" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#2d2d8e"/>
    </marker>
    <style>
      text { font-family: Freesentation, system-ui, sans-serif; }
    </style>
  </defs>

  <!-- 노드 1 -->
  <!-- LABEL: step-1-title -->
  <!-- LABEL: step-1-sub -->
  <rect x="40" y="130" width="300" height="120" rx="12" fill="#fff" stroke="#e0e0e0" stroke-width="2"/>
  <text x="190" y="180" text-anchor="middle" fill="#1a1a2e" font-size="20" font-weight="700">단계 1</text>
  <text x="190" y="210" text-anchor="middle" fill="#888" font-size="15">설명 텍스트</text>

  <!-- 화살표 1→2 -->
  <line x1="340" y1="190" x2="420" y2="190" stroke="#2d2d8e" stroke-width="2" marker-end="url(#arrow-{N})"/>
  <!-- LABEL: arrow-label-1 -->
  <text x="380" y="175" text-anchor="middle" fill="#888" font-size="13"></text>

  <!-- 노드 2 -->
  <!-- LABEL: step-2-title -->
  <!-- LABEL: step-2-sub -->
  <rect x="430" y="130" width="300" height="120" rx="12" fill="#fff" stroke="#e0e0e0" stroke-width="2"/>
  <text x="580" y="180" text-anchor="middle" fill="#1a1a2e" font-size="20" font-weight="700">단계 2</text>
  <text x="580" y="210" text-anchor="middle" fill="#888" font-size="15">설명 텍스트</text>

  <!-- 화살표 2→3 -->
  <line x1="730" y1="190" x2="810" y2="190" stroke="#2d2d8e" stroke-width="2" marker-end="url(#arrow-{N})"/>
  <!-- LABEL: arrow-label-2 -->
  <text x="770" y="175" text-anchor="middle" fill="#888" font-size="13"></text>

  <!-- 노드 3 -->
  <!-- LABEL: step-3-title -->
  <!-- LABEL: step-3-sub -->
  <rect x="820" y="130" width="300" height="120" rx="12" fill="#fff" stroke="#e0e0e0" stroke-width="2"/>
  <text x="970" y="180" text-anchor="middle" fill="#1a1a2e" font-size="20" font-weight="700">단계 3</text>
  <text x="970" y="210" text-anchor="middle" fill="#888" font-size="15">설명 텍스트</text>

  <!-- 화살표 3→4 -->
  <line x1="1120" y1="190" x2="1200" y2="190" stroke="#2d2d8e" stroke-width="2" marker-end="url(#arrow-{N})"/>
  <!-- LABEL: arrow-label-3 -->
  <text x="1160" y="175" text-anchor="middle" fill="#888" font-size="13"></text>

  <!-- 노드 4 -->
  <!-- LABEL: step-4-title -->
  <!-- LABEL: step-4-sub -->
  <rect x="1210" y="130" width="300" height="120" rx="12" fill="#fff" stroke="#e0e0e0" stroke-width="2"/>
  <text x="1360" y="180" text-anchor="middle" fill="#1a1a2e" font-size="20" font-weight="700">단계 4</text>
  <text x="1360" y="210" text-anchor="middle" fill="#888" font-size="15">설명 텍스트</text>
</svg>
```

### 노드 수 조정 가이드

X 좌표 공식 (노드 폭 300, 간격 gap):

```
gap       = (1600 - n * 300) / (n + 1)
rectX(i)  = gap * i + 300 * (i - 1)          (i = 1 ~ n)
centerX(i)= rectX(i) + 150
```

| 노드 수 (n) | gap  | rectX 시작값                     |
|-------------|------|----------------------------------|
| 3           | 175  | 175, 650, 1125                   |
| 4           | 80   | 80, 460, 840, 1220               |
| 5           | 50   | 50, 370, 690, 1010, 1330         |

화살표: `x1 = rectX(i) + 300`, `x2 = rectX(i+1)`. 라벨: 중간점.

---

## 템플릿 3: 순환 다이어그램 (Cycle)

```svg
<svg viewBox="0 0 800 700" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-height:580px">
  <defs>
    <marker id="arrow-{N}" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#2d2d8e"/>
    </marker>
    <style>
      text { font-family: Freesentation, system-ui, sans-serif; }
    </style>
  </defs>

  <!-- 중심: (400, 350), 반지름: 200 -->
  <!-- 노드 위치: top(400,150), right(600,350), bottom(400,550), left(200,350) -->

  <!-- 노드 1: 상단 -->
  <!-- LABEL: cycle-1 -->
  <rect x="300" y="115" width="200" height="70" rx="12" fill="#fff" stroke="#2d2d8e" stroke-width="2"/>
  <text x="400" y="158" text-anchor="middle" fill="#1a1a2e" font-size="18" font-weight="700">단계 1</text>

  <!-- 노드 2: 우측 -->
  <!-- LABEL: cycle-2 -->
  <rect x="500" y="315" width="200" height="70" rx="12" fill="#fff" stroke="#2d2d8e" stroke-width="2"/>
  <text x="600" y="358" text-anchor="middle" fill="#1a1a2e" font-size="18" font-weight="700">단계 2</text>

  <!-- 노드 3: 하단 -->
  <!-- LABEL: cycle-3 -->
  <rect x="300" y="515" width="200" height="70" rx="12" fill="#fff" stroke="#2d2d8e" stroke-width="2"/>
  <text x="400" y="558" text-anchor="middle" fill="#1a1a2e" font-size="18" font-weight="700">단계 3</text>

  <!-- 노드 4: 좌측 -->
  <!-- LABEL: cycle-4 -->
  <rect x="100" y="315" width="200" height="70" rx="12" fill="#fff" stroke="#2d2d8e" stroke-width="2"/>
  <text x="200" y="358" text-anchor="middle" fill="#1a1a2e" font-size="18" font-weight="700">단계 4</text>

  <!-- 곡선 화살표: 1→2 (상단→우측) -->
  <path d="M 490 175 Q 560 220 540 310" fill="none" stroke="#2d2d8e" stroke-width="2" marker-end="url(#arrow-{N})"/>

  <!-- 곡선 화살표: 2→3 (우측→하단) -->
  <path d="M 540 390 Q 560 480 490 525" fill="none" stroke="#2d2d8e" stroke-width="2" marker-end="url(#arrow-{N})"/>

  <!-- 곡선 화살표: 3→4 (하단→좌측) -->
  <path d="M 310 525 Q 240 480 260 390" fill="none" stroke="#2d2d8e" stroke-width="2" marker-end="url(#arrow-{N})"/>

  <!-- 곡선 화살표: 4→1 (좌측→상단) -->
  <path d="M 260 310 Q 240 220 310 175" fill="none" stroke="#2d2d8e" stroke-width="2" marker-end="url(#arrow-{N})"/>
</svg>
```

### 노드 수 조정 가이드

중심 `(cx, cy) = (400, 350)`, 반지름 `r = 200`.

각 노드의 중심 좌표:

```
x(i) = cx + r * sin(2pi * i / n)
y(i) = cy - r * cos(2pi * i / n)
```

| 노드 수 | 각도 (deg) | 좌표 (cx=400, cy=350, r=200)                                         |
|---------|-----------|----------------------------------------------------------------------|
| 3       | 0, 120, 240 | (400,150), (573,450), (227,450)                                     |
| 4       | 0, 90, 180, 270 | (400,150), (600,350), (400,550), (200,350)                      |
| 5       | 0, 72, 144, 216, 288 | (400,150), (590,262), (517,490), (283,490), (210,262)       |
| 6       | 0, 60, 120, 180, 240, 300 | (400,150), (573,250), (573,450), (400,550), (227,450), (227,250) |

`rect` 좌표: `x(i) - 100`, `y(i) - 35` (박스 200x70 기준).

곡선 화살표의 제어점은 두 노드의 중간점에서 중심 반대쪽으로 약 60px 밀어낸 좌표를 사용.

---

## 템플릿 4: 벤 다이어그램 (Venn)

### 4-A: 2원 벤 다이어그램

```svg
<svg viewBox="0 0 900 600" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-height:580px">
  <defs>
    <style>
      text { font-family: Freesentation, system-ui, sans-serif; }
    </style>
  </defs>

  <!-- 원 A -->
  <circle cx="320" cy="300" r="200" stroke="#2d2d8e" stroke-width="2" fill="#2d2d8e" fill-opacity="0.12"/>

  <!-- 원 B -->
  <circle cx="580" cy="300" r="200" stroke="#2d2d8e" stroke-width="2" fill="#2d2d8e" fill-opacity="0.12"/>

  <!-- LABEL: venn2-left -->
  <text x="230" y="305" text-anchor="middle" fill="#1a1a2e" font-size="20" font-weight="700">영역 A</text>

  <!-- LABEL: venn2-right -->
  <text x="670" y="305" text-anchor="middle" fill="#1a1a2e" font-size="20" font-weight="700">영역 B</text>

  <!-- LABEL: venn2-intersection -->
  <text x="450" y="305" text-anchor="middle" fill="#2d2d8e" font-size="18" font-weight="700">교집합</text>
</svg>
```

### 4-B: 3원 벤 다이어그램

```svg
<svg viewBox="0 0 900 600" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-height:580px">
  <defs>
    <style>
      text { font-family: Freesentation, system-ui, sans-serif; }
    </style>
  </defs>

  <!-- 원 A (상단 중앙) -->
  <circle cx="450" cy="220" r="180" stroke="#2d2d8e" stroke-width="2" fill="#2d2d8e" fill-opacity="0.12"/>

  <!-- 원 B (좌하) -->
  <circle cx="300" cy="420" r="180" stroke="#2d2d8e" stroke-width="2" fill="#2d2d8e" fill-opacity="0.12"/>

  <!-- 원 C (우하) -->
  <circle cx="600" cy="420" r="180" stroke="#2d2d8e" stroke-width="2" fill="#2d2d8e" fill-opacity="0.12"/>

  <!-- 개별 영역 라벨 -->
  <!-- LABEL: venn3-a -->
  <text x="450" y="140" text-anchor="middle" fill="#1a1a2e" font-size="18" font-weight="700">A</text>

  <!-- LABEL: venn3-b -->
  <text x="195" y="460" text-anchor="middle" fill="#1a1a2e" font-size="18" font-weight="700">B</text>

  <!-- LABEL: venn3-c -->
  <text x="705" y="460" text-anchor="middle" fill="#1a1a2e" font-size="18" font-weight="700">C</text>

  <!-- 쌍 교집합 라벨 -->
  <!-- LABEL: venn3-ab -->
  <text x="340" y="290" text-anchor="middle" fill="#2d2d8e" font-size="15" font-weight="500">A+B</text>

  <!-- LABEL: venn3-ac -->
  <text x="560" y="290" text-anchor="middle" fill="#2d2d8e" font-size="15" font-weight="500">A+C</text>

  <!-- LABEL: venn3-bc -->
  <text x="450" y="480" text-anchor="middle" fill="#2d2d8e" font-size="15" font-weight="500">B+C</text>

  <!-- 중심 교집합 라벨 -->
  <!-- LABEL: venn3-center -->
  <text x="450" y="380" text-anchor="middle" fill="#2d2d8e" font-size="16" font-weight="700">A+B+C</text>
</svg>
```

### 벤 다이어그램 조정 가이드

**2원**: 교집합 영역 크기는 두 원의 거리로 조절. 거리가 가까울수록 교집합이 넓어진다.
- 현재 거리: `580 - 320 = 260` (반지름 200의 경우 적당한 겹침)
- 겹침 없음: 거리 >= `r * 2` (400 이상)
- 완전 겹침: 거리 = 0

**3원**: 세 원의 중심은 정삼각형 배치. 현재 간격 기준:
- 상단↔좌하 거리: ~250
- 좌하↔우하 거리: 300
- 반지름 180에서 적절한 겹침 유지
