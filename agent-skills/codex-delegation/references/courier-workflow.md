# Explicit Codex courier workflow

## Do NOT use when

- The user did not explicitly request the `codex-worker` courier workflow. Automatic Astra routing uses [automatic dispatch](automatic-dispatch.md) instead; a large plan alone does not select this courier workflow.
- Planning or reviewing — `codex-worker` is implementation-only. A one-off fix needs no spec
  file; a multi-step change does (`impl-plan` first).

## Rules

- **Always run codex through a `codex-worker` spawn — never `codex exec` from your own Bash.** The worker absorbs codex's output (measured: 167k tokens of codex traffic in, ~1.2k reported back); running it yourself puts all that traffic in the top model's context. In-place mode — no Orca card to show for the spawn — is exactly where skipping the worker is most tempting. Only exception: a one-line diagnostic (`codex exec -s read-only "…"` to confirm codex itself works).
- Pass the selected mode and exact checkout to `codex-worker`. In Orca mode it reuses a
  specified existing worktree/card or creates a new one when that is the selected location.
  A new task starts a fresh Codex session; only explicit rework resumes the task's session.
- Before dispatch, classify reuse of the supervisor's own checkout as in-place, even if it
  is registered as a Git or Orca worktree. Courier Orca mode requires a separate worker
  checkout on a branch distinct from `<base>` so its commits can be gated and assembled.
  Pass the supervisor checkout and `<base>` for that check. Resolve conflicting mode and
  location instructions at the supervisor; the courier must not silently switch either.
- Apply AGENTS.md's **워크트리 분리** rule before dispatch. Reuse an already specified or
  approved location for the task and its rework; ask only when an unresolved location choice
  materially affects the result. When in-place is chosen, state "in-place mode" in the prompt.
- In-place mode is single-worker: workers run one at a time in the shared checkout. If the task plans 2+ parallel workers, recommend orca worktree mode in the question (mention in-place would serialize them).
- If `orca status` fails, use AGENTS.md's fallback rule; do not override a specified location
  or isolation requirement silently.
- Worker branches are NOT merged by the worker, and never onto the base branch — that stays the user's call. Union assembly: [delegated execution](../../impl-execute/references/delegated-execution.md).
- Worktrees and their cards are cleaned up only after that call. A card that no longer represents live or pending work is noise in the dashboard that exists to show what *is* running. Procedure: [delegated execution](../../impl-execute/references/delegated-execution.md).
- Astra remains the supervisor and reviewer. Pass its selected implementation model and reasoning effort to the courier; the actual Codex CLI process must use those values explicitly. The courier only transports that assignment.

## Delegation practice — you judge, codex implements

`codex-worker` is a courier: it launches codex and reports facts — it never rewrites the spec, rules on correctness, or re-prompts codex on its own. Every judgment call is yours. The full dispatch procedure (split, gate, union assembly, review loop, rework) lives in the [delegated execution](../../impl-execute/references/delegated-execution.md); the contract below holds for ANY codex dispatch, ad-hoc included:

- **Name codex as the implementer in the spawn prompt** — "codex로 구현하라" / "codex를 실행해 …", never "편집하라" / "수정하라" (measured: the latter made a worker skip codex and edit files itself; the verb decides the outcome).
- **Give the actual CLI child its worker role** — Astra includes in the unchanged prompt:
  "You are a bounded implementation worker supervised by Astra. Do not classify the overall
  task, choose another model, launch other agents or Codex processes, or perform final
  approval. Implement the assigned scope and return evidence to Astra. Preserve others' edits."
  `agents.enabled=false` disables native subagents; this role also excludes CLI re-delegation.
- **Hand over the spec by file path, not paraphrase** — the worker feeds it to codex unchanged; re-summarizing invites drift.
- **Gate each report mechanically before trusting the diff** — the checks, and the bound on re-dispatch, are the [delegated execution](../../impl-execute/references/delegated-execution.md) gate. At that gate open the full diff only on failure or out-of-scope files; the *union* diff is read unconditionally later, at assembly, and a reviewer agent judges it regardless (see the **Review once over the union** bullet).
- **Rework goes through you**: re-spawn against the same worktree with the session id and the correction stated verbatim. The worker never retries on its own.
- **Parallel split**: use the ownership and sequencing rules in delegated execution step 1
  when dispatching; a large plan alone does not justify parallel workers.
- **Review once over the union, never per worker** — cross-worker breakage (stale imports, mismatched signatures) only shows in the combined diff. Codex implementing does not make you the reviewer: a `reviewer` agent reviews the union, always. Read the union diff yourself to write the change summary you hand it; the verdict is the reviewer's.
