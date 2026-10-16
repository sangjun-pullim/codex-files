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
- If `## Review Notes` has `UNRESOLVED` rows, block ordinary execution. Resolve plan-review
  findings through `/impl-plan`, or by hand with evidence only when AGENTS.md does not require
  independent review confirmation.
- When the user resumes corrections for implementation-review findings under AGENTS.md,
  retain those rows and correct the approved implementation through Phase 1 steps 2–4, even
  when all steps are already `[x]`. Then run Phase 2 in Implementation verification mode;
  remove only rows the independent reviewer explicitly confirms are resolved. Unresolved
  plan-review findings and remaining approval gates still block implementation. Review restart and stop counting follow AGENTS.md **리뷰 종료·재개**.
- Record the base branch as `<base>` (`git rev-parse --abbrev-ref HEAD`).

**Who implements**: The supervisor first applies AGENTS.md's subscription-usage decision. Implement directly
when delegation is not selected; otherwise use [codex-delegation](../codex-delegation/SKILL.md).
The supervisor retains the phases and spec lifecycle below in either case.
An explicit `codex-worker` courier request uses
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
   Include retained `UNRESOLVED` findings and ask for explicit confirmation of their resolution.
3. **Disposition** — classify each CRITICAL/HIGH finding under AGENTS.md **리뷰 루프**.
   Remove retained UNRESOLVED rows only after independent confirmation of resolution.
   Record REJECTED findings and concrete evidence in the spec's `## Review Notes`.

   | Finding | Severity | Disposition | Rationale |
   |---------|----------|-------------|-----------|

4. Apply AGENTS.md **리뷰 정지** before any correction, including reproduction tests.
   On a stop, fix nothing and go to Phase 3 without closing. Otherwise fix ACCEPTED findings
   using AGENTS.md **동작 지적의 재현**, update any resulting REJECTED disposition in Review
   Notes, re-run affected required verification, and update the change summary and dependency
   map. A failed required check remains a completion blocker regardless of review severity.
5. **Exit, stop, and resume** follow AGENTS.md **리뷰 종료·재개** and **리뷰 정지**.

## Phase 3: Close & Report

1. **Close the spec** only when all four hold: every step is `[x]`, every `## Tests` entry
   exists in the codebase (a section reading `none needed — <reason>` counts as written),
   the spec's Verification commands and applicable required checks have passing results valid
   for the final code/configuration/inputs (run any missing or invalidated checks now), and
   Phase 2 ended by exit rather than a stop with no UNRESOLVED rows remaining. Then set `status: done` and `git mv` the file to
   `docs/impl-spec/archive/` — this is part of the skill, not a docs suggestion. Otherwise leave
   `status: active` and report which steps, tests, or findings remain.
2. **Report**: what was built, files changed, what the review rounds caught, remaining
   MEDIUM/LOW notes and REJECTED findings with their rationale, verification results.

## Delegated execution

Read [delegated execution](references/delegated-execution.md) for the explicit courier workflow
or isolated worker-branch assembly. Automatic shared-checkout execution uses the phases above.
