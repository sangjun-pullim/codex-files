from __future__ import annotations

import importlib.util
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SYNC_HOOKS_PATH = ROOT / "bin" / "sync-codex-hooks.py"
SYNC_FROM_CLAUDE_PATH = ROOT / "bin" / "sync-from-claude"
SKILL_POLICY_MERGER_PATH = ROOT / "bin" / "merge-skill-policy.py"
AUTO_FORMAT_PATH = ROOT / "hooks" / "auto-format.sh"

spec = importlib.util.spec_from_file_location("sync_codex_hooks", SYNC_HOOKS_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Unable to load {SYNC_HOOKS_PATH}")
sync_codex_hooks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync_codex_hooks)


class SyncFromClaudeTest(unittest.TestCase):
    def test_should_refuse_legacy_sync_without_touching_configuration(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            claude = root / ".claude"
            codex = root / ".codex"
            claude.mkdir()
            codex.mkdir()
            (claude / "CLAUDE.md").write_text("Claude source\n")
            (codex / "AGENTS.md").write_text("Independent Codex instructions\n")
            environment = dict(os.environ, CLAUDE_CONFIG_DIR=str(claude),
                               CODEX_CONFIG_DIR=str(codex), ORCA_CODEX_HOME="")
            before = {str(p): p.read_bytes() for p in root.rglob("*") if p.is_file()}
            for flags in ([], ["--skills"], ["--replace"], ["--skills", "--replace"]):
                with self.subTest(flags=flags):
                    result = subprocess.run([str(SYNC_FROM_CLAUDE_PATH), *flags],
                                            env=environment, text=True, capture_output=True)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("disabled", result.stderr)
                    after = {str(p): p.read_bytes() for p in root.rglob("*") if p.is_file()}
                    self.assertEqual(after, before)

    def test_should_preserve_local_guard_behavior(self) -> None:
        cases = {
            "block-env-commit.sh": [("git add .env", 2), ("git add .env.example", 0)],
            "block-dangerous-git.sh": [("git reset --hard", 2), ("git status --short", 0)],
        }
        for name, commands in cases.items():
            for command, expected in commands:
                with self.subTest(hook=name, command=command):
                    result = subprocess.run(["/bin/bash", str(ROOT / "hooks" / name)],
                        input=json.dumps({"tool_name": "Bash", "tool_input": {"command": command}}),
                        text=True, capture_output=True)
                    self.assertEqual(result.returncode, expected, result.stderr)


class SkillPolicyMergerTest(unittest.TestCase):
    def run_merger(
        self,
        policy_file: Path,
        allowed_root: Path,
        state: str,
        *,
        check: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        command = [
            sys.executable,
            str(SKILL_POLICY_MERGER_PATH),
            "--existing",
            str(policy_file),
            "--target",
            str(policy_file),
            "--state",
            state,
            "--allowed-root",
            str(allowed_root),
        ]
        if check:
            command.append("--check")
        return subprocess.run(
            command,
            text=True,
            capture_output=True,
            check=False,
        )

    def read_source_state(self, source_skill: Path) -> str:
        result = subprocess.run(
            [
                sys.executable,
                str(SKILL_POLICY_MERGER_PATH),
                "--source-skill",
                str(source_skill),
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def test_preserves_unmanaged_false_across_source_transition(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            allowed_root = Path(temporary_directory) / "skills"
            policy_file = allowed_root / "example" / "agents" / "openai.yaml"
            policy_file.parent.mkdir(parents=True)
            original = "policy:\n  allow_implicit_invocation: false\n"
            policy_file.write_text(original)

            denied = self.run_merger(policy_file, allowed_root, "deny")
            allowed = self.run_merger(policy_file, allowed_root, "allow")

            self.assertEqual(denied.returncode, 0, denied.stderr)
            self.assertEqual(allowed.returncode, 0, allowed.stderr)
            self.assertEqual(policy_file.read_text(), original)

    def test_restores_unmanaged_true_across_source_transition(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            allowed_root = Path(temporary_directory) / "skills"
            policy_file = allowed_root / "example" / "agents" / "openai.yaml"
            policy_file.parent.mkdir(parents=True)
            policy_file.write_text(
                "interface:\n  display_name: Example\npolicy:\n"
                "  allow_implicit_invocation: true\n"
            )

            denied = self.run_merger(policy_file, allowed_root, "deny")
            denied_text = policy_file.read_text()
            allowed = self.run_merger(policy_file, allowed_root, "allow")

            self.assertEqual(denied.returncode, 0, denied.stderr)
            self.assertIn("allow_implicit_invocation: false", denied_text)
            self.assertIn("original=true", denied_text)
            self.assertEqual(allowed.returncode, 0, allowed.stderr)
            self.assertIn("allow_implicit_invocation: true", policy_file.read_text())
            self.assertNotIn("managed by sync-from-claude", policy_file.read_text())

    def test_rejects_skill_and_agents_symlink_escapes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            allowed_root = root / "skills"
            external_root = root / "external"
            allowed_root.mkdir()
            external_root.mkdir()

            skill_link = allowed_root / "skill-link"
            skill_link.symlink_to(external_root, target_is_directory=True)
            skill_policy = skill_link / "agents" / "openai.yaml"
            skill_result = self.run_merger(
                skill_policy, allowed_root, "deny", check=True
            )

            real_skill = allowed_root / "real-skill"
            real_skill.mkdir()
            agents_link = real_skill / "agents"
            agents_link.symlink_to(external_root, target_is_directory=True)
            agents_policy = agents_link / "openai.yaml"
            agents_result = self.run_merger(
                agents_policy, allowed_root, "deny", check=True
            )

            self.assertNotEqual(skill_result.returncode, 0)
            self.assertIn("resolves outside", skill_result.stderr)
            self.assertNotEqual(agents_result.returncode, 0)
            self.assertIn("resolves outside", agents_result.stderr)
            self.assertEqual(list(external_root.iterdir()), [])

    def test_ignores_fixed_temporary_symlink_collision(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            allowed_root = root / "skills"
            policy_file = allowed_root / "example" / "agents" / "openai.yaml"
            policy_file.parent.mkdir(parents=True)
            policy_file.write_text("interface:\n  display_name: Example\n")
            external_file = root / "external.yaml"
            external_file.write_text("do not change\n")
            old_temporary = policy_file.with_name(f"{policy_file.name}.sync-tmp")
            old_temporary.symlink_to(external_file)

            result = self.run_merger(policy_file, allowed_root, "deny")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(external_file.read_text(), "do not change\n")
            self.assertTrue(old_temporary.is_symlink())
            self.assertIn("allow_implicit_invocation: false", policy_file.read_text())
            self.assertEqual(
                sorted(path.name for path in policy_file.parent.iterdir()),
                ["openai.yaml", "openai.yaml.sync-tmp"],
            )

    def test_reads_only_boolean_frontmatter_policy(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            commented_true = root / "commented-true.md"
            commented_true.write_text(
                "---\nname: example\ndescription: Example.\n"
                "disable-model-invocation: true # explicit only\n---\n"
                "disable-model-invocation: false\n"
            )
            body_decoy = root / "body-decoy.md"
            body_decoy.write_text(
                "---\nname: example\ndescription: Example.\n---\n"
                "```yaml\ndisable-model-invocation: true\n```\n"
            )
            block_scalar_decoy = root / "block-scalar-decoy.md"
            block_scalar_decoy.write_text(
                "---\nname: example\ndescription: |\n"
                "  disable-model-invocation: false\n"
                "  ---\n"
                "disable-model-invocation: true # explicit only\n---\n"
            )

            self.assertEqual(self.read_source_state(commented_true), "deny true")
            self.assertEqual(self.read_source_state(body_decoy), "allow false")
            self.assertEqual(self.read_source_state(block_scalar_decoy), "deny true")


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


class WorkerReworkInputTest(unittest.TestCase):
    def test_should_pass_initial_prompt_as_literal_stdin(self) -> None:
        worker = tomllib.loads((ROOT / "agents/codex-worker.toml").read_text())
        initial = worker["developer_instructions"].split("## Rework requests", 1)[0]
        commands = re.findall(r"`([^`\n]*codex exec -s[^`\n]*)`", initial)
        self.assertEqual(len(commands), 2)
        for command in commands:
            with self.subTest(command=command), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                payload = "don't expand $(touch injected-dollar) or `touch injected-tick`\n한글\n"
                (root / "prompt.md").write_text(payload)
                rendered = command.replace("<worktree>", directory).replace("<repo-root>", directory)
                rendered = rendered.replace("<scratch>", directory).replace("<PROMPT>", payload)
                mock = (
                    'codex() { while [ "$#" -gt 1 ]; do shift; done; '
                    'if [ "$1" = "-" ]; then cat; else printf "%s" "$1"; fi; }; '
                    'orca() { while [ "$1" != "--command" ]; do shift; done; shift; eval "$1"; }; '
                )
                result = subprocess.run(["/bin/sh", "-c", mock + rendered], cwd=root,
                    text=True, capture_output=True, check=False)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual((root / "out.txt").read_text(), payload)
                self.assertFalse((root / "injected-dollar").exists())
                self.assertFalse((root / "injected-tick").exists())

    def test_should_pass_rework_corrections_as_literal_stdin(self) -> None:
        worker = tomllib.loads((ROOT / "agents/codex-worker.toml").read_text())
        rework = worker["developer_instructions"].split("## Rework requests", 1)[1]
        commands = re.findall(r"`([^`\n]*codex exec resume[^`\n]*)`", rework)
        commands = [command for command in commands if "tee " in command]
        self.assertEqual(len(commands), 2)
        for command in commands:
            with self.subTest(command=command), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                logs = root / "rework-N"
                logs.mkdir()
                payload = "don't expand $(touch injected-dollar) or `touch injected-tick`\n한글\n"
                (logs / "corrections.txt").write_text(payload)
                self.assertNotIn("<corrections>", command)
                rendered = command.replace("<worktree>", directory).replace("<repo-root>", directory)
                rendered = rendered.replace("<scratch>", directory).replace("<session-id>", "test-session")
                # Mock external CLIs while exercising both shell layers.
                mock = (
                    'codex() { test "$6" = "-" || return 91; cat; }; '
                    'orca() { while [ "$1" != "--command" ]; do shift; done; shift; eval "$1"; }; '
                )
                result = subprocess.run(
                    ["/bin/sh", "-c", mock + rendered], cwd=root,
                    text=True, capture_output=True, check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual((logs / "out.txt").read_text(), payload)
                self.assertFalse((root / "injected-dollar").exists())
                self.assertFalse((root / "injected-tick").exists())


if __name__ == "__main__":
    unittest.main()
