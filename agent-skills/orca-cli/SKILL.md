---
name: "orca-cli"
description: "Operate Orca worktrees, terminals, browser, and runtime state when Orca is requested or AGENTS.md routes an agent handoff here."
---

# Orca CLI

Use `orca` when Orca's running editor/runtime is the source of truth. Inside Orca-managed terminals, `orca` always resolves to the Orca CLI on every platform. In any other shell on Linux, use `orca-ide` wherever this file says `orca` — outside Orca's terminals, bare `orca` on Linux is usually the GNOME Orca screen reader (`/usr/bin/orca`), and running it starts speech on the user's machine.

**Dev builds (`pnpm dev`):** after `pnpm build:cli`, the dev CLI is exposed as `orca-dev` (the global shim points at this checkout's wrapper + out/cli). Inside a dev Orca's terminals use `orca-dev emulator ...` (or `./config/scripts/orca-dev.mjs emulator ...` for worktree-local invocation that does not depend on the /usr/local/bin symlink). Plain `orca` targets any installed production Orca. The app's own agent preambles use `orca-dev` automatically in dev mode.

Use plain shell tools when Orca state does not matter.

## Start Here

Before the first Orca command, select the correct executable and confirm the runtime. Reuse that choice for the session. Read [setup.md](references/setup.md).

## Full Handoffs

For full ownership transfer without supervision. Read [handoffs.md](references/handoffs.md).

## Supervised Dispatch

For supervised non-Codex workers. Also read worktrees.md and terminals.md for handles and targeting; Codex CLI workers use codex-delegation. Read [supervised-dispatch.md](references/supervised-dispatch.md).

## Worktrees

For worktrees and their comments. Read [worktrees.md](references/worktrees.md).

## Terminals

For terminal creation, input, output, or waiting. Read [terminals.md](references/terminals.md).

## Automations

For Orca automation state. Read [automations.md](references/automations.md).

## Built-In Browser

For the browser embedded inside Orca. Read [browser.md](references/browser.md).

## Mobile Emulator (iOS Simulator via serve-sim)

For Orca mobile emulator operations. Read [emulator.md](references/emulator.md).

## Next Action

Confirm `orca status --json` unless already checked this turn, then choose the narrowest command for the job: `worktree ps/current/create`, `terminal list/read/wait/send`, `automations list`, or built-in browser `snapshot`.
