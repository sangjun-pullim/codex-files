Read the [skill entrypoint](../SKILL.md) for shared scope and constraints.

## Full Handoffs

For full ownership transfer, use non-lifecycle terminal/worktree commands and then stop monitoring unless the user asks for supervision.

Treat these as full handoff requests by default: "hand off", "handoff", "handover", "give this to another agent", "give this to another worktree", "send this to another agent", "another agent", "another worktree", or "launch another agent to own this." Custom model or reasoning effort words such as `gpt-5.5`, `high`, or `xhigh` do not make the handoff supervised.

Supervised orchestration remains available only when the user explicitly asks for supervision or coordination: "supervise", "monitor", "wait for worker_done", "wait for results", "track completion", "DAG", "decision gate", "ask/reply", or "coordinate workers."

Do not run `orca orchestration task-create`, `orca orchestration dispatch --inject`, or `orca orchestration check --wait` for full handoffs. `task-create` is also forbidden because it records coordinator-owned tracking state; if a task row is needed, the user asked for supervised orchestration. Do not create a `taskId`/`dispatchId`, inject a lifecycle preamble, wait for completion, or read the worker terminal after prompt delivery except to avoid losing the initial prompt.

New top-level worktree handoff:

```bash
orca worktree create --name <task-name> --no-parent --agent codex --prompt "<task brief>" --json
```

Before creating a new worktree from an active feature branch, decide and state whether the desired Orca lineage is child or top-level. Use child worktree lineage only when the new work is conceptually stacked under or dependent on the active worktree. For independent repo-wide fixes, standalone feature work, or unrelated follow-up tasks, create a top-level worktree with `--no-parent`.

Existing terminal handoff:

```bash
orca terminal send --terminal <handle> --text "<task brief>" --enter --json
```

Custom Codex model/effort handoff:

`orca worktree create --agent codex --prompt ...` launches the known Codex agent but does not accept Codex-specific `--model` or `-c model_reasoning_effort=...` arguments. When the user asks for a specific Codex model or effort, create the independent worktree first, launch Codex with the requested command in that worktree, wait only for TUI readiness if prompt delivery would otherwise race startup, send the prompt, and stop.

Note: when no repo default-terminal configuration supplies a primary terminal, bare create opens a fallback shell before `terminal create` adds the agent. Configured default tabs are materialized instead and may run real commands. Prefer `--agent` whenever custom argv is not required. With the two-step path, target only the agent handle; close a prior terminal only after `terminal list` or `terminal show` confirms it is an unused shell.

Use the exact full `<repo-id>::<path>` worktree id returned by `orca worktree create --json`; a bare repo id cannot target the new worktree.

```bash
orca worktree create --name <task-name> --no-parent --json
orca terminal create --worktree id:<newFullWorktreeId> --title <task-name> --command 'codex --model gpt-5.5 -c model_reasoning_effort="xhigh"' --json
orca terminal wait --terminal <handle> --for tui-idle --timeout-ms 60000 --json
orca terminal send --terminal <handle> --text "<task brief>" --enter --json
```

Wait only for `tui-idle` when needed to avoid losing the prompt. Do not monitor task completion.

`--no-parent` only controls Orca lineage; it does not choose the Git base. If the work should start from the repo default base, omit `--base-branch` so Orca uses that default, or explicitly pass the repo default base (`origin/main`, `origin/master`, or the `orca repo show --repo <selector> --json` value); never base it on the current feature branch unless the user explicitly asks for stacked work or "branch from current". Put current-branch context in the prompt instead.
