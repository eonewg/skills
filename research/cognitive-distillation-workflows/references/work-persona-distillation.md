# Work + Persona Distillation

Use when the target is a teammate, colleague-like role, expert worker, operator, team style, or a work identity where the skill must actually help do work.

## Core split
Do not collapse everything into one persona voice. Preserve two layers:

- Work Skill: responsibilities, systems, standards, workflows, artifacts, review criteria, preferences, tools, examples.
- Persona: communication style, decision posture, conflict pattern, feedback style, social behavior, correction notes.

The generated skill may expose three use modes:

- full mode: persona receives the task, work skill completes it, final output uses persona style;
- work-only mode: ignore persona style and execute the workflow cleanly;
- persona-only mode: answer about communication/expectations, not technical execution.

## Intake
Collect only high-leverage information:

- alias / role / context;
- what work they are known for;
- known standards or artifacts;
- examples of decisions or reviews;
- communication traits;
- local files or exports, if the user has them;
- whether this is new, update, or correction.

## Evidence tracks
Recommended files:

- `01-artifacts.md`: documents, PRs, specs, presentations, deliverables.
- `02-decisions.md`: review comments, tradeoff calls, past decisions.
- `03-workflows.md`: repeatable processes and checklists.
- `04-communication.md`: wording, feedback, tone, escalation style.
- `05-corrections.md`: user corrections like “they would not say/do this.”
- `06-meta.md`: source list, confidence, gaps.

## Update loop
Generated work/persona skills should support correction:

1. User says “this is wrong / they would not do this.”
2. Locate which layer is wrong: Work Skill, Persona, or source facts.
3. Patch `references/research/05-corrections.md` and the relevant section of `SKILL.md`.
4. Version the old output when making a substantial rewrite.
5. Re-run quality checks.

## What to borrow from colleague/dot-skill
- The Work Skill + Persona split is the main value.
- Versioning and correction history are useful.
- Family presets are useful as patterns, but do not copy host-specific slash commands into Hermes blindly.
- Avoid bringing over hard-coded `.claude`, OpenClaw, Codex, Feishu, or DingTalk assumptions unless this generated skill explicitly needs them.
