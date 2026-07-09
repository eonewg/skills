# Curriculum Design

Use this when a topic does not yet have a durable curriculum under `~/teach/<topic>/`.

## Eight research tracks
Write notes under `references/research/` when doing a full build.

1. `01-map.md` — knowledge map and prerequisite dependency graph.
2. `02-canon.md` — canonical books, docs, courses, papers, primary sources.
3. `03-paths.md` — how competent practitioners actually learned it; common successful paths.
4. `04-practice.md` — deliberate practice tasks, problem sets, projects, drills.
5. `05-pitfalls.md` — misconceptions, plateaus, common wrong paths.
6. `06-assessment.md` — rubrics, milestones, exams, checklists, “can do X” evidence.
7. `07-feedback.md` — communities, tutors, review channels, real-world feedback loops.
8. `08-motivation.md` — habit rhythm, sustainable pacing, dropout risks.

Quick builds may start with tracks 1, 2, 4, 5, and 6.

## Curriculum skeleton
Build `curriculum.json` before writing lessons. Each module should include:

- id and title;
- prerequisites;
- stage: novice, advanced-beginner, competent;
- Bloom objective;
- resources;
- practice task;
- mastery evidence;
- common pitfalls;
- honest limit if AI cannot evaluate the skill fully.

## Synthesis rules
- Order modules by prerequisite truth, not textbook chapter order.
- Every module must have an assessable output.
- “Understand X” is not a milestone; “can solve/explain/build/classify X under Y condition” is.
- If a prerequisite edge is uncertain, mark it and design a diagnostic task.
- For the user, prefer fewer modules with higher leverage over a huge ideal syllabus.

## Checkpoint to show the user
Before generating lesson files, show:

- topic goal and ceiling;
- module order;
- what will be practiced;
- how advancement is judged;
- likely bottlenecks;
- first session plan.
