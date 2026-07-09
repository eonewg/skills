# Cloud ASR providers for douyin-note

Use this reference when a downloaded Douyin MP4 needs cloud transcription instead of local `faster-whisper`.

## Default route: SiliconFlow SenseVoice

SiliconFlow exposes an OpenAI-style multipart endpoint:

```text
POST https://api.siliconflow.cn/v1/audio/transcriptions
Authorization: Bearer $SILICONFLOW_API_KEY
multipart/form-data:
  file=@audio.m4a
  model=FunAudioLLM/SenseVoiceSmall
```

Documented model options include:

- `FunAudioLLM/SenseVoiceSmall`
- `TeleAI/TeleSpeechASR`

Documented upload limits:

- duration not exceeding 1 hour
- file size not exceeding 50MB

For Douyin MP4s, prefer preparing audio first:

```bash
skill=~/.hermes/skills/media/douyin-note
archive=~/.hermes/workspace/douyin_note_runs/<run>

uv run --with imageio-ffmpeg python "$skill/scripts/cloud_asr_transcribe.py" \
  "$archive/media/<aweme_id>.mp4" \
  --provider siliconflow \
  --prepare-audio \
  --out-dir "$archive/cloud_asr_siliconflow" \
  --dry-run
```

If dry-run reports `api_key_present: false`, set:

```bash
export SILICONFLOW_API_KEY='...'
```

Then rerun without `--dry-run`.

## Volcengine Doubao flash recorded-file HTTP

对 douyin-note 来说，火山优先接“录音文件极速版识别 HTTP”，不是标准版。

Why:

- 抖音/短视频笔记通常小于 2 小时，符合极速版限制。
- 极速版一次请求即返回结果，不需要 submit/query 轮询。
- 极速版支持 `audio.data` base64，本地 MP3 可以直接请求；不需要先上传到公网 URL。
- 返回体包含 `result.text`、`result.utterances`、字级 `words`，够做笔记、分句和时间戳。

Limits from docs:

- duration <= 2 hours
- file size <= 100MB
- formats: WAV / MP3 / OGG OPUS
- resource id: `volc.bigasr.auc_turbo`
- endpoint: `POST https://openspeech.bytedance.com/api/v3/auc/bigmodel/recognize/flash`

Recommended command:

```bash
skill=~/.hermes/skills/media/douyin-note
archive=~/.hermes/workspace/douyin_note_runs/<run>

uv run --with imageio-ffmpeg python "$skill/scripts/cloud_asr_transcribe.py" \
  "$archive/media/<aweme_id>.mp4" \
  --provider volcengine-flash \
  --prepare-audio \
  --prepared-ext mp3 \
  --language zh-CN \
  --out-dir "$archive/cloud_asr_volcengine_flash" \
  --dry-run
```

Then set `VOLCENGINE_ASR_API_KEY` and rerun without `--dry-run`. The script writes request JSON with base64 data redacted, so transcript archives do not balloon with duplicated audio payload.

Post-ASR review is mandatory before final output. After any cloud/local ASR succeeds, run `review_asr_transcript.py` against the raw transcript, utterances, and metadata/chapters:

```bash
python "$skill/scripts/review_asr_transcript.py" \
  --transcript "$archive/cloud_asr_volcengine_flash/transcript.txt" \
  --utterances "$archive/cloud_asr_volcengine_flash/utterances.json" \
  --metadata "$archive/metadata/browser_video_detail.json" \
  --out-dir "$archive/cloud_asr_volcengine_flash/reviewed"
```

Use `reviewed/transcript_corrected.md` / `reviewed/utterances_corrected.json` as the source for final notes. Keep `correction_report.json` to show which terminology rules fired. This pass is conservative: correct obvious technical ASR errors using metadata/chapters/glossary; do not invent missing content.

Insurance for large files:

- `--auto-split` is enabled by default for local `volcengine-flash` input.
- If the prepared local audio exceeds the provider byte limit, the script splits it under `chunks_audio/`, transcribes each chunk separately, then merges `transcript.txt`, `transcript.md`, and offset-adjusted `utterances.json`.
- Tune chunk size with `--chunk-seconds 1800`; force a split test with `--force-split`.
- For files over 2 hours, prefer standard版 or explicit chunking; flash docs cap single-request duration at 2 hours.

Use standard版 only when:

- audio is longer than 2 hours
- you already have a public audio URL and prefer async submit/query
- you need callback workflow
- flash endpoint fails because of size/concurrency/server overload

## Volcengine Doubao recorded-file standard HTTP

火山“录音文件识别标准版HTTP”是异步 submit + query，不是 multipart 本地上传：

```text
POST https://openspeech.bytedance.com/api/v3/auc/bigmodel/submit
POST https://openspeech.bytedance.com/api/v3/auc/bigmodel/query
```

New console headers:

```text
X-Api-Key: $VOLCENGINE_ASR_API_KEY
X-Api-Resource-Id: volc.seedasr.auc
X-Api-Request-Id: <uuid>
X-Api-Sequence: -1   # submit only
```

Old console headers are also supported by the script if these env vars are present:

```bash
export VOLCENGINE_ASR_APP_KEY='...'
export VOLCENGINE_ASR_ACCESS_KEY='...'
```

Resource IDs from the docs:

- Model 1.0: `volc.bigasr.auc`
- Model 2.0: `volc.seedasr.auc`  ← default

The standard API requires `audio.url`; local files must first be converted/compressed and uploaded to a publicly reachable HTTPS URL. Use `--prepare-audio --prepared-ext mp3` to create a doc-compatible MP3:

```bash
skill=~/.hermes/skills/media/douyin-note
archive=~/.hermes/workspace/douyin_note_runs/<run>

uv run --with imageio-ffmpeg python "$skill/scripts/cloud_asr_transcribe.py" \
  "$archive/media/<aweme_id>.mp4" \
  --provider volcengine-standard \
  --prepare-audio \
  --prepared-ext mp3 \
  --audio-url 'https://your-public-host/audio.mp3' \
  --language zh-CN \
  --out-dir "$archive/cloud_asr_volcengine" \
  --dry-run
```

After uploading the generated MP3 and setting the key, run without `--dry-run`:

```bash
export VOLCENGINE_ASR_API_KEY='...'

python "$skill/scripts/cloud_asr_transcribe.py" \
  'https://your-public-host/audio.mp3' \
  --provider volcengine-standard \
  --audio-format mp3 \
  --language zh-CN \
  --out-dir "$archive/cloud_asr_volcengine"
```

Default request settings:

- `model_name`: `bigmodel`
- `enable_itn`: true
- `enable_punc`: true
- `enable_ddc`: false
- `show_utterances`: true, so timestamps can be saved when returned

Optional hotwords/context can be passed through `--context`. For technical videos, put domain terms there, for example `Tools, Skills, Memory, Context, Permission, Subagent, Sessions, Command, Hook, Query Engine, Claude Code, LangChain, LangGraph`.

## Generic OpenAI-compatible route

For providers that implement multipart `/audio/transcriptions`, use:

```bash
python "$skill/scripts/cloud_asr_transcribe.py" audio.m4a \
  --provider openai-compatible \
  --endpoint 'https://provider.example/v1/audio/transcriptions' \
  --model 'provider-asr-model' \
  --api-key-env PROVIDER_API_KEY \
  --out-dir cloud_asr_provider
```

The script writes:

- `cloud_asr_config.json`
- `cloud_asr_response.json`
- `transcript.txt` when the response contains a `text` field
- `transcript.md` when text extraction succeeds
- for Volcengine: `volcengine_submit_request.json`, `volcengine_submit_response.json`, `volcengine_query_*.json`, `volcengine_query_final.json`, and `utterances.json` when available

## DashScope Paraformer note

DashScope Paraformer recorded-file recognition is not the same shape as OpenAI multipart upload. It uses an async task API and expects HTTP/HTTPS file URLs:

```text
POST https://dashscope.aliyuncs.com/api/v1/services/audio/asr/transcription
Authorization: Bearer $DASHSCOPE_API_KEY
X-DashScope-Async: enable
JSON body with model=paraformer-v2 and input.file_urls=[...]
```

So do not point `cloud_asr_transcribe.py` directly at DashScope unless it is extended with a URL-upload/async polling adapter. For local files, either upload the audio to a reachable object store first or use a provider that accepts multipart file upload.

## Provider choice

- Default cloud route for Douyin/Bili-style media notes: Volcengine flash (`volcengine-flash`) when the prepared audio is <= 2 hours / <= 100MB, because it accepts local base64 and returns in one request.
- Fast local draft: `faster-whisper base` CPU.
- Higher-quality local final / privacy-sensitive path: `faster-whisper large-v3` CUDA.
- Cloud comparison / Chinese ASR baseline: SiliconFlow `FunAudioLLM/SenseVoiceSmall`.
- 火山标准版：适合已有公网音频 URL、需要异步 submit/query、需要 `show_utterances` 和上下文热词的场景。
- Long files or batch async workflows: first use flash chunking (`--auto-split` / `--force-split`); use DashScope Paraformer or Volcengine standard only when async URL workflow is actually better.

## Pitfalls

- Volcengine standard HTTP does not upload local files directly; it needs a URL. Do not pass a local path without `--audio-url` and expect it to upload.
- For Volcengine, use MP3/WAV/OGG/raw-compatible audio URLs. The docs list `raw / wav / mp3 / ogg`; create MP3 for safest compatibility.
- Do not upload the full MP4 if it is close to provider size limits; use `--prepare-audio` to create compact audio first.
- Do not save API keys in the skill directory or transcript outputs. Use env vars; for Volcengine ASR, prefer `VOLCENGINE_ASR_API_KEY` for new console or `VOLCENGINE_ASR_APP_KEY` + `VOLCENGINE_ASR_ACCESS_KEY` for old console. `VOLCENGINE_ASR_SECRET_KEY` may be stored for future signed APIs but is not used by the current v3 ASR HTTP headers.
- Some cloud ASR responses return only plain `text`, no segment timestamps. Keep local `faster-whisper` outputs if timestamps matter.
- If cloud ASR and local ASR disagree on technical terms, check video chapters and visible context before writing the final note.