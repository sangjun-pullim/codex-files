---
name: "verify"
description: "Verify a change before a PR or push using project-required checks and review."
---

# Verify a change

Use the repository's required checks and existing tools. Establish the task diff including
staged, unstaged, new, and already committed work belonging to this task.

- Inspect project scripts and run the applicable required build, type, lint, and test checks.
  Docs/config-only work may use syntax, schema, link, or focused behavioral validation.
- Reuse passing results while their code, configuration, and inputs remain unchanged. If the
  build covers the required type check, do not repeat it without a specific reason.
- Fix failures caused by this change and rerun affected checks. Report unrelated baseline
  failures without expanding scope. Required failures still prevent reporting READY.
- Use existing coverage thresholds. Collect coverage when required or useful for a relevant
  gap; without a configured threshold, coverage is informational.
- Inspect the full task diff for unintended edits, secrets, unsafe input handling, and changed
  public behavior. An empty changed-file list must not turn a scan into a whole-tree audit.
- Apply AGENTS.md's risk-surface tests and independent reviewer requirements. Self-review
  does not replace a required reviewer. Use `security-checklist` for a full audit only when
  requested or required and within that skill's backend scope.

Report checks, reused evidence, review results, and blockers. Report READY only when required
checks and reviews pass. Verification does not itself authorize push, merge, deployment, or
unrelated fixes; continue the user's authorized workflow after it.
