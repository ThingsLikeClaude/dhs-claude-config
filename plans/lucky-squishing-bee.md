# Plan: stalab-ppt-make Research Phase + Agent Team

## Context

현재 `stalab-ppt-make` 스킬은 **사용자가 콘텐츠를 직접 제공**해야 PPT를 생성한다. 하지만 실제 사용 시 "AI 반도체 시장 분석 PPT 만들어줘"처럼 **주제만 주는 경우**가 대부분이다.

이때 리서치 → 구조화 → PPT 생성까지 자동화하되, Gemini CLI(웹 리서치) + NotebookLM(소스 합성)을 활용하고, 3인 Agent Team으로 병렬/순차 수행하는 워크플로우를 추가한다.

## 변경 파일

| 파일 | 작업 | 내용 |
|------|------|------|
| `references/research.md` | **신규** | 리서치 Phase 전체 워크플로우, 에이전트 팀 구성, 프롬프트 템플릿, 핸드오프 프로토콜 |
| `SKILL.md` | **수정** | 레퍼런스 테이블에 research.md 추가, Step 0 라우팅 로직 (~25줄 추가) |

---

## Architecture

```
사용자: "AI 반도체 시장 분석 PPT 만들어줘"
         │
    ┌────▼────────────────┐
    │ Lead (main session) │ ← 오케스트레이터, 체크포인트 관리
    └──┬──────┬───────┬───┘
       │      │       │
  ┌────▼──┐ ┌▼────┐ ┌▼──────────┐
  │ mina  │ │ seo │ │ hana      │
  │리서처 │→│에디터│→│PPT 빌더   │
  │sonnet │ │sonnet│ │sonnet     │
  └───────┘ └──────┘ └───────────┘
```

### 파일 소유권 (충돌 방지)

| Agent | 소유 파일 | 역할 |
|-------|-----------|------|
| mina (리서처) | `/tmp/stalab-research/{slug}/raw-research.md` | 웹 리서치 + NotebookLM 합성 |
| seo (에디터) | `/tmp/stalab-research/{slug}/structured-outline.md` | 슬라이드 구조화 |
| hana (PPT빌더) | `~/Downloads/{filename}.html` | STALAB HTML 생성 |

### 실행 모드 (2종)

| 모드 | 트리거 | 체크포인트 | 용도 |
|------|--------|-----------|------|
| **검토 모드** (기본) | 별도 지정 없음 | 2회 (리서치 후 + 아웃라인 후) | 정확도 중요한 발표, 첫 사용 |
| **자동 모드** | "알아서 만들어줘", "자동으로", "auto" | 없음 — 끝까지 논스톱 | 빠른 초안, 시간 없을 때 |

### Task Pipeline (순차 의존)

**검토 모드:**
```
[mina] T1: Gemini CLI 웹 리서치 (한/영 3~5회)
       T2: NotebookLM 노트북 생성 + 소스 추가 + 합성 질문
       T3: raw-research.md 작성 → Lead에 보고

── Checkpoint 1: 리서치 결과 요약 → 사용자 확인/수정 ──

[seo]  T4: raw-research.md 읽기 + Decision Tree 적용
       T5: structured-outline.md 작성 (슬라이드별 제목/레이아웃/콘텐츠)
       T6: Lead에 아웃라인 보고

── Checkpoint 2: 슬라이드 아웃라인 → 사용자 확인 (기존 청크모드 Phase 0과 동일) ──

[hana] T7: outline + slide-template.html + layouts.md 읽기
       T8: HTML 생성 (기존 Step 2~3 로직)
       T9: ~/Downloads/ 저장 + 브라우저 열기
```

**자동 모드:**
```
[mina] T1~T3: 리서치 → raw-research.md (체크포인트 없이 바로 다음으로)
[seo]  T4~T6: 구조화 → structured-outline.md (체크포인트 없이 바로 다음으로)
[hana] T7~T9: HTML 생성 → ~/Downloads/ 저장 + 브라우저 열기
→ 최종 결과만 사용자에게 보고 (슬라이드 목록 + 파일 경로)
```

---

## SKILL.md 수정 내용

### 1. 레퍼런스 테이블에 추가

```markdown
| `references/research.md` | 리서치 Phase + Agent Team 워크플로우 | **Step 0**: 주제만 제공 시 |
```

### 2. Step 0 섹션 추가 (Step 1 앞)

```markdown
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
- 순차 폴백: 에이전트팀 미지원 시 단일 세션에서 동일 워크플로우 실행
```

---

## references/research.md 구조

```
# Research Phase Workflow

## 개요
## 스테이징 디렉토리 (/tmp/stalab-research/{slug}/)
## Agent Team 구성 (3인 테이블)
## Task Pipeline (T1~T9 + 의존성)
## Gemini CLI 리서치 전략
  - 한국어 1차 쿼리 (주제 직접)
  - 영어 2차 쿼리 (글로벌 관점)
  - 데이터/통계 3차 쿼리
  - 각: gemini -p "..." -o text
## NotebookLM 통합
  - notebooklm create → source add → ask → (optional) generate mind-map
## Agent 프롬프트 템플릿
  - mina: 리서치 전략 + raw-research.md 포맷
  - seo: 구조화 전략 + decision.md 참조 + structured-outline.md 포맷
  - hana: 기존 SKILL.md Step 2~3 수행 지시
## 핸드오프 파일 포맷
  - raw-research.md (YAML frontmatter + 섹션)
  - structured-outline.md (YAML frontmatter + 슬라이드별 명세)
## 실행 모드 (검토 모드 vs 자동 모드)
  - 자동 모드 트리거 키워드: "알아서", "자동으로", "auto", "바로"
  - 검토 모드: 체크포인트 2회 (리서치 후, 아웃라인 후)
  - 자동 모드: 체크포인트 없이 끝까지 → 최종 결과만 보고
## 순차 폴백 모드
## 에러 핸들링 (Gemini 실패, NotebookLM 인증 만료 등)
```

---

## Verification

1. `/stalab-ppt-make AI 반도체 시장 분석` → Step 0으로 라우팅되는지 확인
2. `/stalab-ppt-make` + 불릿 리스트 제공 → Step 0 스킵, 바로 Step 1으로 가는지 확인
3. Agent Team 모드: 3인 팀 생성 → T1~T9 순차 실행 → 체크포인트 2회 → HTML 생성
4. 순차 폴백: 에이전트팀 없이 단일 세션에서 동일 결과 생성
5. 최종 HTML이 기존 제약사항 준수 (단일 파일, CSS-only 차트, 브랜드 색상)
