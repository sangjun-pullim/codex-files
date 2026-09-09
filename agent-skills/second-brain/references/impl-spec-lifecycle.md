Read the [skill entrypoint](../SKILL.md) for shared scope and constraints.

## impl-spec Lifecycle

A spec's status decides whether it is editable. **Active specs are working documents; archived specs are frozen history.** Neither is ever synced against code drift — a spec claims what we planned, never "how the code is now" — but that is a reason not to *maintain* them as current-state docs, not a reason to preserve superseded instructions inside an active one.

- **Active (`status: active`, top level) — edit in place.** When the plan changes, rewrite the affected steps to say what you now intend. Do NOT append "update notes" alongside text you no longer mean. A spec carrying both the original and a correction is ambiguous to a machine, and it is read verbatim as an instruction set — it will sometimes get implemented as written. The original plan is not lost: these files are tracked, so `git log -p` is the record of what you planned at the time.
  - **Exception — steps already marked `[x]`.** A marker asserts "implemented as written here", so editing that step's instructions makes it lie and corrupts the resume logic. Either flip it back to `[ ]` so it gets redone, or leave it and add the change as a new step.
- **Archived (`status: done` / `superseded-by`, or under `archive/`) — never edit.** This is the record of what we decided and why, at the time. Frozen means frozen.

Durable why belongs in `ADR.md` (promote a genuine change of direction there when it meets the recording criteria above), current facts belong in `ARCHITECTURE.md` etc.

- **Born**: `/impl-plan` creates the spec with the frontmatter block defined in that skill's `## Output Format`, plus the snapshot NOTE — `impl-plan` owns the field list; never restate it elsewhere. The block is required for every file **created** under `docs/impl-spec/`, including specs written ad-hoc (incident response, manual planning) without the skill — a newly created spec without it is a defect, same as an unstamped derivable doc. A spec that predates a later-added field is not a defect.
- **Closed**: `/impl-execute` sets `status: done` and moves the file to `docs/impl-spec/archive/` on the conditions its Phase 3 step 1 defines — that skill owns them. A spec with unchecked steps stays `active` no matter how clean the review; it was never fully implemented.
- **Superseded**: a new spec replacing an old one marks the old file `status: superseded-by: <NNN>` and archives it.
- **Reference rule**: only top-level (active) specs participate in planning/implementation routing. `archive/` is for archaeology — intent, background, rejected alternatives — and stays valid for that purpose at any age. Never cite an archived spec as evidence of current code state.
