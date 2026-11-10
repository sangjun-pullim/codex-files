# Architecture Report Format

Use one report with the structure below. For Markdown output, cards become sections and
diagrams use Mermaid fences. For HTML or another available visual output, use its supported
layout and drawing features. No external design skill is required. Choose a diagram only
when it explains the candidate more clearly than short text.

## Structure

- **Header** — repo name, date, and a compact legend: solid box = module, dashed line = seam, red arrow = leakage, thick dark box = deep module. No introduction paragraph — straight into the candidates.
- **Candidates** — one card per candidate (anatomy below).
- **Top recommendation** — one larger card: candidate name, one sentence on why, anchor link to its card. That's it.

## Candidate card

The diagrams carry the weight. Prose is sparse, plain, and uses the glossary terms without ceremony.

- **Title** — short, names the deepening (e.g. "Collapse the settlement intake pipeline").
- **Badge row** — recommendation strength (`Strong` / `Worth exploring` / `Speculative`), plus a tag for the dependency category (`in-process`, `local-substitutable`, `ports & adapters`, `mock` — see codebase-design's DEEPENING.md).
- **Files** — monospaced list.
- **Before / After diagram** — the centrepiece. Two columns, side by side. See patterns below.
- **Problem** — one sentence. What hurts.
- **Solution** — one sentence. What changes.
- **Wins** — bullets, ≤6 words each. e.g. "Tests hit one interface", "Pricing logic stops leaking", "Delete 4 shallow wrappers".
- **Decision callout** (if applicable) — one line in a warning-tinted box when the candidate contradicts `docs/ADR.md`.

No paragraphs of explanation. If the diagram needs a paragraph to be understood, redraw the diagram.

## Diagram patterns

Pick the pattern that fits the candidate. Mix them. Don't make every diagram look the same — variety is part of the point.

- **Mermaid graph** (the workhorse for dependencies / call flow) — use a `flowchart` when the point is "X calls Y calls Z, and look at the mess." Style with `classDef` to colour leakage edges red and the deep module dark. Sequence diagrams work well for "before: 6 round-trips; after: 1."
- **Hand-built boxes-and-arrows** (when Mermaid's layout fights you) — modules as divs with borders and labels, arrows as inline SVG. Reach for this when the "after" diagram should feel like one thick-bordered deep module with greyed-out internals — Mermaid won't render that with the right weight.
- **Cross-section** (good for layered shallowness) — stack horizontal bands to show layers a call passes through. Before: 6 thin layers each doing nothing. After: 1 thick band labelled with the consolidated responsibility.
- **Mass diagram** (good for "interface as wide as implementation") — two rectangles per module: interface surface vs implementation. Shallow: nearly equal heights. Deep: short interface, tall implementation.
- **Call-graph collapse** — before: a tree of calls as nested boxes. After: the same tree collapsed into one box, the now-internal calls faded inside it.

Keep diagrams compact. Place before/after side by side when the output format supports it;
otherwise stack them. Label modules with their actual names.

## Tone

Use concise prose and the project's existing identifiers and domain terminology. Apply
`codebase-design` definitions when discussing its design concepts.

**Phrasings that fit the style:**

- "Settlement intake module is shallow — interface nearly matches the implementation."
- "Pricing leaks across the seam."
- "Deepen: one interface, one place to test."
- "Two adapters justify the seam: HTTP in prod, in-memory in tests."

**Wins bullets** name the gain in codebase-design vocabulary: _"locality: bugs concentrate in one module"_, _"leverage: one interface, N call sites"_, _"interface shrinks; implementation absorbs the wrappers"_. Don't write _"easier to maintain"_ or _"cleaner code"_ — those terms aren't in that vocabulary and don't earn their place.

No hedging, no throat-clearing, no "it's worth noting that…". If a sentence could be a bullet, make it a bullet. If a bullet could be cut, cut it. If a term isn't in the codebase-design vocabulary, reach for one that is before inventing a new one.
