---
name: "source-command-check"
description: "Run a quick development check when the user requests check or lint, types, and tests."
---

# Quick development check

Read the project's scripts and run the applicable lint, type, and test checks using its
existing package manager and runner. Reuse passing results covering unchanged inputs.
Fix failures caused by the requested change and rerun affected checks; report unrelated
baseline failures without expanding scope. Limit formatting or lint fixes to the task's files.
Report passed, failed, and unavailable checks. Use `verify` for a PR/push workflow's checks.
