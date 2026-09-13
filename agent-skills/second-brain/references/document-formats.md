Read the [skill entrypoint](../SKILL.md) for shared scope and constraints.

## Standard docs/ Files

Every project should maintain these documentation files under `docs/`:

The **Layer** column decides stamping: derivable-layer docs carry a freshness stamp, hand-written ones never do.

| File | Layer | Purpose | When Required |
|------|-------|---------|---------------|
| `PRD.md` | hand-written | Product requirements — what we're building, what we're not, and why (see PRD section below) | Product documentation requested or approved |
| `ARCHITECTURE.md` | derivable | High-level map — module boundaries, integration points, data flow (not an exhaustive structure listing) | Always |
| `DB-SCHEMA.md` | derivable | Modeling rationale, constraints, migration notes (the schema itself lives in `schema.prisma`) | Prisma/DB projects |
| `API-SPEC.md` | derivable | External API contract — the contract is the truth, not the code | APIs with external consumers (internal-only: route code is the doc) |
| `FRONTEND-ARCHITECTURE.md` | derivable | Component tree, state management, routing | React/Next.js projects |
| `BUSINESS-LOGIC.md` | hand-written | Domain rules, workflows, edge cases — intended behavior, the baseline for judging bugs | Complex business logic |
| `ADR.md` | hand-written | ADR (Architecture Decision Records) | Always |
| `BUG-FIXES.md` | hand-written | Notable bug investigations and fixes | Always |
| `GLOSSARY.md` | hand-written | Domain term ↔ canonical code identifier mapping, with banned aliases | Only when a term has confused the model or a teammate at least once |

**Naming**: standard doc files are UPPERCASE — the README/CONTRIBUTING convention marking
project meta-docs, and the one deliberate exception to the global `AGENTS.md` file naming rule.
Legacy lowercase names (`decisions.md`, `glossary.md`, …) are the same docs: read them
wherever the uppercase name is named; `/docs-sync` proposes migrating them.


## PRD.md — What We're Building

`docs/PRD.md` is a single file holding product requirements — the *what and why* layer every other doc hangs from. One file, because a PRD states current intent as a coherent whole; numbered per-feature files are the shape of event records (that is `impl-spec/`), not of intent. Sections:

- `## Problem / Users`
- `## Goal`
- `## Scope` — one subsection per product surface, each stating what the surface does; a substantial feature is added here as a subsection, never as a new file.
- `## Non-goals` — what the product deliberately does not do, each with its reason, one line. This is the section that pays for the document: a rejected direction is findable here. When the rejection meets `ADR.md`'s recording criteria, the line links that ADR entry instead of restating its reasoning.
- `## Success criteria`

Rules:

- **When useful**: consult relevant PRD scope and non-goals when product intent is unclear.
  Create or update it when product documentation is requested or included in the approved
  scope. File count and PRD absence do not block planning; record settled intent in the spec
  when no PRD exists. Material product decisions and AGENTS.md approval boundaries still apply.
- **Size**: keep it under ~200 lines. Past that, the PRD is absorbing spec content — move the overflow into the active impl-spec's Context; if none exists or the relevant spec is archived, the overflow is product-level and belongs in `ARCHITECTURE.md` / `ADR.md` — never into an archived spec, never into a second PRD file.
- Hand-written layer, no stamp. Update when product direction changes — a PRD states current intent, not history (history lives in git).
- Ask only unresolved product decisions that materially affect the document. Use `grilling`
  when the user requests an idea interview; write from the settled intent.
- **Boundary vs impl-spec**: the PRD owns the product-level what/why and success criteria ("무엇이 되면 성공"); `docs/impl-spec/` owns the code-level how and verification commands ("어떤 테스트로 확인"). A spec references its PRD by section (`PRD.md §Scope/<surface>`) — never restates it.
- Downstream docs (`ARCHITECTURE.md`, `ADR.md`, …) update as decisions land, consistent with the PRD.


## GLOSSARY.md Format

One line per term, table-only. The 금지 표현 (banned aliases) column is the highest-value
part — negative constraints stop naming drift across sessions and subagents better than
definitions do.

```markdown
| 용어 | Canonical identifier | 정의 (1줄) | 금지 표현 |
|------|---------------------|-----------|----------|
| 정산 | `settlement` | 월말 판매대금 정산 프로세스 | adjustment, payout |
```

- A definition that outgrows one line (behavior rules, state transitions) belongs in
  `BUSINESS-LOGIC.md`; the glossary row keeps only a link. Never let the two files
  describe the same rule independently.
- Hand-written layer: no freshness stamp, effectively append-only.
- Creation criterion: a term has confused the model or a teammate at least once.
  Projects with obvious vocabulary skip this file.


## ADR.md — When to Record

Record a decision only when all three hold; if any is missing, skip it:

1. **Hard to reverse** — changing your mind later costs something real.
2. **Surprising without context** — a future reader would look at the code and wonder "why did they do it this way?"
3. **A real trade-off** — genuine alternatives existed and one was picked for specific reasons.

What qualifies: architectural shape; integration patterns between modules; technology choices that carry lock-in (not every library — the ones that would take a quarter to swap); boundary and scope decisions (the explicit no-s are as valuable as the yes-s); deliberate deviations from the obvious path (these stop the next engineer from "fixing" something deliberate); constraints not visible in the code; rejected alternatives when the rejection is non-obvious.

An entry can be a single paragraph — context, decision, why. The value is recording *that* a decision was made and *why*, not filling out sections.
