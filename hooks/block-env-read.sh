#!/bin/sh
set -eu

# Codex exposes shell and unified-exec calls to hooks as Bash commands.
if ! command -v jq >/dev/null 2>&1; then
  echo 'BLOCKED: The secret-file guard requires jq, but jq is unavailable.' >&2
  exit 2
fi
input="$(cat)"
if ! tool_name="$(printf '%s' "$input" | jq -er '.tool_name | strings' 2>/dev/null)"; then
  echo 'BLOCKED: The secret-file guard received invalid hook input.' >&2
  exit 2
fi
[ "$tool_name" = "Bash" ] || exit 0

if ! command_text="$(printf '%s' "$input" | jq -er '.tool_input.command | strings' 2>/dev/null)"; then
  echo 'BLOCKED: The secret-file guard received a Bash call without a command.' >&2
  exit 2
fi

# Match real .env paths while allowing the three committed template names.
normalized="$(printf '%s' "$command_text" | tr '[:upper:]' '[:lower:]')"
without_templates="$(printf '%s' "$normalized" | sed -E 's/\.env\.(example|sample|template)([^[:alnum:]_.-]|$)/\2/g')"
if printf '%s' "$without_templates" | grep -qE '(^|[^[:alnum:]_.-])\.env([^[:alnum:]_-]|$)'; then
  echo 'BLOCKED: A shell command referenced a secret .env file. Templates (.env.example/.sample/.template) are allowed.' >&2
  exit 2
fi

exit 0
