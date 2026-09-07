---
name: "source-command-commit"
description: "Analyze changes and create a Conventional Commits format commit"
---

# source-command-commit

Use this skill when the user asks to run the migrated source command `commit`.

## Command Template

1. Check `git diff --staged` (if empty, check `git diff`)
2. Run a `reviewer` agent on the diff — write it to a file and pass the path, plus the changed-file list. Skip only for prose/doc changes that touch no control-plane file (`CLAUDE.md` Hard Rules)
3. Analyze the changes
4. Generate a Conventional Commits message
   - If multiple logical changes are mixed, suggest splitting into separate commits
5. If the user already authorized committing these changes, show the message and commit after
   the required review. Otherwise show the proposed message and request approval. Honor an
   explicit request to approve the exact message before committing.

Additional context: the user-provided invocation text

