from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from migrate.instructions import MAX_AGENTS_MD_BYTES, validate_agents_md_files
from utils.util import parse_yaml_mapping


class ParseYamlMappingTest(unittest.TestCase):
    def test_parses_folded_block_scalar_as_one_value(self) -> None:
        frontmatter = """name: orchestration
description: >-
  Use Orca orchestration for structured coordination: threaded messages,
  task dispatch, and decision gates.
"""

        parsed = parse_yaml_mapping(frontmatter)

        self.assertEqual(
            parsed,
            {
                "name": "orchestration",
                "description": (
                    "Use Orca orchestration for structured coordination: "
                    "threaded messages, task dispatch, and decision gates."
                ),
            },
        )


class ValidateAgentsMdTest(unittest.TestCase):
    def test_validates_only_the_generated_root_instruction_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            target_root = Path(temporary_directory)
            (target_root / "AGENTS.md").write_text("# Root\n")
            nested = target_root / "unrelated-project"
            nested.mkdir()
            (nested / "AGENTS.md").write_text("x" * (MAX_AGENTS_MD_BYTES + 1))

            report_items = validate_agents_md_files(target_root)

        self.assertEqual([item.path for item in report_items], [Path("AGENTS.md")])


if __name__ == "__main__":
    unittest.main()
