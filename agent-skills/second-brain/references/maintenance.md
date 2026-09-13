Read the [skill entrypoint](../SKILL.md) for shared scope and constraints.

## Documentation Maintenance

- After completing a task that changes architecture, DB schema, API, or business logic, **suggest** updating the relevant `docs/` file
- A review-only request leaves docs unchanged. When documentation edits or synchronization
  are already requested or approved, apply the in-scope changes without asking again.
  Propose additional documentation work outside that scope; AGENTS.md review boundaries apply.
- When suggesting, be specific: state which file and what section needs updating
- Keep docs concise — bullet points and diagrams over prose
- `BUG-FIXES.md` is append-only until promotion: when the same root-cause pattern appears 2+ times, promote it to a durable guard via `/docs-sync` Part 5 (that command owns the target list). Promoted entries are compressed to a one-line reference — promotion doubles as compaction.


## Coexistence with Existing Files

- Standard files coexist with project-specific docs (e.g., `docs/deployment.md`, `docs/troubleshooting.md`)
- Never delete or rename existing documentation files (exception: moving closed impl-specs into `docs/impl-spec/archive/` per the lifecycle above)
- If an existing file covers the same topic as a standard file (e.g., `docs/architecture-proposal.md`), note it and let the user decide whether to merge
