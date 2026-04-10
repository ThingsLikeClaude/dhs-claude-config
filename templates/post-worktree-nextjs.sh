#!/usr/bin/env bash
# post-worktree.sh — Next.js project worktree setup
# Copy this file to: <project-root>/.claude/hooks/post-worktree.sh
#
# Called by global worktree-create.sh after worktree is created.
# Args: $1=WORKTREE_DIR  $2=GIT_ROOT
# stdout is suppressed (>&2 redirect in caller), so use stderr for logs.

set -euo pipefail

WORKTREE_DIR="$1"
GIT_ROOT="$2"

echo "[post-worktree] Next.js setup starting..." >&2

# ── 1. Copy .env files ──
ENV_FILES=(
  ".env"
  ".env.local"
  ".env.development.local"
  "frontend/.env.local"
)

for env_file in "${ENV_FILES[@]}"; do
  SRC="$GIT_ROOT/$env_file"
  DST="$WORKTREE_DIR/$env_file"
  if [ -f "$SRC" ] && [ ! -f "$DST" ]; then
    mkdir -p "$(dirname "$DST")"
    cp "$SRC" "$DST"
    echo "[post-worktree] Copied $env_file" >&2
  fi
done

# ── 2. Install dependencies ──
if [ -f "$WORKTREE_DIR/pnpm-lock.yaml" ]; then
  echo "[post-worktree] Running pnpm install..." >&2
  cd "$WORKTREE_DIR" && pnpm install --frozen-lockfile >&2 2>&1
elif [ -f "$WORKTREE_DIR/package-lock.json" ]; then
  echo "[post-worktree] Running npm ci..." >&2
  cd "$WORKTREE_DIR" && npm ci >&2 2>&1
elif [ -f "$WORKTREE_DIR/yarn.lock" ]; then
  echo "[post-worktree] Running yarn install..." >&2
  cd "$WORKTREE_DIR" && yarn install --frozen-lockfile >&2 2>&1
fi

echo "[post-worktree] Done." >&2
