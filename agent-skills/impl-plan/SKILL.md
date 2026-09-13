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
2. **Draft the spec** in the Output Format below. The planner's reverse dependencies and existing
   patterns go into `## Affected Dependents` and the steps — the implementer never sees the scope
   analysis, so the spec is how they reach it.
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
2. **Disposition** — for each finding: `ACCEPTED` (fix the spec when authorized, otherwise
   propose the correction) or `REJECTED` with concrete
   evidence (file:line or reasoning). "Not needed" without evidence is not a rejection.

   | Finding | Severity | Disposition | Rationale |
   |---------|----------|-------------|-----------|

3. For an authorized plan creation or edit, apply ACCEPTED findings to the spec body. Append
   REJECTED and out-of-scope findings to `## Review Notes` with their rationale. For a
   review-only request, put dispositions and proposed corrections in the report, leave the
   spec unchanged, and proceed to Phase 3; proposed fixes do not clear open findings.
4. **Exit** when a round reports no CRITICAL/HIGH findings. **Cap: 3 rounds.** If CRITICAL/HIGH
   findings remain at the cap, or the same finding keeps coming back, stop: append each open
   CRITICAL/HIGH to `## Review Notes` marked `UNRESOLVED` and tell the user the spec is not
   review-clean — `/impl-execute` must not run on it until those rows are cleared.

## Phase 3: Present

Present the spec path, the risk surface, findings, applied or proposed corrections, and any
remaining notes. For a review-only or planning-only request, finish after presenting the report. If implementation
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
[Code that must keep working but is not being changed: callers of every signature this touches,
consumers of every export it renames, routes behind a middleware it alters. One line each with a path.]

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
<!-- REJECTED / out-of-scope findings with rationale; UNRESOLVED rows block /impl-execute. -->

| Finding | Severity | Disposition | Rationale |
|---------|----------|-------------|-----------|
```
