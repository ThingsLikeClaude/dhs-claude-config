# chargen 구현 플랜

## Context
Claude Code 프로젝트 초기화를 RPG 캐릭터 빌더로 만드는 플러그인. 인터뷰(26문항) 완료, 기술 결정 확정.

## Phase 0: 프로젝트 초기화
- GitHub public repo 생성 (`chargen`, MIT)
- git init + 초기 커밋 + push
- `.claude-plugin/plugin.json` — 플러그인 매니페스트
- `package.json` — 런타임 의존성 없음
- `CLAUDE.md` — 플러그인 문서
- `.gitignore`

## Phase 1: 슬래시 명령어
- `commands/chargen.md` — `/chargen` 명령어 (5단계 워크플로우 전체 정의)
  1. 프로젝트 스캔 → 2. recommended-build.json 생성 → 3. 서버 시작+브라우저 열기
  4. Long-poll 대기 → 5. 결과 적용 (백업→스킬→에이전트→CLAUDE.md→git commit)

## Phase 2: server.js
- `scripts/server.js` — Node.js 내장 http, ~100줄, 의존성 제로
- API 7개: `GET /`, `/api/build`, `/api/skills`, `/api/agent-presets`, `/api/scan`, `/api/wait`, `POST /api/confirm`
- 포트 0 (랜덤) → stdout JSON으로 포트 출력
- Long-poll 10분 타임아웃, CORS 허용

## Phase 3: React + Vite 스캐폴드
- `ui/` 디렉토리: package.json, vite.config.ts, tsconfig.json, tailwind.config.ts
- `ui/src/main.tsx`, `App.tsx` — 3탭 레이아웃 (스킬트리 | 에이전트 | CLAUDE.md)
- `ui/src/api/client.ts` — fetch wrapper
- `ui/src/types/index.ts` — 전체 타입 정의
- `ui/src/context/ChargenContext.tsx` — useReducer 상태관리
- 다크 RPG 테마 (딥퍼플/블루 배경, 골드 추천, 그린 설치됨)

## Phase 4: 스킬트리 UI (핵심)
- `SkillTree/SkillTreeView.tsx` — 메인 컨테이너
- `SkillTree/DomainSelector.tsx` — 도메인 탭 (UI, Review, Verify, Security...)
- `SkillTree/PackBanner.tsx` — 팩 일괄 설치 배너
- `SkillTree/SkillTreeCanvas.tsx` — Tier 1→2→3 노드 그리드
- `SkillTree/SkillNode.tsx` — 개별 노드 (헥사곤, 상태별 색상/글로우)
- `SkillTree/ConnectionLines.tsx` — SVG 의존성 라인
- `SkillTree/SkillDetail.tsx` — 사이드 패널 상세 정보
- 제한: 5-7개 노드/화면, 25개 하드리밋

## Phase 5: 에이전트 빌더 UI
- `AgentBuilder/AgentPresetGrid.tsx` — 프리셋 카드 그리드
- `AgentBuilder/AgentCard.tsx` — 카드 (이름, 설명, 모델 배지)
- `AgentBuilder/InstalledAgentList.tsx` — 기존 에이전트 keep/remove
- `AgentBuilder/CustomAgentForm.tsx` — 커스텀 에이전트 생성 폼

## Phase 6: CLAUDE.md 에디터 UI
- `ClaudeMdEditor/TemplateSelector.tsx` — 프리셋 드롭다운
- `ClaudeMdEditor/SectionEditor.tsx` — 섹션별 텍스트에어리어
- `ClaudeMdEditor/ClaudeMdPreview.tsx` — 마크다운 미리보기
- Merge vs Replace 토글

## Phase 7: 확인 플로우 연결
- `ConfirmButton.tsx` — "Apply Build" 버튼
- `ConfirmDialog.tsx` — 변경사항 요약 모달 (+3 skills, -1 skill, +2 agents...)
- `StatusBar.tsx` — 하단 상태바 (스킬 N/25, 에이전트 N)
- POST /api/confirm → result.json → Claude가 읽고 적용

## Phase 8: 정적 데이터 파일
- `ui/src/data/skill-tree.json` — 스킬 노드/연결 정의 (Tier 구조)
- `ui/src/data/agent-presets.json` — 에이전트 프리셋 (개발/테스트/문서/보안/워크플로우)
- `ui/src/data/claudemd-templates.json` — CLAUDE.md 템플릿 (Next.js, Python, Blank 등)

## Phase 9: 빌드 + 폴리시
- `cd ui && npm run build` → dist/ 생성 (커밋 포함)
- 크로스플랫폼 테스트 (Windows 우선)
- README.md 작성

## 핵심 데이터 구조

### recommended-build.json (Claude 생성)
```json
{
  "projectType": "nextjs-fullstack",
  "detectedStack": ["next", "react", "tailwind"],
  "recommendedSkills": [{ "id": "...", "reason": "..." }],
  "recommendedAgents": ["code-architect"],
  "existingScan": { "installedSkills": [], "skillCount": 0, "skillLimit": 25 }
}
```

### result.json (UI → Claude)
```json
{
  "skills": { "install": [], "uninstall": [], "keep": [] },
  "agents": { "install": [{ "id": "...", "source": "preset|custom" }], "keep": [] },
  "claudeMd": { "mode": "merge|replace", "sections": { ... } }
}
```

## 검증 방법
- Phase별 통과 기준 명시 (서버 curl 테스트, UI 빌드, E2E 플로우)
- `node scripts/server.js` → 7개 엔드포인트 응답 확인
- `/chargen` 실행 → 브라우저 열림 → 커스터마이징 → 확인 → .claude/ 생성 확인

## 안전장치
- 적용 전 `.claude/.chargen-backup/{timestamp}/` 전체 스냅샷
- 기존 설정 보존 + 추가 (리셋 아님)
- 25개 스킬 하드리밋 UI에서 강제
