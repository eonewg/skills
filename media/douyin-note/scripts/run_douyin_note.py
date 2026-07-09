#!/usr/bin/env python3
"""Create a traceable Douyin note material archive.

This script intentionally keeps the first version conservative: it archives local
media reliably and tries URL metadata/download through yt-dlp when available. It
records failures instead of pretending that Douyin extraction succeeded.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

MEDIA_EXTS = {".mp4", ".mov", ".m4v", ".webm", ".mkv", ".avi", ".mp3", ".m4a", ".wav", ".aac", ".flac"}
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".heic"}


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def safe_name(text: str, fallback: str = "douyin_item") -> str:
    text = text.strip() or fallback
    text = re.sub(r"https?://", "", text)
    text = re.sub(r"[^0-9A-Za-z._\-\u4e00-\u9fff]+", "_", text)
    text = text.strip("._-")
    return (text[:80] or fallback)


def is_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def infer_id(value: str) -> str:
    patterns = [
        r"/video/(\d+)",
        r"/note/(\d+)",
        r"/gallery/(\d+)",
        r"modal_id=(\d+)",
        r"aweme_id=(\d+)",
    ]
    for pat in patterns:
        m = re.search(pat, value)
        if m:
            return m.group(1)
    if is_url(value):
        parsed = urlparse(value)
        host = parsed.netloc.replace("www.", "")
        slug = parsed.path.strip("/").split("/")[-1] if parsed.path.strip("/") else host
        return safe_name(f"{host}_{slug}")
    return safe_name(Path(value).stem)


def ensure_layout(archive_dir: Path) -> dict[str, Path]:
    dirs = {
        "root": archive_dir,
        "metadata": archive_dir / "metadata",
        "media": archive_dir / "media",
        "indexes": archive_dir / "indexes",
        "logs": archive_dir / "logs",
    }
    for path in dirs.values():
        path.mkdir(parents=True, exist_ok=True)
    return dirs


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def command_exists(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def yt_dlp_command(no_uvx: bool = False) -> list[str]:
    env_cmd = os.environ.get("DOUYIN_NOTE_YTDLP", "").strip()
    if env_cmd:
        return env_cmd.split()
    if command_exists("yt-dlp"):
        return ["yt-dlp"]
    if not no_uvx and command_exists("uvx"):
        return ["uvx", "--from", "yt-dlp", "yt-dlp"]
    return []


def run_cmd(cmd: list[str], timeout: int, cwd: Path | None = None) -> dict[str, Any]:
    started = now_iso()
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
        return {
            "command": cmd,
            "started_at": started,
            "finished_at": now_iso(),
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "ok": proc.returncode == 0,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": cmd,
            "started_at": started,
            "finished_at": now_iso(),
            "returncode": None,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
            "ok": False,
            "error": f"timeout after {timeout}s",
        }
    except Exception as exc:  # pragma: no cover - environment-specific
        return {
            "command": cmd,
            "started_at": started,
            "finished_at": now_iso(),
            "returncode": None,
            "stdout": "",
            "stderr": "",
            "ok": False,
            "error": str(exc),
        }


def ffprobe(path: Path, timeout: int = 20) -> dict[str, Any]:
    if not command_exists("ffprobe"):
        return {"ok": False, "error": "ffprobe not found"}
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(path),
    ]
    res = run_cmd(cmd, timeout)
    if res["ok"]:
        try:
            return {"ok": True, "data": json.loads(res["stdout"] or "{}")}
        except json.JSONDecodeError as exc:
            return {"ok": False, "error": f"ffprobe JSON parse failed: {exc}", "raw": res}
    return {"ok": False, "error": res.get("error") or res.get("stderr") or "ffprobe failed", "raw": res}


def extract_audio(media_path: Path, output_path: Path, timeout: int) -> dict[str, Any]:
    if not command_exists("ffmpeg"):
        return {"ok": False, "error": "ffmpeg not found"}
    cmd = ["ffmpeg", "-y", "-i", str(media_path), "-vn", "-c:a", "aac", "-b:a", "128k", str(output_path)]
    return run_cmd(cmd, timeout)


def copy_local_input(input_path: Path, dirs: dict[str, Path], extract: bool, timeout: int) -> dict[str, Any]:
    if not input_path.exists():
        return {"ok": False, "error": f"local path does not exist: {input_path}"}
    copied: list[str] = []
    probe: dict[str, Any] | None = None
    audio_result: dict[str, Any] | None = None

    if input_path.is_dir():
        dest = dirs["media"] / safe_name(input_path.name, "local_media_dir")
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(input_path, dest)
        copied.append(str(dest))
        candidates = [p for p in dest.rglob("*") if p.suffix.lower() in MEDIA_EXTS]
        media_for_audio = candidates[0] if candidates else None
    else:
        dest = dirs["media"] / f"original_{safe_name(input_path.name)}"
        shutil.copy2(input_path, dest)
        copied.append(str(dest))
        media_for_audio = dest if input_path.suffix.lower() in MEDIA_EXTS else None

    if media_for_audio:
        probe = ffprobe(media_for_audio)
        write_json(dirs["metadata"] / "ffprobe.json", probe)
        if extract:
            audio_path = dirs["media"] / "audio.m4a"
            audio_result = extract_audio(media_for_audio, audio_path, timeout)
            write_json(dirs["logs"] / "ffmpeg_extract_audio.json", audio_result)
    return {"ok": True, "copied": copied, "ffprobe": probe, "audio": audio_result}


def ytdlp_metadata(url: str, dirs: dict[str, Path], args: argparse.Namespace) -> dict[str, Any]:
    base = yt_dlp_command(no_uvx=args.no_uvx)
    if not base:
        message = "yt-dlp not found and uvx disabled/unavailable"
        write_text(dirs["logs"] / "yt_dlp_metadata.stdout.txt", "")
        write_text(dirs["logs"] / "yt_dlp_metadata.stderr.txt", message + "\n")
        return {"ok": False, "error": message}
    cmd = base + ["--no-playlist", "--dump-single-json"]
    if args.cookies_from_browser:
        cmd += ["--cookies-from-browser", args.cookies_from_browser]
    cmd += [url]
    res = run_cmd(cmd, args.timeout)
    write_text(dirs["logs"] / "yt_dlp_metadata.stdout.txt", res.get("stdout", ""))
    write_text(dirs["logs"] / "yt_dlp_metadata.stderr.txt", res.get("stderr", "") + ("\n" + res.get("error", "") if res.get("error") else ""))
    if not res["ok"]:
        return {"ok": False, "error": res.get("error") or res.get("stderr") or "yt-dlp metadata failed", "command": cmd}
    try:
        info = json.loads(res["stdout"])
    except json.JSONDecodeError as exc:
        return {"ok": False, "error": f"yt-dlp output was not JSON: {exc}", "command": cmd}
    write_json(dirs["metadata"] / "yt_dlp_info.json", info)
    return {"ok": True, "info": info, "command": cmd}


def ytdlp_download(url: str, dirs: dict[str, Path], args: argparse.Namespace) -> dict[str, Any]:
    base = yt_dlp_command(no_uvx=args.no_uvx)
    if not base:
        message = "yt-dlp not found and uvx disabled/unavailable"
        write_text(dirs["logs"] / "yt_dlp_download.stdout.txt", "")
        write_text(dirs["logs"] / "yt_dlp_download.stderr.txt", message + "\n")
        return {"ok": False, "error": message, "media_files": []}
    output_tpl = str(dirs["media"] / "%(id)s.%(ext)s")
    cmd = base + ["--no-playlist", "-f", args.format, "-o", output_tpl, "--write-info-json"]
    if args.cookies_from_browser:
        cmd += ["--cookies-from-browser", args.cookies_from_browser]
    cmd += [url]
    res = run_cmd(cmd, args.timeout)
    write_text(dirs["logs"] / "yt_dlp_download.stdout.txt", res.get("stdout", ""))
    write_text(dirs["logs"] / "yt_dlp_download.stderr.txt", res.get("stderr", "") + ("\n" + res.get("error", "") if res.get("error") else ""))
    media_files = [str(p) for p in dirs["media"].glob("*") if p.is_file()]
    return {"ok": bool(res["ok"]), "command": cmd, "media_files": media_files, "error": None if res["ok"] else (res.get("error") or res.get("stderr"))}


def pick_downloaded_media(dirs: dict[str, Path]) -> Path | None:
    candidates = [p for p in dirs["media"].glob("*") if p.is_file() and p.suffix.lower() in MEDIA_EXTS]
    if not candidates:
        return None
    candidates.sort(key=lambda p: p.stat().st_size, reverse=True)
    return candidates[0]


def summarize_info(info: dict[str, Any] | None, input_value: str, item_id: str) -> dict[str, Any]:
    info = info or {}
    keys = [
        "id",
        "title",
        "description",
        "uploader",
        "uploader_id",
        "creator",
        "channel_id",
        "duration",
        "timestamp",
        "upload_date",
        "webpage_url",
        "view_count",
        "like_count",
        "comment_count",
        "repost_count",
        "thumbnail",
    ]
    summary = {k: info.get(k) for k in keys if info.get(k) is not None}
    summary.setdefault("id", item_id)
    summary["input"] = input_value
    summary["generated_at"] = now_iso()
    return summary


def write_index(dirs: dict[str, Path], summary: dict[str, Any], status: dict[str, Any]) -> None:
    title = summary.get("title") or summary.get("id") or "抖音内容"
    desc = summary.get("description") or ""
    lines = [
        f"# {title}",
        "",
        "## 元数据摘要",
        "",
    ]
    for key in ["id", "uploader", "creator", "duration", "upload_date", "timestamp", "webpage_url", "view_count", "like_count", "comment_count", "repost_count"]:
        if summary.get(key) is not None:
            lines.append(f"- {key}: {summary[key]}")
    lines += ["", "## 原始文案 / 简介", "", desc or "（未从当前路线提取到简介或文案）", "", "## 转写状态", ""]
    if status.get("audio_extracted"):
        lines.append("已抽取音频：`media/audio.m4a`。需要后续 ASR 转写后再写完整笔记。")
    elif status.get("downloaded_media"):
        lines.append("已下载媒体，但未抽音频。需要时重跑 `--extract-audio` 或接入 ASR。")
    else:
        lines.append("当前未获得可转写媒体；只能基于元数据/简介做有限摘要。")
    lines += ["", "## 覆盖与局限", ""]
    for item in status.get("limitations", []):
        lines.append(f"- {item}")
    write_text(dirs["indexes"] / "文案与元数据.md", "\n".join(lines) + "\n")


def write_budget(dirs: dict[str, Path], summary: dict[str, Any], status: dict[str, Any]) -> None:
    desc_chars = len(summary.get("description") or "")
    has_media = bool(status.get("downloaded_media") or status.get("local_media"))
    min_chars = 800 if has_media else 300
    max_chars = 2500 if has_media else 1000
    write_json(
        dirs["metadata"] / "note_budget.json",
        {
            "generated_at": now_iso(),
            "input_basis": "media" if has_media else "metadata_only",
            "description_chars": desc_chars,
            "recommended_note_chars_min": min_chars,
            "recommended_note_chars_max": max_chars,
            "writing_guidance": "完整媒体/转写可用时写内容消化笔记；只有元数据时只写有限摘要并标注局限。",
            "status": status,
        },
    )


def write_report(dirs: dict[str, Path], input_value: str, summary: dict[str, Any], status: dict[str, Any]) -> None:
    lines = [
        "# douyin-note run report",
        "",
        f"- generated_at: {now_iso()}",
        f"- input: {input_value}",
        f"- archive_dir: {dirs['root']}",
        "",
        "## Steps",
        "",
    ]
    for step in status.get("steps", []):
        marker = "OK" if step.get("ok") else "FAILED"
        lines.append(f"- {marker}: {step.get('name')} — {step.get('message', '')}")
    lines += ["", "## Summary", ""]
    for key in ["id", "title", "uploader", "creator", "duration", "webpage_url"]:
        if summary.get(key) is not None:
            lines.append(f"- {key}: {summary[key]}")
    if status.get("next_steps"):
        lines += ["", "## Next steps", ""]
        for item in status["next_steps"]:
            lines.append(f"- {item}")
    write_text(dirs["root"] / "douyin_note_run_report.md", "\n".join(lines) + "\n")


def build_archive(input_value: str, args: argparse.Namespace) -> int:
    item_id = infer_id(input_value)
    work_dir = Path(args.work_dir).expanduser().resolve()
    archive_dir = Path(args.archive_dir).expanduser().resolve() if args.archive_dir else work_dir / f"D{item_id}_{safe_name(item_id)}"
    dirs = ensure_layout(archive_dir)
    work_dir.mkdir(parents=True, exist_ok=True)

    status: dict[str, Any] = {
        "steps": [],
        "limitations": [],
        "next_steps": [],
        "local_media": False,
        "downloaded_media": False,
        "audio_extracted": False,
    }
    write_json(dirs["metadata"] / "input.json", {"input": input_value, "id": item_id, "is_url": is_url(input_value), "created_at": now_iso()})

    info: dict[str, Any] | None = None

    if is_url(input_value):
        meta = ytdlp_metadata(input_value, dirs, args)
        status["steps"].append({"name": "yt-dlp metadata", "ok": meta["ok"], "message": "metadata saved" if meta["ok"] else meta.get("error", "failed")})
        if meta.get("ok"):
            info = meta["info"]
        else:
            status["limitations"].append("yt-dlp 未能解析 URL；详见 logs/yt_dlp_metadata.stderr.txt。")
            status["next_steps"].append("如果浏览器可打开该抖音链接，重跑时尝试 `--cookies-from-browser chrome`。")
            status["next_steps"].append("如果仍失败，改用本地下载视频输入，或接入 jiji262/douyin-downloader 专用路线。")

        if args.download_media:
            dl = ytdlp_download(input_value, dirs, args)
            status["steps"].append({"name": "yt-dlp download", "ok": dl["ok"], "message": "media files saved" if dl["ok"] else (dl.get("error") or "download failed")})
            status["downloaded_media"] = bool(dl.get("media_files"))
            if not dl["ok"]:
                status["limitations"].append("媒体下载未成功；详见 logs/yt_dlp_download.stderr.txt。")
    else:
        local = copy_local_input(Path(input_value).expanduser(), dirs, args.extract_audio, args.timeout)
        status["steps"].append({"name": "local media archive", "ok": local["ok"], "message": "local input copied" if local["ok"] else local.get("error", "failed")})
        status["local_media"] = bool(local.get("ok"))
        if local.get("audio"):
            status["audio_extracted"] = bool(local["audio"].get("ok"))
            if not status["audio_extracted"]:
                status["limitations"].append(f"音频抽取失败：{local['audio'].get('error') or local['audio'].get('stderr') or 'unknown error'}")
        if not local.get("ok"):
            status["limitations"].append(local.get("error", "本地输入归档失败。"))

    if args.extract_audio and is_url(input_value):
        media = pick_downloaded_media(dirs)
        if media:
            audio = extract_audio(media, dirs["media"] / "audio.m4a", args.timeout)
            write_json(dirs["logs"] / "ffmpeg_extract_audio.json", audio)
            status["audio_extracted"] = bool(audio.get("ok"))
            status["steps"].append({"name": "ffmpeg extract audio", "ok": audio.get("ok"), "message": "media/audio.m4a saved" if audio.get("ok") else (audio.get("error") or audio.get("stderr") or "failed")})
            if not audio.get("ok"):
                status["limitations"].append("音频抽取失败；详见 logs/ffmpeg_extract_audio.json。")
        else:
            status["steps"].append({"name": "ffmpeg extract audio", "ok": False, "message": "no downloaded media found"})
            status["limitations"].append("请求了抽音频，但没有找到已下载媒体。")

    if args.comments:
        status["steps"].append({"name": "comments", "ok": False, "message": "comments require a vetted native Douyin tool; not attempted in this minimal runner"})
        status["limitations"].append("评论区未抓取：当前最小 runner 不直接调用未审查的抖音专用爬虫。")

    if status["audio_extracted"]:
        status["next_steps"].append("对 media/audio.m4a 做 ASR 转写，再基于转写写完整笔记。")
    elif status["downloaded_media"] or status["local_media"]:
        status["next_steps"].append("如需完整文案，安装/配置 ASR 后转写媒体音频。")

    summary = summarize_info(info, input_value, item_id)
    write_json(dirs["metadata"] / "summary.json", summary)
    write_budget(dirs, summary, status)
    write_index(dirs, summary, status)
    write_report(dirs, input_value, summary, status)
    print(json.dumps({"ok": True, "archive_dir": str(dirs["root"]), "report": str(dirs["root"] / "douyin_note_run_report.md"), "status": status}, ensure_ascii=False, indent=2))
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Archive Douyin URL or local media for later transcription and note writing.")
    parser.add_argument("input", help="Douyin URL/share link or local media file/directory.")
    parser.add_argument("--work-dir", default="./tmp_douyin_note", help="Working directory. Default: ./tmp_douyin_note")
    parser.add_argument("--archive-dir", default="", help="Archive output directory. Default: work-dir/D<id>_<id>")
    parser.add_argument("--download-media", action="store_true", help="Download media for URL inputs using yt-dlp.")
    parser.add_argument("--extract-audio", action="store_true", help="Extract media/audio.m4a with ffmpeg when media is available.")
    parser.add_argument("--comments", action="store_true", help="Record comment intent; actual comment scraping requires a vetted native tool.")
    parser.add_argument("--cookies-from-browser", default="", metavar="BROWSER", help="Pass through to yt-dlp, e.g. chrome, edge, firefox.")
    parser.add_argument("--format", default="bv*+ba/b", help="yt-dlp format selector. Default: bv*+ba/b")
    parser.add_argument("--timeout", type=int, default=180, help="Per-command timeout seconds. Default: 180")
    parser.add_argument("--no-uvx", action="store_true", help="Do not use uvx to run yt-dlp on demand.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    return build_archive(args.input, args)


if __name__ == "__main__":
    raise SystemExit(main())
