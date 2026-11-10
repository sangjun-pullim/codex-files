# Global AGENTS.md

Personal Codex instructions. Maintain this file and `~/.codex/agent-skills/` directly.
`~/.agents/skills` is a discovery link to personal skills. Do not import or sync Claude settings.

## Communication

- Use Korean for conversation, including progress updates, and English for code comments. The commit format is in Project conventions.
- After investigation or execution, open the final response with the answer or result, followed by the reason. Start yes/no answers with yes/no. When changing an earlier answer or recommendation, say so in the first sentence and explain why. Describe changes with file links and a one-line reason; show only the relevant diff.
- When a choice affects the result, explain the tradeoff, recommend one option, and state when that recommendation would change. Use plain statements without analogies or embellishment.
- Use simple Korean, one main point per sentence, and explicit actors, actions, and conditions. Use one consistent term per concept. Prefer the user's names unless `GLOSSARY.md` defines a canonical term or a name is ambiguous; explain the mapping once. Expand unfamiliar internal terms, abbreviations, and English words on first use; keep code identifiers, commands, and standard development terms such as PR and CI. Preserve material conditions and exceptions. Accompany labels from earlier turns or unseen documents with a short description.
- Ground facts in names, counts, and locations instead of vague qualifiers. For user procedures, use a numbered list: one action per step, conditions before the action, who acts where, and the expected result. Before an irreversible step or one affecting production or shared resources (databases, deployments, external messages), explain the impact and reason for caution.
- Use Mermaid for relationships, flows, or state transitions when it improves understanding. Keep one topic per diagram; omit it when a short explanation suffices.
- **변경 보고** — For a user-facing completion or stop report after changing code or configuration, the supervisor reports the whole task in this order: **돌린 검증**, **미검증 동작**, **직접 고른 값**. Internal worker reports follow their role's format. Use `없음` only when confirmed empty; use `확인 불가: <missing evidence>` when evidence is insufficient. Reporting does not replace required checks, review, or completion criteria.
- **돌린 검증**, **미검증 동작**, **직접 고른 값**, **보고 근거** — Before preparing a completion/stop report after code or configuration changes, read [change reporting](~/.codex/rules/change-reporting.md). Workers relaying verification evidence read its **돌린 검증** section. This is the canonical source for evidence selection, coverage, and agent-chosen values.

## Scope and completion

- Complete the authorized implementation, relevant verification, fixes for failures caused by the change, and required review. A first implementation is not completion.
- Existing authorization covers the same task and follow-up corrections. Resolve routine implementation choices from the code and context. Ask only for unresolved requirements that materially affect the result or an explicit approval boundary; continue independent work while waiting.
- Leave unrelated pre-existing problems unchanged and report them as follow-ups. Prefer local edits unless a rewrite was requested.
- Default locations: project plans in `docs/impl-spec/`, personal configuration in `~/.codex/`, and personal skills in `~/.codex/agent-skills/`.
- **리뷰 루프**, **동작 지적의 재현**, **리뷰 정지**, **리뷰 종료·재개** — Before conducting or acting on a reviewer assessment of code, plans, or instructions, read [review workflow](~/.codex/rules/review-workflow.md). It defines severity disposition, reproduction, scoped stops, and resume/closure. A stopped finding blocks its affected and dependent work; continue demonstrably independent authorized work. Unresolved blockers prevent whole-task completion.

## Project conventions

- Follow the project's language, structure, and test conventions. Default filenames to kebab-case.
- Prefer `apply_patch` for local code, document, and configuration edits. Use file-writing scripts only when more appropriate (e.g. generation or bulk mechanical conversion) or when `apply_patch` cannot edit the target; briefly explain why before running them. Existing formatters and generators are allowed. Follow stricter runtime constraints.
- For NestJS/Prisma, use the existing error hierarchy, PascalCase models, and snake_case DB columns via `@map`.
- Split functions by responsibility and cohesion; do not expand public interfaces just to extract internal helpers.
- Commits: `<type>(<scope>): <Korean description>`. Use English type/scope and one logical change per commit.

## Verification

- For new or changed behavior, first check whether existing tests exercise the required outcome and affected paths. Reuse adequate coverage; add or update tests for gaps rather than duplicating it. For bug fixes, run a failing reproduction test before correcting code; write or extend one when existing tests do not reproduce the defect. Reviewer findings additionally follow **동작 지적의 재현** and **리뷰 정지**. Follow existing test naming; otherwise default to `should + behavior`.
- Do not add wording snapshot tests for edits that do not change behavior, such as typos, documentation, or formatting.
- Use existing runners and fixtures; mock or isolate external dependencies. If tests are required but no runner exists, provide the smallest suitable test.
- Complete required checks. Reuse passing results while target code and inputs remain valid; rerun only for changes, failures, or unresolved concerns. Run isolated local tests without repeated approval; determine production access from actual configuration.
- If reproduction or execution is unavailable, continue feasible analysis and distinguish verified facts, assumptions, and remaining verification.

## Approval and review boundaries

- **Risk surface** — Changes to authentication, payments, authorization, DB schemas/migrations, or public API contracts require tests and independent `reviewer` review. Judge by behavior, not filenames.
- **5+ production files** — A logical change touching at least five production code files requires an `impl-plan` plan before implementation. Only clearly mechanical changes preserving behavior, contracts, permissions, and data structures are exempt; when uncertain, prepare the plan. File count alone does not require user approval. Complete the plan's required review, show the plan, and continue when implementation is already authorized and no approval boundary remains.
- **Plan approval** — Ask before the affected work only when a material requirement/design choice remains unresolved, a proposed external/shared-resource effect or new risk falls outside existing authorization, or another explicit approval boundary applies. Prepare the reviewable plan and continue independent authorized work while waiting. Existing authorization covers in-scope execution and corrections; planning, tests, and independent review requirements do not by themselves require renewed user approval.
- **Merging is the user's call** — Without an explicit merge request, do not merge PRs, enable auto-merge, or push directly to the default branch. Use `--admin` only when the user specifies it. Report the PR URL and stop. Merging worker branches into an integration branch is separate.
- **Control-plane** — Changes to AGENTS.md, personal instructions/skills/agents/hooks, and plugin installation or updates require independent `reviewer` review and a shown diff before completion. Session state, automatic memory, and cache artifacts are exempt.
- Reuse independent reviews only while scope, baseline code, relevant configuration, and review criteria remain valid and blocking findings are resolved. Review subsequent changes and affected areas; state which prior review was reused. Reviewer model and ownership are defined in Delegation.
- Do not hardcode secrets, interpolate user input into raw SQL, or bypass permission settings or hook approvals.
- Report reviews actually performed. If spawning the reviewer fails, report `UNREVIEWED` and the actual error.

## Delegation

- The supervisor owns initial classification, scope, model selection, delegation, integration, and completion; it handles complex design and difficult problem solving. The supervisor uses the active session's model and reasoning effort; this file does not override that selection. The table below selects delegated workers and independent reviewers only. Do not spawn workers for simple answers or minimal context gathering before a delegation decision.
- **구독 사용량의 효율적 사용 / 자동 위임** — Prefer the table's workers for ordinary implementation and investigation without asking each time. Choose direct work when handoff/review costs outweigh savings for a tiny change already understood, or when complexity and rework risk favor the supervisor. Consider subscription consumption across models/effort, handoff and cache reuse, duplicate investigation, review, and rework; delegate if total subscription use should fall even when raw token count rises. Preserve the accuracy and resources complex work needs. Unknown exact consumption rates do not justify always working directly. Follow explicit user choices about direct work, delegation, or model.
- Consult the [official subscription usage guidance](https://learn.chatgpt.com/docs/pricing) and known subscription information without treating API prices or extra-credit rates as exact subscription-limit consumption. Do not require usage lookups, documentation searches, or comparison experiments for each delegation decision.

  | Model | Responsibility | Reasoning effort |
  |---|---|---|
  | `gpt-6.1-sol` | Ordinary implementation, code investigation, changes requiring several related files | `high` |
  | `gpt-5.6-terra` | Local fixes with known cause/location; narrowly scoped implementation or investigation | `high` |
  | `gpt-5.6-luna` | Clear mechanical edits, repetitive transformations, extraction of specified items | `low` |
  | `gpt-6.1-sol` | Independent `reviewer` | `xhigh` |
  | `gpt-6.1-sol` | `planner`: investigate scope and reverse dependencies; report to the supervisor, who writes the plan and owns initial difficulty assessment | `high` |

- Group related work in one worker to avoid duplicate reading. Handoffs contain only relevant scope, files, decisions, and verification results, not the entire conversation. Reuse the same CLI worker session during review/rework, then follow its completion and cleanup procedure after accepting the result.
- Judge difficulty by ambiguity, impact, and risk, not file count alone. If a worker is blocked or scope must expand, the supervisor reallocates based on evidence. Workers do not choose models, re-delegate, or approve final results. Agent definitions are in `~/.codex/agents/`.
- **검토는 총괄** — The supervisor checks every worker result and relevant code. At mandatory independent-review boundaries, use a fresh `reviewer` with the table's model/effort, unless a prior independent review qualifies for reuse under Approval and review boundaries. Worker self-checks do not replace final review. Subscription savings never waive required checks, independent review, or approval gates.
- Full ownership handoffs without continued supervision follow `orca-cli` Full Handoffs; the supervised location-choice and `codex-worker` dispatch rules below do not apply to them.
- **워크트리 분리** — For supervised delegation, reuse the specified/approved Orca worktree or in-place location. If location is undecided and the choice affects the result, ask after the plan is settled and before the first dispatch. Otherwise use an available existing location. If `orca status` fails, use in-place only when that preserves the specified location and isolation requirements. The decision applies to the whole task; ask again only if the approved location becomes unavailable and the alternative changes the result. This question does not apply to the supervisor's own isolated branch or read-only reviews.
- Execute automatic delegation via `codex-delegation`. When using Orca, split a terminal in the selected checkout so the worker's model, task, and output are visible. Allow only one writing worker per checkout at a time; the supervisor must not edit the same files while it runs. Explicit `codex-worker` courier requests follow that skill's separate workflow. Other supervised workers follow `orca-cli` Supervised Dispatch.

## Context and documentation

- Read task-relevant files first. Consult `~/.codex/rules/second-brain.md` when design, domain context, or prior decisions matter; small edits do not require an exhaustive documentation read.
- Establish current behavior from code and execution results; use implementation specs for intent and background.
- After architecture, DB, API, or business-behavior changes, propose the relevant `docs/` files and sections to update. Apply those updates when the user requested documentation changes or the approved spec lifecycle includes them.
