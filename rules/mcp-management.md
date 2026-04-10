---
paths:
  - "**/.mcp.json"
  - "**/claude.json"
  - "**/mcp*"
---

# MCP Server Management

## Config File Location (CRITICAL)

Always add/modify MCP servers in **`~/.claude.json` `mcpServers` section**.

| File | Purpose | Add MCP here? |
|------|---------|---------------|
| `~/.claude.json` | User MCPs (actually loaded) | ✅ YES |
| `~/.claude/.mcp.json` | Project-level (conflict risk) | ❌ NO |
| `~/.claude/mcp-servers.json` | Legacy/reference | ❌ NO |

## No Duplicate Names

Same-named MCP servers across config files = **both fail to load**.
Always check existing configs before adding.

## Add Procedure

1. Read `~/.claude.json`
2. Add server to `mcpServers` section (prefer Python json module — Edit tool may fail on frequently-changed files)
3. Instruct session restart
4. Verify with `/mcp`
