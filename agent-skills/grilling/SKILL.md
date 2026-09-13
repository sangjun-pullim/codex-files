---
name: "grilling"
description: "Question and stress-test an idea when the user asks to clarify it before building. Excludes clear implementation requests."
---

Clarify the idea the user asked to explore. Map material decisions as a **design tree**;
omit routine choices that existing conventions or the user's stated preferences already resolve.

Work the tree in **rounds**. The **frontier** contains unresolved decisions that materially
affect the requested outcome and whose prerequisites are settled. Group related questions
into a manageable round and give your recommendation. Wait for answers before dependent
decisions, while continuing independent analysis.

Each question should be formatted like so:

```
❓ **Q1** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>
```

Each round the user answers reshapes the tree: settled decisions push the frontier outward and unblock questions that depended on them. Recompute the frontier and ask the next round. A question whose answer depends on another question still open in this round belongs to a _later_ round, not this one.

Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the environment (filesystem, tools, etc.), dispatch a sub-agent to find it; don't ask the user for anything you could look up yourself. Don't block on it: a running exploration is an unsettled prerequisite, so only the questions downstream of it wait for the sub-agent to report; ask the rest of the frontier now. The _decisions_ are the user's: put each to them and wait.

Challenge terms the moment they conflict with `docs/GLOSSARY.md` ("glossary는 X라고 정의하는데 지금 Y 의미로 쓰신 것 같아요 — 어느 쪽인가요?"), and sharpen vague or overloaded terms into a canonical one. Collect the domain terms and decisions that settle along the way (per the recording criteria in the `second-brain` skill), and once the frontier is empty propose the matching `docs/GLOSSARY.md` / `docs/ADR.md` updates in one batch — applied only with the user's approval. During the session this skill still only talks.

The interview is complete when material scope and design decisions are settled. Summarize
the decisions and any reasonable assumptions; do not enumerate hypothetical branches. A
discussion-only request ends here. If the user also authorized implementation, continue
once applicable approval boundaries are satisfied; reuse decisions already confirmed.

## Do NOT use when

- The request is already unambiguous — questioning a clear ask is friction, not rigor.
- A spec document is what's wanted (`impl-plan` writes one; this skill only talks).
- Reviewing code that already exists (`reviewer` agent / `/code-review`).
