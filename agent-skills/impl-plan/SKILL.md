---
name: "impl-plan"
description: "Create or verify an implementation plan when requested, or when AGENTS.md requires approval before implementation."
---

# Implementation Plan with Code-Verified Review Loop

Write a concrete plan into `docs/impl-spec/`, then have a fresh-context `reviewer` verify every
claim against the actual code. The plan's author has already read the code and glosses over what
it "understands"; a reviewer that starts from scratch catches wrong line numbers, missed callers,
and skipped patterns.

## Do NOT use when

- A small change needs no written plan and the user did not request one — plan inline; AGENTS.md still controls required tests and reviews.
- The problem itself is still vague — sharpen it with `grilling` first
- An approved spec already exists and it is time to build — `impl-execute`

## Phase 0: Requirements

- Consult relevant PRD scope/non-goals when product intent affects this plan. Surface
  contradictions requiring a user decision; missing documentation alone is not a gate.
- State the goal, scope, acceptance checks, and affected files. Discover facts from code and
  resolve routine choices using existing conventions. Ask only for missing decisions that
  materially change the result; bundle independent questions and continue independent analysis.

## Phase 1: Plan Creation

**Verifying an existing plan** (the user points at a plan document — an active
`docs/impl-spec/` file or any other): skip drafting and numbering — edit that file in place, add
a `risk-surface` field if its frontmatter predates it (an old `tier` field can stay), and go to
Phase 2. For editing a step already marked `[x]`, see the `second-brain` skill's impl-spec
Lifecycle.

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

1. Spawn a **new** `reviewer` agent (never reuse one — fresh context is the point) with the spec
   path. It runs in Plan verification mode (`~/.codex/agents/reviewer.toml`). From round 2 on, also pass the
   previous round's disposition table.
2. **Disposition** — for each finding: `ACCEPTED` (fix the spec) or `REJECTED` with concrete
   evidence (file:line or reasoning). "Not needed" without evidence is not a rejection.

   | Finding | Severity | Disposition | Rationale |
   |---------|----------|-------------|-----------|

3. Apply ACCEPTED findings to the spec body. Append REJECTED and out-of-scope findings to
   `## Review Notes` with their rationale, so later reviewers and the implementer see what was
   deliberately declined.
4. **Exit** when a round reports no CRITICAL/HIGH findings. **Cap: 3 rounds.** If CRITICAL/HIGH
   findings remain at the cap, or the same finding keeps coming back, stop: append each open
   CRITICAL/HIGH to `## Review Notes` marked `UNRESOLVED` and tell the user the spec is not
   review-clean — `/impl-execute` must not run on it until those rows are cleared.

## Phase 3: Present

Present the spec path, the risk surface recorded in its frontmatter, what the review rounds
found and fixed, and any remaining MEDIUM/LOW notes. For a planning-only request, stop after presenting the reviewed spec. If implementation
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
