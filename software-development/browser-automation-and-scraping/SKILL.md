---
name: browser-automation-and-scraping
description: Unified guidance for browser automation, cloud/browser-session orchestration, anti-bot scraping, and web interaction tooling. Use when an agent needs to navigate websites, automate clicks/forms, manage browser sessions, or scrape dynamic pages with browser-based tools.
---

# Browser Automation and Scraping

## Overview
This umbrella skill consolidates browser control, hosted browser sessions, and specialized scraping workflows.

## Core workflow
1. Decide whether the task is simple scraping, interactive automation, or long-lived browser-session management.
2. **For structured Zhihu searches** (title + summary + metadata): use the `zhihu-search` skill via API — fast, no browser needed, structured JSON output. Full article body extraction still requires the CDP browser approach.
3. **For X/Twitter original posts and search results**, prefer CDP logged-in browsing when the task is “read X original text” or “search what people say on X”. X API/MCP may authenticate successfully but still fail on search/bulk read due to API credits or product-tier limits; do not keep retrying API search unchanged. Use `chrome-cdp '<x.com URL>'` with the user's logged-in Chrome profile, verify `http://127.0.0.1:9222/json/list` shows the intended X page, then run `cdp-text text` (or `cdp-text text '<URL>'`) to extract `document.body.innerText`. For a concrete post URL, `xurl read <url>` can be tried first, but CDP is the default fallback and the preferred route for webpage search/timeline/comment context.
4. If the site depends on the user's real login/session state or blocks isolated browsers (Cloudflare/SSO/2FA), prefer the **CDP approach** on the user's WSL setup: launch Chrome with the dedicated cloned profile via `chrome-cdp [URL]`, then extract content via `cdp-text text [URL]` (both on port 9222). This bypasses the Kimi WebBridge extension's known `currentWindow`/`tabs` runtime bug on Chrome 148 + WSLg. If Kimi WebBridge is explicitly requested, start/check the daemon and verify `extension_connected:true`, but be aware it may return `No current window` — in that case switch to CDP. Do **not** substitute Hermes `browser_*` tools, ordinary `web_search`, or headless browsers when the user expects logged-in browsing; report the connector blocker instead of silently using a synthetic fallback.
5. Prefer the lightest browser tool that can complete the task.
4. Escalate to anti-bot or hosted-browser approaches only when basic automation is insufficient.
5. Capture snapshots or extracted outputs as verification artifacts.

## Consolidated subsections
### Local browser automation
Interactive navigation, clicking, typing, and structured snapshots.

### Visual QA for deployed static pages
When a task changes website copy/layout and deploys it, do not stop at `curl` or DOM text checks. Open the public URL with a cache-busting query string (for example `?v=YYYYMMDDHHMM`), take a visual screenshot, and check browser console errors. Longer personalized text often causes layout regressions that text-only verification misses: overlapping floating cards, clipped hero headlines, nav wrapping, and broken spacing. If a visual issue appears, fix CSS spacing/positions and re-verify before reporting success.

When the user asks to make the rest of a personal/static page match the “first screen” or “clean hero” style, treat it as a design-system propagation task, not just copy editing:
- remove or relocate decorative hero-side cards instead of merely repositioning them;
- move useful card content into the next semantic section (`status`, `about`, etc.);
- remove floating bottom docks if they compete with the clean hero language or obscure content; keep the top nav as the primary navigation unless the user explicitly wants dock-style UI;
- verify both the first viewport and at least one scrolled viewport, because reveal animations and fixed/floating elements can look fine in DOM/curl checks but fail visually after scroll.

See `references/static-personal-site-visual-refactor.md` for a compact example workflow and pitfalls from a deployed personal homepage refactor.

### Hosted or cloud browser sessions
Use persistent/remote sessions when login state, profiles, or long-lived automation matters.

### Scraping hard targets
Use specialized scraping flows only for dynamic or anti-bot-protected pages.

### JS-rendered data hidden from a11y tree
Many Chinese web apps render table data via JavaScript after page load. The a11y tree snapshot from `browser_navigate`/`browser_snapshot` may show **"No Data"** even though the data exists in the DOM.

**Check first with `browser_console` before trusting "No Data":**
```js
// If the a11y tree shows "No Data", check actual DOM content
document.body.innerText
// or extract specific table rows
document.querySelectorAll('table')[1]?.rows
```

This reveals data that's rendered but not exposed to the accessibility tree. The a11y tree in `browser_snapshot` often lags behind or omits JS-injected children in SPA table implementations.

**Pitfall**: Don't give up after seeing "No Data" in the snapshot. If the page title and structure clearly show a data table (headers visible, pagination indicators), use `browser_console` to probe the DOM before concluding there's nothing to extract.

### Data table extraction (paginated)
When extracting data from a table spanning multiple pages:

1. **First, check for pagination controls** — look for "page 2", "下一页", numbered list items, or any element showing "1 2 3" at the bottom of the table area. Visual inspection via `browser_vision` or checking `document.body.innerText` for page indicators helps.

2. **Try `browser_click` on the visible page ref first** — some sites expose page buttons as clickable ref elements. If clicking produces no change (same table rows), the page may use client-side rendering where data never leaves the DOM — proceed to step 3 using `browser_console`.

3. **Use `browser_console` with JS for stubborn pagination** — many SPA tables don't expose page buttons as accessible refs. Use a direct DOM selector click:
   ```js
   document.querySelector('li[aria-label="page 2"]').click()
   ```
   Or look for the active page indicator after clicking to confirm the page switched:
   ```js
   document.querySelector('.is-active')?.innerText
   ```

4. **Read the new page's table content** via `browser_console` expression that extracts visible table rows:
   ```js
   (async () => {
     await new Promise(r => setTimeout(r, 800));
     let rows = document.querySelectorAll('table')[1]?.rows;
     // ... extract cell text from each row
   })()
   ```

5. **Continue iterating** — check if a "next page" or next-number page element exists and is not disabled. Repeat until no more pages.

**Pitfall**: Don't assume all data is on page 1 just because the initial snapshot shows a full table. If you see numbered page indicators ("1 2"), always check page 2. The user will correct you if you miss data, but it's better to be thorough on the first pass.

### Broad web reach integrations
Use ecosystem-specific expansion only when the task spans many external content sources.

## Absorbed specialized skills
- `Agent Browser` — local structured browser automation CLI.
- `browser-use` — cloud/persistent browser sessions.
- `playwright-scraper-skill` — anti-bot scraping recipes.
- `agent-reach` — broader web/content-source reach integrations.
- `Kimi WebBridge` — real browser control via local daemon + Chrome/Edge extension (user's actual login sessions). **Known limitation on this WSL setup**: Chrome 148 + Kimi WebBridge v1.10.0 has a `currentWindow`/`tabs` runtime bug. The CDP fallback (`chrome-cdp` + `cdp-text`) is the reliable alternative for logged-in browsing. See `references/kimi-webbridge.md`; for Zhihu research workflows see `references/chrome-cdp-zhihu-research.md` (CDP preferred, Kimi extension steps kept as reference in `kimi-webbridge.md`).

## Common pitfalls
- Overusing heavy browser stacks for pages that simple fetch/search can handle.
- Failing to verify extracted content after automation.
- Jumping to anti-bot workflows too early.

## Verification checklist
- [ ] Browser automation is actually required.
- [ ] Session strategy matches the site complexity.
- [ ] Extracted result was verified from page state or saved output.
