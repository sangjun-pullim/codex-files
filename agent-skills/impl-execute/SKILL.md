---
name: "impl-execute"
description: "Implement a reviewed plan in docs/impl-spec/ when execution is authorized and approval gates are satisfied; verify it and complete review and lifecycle steps."
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

- Require an implementation request or existing authorization covering the plan. A reviewed
  plan does not require a separate approval turn unless AGENTS.md's approval boundaries apply.
- Spec path (`docs/impl-spec/<NNN>-*.md`). Reuse the plan already selected in the
  conversation. Otherwise inspect active top-level specs and use the unique relevant plan;
  ask only when multiple plausible plans remain. Selection does not itself grant approval.
  A replacement still marked pending in `## Review Notes` must complete
  [`impl-plan` Phase 3](../impl-plan/SKILL.md#phase-3-present) before execution.
- If `## Review Notes` has `UNRESOLVED` rows, block ordinary execution. Scoped continuation
  of an active implementation-review loop follows Phase 2 and the review workflow; it is
  not a restart or permission to implement an unresolved plan. Resolve plan-review
  findings through `/impl-plan`, or by hand with evidence only when AGENTS.md does not require
  independent review confirmation.
- When the user resumes corrections for implementation-review findings under AGENTS.md,
  retain those rows and correct the approved implementation through Phase 1 steps 2–4, even
  when all steps are already `[x]`. Then run Phase 2 in Implementation verification mode;
  remove only rows the independent reviewer explicitly confirms are resolved. Unresolved
  plan-review findings and remaining approval gates still block implementation. Review restart and stop counting follow AGENTS.md **리뷰 종료·재개**.
- Before implementation, record the fixed starting commit as `<base-commit>`
  (`git rev-parse HEAD`) and the return branch separately as `<base>`
  (`git symbolic-ref --quiet --short HEAD`; detached HEAD has no return branch).
  Keep both and the initial dirty-file inventory in the spec's `## Review Notes`.
  Reuse that starting commit on resume. If it was not recorded, reconstruct the task's
  starting point from its commits and spec; do not use the current HEAD and omit earlier work.
  Identify pre-existing changes separately so review covers the task without claiming others' edits.

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
   - All `[x]` but `status: active` → implement nothing; run Phase 2 on the whole task's
     change inventory from its recorded baseline, including pending changes, then close via Phase 3.
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

Read [review workflow](~/.codex/rules/review-workflow.md) before this phase. It defines
disposition, reproduction, scoped stops, and resume/closure; use it for every round.

1. Build the review inventory without changing the index. `git diff --binary <base-commit>`
   covers the net tracked change from the fixed starting commit to the working tree.
   Also inspect `git diff --cached --binary` and `git diff --binary` so staged and unstaged
   changes that cancel each other remain visible. Use `git ls-files --others --exclude-standard -z`
   to enumerate untracked files and include task-owned additions with their contents or
   `git diff --no-index --binary -- /dev/null <file>` (exit 1 means differences).
   Save the task patch and these inventories under `<scratch>/review-N.*`, identify
   pre-existing changes, and give the reviewer all task changes, committed or pending.
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

4. Apply **리뷰 정지** from the review workflow before any correction, including reproduction tests.
   Freeze stopped/dependent work; continue only corrections and verification whose independence
   is established under that workflow. Fix eligible ACCEPTED findings
   using **동작 지적의 재현**, update any resulting REJECTED disposition in Review
   Notes, re-run affected required verification, and update the change summary and dependency
   map. After independent work is exhausted, report any remaining stop in Phase 3 without
   closing. A failed required check remains a completion blocker regardless of review severity.
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
   MEDIUM/LOW notes and REJECTED findings with their rationale.
   Apply `~/.codex/AGENTS.md` `## Communication` **변경 보고** to this user-facing report.

## Delegated execution

Read [delegated execution](references/delegated-execution.md) for the explicit courier workflow
or isolated worker-branch assembly. Automatic shared-checkout execution uses the phases above.
