# the user homepage split-domain deployment

Current intended shape:

- `example-user/example-user.github.io` serves `https://example-user.github.io/` and must not have a `CNAME` file or GitHub Pages custom domain.
- `example-user/example.com` serves `https://example.com/` and keeps `CNAME` containing `example.com`.
- Both repos carry the same static site content; edit the github.io source first, then sync to the custom-domain mirror.

Why this split exists:

GitHub Pages redirects a user site (`example-user.github.io`) to its custom domain when the custom domain is attached to that same repository. the user specifically wants entering `example-user.github.io` to keep the github.io URL, while `example.com` also works as the personal domain. Separate Pages repos are the reliable fix.

Recommended workflow for future homepage edits:

1. Clone/update `example-user/example-user.github.io`.
2. Edit and verify locally.
3. Cache-bust CSS/JS links when changing layout or scripts, e.g. `style.css?v=<commit-or-change-id>`.
4. Commit and push `example-user/example-user.github.io`.
5. Sync the same content into `example-user/example.com`, preserving its `CNAME` file.
6. Commit and push `example-user/example.com`.
7. Verify both URLs independently:
   - `curl -I https://example-user.github.io` should return `200`, no `Location:` redirect.
   - `curl -I https://example.com` should return `200` with HTTPS enforced.
   - Browser check should confirm the visible URL remains whichever address was entered.

Visual preferences captured from the correction session:

- Footer should stay minimal: `© 2026 the user` and `↑ Top`; do not add the motto `一蓑烟雨任平生。`.
- In the Contact section, aligning the entire left column is not enough because the `CONTACT` kicker pushes `Say hi.` downward. Align the visible `Say hi.` heading with the right-side paragraph's visual start. In the current CSS this used a small negative margin on `.contact-section .section-shell > div:first-child`.
- If the user says a fix is still not visible, suspect stale CSS first and inspect the loaded stylesheet URL in the browser before reworking the design.
