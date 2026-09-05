from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from migrate.skills import convert_skill_file


class SkillSupportArtifactsTest(unittest.TestCase):
    def test_copies_root_markdown_support_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            skill_root = Path(temporary_directory) / "example"
            skill_root.mkdir()
            skill_file = skill_root / "SKILL.md"
            skill_file.write_text(
                "---\nname: example\ndescription: Example skill.\n---\n\nRead GUIDE.md.\n"
            )
            (skill_root / "reference.md").write_text("# Reference\n")
            (skill_root / "GUIDE.md").write_text("# Guide\n")

            artifacts, _ = convert_skill_file(skill_file)

        artifact_paths = [artifact.relative_path for artifact in artifacts]
        self.assertEqual(
            artifact_paths.count(Path(".agents/skills/example/SKILL.md")),
            1,
        )
        self.assertIn(Path(".agents/skills/example/reference.md"), artifact_paths)
        self.assertIn(Path(".agents/skills/example/GUIDE.md"), artifact_paths)


if __name__ == "__main__":
    unittest.main()
