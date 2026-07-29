#!/bin/bash
# Format files changed through Codex apply_patch when the project opts in to Prettier.

INPUT=$(cat)
TOOL_NAME=$(printf '%s' "$INPUT" | jq -r '.tool_name // empty')
[ "$TOOL_NAME" = "apply_patch" ] || exit 0

PATCH=$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty')
[ -n "$PATCH" ] || exit 0

printf '%s\n' "$PATCH" |
  sed -n \
    -e 's/^\*\*\* Add File: //p' \
    -e 's/^\*\*\* Update File: //p' \
    -e 's/^\*\*\* Move to: //p' |
  sort -u |
  while IFS= read -r FILE_PATH; do
    [ -f "$FILE_PATH" ] || continue

    case "$FILE_PATH" in
      *.ts | *.tsx | *.js | *.jsx | *.json | *.css | *.scss) ;;
      *) continue ;;
    esac

    FORMAT_PATH="$FILE_PATH"
    case "$FORMAT_PATH" in
      /* | ./*) ;;
      *) FORMAT_PATH="./$FORMAT_PATH" ;;
    esac

    CONFIG=$(npx --no-install prettier --find-config-path "$FORMAT_PATH" 2>/dev/null) || continue
    [ -n "$CONFIG" ] || continue

    npx --no-install prettier --write "$FORMAT_PATH" >/dev/null 2>&1 || true
  done

exit 0
