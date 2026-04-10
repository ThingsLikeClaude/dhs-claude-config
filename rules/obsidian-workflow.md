---
paths:
  - "**/2-notes/**"
  - "**/3-docs/**"
  - "**/*.md"
---

# Obsidian Workflow

## Priority 0: Knowledge Base vs Obsidian Search

SessionStart hook auto-injects `D:\my-vault\knowledge\index.md` (compiled wiki catalog).

| Question type | Tool |
|---|---|
| Past decisions / learnings / concept summaries ("how did I do ordify", "SIFT design principles") | Scan injected index → `Read D:\my-vault\knowledge\concepts\{slug}.md` |
| In-progress docs / original notes / locating specific files | `obsidian search` (rules below) |

Try knowledge base first; fall back to `obsidian search` if insufficient.
`knowledge/` is LLM-owned — never edit directly. Add source material to `D:\my-vault\raw\`.

## Tool Selection by Purpose (CRITICAL)

| Purpose | Tool | Reason |
|---------|------|--------|
| **Search** | Bash → `obsidian search query="..." limit=N` | No tagging rules needed. Token-efficient |
| **Create/edit md** | Skill tool → `obsidian-vault` skill | Tagging rules auto-loaded |
| **Read known-path file** | Read / Glob / Grep | Direct access |
| **Obsidian not running** | Glob/Grep fallback | Notify user |

## Search — Direct Bash CLI

Do NOT load skills for search. Call CLI directly via Bash.

```
1. obsidian version → verify CLI available
2. obsidian search query="..." limit=N → search entire vault
3. If insufficient results, modify query and retry
4. CLI unavailable → Glob/Grep fallback (must notify user)
```

**Banned**: Loading `obsidian-vault` skill just for search (token waste)

## Create/Edit — Skill tool required

When creating or editing md files, MUST use Skill tool to invoke `obsidian-vault` skill.

- Frontmatter tagging rules are defined in the skill
- Project-specific tagging skill takes priority if available
- `date` field required (`YYYY-MM-DD`)

## "Known path" definition (strict)

ALL of the following must be true:
1. User **explicitly mentioned** the path in their message, OR
2. Path was **confirmed by CLI/Glob result** in the current conversation, OR
3. User **opened the file in IDE** and path appears in system message

**Banned**: Using Glob based on assumption ("it should be here based on project structure")

## Availability check

Run `obsidian version` before using CLI.
On failure, fall back to Glob/Grep and notify user:
"Obsidian이 실행 중이 아닙니다. Glob/Grep으로 검색합니다."

## Prerequisites

- Obsidian app must be running for CLI to work
- CLI path: `~/bin/obsidian` (wrapper → `Obsidian.com`)
