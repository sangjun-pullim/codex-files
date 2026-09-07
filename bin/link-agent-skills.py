#!/usr/bin/env python3
"""Link Codex skill discovery to the versioned skill directory."""

from __future__ import annotations

import argparse
import hashlib
import os
import stat
import sys
import tempfile
from pathlib import Path


class SkillsLinkError(Exception):
    """An existing skills path cannot be safely replaced."""


def tree_snapshot(root: Path) -> dict[str, tuple[str, str, int]]:
    entries = {}
    for path in root.rglob("*"):
        mode = stat.S_IMODE(path.lstat().st_mode)
        if path.is_symlink():
            entry = ("link", os.readlink(path), mode)
        elif path.is_dir():
            entry = ("directory", "", mode)
        elif path.is_file():
            entry = ("file", hashlib.sha256(path.read_bytes()).hexdigest(), mode)
        else:
            raise SkillsLinkError(f"Unsupported file type: {path}")
        entries[str(path.relative_to(root))] = entry
    return entries


def link_skills(codex_root: Path, agents_root: Path) -> Path | None:
    source = (codex_root / "agent-skills").resolve()
    target = agents_root / "skills"
    if not source.is_dir():
        raise SkillsLinkError(f"Missing versioned skills directory: {source}")
    if target.is_symlink():
        if target.resolve() == source:
            return None
        raise SkillsLinkError(f"Refusing to replace a different symlink: {target}")
    backup = None
    if target.exists():
        if not target.is_dir() or tree_snapshot(target) != tree_snapshot(source):
            raise SkillsLinkError(
                f"Existing skills differ from {source}; reconcile them before linking."
            )
        backup_root = Path(tempfile.mkdtemp(prefix="skills-backup-", dir=agents_root))
        backup = backup_root / "skills"
        target.rename(backup)
    else:
        agents_root.mkdir(parents=True, exist_ok=True)
    try:
        target.symlink_to(source, target_is_directory=True)
    except OSError:
        if backup is not None:
            backup.rename(target)
        raise
    return backup


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex-root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--agents-root", type=Path, default=Path.home() / ".agents")
    args = parser.parse_args()
    try:
        backup = link_skills(args.codex_root, args.agents_root)
    except (SkillsLinkError, OSError) as exc:
        print(f"Cannot link skills: {exc}", file=sys.stderr)
        return 1
    print(f"Skills: {args.agents_root / 'skills'} -> {(args.codex_root / 'agent-skills').resolve()}")
    if backup is not None:
        print(f"Previous directory preserved at: {backup}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
