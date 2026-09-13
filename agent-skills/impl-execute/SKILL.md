---
name: "impl-execute"
description: "Implement an approved plan in docs/impl-spec/, verify it, and complete its review and lifecycle steps."
---

# Implementation Execution with Code-Verified Review Loop

Implement a spec from `docs/impl-spec/`, then have a fresh-context `reviewer` verify the code
against the spec. The implementer never reviews its own work — whoever wrote the code (you or
Codex) carries the blind spot this loop exists to defeat.

## Do NOT use when

- No spec exists — write one with `impl-plan` first
- One-line fixes or typos — the review loop costs more than the change
- The spec is in `archive/` or has `status: done` / `superseded-by` — frozen history

## Inputs

- Spec path (`docs/impl-spec/<NNN>-*.md`). Reuse the plan already selected in the
  conversation. Otherwise inspect active top-level specs and use the unique relevant plan;
  ask only when multiple plausible plans remain. Selection does not itself grant approval.
- If `## Review Notes` has `UNRESOLVED` rows, stop: the plan review never came back clean.
  Clear them first (re-run `/impl-plan`, or dispose them by hand with evidence).
- Record the base branch as `<base>` (`git rev-parse --abbrev-ref HEAD`).

**Who implements**: follow AGENTS.md's Astra routing policy. For automatic model-based
delegation, use [codex-delegation](../codex-delegation/SKILL.md); the Astra supervisor retains
the phases and spec lifecycle below. An explicit `codex-worker` courier request uses
[delegated execution](references/delegated-execution.md) instead of Phase 1.

**Delegated worker**: if a parent assigned you bounded implementation steps, implement only
those steps, leave the spec to the parent, and return facts; the parent owns markers, review,
and closing. Determine this role from the dispatch, not the model name. A top-level Codex
session owns all phases below, including review and closing.

## Phase 1: Implementation

1. **Resume point** — `grep -n '^### \[ \]' <spec>` gives the first unimplemented step.
   - Some steps already `[x]` → verify the marked work against the code and relevant checks,
     report the resume point, and continue within the approved scope. Ask only if a discrepancy
     requires a material scope/design decision or crosses an explicit approval boundary.
   - All `[x]` but `status: active` → implement nothing; run Phase 2 on the committed work
     (build the change inventory from the spec's `## Affected Files` and the commits since its
     `date`), then close via Phase 3.
   - A step marked `> BLOCKED: <reason>` needs the blocker resolved or the user's call.
2. **Implement step by step.** After each step: run checks relevant to that change, then flip
   its marker to `[x]` in the spec immediately — this write is what survives an interrupted
   session. Complete the full required checks in Verify below. Implement each `## Tests` entry alongside the step it pins; they carry no marker, so
   nothing else will catch a skipped one. A step you cannot complete stays `[ ]` with a
   `> BLOCKED: <reason>` line under its heading.
3. **Verify** — run the spec's `## Verification` commands and applicable required checks.
   Reuse passing results only while the code and inputs they cover remain unchanged; repeat
   checks when later changes, failures, or unresolved concerns invalidate those results.
4. **Change summary** — steps completed, files changed with one line each, deviations from the
   plan and why, and a **dependency map** for changed interfaces or structure: affected callers and importers. On a
   resumed run cover every step in the spec, not only this session's.

## Phase 2: Review Loop

1. Write the change as a patch: `git add -A -N && git diff > <scratch>/review-N.diff` (from
   `<base>` if the work was committed as it went). The patch gives the reviewer
   the exact additions and deletions alongside current file contents.
2. Reuse valid independent review evidence under AGENTS.md's review-reuse rule. When new
   review is needed, spawn a **new** `reviewer` for that round with: the spec path, the change summary and
   dependency map, the patch path, the absolute checkout path, and (round 2+) the previous
   disposition table. It runs in Implementation verification mode (`~/.codex/agents/reviewer.toml`).
3. **Disposition** — `ACCEPTED` (fix the code) or `REJECTED` with concrete evidence:

   | Finding | Severity | Disposition | Rationale |
   |---------|----------|-------------|-----------|

4. Fix ACCEPTED findings, re-run verification (a non-zero exit is itself an open finding), and
   update the change summary and dependency map for every file the fixes touched.
5. **Exit** when a round reports no CRITICAL/HIGH findings. **Cap: 3 rounds.** At the cap with
   CRITICAL/HIGH still open, or the same finding coming back after a fix: stop, append each open
   CRITICAL/HIGH to the spec's `## Review Notes` marked `UNRESOLVED`, present them to the user,
   and go to Phase 3 without closing.

## Phase 3: Close & Report

1. **Close the spec** only when all three hold: every step is `[x]`, every `## Tests` entry
   exists in the codebase (a section reading `none needed — <reason>` counts as written), and
   Phase 2 exited clean. Then set `status: done` and `git mv` the file to
   `docs/impl-spec/archive/` — this is part of the skill, not a docs suggestion. Otherwise leave
   `status: active` and report which steps, tests, or findings remain.
2. **Report**: what was built, files changed, what the review rounds caught, remaining
   MEDIUM/LOW notes, verification results.

## Delegated execution

Read [delegated execution](references/delegated-execution.md) for the explicit courier workflow
or isolated worker-branch assembly. Automatic shared-checkout execution uses the phases above.
