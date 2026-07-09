# Cloud ASR fallback for Bili Note

Use this when a Bilibili video has no usable official subtitle / AI subtitle, or the subtitle is too noisy to support a high-quality learning note.

## Decision rule

Bili Note should not replace B站字幕 with ASR by default. Use this order:

1. Official / public subtitles from B站 APIs.
2. Logged-in browser AI subtitle route when public subtitle metadata exists but `subtitle_url` is empty.
3. Cloud ASR fallback for missing/bad subtitles.
4. ASR review/correction pass: normalize obvious terminology errors against title, chapters, and glossary before writing the final note.
5. Local ASR fallback when no cloud key is configured or the content is privacy-sensitive.

## Preferred cloud route: Volcengine flash

For normal B站 learning videos, prefer Volcengine Doubao recorded-file flash HTTP when the audio is within limits:

- Duration <= 2 hours.
- File size <= 100MB after audio extraction/compression.
- Formats: WAV / MP3 / OGG OPUS.
- Endpoint: `POST https://openspeech.bytedance.com/api/v3/auc/bigmodel/recognize/flash`.
- Resource ID: `volc.bigasr.auc_turbo`.
- Supports local `audio.data` base64, so no public audio URL is required.

This is better than the standard submit/query API for ordinary Bili Note fallback because it avoids object storage/public URL setup and returns in one request.

## Command pattern

```bash
skill=~/.hermes/skills/media/bili-note
export VOLCENGINE_ASR_API_KEY='...'

uv run --with imageio-ffmpeg python "$skill/scripts/cloud_asr_transcribe.py" \
  "/path/to/bilibili_video_or_audio.mp4" \
  --provider volcengine-flash \
  --prepare-audio \
  --prepared-ext mp3 \
  --language zh-CN \
  --uid bili-note \
  --out-dir "/path/to/archive/cloud_asr_volcengine_flash"
```

Always dry-run first when using a new file or environment:

```bash
uv run --with imageio-ffmpeg python "$skill/scripts/cloud_asr_transcribe.py" \
  "/path/to/bilibili_video_or_audio.mp4" \
  --provider volcengine-flash \
  --prepare-audio \
  --prepared-ext mp3 \
  --language zh-CN \
  --uid bili-note \
  --out-dir "/path/to/archive/cloud_asr_volcengine_flash" \
  --dry-run
```

The dry-run verifies the prepared MP3 path, byte size, provider limits, output directory, and whether a Volcengine key is present. It does not call the API.

## Large-file insurance

`cloud_asr_transcribe.py` has split insurance built in:

- `--auto-split` is enabled by default for local `volcengine-flash` input.
- If the prepared MP3 exceeds the provider byte limit, the script creates `chunks_audio/chunk_*.mp3`, transcribes each chunk separately, then merges `transcript.txt`, `transcript.md`, and offset-adjusted `utterances.json`.
- Default chunk size is `--chunk-seconds 1800`; tune it for provider stability or force a test with `--force-split`.
- Dry-run also exercises splitting when `--force-split` is set, so use it to verify chunk count and chunk sizes before spending API calls.

Example split test:

```bash
uv run --with imageio-ffmpeg python "$skill/scripts/cloud_asr_transcribe.py" \
  "/path/to/bilibili_video_or_audio.mp4" \
  --provider volcengine-flash \
  --prepare-audio \
  --prepared-ext mp3 \
  --language zh-CN \
  --uid bili-note \
  --force-split \
  --chunk-seconds 1800 \
  --out-dir "/path/to/archive/cloud_asr_volcengine_flash" \
  --dry-run
```

## Standard API fallback

Use `volcengine-standard` only when:

- audio is longer than the flash limit;
- the user already has a public audio URL;
- async submit/query or callback is needed;
- flash fails due to size/concurrency/provider overload.

Standard mode requires `audio.url`; do not expect it to upload local files directly.

## Output integration

The cloud ASR script writes:

- `cloud_asr_config.json`
- `cloud_asr_response.json`
- `volcengine_flash_request.json` with base64 data redacted
- `volcengine_flash_response.json`
- `chunks_audio/chunk_*.mp3` and `split_audio.json` when split insurance is triggered
- `chunk_responses/chunk_*/` and `chunk_results_manifest.json` after chunked real API calls
- `transcript.txt` when `result.text` exists
- `transcript.md`
- `utterances.json` when returned

When incorporating into a Bili Note archive, first run `review_asr_transcript.py`, then treat `reviewed/transcript_corrected.md` / `reviewed/utterances_corrected.json` like subtitle fallback material and still record coverage and limitations in the final note.

Review command:

```bash
python "$skill/scripts/review_asr_transcript.py" \
  --transcript "/path/to/archive/cloud_asr_volcengine_flash/transcript.txt" \
  --utterances "/path/to/archive/cloud_asr_volcengine_flash/utterances.json" \
  --metadata "/path/to/archive/metadata/video_detail.json" \
  --out-dir "/path/to/archive/cloud_asr_volcengine_flash/reviewed"
```

The review step writes:

- `reviewed/transcript_corrected.txt`
- `reviewed/transcript_corrected.md`
- `reviewed/utterances_corrected.json`
- `reviewed/correction_report.json`

## Pitfalls

- Do not run cloud ASR before trying official / AI subtitles; it wastes money and can be less accurate than platform subtitles.
- Do not store raw base64 audio in reference files or notes. Keep only redacted request JSON and the prepared MP3. Configure credentials via env vars: `VOLCENGINE_ASR_API_KEY` for new console, or `VOLCENGINE_ASR_APP_KEY` + `VOLCENGINE_ASR_ACCESS_KEY` for old console. `VOLCENGINE_ASR_SECRET_KEY` is only for future signed APIs and is not used by the current v3 ASR HTTP header flow.
- For technical videos, pass `--context` with important terms if needed, then still validate terminology against video title, chapters, visible context, and comments.
- For videos over 2 hours, split audio or use standard async mode; do not force flash.