#!/usr/bin/env bash
# PostToolUse hook (spec 003 R6): after an edit to a .c or .h file, run `make warn`.
# Silent on success. When the build fails or prints a warning, it writes the
# compiler output to stderr and exits 2, which Claude Code feeds back to the agent.
# The baseline compiles with zero warnings, so any warning is new.
set -u
input=$(cat)
file=$(printf '%s' "$input" | python3 -c '
import json, sys
try:
    print(json.load(sys.stdin).get("tool_input", {}).get("file_path", ""))
except Exception:
    print("")
')
case "$file" in
  *.c|*.h) ;;
  *) exit 0 ;;
esac
cd "${CLAUDE_PROJECT_DIR:-$PWD}" || exit 0
out=$(make warn 2>&1)
rc=$?
if [ "$rc" -ne 0 ] || printf '%s' "$out" | grep -qE 'warning:|error:'; then
  {
    echo "make warn reported problems after editing $file (the baseline has zero warnings):"
    echo "$out"
  } >&2
  exit 2
fi
exit 0
