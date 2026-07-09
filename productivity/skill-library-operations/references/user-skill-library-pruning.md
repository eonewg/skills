# the user Skill Library Pruning

## When to use
Use this reference when the user asks to identify unused skills, propose deletion candidates, or clean a bloated Hermes skill library.

## Proven workflow
1. Load `skill-library-operations` first.
2. Inspect the visible skill library with `skills_list`.
3. Use the skill usage sidecar when available: `~/.hermes/skills/.usage.json`.
4. Classify candidates with multiple signals, not usage alone:
   - `use_count == 0` and `view_count == 0` is a strong deletion signal.
   - Skills outside the user's active workflows are strong candidates: unused creative, MLOps, social media, game-server, red-team, third-party SaaS, and narrow debugging skills.
   - Preserve active class-level umbrellas and user-designated exceptions even if low-use.
   - Do not delete replacement/umbrella skills that encode current workflows, e.g. Feishu, search routing, memory, knowledge ingestion, PDF OCR, email, Hermes operations.
5. Present a deletion plan first. Do not delete before the user confirms.
6. Capture explicit keep-exceptions from the user and apply them exactly.
7. Before deletion, create a full backup tarball of `~/.hermes/skills/`, e.g. under `~/.hermes/backups/skills-before-cleanup-<timestamp>.tar.gz`.
8. Delete only confirmed skill directories.
9. Clean empty directories after deletion.
10. Remove stale `.usage.json` entries for deleted skills by name, relative path, and colon-qualified path variants.
11. Verify with `skills_list` and report before/after counts plus preserved exceptions.

## the user's current keep bias
Even if low-use, the user explicitly wanted to keep these during the 2026-06 cleanup:
- `love`
- `midnight-companion`
- `notion`
- `obsidian`
- `powerpoint`
- `youtube-content`
- `yt-dlp-downloader`

Treat this as a preference signal, not a permanent ban on future cleanup. Ask again before removing any of them.

## Reporting style
Be concise and concrete:
- backup path
- deleted count
- remaining count
- explicitly preserved exceptions
- any overlap/consolidation notes

Avoid dumping the full deletion list unless the user asks for the complete audit trail.

## Pitfalls
- Do not delete based purely on `skills_list`; it lacks usage history.
- Do not delete active routing/umbrella skills just because they are newly created and low-use.
- Do not delete user-specified exceptions.
- Prefer class-level cleanup and consolidation over one-off narrow skill churn.
