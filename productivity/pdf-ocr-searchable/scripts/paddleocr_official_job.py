#!/usr/bin/env python3
"""Run Baidu Qianfan / AI Studio official PaddleOCR-VL job API and download JSONL/Markdown/images.

Default model: PaddleOCR-VL-1.6.
Token is read from PADDLEOCR_TOKEN or --token. Do not hardcode tokens.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import time
from typing import Any
from urllib.parse import urlparse

try:
    import requests
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Missing dependency: requests. Install with:\n"
        "  python -m pip install requests\n"
        "or: uv pip install requests"
    ) from exc

JOB_URL = "https://paddleocr.aistudio-app.com/api/v2/ocr/jobs"
DEFAULT_MODEL = "PaddleOCR-VL-1.6"
DEFAULT_TOKEN_ENV_FILE = Path(os.environ["PADDLEOCR_TOKEN_FILE"]).expanduser() if os.environ.get("PADDLEOCR_TOKEN_FILE") else None


def load_token_from_env_file(path: Path | None = DEFAULT_TOKEN_ENV_FILE) -> str | None:
    """Load PADDLEOCR_TOKEN from an optional local dotenv-style file."""
    if path is None or not path.exists():
        return None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key.strip() == "PADDLEOCR_TOKEN":
            return value.strip().strip('"').strip("'") or None
    return None


def parse_bool(value: str) -> bool:
    lowered = value.lower()
    if lowered in {"1", "true", "yes", "y", "on"}:
        return True
    if lowered in {"0", "false", "no", "n", "off"}:
        return False
    raise argparse.ArgumentTypeError(f"not a boolean: {value}")


def safe_filename(name: str, fallback: str) -> str:
    cleaned = "".join(c if c.isalnum() or c in "._-" else "_" for c in name).strip("._")
    return cleaned or fallback


def download(url: str, path: Path, session: requests.Session) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    response = session.get(url, timeout=120)
    response.raise_for_status()
    path.write_bytes(response.content)


def submit_job(args: argparse.Namespace, session: requests.Session, headers: dict[str, str]) -> str:
    optional_payload = {
        "useDocOrientationClassify": args.use_doc_orientation_classify,
        "useDocUnwarping": args.use_doc_unwarping,
        "useChartRecognition": args.use_chart_recognition,
    }

    if args.input.startswith(("http://", "https://")):
        headers = {**headers, "Content-Type": "application/json"}
        payload = {
            "fileUrl": args.input,
            "model": args.model,
            "optionalPayload": optional_payload,
        }
        response = session.post(JOB_URL, json=payload, headers=headers, timeout=120)
    else:
        input_path = Path(args.input).expanduser()
        if not input_path.exists():
            raise SystemExit(f"Input file not found: {input_path}")
        data = {
            "model": args.model,
            "optionalPayload": json.dumps(optional_payload, ensure_ascii=False),
        }
        with input_path.open("rb") as file_obj:
            files = {"file": file_obj}
            response = session.post(JOB_URL, headers=headers, data=data, files=files, timeout=120)

    if response.status_code != 200:
        raise SystemExit(f"Submit failed: HTTP {response.status_code}\n{response.text}")

    payload = response.json()
    try:
        return payload["data"]["jobId"]
    except KeyError as exc:
        raise SystemExit(f"Submit response did not contain data.jobId:\n{json.dumps(payload, ensure_ascii=False, indent=2)}") from exc


def poll_job(job_id: str, session: requests.Session, headers: dict[str, str], interval: float, timeout: float) -> dict[str, Any]:
    deadline = time.time() + timeout
    last_state = None
    while True:
        if time.time() > deadline:
            raise SystemExit(f"Timed out waiting for job {job_id}")
        response = session.get(f"{JOB_URL}/{job_id}", headers=headers, timeout=60)
        if response.status_code != 200:
            raise SystemExit(f"Poll failed: HTTP {response.status_code}\n{response.text}")
        payload = response.json()
        data = payload.get("data", {})
        state = data.get("state")
        if state != last_state:
            print(f"state={state}", flush=True)
            last_state = state
        if state == "running":
            progress = data.get("extractProgress", {})
            total = progress.get("totalPages")
            extracted = progress.get("extractedPages")
            if total is not None or extracted is not None:
                print(f"running: extracted={extracted} total={total}", flush=True)
        elif state == "pending":
            print("pending", flush=True)
        elif state == "done":
            return payload
        elif state == "failed":
            raise SystemExit(f"Job failed: {data.get('errorMsg', 'unknown error')}")
        elif state:
            print(f"unknown state={state}; keep polling", flush=True)
        time.sleep(interval)


def extract_results(job_payload: dict[str, Any], output_dir: Path, session: requests.Session) -> dict[str, Any]:
    data = job_payload.get("data", {})
    result_url = data.get("resultUrl", {})
    jsonl_url = result_url.get("jsonUrl")
    if not jsonl_url:
        raise SystemExit(f"No resultUrl.jsonUrl in job result:\n{json.dumps(job_payload, ensure_ascii=False, indent=2)}")

    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_response = session.get(jsonl_url, timeout=120)
    jsonl_response.raise_for_status()
    jsonl_text = jsonl_response.text
    jsonl_path = output_dir / "result.jsonl"
    jsonl_path.write_text(jsonl_text, encoding="utf-8")

    combined_md: list[str] = []
    page_num = 0
    md_files: list[str] = []
    image_files: list[str] = []

    for line_num, line in enumerate(jsonl_text.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            line_payload = json.loads(line)
            result = line_payload["result"]
        except (json.JSONDecodeError, KeyError) as exc:
            raise SystemExit(f"Bad JSONL line {line_num}: {line[:500]}") from exc

        for res in result.get("layoutParsingResults", []):
            page_label = f"page_{page_num:04d}"
            markdown = res.get("markdown", {})
            md_text = markdown.get("text", "")
            md_path = output_dir / f"{page_label}.md"
            md_path.write_text(md_text, encoding="utf-8")
            md_files.append(str(md_path))
            combined_md.append(f"\n\n<!-- {page_label} -->\n\n{md_text}")

            for img_path, img_url in markdown.get("images", {}).items():
                rel = Path("markdown_images") / page_label / img_path
                target = output_dir / rel
                download(img_url, target, session)
                image_files.append(str(target))

            for img_name, img_url in res.get("outputImages", {}).items():
                parsed = urlparse(img_url)
                suffix = Path(parsed.path).suffix or ".jpg"
                file_name = f"{safe_filename(img_name, 'image')}_{page_num:04d}{suffix}"
                target = output_dir / "output_images" / file_name
                download(img_url, target, session)
                image_files.append(str(target))

            page_num += 1

    combined_path = output_dir / "combined.md"
    combined_path.write_text("".join(combined_md).strip() + "\n", encoding="utf-8")

    metadata_path = output_dir / "job_result.json"
    metadata_path.write_text(json.dumps(job_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "jsonl": str(jsonl_path),
        "combined_markdown": str(combined_path),
        "metadata": str(metadata_path),
        "pages": page_num,
        "markdown_files": md_files,
        "image_files": image_files,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Official PaddleOCR-VL job API downloader")
    parser.add_argument("input", help="Local PDF/image path or remote file URL")
    parser.add_argument("-o", "--output-dir", default="output", help="Directory for JSONL/Markdown/images")
    parser.add_argument(
        "--token",
        default=os.environ.get("PADDLEOCR_TOKEN") or load_token_from_env_file(),
        help="API token; default from PADDLEOCR_TOKEN or optional PADDLEOCR_TOKEN_FILE dotenv file",
    )
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--poll-interval", type=float, default=5)
    parser.add_argument("--timeout", type=float, default=3600)
    parser.add_argument("--use-doc-orientation-classify", type=parse_bool, default=False)
    parser.add_argument("--use-doc-unwarping", type=parse_bool, default=False)
    parser.add_argument("--use-chart-recognition", type=parse_bool, default=False)
    args = parser.parse_args()

    if not args.token:
        raise SystemExit(
            "Missing token. Set PADDLEOCR_TOKEN, pass --token, or set PADDLEOCR_TOKEN_FILE to a local dotenv file."
        )

    session = requests.Session()
    headers = {"Authorization": f"bearer {args.token}"}

    print(f"Submitting {args.input} to {args.model}", flush=True)
    job_id = submit_job(args, session, headers)
    print(f"job_id={job_id}", flush=True)
    job_payload = poll_job(job_id, session, headers, args.poll_interval, args.timeout)
    outputs = extract_results(job_payload, Path(args.output_dir).expanduser(), session)
    print(json.dumps({"ok": True, "job_id": job_id, "outputs": outputs}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
