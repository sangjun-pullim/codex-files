Read the [skill entrypoint](../SKILL.md) for shared scope and constraints.

## Messaging

```bash
orca orchestration send --to <handle|@group> --subject <text> [--from <handle>] [--body <text>] [--type <type>] [--priority <level>] [--thread-id <id>] [--payload <json>] [--json]
orca orchestration check [--terminal <handle>] [--unread|--peek|--all] [--types <type,...>] [--inject] [--wait] [--timeout-ms <n>] [--json]
orca orchestration reply --id <msg_id> --body <text> [--from <handle>] [--json]
orca orchestration ask --to <handle> --question <text> [--options <csv>] [--timeout-ms <n>] [--from <handle>] [--json]
orca orchestration inbox [--limit <n>] [--json]
```

Rules:

- Omit `--from` unless impersonating another terminal; Orca auto-resolves it from the current terminal.
- `check` and `check --unread` return unread matches and mark them read. Use `--peek` for unread matches without consuming them; use `--all` for read and unread history without consuming anything. If an older CLI rejects `--peek` as an unknown flag, use `--all` and filter unread rows yourself.
- Message **one** live agent handle per worker. Use `startupTerminal.handle` from the create response when present; if it is missing or later returns `terminal_handle_stale`, re-resolve with `orca terminal list --worktree ... --json` and continue with the replacement only.
- `orca orchestration check --unread --inject --json` renders unread mail for the agent terminal that runs it; it does not remotely wake another terminal. Use `orchestration dispatch --inject` to deliver a tracked task, or `terminal send` when an existing agent needs a free-form prompt.
- While supervising workers manually, use `check --wait --types worker_done,escalation,decision_gate --timeout-ms <n>` instead of sleep/poll loops. Reply to `decision_gate` messages with `orca orchestration reply --id <msg_id> --body <answer> --json`, then keep waiting.
- Treat a `check --wait` timeout or `{count:0}` as a checkpoint, not a worker failure. Long coding tasks routinely run 15-60 minutes; keep using rolling waits unless you receive `worker_done`/`escalation`, the terminal exits or disappears, or the user explicitly asks you to stop.
- Heartbeats and visible terminal activity mean the worker is alive, not done. Do not stop, close, kill, or restart a worker just because it has not produced a completion message yet.
- Use `ask` when a worker needs a blocking answer from the coordinator; it waits for the reply and returns the answer directly.
- `check --wait` returns one message at a time. If N workers may finish together, loop N times and dispatch newly ready tasks after each completion.
- Group addresses include `@all`, `@idle`, `@claude`, `@codex`, `@opencode`, `@gemini`, `@droid`, `@grok`, `@cursor`, and `@worktree:<id>`.
- Message types include `status`, `dispatch`, `worker_done`, `merge_ready`, `escalation`, `handoff`, `decision_gate`, and `heartbeat`.
- Use group addresses only for messages that are genuinely useful to many terminals, such as `status` broadcasts or intentional fan-out questions. Do not send dispatch lifecycle messages to groups.
- `worker_done` must target the concrete coordinator handle from the live preamble. It is completion authority for one dispatch; group fanout would create false lifecycle mail in unrelated terminals.
- A valid `worker_done` for the active `taskId` + `dispatchId` marks the task and dispatch completed automatically. Do not follow it with `task-update --status completed`; reserve manual updates for explicit recovery or overrides.
- `heartbeat` is also dispatch-scoped. Send it only to the concrete coordinator handle with both `taskId` and `dispatchId`; use `status` for broad progress updates.


## Tasks And Dispatch

A task is the work item, a dispatch assigns it to a terminal, and a gate blocks progress until a coordinator or user decision is recorded.

```bash
orca orchestration task-create --spec <text> [--deps <json_array>] [--parent <task_id>] [--json]
orca orchestration task-list [--status <status>] [--ready] [--brief] [--json]
orca orchestration task-update --id <task_id> --status <status> [--result <json>] [--json]
orca orchestration dispatch --task <task_id> --to <handle> [--from <handle>] [--inject] [--json]
orca orchestration dispatch-show --task <task_id> [--json]
```

Task statuses: `pending`, `ready`, `dispatched`, `completed`, `failed`, `blocked`.

Dispatch rules:

- `--inject` sends the task spec plus preamble into a recognized agent CLI so it can report `worker_done`.
- If the target is a bare shell, omit `--inject`, dispatch for tracking if needed, then send the prompt manually with `orca terminal send --terminal <handle> --text <prompt> --enter --json`.
- After 3 consecutive failures on one task, the dispatch context circuit-breaks and the task is marked failed.
- Use `task-list --brief --json` for coordinator sweeps; it collapses whitespace and caps each echoed spec at 160 characters (`spec_truncated` marks shortened rows). Omit `--brief` when the full spec is required, or when an older CLI rejects it as an unknown flag.


## Gates And Coordinator

```bash
orca orchestration gate-create --task <task_id> --question <text> [--options <json_array>] [--json]
orca orchestration gate-resolve --id <gate_id> --resolution <text> [--json]
orca orchestration gate-list [--task <task_id>] [--status <status>] [--json]
orca orchestration run --spec <text> [--from <handle>] [--poll-interval-ms <n>] [--max-concurrent <n>] [--worktree <selector>] [--json]
orca orchestration run-stop [--json]
```

`run` returns immediately with a run ID. Query progress with `task-list`. Use `ask` for worker-to-coordinator questions; it creates a `decision_gate` message that the coordinator answers with `reply`. Use `gate-create` only for coordinator-managed task DAG decisions, not for answering a worker's `ask`.

Recovery only: `orca orchestration reset --tasks|--messages|--all --json` clears runtime-global orchestration state. Do not run it during active coordination unless explicitly abandoning that state.
