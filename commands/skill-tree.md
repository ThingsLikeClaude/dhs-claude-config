# /skill-tree — Skill Tree Manager

Manage skills across global registry and project-level installation.
Skills are organized in a tree structure (`~/.claude/skill-registry/skill-tree.yaml`)
and bundled into packs (`~/.claude/skill-registry/packs.yaml`).

## Usage

```
/skill-tree install <pack|skill>    Install to project .claude/skills/
/skill-tree uninstall <pack|skill>  Remove from project
/skill-tree list                     Show available packs and skills
/skill-tree search <keyword>        Search skill tree by keyword
/skill-tree status                   Show project installation status
/skill-tree upgrade [skill]          Update installed skills from pool
/skill-tree rollback                 Restore from last backup
```

## Architecture

```
~/.claude/skill-registry/
├── skill-tree.yaml     ← Tree index (all skills mapped)
├── packs.yaml          ← Skill pack definitions
├── .last-backup-path   ← Migration rollback path
└── pool/               ← 69 uninstalled skills stored here

~/.claude/skills/       ← 4 global high-frequency skills (CC native)
project/.claude/skills/ ← Installed per-project (CC native)
```

## Subcommand Details

### install <pack|skill>

1. Read `~/.claude/skill-registry/packs.yaml` (if pack name) or locate skill in `pool/`
2. Check project `.claude/skills/` current count
   - **HARD LIMIT: 25 skills per project** (CTO review: ~500 tokens/skill × 25 = ~12,500 tokens, ~6% of CC context)
   - If installing would exceed 25: STOP and show error with current count
3. For each skill in pack (or single skill):
   a. Check if already exists in project `.claude/skills/` → skip if yes
   b. Check if exists in `~/.claude/skill-registry/pool/` → error if not found
   c. Create project `.claude/skills/` directory if needed: `mkdir -p .claude/skills/`
   d. Copy: `cp -r ~/.claude/skill-registry/pool/<skill>/ .claude/skills/<skill>/`
4. Output installed skill list
5. Note: "CC recognizes installed skills from the next turn. To use immediately in this turn, call `Skill('<skill-name>')`."

### uninstall <pack|skill>

1. Validate path safety: target MUST be under `.claude/skills/` (CTO review: whitelist check)
2. Verify skill exists in project `.claude/skills/`
3. Remove: `rm -rf .claude/skills/<skill>/`
   - ONLY if path matches pattern: `.claude/skills/<alphanumeric-and-hyphens>/`
4. Output confirmation

### list

1. Read `packs.yaml` and show all packs with description and skill count
2. Read `skill-tree.yaml` top-level domains
3. For each pack, indicate if any skills are already installed in current project
4. Show: pack name, description, skill count, [installed] status

### search <keyword>

1. Read `skill-tree.yaml` via `cat ~/.claude/skill-registry/skill-tree.yaml`
2. Find nodes matching keyword in `_keywords` arrays
3. Display matching subtree with:
   - Skill names
   - Location: [global], [pool], [installed] (check project .claude/skills/)
   - Which pack(s) contain each skill
4. Suggest install command

### status

1. Count global skills: `ls ~/.claude/skills/`
2. Count project skills: `ls .claude/skills/` (if exists)
3. Count pool skills: `ls ~/.claude/skill-registry/pool/`
4. Show hard limit usage: `N/25`
5. List installed project skills with names
6. Note: plugin skills (bkit:*, obsidian:*, codex:*) are separate and not counted

### upgrade [skill]

1. If skill specified: upgrade that one skill
2. If no argument: check all installed project skills
3. For each skill:
   a. Compare pool version vs installed version using file modification time
      - Use: `date -r ~/.claude/skill-registry/pool/<skill>/SKILL.md +%s` vs `date -r .claude/skills/<skill>/SKILL.md +%s`
   b. If pool is newer:
      - Copy to temp: `cp -r pool/<skill>/ .claude/skills/<skill>.tmp/` (CTO review: atomic via tmp+mv)
      - Swap: `rm -rf .claude/skills/<skill>/ && mv .claude/skills/<skill>.tmp/ .claude/skills/<skill>/`
   c. If same: skip
4. Report updated skills

### rollback

1. Read backup path from `~/.claude/skill-registry/.last-backup-path`
2. Confirm with user before proceeding
3. Restore: copy all skills from backup back to `~/.claude/skills/`
4. Move pool/ skills back if needed

## Safety Rules

- **Path whitelist**: All rm -rf operations MUST verify path contains `.claude/skills/` and skill name matches `^[a-zA-Z0-9_-]+$`
- **Hard limit**: 25 skills per project, enforced on install
- **Backup**: Migration backup path stored in `.last-backup-path`
- **Atomic upgrade**: Always use tmp+mv pattern, never in-place overwrite
- **No global mutation**: install/uninstall only affect project `.claude/skills/`, never `~/.claude/skills/`
