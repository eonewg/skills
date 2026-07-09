# Publishing SkillHub/ClawHub-style skills to GitHub

## GitHub operation policy for the user-owned skill repos

Use `gh` CLI + `git` as the primary path for repository writes: clone/create, commit, push, release creation, repo metadata changes, issues, and PRs. Use raw GitHub API only for read-only public checks or as a fallback when `gh` is unavailable or unauthenticated. If a repo was previously published, recall it via TencentDB memory first, then session search, then verify current remote state.



## Key lesson

Do **not** default to a generic project layout like `skill/SKILL.md` unless the user explicitly wants a package repository. SkillHub/ClawHub-style skill repositories are usually skill-first, with the skill metadata at the repository root.

Preferred public repo shape:

```text
SKILL.md
skill-card.md
references/
  <topic>.md
scripts/
  <helper>.sh|py
README.md
LICENSE
.gitignore
```

Minimal examples from ClawHub inspection often contain only:

```text
SKILL.md
skill-card.md
```

## Workflow

1. Inspect a comparable published skill if needed:

```bash
clawhub search <topic>
clawhub inspect <slug> --files
clawhub inspect <slug> --file SKILL.md
```

2. Reshape the local skill for publishing:
   - Move the main `SKILL.md` to repository root.
   - Put detailed notes under `references/`.
   - Put deterministic helper scripts under `scripts/`.
   - Add `skill-card.md` for marketplace/repo presentation.
   - Keep `README.md` focused on human installation and usage.

3. Run a secret and portability scan before publishing:
   - No API tokens, PATs, `.env`, secret files, or bearer tokens.
   - Replace user-specific absolute paths like `/home/<user>/.hermes` with `~/.hermes` or documented configurable paths.
   - Keep token examples as placeholders only, never real-looking values.
   - Check that README/SKILL references no obsolete layout such as `skill/SKILL.md` or `skill/references/` after reshaping.
   - Syntax-check executable helpers before publishing (`bash -n scripts/*.sh`; `python -m py_compile scripts/*.py` when Python helpers exist).

4. Publish to GitHub:
   - Prefer `gh repo create ... --source . --public --push` when `gh` is installed and authenticated.
   - For the user-owned repos, default to `gh` + `git` for writes; raw GitHub API is only a read-only verification path or explicit fallback.
   - If `gh` is unavailable, use the GitHub API to create the repo, then push with git credentials or another authenticated path.
   - Do not persist the user's GitHub token into repository remotes, scripts, README, shell history snippets, or skill files.

5. Verify the remote, not just the local tree:
   - Use `gh api repos/<owner>/<repo>/contents?ref=<default-branch>` or `gh repo view` plus a contents call to confirm `SKILL.md`, `skill-card.md`, `references/`, and `scripts/` are visible at the default branch root.
   - Confirm the old nested `skill/` directory is gone when the target format is SkillHub/ClawHub root layout.
   - Report the pushed commit SHA and timestamp only after remote verification succeeds.

## Pitfalls

- User says "the OCR skill" / "SkillHub GitHub skill" means publish the skill as a skill artifact, not merely a normal project archive.
- Creating the remote repo is not enough; verify that the default branch has the expected files visible remotely.
- If a token was pasted in chat for one-off publishing, recommend revoking it after use.
