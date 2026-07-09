---
name: skill-library-operations
description: Unified guidance for discovering, evaluating, vetting, updating, publishing, and maintaining agent skills as a library. Use when searching for skills, assessing skill quality or safety, installing from hubs, publishing skills, or maintaining the overall skill collection lifecycle.
---

# Skill Library Operations

## Overview
This umbrella skill consolidates the skill-lifecycle surface area: discovery, installation, security review, quality evaluation, publishing, and update management.

## Core workflow
1. Identify the lifecycle stage: discover, inspect, vet, install, update, evaluate, or publish.
2. Check trust and provenance before installation.
3. Distinguish functional quality review from security review.
4. Prefer umbrella-level maintenance and discoverability over micro-skills.

## Consolidated subsections
### Skill discovery and hub operations
Find candidate skills, query hubs/registries, install them, and manage publishing/update flows.

### Security vetting
Review permissions, suspicious patterns, network behavior, and supply-chain risk before adoption.

### Quality evaluation
Score skills for clarity, completeness, robustness, and publish readiness.

### Library maintenance
Handle updates, refreshes, and collection-wide hygiene as a library-management task. For the user's Hermes skill library, use `references/anthropic-skills-operating-model.md` before adding or reshaping skills: classify the skill, keep SKILL.md as the thin operating spine, move long background to references, prefer gotchas over generic instructions, and require verification evidence for side-effect workflows. When authoring or reviewing the actual `SKILL.md` content, also use `references/hermes-skill-writing-standard.md`: description must name task/trigger/key actions; body must define applicability checks, boundaries, executable steps, examples, verification, safety, and iteration rules. When a session produces a reusable operational lesson — command sequence, troubleshooting path, tool-specific pitfall, browser automation workaround, validation checklist, or workflow order correction — prefer patching the governing class-level skill or its `references/` over adding durable memory. Memory is for stable user/environment facts; skills are for “how to do this class of task next time.” If you accidentally saved a procedural/tool detail to memory and the user corrects you, remove/shorten the memory and patch the relevant skill instead. When the user asks to prune unused skills, first propose a deletion plan, preserve explicit keep-exceptions, back up `~/.hermes/skills/`, clean stale `.usage.json` entries after deletion, and verify with `skills_list`; see `references/the user-skill-library-pruning.md`.

When evaluating whether to add, merge, or reshape a skill, map it onto a workflow line rather than treating it as a standalone novelty. A useful lens is `Read → Think → Write → Publish`:
- Read: ingest/read/extract external material.
- Think: reconstruct concepts, reduce rank, ask boundary-aware Q&A, form the user's own language.
- Write: turn judgment into essays, decisions, plans, relationship/roundtable analysis, or other argued outputs.
- Publish: convert outputs into cards, slides, repos, scripts, docs, pages, or other deliverables.
If a candidate skill cannot name which stage it serves, keep it as a reference/script or merge it into an umbrella rather than adding another active skill. Prefer action-revealing names (`concept-dissect`, `plain-language`, `paper-river`, `content-card`) over vague adjectives like “intelligent”, “AI-powered”, or “all-in-one”.

### Imported skill cleanup
When cleaning imported skill folders such as `openclaw-imports`, treat them as quarantine rather than a permanent category: create a backup first, classify each skill into a Hermes domain category, migrate portable/high-confidence skills, archive OpenClaw-specific or duplicate skills under `.archive/`, merge any useful pitfall notes into the active replacement, then verify there are no active duplicate names and no active `openclaw-imports/*/SKILL.md` entries.

### External ZIP skill installation
When a user provides a direct `.zip` containing a skill, download to a temp directory, compute SHA256, inspect/vet before install, normalize non-Hermes-friendly names, place supporting docs under `references/`, and verify with `skill_view`. See `references/external-zip-skill-install.md`.

### GitHub Hermes skill from content link
When a user shares an article/blog/tweet that links to a GitHub repo with a SKILL.md, first process the article into the knowledge system (wiki ingest), then evaluate the repo (readme + SKILL.md + docs + scripts) for compatibility with the user's setup before recommending install. See `references/evaluate-github-hermes-skill.md`.

### Direct root SKILL.md repo installation
When the user gives a GitHub repository or install page for a single root-level `SKILL.md` repo and asks to install it, quarantine-clone first, inspect upstream docs and scripts, scan for destructive/dynamic execution and expected network endpoints, copy into the active Hermes profile's category directory, write runtime config with installed absolute paths, then verify with `skill_view` plus a minimal entry/probe command. See `references/direct-root-skill-repo-install.md`.

### Adapting third-party Claude Code skills into Hermes
When a user shares a GitHub repo containing Claude Code skills and asks to install/adapt it, do not blindly run upstream installers into `~/.claude/skills/`. Quarantine, inspect, collapse narrow command skills into a class-level Hermes umbrella when appropriate, move reusable files into `templates/`/`references/`, adapt paths/OS assumptions to the user's environment, initialize data safely, and verify with `skill_view`. See `references/adapt-third-party-claude-skills.md`.

### Search-provider skill installation
When installing or restoring third-party search skills (AnySearch, Tavily, Exa-backed integrations), inspect scripts before activation, avoid skill-name collisions, store provider keys in the narrowest `.env` with `0600`, verify scripts actually load that `.env`, and use direct REST probes for MCP-backed providers before restart. See `references/search-skill-provider-installation.md`. 

### Search provider skill setup and comparison
When installing or restoring search-provider skills such as AnySearch or Tavily, quarantine and scan first, prefer `~/.hermes/skills/research/<provider>/`, configure local `.env` only when the CLI loads it or after adding a minimal loader, set `chmod 600`, then verify with a real low-cost search. For Tavily/AnySearch/Exa comparison patterns and provider-routing notes, see `references/search-provider-skill-setup.md`.

### Publishing SkillHub/ClawHub-style skills to GitHub
When the user asks to publish "this skill" to GitHub, especially if they mention SkillHub/ClawHub or correct you away from a generic project repo, use a skill-first repository shape: root `SKILL.md`, `skill-card.md`, optional `references/` and `scripts/`. See `references/publish-skill-to-github.md`.

## Absorbed specialized skills
- `skill-creator` — authoring and structuring reusable skills.
- `skill-evaluator` — quality and publish-readiness review.
- `skill-vetter` and `security-skill-scanner` — security-first vetting.
- `find-skills` and `clawhub` — discovery, install, and hub operations.
- `auto-updater` — scheduled update and refresh workflows.

## Navigation
Absorbed specialized skill-management notes live in `references/`.

## Common pitfalls
- Treating quality review as equivalent to security review.
- Installing narrow skills without considering umbrella discoverability.
- Updating skills without checking local customizations.
- Publishing before running both functional and security checks.

## Verification checklist
- [ ] Lifecycle stage identified.
- [ ] Trust/provenance checked before install.
- [ ] Security and quality reviewed separately.
- [ ] Collection-level discoverability considered before adding new skills.