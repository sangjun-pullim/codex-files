---
name: "source-command-commit"
description: "Create a Conventional Commit when the user asks to commit changes."
---

# source-command-commit

Use this skill when the user asks to run the migrated source command `commit`.

## Command Template

1. Check `git diff --staged` (if empty, check `git diff`)
2. Establish independent review of the commit's diff. Reuse valid reviewer evidence under
   AGENTS.md's review-reuse rule; review later changes and affected context. When a review
   is needed, provide the patch path and changed-file list to a `reviewer`. Only prose/doc
   changes touching no control-plane file are exempt from independent review.
3. Analyze the changes
4. Generate a Conventional Commits message
   - When the subject alone cannot explain the reason or impact, add a concise Korean body
     after a blank line. Summarize the meaningful changes and why they were needed; include
     relevant verification results only when actually performed. Simple changes may use only
     a subject; do not repeat it or list every changed file in the body.
   - If multiple logical changes are mixed, suggest splitting into separate commits
5. If the user already authorized committing these changes, show the message and commit after
   the required review. Otherwise show the proposed message and request approval. Honor an
   explicit request to approve the exact message before committing.

Additional context: the user-provided invocation text
