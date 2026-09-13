Read the [skill entrypoint](../SKILL.md) for shared scope and constraints.

## Supervised Dispatch

Use when you keep ownership — you gate the worker's diff, run review, and assemble. Handing over and stopping is [Full Handoffs](handoffs.md); a `codex-worker` spawn is the `codex-delegation` skill, which does not use orchestration at all.

```text
ORCA worktree create --name <task> --agent claude --base-branch <base> --json
ORCA terminal wait --terminal <agent_handle> --for tui-idle --timeout-ms 120000 --json
ORCA orchestration task-create --spec "<brief>" --task-title <short> --display-name <short> --json
ORCA orchestration dispatch --task <task_id> --to <agent_handle> --inject --json
ORCA orchestration check --terminal <your_handle> --unread --types worker_done,escalation,decision_gate --wait --timeout-ms <n> --json
```

Handles: the worker's is `startupTerminal.handle` from the create response (see **Worktrees**); yours is the current worktree's active terminal, so `--terminal` may be omitted (see **Terminal rules**).

- `--inject` hands the worker its whole protocol: the `worker_done` command with the correct `--from`, a 5-minute heartbeat, `ask` for questions, and escalation. Put the work in `task-create --spec` and leave `--prompt` off the create — a prompt plus a dispatch gives the worker two briefs. When an impl-spec file covers the work, name its absolute path in the brief instead of pasting or summarising it.
- **State in the brief that the protocol is real and name `orca orchestration --help` as the way to confirm it.** A worker that cannot verify `orchestration` refuses the injected preamble as an unverified protocol and reports nothing (measured: refusal without the verification path, compliance with it).
- `check --wait` prints one pretty-printed JSON document on stdout and JSON keepalive lines on stderr. Parse stdout whole (`json.load`); a line-by-line parse silently drops every message and still marks it read.
- Wait on `decision_gate` and `escalation` beside `worker_done`: a worker's question arrives as `decision_gate` and blocks it until you `orchestration reply --id <msg_id> --body <text>`.
- `worker_done` moves the task to `completed` by itself (measured). Reach for `task-update --status failed|completed` only for a task that ended without one — refused, abandoned, or stopped by you.
- One pane holds one active dispatch. `task-update` does not release it and no command clears it, so send a retry to a fresh pane.
- Read `dispatch --dry-run --return-preamble` to see exactly what the worker will be told.
- Assembly and review follow `impl-execute` Phase 2 and [delegated execution](../../impl-execute/references/delegated-execution.md) steps 4 and 6 whatever the worker was — step 6 is what keeps the spec open while the integration branch is unmerged. Worker branches stay off the base branch — AGENTS.md **Merging is the user's call**.
- `orchestration reset` has no per-task scope — it clears every task or every message at once.
