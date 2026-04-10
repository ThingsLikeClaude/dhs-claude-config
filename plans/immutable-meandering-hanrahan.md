# GitHub 레포 정리: claude-forge 스타일

## Context

oh-my-stalab Harness + oh-my-stalab-pro-max를 각각 독립 GitHub 레포로 정리.
claude-forge 스타일 적용: .claude-plugin/ manifest, 심링크 기반 install.sh, 구조화된 README.

## 잔여 작업: 에이전트 파일 리네임
- pm-agent.md, test-designer.md, verification-orchestrator.md에서 `mega-dev-cycle` → `oms-pro-max` 변경 필요
- response-language.md에서 `noyeah-harness` → `oh-my-stalab-pro-max` 변경

## Repo 1: oh-my-stalab-harness

### 현재 위치
`D:/Obsidian/MD_MY_VAULT/1-projects/claude-utils/oh-my-stalab/Harness/`

### 목표 구조 (claude-forge 스타일)
```
oh-my-stalab-harness/
├── .claude-plugin/
│   ├── plugin.json              ★ 신규
│   └── marketplace.json         ★ 신규
├── agents/                      ← .claude/agents/ → agents/ (한 레벨 위로)
│   └── (10개 .md)
├── commands/                    ← .claude/commands/
│   └── (14개 .md)
├── hooks/                       ← .claude/hooks/
│   ├── hooks.json
│   └── (12개 .sh)
├── skills/                      ← .claude/skills/
│   └── (13개 스킬 디렉토리)
├── rules/                       ← .claude/rules/
│   └── (6개 .md)
├── cc-chips-custom/             ← .claude/cc-chips-custom/
├── knowledge/                   ← knowledge/ (그대로)
├── fonts/                       ← fonts/ (그대로)
├── install.sh                   ★ 신규 (심링크 기반)
├── install.ps1                  ★ 신규 (Windows용)
├── settings.json                ← .claude/settings.json
├── .mcp.json                    ← .mcp.json
├── CLAUDE.md                    ← CLAUDE.md
├── README.md                    ★ 재작성 (claude-forge 스타일)
├── README.ko.md                 ★ 신규 (한국어)
└── LICENSE                      ★ 신규
```

### 변경 요약
- `.claude/` 하위 → 최상위로 이동 (agents/, commands/ 등)
- `.claude-plugin/` manifest 추가
- install.sh 새로 작성 (심링크 방식, ~/.claude/에 설치)
- README 재작성

## Repo 2: oh-my-stalab-pro-max

### 현재 위치
`D:/Obsidian/MD_MY_VAULT/1-projects/claude-utils/oh-my-stalab-pro-max/`

### 목표 구조
```
oh-my-stalab-pro-max/
├── .claude-plugin/
│   ├── plugin.json              ★ 신규
│   └── marketplace.json         ★ 신규
├── agents/                      ← .claude/agents/
│   ├── pm-agent.md
│   ├── test-designer.md
│   └── verification-orchestrator.md
├── commands/                    ← .claude/commands/
│   └── oms-pro-max.md
├── rules/                       ← .claude/rules/
│   └── response-language.md
├── install.sh                   ★ 재작성 (심링크 + harness 의존 체크)
├── CLAUDE.md                    ← (그대로)
├── README.md                    ★ 재작성
├── README.ko.md                 ★ 신규
└── LICENSE                      ★ 신규
```

## 구현 순서

### Step 1: 잔여 리네임 완료
- pm-agent.md, test-designer.md, verification-orchestrator.md: `mega-dev-cycle` → `oms-pro-max`
- response-language.md: `noyeah-harness` → `oh-my-stalab-pro-max`

### Step 2: oh-my-stalab-harness 재구조화
1. 새 폴더 생성: `oh-my-stalab-harness/`
2. `.claude/agents/` → `agents/`로 이동 (최상위)
3. `.claude/commands/` → `commands/`
4. `.claude/hooks/` → `hooks/`
5. `.claude/skills/` → `skills/`
6. `.claude/rules/` → `rules/`
7. `.claude/cc-chips-custom/` → `cc-chips-custom/`
8. `.claude-plugin/` 생성 + plugin.json, marketplace.json
9. install.sh 작성 (심링크 기반)
10. install.ps1 작성 (Windows)
11. README.md 재작성
12. LICENSE 추가

### Step 3: oh-my-stalab-pro-max 재구조화
1. `.claude/agents/` → `agents/`
2. `.claude/commands/` → `commands/`
3. `.claude/rules/` → `rules/`
4. `.claude-plugin/` 생성
5. install.sh 재작성 (harness 의존 체크 + 심링크)
6. README.md 재작성
7. LICENSE 추가

### Step 4: 검증
- 두 레포 구조 확인
- install.sh 구문 검증 (bash -n)
- plugin.json 유효성

## 핵심 파일: plugin.json

### oh-my-stalab-harness
```json
{
  "name": "oh-my-stalab-harness",
  "version": "1.0.0",
  "description": "Claude Code development harness with agents, commands, hooks, skills, and rules",
  "repository": "https://github.com/{owner}/oh-my-stalab-harness",
  "agents": "agents/",
  "commands": "commands/",
  "hooks": "hooks/",
  "skills": "skills/",
  "rules": "rules/",
  "scripts": "scripts/",
  "mcpServers": "./.mcp.json"
}
```

### oh-my-stalab-pro-max
```json
{
  "name": "oh-my-stalab-pro-max",
  "version": "1.0.0",
  "description": "Autonomous full-cycle development pipeline (requires oh-my-stalab-harness + bkit)",
  "repository": "https://github.com/{owner}/oh-my-stalab-pro-max",
  "dependencies": ["oh-my-stalab-harness", "bkit"],
  "agents": "agents/",
  "commands": "commands/",
  "rules": "rules/"
}
```

## install.sh 핵심 로직

### oh-my-stalab-harness/install.sh
```bash
# 1. 의존성 체크 (node, git)
# 2. 기존 ~/.claude/ 백업 (사용자 확인)
# 3. 심링크 생성:
#    ln -sf $REPO/agents ~/.claude/agents
#    ln -sf $REPO/commands ~/.claude/commands
#    ln -sf $REPO/hooks ~/.claude/hooks
#    ln -sf $REPO/skills ~/.claude/skills
#    ln -sf $REPO/rules ~/.claude/rules
#    ln -sf $REPO/cc-chips-custom ~/.claude/cc-chips-custom
# 4. settings.json, .mcp.json 병합
# 5. CLAUDE.md 병합
# 6. Windows/WSL: 심링크 대신 복사
```

### oh-my-stalab-pro-max/install.sh
```bash
# 1. oh-my-stalab-harness 설치 확인 (~/.claude/agents/code-architect.md)
# 2. bkit 설치 확인
# 3. 프로젝트 .claude/에 심링크:
#    ln -sf $REPO/agents/* project/.claude/agents/
#    ln -sf $REPO/commands/* project/.claude/commands/
#    ln -sf $REPO/rules/* project/.claude/rules/
# 4. CLAUDE.md 병합
```

## 검증
1. `tree oh-my-stalab-harness/` 구조 확인
2. `tree oh-my-stalab-pro-max/` 구조 확인
3. `bash -n install.sh` 구문 검증
4. `jq . .claude-plugin/plugin.json` JSON 유효성
