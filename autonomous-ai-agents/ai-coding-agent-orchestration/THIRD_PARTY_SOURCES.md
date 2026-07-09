# Third-party sources and attribution for `ai-coding-agent-orchestration`

This file is generated during public packaging to keep upstream references visible. Verify upstream licenses before redistributing modified scripts or templates.

## URLs

- https://github.com/openai/codex
- https://github.com/user/repo.git

## Source/license lines found in the skill files

- `license: MIT`
- `2. **Local project:** `.claude/settings.local.json` (personal, gitignored)`
- `3. **Project:** `.claude/settings.json` (shared, git-tracked)`
- `2. **Project:** `./CLAUDE.md` — project-specific context (git-tracked)`
- `# Project: My API`
- `Delegate coding tasks to [Codex](https://github.com/openai/codex) via the Hermes terminal. Codex is OpenAI's autonomous coding agent CLI.`
- `terminal(command="REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git $REVIEW && cd $REVIEW && gh pr checkout 42 && codex review --base origin/main", pty=true)`
- `terminal(command="REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git $REVIEW && cd $REVIEW && opencode run 'Review this PR vs main. Report bugs, security risks, test gaps, and style issues.' -f $(git diff origin/main --name-only | head -20 | tr '\n' ' ')", pty=true)`

## License signals

- `license: MIT`
