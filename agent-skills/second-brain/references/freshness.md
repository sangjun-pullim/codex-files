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

- Validate that the stamp names an available commit and `sources` covers the documented facts.
  Missing/invalid commits or incomplete source coverage require a full comparison.
- Compare the current document with `git show <hash>:<repo-relative-doc-path>`.
  Ignore only the frontmatter's `verified-against` field; compare all other metadata
  (including `sources`) and body content. Compare staged document content too when it
  differs from the working tree. A missing snapshot, changed content, or unavailable
  comparison requires a full comparison; unchanged sources alone cannot validate an edited doc.
- For valid stamps, collect the union of changed paths from these commands, passing each
  source glob as a separate quoted Git pathspec:
  - `git diff --no-renames --name-only <hash> HEAD -- <globs>` (committed changes)
  - `git diff --cached --no-renames --name-only HEAD -- <globs>` (staged changes)
  - `git diff --no-renames --name-only -- <globs>` (unstaged changes)
  - `git ls-files --others --exclude-standard -- <globs>` (untracked sources)
  `--no-renames` includes both old and new paths. Use `-z` and NUL-aware processing when
  collecting paths programmatically.
- Only unchanged document content and successful source checks with an empty union permit
  **OK (stamp-verified)** for code-derived facts. Errors are
  not empty results. A non-empty union requires comparison against the affected current
  sources and relevant dependent facts; inspect staged content too when it differs from
  the working tree. Deletions and renames must be reflected in the documentation.
- Update the stamp only when the verified source state is represented by that commit.
  Relevant staged, unstaged, or untracked changes prevent a HEAD stamp; report the dirty
  source state instead. Changes outside the document's source scope do not prevent stamping.
- `/docs-sync` uses stamps for incremental checking and bumps them after a confirmed sync.
- When reading a stamped doc for derivable facts, trust it only if the stamp check passes; otherwise verify against code.
- Stamps do not establish intended rules or approve contracts; use the
  [evidence rules](document-formats.md#evidence-for-intent-and-current-behavior) for those claims.
- Harness protocol files under `~/.codex/docs/**` are hand-written-layer by definition — they describe procedure, not code — so they take no stamp either.
- A derivable-layer doc without a stamp is a defect, not an option: include the stamp when creating one (`/init-docs` scaffolds it), and when substantially updating an unstamped one, verify its facts against code and add the stamp in the same change.
