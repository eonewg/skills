---
name: static-site-operations
description: Maintain and deploy small static websites served from a Linux/Nginx server, including copy-editing personal homepages, safe backups, cache-busted verification, and visual QA.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [static-site, nginx, ssh, html, css, deployment, visual-qa]
---

# Static Site Operations

Use this skill when the user asks to inspect, edit, personalize, deploy, or verify a small static website hosted on a Linux server, especially a single-page personal homepage served by Nginx.

## Memory preflight

Before inspecting or changing the user's homepage/static site, route memory with:

```bash
~/.hermes/scripts/memory_route.py server
~/.hermes/scripts/memory_route.py project
```

Read the returned modules, normally `memory-modules/tools-memory.md`, `memory-modules/project-memory.md`, and `user-modules/workflow-profile.md`. They contain current SSH/server boundaries, GitHub Pages split-repo homepage facts, and the user's preference that server-impacting changes require explicit confirmation.

## Core workflow

1. **Inspect the live page before editing**
   - Fetch or open the public URL.
   - Use browser snapshot for content/structure and browser visual inspection for layout/style.
   - Identify whether the needed change is copy-only, layout/CSS, assets, or server config.

2. **Pull and understand the source file**
   - SSH/SCP the live HTML/CSS/assets to a local temp file or read them remotely.
   - Extract section text and headings before rewriting so edits preserve the existing design system.
   - Do not rewrite the whole site unless the user asked for a redesign; prefer targeted, style-preserving edits.

3. **Rewrite with the user's real identity and use-case in mind**
   - Avoid generic portfolio filler like “personal website / slowly growing / future projects” when the user has known concrete context.
   - Keep the page honest: real current work, real learning tracks, real projects, real contact paths.
   - For the user-style personal pages, prefer “learning operating system / public study archive / AI assistant workflow / long-term progress” over résumé boilerplate.
   - Do not assume every known life context belongs on the public homepage. If the user asks to remove a theme (for example an exam target), remove every visible trace and verify by searching the deployed page for the banned terms.
   - For the user's current homepage preference: keep the hero clean and centered; avoid right-side floating cards, bottom dock navigation, and repeated card grids unless explicitly requested. GitHub should be intentionally placed, not repeated across every section.
   - For the user's personal homepage redesigns, do not rush directly into edits when the ask is aesthetic/strategic. First research comparable personal sites/portfolio styles, synthesize a direction, then implement. Current preferred direction: “editorial / magazine-style personal page + serif/mono dual-font system + restrained whitespace” — use section kickers and magazine composition more than visible numbered indexes. Avoid oversized cinematic type or excessive hero whitespace: the initial hero should fit within the first viewport on common laptop/short browser heights; verify with browser measurements (`hero.bottom <= innerHeight`) and keep h1/h2 restrained. Language direction: do not add a global EN/ZH switch on the lightweight homepage yet; make it “中英气质兼容” instead — English provides structure/external-facing labels (nav, kickers, metadata, project labels), Chinese carries personality, concrete experience, and authentic body copy.
   - For minimalist content sections on the user's homepage, do not use visible "panel" styling unless explicitly requested: avoid tinted/gradient section backgrounds, outer borders, boxed frames, and card-like color blocks. Separate sections with whitespace, typography, and thin internal dividers only.
   - Do not leave the whole page in one font treatment. Establish a quiet typography system: display/serif-like treatment for hero and section headings, readable sans-serif for paragraphs, and mono/technical treatment for navigation, buttons, labels, or small metadata. Verify that computed fonts actually differ.
   - Avoid scroll reveal patterns that leave content hidden in full-page screenshots or when JavaScript timing fails; content should be visible by default, with animation as progressive enhancement only.
   - For the user's contact/footer area: keep the footer minimal (`© 2026 the user` and `↑ Top` only; no poetic motto). Align the visible `Say hi.` heading with the right-side contact copy's visual start, not merely the whole left column with its small kicker.
   - When changing static assets on GitHub Pages, cache-bust CSS/JS links (`style.css?v=<commit-or-change-id>`) before asking the user to refresh; GitHub Pages and browser caches can otherwise make fixed CSS appear unchanged.
   - the user wants `https://example-user.github.io/` to remain its own URL and `https://example.com/` to remain the custom-domain mirror with identical content. Do not bind the custom domain directly to `example-user/example-user.github.io`, because GitHub Pages redirects the github.io user site to the custom domain. Keep separate repos in sync instead: `example-user/example-user.github.io` for github.io and `example-user/example.com` for example.com.

4. **Validate locally before deploy**
   - Basic HTML parse check is enough for simple static HTML.
   - Search for expected key phrases in the generated file.
   - If text length changes, proactively review layout-sensitive CSS (floating cards, hero copy, nav labels, marquee items, mobile breakpoints).

5. **Backup before writing to the server**
   - Create a timestamped remote backup beside the live file, e.g. `index.html.bak-YYYYMMDD-HHMMSS`.
   - Then `scp` the new file into place.
   - If Nginx config was touched, run `nginx -t` before reload/restart. For pure HTML/CSS replacement, `nginx -t` is still a cheap sanity check but reload is usually unnecessary.

6. **Verify from the public URL, not just the remote filesystem**
   - Use a cache-busted URL such as `?v=YYYYMMDDHHMM`.
   - `curl` the public page and assert expected title/key phrases are present.
   - Open in browser and visually inspect the top sections.
   - Check browser console for JS errors.
   - For GitHub Pages custom domains, verify both content deployment and domain health separately: Pages can be `built` and serve new HTTP content while HTTPS certificate issuance is still pending.

7. **Fix visual regressions immediately**
   - Longer personalized copy often breaks previously balanced layouts.
   - Watch for overlapping floating cards, clipped hero text, nav label wrapping, oversized cinematic headings, and mobile breakpoint issues.
   - If removing major DOM blocks such as cards, docks, or hero sidebars, re-center the remaining composition instead of leaving the old two-column spacing behind.
   - Watch for overlapping floating cards, clipped hero text, nav label wrapping, oversized cinematic headings, and mobile breakpoint issues.
   - Also check whether "clean" sections accidentally still read as boxes because of subtle tinted backgrounds, gradient fills, outer borders, or excessive horizontal rules.
   - Check typography as a first-class visual dimension: headings, body text, nav/buttons, and labels should have distinct roles through font family, size, weight, letter spacing, and line height. Use browser computed styles when needed.
   - Treat animation as progressive enhancement only. Do not make important content depend on `opacity: 0` + JavaScript reveal; screenshots, slow JS, or failed observers can make the page look blank. Prefer content visible by default and add motion without hiding the base state.
   - Adjust CSS positions/widths/spacing/typography and redeploy, then re-verify visually.

## GitHub Pages custom domain workflow

When the homepage source is in `example-user/example-user.github.io`, treat GitHub as the source of truth and avoid editing the Baidu/Nginx mirror unless the user explicitly asks for mirror sync.

the user's preferred current layout is a split GitHub Pages setup:

```text
example-user/example-user.github.io  -> https://example-user.github.io/   # canonical editing source, no CNAME
example-user/example.com         -> https://example.com/          # custom-domain mirror, keeps CNAME=example.com
```

Why: if `CNAME` lives in `example-user.github.io`, GitHub Pages redirects `example-user.github.io` to the custom domain. Keeping the custom domain in a separate mirror preserves `github.io` as a stable fallback if `example.com` is not renewed later.

1. Clone or update the main repo with `gh repo clone example-user/example-user.github.io` / `git pull --ff-only`.
2. Do **not** add `CNAME` to `example-user.github.io`; `CNAME` belongs only in `example-user/example.com`.
3. Edit and commit the main repo first.
4. Sync the custom-domain mirror from the main repo:
   ```bash
   cd ~/.hermes/workspace/github/example-user.github.io
   ./scripts/sync-custom-domain-mirror.sh
   ```
   The script copies all source files to `../example.com`, preserves/writes `CNAME=example.com`, commits, pushes, and refuses to run if either repo has uncommitted changes.
5. Add canonical and share metadata when the public domain is known:
   - `<link rel="canonical" href="https://example.com/">`
   - basic Open Graph title/description/url/type.
6. After push/sync, wait for both GitHub Pages builds and verify cache-busted content:
   ```bash
   curl -fsSL 'https://example-user.github.io/?v=<sha>' | grep '<expected phrase>'
   curl -fsSL 'https://example.com/?v=<sha>' | grep '<expected phrase>'
   ```
7. Check Pages status for both repos:
   ```bash
   gh api repos/example-user/example-user.github.io/pages --jq '{status,cname,html_url,https_enforced}'
   gh api repos/example-user/example.com/pages --jq '{status,cname,html_url,https_certificate,https_enforced}'
   ```
8. If the mirror `https_certificate` is pending/null, do not claim HTTPS is fixed. Re-save the mirror domain to trigger issuance if needed:
   ```bash
   gh api --method PUT repos/example-user/example.com/pages -F cname='example.com'
   ```
   GitHub may return `The certificate does not exist yet` when enabling HTTPS; this means certificate issuance is pending, not that deploy failed.
9. Once `https_certificate` exists and `https_enforced` is false, enable HTTPS on the mirror:
   ```bash
   gh api --method PUT repos/example-user/example.com/pages -F cname='example.com' -F https_enforced=true
   ```
10. Probe with `curl -I https://example-user.github.io` and `curl -I https://example.com`; `example-user.github.io` should return `200`, not a `Location: example.com` redirect.

## Safety rules

- Read-only server inspection is fine when appropriate, but file modification, deletion, package installation, service restart, or long resource-heavy tasks should be treated as server-impacting work.
- Never expose secrets in page content, command output summaries, or skill references.
- Keep backups until the user confirms the new page is satisfactory or a normal cleanup policy exists.

## Rollback recipe

If the deployed page is wrong:

```bash
ssh <host> 'cp /var/www/html/index.html.bak-YYYYMMDD-HHMMSS /var/www/html/index.html && nginx -t'
```

Then verify the public URL again with a cache-busting query parameter.

## Verification checklist

- [ ] Live page inspected before edit.
- [ ] Existing file backed up with timestamp.
- [ ] New HTML/CSS deployed to the correct document root.
- [ ] Public URL returns expected title/key phrases.
- [ ] Browser visual check shows no obvious overlap, clipping, or layout breakage.
- [ ] Browser console has no JS errors.

## References

- `references/the user-personal-homepage.md` — the user's current static homepage deployment notes and personalization patterns captured from a real update session.
- `references/the user-minimal-homepage-visual-preferences.md` — the user-specific visual QA notes for avoiding tinted section bands, outer frames, repeated cards, and deploy retry pitfalls.
- `references/the user-homepage-split-domain.md` — Current GitHub Pages split-domain setup: `example-user.github.io` stays on the github.io URL, `example.com` is served from a mirror repo, plus cache-busting/contact/footer lessons.
