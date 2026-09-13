Read the [skill entrypoint](../SKILL.md) for shared scope and constraints.

## Worktrees

An Orca worktree is Orca's tracked view of a repo checkout, its metadata, terminals, browser tabs, and UI state.

Think of its id as a two-part address: `<repoId>::<worktreePath>`. For example, `repo-123::/Users/me/orca/fix-login` means “the `fix-login` checkout inside repo `repo-123`.” Always copy the complete `id` field from `orca worktree create --json` or `orca worktree list --json`; `repo-123` alone identifies only the repo.

Common commands:

```text
ORCA repo list --json
ORCA repo show --repo id:<repoId> --json
ORCA repo add --path /abs/repo --json
ORCA repo set-base-ref --repo id:<repoId> --ref origin/main --json
ORCA repo search-refs --repo id:<repoId> --query main --limit 10 --json
ORCA worktree list --repo id:<repoId> --json
ORCA worktree ps --json
ORCA worktree current --json
ORCA worktree show --worktree <selector> --json
ORCA worktree create --repo id:<repoId> --name related-task --json
ORCA worktree create --repo id:<repoId> --name related-task --parent-worktree active --json
ORCA worktree create --repo id:<repoId> --name folder-child --parent-worktree folder:<folderId> --json
ORCA worktree create --name child-task --agent codex --prompt "hi" --json
ORCA worktree create --name independent-task --no-parent --json
ORCA worktree set --worktree id:<repoId>::<worktreePath> --display-name "My Task" --json
ORCA worktree set --worktree active --comment "reproduced bug; testing fix" --json
ORCA worktree set --worktree active --workspace-status in-review --json
ORCA worktree rm --worktree id:<repoId>::<worktreePath> --json
ORCA worktree rm --worktree id:<repoId>::<worktreePath> --force --json
```

`--force` removes a worktree with uncommitted changes. Use it only on a worktree you know is
expendable — see [delegated execution](../../impl-execute/references/delegated-execution.md) step 6 for the cleanup rule, which forbids it.

Selectors:

- `id:<repoId>::<worktreePath>`, `name:<displayName>`, `path:<absolutePath>`, `branch:<branchName>`, `issue:<number>`
- The full id is the exact `<repo-id>::<path>` value returned by `orca worktree create --json` or `orca worktree list --json`; a bare repo id is not a worktree id.
- `active` / `current` for the enclosing Orca-managed worktree from the shell cwd
- For `worktree create --parent-worktree` only, folder/worktree parent context keys are also valid: `folder:<folderId>`, `worktree:<repoId>::<worktreePath>`, `id:folder:<folderId>`, `id:worktree:<repoId>::<worktreePath>`

Lineage rules:

- When creating from inside an Orca-managed worktree or folder context, Orca infers the current parent context when it can.
- Use `--parent-worktree active` when the child worktree relationship should be explicit.
- Use `--parent-worktree folder:<folderId>` or `--parent-worktree worktree:<repoId>::<worktreePath>` when a folder or worktree parent context should be explicit.
- Use `--no-parent` only when the new work is independent.
- `--no-parent` only controls Orca lineage; it does not choose the Git base. For independent top-level work, omit `--base-branch` so Orca uses the repo default base, or explicitly pass the repo default base. Never base it on the current feature branch unless the user asks for stacked work or "branch from current".
- If `--repo` is omitted, Orca infers the repo from the current Orca worktree when possible.

Agent/setup flags:

```text
ORCA worktree create --name task --agent codex --prompt "hi" --json
ORCA worktree create --name task --agent claude --setup run --json
ORCA worktree create --name task --setup skip --json
ORCA worktree create --name task --run-hooks --json
```

- `--agent <id>` launches that agent **in the first terminal** (Orca docs: *"`--agent` launches the selected agent in the first terminal"*); `--prompt <text>` sends initial work to it. Known ids include `claude`, `codex`, `omp`, `pi`, `grok`, and other installed TUI agents.
- **Prefer agent-first create for agent workers.** `orca worktree create --agent <id> --prompt "..."` puts the agent in the worktree's first terminal without adding a separate fallback shell for that worker. Repo setup or default-terminal settings may still add tabs or splits. Without configured default tabs, the bare-create fallback shell plus a later `terminal create --command <agent>` is an anti-pattern for ordinary agent worktrees — use `--agent` instead of “create worktree, then open agent.” Configured default tabs are intentional surfaces; never treat one as disposable without verifying that it is an unused shell.
- After create, use exactly one agent handle: `startupTerminal.handle` from the create response when present, or the matching result from `orca terminal list --worktree id:<repoId>::<newWorktreePath> --json` (or `name:<displayName>`) when the response omits it. If a handle later returns `terminal_handle_stale`, re-list it; never dual-send to old and replacement handles.
- `--setup run|skip|inherit` controls repo setup hooks. Default is `inherit`, which follows the repo's setup policy.
- `--run-hooks` is a legacy alias for `--setup run`; it also reveals/activates the new worktree.
- `--agent`, `--activate`, and `--run-hooks` reveal the new worktree. Plain create stays in the background.
- Let Orca choose setup terminal placement from repo settings, including tab vs split behavior. Do not manually create extra setup terminals when `--agent` already owns the first tab.
- If an older installed CLI rejects `--agent`, `--prompt`, or `--setup`, create the worktree normally, then run `orca terminal create --worktree <selector> --command "<requested-agent>"` and `orca terminal send` if a prompt is needed. This can leave a fallback shell when no default tabs are configured; close it only after confirming it is unused.
- `worktree create` creates a new checkout. For a fresh agent in the **current** checkout (no new worktree), use `orca terminal create --worktree active --command "codex" --json` — that path does not create a second worktree shell.


## Worktree Comments

A worktree comment is the short status text shown in Orca's workspace list/card for quick progress visibility.

Coding agents should update the active worktree comment at meaningful checkpoints:

```text
ORCA worktree set --worktree active --comment "fix implemented; running integration tests" --json
```

Update after meaningful state changes such as repro, fix, validation, handoff, or blocker. Keep comments short/current; failures are best-effort unless Orca state was requested.

Card status uses `--workspace-status <id>`; defaults are `todo`, `in-progress`, `in-review`, `completed`.
