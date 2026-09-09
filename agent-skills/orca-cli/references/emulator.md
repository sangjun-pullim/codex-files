Read the [skill entrypoint](../SKILL.md) for shared scope and constraints.

## Mobile Emulator (iOS Simulator via serve-sim)

The mobile emulator surface is workspace-scoped like browser tabs (active per worktree for unqualified; explicit --worktree/--device/--emulator for targeting). Always prefer `orca emulator ...` over raw `npx serve-sim` or simctl when inside Orca (the bridge owns lifecycle, scoping, and registration with the live pane).

`orca emulator --help` (and `orca emulator <subcommand> --help`) is the full command table — read it there rather than from memory.

Common:

```text
ORCA emulator list --json
ORCA emulator attach "iPhone 17 Pro" --json
ORCA emulator tap 0.5 0.7 --json
ORCA emulator type "hello" --json
ORCA emulator gesture '[{"type":"begin","x":0.5,"y":0.8},{"type":"move","x":0.5,"y":0.4},{"type":"end","x":0.5,"y":0.2}]' --json
ORCA emulator button home --json
ORCA emulator exec --command "tap 0.5 0.7" --json   # no "serve-sim" in the command string
ORCA emulator kill --json
```

Rules (mirror browser):

- Default: current worktree's active (pane open or attach sets it; unqualified "just works").
- Explicit: --device <udid|name> or --emulator <OrcaId from list> (bridge resolves names early to avoid serve-sim control bug).
- --worktree all only for list.
- Recoveries: 'emulator_no_active' → orca emulator attach or open pane; stale → list/kill/attach.
- No raw serve-sim in agent prompts/skills — use the `orca emulator` wrappers.

The live pane (when implemented) registers its stream with the bridge for default targeting (seamless, recommended option per design).


## Next Action (continued)

... or emulator list/attach/tap while the live view is visible.
