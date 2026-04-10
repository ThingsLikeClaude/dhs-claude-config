# 글로벌 CLAUDE.md + rules/ 최적화 플랜

## Context

현재 매 세션마다 **CLAUDE.md 16줄 + rules/ 852줄 = ~868줄**이 무조건 로드됨.
리서치 권장치(150-200줄)의 4배 이상. 규칙이 너무 많으면 모든 규칙의 준수율이 균일하게 떨어짐.
특히 jina 우선 사용 같은 규칙이 무시되는 근본 원인.

## 현재 rules/ 분석 (총 13개 파일, 891줄)

### 항상 로드 (paths: 없음) — 12개, 852줄
| 파일 | 줄수 | 분류 |
|------|------|------|
| interaction.md | 129 | 🔴 비대 — MCP 사용법+대화스타일 혼재 |
| verification.md | 116 | 🟡 golden-principles #10과 중복 많음 |
| agents-v2.md | 94 | 🟡 에이전트 목록은 매 세션 불필요 |
| golden-principles.md | 93 | 🟢 핵심 — 하지만 anti-rationalization 테이블이 길다 |
| coding-style.md | 70 | 🟡 golden-principles와 중복 (immutability, file size) |
| google-tasks-workflow.md | 66 | 🔴 gws tasks 안 쓰는 세션이 대부분 |
| git-workflow-v2.md | 63 | 🟡 agents 부분은 agents-v2와 중복 |
| date-calculation.md | 57 | 🟢 짧고 구체적 — 유지 |
| obsidian-workflow.md | 51 | 🟡 Obsidian 안 쓰는 세션도 많음 |
| security.md | 46 | 🟡 커밋 전 체크리스트 → 조건부 로드 가능 |
| email-workflow.md | 44 | 🔴 메일 작업 시에만 필요 |
| mcp-management.md | 23 | 🟢 짧고 중요 — 유지 |

### 조건부 로드 (paths: 있음) — 1개, 39줄
| 파일 | 줄수 |
|------|------|
| testing.md | 39 | ✅ 이미 최적화됨 |

## 개선 방향

### Step 1: CLAUDE.md를 ~100줄 핵심 규칙으로 재작성

현재 16줄(스킬 포인터만)을 **핵심 원칙 + 도구 우선순위 + 금지사항** 중심으로 재작성.
이게 매 세션 가장 먼저, 가장 강하게 로드되는 곳이므로 "절대 지켜야 할 것"을 여기에.

```markdown
# 동현의 Claude Code 설정

## 핵심 원칙 (Golden Rules)
- 결론 먼저, 이유는 뒤에
- 요청한 것만 변경 (surgical changes)
- 날짜/시간은 반드시 시스템 명령으로 계산
- 완료 주장 전 실행 증거 필수 (speculative completion 금지)
- 3개 이상 파일 변경 시 /plan 먼저
- 불변성: 객체 mutation 금지, spread로 새 객체 생성
- 파일 800줄, 함수 50줄, 중첩 4단계 이하

## 도구 우선순위 (CRITICAL)
- 웹 읽기: jina-reader → fetch MCP (내장 WebFetch 절대 금지)
- 코드 예제: exa → context7
- 라이브러리 문서: context7
- UI 확인: agent-browser --auto-connect (새 창 열지 않음)
- 빌드 검증: tsc --noEmit (pnpm build 금지)

## MCP 서버 관리
- 추가/수정은 반드시 ~/.claude.json의 mcpServers에
- 중복 이름 = 둘 다 로드 실패

## 커뮤니케이션
- 한국어 응답 기본
- 불확실하면 추측 대신 "확인해보겠습니다"
- 비유 먼저 → 기술 설명
- 모호한 요구사항 → 가정 명시 후 확인

## 스킬 참조
- PDF: ~/.claude/skills/pdf/SKILL.md
- NotebookLM: ~/.claude/skills/notebooklm/SKILL.md
- YouTube Playlist Notes: ~/.claude/skills/youtube-playlist-notes/SKILL.md
```

### Step 2: rules/ 파일을 조건부 로드로 전환

**항상 로드 유지 (핵심, ~100줄 이하):**
- `date-calculation.md` (57줄) — 짧고 보편적
- `mcp-management.md` (23줄) — 짧고 중요

**paths: 추가하여 조건부 로드로 전환:**
| 파일 | paths: 트리거 |
|------|-------------|
| coding-style.md | `**/*.ts`, `**/*.tsx`, `**/*.js` |
| security.md | `**/*.ts`, `**/*.tsx`, `.env*` |
| git-workflow-v2.md | `.git/**`, `**/.gitignore` |
| obsidian-workflow.md | `**/*.md` (2-notes/, 3-docs/ 내) |
| email-workflow.md | `**/gmail*`, `**/email*` |
| google-tasks-workflow.md | `**/tasks*`, `**/gws*` |
| agents-v2.md | `**/.claude/agents/**` |
| testing.md | 이미 조건부 ✅ |

**golden-principles.md + verification.md + interaction.md → 삭제 후 CLAUDE.md로 흡수:**
이 3개 파일의 핵심 내용은 위 CLAUDE.md 100줄에 이미 압축됨.
중복되는 상세 설명과 예시 코드블록은 제거.

### Step 3: 잘 안 지켜지는 규칙 → hooks/deny로 강제

| 규칙 | 현재 | 개선 |
|------|------|------|
| WebFetch 사용 금지 | interaction.md에 텍스트 | `settings.json` deny: `"WebFetch(*)"` |
| pnpm build 금지 | CLAUDE.md에 텍스트 | `settings.json` deny: `"Bash(pnpm build*)"` |
| jina 우선 사용 | interaction.md에 텍스트 | CLAUDE.md 도구 우선순위 (가장 눈에 띄는 위치) |

### 예상 결과

| | Before | After |
|---|---|---|
| 매 세션 로드 | ~868줄 | ~180줄 (CLAUDE.md 100 + date 57 + mcp 23) |
| 조건부 로드 | 39줄 | ~560줄 (필요 시에만) |
| 삭제 | 0줄 | ~200줄 (중복/장황한 설명) |
| 규칙 준수율 | 규칙 과다로 낮음 | 핵심 집중으로 향상 |

## 검증 방법

1. 새 세션 시작 후 `jina-reader` 우선 사용되는지 확인
2. `pnpm build` 시도 시 deny로 차단되는지 확인
3. 코드 작업 시 `coding-style.md`가 조건부 로드되는지 확인
4. 세션 초기 로드 시간/토큰 체감 비교
