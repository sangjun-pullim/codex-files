from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from migrate.skills import convert_skill_file


class SkillSupportArtifactsTest(unittest.TestCase):
    def test_copies_root_reference_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            skill_root = Path(temporary_directory) / "example"
            skill_root.mkdir()
            skill_file = skill_root / "SKILL.md"
            skill_file.write_text(
                "---\nname: example\ndescription: Example skill.\n---\n\nRead reference.md.\n"
            )
            (skill_root / "reference.md").write_text("# Reference\n")

            artifacts, _ = convert_skill_file(skill_file)

        self.assertIn(
            Path(".agents/skills/example/reference.md"),
            [artifact.relative_path for artifact in artifacts],
        )


if __name__ == "__main__":
    unittest.main()
