# Evaluating Third-Party Hermes Skills from GitHub

Use this workflow when a user shares a content link (WeChat article, blog post, tweet) that links to a GitHub repo containing a Hermes SKILL.md.

## Workflow

0. **Recall existing history before re-evaluating** — If the user asks about a skill/repo that may have been installed, published, or modified before, search TencentDB structured memory first. Use `session_search` only when raw conversation details are needed, then verify live state with GitHub/`gh`/filesystem if current status matters.

1. **Process the content first** — Save the article/blog/video to the user's knowledge system (wiki ingest). The content establishes *what problem the skill solves*.

2. **Explore the GitHub repo** — Navigate to the repo and read:
   - `README.md` — installation instructions, dependencies, philosophy
   - `SKILL.md` — Hermes metadata, workflow descriptions, trigger phrases, common pitfalls
   - `docs/` directory — any design docs, validation reports, or usage guides
   - `scripts/` — Python/Shell scripts the skill depends on

3. **Assess compatibility with this user's setup** — Key questions:
   - **Context sources**: Does the skill expect Obsidian, a specific directory structure, or other tools the user doesn't have? Can it degrade gracefully?
   - **Dependencies**: Does it need a new API key the user doesn't have? Does it duplicate an existing skill?
   - **Customization depth**: Are the scripts tightly coupled to the author's personal setup (hardcoded paths, personal directory names)?
   - **Maturity**: Number of commits, stars, age. Very new repos (< 1 week, < 5 commits) may have rough edges.
   - **Overlap with existing skills**: Does the user already have a skill that provides the same underlying API access?

4. **Make a tiered recommendation**:
   - **Lightweight install** (SKILL.md only): `hermes skills install <raw SKILL.md URL>` — loads methodology/mental model without code
   - **Full clone + configure**: `git clone` into skills directory, install deps, configure API keys
   - **Skip, capture concepts only**: The most valuable part is the *workflow design* — extract it into the wiki as a concept page and update related pages

5. **Recommendation criteria**:
   - Recommend lightweight install when the skill's methodology adds value but the scripts don't match the user's environment
   - Recommend full clone when both the methodology AND the automation scripts are compatible
   - Recommend skip+capture when the user already has equivalent tools and the real value is the design philosophy

## Common pitfalls
- Assuming a skill works out of the box because it has a proper SKILL.md format
- Installing scripts that reference Obsidian paths when the user doesn't use Obsidian
- Overlooking that the user may already have the same API access via a different skill
- Recommending full clone for a skill that's too young or too personalized