# 청크 생성 모드 (Chunked Generation)

> 이 파일은 10장 초과 프레젠테이션 생성 시 Read로 참조한다. SKILL.md에서 직접 로드하지 않음.

---

## 트리거 조건

다음 중 하나에 해당하면 청크 모드를 자동 활성화:
- 예상 슬라이드 수 **10장 초과**
- 사용자가 "많은", "30장", "대량" 등 대규모 키워드 사용
- 콘텐츠 분석 결과 단일 배치로 생성하기에 토큰 부담이 큰 경우

---

## 워크플로우

```
Phase 0: 아웃라인    → 전체 슬라이드 목록 (번호, 제목, 레이아웃) 제시
Phase 1: 1차 생성    → Cover + 슬라이드 1~5 (Bash cp로 템플릿 복사 + Edit로 삽입)
Phase 2: 2차 추가    → 슬라이드 6~10 (Edit로 .slide-area에 삽입)
Phase 3: 3차 추가    → 슬라이드 11~15 (Edit로 추가)
...
Phase N: 최종 확인   → 브라우저 열기 + 전체 슬라이드 목록 출력
```

---

## Phase 0: 아웃라인 (필수)

청크 모드에서는 코드 생성 전에 **반드시 아웃라인을 먼저 제시**하고 사용자 확인을 받는다.

아웃라인 형식:
```
📋 슬라이드 아웃라인 (총 N장)

[Chunk 1] 슬라이드 1~5
  1. Cover — 프레젠테이션 제목
  2. Text — 프로젝트 배경 및 목적
  3. Card Grid — 핵심 목표 3가지
  4. Two-Column — AS-IS vs TO-BE
  5. Chart — 분기별 성과 추이

[Chunk 2] 슬라이드 6~10
  6.  KPI — 핵심 지표
  7.  Timeline — 마일스톤
  ...

[Chunk 3] 슬라이드 11~15
  11. Step-by-Step — 구현 과정
  ...
  15. Text — Q&A / 감사 인사

→ 이 구성으로 진행할까요? 수정할 부분이 있으면 말씀해주세요.
```

---

## Phase 1: 1차 생성 (Write)

1. `references/slide-template.html` 복사
2. `<title>`, header, footer 텍스트 수정
3. `.slide-area`에 Cover + 첫 번째 청크 슬라이드 삽입 (5장)
4. 파일 저장: `~/Downloads/{filename}.html`
5. `start` 명령으로 브라우저 열기
6. 사용자에게 진행 상황 보고:

```
✅ Chunk 1 완료 (슬라이드 1~5 / 총 15장)
📄 file:///C:/Users/{user}/Downloads/{filename}.html

다음 청크로 진행할까요? 수정할 부분이 있으면 먼저 말씀해주세요.
```

---

## Phase 2+: 추가 청크 (Edit)

1. 기존 파일의 `.slide-area` 마지막 `</section>` 뒤, `</div><!-- .slide-area -->` 앞에 새 슬라이드 삽입
2. Edit 도구의 `old_string`으로 삽입 위치를 특정:

```
삽입 앵커:
old_string: "    </div><!-- .slide-area -->"
new_string: "{새 슬라이드들}\n\n    </div><!-- .slide-area -->"
```

3. `start` 명령으로 브라우저 새로고침
4. 진행 상황 보고:

```
✅ Chunk {N} 완료 (슬라이드 {시작}~{끝} / 총 {전체}장)

다음 청크로 진행할까요?
```

---

## 청크 크기 가이드

| 슬라이드 유형 구성 | 권장 청크 크기 | 이유 |
|-------------------|---------------|------|
| Text/Two-Col 위주 | 5~6장 | HTML 경량, Edit 도구 안정성 확보 |
| Chart/KPI 포함 | 4~5장 | 데이터 변환 로직 포함 |
| SVG Diagram 포함 | 3~4장 | SVG 마크업이 무거움 |
| Code Block 포함 | 4~5장 | 구문 하이라이팅 마크업 |
| 혼합 구성 | **5장** | 안전한 기본값 |

---

## 청크 간 연속성 규칙

1. **레이아웃 연속 금지**: 청크 경계에서도 같은 레이아웃 3연속 금지 유지
2. **번호 연속**: 슬라이드 번호는 전체 기준으로 연속 (청크 내 리셋 없음)
3. **linearGradient ID 충돌 방지**: 차트가 여러 슬라이드에 있을 경우 `id="lineGrad"` → `id="lineGrad-{슬라이드번호}"` 로 고유화
4. **arrowhead ID 충돌 방지**: SVG diagram이 여러 장일 경우 `id="arrowhead-{슬라이드번호}"`로 고유화
