Read the [skill entrypoint](../SKILL.md) for shared scope and constraints.

## Worker Terminals

Choose the worker location before creating a terminal. `Fresh worker` means a fresh agent session, not a new git worktree. If the task says current worktree only, depends on uncommitted files/artifacts, or must validate/PR the current branch, create the worker in the active worktree:

```bash
orca terminal create --worktree active --title <task-name> --command "codex" --json
orca terminal wait --terminal <handle> --for tui-idle --timeout-ms 60000 --json
orca orchestration dispatch --task <task_id> --to <handle> --inject --json
```

Reuse an idle agent in the required worktree only if the prompt allows reuse; otherwise create a fresh terminal there. Use a new worktree only when explicitly requested or when independent isolated checkout state is intended. For supervised new-worktree workers, decide the desired Orca lineage before creation: use child lineage only when the work is conceptually stacked under or dependent on the active worktree, and use `--no-parent` for independent repo-wide fixes, standalone feature work, or unrelated follow-up tasks. Decide the Git base separately from lineage: `--no-parent` makes the worktree top-level in Orca, while omitted `--base-branch` uses the repo default base.

```bash
orca worktree create --name <task-name> --agent codex --json
# or: --agent claude | omp | pi | grok | ...
# Read <handle> from startupTerminal.handle in the create response.
orca terminal wait --terminal <handle> --for tui-idle --timeout-ms 60000 --json
orca orchestration dispatch --task <task_id> --to <handle> --inject --json
```

For new-worktree workers, read the id and `startupTerminal.handle` from `worktree create`. Use that as the sole worker handle when present; otherwise use `terminal list` to resolve the agent handle. Omit `--repo` only inside an Orca-managed worktree; otherwise pass `--repo <selector>`.

**Agent-first (required for ordinary agent workers):** `--agent` reveals the new worktree and launches the selected agent **in its first terminal**, without adding a separate fallback shell for that worker. Repo setup or default-terminal settings may still add tabs or splits. Do **not** run bare `worktree create` and then `terminal create --command <agent>` for the same worker when agent-first create is available: without configured default tabs, that two-step path leaves a fallback shell + agent pair. Only use it when custom agent argv is required (for example Codex model/effort flags) or when an older CLI rejects `--agent`; if you must, message only the agent handle. Configured default tabs are intentional surfaces, so close a prior terminal only after `terminal list` or `terminal show` confirms it is an unused shell. Do not run `worktree create` when the task must stay in the current worktree.

Use `orca worktree create --prompt ...` or `orca terminal send ...` for full handoffs or untracked/lightweight prompts. Those paths do not attach `taskId`/`dispatchId`; the worker should not send lifecycle messages unless the prompt supplies a live orchestration preamble.

Sidebar lineage and orchestration lifecycle are related but not identical. A same-worktree worker created with `orca terminal create --worktree active` may appear as a peer terminal/agent under the same worktree in the sidebar even though it is a child dispatch in Orca orchestration state. A visible parent/child worktree relationship requires creating a child worktree, but do that only when the task can safely run from an isolated checkout and does not need uncommitted artifacts from the current working tree.

Other terminal commands coordinators often need:

```bash
orca terminal list [--worktree <selector>] [--json]
orca terminal create [--worktree <selector>] [--title <text>] [--command <cmd>] [--json]
orca terminal split --terminal <handle> [--direction horizontal|vertical] [--command <cmd>] [--json]
orca terminal wait --terminal <handle> --for tui-idle --timeout-ms <n> --json
orca terminal read --terminal <handle> --json
orca terminal send --terminal <handle> --text <text> --enter --json
```

If an older CLI rejects `worktree create --agent`, create the worktree normally, then run `orca terminal create --worktree <selector> --command "codex" --json` or `--command "claude"`.

Wait for `tui-idle` before dispatching. Always pass `--timeout-ms`; real coding tasks can take 15-60 minutes. During supervision, use rolling `check --wait` windows. If a window returns no matching message, inspect `task-list`, `terminal read`, or `terminal wait --for tui-idle` as a liveness checkpoint; if the terminal is still working or producing activity, keep waiting instead of retrying the task.


## Agent Guidance

- Workers with a valid live preamble must send `worker_done` exactly once from their own terminal, even on failure:
  `orca orchestration send --to <coordinator_handle> --type worker_done --subject "<short status>" --body "<3-sentence summary: what you did, what you found, what's left>" --payload '{"taskId":"<task_id>","dispatchId":"<dispatch_id>","filesModified":["path/a"],"reportPath":"<optional>"}' --json`
- After sending `worker_done`, end your turn and idle at the agent prompt. Do not poll or keep calling `orca orchestration check`; the coordinator re-engages you with a fresh preamble + TASK block delivered as new terminal input.
- For long tasks, send heartbeat/status only when the preamble asks for it, including both IDs:
  `orca orchestration send --to <coordinator_handle> --type heartbeat --subject "alive" --payload '{"taskId":"<task_id>","dispatchId":"<dispatch_id>","phase":"implementing"}' --json`
- If blocked before completion, use `ask`; use `escalation` only when ownership is valid and the coordinator must intervene.
- Treat preambles inherited through terminal history or full handoffs as stale unless the current prompt explicitly keeps that coordinator in the loop.
- Coordinators should use `task-list --ready` as external memory, dispatch parallel waves, and avoid dependency chains deeper than 3-4 steps.
- Prefer inter-worktree workers only for independent work that does not need current uncommitted state. When same-worktree work is required, create fresh terminals in that worktree and keep edit ownership clear.
