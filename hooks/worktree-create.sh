#!/usr/bin/env bash
# WorktreeCreate hook — creates worktree from master (latest)
# Input: JSON with "name" field via stdin
# Output: absolute path to created worktree on stdout (MUST be last line)
#
# Project-specific setup:
#   Place .claude/hooks/post-worktree.sh in your project root.
#   It receives two args: $1=WORKTREE_DIR  $2=GIT_ROOT

set -euo pipefail

# Parse input
INPUT=$(cat)
NAME=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('name',''))" 2>/dev/null || echo "")
CWD=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('cwd',''))" 2>/dev/null || echo "$(pwd)")

if [ -z "$NAME" ]; then
  NAME="worktree-$(date +%s)"
fi

# Find git root from cwd
GIT_ROOT=$(git -C "$CWD" rev-parse --show-toplevel 2>/dev/null || echo "$CWD")

# Worktree destination
WORKTREE_DIR="$GIT_ROOT/.claude/worktrees/$NAME"
BRANCH_NAME="worktree-$NAME"

# Ensure .claude/worktrees/ exists
mkdir -p "$(dirname "$WORKTREE_DIR")"

# Create worktree from master (not HEAD)
git -C "$GIT_ROOT" worktree add -b "$BRANCH_NAME" "$WORKTREE_DIR" master 2>/dev/null \
  || git -C "$GIT_ROOT" worktree add -b "$BRANCH_NAME" "$WORKTREE_DIR" main 2>/dev/null \
  || git -C "$GIT_ROOT" worktree add -b "$BRANCH_NAME" "$WORKTREE_DIR" HEAD

# Post-worktree setup: project hook > auto-detect > skip
TEMPLATES_DIR="$HOME/.claude/templates"
POST_HOOK="$GIT_ROOT/.claude/hooks/post-worktree.sh"

if [ -f "$POST_HOOK" ]; then
  # 1) Project-level custom hook (highest priority)
  bash "$POST_HOOK" "$WORKTREE_DIR" "$GIT_ROOT" >&2
elif ls "$WORKTREE_DIR"/next.config.* >/dev/null 2>&1; then
  # 2) Auto-detect: Next.js project → global template
  bash "$TEMPLATES_DIR/post-worktree-nextjs.sh" "$WORKTREE_DIR" "$GIT_ROOT" >&2
fi

# Output the worktree path (required by Claude Code — MUST be last stdout line)
echo "$WORKTREE_DIR"
