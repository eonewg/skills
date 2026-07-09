# Chrome CDP for Zhihu research calibration

> **2026-06-20 alternative**: For structured Zhihu searches (title + summary + metadata), prefer the `zhihu-search` skill — API-based, no browser needed, returns structured JSON with vote/comment counts in ~5s. Use CDP only when you need **full article body text** that the API doesn't return.
>
> **CDP approach** (replaces Kimi WebBridge extension which has a confirmed `currentWindow`/`tabs` runtime bug on Chrome 148 + WSLg):
> - Launch: `chrome-cdp [URL]`
> - Extract: `cdp-text text [URL]`
> - CDP port: 9222, profile at `~/.config/google-chrome-cdp`
>
> Keep the Kimi WebBridge flow (via `http://127.0.0.1:10086/command`) as a fallback reference for when/if the extension bug is resolved. See `references/kimi-webbridge.md`.

Use CDP when logged-in browsing is needed for Chinese social-platform research (Zhihu, XiaoHongShu, ChatGPT) and normal browser/search tools risk losing login state, dates, comments, or ranking.

## Minimal verified flow

1. Launch the dedicated Chrome profile with CDP:

```bash
chrome-cdp [URL]  # or just chrome-cdp to start browser without navigation
```

Wait ~3 seconds for Chrome to start and CDP port to open.

2. Extract page text:

```bash
cdp-text text [URL]   # Navigate and extract title + body text
cdp-text text         # Read text from current page (no navigation)
cdp-text list         # List open pages
cdp-text navigate <URL>  # Navigate to URL without extracting
cdp-text eval 'document.title'  # Run arbitrary JS
```

The CDP helper script (`~/.local/bin/cdp-text`) uses Python `websockets` to communicate with Chrome DevTools Protocol on `127.0.0.1:9222`.

## Batch extraction pattern (Zhihu search results)

When the user gives short Chinese keywords (e.g. `南软`, `软微`, `科软`) and wants to search directly:

```bash
SEARCH_URL="https://www.zhihu.com/search?type=content&q=$(python3 -c 'import urllib.parse; print(urllib.parse.quote(input()))' <<< '南软')"
chrome-cdp "$SEARCH_URL"

# Check search results
cdp-text eval '
(() => {
  const anchors = [...document.querySelectorAll("a[href*=\"zhihu.com\"]")];
  return anchors.slice(0, 12).map(a => ({title: a.innerText?.trim()?.slice(0,100), href: a.href}));
})()
'
```

Do **not** silently add qualifiers like `考研`, `408`, `经验贴` before the first pass; those can hide native high-signal results.

For full article body extraction, open each selected post in sequence (one at a time to avoid tab state loss):

```bash
cdp-text text 'https://zhuanlan.zhihu.com/p/XXXXX'
# Save output to /tmp/zhihu_article_XXXXX.json
```

Then close tabs between posts if needed via CDP.

## Evidence discipline

- Do not say CDP was used unless the run actually went through port 9222 and page state was extracted from the real Chrome instance.
- Record the query, page title, and a few extracted result titles/snippets in the task artifact (`RESOURCES.md`, research notes, or final summary).
- Track partial success explicitly: distinguish **candidate URLs found**, **articles opened**, and **full bodies extracted**. If a batch finds 8 candidates but only 2 bodies are extracted, say exactly that.
- When one article succeeds outside the main batch, save it as its own temp/artifact file, then mention the exact path(s) in the final summary.
- For long Zhihu/Zhuanlan articles, prefer CDP DOM extraction into JSON/text files over screenshots; quote only short, task-relevant excerpts and summarize the rest.
- Ordinary `web_search`, Tardis pages, and Hermes `browser_*` tools are fallback/cross-check paths, not substitutes, when the user expects logged-in browsing.