---
name: "verify"
description: "Run a 6-phase verification loop (build, types, lint, tests, security scan, diff review) before creating a PR or pushing code"
---

# Verification Loop

Run all phases in order. Stop and fix if any phase fails before moving on.

## Do NOT use when

- A quick mid-development check is all that is needed (`/check` — lint/types/tests only)
- The repository has no build or test scripts (config-only, docs-only repos)
- Experimental changes that will not be committed

## Phase 0: Detect Package Manager

Check which package manager the project uses (look for `pnpm-lock.yaml`, `yarn.lock`, `bun.lockb`, or `package-lock.json`). Use the detected package manager for all commands below. Default to `npm` if none found.

## Phase 1: Build

Run the project's build script via the detected package manager. If build fails, STOP. Fix build errors before continuing.

## Phase 2: Type Check

Run `tsc --noEmit` (via `npx` or the project's type-check script). Report and fix all type errors.

## Phase 3: Lint

Run the project's lint script. Auto-fix what can be fixed. Report remaining issues.

## Phase 4: Tests

Run the project's required tests. Collect coverage when supported by the existing runner or
required by project policy; report unavailable metrics as N/A. Enforce the project's configured
thresholds, and report coverage as informational when none are defined. For required test
surfaces, see the applicable `AGENTS.md` (or fallback `CLAUDE.md`) Hard Rules.

## Phase 5: Security Scan

A fast gate over **changed files only** — this is not a full audit:

```bash
# Loop rather than `xargs rg` — an empty file list makes xargs scan the whole tree
for f in $(git diff --name-only); do
  [ -f "$f" ] && rg -n "(api[_-]?key|secret|password|token)\s*[:=]\s*[\"'][^\"']{8,}|console\.log|\$queryRawUnsafe|\$executeRawUnsafe" "$f"
done
```

- Hardcoded secrets (API keys, tokens, passwords)
- `console.log` left in production code
- Raw SQL with string interpolation
- Unvalidated user input on new endpoints

For risk-surface changes, also review the affected security behavior and its tests; see the
applicable `AGENTS.md` (or fallback `CLAUDE.md`) Hard Rules. Use
`~/.agents/skills/security-checklist/SKILL.md` for a full audit when the user or project rules
require one and the project is within that skill's scope.

## Phase 6: Diff Review

```bash
git diff --stat
git diff --name-only
```

Review each changed file for:
- Unintended changes
- Missing error handling
- Potential edge cases
- Files that shouldn't be committed (.env, node_modules, etc.)

**Your own pass over the diff is not the required independent review.** Run a `reviewer`
agent when required by the applicable `AGENTS.md` (or fallback `CLAUDE.md`), handing it the
diff written to a file plus the changed-file list. Report `READY` only after required checks
and reviews pass; report an unavailable required reviewer explicitly.

## Output

```
VERIFICATION REPORT
===================
Build:     [PASS/FAIL]
Types:     [PASS/FAIL] (X errors)
Lint:      [PASS/FAIL] (X warnings)
Tests:     [PASS/FAIL] (X/Y passed, Z% coverage)
Security:  [PASS/FAIL] (X issues)
Diff:      [X files changed]
Review:    [PASS/FAIL/NOT REQUIRED] (reviewer agent — cite the applicable rule)

Overall:   [READY / NOT READY] for PR

Issues to Fix:
1. ...
```

Apply any user-provided invocation text as additional task context.
