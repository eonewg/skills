#!/usr/bin/env python3
"""Check local routes available for douyin-note."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


def command_exists(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def run_version(cmd: list[str], timeout: int = 8) -> dict[str, Any]:
    try:
        proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
        out = (proc.stdout or proc.stderr or "").strip().splitlines()
        return {"ok": proc.returncode == 0, "version": out[0] if out else "", "returncode": proc.returncode}
    except Exception as exc:  # pragma: no cover - environment-specific
        return {"ok": False, "version": "", "error": str(exc)}


def detect() -> dict[str, Any]:
    python = sys.executable
    uvx = shutil.which("uvx") or shutil.which("uv")
    yt_dlp = shutil.which("yt-dlp")
    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    native_home = os.environ.get("DOUYIN_DOWNLOADER_HOME", "").strip()

    if yt_dlp:
        yt_dlp_cmd = [yt_dlp]
        yt_dlp_source = "system"
    elif shutil.which("uvx"):
        yt_dlp_cmd = ["uvx", "--from", "yt-dlp", "yt-dlp"]
        yt_dlp_source = "uvx"
    else:
        yt_dlp_cmd = []
        yt_dlp_source = "missing"

    result: dict[str, Any] = {
        "python": {"path": python, "version": sys.version.split()[0]},
        "uv_or_uvx": {"path": uvx, "available": bool(uvx)},
        "yt_dlp": {
            "path": yt_dlp,
            "source": yt_dlp_source,
            "command": yt_dlp_cmd,
            "available": bool(yt_dlp_cmd),
        },
        "ffmpeg": {"path": ffmpeg, "available": bool(ffmpeg)},
        "ffprobe": {"path": ffprobe, "available": bool(ffprobe)},
        "native_douyin_downloader": {
            "env": "DOUYIN_DOWNLOADER_HOME",
            "path": native_home or None,
            "available": bool(native_home and Path(native_home).exists()),
        },
    }

    if yt_dlp_cmd and yt_dlp_source == "system":
        result["yt_dlp"].update(run_version(yt_dlp_cmd + ["--version"]))
    elif yt_dlp_cmd:
        result["yt_dlp"]["version"] = "available via uvx on demand"

    if ffmpeg:
        result["ffmpeg"].update(run_version([ffmpeg, "-version"]))
    if ffprobe:
        result["ffprobe"].update(run_version([ffprobe, "-version"]))

    result["routes"] = {
        "local_file_archive": {
            "status": "OK",
            "reason": "Python is available; local media can be copied into an archive.",
        },
        "url_metadata_with_ytdlp": {
            "status": "OK" if yt_dlp_cmd else "MISSING",
            "reason": "yt-dlp command is available" if yt_dlp_cmd else "Install yt-dlp or uvx to try URL parsing.",
        },
        "media_download_with_ytdlp": {
            "status": "OK" if yt_dlp_cmd else "MISSING",
            "reason": "Can call yt-dlp directly or through uvx." if yt_dlp_cmd else "No downloader command found.",
        },
        "audio_extract_with_ffmpeg": {
            "status": "OK" if ffmpeg else "MISSING",
            "reason": "ffmpeg is available." if ffmpeg else "Install ffmpeg before --extract-audio.",
        },
        "native_douyin_tool": {
            "status": "CONFIGURED" if result["native_douyin_downloader"]["available"] else "NOT_CONFIGURED",
            "reason": "DOUYIN_DOWNLOADER_HOME points to an existing directory." if result["native_douyin_downloader"]["available"] else "Optional; set only after vetting a third-party Douyin tool.",
        },
    }
    return result


def print_human(data: dict[str, Any]) -> None:
    print("douyin-note environment")
    print(f"- python: {data['python']['path']} ({data['python']['version']})")
    print(f"- uv/uvx: {data['uv_or_uvx']['path'] or 'missing'}")
    print(f"- yt-dlp: {data['yt_dlp']['source']} ({' '.join(data['yt_dlp']['command']) if data['yt_dlp']['command'] else 'missing'})")
    print(f"- ffmpeg: {data['ffmpeg']['path'] or 'missing'}")
    print(f"- ffprobe: {data['ffprobe']['path'] or 'missing'}")
    print(f"- native tool: {data['native_douyin_downloader']['path'] or 'not configured'}")
    print("\nroutes:")
    for name, route in data["routes"].items():
        print(f"- {name}: {route['status']} — {route['reason']}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check douyin-note dependencies and routes.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()
    data = detect()
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print_human(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
