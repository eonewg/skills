#!/usr/bin/env python3
"""Cloud ASR adapter for bili-note / media note archives.

Supports:
- SiliconFlow / OpenAI-compatible multipart /audio/transcriptions.
- Volcengine Doubao Speech recorded-file flash HTTP API (one request, URL or base64 data).
- Volcengine Doubao Speech recorded-file standard HTTP API (submit + query),
  which requires an audio URL rather than direct local-file upload.

Keeps API keys in environment variables and writes raw responses plus Markdown
transcripts. No secrets are printed except boolean presence flags in --dry-run.
"""
from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path
from typing import Any

DEFAULTS = {
    "siliconflow": {
        "endpoint": "https://api.siliconflow.cn/v1/audio/transcriptions",
        "model": "FunAudioLLM/SenseVoiceSmall",
        "api_key_env": "SILICONFLOW_API_KEY",
        "max_bytes": 50 * 1024 * 1024,
        "max_duration_note": "1 hour",
        "mode": "multipart",
    },
    "openai-compatible": {
        "endpoint": "https://api.openai.com/v1/audio/transcriptions",
        "model": "gpt-4o-transcribe",
        "api_key_env": "OPENAI_API_KEY",
        "max_bytes": None,
        "max_duration_note": "provider-specific",
        "mode": "multipart",
    },
    "volcengine-flash": {
        "recognize_endpoint": "https://openspeech.bytedance.com/api/v3/auc/bigmodel/recognize/flash",
        "model": "bigmodel",
        "api_key_env": "VOLCENGINE_ASR_API_KEY",
        "app_key_env": "VOLCENGINE_ASR_APP_KEY",
        "access_key_env": "VOLCENGINE_ASR_ACCESS_KEY",
        "resource_id": "volc.bigasr.auc_turbo",
        "max_bytes": 100 * 1024 * 1024,
        "max_duration_note": "2 hours; flash API is one request and supports audio.url or audio.data base64",
        "mode": "volcengine_flash",
    },
    "volcengine-standard": {
        "submit_endpoint": "https://openspeech.bytedance.com/api/v3/auc/bigmodel/submit",
        "query_endpoint": "https://openspeech.bytedance.com/api/v3/auc/bigmodel/query",
        "model": "bigmodel",
        "api_key_env": "VOLCENGINE_ASR_API_KEY",
        "app_key_env": "VOLCENGINE_ASR_APP_KEY",
        "access_key_env": "VOLCENGINE_ASR_ACCESS_KEY",
        "resource_id": "volc.seedasr.auc",  # Doubao recorded-file recognition model 2.0
        "max_bytes": 512 * 1024 * 1024,
        "max_duration_note": "provider queue/usage limits; standard API is async submit + query",
        "mode": "volcengine_submit_query",
    },
}

PENDING_CODES = {"20000001", "20000002"}
SUCCESS_CODE = "20000000"


def die(message: str, code: int = 2) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return code


def is_url(value: str) -> bool:
    parsed = urllib.parse.urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def find_ffmpeg() -> str | None:
    for name in ("ffmpeg",):
        try:
            proc = subprocess.run([name, "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if proc.returncode == 0:
                return name
        except FileNotFoundError:
            pass
    try:
        import imageio_ffmpeg  # type: ignore

        exe = imageio_ffmpeg.get_ffmpeg_exe()
        if exe and Path(exe).exists():
            return exe
    except Exception:
        return None
    return None


def prepare_audio(input_path: Path, output_path: Path, bitrate: str = "96k") -> dict[str, Any]:
    ffmpeg = find_ffmpeg()
    if not ffmpeg:
        return {
            "ok": False,
            "error": "ffmpeg not found. Install system ffmpeg or run with `uv run --with imageio-ffmpeg ... --prepare-audio`.",
        }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    suffix = output_path.suffix.lower()
    if suffix == ".mp3":
        audio_args = ["-c:a", "libmp3lame", "-b:a", bitrate]
    elif suffix == ".wav":
        audio_args = ["-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1"]
    else:
        audio_args = ["-c:a", "aac", "-b:a", bitrate]
    cmd = [ffmpeg, "-y", "-i", str(input_path), "-vn", *audio_args, str(output_path)]
    started = time.time()
    proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return {
        "ok": proc.returncode == 0,
        "command": cmd,
        "elapsed_seconds": round(time.time() - started, 2),
        "stdout": proc.stdout,
        "stderr": proc.stderr[-4000:],
        "output": str(output_path),
        "bytes": output_path.stat().st_size if output_path.exists() else 0,
    }




def split_audio(
    input_path: Path,
    chunks_dir: Path,
    chunk_seconds: int,
    bitrate: str = "96k",
    audio_format: str = "mp3",
) -> dict[str, Any]:
    ffmpeg = find_ffmpeg()
    if not ffmpeg:
        return {
            "ok": False,
            "error": "ffmpeg not found. Install system ffmpeg or run with `uv run --with imageio-ffmpeg ...`.",
        }
    chunks_dir.mkdir(parents=True, exist_ok=True)
    ext = audio_format.lower().strip().lstrip(".") or input_path.suffix.lower().lstrip(".") or "mp3"
    if ext == "ogg":
        ext = "ogg"
        audio_args = ["-c:a", "libopus", "-b:a", bitrate]
    elif ext == "wav":
        audio_args = ["-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1"]
    elif ext == "m4a":
        audio_args = ["-c:a", "aac", "-b:a", bitrate]
    else:
        ext = "mp3"
        audio_args = ["-c:a", "libmp3lame", "-b:a", bitrate]
    pattern = chunks_dir / f"chunk_%03d.{ext}"
    cmd = [
        ffmpeg,
        "-y",
        "-i",
        str(input_path),
        "-vn",
        "-map",
        "0:a:0",
        *audio_args,
        "-f",
        "segment",
        "-segment_time",
        str(chunk_seconds),
        "-reset_timestamps",
        "1",
        str(pattern),
    ]
    started = time.time()
    proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    chunks = []
    for idx, path in enumerate(sorted(chunks_dir.glob(f"chunk_*.{ext}"))):
        chunks.append({
            "index": idx,
            "path": str(path),
            "bytes": path.stat().st_size,
            "start_time_ms_estimate": idx * chunk_seconds * 1000,
        })
    return {
        "ok": proc.returncode == 0 and bool(chunks),
        "command": cmd,
        "elapsed_seconds": round(time.time() - started, 2),
        "stdout": proc.stdout,
        "stderr": proc.stderr[-4000:],
        "chunk_seconds": chunk_seconds,
        "audio_format": ext,
        "chunks": chunks,
    }


def offset_utterance_times(utterance: dict[str, Any], offset_ms: int) -> dict[str, Any]:
    copied = json.loads(json.dumps(utterance, ensure_ascii=False))
    for key in ("start_time", "end_time"):
        if isinstance(copied.get(key), (int, float)):
            copied[key] = int(copied[key] + offset_ms)
    words = copied.get("words")
    if isinstance(words, list):
        for word in words:
            if isinstance(word, dict):
                for key in ("start_time", "end_time"):
                    if isinstance(word.get(key), (int, float)):
                        word[key] = int(word[key] + offset_ms)
    return copied


def merge_chunk_results(chunk_results: list[dict[str, Any]], chunk_seconds: int) -> dict[str, Any]:
    texts: list[str] = []
    utterances: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    ok = True
    for idx, result in enumerate(chunk_results):
        ok = ok and bool(result.get("ok"))
        chunk = result.get("chunk", {}) if isinstance(result.get("chunk"), dict) else {}
        offset_ms = int(chunk.get("start_time_ms_estimate", idx * chunk_seconds * 1000))
        text = extract_text(result)
        if text:
            texts.append(text)
        for utt in extract_utterances(result):
            utterances.append(offset_utterance_times(utt, offset_ms))
        summaries.append({
            "index": idx,
            "ok": bool(result.get("ok")),
            "request_id": result.get("request_id"),
            "status_code": result.get("status_code"),
            "message": result.get("message"),
            "text_chars": len(text),
            "chunk": chunk,
        })
    return {
        "ok": ok,
        "chunked": True,
        "chunk_seconds": chunk_seconds,
        "elapsed_seconds": round(sum(float(r.get("elapsed_seconds") or 0) for r in chunk_results), 2),
        "data": {
            "result": {
                "text": "\n".join(texts),
                "utterances": utterances,
            },
            "chunks": summaries,
        },
    }


def multipart_body(fields: dict[str, str], file_field: str, file_path: Path) -> tuple[bytes, str]:
    boundary = f"----douyin-note-{uuid.uuid4().hex}"
    chunks: list[bytes] = []
    for name, value in fields.items():
        chunks.append(f"--{boundary}\r\n".encode())
        chunks.append(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
        chunks.append(str(value).encode("utf-8"))
        chunks.append(b"\r\n")
    filename = file_path.name
    ctype = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    chunks.append(f"--{boundary}\r\n".encode())
    chunks.append(f'Content-Disposition: form-data; name="{file_field}"; filename="{filename}"\r\n'.encode())
    chunks.append(f"Content-Type: {ctype}\r\n\r\n".encode())
    chunks.append(file_path.read_bytes())
    chunks.append(b"\r\n")
    chunks.append(f"--{boundary}--\r\n".encode())
    return b"".join(chunks), boundary


def post_json(url: str, headers: dict[str, str], payload: dict[str, Any], timeout: int) -> dict[str, Any]:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    started = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", "replace")
            status = resp.status
            resp_headers = dict(resp.headers.items())
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace")
        return {
            "ok": False,
            "status": exc.code,
            "headers": dict(exc.headers.items()) if exc.headers else {},
            "elapsed_seconds": round(time.time() - started, 2),
            "raw": raw,
            "error": str(exc),
        }
    except Exception as exc:
        return {"ok": False, "elapsed_seconds": round(time.time() - started, 2), "error": str(exc)}
    try:
        body = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        body = {"raw_text": raw}
    return {
        "ok": 200 <= status < 300,
        "status": status,
        "headers": resp_headers,
        "elapsed_seconds": round(time.time() - started, 2),
        "data": body,
        "raw": raw,
    }


def post_transcription(endpoint: str, api_key: str, model: str, file_path: Path, timeout: int) -> dict[str, Any]:
    body, boundary = multipart_body({"model": model}, "file", file_path)
    req = urllib.request.Request(
        endpoint,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Accept": "application/json",
        },
        method="POST",
    )
    started = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", "replace")
            status = resp.status
            headers = dict(resp.headers.items())
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace")
        return {
            "ok": False,
            "status": exc.code,
            "elapsed_seconds": round(time.time() - started, 2),
            "raw": raw,
            "error": str(exc),
        }
    except Exception as exc:
        return {"ok": False, "elapsed_seconds": round(time.time() - started, 2), "error": str(exc)}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {"raw_text": raw}
    return {
        "ok": 200 <= status < 300,
        "status": status,
        "headers": headers,
        "elapsed_seconds": round(time.time() - started, 2),
        "data": data,
        "raw": raw,
    }


def header_ci(headers: dict[str, Any], key: str) -> str:
    for k, v in (headers or {}).items():
        if k.lower() == key.lower():
            return str(v)
    return ""


def volcengine_auth_headers(args: argparse.Namespace, defaults: dict[str, Any], request_id: str, submit: bool) -> tuple[dict[str, str], dict[str, bool]]:
    api_key_env = args.api_key_env or defaults["api_key_env"]
    app_key_env = args.volcengine_app_key_env or defaults["app_key_env"]
    access_key_env = args.volcengine_access_key_env or defaults["access_key_env"]
    api_key = os.environ.get(api_key_env, "").strip()
    app_key = os.environ.get(app_key_env, "").strip()
    access_key = os.environ.get(access_key_env, "").strip()
    headers = {
        "Content-Type": "application/json",
        "X-Api-Resource-Id": args.resource_id or defaults["resource_id"],
        "X-Api-Request-Id": request_id,
    }
    if submit:
        headers["X-Api-Sequence"] = "-1"
    if api_key:
        headers["X-Api-Key"] = api_key
    elif app_key and access_key:
        headers["X-Api-App-Key"] = app_key
        headers["X-Api-Access-Key"] = access_key
    return headers, {
        api_key_env: bool(api_key),
        app_key_env: bool(app_key),
        access_key_env: bool(access_key),
    }


def volcengine_payload(args: argparse.Namespace, defaults: dict[str, Any], audio_url: str) -> dict[str, Any]:
    audio: dict[str, Any] = {
        "url": audio_url,
        "format": args.audio_format,
    }
    if args.language:
        audio["language"] = args.language
    request: dict[str, Any] = {
        "model_name": args.model or defaults["model"],
        "enable_itn": args.enable_itn,
        "enable_punc": args.enable_punc,
        "enable_ddc": args.enable_ddc,
        "show_utterances": args.show_utterances,
    }
    if args.enable_speaker_info:
        request["enable_speaker_info"] = True
    if args.context:
        request["corpus"] = {"context": args.context}
    payload = {
        "user": {"uid": args.uid or "media-note"},
        "audio": audio,
        "request": request,
    }
    if args.callback:
        payload["callback"] = args.callback
    if args.callback_data:
        payload["callback_data"] = args.callback_data
    return payload


def file_to_base64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("utf-8")


def volcengine_flash_payload(args: argparse.Namespace, defaults: dict[str, Any], audio: dict[str, Any]) -> dict[str, Any]:
    request: dict[str, Any] = {
        "model_name": args.model or defaults["model"],
        "enable_itn": args.enable_itn,
        "enable_punc": args.enable_punc,
        "enable_ddc": args.enable_ddc,
        "show_utterances": args.show_utterances,
    }
    if args.enable_speaker_info:
        request["enable_speaker_info"] = True
    if args.context:
        request["corpus"] = {"context": args.context}
    return {
        "user": {"uid": args.uid or "media-note"},
        "audio": audio,
        "request": request,
    }


def redact_payload_for_storage(payload: dict[str, Any]) -> dict[str, Any]:
    safe = json.loads(json.dumps(payload, ensure_ascii=False))
    audio = safe.get("audio")
    if isinstance(audio, dict) and isinstance(audio.get("data"), str):
        data_len = len(audio["data"])
        audio["data"] = f"<base64 redacted, chars={data_len}>"
    return safe


def volcengine_flash_recognize(
    args: argparse.Namespace,
    defaults: dict[str, Any],
    audio: dict[str, Any],
    out_dir: Path,
) -> dict[str, Any]:
    request_id = args.request_id or str(uuid.uuid4())
    headers, key_presence = volcengine_auth_headers(args, defaults, request_id, submit=True)
    if not (headers.get("X-Api-Key") or (headers.get("X-Api-App-Key") and headers.get("X-Api-Access-Key"))):
        return {
            "ok": False,
            "provider": args.provider,
            "request_id": request_id,
            "api_key_presence": key_presence,
            "error": "missing Volcengine credentials; set VOLCENGINE_ASR_API_KEY for new console, or VOLCENGINE_ASR_APP_KEY + VOLCENGINE_ASR_ACCESS_KEY for old console",
        }
    payload = volcengine_flash_payload(args, defaults, audio)
    (out_dir / "volcengine_flash_request.json").write_text(
        json.dumps({"headers_redacted": redact_headers(headers), "payload": redact_payload_for_storage(payload)}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    response = post_json(defaults["recognize_endpoint"], headers, payload, args.timeout)
    (out_dir / "volcengine_flash_response.json").write_text(json.dumps(response, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    code = header_ci(response.get("headers", {}), "X-Api-Status-Code")
    msg = header_ci(response.get("headers", {}), "X-Api-Message")
    return {
        "ok": bool(response.get("ok") and code == SUCCESS_CODE),
        "provider": args.provider,
        "request_id": request_id,
        "status_code": code,
        "message": msg,
        "elapsed_seconds": response.get("elapsed_seconds"),
        "data": response.get("data"),
        "raw_response": response,
        "api_key_presence": key_presence,
    }




def transcribe_volcengine_flash_chunks(
    args: argparse.Namespace,
    defaults: dict[str, Any],
    chunks: list[dict[str, Any]],
    out_dir: Path,
) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    base_request_id = args.request_id or str(uuid.uuid4())
    original_request_id = args.request_id
    try:
        for chunk in chunks:
            idx = int(chunk["index"])
            chunk_path = Path(str(chunk["path"]))
            args.request_id = f"{base_request_id}-{idx:03d}"
            audio: dict[str, Any] = {"data": file_to_base64(chunk_path), "format": args.audio_format}
            if args.language:
                audio["language"] = args.language
            chunk_out_dir = out_dir / "chunk_responses" / f"chunk_{idx:03d}"
            chunk_out_dir.mkdir(parents=True, exist_ok=True)
            result = volcengine_flash_recognize(args, defaults, audio, chunk_out_dir)
            result["chunk"] = chunk
            results.append(result)
            if not result.get("ok"):
                break
    finally:
        args.request_id = original_request_id
    combined = merge_chunk_results(results, args.chunk_seconds)
    combined.update({
        "provider": args.provider,
        "request_id": base_request_id,
        "chunk_count": len(chunks),
        "completed_chunks": len(results),
    })
    (out_dir / "chunk_results_manifest.json").write_text(
        json.dumps(combined.get("data", {}).get("chunks", []), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return combined


def volcengine_submit_query(args: argparse.Namespace, defaults: dict[str, Any], audio_url: str, out_dir: Path) -> dict[str, Any]:
    request_id = args.request_id or str(uuid.uuid4())
    submit_headers, key_presence = volcengine_auth_headers(args, defaults, request_id, submit=True)
    if not (submit_headers.get("X-Api-Key") or (submit_headers.get("X-Api-App-Key") and submit_headers.get("X-Api-Access-Key"))):
        return {
            "ok": False,
            "provider": args.provider,
            "request_id": request_id,
            "api_key_presence": key_presence,
            "error": "missing Volcengine credentials; set VOLCENGINE_ASR_API_KEY for new console, or VOLCENGINE_ASR_APP_KEY + VOLCENGINE_ASR_ACCESS_KEY for old console",
        }
    payload = volcengine_payload(args, defaults, audio_url)
    submit = post_json(defaults["submit_endpoint"], submit_headers, payload, args.timeout)
    (out_dir / "volcengine_submit_request.json").write_text(json.dumps({"headers_redacted": redact_headers(submit_headers), "payload": payload}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_dir / "volcengine_submit_response.json").write_text(json.dumps(submit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    submit_code = header_ci(submit.get("headers", {}), "X-Api-Status-Code")
    submit_msg = header_ci(submit.get("headers", {}), "X-Api-Message")
    if not submit.get("ok") or submit_code != SUCCESS_CODE:
        return {
            "ok": False,
            "provider": args.provider,
            "request_id": request_id,
            "submit_status_code": submit_code,
            "submit_message": submit_msg,
            "submit": submit,
            "api_key_presence": key_presence,
        }
    if args.no_wait or args.callback:
        return {
            "ok": True,
            "pending": True,
            "provider": args.provider,
            "request_id": request_id,
            "submit_status_code": submit_code,
            "submit_message": submit_msg,
            "submit": submit,
            "api_key_presence": key_presence,
        }

    query_headers, _ = volcengine_auth_headers(args, defaults, request_id, submit=False)
    history: list[dict[str, Any]] = []
    started = time.time()
    final: dict[str, Any] | None = None
    for attempt in range(1, args.max_polls + 1):
        query = post_json(defaults["query_endpoint"], query_headers, {}, args.timeout)
        code = header_ci(query.get("headers", {}), "X-Api-Status-Code")
        msg = header_ci(query.get("headers", {}), "X-Api-Message")
        item = {
            "attempt": attempt,
            "status_code": code,
            "message": msg,
            "http_status": query.get("status"),
            "elapsed_seconds": query.get("elapsed_seconds"),
        }
        history.append(item)
        (out_dir / f"volcengine_query_{attempt:03d}.json").write_text(json.dumps(query, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if query.get("ok") and code == SUCCESS_CODE:
            final = query
            break
        if code not in PENDING_CODES:
            final = query
            break
        time.sleep(args.poll_interval)
    result = {
        "ok": bool(final and final.get("ok") and header_ci(final.get("headers", {}), "X-Api-Status-Code") == SUCCESS_CODE),
        "provider": args.provider,
        "request_id": request_id,
        "submit_status_code": submit_code,
        "submit_message": submit_msg,
        "poll_history": history,
        "elapsed_seconds": round(time.time() - started, 2),
        "final": final,
        "api_key_presence": key_presence,
    }
    (out_dir / "volcengine_query_final.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def redact_headers(headers: dict[str, str]) -> dict[str, str]:
    redacted = {}
    for k, v in headers.items():
        if k.lower() in {"x-api-key", "x-api-app-key", "x-api-access-key", "authorization"}:
            redacted[k] = "***"
        else:
            redacted[k] = v
    return redacted


def extract_text(result: dict[str, Any]) -> str:
    data = result.get("data")
    if isinstance(data, dict):
        if isinstance(data.get("text"), str):
            return data["text"]
        if isinstance(data.get("data"), dict) and isinstance(data["data"].get("text"), str):
            return data["data"]["text"]
        if isinstance(data.get("result"), dict) and isinstance(data["result"].get("text"), str):
            return data["result"]["text"]
        if isinstance(data.get("raw_text"), str):
            return data["raw_text"]
    final = result.get("final")
    if isinstance(final, dict):
        final_data = final.get("data")
        if isinstance(final_data, dict) and isinstance(final_data.get("result"), dict):
            text = final_data["result"].get("text")
            if isinstance(text, str):
                return text
    return ""


def extract_utterances(result: dict[str, Any]) -> list[dict[str, Any]]:
    candidates: list[Any] = []
    data = result.get("data")
    if isinstance(data, dict):
        candidates.append(data)
    final = result.get("final")
    if isinstance(final, dict) and isinstance(final.get("data"), dict):
        candidates.append(final["data"])
    for obj in candidates:
        res = obj.get("result") if isinstance(obj, dict) else None
        if isinstance(res, dict) and isinstance(res.get("utterances"), list):
            return res["utterances"]
    return []


def write_transcript_outputs(out_dir: Path, provider: str, model: str, source_desc: str, result: dict[str, Any]) -> int:
    text = extract_text(result)
    utterances = extract_utterances(result)
    if text:
        (out_dir / "transcript.txt").write_text(text + "\n", encoding="utf-8")
    if utterances:
        (out_dir / "utterances.json").write_text(json.dumps(utterances, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md = [
        f"# 云端 ASR 转写（{provider}）",
        "",
        f"- provider: `{provider}`",
        f"- model: `{model}`",
        f"- source: `{source_desc}`",
        f"- elapsed_seconds: {result.get('elapsed_seconds')}",
        "",
    ]
    if utterances:
        md += ["## Utterances", ""]
        for u in utterances:
            start_ms = u.get("start_time")
            if isinstance(start_ms, (int, float)):
                mm = int(start_ms / 1000 // 60)
                ss = int(start_ms / 1000 % 60)
                md.append(f"- [{mm:02d}:{ss:02d}] {u.get('text', '')}")
            else:
                md.append(f"- {u.get('text', '')}")
        md.append("")
    if text:
        md += ["## Transcript", "", text, ""]
    if text or utterances:
        (out_dir / "transcript.md").write_text("\n".join(md), encoding="utf-8")
    return len(text)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Transcribe a media/audio file or URL with a cloud ASR provider.")
    parser.add_argument("input", help="Local audio/video path for multipart providers, or URL for URL-based providers.")
    parser.add_argument("--provider", choices=sorted(DEFAULTS), default="siliconflow")
    parser.add_argument("--endpoint", default="", help="Override multipart API endpoint.")
    parser.add_argument("--model", default="", help="Override ASR model name.")
    parser.add_argument("--api-key-env", default="", help="Environment variable containing API key.")
    parser.add_argument("--out-dir", default="", help="Output directory. Default: input.parent/cloud_asr_<provider>")
    parser.add_argument("--prepare-audio", action="store_true", help="Convert local input media before upload/use.")
    parser.add_argument("--audio-bitrate", default="96k", help="Bitrate for --prepare-audio. Default: 96k")
    parser.add_argument("--prepared-ext", default="", choices=["", "m4a", "mp3", "wav"], help="Prepared audio extension. Defaults to m4a, or mp3 for Volcengine examples.")
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--dry-run", action="store_true", help="Show resolved config and file checks without calling the API.")
    parser.add_argument("--auto-split", action=argparse.BooleanOptionalAction, default=True, help="Automatically split local audio when it exceeds provider size limits. Default: enabled.")
    parser.add_argument("--force-split", action="store_true", help="Split local audio even when it is under the provider limit; useful for testing or safer long-video processing.")
    parser.add_argument("--chunk-seconds", type=int, default=1800, help="Chunk duration for --auto-split/--force-split. Default: 1800 seconds.")

    # Volcengine recorded-file ASR options. Flash accepts URL or local base64; standard requires URL.
    parser.add_argument("--audio-url", default="", help="Public HTTP(S) audio URL for Volcengine. If input is URL, input is used. For flash, local files can be sent as base64 instead.")
    parser.add_argument("--audio-format", default="mp3", help="Volcengine audio.format: raw, wav, mp3, ogg. Default: mp3")
    parser.add_argument("--language", default="", help="Optional language, e.g. zh-CN, en-US, yue-CN.")
    parser.add_argument("--uid", default="douyin-note", help="Volcengine user.uid. Default: media-note")
    parser.add_argument("--resource-id", default="", help="Volcengine X-Api-Resource-Id. Default: volc.seedasr.auc")
    parser.add_argument("--request-id", default="", help="Volcengine task id / X-Api-Request-Id. Default: random UUID")
    parser.add_argument("--volcengine-app-key-env", default="", help="Old console app key env var. Default: VOLCENGINE_ASR_APP_KEY")
    parser.add_argument("--volcengine-access-key-env", default="", help="Old console access key env var. Default: VOLCENGINE_ASR_ACCESS_KEY")
    parser.add_argument("--enable-itn", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--enable-punc", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--enable-ddc", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--show-utterances", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--enable-speaker-info", action="store_true")
    parser.add_argument("--context", default="", help="Volcengine corpus.context JSON string / hotword context.")
    parser.add_argument("--callback", default="", help="Volcengine callback URL. If set, submit succeeds without polling.")
    parser.add_argument("--callback-data", default="")
    parser.add_argument("--no-wait", action="store_true", help="For Volcengine: submit only, do not poll query endpoint.")
    parser.add_argument("--poll-interval", type=float, default=3.0)
    parser.add_argument("--max-polls", type=int, default=120)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    defaults = DEFAULTS[args.provider]
    mode = defaults["mode"]

    input_is_url = is_url(args.input)
    input_path: Path | None = None
    if not input_is_url:
        input_path = Path(args.input).expanduser().resolve()
        if not input_path.exists():
            return die(f"input not found: {input_path}")

    # Resolve output dir.
    if args.out_dir:
        out_dir = Path(args.out_dir).expanduser().resolve()
    elif input_path:
        out_dir = input_path.parent / f"cloud_asr_{args.provider}"
    else:
        out_dir = Path.cwd() / f"cloud_asr_{args.provider}_{uuid.uuid4().hex[:8]}"
    out_dir.mkdir(parents=True, exist_ok=True)

    upload_path = input_path
    prep: dict[str, Any] | None = None
    if args.prepare_audio:
        if not input_path:
            return die("--prepare-audio requires a local file input")
        ext = args.prepared_ext or ("mp3" if args.provider in {"volcengine-standard", "volcengine-flash"} else "m4a")
        upload_path = out_dir / f"{input_path.stem}.{ext}"
        prep = prepare_audio(input_path, upload_path, args.audio_bitrate)
        (out_dir / "prepare_audio.json").write_text(json.dumps(prep, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if not prep.get("ok"):
            return die(prep.get("error") or "audio preparation failed")


    if mode == "volcengine_flash":
        api_key_env = args.api_key_env or defaults["api_key_env"]
        app_key_env = args.volcengine_app_key_env or defaults["app_key_env"]
        access_key_env = args.volcengine_access_key_env or defaults["access_key_env"]
        audio_url = args.audio_url or (args.input if input_is_url else "")
        source_desc = audio_url or (str(upload_path) if upload_path else str(input_path))
        upload_bytes = upload_path.stat().st_size if upload_path and upload_path.exists() else None
        max_bytes = defaults.get("max_bytes")
        size_exceeds_limit = bool(max_bytes and upload_bytes and upload_bytes > int(max_bytes))
        split_required = bool((not audio_url) and upload_path and (args.force_split or (args.auto_split and size_exceeds_limit)))
        dry_config = {
            "provider": args.provider,
            "mode": mode,
            "recognize_endpoint": defaults["recognize_endpoint"],
            "model": args.model or defaults["model"],
            "resource_id": args.resource_id or defaults["resource_id"],
            "request_id": args.request_id or "<random UUID>",
            "audio_url": audio_url or None,
            "audio_format": args.audio_format,
            "language": args.language or None,
            "supports_local_base64": True,
            "local_prepared_audio": str(upload_path) if upload_path else None,
            "upload_bytes": upload_bytes,
            "provider_max_bytes": max_bytes,
            "provider_max_duration_note": defaults.get("max_duration_note"),
            "prepared_audio": prep,
            "auto_split": args.auto_split,
            "force_split": args.force_split,
            "chunk_seconds": args.chunk_seconds,
            "size_exceeds_limit": size_exceeds_limit,
            "split_required": split_required,
            "api_key_env": api_key_env,
            "old_console_envs": [app_key_env, access_key_env],
            "api_key_present": bool(os.environ.get(api_key_env, "").strip()),
            "old_console_keys_present": bool(os.environ.get(app_key_env, "").strip() and os.environ.get(access_key_env, "").strip()),
        }
        if size_exceeds_limit and not args.auto_split:
            (out_dir / "cloud_asr_config.json").write_text(json.dumps(dry_config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            return die(f"upload file is {upload_bytes} bytes, exceeds provider documented limit {max_bytes} bytes; rerun with --auto-split or choose volcengine-standard")
        if split_required:
            if (not args.dry_run) and not (dry_config["api_key_present"] or dry_config["old_console_keys_present"]):
                (out_dir / "cloud_asr_config.json").write_text(json.dumps(dry_config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                return die("missing Volcengine credentials; set VOLCENGINE_ASR_API_KEY for new console, or VOLCENGINE_ASR_APP_KEY + VOLCENGINE_ASR_ACCESS_KEY for old console")
            split = split_audio(upload_path, out_dir / "chunks_audio", args.chunk_seconds, args.audio_bitrate, args.audio_format)
            (out_dir / "split_audio.json").write_text(json.dumps(split, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            dry_config["split_audio"] = {k: v for k, v in split.items() if k != "stderr"}
            (out_dir / "cloud_asr_config.json").write_text(json.dumps(dry_config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            if not split.get("ok"):
                return die(split.get("error") or "audio split failed")
            if args.dry_run:
                print(json.dumps(dry_config, ensure_ascii=False, indent=2))
                return 0
            result = transcribe_volcengine_flash_chunks(args, defaults, split["chunks"], out_dir)
            (out_dir / "cloud_asr_response.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            text_chars = write_transcript_outputs(out_dir, args.provider, args.model or defaults["model"], source_desc, result)
            print(json.dumps({"ok": result.get("ok"), "chunked": True, "chunks": result.get("completed_chunks"), "out_dir": str(out_dir), "request_id": result.get("request_id"), "text_chars": text_chars, "elapsed_seconds": result.get("elapsed_seconds")}, ensure_ascii=False, indent=2))
            return 0 if result.get("ok") else 1
        (out_dir / "cloud_asr_config.json").write_text(json.dumps(dry_config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if args.dry_run:
            print(json.dumps(dry_config, ensure_ascii=False, indent=2))
            return 0
        if not (dry_config["api_key_present"] or dry_config["old_console_keys_present"]):
            return die("missing Volcengine credentials; set VOLCENGINE_ASR_API_KEY for new console, or VOLCENGINE_ASR_APP_KEY + VOLCENGINE_ASR_ACCESS_KEY for old console")
        if audio_url:
            audio: dict[str, Any] = {"url": audio_url, "format": args.audio_format}
        else:
            if not upload_path:
                return die("Volcengine flash requires a local file or --audio-url")
            audio = {"data": file_to_base64(upload_path), "format": args.audio_format}
        if args.language:
            audio["language"] = args.language
        result = volcengine_flash_recognize(args, defaults, audio, out_dir)
        (out_dir / "cloud_asr_response.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        text_chars = write_transcript_outputs(out_dir, args.provider, args.model or defaults["model"], source_desc, result)
        print(json.dumps({"ok": result.get("ok"), "out_dir": str(out_dir), "request_id": result.get("request_id"), "text_chars": text_chars, "elapsed_seconds": result.get("elapsed_seconds"), "status_code": result.get("status_code"), "message": result.get("message")}, ensure_ascii=False, indent=2))
        return 0 if result.get("ok") else 1

    if mode == "volcengine_submit_query":
        audio_url = args.audio_url or (args.input if input_is_url else "")
        request_id = args.request_id or "<random UUID>"
        api_key_env = args.api_key_env or defaults["api_key_env"]
        app_key_env = args.volcengine_app_key_env or defaults["app_key_env"]
        access_key_env = args.volcengine_access_key_env or defaults["access_key_env"]
        dry_config = {
            "provider": args.provider,
            "mode": mode,
            "submit_endpoint": defaults["submit_endpoint"],
            "query_endpoint": defaults["query_endpoint"],
            "model": args.model or defaults["model"],
            "resource_id": args.resource_id or defaults["resource_id"],
            "request_id": request_id,
            "audio_url": audio_url or None,
            "audio_format": args.audio_format,
            "language": args.language or None,
            "requires_public_audio_url": True,
            "local_prepared_audio": str(upload_path) if upload_path else None,
            "prepared_audio": prep,
            "api_key_env": api_key_env,
            "old_console_envs": [app_key_env, access_key_env],
            "api_key_present": bool(os.environ.get(api_key_env, "").strip()),
            "old_console_keys_present": bool(os.environ.get(app_key_env, "").strip() and os.environ.get(access_key_env, "").strip()),
        }
        (out_dir / "cloud_asr_config.json").write_text(json.dumps(dry_config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if args.dry_run:
            print(json.dumps(dry_config, ensure_ascii=False, indent=2))
            return 0
        if not audio_url:
            return die("Volcengine standard API requires a public audio URL. Pass `--audio-url https://...` or use a URL as input. Local file upload is not supported by this standard API.")
        result = volcengine_submit_query(args, defaults, audio_url, out_dir)
        (out_dir / "cloud_asr_response.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        text_chars = write_transcript_outputs(out_dir, args.provider, args.model or defaults["model"], audio_url, result)
        print(json.dumps({"ok": result.get("ok"), "pending": result.get("pending", False), "out_dir": str(out_dir), "request_id": result.get("request_id"), "text_chars": text_chars, "elapsed_seconds": result.get("elapsed_seconds")}, ensure_ascii=False, indent=2))
        return 0 if result.get("ok") or result.get("pending") else 1

    # Multipart providers.
    if input_is_url:
        return die(f"provider {args.provider} expects a local file input; got URL")
    assert upload_path is not None
    endpoint = args.endpoint or defaults["endpoint"]
    model = args.model or defaults["model"]
    api_key_env = args.api_key_env or defaults["api_key_env"]
    size = upload_path.stat().st_size
    max_bytes = defaults.get("max_bytes")
    config = {
        "provider": args.provider,
        "mode": mode,
        "endpoint": endpoint,
        "model": model,
        "api_key_env": api_key_env,
        "input": str(input_path),
        "upload_file": str(upload_path),
        "upload_bytes": size,
        "provider_max_bytes": max_bytes,
        "provider_max_duration_note": defaults.get("max_duration_note"),
        "prepared_audio": prep,
    }
    (out_dir / "cloud_asr_config.json").write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if max_bytes and size > int(max_bytes):
        return die(f"upload file is {size} bytes, exceeds provider documented limit {max_bytes} bytes")
    api_key = os.environ.get(api_key_env, "").strip()
    if args.dry_run:
        print(json.dumps({**config, "api_key_present": bool(api_key)}, ensure_ascii=False, indent=2))
        return 0
    if not api_key:
        return die(f"missing API key env var: {api_key_env}")
    result = post_transcription(endpoint, api_key, model, upload_path, args.timeout)
    (out_dir / "cloud_asr_response.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    text_chars = write_transcript_outputs(out_dir, args.provider, model, str(upload_path), result)
    print(json.dumps({"ok": result.get("ok"), "out_dir": str(out_dir), "text_chars": text_chars, "elapsed_seconds": result.get("elapsed_seconds"), "status": result.get("status")}, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
