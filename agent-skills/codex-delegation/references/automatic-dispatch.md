# Automatic dispatch supervised by Astra

Use this workflow after Astra selects delegation under AGENTS.md's subscription-usage policy.
AGENTS.md owns the decision criteria and model table. Workers do not become supervisors.

## Assignment and execution location

- Astra identifies the bounded outcome, exact checkout, owned files, acceptance criteria,
  selected model and reasoning effort. A worker prompt must say that others may be working
  in the repository: preserve their edits and do not modify files outside its assignment.
- Group related work that needs the same context into one assignment. Pass relevant paths,
  decisions, and existing verification evidence instead of the full conversation. Keep the
  report focused on findings or changes, evidence, and unresolved issues; continue related
  rework in the same worker session as described below.
- For an approved spec, pass its absolute path and assigned steps unchanged. The supervisor
  owns spec markers, assembly, review, and closing. A small task needs no new spec unless
  an existing approval boundary requires one.
- Reuse the chosen checkout. A single worker can use the current checkout sequentially;
  opening a split pane does not itself create isolation. Do not run concurrent writers or
  edit the worker's files from the supervisor while it runs. Independent read-only tasks
  may run in parallel when they do not depend on files being changed.
- When separate checkouts are necessary, follow AGENTS.md's worktree-location boundary and
  `orca-cli`'s worktree reference. Select an existing terminal in each chosen checkout's card
  as the split anchor. Do not split an unrelated card and silently run in another checkout.

## Visible Orca execution

Read `orca-cli`'s setup and terminal references for the executable and handle lifecycle.
Check runtime status, then obtain the intended terminal with `terminal list`; do not use
whichever unrelated pane happens to be active. The split is horizontal (left/right).

Keep task artifacts in a unique scratch directory outside the checkout. Use a file-writing
tool to save `prompt.md` and a short launcher. Pass the prompt as a literal process argument,
not shell source. Keep stdin, stdout, and stderr attached to the pane's PTY so Codex can
render its interactive interface; do not pipe them through `tee` or redirect stdin from a file.

The worker prompt includes the task and these role constraints:

> You are the worker assigned by the Astra supervisor. Implement or investigate only the
> assigned scope. Do not classify the overall task, spawn agents, select another model,
> or approve your own result. Return changed files or findings, supporting evidence,
> checks with exit codes, and unresolved issues. Preserve other contributors' changes.

Launch interactive `codex`, without the `exec` subcommand or `--json`. Use an explicit model
and effort so it does not inherit Astra's user default.
Disable further subagents for this child invocation using `-c agents.enabled=false`.
Code investigation uses `-s read-only`; implementation may use `-s workspace-write` only
within the supervisor's granted write scope. Match a more restrictive parent sandbox and
applicable managed restrictions; never use danger flags, ignore user rules, bypass hooks,
or copy credentials. Pass the parent's approval mode explicitly instead of relying on an
unrelated CLI default. If a trust or approval prompt blocks work, report that concrete
boundary to Astra; do not broaden permissions or approve it merely to make the worker finish.

Example `run.py` beside `prompt.md`, after replacing the checkout, model, effort, and
permission values with Astra's selection:

```python
from pathlib import Path
import os

prompt = Path(__file__).with_name("prompt.md").read_text()
args = [
    "codex", "-m", "gpt-5.6-sol", "-c", 'model_reasoning_effort="high"',
    "-c", "agents.enabled=false", "-a", "on-request", "-s", "workspace-write",
    "-C", "<checkout>", prompt,
]
os.execvp(args[0], args)
```

Use the mode and approval value appropriate to the actual parent, not the example's values
blindly. Execute the prepared launcher in a split:

```text
orca terminal split --terminal <anchor-handle> --direction horizontal --command <quoted-exec-python-launcher-command> --json
```

Record the returned handle and rename that pane to `<model> · <task>`. The startup command
is `exec python3 <shell-quoted-launcher-path>`. Verify the pane shows the Codex interface
with the selected model and effort.

Wait on the exact worker handle with `terminal wait --for tui-idle`, using waits of at most
60 seconds so the supervisor can report progress. Then use bounded `terminal read` output
and cursors to inspect the current response. Idle alone is not success: it can be an initial
input prompt, a trust/approval dialog, or a stopped turn. Require a final response to the
assigned task, check its evidence and relevant diff, and resolve missing work. A timeout is
not completion or failure. The TUI normally remains running after a response; do not wait
for process exit to recognize task completion, or treat an unexpected exit as a passing run.

Record the exact session ID, model, effort, and permissions from metadata unambiguously
associated with this worker. If unavailable, after reading the final response use
`terminal send --terminal <worker-handle> --text /status --enter` on that idle Codex pane
and read its output. Orca can report `agent_prompt_stalled` for a
handled slash command; inspect the pane before assuming delivery failed or retrying it.
For incomplete or ambiguous output, inspect only that session's saved transcript; terminal
reads can omit a final line even without a truncation flag. Do not choose a session by recency.
Keep the pane and task artifacts through review and correction. After final acceptance, record the needed evidence,
then close only this dispatch's pane and remove its scratch files. Do not remove checkouts
or branches as pane cleanup.

## Review and correction

Astra inspects the worker's findings or actual diff and relevant callers, checks acceptance
criteria, and decides whether the result is correct. Worker self-checks are evidence, not
the final review. Use a fresh Astra `reviewer` whenever AGENTS.md or an approved spec requires
independent review. Reuse still-valid review and test evidence as AGENTS.md permits.

Preserve the worker's checkout and session for a correction of the same task. Read the pane
before sending a bounded follow-up with
`terminal send --terminal <worker-handle> --text <literal-prompt> --enter`;
confirm it is the intended idle Codex input, not a shell or an approval dialog. Use argument
arrays or proper shell quoting for the input. Confirm delivery from subsequent output before
retrying a timed-out send, to avoid duplicate instructions. Apply the same completion checks
to the new response, not an earlier final response.

If the pane has closed, open interactive `codex resume <exact-session-id> <literal-prompt>`
in the chosen checkout's split. Explicitly pass the selected model, effort, `-C`, `-s`, `-a`,
and `-c agents.enabled=false` again. Do not use `exec resume` or `--last`. If the session ID
cannot be established, report that limitation instead of resuming another session.
Astra decides whether to keep the model, promote the task, or handle it as complex work.
After the same failure repeats, inspect the cause before another attempt; do not loop
through models without new evidence. Continue other independent work while a real decision
or approval is pending.

For separately committed worker branches, use only the assembly and completion rules in
[delegated execution](../../impl-execute/references/delegated-execution.md); automatic
dispatch does not select that document's courier-specific steps. Preserve the user's merge
boundary. Shared-checkout work does not need an integration branch merely because it was
delegated.

## When Orca is unavailable

Distinguish sandbox-denied runtime access from a stopped Orca instance; use the applicable
tool approval flow for a denied status/list command before declaring Orca unavailable.
If there is no usable Orca runtime, report the display limitation and use a native worker
with explicit `model` and `reasoning_effort` from Astra's selection and `fork_turns="none"`,
if it preserves the requested location and isolation. A custom role must not override those
values; use a compatible role or the default role. Include the same role constraints. Never silently discard an explicit
requirement for a visible Orca worker or a specific isolated checkout; continue independent
analysis while that requirement is unresolved.
