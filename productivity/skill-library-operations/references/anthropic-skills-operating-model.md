# Anthropic Skills operating model for the user

Use this reference when maintaining the user's Hermes skill library after ingesting Anthropic's internal Skills lessons.

## Core interpretation

A Skill is not a longer prompt. Treat it as a task-oriented work package: trigger description, short operating protocol, references, scripts, templates, setup config, gotchas, hooks/guardrails, usage evidence, and verification.

## Nine-way routing

Before adding or rewriting a skill, classify it into one primary class:

| Class | What belongs here | the user examples |
|---|---|---|
| Library / API reference | Team-specific use of SDKs, CLIs, APIs, schema quirks | lark-cli, WeRead API, Kimi/WebBridge, wiki scripts |
| Product verification | Proving output really works | wiki ingest verification, Feishu task read-back, browser proof |
| Data fetching / analysis | Stable data retrieval and analysis helpers | WeRead shelf sync, task queries, market/search batches |
| Business process / automation | Repeated team/life workflows | morning brief, article ingestion, daily task triage |
| Code scaffolding / templates | Fixed code or document skeletons with NL constraints | plans, reports, HTML artifacts, PR templates |
| Code quality / review | Review, lint, adversarial checks | PR review, skill review, wiki source validation |
| CI/CD / deployment | Build, release, rollout, rollback | Hermes/plugin deploy flows |
| Runbooks | Symptom-first troubleshooting | gateway down, memory plugin broken, extraction blocked |
| Infrastructure operations | Dangerous cleanup, resources, credentials, cost | cron cleanup, profile hygiene, destructive operations |

If one skill seems to span more than two classes, it is probably an umbrella skill plus references, not a single narrow operational skill.

## What to write into SKILL.md

Keep `SKILL.md` as the directory and operating spine:

- trigger conditions and negative triggers;
- prerequisites and setup checks;
- the shortest safe workflow;
- high-signal gotchas;
- checkpoint / verification commands;
- safety guardrails and escalation rules;
- pointers to `references/`, `scripts/`, `templates/`, and `assets/`.

Do not put long background, full API docs, whole article summaries, or generic instructions the model already knows into `SKILL.md`. Put long material into `references/` and deterministic checks into `scripts/`.

## Gotchas beat generic steps

Prefer facts that pull the agent away from a likely wrong default:

- field aliases across systems;
- append-only/versioned tables;
- "HTTP 200 does not mean business success" cases;
- user-specific target IDs, task-list IDs, channel routing;
- hash/lint/index count exactness;
- commands that look safe but mutate external state;
- platform quirks and login/CAPTCHA failure modes.

If a line merely says "run tests" or "be careful", replace it with the exact test command, expected output, or state read-back.

## Verification-first rule

For every skill with side effects, define evidence stronger than a final natural-language report:

- file hash or lint result;
- read-back from external API;
- database/API state check;
- screenshot/video/log for UI flows;
- source-path existence validation;
- diff + test command for code changes;
- rollback/checkpoint path for risky operations.

The final answer can explain; it cannot be the proof.

## Usage measurement and pruning

When maintaining the library, ask:

- Which skills are frequently triggered and save real work?
- Which should have triggered but did not? Patch the description.
- Which trigger too broadly and pollute context? Narrow or split.
- Which contain long references in the body? Move them to `references/`.
- Which are obsolete because an umbrella skill absorbed them? Merge and delete.

Skill quality is not "more skills". It is accurate trigger, thin context, hard verification, and low maintenance tax.
