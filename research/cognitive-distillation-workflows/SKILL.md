---
name: cognitive-distillation-workflows
description: Create or evaluate Hermes-native skills that distill a person, persona, teammate/colleague, public thinker, theme, or niche industry into a reusable cognitive operating system. Use for requests like “蒸馏某人/某行业”, “造一个人物视角 skill”, “做大师/同事/女娲类 skill”, “把某领域变成 master skill”, or adapting Nuwa/colleague/master-skill methods into Hermes. Not for simple biographical summaries or generic web research.
---

# Cognitive Distillation Workflows

## Purpose
Turn high-signal material about a person, role, relationship, theme, or niche industry into a self-contained Hermes skill that can reason and act with reusable models, not just imitate surface style.

This skill is adapted from three upstream patterns inspected locally in quarantine:
- `nuwa-skill`: public/personality cognition distillation, six-track evidence, mental models, fidelity scoring.
- `colleague-skill` / `dot-skill`: Work Skill + Persona split, correction/update loop, versioned generated skills.
- `master-skill`: industry Master OS, six-track field research, wave sequencing, tools/workflows/canon/sources/glossary.

## Trigger decision
1. If the target is a person or persona, use the **Persona / Thinker** branch.
2. If the target is a teammate/role/work identity, use the **Work + Persona** branch.
3. If the target is a niche industry/domain, use the **Industry Master OS** branch.
4. If the user asks to install/adapt third-party skill repos, first quarantine clone and inspect before copying anything into `~/.hermes/skills/`.

## Default Hermes output shape
Create generated skills as self-contained directories:

```text
<generated-skill>/
├── SKILL.md
├── meta.json
├── references/
│   ├── research/
│   ├── synthesis.md
│   └── sources/
└── scripts/        # optional, only deterministic helpers
```

For active Hermes library additions, keep `SKILL.md` thin and move long background into `references/`.

## Operating protocol
1. Clarify only what changes the research plan:
   - target and scope;
   - persona vs work vs industry;
   - user role / intended use;
   - local materials, if any;
   - budget tier: quick, standard, deep.
2. Create a local working directory before research. Every research track must write a file under `references/research/`; research that is not written down does not count.
3. Use primary material first when available. Label every claim as primary, secondary, or inference. Keep contradictions instead of smoothing them away.
4. Insert two checkpoints before final construction:
   - research checkpoint: source count, key findings, missing tracks, contradictions;
   - synthesis checkpoint: models, heuristics/playbooks, style/industry DNA, boundaries, weak spots.
5. Build the generated skill only after the synthesis is coherent.
6. Verify with `scripts/distillation_quality_check.py` or an equivalent section check, then read back the generated `SKILL.md`.

## Branch summaries
### Persona / Thinker branch
Use `references/persona-distillation.md`.
Core tracks: writings, conversations, expression DNA, external views, decisions, timeline.
Output: 3-7 mental models, 5-10 decision heuristics, expression DNA, values/anti-patterns, knowledge lineage, honest boundaries, answer protocol.

### Work + Persona branch
Use `references/work-persona-distillation.md`.
Core split: Work Skill for actual methods and reusable workflows; Persona for communication and decision posture. Keep them separable so tasks can invoke work-only or persona-only behavior when useful.

### Industry Master OS branch
Use `references/industry-master-distillation.md`.
Core tracks: figures, tools, workflows, canon, sources, glossary. Prefer wave sequencing: canon/sources/glossary first, then figures/tools, then workflows.

## Cost and scope controls
- Quick: 3 tracks, shallow source count, useful prototype.
- Standard: full relevant tracks, enough sources for cross-checking.
- Deep: full tracks plus local materials, long-form transcripts, scoring, and optional sub-skills.

Default to **quick** when the user has not explicitly asked for a polished publishable skill.

## Verification checklist
- [ ] Generated skill directory is self-contained.
- [ ] Research files exist under `references/research/`.
- [ ] Claims are source-labeled or explicitly marked as inference.
- [ ] Final skill has models/playbooks, DNA, anti-patterns, boundaries, and agentic protocol.
- [ ] Third-party install scripts were not run against the real home directory unless intentionally approved.
- [ ] Final answer reports real paths and real verification output.

## Common pitfalls
- Copying upstream `SKILL.md` directly into Hermes: usually too long, path assumptions differ, and the trigger will be noisy.
- Building a role-play skin without work protocol or evidence.
- Letting a single famous figure dominate an industry skill; use the field’s workflow and tools, not only celebrities.
- Treating generated examples as automatically verified; run a local check and inspect the sections.
- Using full transcripts or copyrighted long text in the generated skill. Store only concise notes, metadata, and short necessary quotes.