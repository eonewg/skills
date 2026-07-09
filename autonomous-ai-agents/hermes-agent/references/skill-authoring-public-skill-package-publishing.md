# Public Skill Package Publishing Notes

Use this when preparing a Hermes skill repository for public GitHub / SkillHub / ClawHub-style release.

## Repository Shape

Prefer a skill-first root layout:

```text
README.md
LICENSE
.gitignore
SKILL.md
skill-card.md
references/
scripts/
```

Avoid nesting the real skill under `skill/SKILL.md` for public distribution unless the target registry explicitly requires that layout. Public consumers should be able to inspect `SKILL.md` at repository root.

## README Tone

The public README is user-facing product documentation, not an internal release checklist.

Include:

- What the skill does.
- Repository layout.
- Dependencies and basic usage.
- Token handling rules when relevant.
- Installation as a Hermes skill.
- Model/provider attribution when external APIs or hosted models are used.

Avoid publishing internal QA text such as:

- “This repository has been sanitized...” claims.
- “Public-safety checklist before publishing changes.”
- Instructions to search for private usernames, generated outputs, local configs, or `__pycache__`.
- Session-specific audit records.

Do those checks before committing, but do not leave the checklist in the public README unless the user explicitly wants a maintainer guide.

## Provider / Model Attribution

When a skill calls hosted models or third-party APIs, document the provider and default model names in public docs and agent-facing docs.

Example pattern:

```md
### Model and provider notes

- Official structured extraction uses Baidu Qianfan / AI Studio's PaddleOCR-VL job API, defaulting to `PaddleOCR-VL-1.6`.
- The legacy fallback uses SiliconFlow's OpenAI-compatible chat completions API, defaulting to `PaddlePaddle/PaddleOCR-VL-1.5`.
```

Also mirror the same facts in `SKILL.md` and `skill-card.md` so both humans and agents see the dependency surface.

## Verification Before Push

Run the checks, but keep them out of README:

```bash
bash -n scripts/*.sh
python3 -m py_compile scripts/*.py
rm -rf scripts/__pycache__ __pycache__
grep -RInE 'sk-|token|api[_-]?key|/home/|/Users/|C:\\Users|\.env|__pycache__' . --exclude-dir=.git
```

Manually inspect matches before commit. Use `git status --short`, `git diff`, then commit/push with `git` and verify remote contents with `gh api` when working on the user's GitHub repositories.
