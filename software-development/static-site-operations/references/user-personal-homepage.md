# the user personal homepage deployment notes

Session-derived notes for maintaining the user's current static homepage. Keep this as operational context, not a secret store.

## Current shape

- Site type: single-page static HTML served by Nginx.
- Remote access: use the configured SSH alias from memory (`baidu-vm`).
- Live document root: `/var/www/html/`.
- Main file: `/var/www/html/index.html`.
- Public URL: the bare IP homepage currently serves the page over HTTP.
- Current design direction: minimal, centered, white-background, linear sections; avoid card-heavy portfolio styling.

## Editing pattern that worked

1. Pull the live file locally with `scp` into `/tmp`.
2. Parse/extract visible section text before editing to avoid breaking the existing visual system.
3. Preserve the existing clean iOS-like design unless the user explicitly asks for a redesign.
4. Before deploy, back up live file as `index.html.bak-YYYYMMDD-HHMMSS`.
5. Deploy via `scp`, then run `nginx -t` when relevant.
6. Verify with public `curl`, cache-busted browser URL, visual screenshot, and browser console.
7. Search the deployed public HTML for banned/removed phrases, not only the local file.

## the user homepage content preferences

Current preferences captured from iteration:

- First screen should be clean, centered, and composed around a big title plus buttons.
- Do not leave a lopsided layout after removing a right-side hero panel; re-center the hero.
- Remove public exam-target content when requested. Current final page should not mention `北大`, `PKU`, `备考北大`, or `<exam-target>`.
- Avoid lots of cards. Prefer natural paragraphs, simple section titles, separators, and a few linear items.
- GitHub (`example-user`) should be intentionally sparse: current preference is only the hero button and contact section.
- Avoid over-polished résumé boasting. The tone should feel honest, ambitious, slightly literary, and grounded in actual work.

Good language patterns:

- “长期操作台”
- “公开学习档案”
- “正在进化的学习操作系统”
- “把混乱的热情，训练成稳定的能力”
- “用工程化的方法学习”
- “把努力留下痕迹，而不是只留在待办清单里”

## Layout pitfalls from the update

- Copy-only edits can still break the page. Longer Chinese text changed floating-card heights enough to overlap.
- Removing hero floating cards without changing the parent layout left the first screen visually unbalanced. Fix by converting the hero to a centered layout rather than just deleting the side DOM.
- Simplifying/removing sections can expose scroll animation assumptions. If `.reveal` content stays invisible or creates large blank gaps, set the relevant simplified sections to visible/static (`opacity: 1`, `transform: none`) or remove the reveal dependency.
- When reducing cards, remove both DOM and stale CSS/JS assumptions where possible; then verify the full scroll, not just the first viewport.

## Verification phrases and negative checks

Positive checks for the current style can include:

- `BUPT · Data · Builder`
- `GitHub: example-user`
- `github.com/example-user`

Negative checks should include:

- `北大`
- `PKU`
- `备考北大`
- `<exam-target>`
- duplicated mid-page GitHub mentions beyond the intended two placements
