---
name: sijiao-learning-workflows
description: Stateful private-tutor workflow for turning “I want to learn X” into a durable learning path with curriculum DAG, learner state, spaced repetition, mastery checks, and Hermes teach-workspace integration. Use for “私教 skill”, “学 X”, “继续学 X”, “考我 X”, “做一个 X 学习 skill”, “把 X 做成长期学习路线”. Not for one-off explanations; use `teach` directly for a single HTML lesson.
---

# Sijiao Learning Workflows

## Purpose
Create and operate stateful private-tutor learning paths. This is separate from `cognitive-distillation-workflows`: cognitive distillation makes agents think/operate like a person or field; 私教 makes the user learn a skill.

Upstream inspected locally:
- `swaylq/sijiao-skill` at HEAD `16d5d55`.
- Local verification: `tools/self_test.py` passed, `pytest` showed `35 passed`.

## Position in the user's system
- This skill owns the curriculum/state layer.
- `teach` owns individual lesson delivery under `~/teach/<topic>/`.
- `teach-html-design` owns HTML visual/layout QA when lessons are generated.
- `study-habits` owns broad exam planning and spaced review advice; this skill owns topic-local learner state.

Do not merge this skill into `teach`: upstream `teach` is a lesson-workspace protocol, while upstream 私教 is a curriculum/state generator. They share learning-science language but operate at different time scales.

## When to use
Use this when the task asks for a durable learning system:
- build a learning path;
- continue a previous topic;
- quiz/review a topic based on prior state;
- generate a reusable learning skill for a subject;
- adapt upstream 私教.skill ideas to Hermes.

Do not use for a single answer, quick concept explanation, or one-off resource recommendation.

## Hermes workspace shape
For the user, prefer the canonical teaching root instead of random generated folders:

```text
~/teach/<kebab-topic>/
├── MISSION.md
├── curriculum.json
├── curriculum.md
├── learner-state.json              # private/local, never publish by default
├── learner-state.example.json
├── GLOSSARY.md
├── RESOURCES.md
├── references/
├── lessons/
├── learning-records/
└── NOTES.md
```

If a portable skill package is explicitly requested, create a separate self-contained `<topic>-learn/` export from this workspace.

## Operating protocol
1. Decide whether the user wants a stateful learning path or a single lesson.
2. If stateful, create or open `~/teach/<topic>/`.
3. Read existing `MISSION.md`, `curriculum.json`, `learner-state.json`, and recent `learning-records/` if present.
4. If no curriculum exists, run the eight-track research/synthesis workflow in `references/curriculum-design.md`.
5. Before generating lessons, checkpoint the curriculum skeleton: modules, order, milestones, and assessment style.
6. For actual lesson creation, load `teach`; for HTML lessons also load `teach-html-design`.
7. Each session starts with due retrieval/review items, then one small new learning target.
8. End by updating `learner-state.json` and recording the next concrete action.

## the user-specific defaults
- Default ceiling is competent performance, not expert/mastery.
- Prefer compressed, high-yield routes over “complete textbook coverage.”
- For exam subjects, preserve current考研 constraints: topic progress must fit the active <exam-target> timeline, not an ideal long course.
- Do not create Feishu tasks or recurring reminders unless the user asks; output the next action first.
- A beautiful lesson is not enough: every lesson must include observable evidence for advancing.

## Key references
- `references/curriculum-design.md` — eight-track research and curriculum DAG.
- `references/learner-state.md` — state model, spaced repetition, update rules.
- `references/the user-system-adaptation.md` — adaptations from upstream 私教.skill to this Hermes setup.

## Verification
For generated learning paths, run:

```bash
python3 scripts/tutor_quality_check.py ~/teach/<topic>
```

This checks structure only. Real quality still requires reading the curriculum and trying one lesson.