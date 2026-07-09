# the user System Adaptation

These are the concrete changes from upstream `swaylq/sijiao-skill` for this Hermes setup.

## 1. Use `~/teach/` as source of truth
Upstream emits `{skill}-learn/` directories. For the user, long-term learning artifacts should live under `~/teach/<topic>/` so they align with the existing `teach` skill, HTML lessons, records, resources, and references.

Portable `<topic>-learn/` exports are only created when the user asks to share or install a standalone skill elsewhere.

## 2. Private tutor is a planning/state layer, not the lesson renderer
When producing the actual lesson, load `teach` and, for HTML, `teach-html-design`. This skill should not duplicate their visual/layout rules.

## 3. Add learner-state to existing teach workspace
The main missing layer in the current system is operational study state:

- current module;
- mastery scores;
- due reviews;
- mistakes;
- next action.

Add this as `learner-state.json` next to `MISSION.md`, `GLOSSARY.md`, and `learning-records/`.

## 4. Use curriculum DAG as a compact steering artifact
For exam or technical topics, keep `curriculum.json` small and high-signal. It should answer:

- what must come before what;
- what counts as observable competence;
- what practice proves it;
- where the user is likely to get stuck.

## 5. Fit active exam constraints
For <exam-target>/考研 topics, do not generate idealized months-long routes unless asked. Compress to the active timeline and preserve current priority decisions. A private tutor plan must be a usable next-step system, not a perfect syllabus.

## 6. Default no task spam
Do not auto-create Feishu reminders, daily jobs, or recurring check-ins. the user prefers autonomous rhythm over external periodic nudges. Offer task creation only when scheduling is explicitly requested.

## 7. Verification expectations
A generated private-tutor workspace is not done until:

- `curriculum.json` exists;
- `curriculum.md` exists or can be rendered;
- `learner-state.example.json` exists;
- at least the first session plan is concrete;
- `scripts/tutor_quality_check.py` passes structure checks.
