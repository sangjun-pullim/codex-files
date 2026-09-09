---
name: "orchestration"
description: "Coordinate agents through Orca tasks and lifecycle messages when supervised Orca coordination is explicitly requested."
---

# Orca supervised coordination

Use Orca task/dispatch state for explicitly requested supervised coordination. Generic
agent handoffs do not authorize creating a tracked run. Load references for the current
role; ordinary Orca terminal control belongs to `orca-cli`.

## Tool Boundary

Before orchestration, confirm this is supervised Orca work and verify runtime prerequisites. Read [scope.md](references/scope.md).

## Ownership

Before lifecycle messages or dispatch, establish live ownership and task/dispatch provenance. Read [ownership.md](references/ownership.md).

## Messaging

For coordinator dispatch, messages, gates, and completion waits. Read ownership.md first. Read [coordination.md](references/coordination.md).

## Full Handoffs

For full ownership transfer, use this untracked handoff workflow. Read [handoffs.md](references/handoffs.md).

## Worker Terminals

For coordinated workers and completion reporting. Read ownership.md first; use coordination.md for ask/reply command syntax. Read [workers.md](references/workers.md).

## Example

For a command example when needed by the selected workflow. Read [examples.md](references/examples.md).
