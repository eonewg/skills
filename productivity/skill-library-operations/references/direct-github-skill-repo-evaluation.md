# Direct GitHub Skill Repo Evaluation

Use this when a user drops a GitHub repository that appears to contain agent skills, especially repos designed for Claude Code/OpenClaw/ClawHub rather than Hermes.

## Fast workflow

1. Clone to `/tmp` with shallow history.
2. Inspect repository shape:
   - `README.md` for intent, install instructions, data directories, assumptions.
   - `SKILL.md` files under root or subdirectories.
   - `templates/`, `references/`, `scripts/`, and any install script.
3. Scan for risk patterns before recommending installation:
   - Secrets: `token`, `api_key`, `password`, `secret`, private key material.
   - Destructive shell: `rm -rf`, `sudo`, `chmod/chown` outside the repo, credential edits.
   - Network/supply-chain: `curl|wget|pip|npm|uv|git clone` in install scripts.
4. If there is an install script, do a harmless dry-run style execution only when feasible:
   - Use a temporary `HOME` and any documented data-dir env vars.
   - Verify created files and that it does not touch the real profile.
5. Check fit with the user's environment and preferences:
   - Does it write to `~/.claude/skills`, `~/.hermes/skills`, or another agent's skill path?
   - Does it assume Obsidian or a personal vault path? If the user avoids Obsidian by default, recommend a local data directory instead.
   - Does it duplicate an existing umbrella skill?
6. Give a tiered recommendation:
   - **Install as-is** only when target agent, paths, deps, and workflows match.
   - **Adapt into Hermes** when the core workflow is valuable but paths/triggers/agent conventions differ.
   - **Capture concepts only** when the repo is mostly a good mental model or duplicates existing tooling.

## Compatibility notes from the LeetCode skill repo case

A repo can be safe and still not be a good direct install. `beyondaprilzjl-lab/leetcode-skill` was a clean, tiny, dependency-free Claude Code skill repo, but direct install would copy to `~/.claude/skills/`, not Hermes. The better recommendation was to adapt the workflow into a Hermes class-level skill, keep the data under the user's study directory, and preserve the useful loop: low-friction start → Socratic post-solve review → local Markdown notes → spaced repetition.

## Persona / distillation skill repo evaluation

For repos that generate persona, colleague, celebrity, mentor, or industry "distillation" skills, evaluate the method separately from direct installability:

1. Quarantine-clone the full repo before installation and record path, HEAD, branch, remote, total size, tracked file count, and every `SKILL.md` found.
2. Inspect the root `SKILL.md`, README, `references/`, `scripts/`, `examples/`, and any claimed runtime installers. If the README claims Hermes support via a script such as `tools/install_hermes_skill.py`, verify the file actually exists before recommending direct install.
3. Scan for destructive and supply-chain patterns (`rm -rf`, `sudo`, `chmod/chown`, `curl|wget`, `pip install`, `npm/npx`, `git clone`, secret-looking strings), but distinguish README examples and semantic words like "token" from real credential leaks.
4. For Python/Bash helpers, prefer harmless verification: `python3 -m py_compile` for Python scripts, then run bundled self-check scripts against sample skills when they are read-only. Treat self-reported fidelity scores as claims; compare them with executable checks when available.
5. For persona distillation specifically, preserve useful methodology even when not installing: multi-axis source collection, first-hand vs second-hand source weighting, explicit honest boundaries, fidelity scorecards, and cost/agent-count checkpoints are often more valuable than the repo's runtime-specific slash commands.
6. Recommend **adapt into a Hermes class-level umbrella** when the repo assumes `.claude/skills/`, long multi-agent Claude Code workflows, or missing Hermes installers, even if the conceptual workflow is strong.

## Common pitfalls

- Treating a Claude Code skill as automatically usable by Hermes.
- Trusting README compatibility claims without checking that the named installer or target path exists.
- Running `install.sh` against the real `$HOME` before sandboxing it.
- Calling a repo unsafe just because it has an installer; inspect what the installer actually changes.
- Importing a narrow set of slash-command skills as separate flat skills when one class-level umbrella with trigger flows would fit the library better.
- Treating a repo's own fidelity/quality badges as verification without running any included deterministic checks.
- Letting model-generated LeetCode slugs become a hidden source of broken links; prefer explicit slugs/links in templates when adapting such skills.
