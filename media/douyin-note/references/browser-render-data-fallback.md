# Browser RENDER_DATA fallback for Douyin

Use this when `yt-dlp` fails on a Douyin URL with `Fresh cookies are needed`, even when `--cookies-from-browser chrome` is supplied.

## Proven case

Input: `https://v.douyin.com/cu4aZGO8ko0/`

`yt-dlp` resolved the aweme id but failed metadata and download with fresh-cookie errors. Browser navigation to the SSR modal page succeeded:

```text
https://www.douyin.com/jingxuan?modal_id=7648892907285417268
```

The page contained `script#RENDER_DATA` with `app.videoDetail`, including title, author, stats, chapters, and `video.bitRateList[].playAddr` MP4 URLs. The first 1080p SSR playAddr downloaded successfully with curl to a 48,440,571 byte MP4.

## Steps

1. Extract aweme id from the URL or from yt-dlp's error line.
2. Open the SSR page in the browser:

```text
https://www.douyin.com/jingxuan?modal_id=<aweme_id>
```

3. In page JS, read the render data:

```js
const j = JSON.parse(decodeURIComponent(document.getElementById('RENDER_DATA').textContent));
const v = j.app.videoDetail;
```

4. Save selected fields:

- `v.awemeId`
- `v.itemTitle`
- `v.desc`
- `v.authorInfo`
- `v.stats`
- `v.chapterInfo.list`
- `v.video.duration`
- `v.video.bitRateList`

5. Choose a play URL:

```js
v.video.bitRateList?.[0]?.playAddr?.[0]?.src || v.video.playAddr?.[0]?.src
```

6. Download with browser-like headers:

```bash
curl -L --fail --retry 2 \
  -A 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36' \
  -e 'https://www.douyin.com/jingxuan?modal_id=<aweme_id>' \
  -o 'media/<aweme_id>.mp4' '<playAddr src>'
```

7. Verify:

```bash
file 'media/<aweme_id>.mp4'
sha256sum 'media/<aweme_id>.mp4'
wc -c 'media/<aweme_id>.mp4'
```

## ASR fallback without system ffmpeg

If WSL has no `ffmpeg` / `ffprobe`, `faster-whisper` can still transcribe the MP4 through PyAV:

```bash
uv run --with faster-whisper python transcribe_faster_whisper.py
```

For the proven case, `faster-whisper base`, CPU int8, transcribed a 19m44s MP4 in about 129 seconds and produced 674 segments. Expect term errors on technical English words; correct terms against the video context and chapter list.

## Pitfalls

- Direct `urllib` page fetch may not include `RENDER_DATA`; browser navigation did. Use the browser tool/CDP when plain HTTP gets a generic page.
- The playAddr URLs expire. Download immediately after extraction.
- Chapter info is not a full transcript; use it for structure, then run ASR for full notes.
- Do not expose cookies. This route uses page-rendered SSR data and browser-like headers, not printed cookie values.
