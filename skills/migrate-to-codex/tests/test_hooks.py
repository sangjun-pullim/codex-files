from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from migrate.hooks import ClaudeHooks


class ClaudeHooksTest(unittest.TestCase):
    def test_converts_current_codex_lifecycle_events(self) -> None:
        settings = {
            "hooks": {
                event_name: [
                    {
                        "matcher": "*",
                        "hooks": [{"type": "command", "command": "hook-command"}],
                    }
                ]
                for event_name in (
                    "PermissionRequest",
                    "SubagentStart",
                    "SubagentStop",
                )
            }
        }
        settings["hooks"]["StopFailure"] = [
            {"hooks": [{"type": "command", "command": "unsupported-command"}]}
        ]

        converted = ClaudeHooks.from_settings_mapping(
            Path(".claude/settings.json"), settings
        )
        rendered = json.loads(converted.render_codex_file())["hooks"]

        self.assertEqual(
            set(rendered),
            {"PermissionRequest", "SubagentStart", "SubagentStop"},
        )
        self.assertTrue(
            all(rendered[event_name][0]["matcher"] == "*" for event_name in rendered)
        )
        self.assertEqual(converted.unsupported_fields, ("hooks.StopFailure",))

    def test_reports_current_hook_feature_and_tool_coverage(self) -> None:
        converted = ClaudeHooks.from_settings_mapping(
            Path(".claude/settings.json"),
            {
                "hooks": {
                    "PreToolUse": [
                        {
                            "matcher": "Write|Edit",
                            "hooks": [
                                {"type": "command", "command": "hook-command"}
                            ],
                        }
                    ]
                }
            },
        )

        detail = converted.report_detail()

        self.assertIn("`[features].hooks`", detail)
        self.assertIn("enabled by default", detail)
        self.assertIn("`apply_patch`", detail)
        self.assertNotIn("`[features].codex_hooks`", detail)
        self.assertNotIn("shell commands only", detail)


if __name__ == "__main__":
    unittest.main()
