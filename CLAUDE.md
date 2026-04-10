# Donghyun's Claude Code Config

## Large File Reading Protocol (MANDATORY)

Before reading any file with the Read tool, run `wc -l <file>` to count lines.
- **≤2000 lines**: Read normally (no special handling)
- **>2000 lines**: NEVER read the entire file at once. Use `offset` and `limit` parameters to read in chunks of ≤2000 lines. Iterate through the file chunk by chunk as needed.
- This applies to ALL file types: logs, JSON, source code, data files.
- Example: 8000-line file → read lines 1-2000, then 2001-4000, etc.

## Golden Rules

- Always respond in Korean
- Conclusion first, reasoning second. Never start with "Because..."
- Surgical changes only. Don't touch adjacent code unless asked
- Date/time: always use `date` or `python3`. Never calculate mentally
- No completion claims without fresh execution evidence. "should work" is banned
- 3+ files changing → `/plan` first. Exception: 1-2 file trivial fixes
- Immutability: no object mutation, use spread for new objects
- File ≤800 lines / Function ≤50 lines / Nesting ≤4 levels
- When uncertain: "Let me verify" + verification method. No guessing
- Analogy first (1-2 sentences) → technical explanation
- Ambiguous requirements → state assumptions, ask for confirmation

## Personal Knowledge Base (`D:\my-vault\knowledge\`)

SessionStart hook auto-injects `knowledge/index.md` catalog at every session start.
For questions about past work/decisions/concepts (e.g., "ordify channel", "SIFT design"):
1. **First**: scan the injected index for relevant `[[concepts/...]]` entries
2. `Read D:\my-vault\knowledge\concepts\{slug}.md` for details
3. Only fall back to `obsidian search` if not found in knowledge base

`knowledge/` is LLM-owned — never edit. Add source material to `D:\my-vault\raw\`.

## Tool Priority (CRITICAL)

| Purpose          | 1st                              | 2nd                 | Banned                   |
| ---------------- | -------------------------------- | ------------------- | ------------------------ |
| Web page reading | `mcp__jina-reader__*`            | `mcp__fetch__fetch` | Built-in WebFetch        |
| Web crawling (full site / JS / bulk) | `mcp__firecrawl-mcp__*` | `mcp__playwright__*` | - |
| Code examples    | `mcp__exa__get_code_context_exa` | context7            | -                        |
| Library docs     | `mcp__context7__*`               | -                   | -                        |
| UI verification  | `mcp__playwright__*`             | -                   | -                        |
| Build check      | `tsc --noEmit`                   | -                   | `pnpm build`             |
| Obsidian search  | Bash → `obsidian search`         | Glob/Grep fallback  | Loading skill for search |

## MCP Server Management

- Add/modify servers only in `~/.claude.json` `mcpServers` section
- Duplicate names = both fail to load. Check existing configs before adding
- Never add to `~/.claude/.mcp.json` or `mcp-servers.json`

## Agent Usage

- Complex features → planner agent
- After writing code → code-reviewer agent
- Bug fix / new feature → tdd-guide agent
- Independent tasks → parallel execution (never sequential)
- Details: `~/.claude/rules/agents-v2.md`

## Git

- Commits: `<type>: <description>` (feat, fix, refactor, docs, test, chore)
- Never amend/rebase pushed commits
- Never commit secrets or API keys

## Google Workspace

- Email triage request → read+archive immediately without asking
- Email: use gws-gmail-\* skills
- Tasks: only register 5+ steps & 30+ min work to Google Tasks
- Details: `~/.claude/rules/email-workflow.md`, `google-tasks-workflow.md`

## Obsidian

- Search: Bash → `obsidian search` (direct CLI, no skill loading)
- Create/edit md: Skill tool → `obsidian-vault` skill (tagging rules needed)
- "Known path" = user explicitly stated OR confirmed by previous search result
- Details: `~/.claude/rules/obsidian-workflow.md`

## Security

- Before commit: check hardcoded secrets, SQL injection, XSS
- Secrets via `process.env` only. Throw immediately if unset
- Security issue found → deploy security-reviewer agent

## Rules Index (Conversation Keyword → Read rule file)

When conversation matches keywords below, Read the rule file and follow it.

| Keywords                                        | Rule File                                  |
| ----------------------------------------------- | ------------------------------------------ |
| 날짜, 요일, D-day, 며칠, 언제, date, calendar, schedule | `~/.claude/rules/date-calculation.md`      |
| 메일, 이메일, 메일 정리, 메일 확인, gmail, triage            | `~/.claude/rules/email-workflow.md`        |
| 태스크, 할일, 작업 등록, tasks, todo                     | `~/.claude/rules/google-tasks-workflow.md` |
| 옵시디언, 노트, 볼트, obsidian, vault, note             | `~/.claude/rules/obsidian-workflow.md`     |
| MCP, mcp 서버, mcp 추가, mcp server                 | `~/.claude/rules/mcp-management.md`        |
| 에이전트, 서브에이전트, 병렬 실행, agent, subagent, parallel  | `~/.claude/rules/agents-v2.md`             |
| 텔레그램, telegram, 채팅, channel                       | `~/.claude/rules/telegram-response.md`     |
| 불변, immutable, mutation, spread, 코딩스타일, coding style | `~/.claude/rules/coding-style.md`          |
| 보안, injection, XSS, CSRF, secrets, 시크릿, 취약점       | `~/.claude/rules/security.md`              |
