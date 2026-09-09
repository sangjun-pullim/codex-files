# Codex skill mechanics

A skill needs `SKILL.md` with `name` and `description` in YAML frontmatter. The description
defines discovery; the body contains task guidance. Supporting files are read when needed.

## Invocation policy

Keep automatic discovery enabled by default and preserve existing policy unless the user
requests a change. Sensitivity or an approval gate is not a reason to hide a skill.
Only for a user-requested explicit-only skill, set `agents/openai.yaml`:

```yaml
policy:
  allow_implicit_invocation: false
```

This changes discovery, not permission for external actions. Preserve other interface,
dependency, and policy fields. `disable-model-invocation` is a Claude field, not a Codex setting.

## References and validation

Use relative links and state which task needs each reference. Share supporting files without
copying them or requiring unrelated workflows. Check that referenced tools and skills exist
in the target environment. When `skill-creator` is available, use its packaging validator.
Also check reference targets and realistic workflow selection: metadata validation alone does
not prove correct behavior. Write requirements that remain useful across models.
