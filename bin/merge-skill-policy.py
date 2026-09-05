#!/usr/bin/env python3
"""Merge the Claude invocation policy into a Codex skill metadata file."""

from __future__ import annotations

import argparse
import os
import re
import stat
import tempfile
from pathlib import Path


MANAGED_MARKER = "# managed by sync-from-claude"
ORIGINAL_STATE = re.compile(r"\boriginal=(absent|true|false)\b")
POLICY_HEADER = re.compile(r"^policy:\s*(?:#.*)?$")
INLINE_POLICY = re.compile(r"^policy:\s*\S")
IMPLICIT_KEY = re.compile(
    r"^(\s+)allow_implicit_invocation\s*:\s*(true|false)\s*(?:#.*)?$",
    re.IGNORECASE,
)
SOURCE_POLICY_KEY = re.compile(
    r"^disable-model-invocation\s*:\s*(true|false)\s*(?:#.*)?$",
    re.IGNORECASE,
)
SOURCE_POLICY_PREFIX = re.compile(r"^disable-model-invocation\s*:")


def source_policy_state(source_skill: Path) -> tuple[str, bool]:
    lines = source_skill.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return "allow", False

    for line in lines[1:]:
        if line == "---":
            break
        if not line or line[0].isspace():
            continue
        match = SOURCE_POLICY_KEY.fullmatch(line)
        if match:
            return ("deny" if match.group(1).lower() == "true" else "allow"), True
        if SOURCE_POLICY_PREFIX.match(line):
            return "preserve", True
    return "allow", False


def policy_block(
    lines: list[str], *, reject_inline: bool = True
) -> tuple[int, int] | None:
    for index, line in enumerate(lines):
        content = line.rstrip("\r\n")
        if POLICY_HEADER.fullmatch(content):
            end = index + 1
            while end < len(lines):
                candidate = lines[end]
                if candidate.strip() and not candidate[0].isspace() and not candidate.lstrip().startswith("#"):
                    break
                end += 1
            return index, end
        if reject_inline and INLINE_POLICY.match(content):
            raise SystemExit("Refusing to rewrite inline policy YAML; use a block mapping")
    return None


def line_ending(text: str) -> str:
    return "\r\n" if "\r\n" in text else "\n"


def deny_implicit(text: str) -> str:
    newline = line_ending(text)
    lines = text.splitlines(keepends=True)
    block = policy_block(lines)

    def managed_value(original: str) -> str:
        return (
            "allow_implicit_invocation: false  "
            f"{MANAGED_MARKER}; original={original}{newline}"
        )

    if block is None:
        if lines and not lines[-1].endswith(("\n", "\r")):
            lines[-1] = f"{lines[-1]}{newline}"
        if lines and lines[-1].strip():
            lines.append(newline)
        lines.extend([f"policy:{newline}", f"  {managed_value('absent')}"])
        return "".join(lines)

    start, end = block
    for index in range(start + 1, end):
        match = IMPLICIT_KEY.match(lines[index].rstrip("\r\n"))
        if match:
            current_value = match.group(2).lower()
            if MANAGED_MARKER not in lines[index] and current_value == "false":
                return text
            original = ORIGINAL_STATE.search(lines[index])
            if original:
                original_value = original.group(1)
            elif MANAGED_MARKER in lines[index]:
                original_value = "absent"
            else:
                original_value = current_value
            lines[index] = f"{match.group(1)}{managed_value(original_value)}"
            return "".join(lines)

    indentation = "  "
    for line in lines[start + 1 : end]:
        match = re.match(r"^(\s+)\S", line)
        if match:
            indentation = match.group(1)
            break
    lines.insert(start + 1, f"{indentation}{managed_value('absent')}")
    return "".join(lines)


def allow_implicit(text: str) -> str:
    lines = text.splitlines(keepends=True)
    block = policy_block(lines, reject_inline=False)
    if block is None:
        return text

    start, end = block
    changed = False
    retained_body: list[str] = []
    for line in lines[start + 1 : end]:
        match = IMPLICIT_KEY.match(line.rstrip("\r\n"))
        if match and MANAGED_MARKER in line:
            changed = True
            original = ORIGINAL_STATE.search(line)
            original_value = original.group(1) if original else "absent"
            if original_value != "absent":
                newline = "\r\n" if line.endswith("\r\n") else "\n"
                retained_body.append(
                    f"{match.group(1)}allow_implicit_invocation: "
                    f"{original_value}{newline}"
                )
            continue
        retained_body.append(line)
    if not changed:
        return text

    meaningful = [
        line
        for line in retained_body
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if meaningful:
        lines[start + 1 : end] = retained_body
    elif any(line.lstrip().startswith("#") for line in retained_body):
        newline = line_ending(text)
        lines[start] = f"policy: {{}}{newline}"
        lines[start + 1 : end] = retained_body
    else:
        del lines[start:end]
    return "".join(lines)


def validate_target(target: Path, allowed_root: Path) -> None:
    lexical_root = allowed_root.absolute()
    lexical_target = target.absolute()
    try:
        lexical_target.relative_to(lexical_root)
    except ValueError as error:
        raise SystemExit(f"Policy target is outside the allowed root: {target}") from error

    resolved_root = allowed_root.resolve()
    paths = [target.parent.resolve(strict=False)]
    if target.exists() or target.is_symlink():
        paths.append(target.resolve(strict=False))
    for resolved_path in paths:
        try:
            resolved_path.relative_to(resolved_root)
        except ValueError as error:
            raise SystemExit(
                f"Policy target resolves outside the allowed root: {target}"
            ) from error


def write_target(
    target: Path, text: str, mode: int | None, allowed_root: Path
) -> None:
    if not text.strip():
        if target.exists():
            target.unlink()
        try:
            target.parent.rmdir()
        except OSError:
            pass
        return

    target.parent.mkdir(parents=True, exist_ok=True)
    validate_target(target, allowed_root)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{target.name}.sync-", dir=target.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as temporary_file:
            temporary_file.write(text)
        if mode is not None:
            temporary.chmod(mode)
        validate_target(target, allowed_root)
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-skill", type=Path)
    parser.add_argument("--existing", type=Path)
    parser.add_argument("--target", type=Path)
    parser.add_argument("--state", choices=("deny", "allow", "preserve"))
    parser.add_argument("--allowed-root", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if args.source_skill is not None:
        state, field_present = source_policy_state(args.source_skill)
        print(f"{state} {'true' if field_present else 'false'}")
        return

    if None in (args.existing, args.target, args.state, args.allowed_root):
        parser.error("--existing, --target, --state, and --allowed-root are required")

    validate_target(args.target, args.allowed_root)

    base = args.existing if args.existing.is_file() else args.target
    if not base.is_file():
        if args.state == "deny":
            text = deny_implicit("")
            if not args.check:
                write_target(args.target, text, None, args.allowed_root)
        return

    text = base.read_text(encoding="utf-8")
    mode = stat.S_IMODE(base.stat().st_mode)
    if args.state == "deny":
        text = deny_implicit(text)
    elif args.state == "allow":
        text = allow_implicit(text)
    if not args.check:
        write_target(args.target, text, mode, args.allowed_root)


if __name__ == "__main__":
    main()
