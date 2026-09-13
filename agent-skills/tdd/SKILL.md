---
name: "tdd"
description: "Develop test-first or add integration tests when the user requests that workflow."
---

# Test-Driven Development

TDD is the red → green loop. Consult the relevant guidance at the start and revisit a
section only when a new decision needs it; do not reread the skill on every cycle.

Consult relevant `docs/GLOSSARY.md` entries when domain terminology is unclear, and related
`docs/ADR.md` decisions when they affect the change. Reuse context already established.

## What a good test is

Tests verify behavior through public interfaces, not implementation details. Code can change entirely; tests shouldn't. A good test reads like a specification — "should confirm checkout with a valid cart" tells you exactly what capability exists — and survives refactors because it doesn't care about internal structure.

See [tests.md](tests.md) for examples and [mocking.md](mocking.md) for mocking guidelines.

## Seams — where tests go

A **seam** is the public boundary you test at: the interface where you observe behavior without reaching inside. Tests live at seams, never against internals.

**Choose seams within the authorized scope.** Use an approved plan or the existing public
interface to select the boundaries under test, state the choice, and proceed. Reuse prior
seam decisions. Ask when the choice materially changes the public interface or task scope,
or when the user explicitly requested approval before selecting seams. This decision controls
where tests go, never whether required tests are written; see the global `AGENTS.md` approval and review boundaries.

When the shape of that interface is itself in question — how deep the module is, where the seam belongs, what the interface should expose — read and follow `~/.agents/skills/codebase-design/SKILL.md` for the vocabulary. It is the shared source of the module, interface, depth, seam, adapter, leverage and locality terms, and it is a reference to consult, not a session to run.

## Anti-patterns

- **Implementation-coupled** — mocks internal collaborators, tests private methods, or verifies through a side channel (querying the database instead of using the interface). The tell: the test breaks when you refactor but behavior hasn't changed.
- **Tautological** — the assertion recomputes the expected value the way the code does (`expect(add(a, b)).toBe(a + b)`, a snapshot derived by hand the same way, a constant asserted equal to itself), so it passes by construction and can never disagree with the code. Expected values must come from an independent source of truth — a known-good literal, a worked example, the spec.
- **Horizontal slicing** — writing all tests first, then all implementation. Bulk tests verify _imagined_ behavior: you test the _shape_ of things rather than user-facing behavior, the tests go insensitive to real changes, and you commit to test structure before understanding the implementation. Work in **vertical slices** instead — one test → one implementation → repeat, each test a **tracer bullet** that responds to what the last cycle taught you.

## Rules of the loop

- **Red before green.** Write the failing test first, then only enough code to pass it. Don't anticipate future tests or add speculative features.
- **One slice at a time.** One seam, one test, one minimal implementation per cycle.
- **Refactoring is not part of the loop.** It belongs to the review stage (the `reviewer` agent / `/code-review`), not the red → green implementation cycle.
