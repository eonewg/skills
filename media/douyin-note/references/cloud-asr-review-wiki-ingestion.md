# Cloud ASR → review → wiki ingestion pattern

Session-proven pattern for Douyin technical videos.

## Volcengine credential mapping

When the user provides Doubao/Volcengine ASR credentials in the old-console shape:

- `appid` → `VOLCENGINE_ASR_APP_KEY`
- `access token` → `VOLCENGINE_ASR_ACCESS_KEY`
- `secret key` → `VOLCENGINE_ASR_SECRET_KEY` (store for future signed APIs; current v3 flash HTTP path uses app/access key headers)

Store them in `~/.hermes/.env` with `0600` permissions. Dry-run should show `old_console_keys_present: true`; it is OK for `api_key_present` to remain false when using old-console credentials.

## Tested flash ASR flow

For an already prepared local MP3:

```bash
set -a
. ~/.hermes/.env
set +a

python3 ~/.hermes/skills/media/douyin-note/scripts/cloud_asr_transcribe.py \
  /path/to/audio.mp3 \
  --provider volcengine-flash \
  --language zh-CN \
  --out-dir /path/to/archive/cloud_asr_volcengine_flash_real
```

Expected successful response shape:

- `status_code: 20000000`
- `message: OK`
- `transcript.txt`, `transcript.md`, `utterances.json`, `cloud_asr_response.json`

## Mandatory review step

Do not write final notes from raw ASR directly. Run:

```bash
python3 ~/.hermes/skills/media/douyin-note/scripts/review_asr_transcript.py \
  --transcript /path/to/cloud_asr_volcengine_flash_real/transcript.txt \
  --utterances /path/to/cloud_asr_volcengine_flash_real/utterances.json \
  --metadata /path/to/archive/metadata/browser_video_detail.json \
  --out-dir /path/to/cloud_asr_volcengine_flash_real/reviewed
```

Use `reviewed/transcript_corrected.md` as the source for final notes. Keep `correction_report.json` as QA evidence.

Common AI-Agent technical corrections seen in this session:

- `Core Engine` → `Query Engine`
- `TOS` / `to` / `拓` in tool context → `Tools`
- `Hulk` → `Hook`
- `touch script` → `TypeScript`
- `luncheon` → `LangChain`
- `long graph` → `LangGraph`
- `cyclize` → `SQLite`

## Wiki archival shape

When the user explicitly says to archive a Douyin learning video to wiki:

1. Preserve raw evidence under `~/wiki/raw/transcripts/<topic>-<year>.md`.
2. Create or patch a formal concept page under `~/wiki/concepts/`.
3. Patch adjacent concept pages when the video strengthens an existing framework.
4. Update `index.md`, `hot.md`, `log.md`, `.manifest.json`.
5. Run `scripts/wiki_lint.py`, `scripts/wiki_v2_build.py`, semantic embedding rebuild when needed, and smoke-query the target terms.
6. Report both raw evidence path and formal concept path.

Do not confuse the working archive under `~/.hermes/workspace/douyin_note_runs/...` with wiki archival completion.