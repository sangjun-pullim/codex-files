---
name: "writing-for-agents"
description: "Create or edit agent instructions, skills, and control-plane files with precise scope and conditional references."
---

# Writing instructions for agents

Write guidance that changes a relevant decision: user conventions, non-obvious system
facts, operational invariants, completion criteria, and real approval boundaries.

- Define the outcome and scope. Prefer decision criteria to a prescribed itinerary.
- Keep descriptions specific about when the skill applies. Remove synonym lists and generic
  encouragement that add no routing information.
- Put substantial conditional workflows in supporting files. Explain when to read each;
  a short self-contained skill does not need a router.
- Keep one maintained source for each rule. Brief context at a reference can explain why it
  matters; do not copy the referenced procedure.
- Include built-in runtime instructions in that source-of-truth check. Compare the effective
  instructions for the models, modes, and agents that use the file. Do not restate behavior
  already prescribed in every applicable case; a lapse is non-compliance, not a missing rule.
  Preserve user conventions, approval boundaries, and validation requirements that add a
  decision the runtime does not make. Do not exempt subagents automatically: check the base
  and role instructions they receive and whether they can encounter the situation. Include
  separately launched CLI workers and their selected models. If coverage is unverified,
  state the uncertainty rather than recommending deletion on that basis.
- When runtime coverage is confirmed for every applicable case and a lapse prompts a rule
  request, explain that coverage and recommend no additional rule. Respect an explicit user
  decision to keep one. Propose such a redundant rule yourself only when documented recurring
  outcomes required user correction or undo; name those incidents in the proposal and commit
  message, not in the maintained rule.
- Distinguish required checks, conventions, and suggestions. Use exact steps for fragile
  operations and permission boundaries, not for every ordinary coding task.
- Respect existing authorization. Ask again only if scope changes or an explicit gate remains;
  complete independent work while waiting.
- Define completion through observable behavior and required validation. Reuse valid check
  results and bound retries according to actual risk.
- Preserve data protection and ownership rules. Prompt edits do not grant tool permissions
  or authorize hook trust changes.

For Codex metadata and invocation policy, read [skill mechanics](SKILL-MECHANICS.md).
Use `second-brain` only when a project documentation workflow is part of the request.

## Review

Follow AGENTS.md's independent control-plane review requirement. Provide the diff so removals
and changed boundaries are visible. Check contradictions, unresolved terms, broken references,
and realistic requests that would stop early or exceed scope. Use behavioral examples when
they test a meaningful decision; avoid wording snapshot tests.
