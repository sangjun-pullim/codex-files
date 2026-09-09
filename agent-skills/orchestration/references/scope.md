Read the [skill entrypoint](../SKILL.md) for shared scope and constraints.

## Tool Boundary

If a task says to use Orca orchestration, the coordinator must create Orca runtime state with `orca orchestration task-create` and `orca orchestration dispatch --inject` or `orca orchestration run`.

Do not substitute non-Orca subagent tools, generic agent-spawn APIs, or chat-only parallel worker features. Those may create useful workers, but they do not create Orca task/dispatch provenance, injected lifecycle preambles, `worker_done` authority, or decision gates.

Before claiming a worker was orchestrated, verify the task/dispatch exists:

```bash
orca orchestration task-list --json
orca orchestration dispatch-show --task <task_id> --json
```

If the work was accidentally run outside Orca orchestration, say so plainly. To repair provenance, rerun or revalidate the needed work through a fresh Orca terminal plus injected dispatch; do not retroactively describe the external worker as orchestrated.


## When To Use

- Send/reply/ask between agent terminals with persistent messages.
- Dispatch structured tasks to workers and wait for `worker_done` or `escalation`.
- Track task DAGs with dependencies.
- Run coordinator loops or decision gates.

Do not use orchestration merely because the user says "hand off", "handoff", "handover", "give this to another agent", or asks for another worktree/agent/model/effort. Those are full ownership transfers unless the user explicitly asks to supervise, monitor, wait for worker completion/results, coordinate a DAG, use decision gates, or keep a blocking ask/reply loop.


## Preconditions

- `orca status --json` should show a running runtime.
- `orca` must be on PATH (`orca-ide` on Linux).
- The orchestration experimental feature must be enabled in Settings > Experimental.
- `orca orchestration` commands are RPC calls to the running Orca runtime.
