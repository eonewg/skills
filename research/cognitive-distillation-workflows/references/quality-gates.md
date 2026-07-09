# Quality Gates and Repo Adaptation Notes

## Third-party skill repo adaptation
When adapting repos like `nuwa-skill`, `colleague-skill`, or `master-skill`:

1. Clone to quarantine, not the live skill directory.
2. Inspect `SKILL.md`, install scripts, tools, examples, and path assumptions.
3. Scan for destructive commands, dynamic downloads, credential handling, and host-specific paths.
4. Extract workflows into Hermes-native references rather than copying the whole upstream prompt.
5. Keep attribution in notes when borrowing method ideas.
6. Verify the resulting Hermes skill with `skill_view`.

## Local findings from inspected repos
- `nuwa-skill` downloaded to quarantine at HEAD `72857dc`, size about 73M. It had no `tools/install_hermes_skill.py` despite README mentioning one. Its core value is six-track persona cognition distillation and fidelity scoring.
- `colleague-skill` downloaded at HEAD `47039d0`, size about 15M. It includes `tools/install_hermes_skill.py` and many host/data collectors, but the reusable idea is the Work Skill + Persona split with updates/corrections.
- `master-skill` downloaded at HEAD `34ed58e`, size about 49M. Its reusable idea is field-level six-track Master OS with wave sequencing, source verification, generated CLI/playbooks, and optional figure sub-skills.

## Generated skill section check
A useful generated persona or industry skill should include:

- frontmatter with narrow trigger description;
- operating mode / answer protocol;
- models or playbooks;
- expression or field DNA;
- quality standards or anti-patterns;
- boundaries / weak spots;
- source summary and links to research notes.

Use the bundled script:

```bash
python3 scripts/distillation_quality_check.py /path/to/generated/SKILL.md
```

The script is a section sanity check, not a proof of factual correctness. Factual correctness still depends on source quality and read-back of research notes.
