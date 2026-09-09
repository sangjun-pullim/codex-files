---
name: "diagnosing-bugs"
description: "Diagnose difficult bugs or performance regressions when requested, or after a straightforward fix fails."
---

# Diagnose difficult bugs

Start with the simplest evidence: the error, stack trace, failing test, recent change, or
relevant code path. Consult expected-behavior docs or past decisions when they resolve uncertainty.

## Evidence and reproduction

Find a feedback loop observing the user's exact symptom. An existing failing test or command
qualifies. Otherwise choose a small test, dev request, browser interaction, or captured trace.
Keep credentials in environment variables and redact logs. Prefer existing runners and fixtures.

If the environment cannot reproduce the issue, continue read-only code and log analysis.
Label hypotheses and the evidence that would distinguish them. Ask for missing artifacts
when needed; production access or instrumentation needs the corresponding authorization.
Do not report an untested hypothesis as a confirmed root cause or a completed fix.

For intermittent failures, record frequency and conditions instead of demanding a fixed
reproduction rate. Bound stress runs to local resources and stop when they add no evidence.
When human interaction is necessary, [the capture helper](scripts/hitl-loop.template.sh) can
collect output; use it only when automated reproduction is impractical.

## Diagnose and fix

Form falsifiable hypotheses from the evidence and test the most likely one. Each probe should
distinguish a cause. Isolate relevant variables where needed. Reduce a reproduction when that
helps distinguish causes, not as a prerequisite to reading code.

Before fixing code, write AGENTS.md's required regression test. Assert the reported behavior
at an existing boundary and demonstrate failure before the fix and success afterward. If a
required test cannot run, report the missing validation and continue independent work.
Apply the smallest in-scope correction, then run affected and project-required checks.

## Completion

Remove temporary probes introduced for this task. Report the cause and evidence, correction,
test results, and unresolved reproduction limits. Unavailable environments remain visible as
verification limits, especially for risk-surface changes.
