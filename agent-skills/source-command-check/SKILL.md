---
name: "source-command-check"
description: "Quick check \u2014 run lint, type check, and tests during development (use /verify for full pre-push validation)"
---

# source-command-check

Use this skill when the user asks to run the migrated source command `check`.

## Command Template

Check the project's package.json to identify available scripts, then run the following in order:

1. Lint — auto-fix what can be fixed
2. Type check (if TypeScript project) — fix any errors
3. Tests — fix failures
4. If all pass, provide a one-line summary of changes

If a step has issues, fix them before moving to the next.
Only report problems that cannot be auto-fixed.

Apply any user-provided invocation text as additional task context.

