#!/usr/bin/env python3
"""Adapt migrated Claude hooks and mirror them into Orca's active Codex home."""

from __future__ import annotations

import argparse
import json
import shlex
import stat
from pathlib import Path
from typing import Any


HookGroup = dict[str, Any]


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def save_json(path: Path, data: dict[str, Any]) -> None:
    rendered = f"{json.dumps(data, indent=2, ensure_ascii=False)}\n"
    if path.read_text(encoding="utf-8") == rendered:
        return
    temporary = path.with_name(f"{path.name}.sync-tmp")
    temporary.write_text(rendered, encoding="utf-8")
    temporary.chmod(stat.S_IMODE(path.stat().st_mode))
    temporary.replace(path)


def commands(group: HookGroup) -> list[str]:
    return [
        handler.get("command", "")
        for handler in group.get("hooks", [])
        if isinstance(handler, dict) and isinstance(handler.get("command", ""), str)
    ]


def adapt_user_hooks(data: dict[str, Any], hooks_dir: Path) -> None:
    event_groups = data.get("hooks", {})
    env_command = f"/bin/sh {shlex.quote(str(hooks_dir / 'block-env-read.sh'))}"

    for group in event_groups.get("PreToolUse", []):
        for handler in group.get("hooks", []):
            command = handler.get("command", "")
            if ".claude/hooks/block-env-read.sh" in command:
                group["matcher"] = "Bash"
                handler["command"] = env_command

    post_tool_use_groups: list[HookGroup] = []
    for group in event_groups.get("PostToolUse", []):
        group["hooks"] = [
            handler
            for handler in group.get("hooks", [])
            if ".claude/hooks/auto-format.sh" not in handler.get("command", "")
            and ".codex/hooks/auto-format.sh" not in handler.get("command", "")
        ]
        if group["hooks"]:
            post_tool_use_groups.append(group)
    event_groups["PostToolUse"] = post_tool_use_groups


def is_orca_managed(group: HookGroup) -> bool:
    return any("/.orca/agent-hooks/" in command and "claude-hook.sh" not in command for command in commands(group))


def fingerprint(group: HookGroup) -> str:
    return json.dumps(group, sort_keys=True, separators=(",", ":"))


def is_known_user_derived(group: HookGroup) -> bool:
    derived_markers = (
        "/.claude/hooks/block-env-read.sh",
        "~/.claude/hooks/block-env-read.sh",
        "/.claude/hooks/block-env-commit.sh",
        "~/.claude/hooks/block-env-commit.sh",
        "/.claude/hooks/auto-format.sh",
        "~/.claude/hooks/auto-format.sh",
        "/.codex/hooks/block-env-read.sh",
        "~/.codex/hooks/block-env-read.sh",
        "/.codex/hooks/auto-format.sh",
        "~/.codex/hooks/auto-format.sh",
        "/.orca/agent-hooks/claude-hook.sh",
    )
    return any(marker in command for command in commands(group) for marker in derived_markers)


def deduplicate(groups: list[HookGroup]) -> list[HookGroup]:
    result: list[HookGroup] = []
    seen: set[str] = set()
    for group in groups:
        group_fingerprint = fingerprint(group)
        if group_fingerprint not in seen:
            result.append(group)
            seen.add(group_fingerprint)
    return result


def merge_active_hooks(active: dict[str, Any], user: dict[str, Any]) -> None:
    active_events = active.setdefault("hooks", {})
    user_events = user.get("hooks", {})
    merged: dict[str, list[HookGroup]] = {}
    event_names = list(active_events)
    event_names.extend(event for event in user_events if event not in active_events)

    for event in event_names:
        user_fingerprints = {fingerprint(group) for group in user_events.get(event, [])}
        managed: list[HookGroup] = []
        for index, group in enumerate(active_events.get(event, [])):
            if is_orca_managed(group):
                managed.append(group)
            elif fingerprint(group) in user_fingerprints or is_known_user_derived(group):
                continue
            else:
                raise SystemExit(
                    f"Refusing to replace unknown active hook group: {event}[{index}]"
                )
        merged[event] = deduplicate([*managed, *user_events.get(event, [])])

    active["hooks"] = merged


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hooks-file", type=Path, required=True)
    parser.add_argument("--hooks-dir", type=Path, required=True)
    parser.add_argument("--active-file", type=Path)
    args = parser.parse_args()

    user_hooks = load_json(args.hooks_file)
    adapt_user_hooks(user_hooks, args.hooks_dir)
    save_json(args.hooks_file, user_hooks)

    if args.active_file:
        active_hooks = load_json(args.active_file)
        merge_active_hooks(active_hooks, user_hooks)
        save_json(args.active_file, active_hooks)


if __name__ == "__main__":
    main()
