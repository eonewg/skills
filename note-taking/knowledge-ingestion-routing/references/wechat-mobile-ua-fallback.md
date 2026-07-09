# WeChat article mobile-User-Agent fallback

Use when `web_extract` cannot access `mp.weixin.qq.com` and the local extractor is unavailable, its venv is stale, or Camoufox/browser download is slow/risk-gated.

## Pattern

1. Try the normal local extractor first:
   `~/.hermes/scripts/wechat_article_to_md.sh '<URL>'`
2. If it fails for environment/setup reasons, do **not** conclude the article is inaccessible. Fetch the URL directly with a WeChat-like mobile User-Agent:

```python
import html, json, re, urllib.request
url = 'https://mp.weixin.qq.com/s/...'
headers = {
  'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.50 NetType/WIFI Language/zh_CN',
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
  'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
  'Referer': 'https://mp.weixin.qq.com/',
}
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=30) as r:
    html_text = r.read().decode('utf-8', 'ignore')
```

3. Extract metadata from JavaScript variables when present:
   - `msg_title`
   - `nickname`
   - `ct`
   - `msg_desc`
   - `msg_cdn_url`
   - `user_name`
4. Extract body from `id="js_content"`, converting paragraph/section breaks to newlines, stripping tags, and `html.unescape`-ing text.
5. Save the fallback copy under `~/.hermes/data/wechat-articles/_raw-html/<article-id>.html` and `.txt` for summarization and later archive verification.
6. If the local extractor repair caused a large partial Camoufox/browser download or broken venv backup, clean only those temporary artifacts after the article text is safely saved.

## User-facing behavior

Follow confirm-first ingestion: summarize the article and ask whether to archive. Do not write wiki pages until the user explicitly confirms.

## Pitfalls

- Browser navigation may land on `wappoc_appmsgcaptcha` / “环境异常”; mobile-UA direct fetch can still return the real article HTML.
- A broken extractor venv is setup state. Capture the fallback/rebuild pattern, not a durable claim that the extractor is broken.
- Avoid downloading a 700MB browser just to summarize a link if the mobile-UA fallback works. If the normal extractor starts a large Camoufox download and fails or times out, switch to this fallback and clean only the partial cache after the article text is safely saved. Practical threshold: once logs show a fresh `Downloading package: ...camoufox...` and progress is slow, stop waiting for the full browser; use the mobile UA extractor, then verify/save the `.txt` body and remove `~/.cache/camoufox` only after the text is safely captured.
- Mobile-UA extraction can return mojibake for JavaScript metadata (`msg_title`, `nickname`) while the article body is readable. Do not trust garbled metadata blindly; repair title/author from the body, URL context, visible article text, or `<meta property="og:title">` / `<meta name="twitter:title">` before writing raw frontmatter. If a regex overcaptures escaped HTML into `nickname` or another JS variable, discard that field rather than preserving garbage metadata.
- For low-signal WeChat “夜读/鸡汤” pieces that the user still says to archive, use light ingestion: preserve full raw article, patch one existing umbrella concept (often `long-term-life-strategy`, `personal-daily-dashboard`, `self-worth-and-action`, `social-speech-boundary-checklist`, or adjacent personal-operating-system page), update `hot.md`/`log.md`/manifest, and verify with lint + build + a query that should retrieve the umbrella page. Do not create a narrow concept page just because the link was archived.
- When using a local deterministic ingestion script for this fallback, delete the temporary script after successful lint/build/query verification. If `wiki_lint.py` reports a raw hash mismatch for the newly written file, update the raw frontmatter and `.manifest.json` to the linter-reported actual hash, then rerun lint until both `issue_count` and `warning_count` are 0.
- If wrapping the extractor with `timeout ... | tail`, remember pipelines can mask the timeout exit status unless `set -o pipefail` is active. Prefer direct execution, or run under `bash -o pipefail -c 'timeout ... 2>&1 | tail -80'` when you need clipped logs.
