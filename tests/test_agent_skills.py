from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


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


if __name__ == "__main__":
    unittest.main()
