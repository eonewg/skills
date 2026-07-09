# Curation Policy

This repository is not a dump of a local skill directory. It publishes only skills that are original to this library or have been substantially adapted into reusable Hermes/OpenClaw workflows.

## Kept

- Original workflow skills authored for recurring agent operations.
- Substantially adapted skills that combine upstream ideas with new Hermes-native procedures, validation steps, scripts, or operating rules.
- Umbrella skills that consolidate multiple narrower skills into a reusable class-level workflow.

## Excluded

- Directly downloaded third-party skills with little or no modification.
- Vendor or marketplace wrappers whose main function is connecting to a specific external service.
- Skills that mainly package another project without adding a reusable agent workflow layer.

## Publication checks

- Redact personal identifiers, local paths, emails, chat IDs, and real-looking secrets.
- Preserve attribution for adapted sources in `THIRD_PARTY_SOURCES.md` and `NOTICE.md`.
- Validate frontmatter and script syntax before pushing.
- Verify the remote README and remote `SKILL.md` count after pushing.
