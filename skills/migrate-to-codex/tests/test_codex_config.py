from __future__ import annotations

import sys
import tomllib
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from migrate.codex_config import render_codex_config


class RenderCodexConfigTest(unittest.TestCase):
    def test_uses_canonical_hooks_feature_key(self) -> None:
        rendered = render_codex_config(
            model=None,
            permission_mode=None,
            enabled_mcp_servers=(),
            disabled_mcp_servers=frozenset(),
            mcp_servers=(),
            codex_hooks_enabled=True,
        )

        parsed = tomllib.loads(rendered)

        self.assertEqual(parsed["features"], {"hooks": True})


if __name__ == "__main__":
    unittest.main()
