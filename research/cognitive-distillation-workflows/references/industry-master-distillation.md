# Industry Master OS Distillation

Use when the target is a field, niche industry, professional domain, or operating discipline. The goal is not an encyclopedia; it is a reusable field operating system.

## Scope rule
Narrow the target until it is actionable. Prefer “LLM agent infrastructure for product builders” over “AI”, “cross-border Amazon operations for small teams” over “e-commerce”, or “China ICP filing for SaaS sites” over “compliance”.

## Research tracks
Write each track to `references/research/`.

1. `01-figures.md` — practitioners, thinkers, companies, representative voices, key disputes, recent activity.
2. `02-tools.md` — canonical tools, emerging tools, decision tree, pitfalls, integration patterns.
3. `03-workflows.md` — SOPs, pipelines, novice path vs expert path, recent workflow changes.
4. `04-canon.md` — books, papers, courses, concepts, recurring references.
5. `05-sources.md` — newsletters, podcasts, communities, conferences, datasets, update cadence.
6. `06-glossary.md` — terms, standards, regulations, metrics, acronyms, quality vocabulary.

## Wave sequencing
Pure parallelism can produce weak seeds. Prefer waves:

- Wave 1: canon, sources, glossary. These tracks give seed entities and vocabulary.
- Wave 2: figures and tools, using Wave 1 seeds.
- Wave 3: workflows, using figures + tools + canon.

If source signal is low, degrade gracefully and tell the user what is missing.

## Synthesis output
Extract:

- 3-7 field mental models: how people in this field see the world.
- 5-10 playbooks: if-situation-then-action rules.
- Tool stack and selection tree.
- Workflow/pipeline: novice path, expert path, recent changes.
- Field expression DNA: terms, registers, inside/outside communication.
- Quality standards and anti-patterns.
- Knowledge lineage: schools, camps, major disagreements.
- Boundaries: freshness, weak tracks, external constraints, areas needing real practitioner validation.

## Optional cross-skill composition
For deep industry skills, select top figures only after `01-figures.md` is evidence-rich. Then generate or link sub-skills for 1-3 figures using the Persona branch. Skip this in quick tier.

## Quality gates
Before delivery:

- Does the skill help make decisions in the field, or only summarize facts?
- Are tools/workflows fresh enough for the task?
- Are weak tracks named explicitly?
- Can a future agent answer “what should I do next?” using the generated protocol?
