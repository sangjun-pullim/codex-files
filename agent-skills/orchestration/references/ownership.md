Read the [skill entrypoint](../SKILL.md) for shared scope and constraints.

## Ownership

Orchestration messages and tasks are runtime-global. Lifecycle authority comes from the payload `taskId` + `dispatchId` of the active dispatch, verified against the dispatched pane. Terminal handles are routing metadata — a pane can receive a new handle after restart — so never accept or reject lifecycle provenance by comparing handles. Send `worker_done` and `heartbeat` from the worker's own terminal; the runtime ignores them when sent from a different pane.

Classify inherited context before sending lifecycle messages:

- Coordinated subtask: a live coordinator owns the DAG and waits on this dispatch. Follow the preamble exactly, including `worker_done`, heartbeat/status, `ask`, and `escalation`.
- Full handoff means ownership transfer, not supervised dispatch. The original actor is not monitoring a DAG, so do not create lifecycle obligations unless the user explicitly asks you to supervise.
- Classify requests containing "hand off", "handoff", "handover", "give this to another agent", "give this to another worktree", "another agent", or "another worktree" as full handoffs by default, even when the user names a custom model or reasoning effort.
- Use supervised orchestration only when the user explicitly asks you to "supervise", "monitor", "wait", "track completion", "wait for worker_done", return results, coordinate a DAG, use a decision gate, or manage ask/reply flow.
- Do not use `orca orchestration dispatch --inject` for full handoffs. It injects a coordinator preamble that tells the worker to send `worker_done`, heartbeat, and `ask` messages, then end its turn under the original terminal's dispatch lifecycle.
- Do not run `orca orchestration task-create`, `orca orchestration dispatch --inject`, or `orca orchestration check --wait` for full handoffs. Do not peek at terminal output after prompt delivery to monitor progress.
- A review-only `worker_done` reports findings; it does not authorize coordinator file edits. After a review-only completion, synthesize findings, ask a decision gate if ownership is unclear, and dispatch or hand off fixes unless the user explicitly asked the coordinator to own fixes.
- If the user's plan names a next owner agent (for example, "then use opencode to create a PR"), post-review corrections and PR prep belong to that named owner. The coordinator routes, synthesizes, asks decision gates when needed, and supervises; the named owner edits files and creates the PR.

If unclear, inspect orchestration state before sending lifecycle messages:

```bash
orca orchestration task-list --json
orca terminal list --json
# If inherited context includes a task id:
orca orchestration dispatch-show --task <task_id> --json
```
