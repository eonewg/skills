# Third-party sources and attribution for `agent-memory-systems`

This file is generated during public packaging to keep upstream references visible. Verify upstream licenses before redistributing modified scripts or templates.

## URLs

- https://github.com/CortexReach/memory-lancedb-pro.git
- https://github.com/CortexReach/toolbox
- https://github.com/CortexReach/toolbox/tree/main/memory-lancedb-pro-setup
- https://github.com/EvoMap/evolver/releases`
- https://github.com/hopyky
- https://github.com/peterskoett/self-improving-agent.git
- https://github.com/pskoett/pskoett-ai-skills
- https://github.com/pskoett/pskoett-ai-skills/tree/main/skills/self-improvement

## Source/license lines found in the skill files

- `- network: [api.github.com, evomap.ai]`
- `- network: ["!api.github.com", "!*.evomap.ai"]`
- `- host: api.github.com`
- `| `api.github.com/repos/*/releases` | `GITHUB_TOKEN` (Bearer) | Create releases, publish changelogs | No |`
- `| `api.github.com/repos/*/issues` | `GITHUB_TOKEN` (Bearer) | Auto-create failure reports (sanitized via `redactString()`) | No |`
- `Latest releases and changelog: `https://github.com/EvoMap/evolver/releases``
- `source: explicit`
- `source: inferred`
- `Source: https://github.com/CortexReach/toolbox/tree/main/memory-lancedb-pro-setup`
- `git clone -b master https://github.com/CortexReach/memory-lancedb-pro.git /tmp/memory-lancedb-pro`
- `git clone -b master https://github.com/CortexReach/memory-lancedb-pro.git plugins/memory-lancedb-pro`
- `**Config validation tool** (from [CortexReach/toolbox](https://github.com/CortexReach/toolbox)):`
- `**Access reinforcement note:** Reinforcement is whitelisted to `source: "manual"` only — auto-recall does NOT strengthen memories, preventing noise amplification.`
- `| `project:<id>` | Project-specific memories |`
- `Project: { name, status, goals[], owner? }`
- `| Simplify/Harden recurring patterns | Log/update `.learnings/LEARNINGS.md` with `Source: simplify-and-harden` and a stable `Pattern-Key` |`
- `git clone https://github.com/peterskoett/self-improving-agent.git ~/.openclaw/skills/self-improving-agent`
- `Remade for openclaw from original repo : https://github.com/pskoett/pskoett-ai-skills - https://github.com/pskoett/pskoett-ai-skills/tree/main/skills/self-improvement`
- `- Source: conversation | error | user_feedback`
- `- Set `Source: simplify-and-harden``
- `Create `.claude/settings.json` in your project:`
- `homepage: https://clawic.com/skills/self-improving`
- `- Every action from memory → cite source: "Using X (from projects/foo.md:12)"`
- `Created by [hopyky](https://github.com/hopyky)`

## License signals

- `MIT`
