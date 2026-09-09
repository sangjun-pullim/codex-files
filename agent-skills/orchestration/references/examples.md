Read the [skill entrypoint](../SKILL.md) for shared scope and constraints.

## Example

```bash
orca terminal create --worktree active --title login-css-worker --command "claude" --json
orca terminal wait --terminal <handle> --for tui-idle --timeout-ms 60000 --json
orca orchestration task-create --spec "Fix the login button CSS" --json
orca orchestration dispatch --task <task_id> --to <handle> --inject --json
orca orchestration check --wait --types worker_done,escalation,decision_gate --timeout-ms 900000 --json
```


## Next Action

Coordinator: confirm `orca status --json`, inspect `task-list`/`dispatch-show` if inheriting state, then choose either a manual loop (`task-create` -> worker -> `dispatch --inject` -> `check --wait`) or `orchestration run`.

Worker: if the current prompt contains a live dispatch preamble, do the task, use `ask` for blocking questions, and send `worker_done` once with the required payload. If the preamble is stale or absent, do not send lifecycle messages; inspect state or treat the prompt as an ordinary handoff.
