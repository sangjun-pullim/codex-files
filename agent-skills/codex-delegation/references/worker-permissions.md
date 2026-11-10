# Worker permissions

Read before launching or resuming an automatic CLI worker or an explicit courier's CLI child.
The supervisor supplies the effective parent approval policy, selected sandbox, authorized
checkout/write scope, and any additional managed restrictions. Config-file defaults alone
do not establish the parent session's permissions.

- Investigation uses `read-only`. Implementation uses at most `workspace-write`, within
  the parent's authorized write scope. Match a more restrictive parent sandbox; a
  `danger-full-access` parent does not grant that mode to these workers.
- Pass the parent's effective approval policy explicitly on every launch and resume.
  For interactive CLI use `-a <approval> -s <sandbox>`; for `exec` and `exec resume` use
  `-c 'approval_policy="<approval>"' -c 'sandbox_mode="<sandbox>"'` so both paths use
  supported configuration overrides. Shell-quote the actual values in nested commands.
- Preserve applicable rules, managed restrictions, and hook trust. If the effective parent
  settings are unknown or cannot be represented without broadening access, report the
  missing setting to the supervisor before launch. Do not infer them from Full Access alone.
- On rework, the supervisor rechecks permissions against the current parent and original
  assignment. Do not inherit stale permissions from the saved child session.
- A blocked command or trust prompt is evidence to report, not permission to enable a
  bypass flag, widen access, copy credentials, or approve a hook. `never` means report an
  unavailable operation instead of requesting escalation.
