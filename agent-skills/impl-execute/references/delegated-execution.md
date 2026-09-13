# Delegated execution

For an explicit `codex-worker` courier request, read [codex-delegation](../../codex-delegation/SKILL.md)
and use steps 1–6. For automatic Astra routing and other supervised workers, use their dispatch workflow and the union
assembly and completion rules in steps 4 and 6. Phase references below point to
[impl-execute](../SKILL.md). AGENTS.md owns the worktree/in-place choice and review reuse.

1. **Split** the unchecked steps into workers with disjoint file sets. A step that changes an
   exported signature, schema, barrel, or shared type runs alone; a signature change and its
   callers stay in one worker; no clean split → sequential. Each `## Tests` entry goes to the
   worker owning the step it pins.
2. **Dispatch** one `codex-worker` per group with the spec's absolute path, the step numbers it
   owns, the `## Tests` entries for those steps quoted verbatim, and `<base>`. Workers never write
   the spec; you flip markers after gating. In-place mode: one worker at a time.
3. **Gate each report mechanically** (no diff review here): `codex 호출 0회` or no session id →
   failed, re-dispatch; any `검증 → exit` non-zero → send the failing output back as a rework
   request to the same session; `스펙 외 변경 파일` non-empty → inspect those paths; orca mode →
   `git -C <worktree> log <base>..HEAD` must be non-empty (commit a dirty worktree there
   yourself — that is assembly, not implementation). After two failures of the same check,
   stop repeating the same approach. Inspect the evidence; a new, concrete cause can justify
   a bounded correction within the authorized scope. Record what changed before another
   attempt. If no new evidence or safe correction remains, mark that group blocked and
   report its raw output and log path. Continue independent groups; never mark failed work
   complete or close the spec while it remains blocked.
   All clear → mark that group's steps `[x]` in the base checkout.
4. **Assemble the union** — Phase 2 reviews one combined change.
   - In-place: the checkout already holds it; `git add -A -N && git diff` is the union.
   - Orca worktree: `git switch -c <task>-integration <base>`, **commit the spec marker flips
     there**, merge each worker branch. A merge conflict is a cross-worker collision — resolve
     only if mechanical, otherwise send it back to the owning sessions. Run build/lint/test on
     the integration branch before any review: stale imports and mismatched signatures fail only
     here. The patch for Phase 2 is `git diff <base>...HEAD`; pass the integration branch name.
   - Write the change summary and dependency map for the union yourself, attributing each step
     to its worker.
5. **Phase 2 fixes** go back to the owning Codex session as rework (re-spawn the worker against
   the same worktree/checkout with the session id and the correction verbatim), then re-gate and
   re-assemble. A one-line mechanical fix may be done by you — say so, and in orca mode commit it
   on the integration branch.
6. **Phase 3 in orca worktree mode**, whatever the worker was: do not close the spec — the code sits on an unmerged integration
   branch. Return the repo-root checkout to `<base>`, then report: worker → steps → Codex
   worker id (codex: session id), the integration and worker branches, that nothing was merged into `<base>`, and
   the cleanup the user runs after merging: `orca worktree rm --worktree path:<worktree>` per
   worker, then `git branch -D` on each worker branch and `<task>-integration`. Never remove a
   worktree holding uncommitted changes. Close the spec after the user merges.
