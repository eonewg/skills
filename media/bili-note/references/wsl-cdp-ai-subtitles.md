# WSL Chrome CDP route for Bilibili AI subtitles

Use when Bili Note's public `/x/player/v2` probe shows no subtitle URL (often `need_login_subtitle: true` or empty `subtitles`), but the user's logged-in Chrome CDP profile is available on `127.0.0.1:9222` via `chrome-cdp` / `cdp-text`.

## When to use

- Public subtitles are missing or `subtitle_url` is empty.
- `web-access` proxy on `localhost:3456` is unavailable.
- A logged-in Bilibili tab can be opened in the WSL Chrome CDP profile.

Do not treat this as a failure of Bili Note. It is the preferred local workaround for the user's setup.

## Minimal workflow

```bash
skill=~/.hermes/skills/media/bili-note
work=~/.hermes/workspace/bili-note/<BVID>
archive=~/.hermes/data/bili-note/<BVID>_<short-title>
url='https://www.bilibili.com/video/<BVID>/'

# 1. First run the normal route. It captures metadata/comments and proves whether public subtitles exist.
python3 "$skill/scripts/run_bili_note.py" "$url" \
  --work-dir "$work" \
  --archive-dir "$archive" \
  --parts all \
  --subtitle-mode auto

# 2. Open the video in logged-in Chrome CDP.
cdp-text navigate "$url"
sleep 5

# 3. Ask the loaded Bilibili page to call the logged-in player subtitle API.
cat >/tmp/bili_fetch_subs.js <<'JS'
(async () => {
  const state = window.__INITIAL_STATE__ || {};
  const aid = state.aid || state.arc?.aid || state.videoData?.aid;
  const bvid = state.bvid || state.videoData?.bvid;
  const pages = state.videoData?.pages || state.pages || [];
  const p = pages[0];
  const ep = `https://api.bilibili.com/x/player/wbi/v2?bvid=${encodeURIComponent(bvid)}&cid=${encodeURIComponent(p.cid)}&aid=${encodeURIComponent(aid || '')}`;
  const r = await fetch(ep, {credentials: 'include'});
  const j = await r.json();
  return {aid, bvid, cid: p.cid, part: p.part, duration: p.duration, code: j.code, message: j.message, subtitles: j?.data?.subtitle?.subtitles || []};
})()
JS
cdp-text eval "$(cat /tmp/bili_fetch_subs.js)" >/tmp/bili_subs_eval.json
```

## Converting the CDP result into Bili Note archive inputs

After the `cdp-text eval`, parse `/tmp/bili_subs_eval.json`, choose the first subtitle object with `subtitle_url`, download it with Bilibili referer headers, and write these files under `$work`:

- `browser_ai_subtitles/p01_<cid>_ai-zh.subtitle.json`
- `browser_ai_subtitles/p01_<cid>_ai-zh.txt`
- `browser_ai_subtitles/p01_<cid>_ai-zh.srt`
- `browser_ai_subtitle_manifest.json`
- `browser_ai_subtitle_urls.json`

**Important manifest shape:** `archive_bili_materials.py` expects `browser_ai_subtitle_manifest.json` to be an object, not a bare list. Use this structure, matching the real output from `fetch_browser_ai_subtitles.py`:

```json
{
  "aid": 116347946144173,
  "bvid": "BVxxxx",
  "referer": "https://www.bilibili.com/video/BVxxxx/",
  "count": 1,
  "downloaded": 1,
  "outputs": [
    {
      "page": 1,
      "cid": 37245617754,
      "part": "Part title",
      "duration": 1402,
      "subtitle": {"lan": "ai-zh", "subtitle_url": "//aisubtitle..."},
      "files": {
        "json": "/abs/path/browser_ai_subtitles/p01_<cid>_ai-zh.subtitle.json",
        "txt": "/abs/path/browser_ai_subtitles/p01_<cid>_ai-zh.txt",
        "srt": "/abs/path/browser_ai_subtitles/p01_<cid>_ai-zh.srt",
        "line_count": 497
      }
    }
  ]
}
```

If you accidentally wrote a list and archive fails with `AttributeError: 'list' object has no attribute 'get'`, rewrite the manifest to the object shape above and rerun archive; do not re-fetch subtitles unless the files are missing.

Then re-run the archive step:

```bash
python3 "$skill/scripts/archive_bili_materials.py" \
  --extract-dir "$work" \
  --archive-dir "$archive"
```

The archive step should then report `subtitles.available: true`, `subtitle_lines`, `subtitle_chars`, `evidence_blocks`, and a usable `metadata/note_budget.json`.

## Pitfalls

- The top-level `cdp-text eval` output is wrapped like `{id,result:{result:{value: ...}}}`; extract the nested `value` object.
- Use `subtitle_url` from `/x/player/wbi/v2`, not the public probe's empty subtitle list.
- Normalize URLs beginning with `//` to `https://...` before downloading.
- Use `Referer: https://www.bilibili.com/video/<BVID>/` and a browser-like User-Agent when fetching the subtitle JSON.
- This route uses page credentials through `fetch(..., {credentials:'include'})`; do not read, print, or copy browser cookies.
- After writing the subtitle files, always re-run `archive_bili_materials.py` so indexes, evidence blocks, and `note_budget.json` reflect the new transcript.
