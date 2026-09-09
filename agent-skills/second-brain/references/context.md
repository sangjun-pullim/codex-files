Read the [skill entrypoint](../SKILL.md) for shared scope and constraints.

## Lazy Loading Principle

**AGENTS.md should be lightweight.** It serves as an index, not an encyclopedia.

- AGENTS.md contains: project overview, quick-start commands, key conventions, and `## Documentation` section with references to `docs/`
- Detailed architecture, schemas, API specs live in `docs/` files
- Read `docs/` files only when the current task requires that context
- This keeps the context window lean and loads knowledge on-demand

Example `## Documentation` section in AGENTS.md:

```markdown
## Documentation

Detailed docs live in `docs/`. Read as needed:
- `docs/ARCHITECTURE.md` — System architecture and module relationships (sources: src/**)
- `docs/DB-SCHEMA.md` — Database schema and relations (sources: prisma/**)
- `docs/API-SPEC.md` — API endpoints and contracts (sources: src/**/*.controller.ts)
```

The `(sources: <glob>)` annotation makes update routing a lookup, not a judgment:
when a change touches a doc's sources glob, that doc is an update candidate.
