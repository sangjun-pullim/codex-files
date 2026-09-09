from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


class AgentSkillsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.codex = self.root / ".codex"
        self.agents = self.root / ".agents"
        self.source = self.codex / "agent-skills"
        self.source.mkdir(parents=True)
        self.agents.mkdir()
        (self.source / "example.md").write_text("Codex-specific guidance\n")

    def link(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(ROOT / "bin/link-agent-skills.py"),
             "--codex-root", str(self.codex), "--agents-root", str(self.agents)],
            capture_output=True, text=True, check=False,
        )

    def test_should_link_skills_and_allow_repeated_setup(self) -> None:
        for _ in range(2):
            result = self.link()
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.agents / "skills").resolve(), self.source)

    def test_should_preserve_existing_identical_skills_in_a_backup(self) -> None:
        existing = self.agents / "skills"
        existing.mkdir()
        (existing / "example.md").write_text("Codex-specific guidance\n")
        result = self.link()
        self.assertEqual(result.returncode, 0, result.stderr)
        backups = list(self.agents.glob("skills-backup-*/skills/example.md"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), "Codex-specific guidance\n")
        self.assertEqual(existing.resolve(), self.source)

    def test_should_refuse_to_replace_different_skills(self) -> None:
        existing = self.agents / "skills"
        existing.mkdir()
        (existing / "example.md").write_text("Keep my local edits\n")
        result = self.link()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(existing.is_symlink())
        self.assertEqual((existing / "example.md").read_text(), "Keep my local edits\n")

    def test_should_refuse_to_replace_an_unrelated_symlink(self) -> None:
        other = self.root / "other"
        other.mkdir()
        (self.agents / "skills").symlink_to(other, target_is_directory=True)
        self.assertNotEqual(self.link().returncode, 0)
        self.assertEqual((self.agents / "skills").resolve(), other)

    def prepare_sync(self) -> tuple[dict[str, str], Path]:
        claude = self.root / ".claude"
        skill = claude / "skills/example"
        skill.mkdir(parents=True)
        (claude / "CLAUDE.md").write_text("# Global CLAUDE.md\n")
        (skill / "SKILL.md").write_text(
            "---\nname: example\ndescription: Example skill\n---\nClaude guidance\n"
        )
        package = self.codex / "skills/migrate-to-codex"
        package.parent.mkdir()
        package.symlink_to(ROOT / "skills/migrate-to-codex", target_is_directory=True)
        target = self.source / "example/SKILL.md"
        target.parent.mkdir()
        target.write_text("Codex-specific guidance\n")
        (self.agents / "skills").symlink_to(self.source, target_is_directory=True)
        environment = dict(os.environ, CLAUDE_CONFIG_DIR=str(claude),
                           CODEX_CONFIG_DIR=str(self.codex), PYTHON3_BIN=sys.executable,
                           ORCA_CODEX_HOME="")
        return environment, target

    def test_should_preserve_codex_skills_without_explicit_import(self) -> None:
        environment, target = self.prepare_sync()
        claude = Path(environment["CLAUDE_CONFIG_DIR"])
        (claude / "commands").mkdir()
        (claude / "commands/example.md").write_text("Claude command\n")
        command = self.source / "source-command-example/SKILL.md"
        command.parent.mkdir()
        command.write_text("Keep $ARGUMENTS unchanged\n")
        policy = target.parent / "agents/openai.yaml"
        policy.parent.mkdir()
        policy.write_text("policy:\n  allow_implicit_invocation: false\n")
        before = {p.relative_to(self.source): p.read_bytes()
                  for p in self.source.rglob("*") if p.is_file()}
        for flags in ([], ["--replace"]):
            result = subprocess.run([str(ROOT / "bin/sync-from-claude"), *flags],
                                    env=environment, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(target.read_text(), "Codex-specific guidance\n")
            self.assertTrue((self.agents / "skills").is_symlink())
            after = {p.relative_to(self.source): p.read_bytes()
                     for p in self.source.rglob("*") if p.is_file()}
            self.assertEqual(after, before)

    def test_should_preserve_codex_skills_when_legacy_import_is_requested(self) -> None:
        environment, target = self.prepare_sync()
        result = subprocess.run([str(ROOT / "bin/sync-from-claude"), "--skills"],
                                env=environment, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual("Codex-specific guidance\n", target.read_text())
        self.assertTrue((self.agents / "skills").is_symlink())


if __name__ == "__main__":
    unittest.main()
