# Context for project changes

Read documentation when it can change a decision about the task. A local typo, formatting
edit, or straightforward fix does not require a documentation index or ADR tour.

- Expected behavior or domain terms unclear: consult the relevant BUSINESS-LOGIC.md,
  GLOSSARY.md, or PRD.md section.
- Structural or interface decisions: consult related ADR.md and ARCHITECTURE.md sections.
- DB/API/frontend work: consult the corresponding contract when that contract is affected.
- Difficult bugs: inspect related BUG-FIXES.md entries when prior incidents could explain them.

These are context pointers, not an ordered reading checklist. Search code first when it is
the shortest route to the answer. Use code and execution evidence for current behavior;
use impl-specs for intent. Treat stale documentation as a discrepancy to report, not as
evidence that overrides current code. Missing documents do not block independent work.

For creating or restructuring docs, use the `second-brain` skill. Preserve relevant project
decisions and canonical domain terms. Legacy lowercase document names remain valid.
