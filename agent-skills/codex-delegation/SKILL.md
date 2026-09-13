---
name: "codex-delegation"
description: "Dispatch coding or code-investigation workers under AGENTS.md's Astra model routing, or an explicit Codex courier request."
---

# Codex delegation

Astra classifies the task, chooses the model and scope, supervises execution, and reviews
the result. Use AGENTS.md's model table; this skill does not independently choose models.

Choose the relevant workflow only:

- **Automatic Astra routing:** read [automatic dispatch](references/automatic-dispatch.md).
  Astra launches the selected interactive Codex CLI worker in an Orca split pane and reads
  its final response and relevant diff. This path supports implementation and read-only code
  investigation; it does not require an extra `codex-worker` courier agent.
- **Explicit `codex-worker` courier request:** read
  [courier workflow](references/courier-workflow.md). The courier launches Codex and reports
  facts; Astra retains all judgment. These courier-only restrictions do not apply to the
  automatic path above.

If a parent assigned you a bounded task, execute that task and return evidence. Do not apply
the supervisor's routing policy recursively. Simple conversational answers and initial
classification do not require this skill. Full ownership handoffs use `orca-cli` instead.

Existing scope, sandbox, hook-trust, merge, test, and independent-review boundaries still
apply. Neither automatic routing nor a worker launch authorizes external actions.
