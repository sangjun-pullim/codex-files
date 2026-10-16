---
name: "impl-plan"
description: "Create or verify an implementation plan when requested, or when AGENTS.md requires approval before implementation."
---

# Implementation Plan with Code-Verified Review Loop

Create a concrete plan in `docs/impl-spec/`, or review an existing plan within the requested
write scope, then have an independent `reviewer` verify its claims against the code.
The plan's author has already read the code and glosses over what
it "understands"; a reviewer that starts from scratch catches wrong line numbers, missed callers,
and skipped patterns.

## Do NOT use when

- A small change needs no written plan and the user did not request one — plan inline; AGENTS.md still controls required tests and reviews.
- The user wants an idea interview rather than a plan — use `grilling`. For a plan with
  unresolved requirements, ask only the material decisions needed for that plan.
- An approved spec already exists and it is time to build — `impl-execute`

## Phase 0: Requirements

- Consult relevant PRD scope/non-goals when product intent affects this plan. Surface
  contradictions requiring a user decision; missing documentation alone is not a gate.
- State the goal, scope, acceptance checks, and affected files. Discover facts from code and
  resolve routine choices using existing conventions. Ask only for missing decisions that
  materially change the result; bundle independent questions and continue independent analysis.

## Phase 1: Plan Creation

**Verifying an existing plan**: skip drafting and numbering, and go to Phase 2. A review-only
request leaves the file unchanged: report findings and proposed edits, including any needed
`risk-surface` field. If plan edits are already requested or approved, update the active file
in place; an old `tier` field can stay. For editing a step already marked `[x]`, follow the
`second-brain` skill's impl-spec Lifecycle. Archived specs remain frozen.

1. **Scope analysis** — spawn a `planner` agent with the requirements above. Resolve factual
   questions through inspection; bring only material scope/design decisions to the user.
2. **Draft the spec** in the Output Format below. The planner's code dependencies and document
   copies per changed rule go into `## Affected Dependents`, including owners and search gaps;
   existing patterns constrain the steps. Use `## Change Map` when relationships help explain
   the change, with `restates` edges for document copies. A found copy is a dependency to assess,
   not automatic permission to change an external contract or declare another team's ownership.
   The implementer never sees the scope report, so carry its relevant evidence into the spec.
3. **Save** to `docs/impl-spec/<NNN>-<short-description>.md`. `NNN` = highest existing number
   across `docs/impl-spec/` and `docs/impl-spec/archive/` + 1, zero-padded to 3 digits; `001` if
   none. Create the directory if missing.
   - If this plan replaces an existing spec, set the old one's frontmatter to
     `status: superseded-by: <new NNN>` and move it to `docs/impl-spec/archive/`.

## Phase 2: Review Loop

1. Reuse valid independent review evidence under AGENTS.md's review-reuse rule. When a new
   review is needed, spawn a **new** `reviewer` agent with the spec
   path. It runs in Plan verification mode (`~/.codex/agents/reviewer.toml`). From round 2 on, also pass the
   previous round's disposition table.
2. **Disposition** — classify each CRITICAL/HIGH finding under AGENTS.md **리뷰 루프**.
   Give concrete evidence for REJECTED findings (file:line or reasoning).

   | Finding | Severity | Disposition | Rationale |
   |---------|----------|-------------|-----------|

3. Apply AGENTS.md **리뷰 정지** before any correction. Unless stopped, apply ACCEPTED
   findings to the spec when editing is authorized. Record REJECTED findings with rationale
   in `## Review Notes`. In read-only reviews, leave the spec unchanged and present dispositions
   and proposed corrections in Phase 3; proposed corrections do not resolve open findings.
4. **Exit, stop, and resume** follow AGENTS.md **리뷰 종료·재개** and **리뷰 정지**.
   Pass retained UNRESOLVED rows to the reviewer for explicit resolution confirmation;
   remove only confirmed rows. On a stop, report that the spec is not review-clean.
   Unresolved plan-review findings block implementation; implementation-review corrections
   follow `/impl-execute`'s Inputs.

## Phase 3: Present

Present the spec path, the risk surface, findings, applied or proposed corrections, and any
remaining MEDIUM/LOW notes and REJECTED findings with their rationale. For a review-only or planning-only request, finish after presenting the report. If implementation
is already authorized and applicable approval gates are satisfied, continue with `impl-execute`.

## Output Format

```markdown
---
status: active            # active | done | superseded-by: <NNN>
date: <YYYY-MM-DD>
risk-surface: <none | auth | payment | permission | db-schema | public-api>
---
> NOTE: This is the plan, not a description of the code — never read it as evidence of current code state. While `status: active`, edit it in place as the plan changes; once archived it is frozen.

# [Title]

## Context
[Problem and motivation; reference the PRD section if one exists — never restate it]

## Affected Files
1. `path/to/file.ts` — brief description of change

## Affected Dependents
[Code that must keep working: callers of every signature this touches, consumers of every export
it renames, routes behind a middleware it alters. One line each with a path.
For each changed rule, one line with the count of document copies found, every `path:line` and
its documented owner (`this repo`, named other team/system, or `unstated`), and search scope/gaps.
Include changed documents as well as unchanged consumers; do not treat the count as exhaustive.]

## Change Map
[Include when relationships help explain the change; omit otherwise. Show code dependency edges
such as `calls` / `consumes` and document edges as `doc/path:line --restates--> rule or canonical
source`. A `restates` edge identifies a statement that reasserts the rule, not a mere link to it.]

## Implementation Steps

Every step heading carries a progress marker: `[ ]` unstarted, `[x]` implemented.
`/impl-execute` flips these as it works. Write them all as `[ ]`.

### [ ] Step N: [Title]
**File**: `path/to/file.ts`
- Change description with specific line references
- Code snippets where helpful

## Tests
[Required. Name each test to add or change and the behavior it pins. When `risk-surface` is not
`none`, "none needed" is not an available answer; off the risk surface it needs a reason.]

## Risks
- [Risk and mitigation]

## Verification
- [Commands that prove the change works]

## Review Notes
<!-- REJECTED / out-of-scope findings with rationale; UNRESOLVED plan-review findings block implementation. Resuming implementation-review corrections follows /impl-execute. -->

| Finding | Severity | Disposition | Rationale |
|---------|----------|-------------|-----------|
```
