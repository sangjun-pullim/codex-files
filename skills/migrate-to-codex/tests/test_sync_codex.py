from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SYNC_HOOKS_PATH = ROOT / "bin" / "sync-codex-hooks.py"
AUTO_FORMAT_PATH = ROOT / "hooks" / "auto-format.sh"

spec = importlib.util.spec_from_file_location("sync_codex_hooks", SYNC_HOOKS_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Unable to load {SYNC_HOOKS_PATH}")
sync_codex_hooks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync_codex_hooks)


class SyncCodexHooksTest(unittest.TestCase):
    def test_rewrites_claude_auto_format_for_codex(self) -> None:
        data = {
            "hooks": {
                "PostToolUse": [
                    {
                        "matcher": "Write|Edit",
                        "hooks": [
                            {
                                "type": "command",
                                "command": "bash ~/.claude/hooks/auto-format.sh",
                            }
                        ],
                    }
                ]
            }
        }

        sync_codex_hooks.adapt_user_hooks(data, ROOT / "hooks")
        sync_codex_hooks.adapt_user_hooks(data, ROOT / "hooks")

        group = data["hooks"]["PostToolUse"][0]
        self.assertEqual(group["matcher"], "Write|Edit")
        self.assertIn(
            str(AUTO_FORMAT_PATH),
            group["hooks"][0]["command"],
        )

    def test_active_merge_uses_native_orca_hook_once(self) -> None:
        native_command = "/Users/pullim/.orca/agent-hooks/codex-hook.sh"
        claude_command = "/Users/pullim/.orca/agent-hooks/claude-hook.sh"
        active = {
            "hooks": {
                "PermissionRequest": [
                    {"hooks": [{"type": "command", "command": native_command}]}
                ]
            }
        }
        user = {
            "hooks": {
                "PermissionRequest": [
                    {"hooks": [{"type": "command", "command": claude_command}]},
                    {"hooks": [{"type": "command", "command": "user-policy"}]},
                ]
            }
        }

        sync_codex_hooks.merge_active_hooks(active, user)
        first_merge = json.dumps(active, sort_keys=True)
        sync_codex_hooks.merge_active_hooks(active, user)

        commands = [
            handler["command"]
            for group in active["hooks"]["PermissionRequest"]
            for handler in group["hooks"]
        ]
        self.assertEqual(commands, [native_command, "user-policy"])
        self.assertEqual(json.dumps(active, sort_keys=True), first_merge)

    def test_active_merge_keeps_claude_shim_without_native_codex_hook(self) -> None:
        other_managed_command = "/Users/pullim/.orca/agent-hooks/other-hook.sh"
        claude_command = "/Users/pullim/.orca/agent-hooks/claude-hook.sh"
        active = {
            "hooks": {
                "PermissionRequest": [
                    {
                        "hooks": [
                            {"type": "command", "command": other_managed_command}
                        ]
                    }
                ]
            }
        }
        user = {
            "hooks": {
                "PermissionRequest": [
                    {"hooks": [{"type": "command", "command": claude_command}]}
                ]
            }
        }

        sync_codex_hooks.merge_active_hooks(active, user)

        commands = [
            handler["command"]
            for group in active["hooks"]["PermissionRequest"]
            for handler in group["hooks"]
        ]
        self.assertEqual(commands, [other_managed_command, claude_command])


class AutoFormatHookTest(unittest.TestCase):
    def run_hook(self, root: Path, patch: str) -> subprocess.CompletedProcess[str]:
        fake_bin = root / "fake-bin"
        fake_bin.mkdir(exist_ok=True)
        fake_npx = fake_bin / "npx"
        fake_npx.write_text(
            "#!/bin/sh\n"
            'printf \'%s\\n\' "$*" >> "$FAKE_NPX_LOG"\n'
            'case "$*" in\n'
            '  *"--find-config-path"*) [ -f "$PWD/.prettierrc" ] || exit 1; printf \'%s\\n\' "$PWD/.prettierrc" ;;\n'
            "esac\n"
        )
        fake_npx.chmod(0o755)
        log_path = root / "npx.log"
        environment = os.environ.copy()
        environment["PATH"] = f"{fake_bin}{os.pathsep}{environment['PATH']}"
        environment["FAKE_NPX_LOG"] = str(log_path)

        result = subprocess.run(
            ["/bin/bash", str(AUTO_FORMAT_PATH)],
            cwd=root,
            input=json.dumps(
                {
                    "tool_name": "apply_patch",
                    "tool_input": {"command": patch},
                }
            ),
            text=True,
            capture_output=True,
            env=environment,
            check=False,
        )
        result.log_path = log_path  # type: ignore[attr-defined]
        return result

    def test_formats_add_update_move_and_space_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / ".prettierrc").write_text("{}\n")
            (root / "src").mkdir()
            for relative_path in (
                "src/existing.ts",
                "src/new file.ts",
                "src/moved.ts",
                "--config=unexpected.ts",
            ):
                (root / relative_path).write_text("const value=1\n")
            patch = """*** Begin Patch
*** Update File: src/existing.ts
*** Add File: src/new file.ts
*** Update File: src/old.ts
*** Move to: src/moved.ts
*** Add File: --config=unexpected.ts
*** End Patch
"""

            result = self.run_hook(root, patch)
            log = result.log_path.read_text()  # type: ignore[attr-defined]

        self.assertEqual(result.returncode, 0, result.stderr)
        for relative_path in ("src/existing.ts", "src/new file.ts", "src/moved.ts"):
            self.assertIn(f"prettier --write ./{relative_path}", log)
        self.assertIn("prettier --write ./--config=unexpected.ts", log)
        self.assertNotIn("prettier --write ./src/old.ts", log)

    def test_skips_when_config_or_patch_target_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "src").mkdir()
            (root / "src/no-config.ts").write_text("const value=1\n")

            result = self.run_hook(
                root,
                "*** Begin Patch\n*** Update File: src/no-config.ts\n*** End Patch\n",
            )
            first_log = result.log_path.read_text()  # type: ignore[attr-defined]
            result.log_path.unlink()  # type: ignore[attr-defined]
            no_target_result = self.run_hook(
                root,
                "*** Begin Patch\n*** Delete File: src/no-config.ts\n*** End Patch\n",
            )
            no_target_log_exists = no_target_result.log_path.exists()  # type: ignore[attr-defined]

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--find-config-path ./src/no-config.ts", first_log)
        self.assertNotIn("prettier --write", first_log)
        self.assertEqual(no_target_result.returncode, 0, no_target_result.stderr)
        self.assertFalse(no_target_log_exists)


if __name__ == "__main__":
    unittest.main()
