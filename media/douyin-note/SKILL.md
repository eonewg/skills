---
name: douyin-note
description: Use when extracting, archiving, transcribing, or summarizing Douyin/TikTok China short-video, image-note, gallery, share-link, or local downloaded media into reusable Markdown notes. Handles Douyin-specific parsing routes, fallback downloaders, local-file fallback, metadata capture, audio extraction, and note-writing verification.
version: 0.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [douyin, media, transcription, notes, downloader]
    related_skills: [media-ingestion-and-transcription, yt-dlp-downloader, bili-note]
---

# Douyin Note

## Overview

把抖音分享链接、公开视频、图文作品、已经下载到本地的视频，整理成可追溯的材料包和 Markdown 笔记。它不是 Bili Note 的替代品：B站仍走 `bili-note`；抖音内容走本 skill。

抖音的网页接口变化快，默认采用“多路线、先验证、可降级”的方式：先尝试轻量解析和下载，失败时保留错误证据并提示下一条可走路线；不要把只拿到标题/封面/文案的内容说成完整转写。

## When to Use

使用本 skill，当用户给出：

- 抖音短链，例如 `https://v.douyin.com/...`。
- 抖音长链，例如 `https://www.douyin.com/video/...`、`/note/...`、`/gallery/...`、`/user/...`。
- 用户从抖音下载好的本地视频或图集目录。
- “提取抖音文案”“整理抖音视频笔记”“归档这个抖音”“抖音评论/图文/视频解析”等需求。

不要用于：

- B站视频、图文、动态：用 `bili-note`。
- YouTube 或普通网页视频：先走 `media-ingestion-and-transcription` / `yt-dlp-downloader`。
- 私密账号、未授权内容、批量搬运：不要绕过权限或平台限制。

## Capability Levels

### Level 0：本地文件兜底

如果用户能提供本地视频文件，这是最稳路线。脚本会复制原始文件、写元数据、可选抽音频，后续再转写和总结。

```bash
skill=~/.hermes/skills/media/douyin-note
python3 "$skill/scripts/run_douyin_note.py" "/path/to/video.mp4" \
  --work-dir ./tmp_douyin_note \
  --archive-dir ./douyin_archive \
  --extract-audio
```

### Level 1：yt-dlp / uvx 轻量解析

如果系统有 `yt-dlp`，或有 `uvx` 可临时运行 `yt-dlp`，先尝试抓元数据；需要下载时加 `--download-media`。

```bash
skill=~/.hermes/skills/media/douyin-note
python3 "$skill/scripts/check_environment.py"
python3 "$skill/scripts/run_douyin_note.py" "DOUYIN_URL" \
  --work-dir ./tmp_douyin_note \
  --archive-dir ./douyin_archive \
  --download-media \
  --extract-audio
```

如果需要浏览器登录态：

```bash
python3 "$skill/scripts/run_douyin_note.py" "DOUYIN_URL" \
  --cookies-from-browser chrome \
  --download-media
```

### Level 1.5：浏览器 `RENDER_DATA` 兜底

当 `yt-dlp` 报 `Fresh cookies are needed`，不要立刻放弃。优先用浏览器打开：

```text
https://www.douyin.com/jingxuan?modal_id=<aweme_id>
```

如果页面源码里有 `script#RENDER_DATA`，在浏览器控制台读取：

```js
const j = JSON.parse(decodeURIComponent(document.getElementById('RENDER_DATA').textContent));
const v = j.app.videoDetail;
```

重点保存：`v.awemeId`、`v.itemTitle`、`v.desc`、`v.authorInfo`、`v.stats`、`v.chapterInfo.list`、`v.video.bitRateList`。如果 `v.video.bitRateList[0].playAddr[0].src` 可访问，可用 `curl -L -A <browser UA> -e <douyin page>` 下载 MP4。这个路线已经在 `https://v.douyin.com/cu4aZGO8ko0/` 上验证：yt-dlp 失败，但浏览器 RENDER_DATA + SSR playAddr 成功下载 48MB MP4。

### Level 1.6：本地 ASR 转写

如果已经下载到 MP4，但系统没有 `ffmpeg` / `ffprobe`，可以直接用 `faster-whisper` 通过 PyAV 读取 MP4。快速草稿可用 CPU base：

```bash
uv run --with faster-whisper python transcribe_faster_whisper.py
```

如果机器有 NVIDIA GPU，最终转写优先用 CUDA + `large-v3`：

```bash
uv run \
  --with faster-whisper \
  --with nvidia-cublas-cu12 \
  --with nvidia-cudnn-cu12 \
  python transcribe_faster_whisper_large_cuda.py
```

WSL 下 `nvidia-smi` 可能不在 PATH，先检查 `/usr/lib/wsl/lib/nvidia-smi`。实测 RTX 4060 Laptop：`faster-whisper base`、CPU int8、中文 19m44s 视频约 129 秒转写完成；`large-v3`、CUDA float16 约 513 秒完成，技术英语词明显更准。技术视频仍要预期术语误识别，写笔记时必须结合章节和上下文校正。

### Level 1.7：云端 ASR

抖音视频笔记默认接“录音文件识别 / file transcription”，不是实时流式识别。原因：抖音内容已经是完整 MP4/M4A，文件识别更简单、可重试、可归档、成本和结果更稳定；流式识别只适合麦克风实时字幕、直播监听、边说边出字、语音助手低延迟交互。超长视频也优先切片后走文件识别，而不是强行模拟实时流。

可以接 OpenAI-compatible 的云端转写接口，也可以接火山豆包语音。当前脚本已支持 SiliconFlow、通用 OpenAI-compatible multipart `/audio/transcriptions`、Volcengine Flash 一次请求、本地 base64、以及 Volcengine Standard `submit/query` URL 异步模式：

```bash
skill=~/.hermes/skills/media/douyin-note
export SILICONFLOW_API_KEY='...'
uv run --with imageio-ffmpeg python "$skill/scripts/cloud_asr_transcribe.py" media/video.mp4 \
  --provider siliconflow \
  --prepare-audio \
  --out-dir cloud_asr_siliconflow
```

SiliconFlow 路线使用 `https://api.siliconflow.cn/v1/audio/transcriptions`，默认模型 `FunAudioLLM/SenseVoiceSmall`，官方限制单文件不超过 1 小时且不超过 50MB。对 MP4 建议先 `--prepare-audio` 转成压缩 `.m4a` 再上传；实测 48MB/19m44s MP4 可转成约 14.35MB m4a。

火山路线优先接极速版，而不是标准版：抖音笔记通常小于 2 小时，极速版一次请求返回、支持 `audio.data` base64 本地文件上传，不需要公网音频 URL；标准版只在超 2 小时、需要异步队列/回调、或文件/任务规模更大时作为 fallback。

```bash
export VOLCENGINE_ASR_API_KEY='***'
uv run --with imageio-ffmpeg python "$skill/scripts/cloud_asr_transcribe.py" media/video.mp4 \
  --provider volcengine-flash \
  --prepare-audio \
  --prepared-ext mp3 \
  --language zh-CN \
  --out-dir cloud_asr_volcengine_flash
```

脚本带保险：`--auto-split` 默认开启。若本地音频超过 provider 限制，火山极速版会先切成多个 chunk，逐段识别，再合并 `transcript.txt`、`transcript.md` 和带偏移后的 `utterances.json`。可用 `--chunk-seconds 1800` 调整分片长度，或用 `--force-split` 强制测试分片流程。

识别完成后必须走核对纠错再输出：用 `review_asr_transcript.py` 读取原始 transcript、utterances 和视频 metadata/chapters，产出 `reviewed/transcript_corrected.md`、`reviewed/transcript_corrected.txt`、`reviewed/utterances_corrected.json`、`reviewed/correction_report.json`。最终笔记和对用户输出默认基于 corrected transcript，而不是直接基于 raw ASR。

```bash
python "$skill/scripts/review_asr_transcript.py" \
  --transcript cloud_asr_volcengine_flash/transcript.txt \
  --utterances cloud_asr_volcengine_flash/utterances.json \
  --metadata metadata/browser_video_detail.json \
  --out-dir cloud_asr_volcengine_flash/reviewed
```

火山标准版路线要求公网音频 URL，不能直接 multipart 上传本地文件。先用脚本生成 MP3，再上传到可访问地址，然后运行：

```bash
export VOLCENGINE_ASR_API_KEY='***'
python "$skill/scripts/cloud_asr_transcribe.py" 'https://your-public-host/audio.mp3' \
  --provider volcengine-standard \
  --audio-format mp3 \
  --language zh-CN \
  --out-dir cloud_asr_volcengine
```

默认使用资源 ID `volc.seedasr.auc`（豆包录音文件识别模型 2.0），提交地址 `/api/v3/auc/bigmodel/submit`，查询地址 `/api/v3/auc/bigmodel/query`。

### Level 2：专用抖音工具路线

当 yt-dlp 和浏览器 RENDER_DATA 路线都失败，优先研究/接入这些工具，而不是硬编临时接口：

- `jiji262/douyin-downloader`：适合做主底座，支持视频、图文、合集、主页、评论、浏览器 fallback、REST API。
- `Evil0ctal/Douyin_TikTok_Download_API`：适合完整 FastAPI 服务，能力强但部署重。
- `Johnserf-Seed/f2`：适合底层库研究和长期封装。
- `yzfly/douyin-mcp-server`：适合参考“下载 + 抽音频 + SenseVoice 转写 + Markdown 输出”，但仓库已归档，不建议长期直接依赖。

当前脚本支持通过 `DOUYIN_DOWNLOADER_HOME` 标记本地专用工具目录，环境检查会提示其存在；真正接入前要先做安全审查和最小样例验证。

## Default Workflow

1. 判断输入类型：短链、长链、图文、主页、直播、本地文件。
2. 运行环境检查：

```bash
python3 ~/.hermes/skills/media/douyin-note/scripts/check_environment.py --json
```

3. 创建材料包：优先保存原始输入、解析结果、下载文件、抽取音频、错误日志。
4. 只在确实拿到媒体或可靠文案后写完整笔记；否则写“有限材料摘要”，明确覆盖范围。
5. 如果用户要评论区：只有专用工具验证可用时才抓；失败时不要伪造评论。
6. 写笔记时保留：标题、作者、链接、发布时间/时长/统计数据、文案或转写、关键画面说明、可迁移方法、局限。
7. 最后报告真实产物路径和失败路线，不要只说“应该可以”。

## Output Layout

`run_douyin_note.py` 生成的归档目录默认包含：

```text
archive_dir/
  douyin_note_run_report.md
  metadata/
    input.json
    summary.json
    yt_dlp_info.json            # 如果 yt-dlp 成功
    note_budget.json
  media/
    original_*                  # 本地输入复制或下载结果
    audio.m4a                   # 可选抽音频
  indexes/
    文案与元数据.md
  logs/
    yt_dlp_metadata.stderr.txt
    yt_dlp_download.stderr.txt
```

## Note Writing Standard

默认写“学习型笔记”或“内容消化笔记”，而不是只贴下载信息。

建议结构：

1. `# 标题`
2. `## 我从这个内容里拿到什么`
3. `## 一句话总结`
4. `## 关键内容`
5. `## 可迁移的方法或判断`
6. `## 适用边界与误区`
7. `## 原文文案 / 转写摘要`
8. `## 来源、覆盖与局限`

如果只拿到元数据：明确说“未完成音频转写”。如果只拿到本地视频但没有 ASR：明确说“已归档媒体和音频，等待转写”。

## References

- `references/browser-render-data-fallback.md`：当 yt-dlp / cookies 路线报 `Fresh cookies needed` 时，使用浏览器 `RENDER_DATA.app.videoDetail` 和 SSR `playAddr` 提取元数据、章节和 MP4 的实测路线。
- `references/asr-cuda-faster-whisper.md`：NVIDIA / WSL 下使用 `faster-whisper large-v3` + CUDA + pip CUDA wheels 做高质量转写的实测路线。
- `references/cloud-asr-providers.md`：SiliconFlow SenseVoice、通用 OpenAI-compatible `/audio/transcriptions`、DashScope Paraformer async URL 模式的云端 ASR 路由和坑点。
- `references/cloud-asr-review-wiki-ingestion.md`：本 session 验证过的火山极速版凭证映射、真实 ASR 调用、ASR 后纠错、以及抖音技术视频归档到 wiki 的完整形状。
- `references/candidate-tools.md`：抖音专用解析/下载工具候选及适用场景。

## Scripts

### `scripts/check_environment.py`

检查 Python、uvx、yt-dlp、ffmpeg、ffprobe，以及可选的 `DOUYIN_DOWNLOADER_HOME`。

### `scripts/run_douyin_note.py`

最小可用归档器：支持本地媒体文件、抖音 URL 元数据抓取、可选下载、可选抽音频，并写出可被后续总结使用的材料包。

### `scripts/cloud_asr_transcribe.py`

云端 ASR 适配器：支持 SiliconFlow `FunAudioLLM/SenseVoiceSmall`、通用 OpenAI-compatible `/audio/transcriptions`、火山 `volcengine-flash` 极速版本地 base64 识别、火山 `volcengine-standard` 标准版 URL submit/query；可用 `--prepare-audio` 通过 `imageio-ffmpeg` 临时 ffmpeg 把 MP4 转成 `.mp3` 或 `.m4a` 后上传/识别。`--auto-split` 默认开启，超 provider 限制时会分片识别并合并 transcript/utterances。

### `scripts/review_asr_transcript.py`

ASR 后处理核对器：读取 raw transcript、utterances 和 metadata/chapters，用保守术语表纠正明显误识别（如 Tools/Skills/Memory/Context/Permission/Subagent/Sessions/Command/Hook/Query Engine、TypeScript/LangChain/LangGraph/SQLite 等），输出 corrected transcript、corrected utterances 和 correction report。最终笔记默认使用 corrected transcript。

## Common Pitfalls

1. 把抖音当成稳定公开网页。抖音经常需要 fresh cookies、A-Bogus/X-Bogus、浏览器 fallback。
2. yt-dlp 成功不代表长期可靠。它可做第一尝试，但不要把它当唯一方案。
3. yt-dlp 报 `Fresh cookies needed` 时漏掉浏览器 SSR 页面。先试 `/jingxuan?modal_id=<aweme_id>`，检查 `RENDER_DATA.videoDetail` 和 `video.bitRateList[].playAddr`。
4. 不要承诺评论区一定能抓全。评论抓取通常需要 Cookie 和专用工具。
5. 不要把封面/标题/简介写成“完整转写”。完整笔记必须有媒体、文案或 ASR 证据。
6. 不要绕过授权处理私密内容。用户未明确授权时，只处理公开内容或用户自己上传的本地文件。

## Verification Checklist

- [ ] `check_environment.py` 能运行并输出当前路线可用性。
- [ ] `run_douyin_note.py --help` 正常。
- [ ] 本地文件输入能生成归档目录和 `douyin_note_run_report.md`。
- [ ] URL 输入失败时保留 stderr 和下一步建议，不伪造成功。
- [ ] yt-dlp fresh-cookie 失败时尝试浏览器 `RENDER_DATA` 兜底。
- [ ] 已下载 MP4 后优先尝试本地 ASR；无系统 ffmpeg 时可用 `uv run --with faster-whisper`。
- [ ] 需要云端 ASR 时，先用 `cloud_asr_transcribe.py --dry-run` 验证 key、大小和输出目录；MP4 优先 `--prepare-audio` 压缩成 mp3/m4a；超限时确认 `--auto-split` 生成了 `chunks_audio/`、`split_audio.json` 和合并后的 transcript/utterances。
- [ ] ASR 完成后必须运行 `review_asr_transcript.py`，最终笔记/回复使用 `reviewed/transcript_corrected.*`，并保留 `correction_report.json`。
- [ ] 最终回复包含真实产物路径、成功步骤、失败步骤和下一步。