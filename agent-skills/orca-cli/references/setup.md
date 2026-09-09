Read the [skill entrypoint](../SKILL.md) for shared scope and constraints.

## Start Here

Choose the executable once for the current session:

- If the `ORCA_CLI_COMMAND` environment variable is set, use its value. Orca exports this
  for managed WSL sessions.
- Otherwise, in a dev checkout whose session exposes `ORCA_DEV_REPO_ROOT`, use `orca-dev`.
- Otherwise, on Linux outside an Orca-managed terminal, use `orca-ide`. Never use bare
  `orca` there because it normally resolves to the GNOME screen reader.
- Otherwise, use `orca`.

In every command block, `ORCA` is a documentation placeholder. Replace it with the chosen
executable before running the command; do not create a shell variable or run `ORCA`
literally. This substitution works the same way in POSIX shells, PowerShell, and cmd.exe.

```text
ORCA status --json
ORCA worktree ps --json
ORCA terminal list --json
```

Keep using that same executable for every later command so dev sessions do not reach a
production CLI and Linux never falls through to the GNOME screen reader.

If Orca is not running, start it:

```text
ORCA open --json
ORCA status --json
```

Prefer `--json` for agent-driven calls. If the CLI is missing, say so explicitly instead of inspecting source files first.
