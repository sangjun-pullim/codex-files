Read the [skill entrypoint](../SKILL.md) for shared scope and constraints.

## Two-Layer Rule & Freshness Stamps

Docs split into two layers by maintenance cost:

- **Hand-written layer** — why, invariants, rejected alternatives, business rules: things code cannot express. Maintained by hand; rarely invalidated.
- **Derivable layer** — facts reproducible from code (schema, endpoints, field/column mappings, indexes). NEVER hand-maintain these. Either generate them from code, or attach a freshness stamp so staleness is machine-checkable.
- **Keep the derivable layer thin.** Agentic code search regenerates structure cheaply; a derivable doc earns its place by curation (high-level map, integration points, modeling rationale), not enumeration. A section that merely restates what code or schema already shows is a deletion candidate — a stale doc grounds the model in the wrong direction, which is worse than no doc.

Stamp convention (frontmatter at the top of the doc):

```yaml
---
verified-against: a1b2c3d   # commit hash the doc was last verified against
sources: prisma/**, src/payment/**
---
```

- `git diff --name-only <hash>..HEAD -- <globs>` empty → doc is fresh; no judgment needed.
- Non-empty → potentially stale; the diff IS the sync-check scope.
- `/docs-sync` uses stamps for incremental checking and bumps them after a confirmed sync.
- When reading a stamped doc for derivable facts, trust it only if the stamp check passes; otherwise verify against code.
- Harness protocol files under `~/.codex/docs/**` are hand-written-layer by definition — they describe procedure, not code — so they take no stamp either.
- A derivable-layer doc without a stamp is a defect, not an option: include the stamp when creating one (`/init-docs` scaffolds it), and when substantially updating an unstamped one, verify its facts against code and add the stamp in the same change.
