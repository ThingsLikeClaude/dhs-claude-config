#!/bin/bash
# vault-sync.sh - PostToolUse Hook (Edit|Write)
# D:\vault 안의 .md 파일이 생성/수정되면 D:\Obsidian\MD_MY_VAULT로 자동 복사
# exit 0 필수 (세션 방해 금지)

INPUT=$(cat)

# Extract file path from tool input
FILE_PATH=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    inp = d.get('tool_input', {})
    print(inp.get('file_path', ''))
except:
    pass
" 2>/dev/null)

# No file path = not relevant
if [[ -z "$FILE_PATH" ]]; then
    exit 0
fi

# Normalize path: convert backslashes, resolve /d/ or D:/ prefix
NORM_PATH=$(echo "$FILE_PATH" | sed 's|\\|/|g' | sed 's|^D:/|/d/|i')

# Only process .md files
if [[ "$NORM_PATH" != *.md ]]; then
    exit 0
fi

# Only process files under D:\vault (= /d/vault/)
SRC_ROOT="/d/vault"
if [[ "$NORM_PATH" != "$SRC_ROOT/"* ]]; then
    exit 0
fi

# Exclude patterns
BASENAME=$(basename "$NORM_PATH")
case "$NORM_PATH" in
    */node_modules/*|*/.obsidian/*|*/.git/*|*/.bkit/*|*/.claude/*|*/.next/*|*/.makemd/*|*/.space/*)
        exit 0 ;;
esac
case "$BASENAME" in
    CLAUDE.md|*snapshot*.md|snap*.md)
        exit 0 ;;
esac

# Calculate relative path from vault root
REL_PATH="${NORM_PATH#$SRC_ROOT/}"

# Destination
DST_ROOT="/d/Obsidian/MD_MY_VAULT"
DST_PATH="$DST_ROOT/$REL_PATH"

# Create destination directory if needed
DST_DIR=$(dirname "$DST_PATH")
mkdir -p "$DST_DIR" 2>/dev/null

# Copy file
if [[ -f "$NORM_PATH" ]]; then
    cp "$NORM_PATH" "$DST_PATH" 2>/dev/null

    # Log
    LOG_DIR="$HOME/.claude/logs"
    mkdir -p "$LOG_DIR" 2>/dev/null
    echo "$(date '+%Y-%m-%d %H:%M:%S') SYNC $REL_PATH" >> "$LOG_DIR/vault-sync.log"
fi

exit 0
