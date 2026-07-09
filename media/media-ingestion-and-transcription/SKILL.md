---
name: media-ingestion-and-transcription
description: Unified guidance for turning videos, audio, images, and URLs into usable text or inspectable inputs. Use when the user needs transcripts, summaries, video notes, or a reliable path for loading media into downstream workflows.
---

# Media Ingestion and Transcription

## Overview
This umbrella skill consolidates the front end of media-understanding workflows: load the media correctly, extract text/transcripts, and summarize or structure the result.

## Core workflow
1. Identify the media type: URL/article/video, audio, or image.
2. Decide whether the user needs raw extraction, a transcript, structured notes, or a summary.
3. Use the lightest extraction path that preserves fidelity.
4. Verify the extracted artifact before building downstream analysis on top of it.

## Consolidated subsections
### URL and article summarization
Pull text or concise summaries from web pages, links, podcasts, or video URLs when raw extraction is enough. For WeChat public-account links (`mp.weixin.qq.com`), use the local workflow documented in `references/wechat-article-extraction.md` before summarizing or writing notes.

### Video-to-notes workflows
Generate structured notes from supported video inputs when the user wants a document-like output instead of a plain transcript. For YouTube URLs, use the absorbed YouTube workflow at `references/youtube-content.md`; the helper script is now `scripts/youtube/fetch_transcript.py`, and additional formatting guidance is in `references/youtube-output-formats.md`.

### Media loading and normalization
Resolve local-vs-remote image/media inputs cleanly before inspection or downstream processing.

## Absorbed specialized skills
- `summarize`
- `ai-notes-ofvideo`
- `youtube-content` — YouTube transcript extraction and transcript-to-summary/chapter/thread/blog formatting.
- `smart-image-loader`

## Navigation
Provider-specific commands, scripts, and absorbed narrow skill bodies live in `references/` and `scripts/`.

## Cloud ASR fallback pattern
When subtitles or native transcripts are missing/unusable, prefer recorded-file ASR over streaming ASR for already-downloaded videos/audio. Use streaming only for live microphone, meetings, calls, or low-latency subtitle needs.

For local media cloud ASR, normalize first: extract/compress audio to a provider-supported format (usually MP3/M4A/WAV), dry-run/check file size and credentials, then call the provider. For providers with single-file limits, build in split insurance: split large prepared audio into chunks, transcribe each chunk separately, and merge transcript text plus offset-adjusted utterance timestamps. Keep artifacts such as prepared audio, split manifest, per-chunk responses, merged transcript, and limitations in the archive.

## Common pitfalls
- Treating every media request as a transcript request.
- Skipping media normalization for remote URLs.
- Trusting summaries without checking extraction success.
- Using heavy note-generation when a direct transcript or summary would do.
- Using streaming ASR for complete media files when recorded-file ASR is simpler, cheaper to retry, and easier to archive.
- Forgetting provider size/duration limits; always dry-run and split large local media before paying for cloud ASR.

## Verification checklist
- [ ] Media type identified.
- [ ] Extraction vs summary vs notes path chosen.
- [ ] Input successfully loaded before processing.
- [ ] Output artifact verified before downstream use.
