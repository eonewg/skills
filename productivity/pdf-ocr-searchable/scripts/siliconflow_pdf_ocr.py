#!/usr/bin/env python3
"""Make a scanned PDF searchable with SiliconFlow PaddleOCR-VL.

Default model: PaddlePaddle/PaddleOCR-VL-1.5.
Pipeline:
  PDF page -> rendered PNG -> SiliconFlow chat/completions VLM OCR ->
  original visual PDF page + invisible OCR text layer -> searchable PDF.

The script does NOT hardcode API keys. Set SILICONFLOW_API_KEY in the environment.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import shlex
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

try:
    import fitz  # PyMuPDF
except Exception as exc:  # pragma: no cover
    raise SystemExit(
        "PyMuPDF is required. Install with: "
        "python -m pip install pymupdf pillow"
    ) from exc

API_URL = "https://api.siliconflow.cn/v1/chat/completions"
DEFAULT_MODEL = "PaddlePaddle/PaddleOCR-VL-1.5"
DEFAULT_PROMPT = """你是 OCR 引擎。请识别这张 PDF 页面图片中的全部可见文字。
要求：
- 按自然阅读顺序输出。
- 保留标题、段落、列表、页眉页脚中有意义的文字。
- 表格尽量用 Markdown 表格；无法确定时用按行文本。
- 数学公式尽量用 LaTeX 表达。
- 不要解释，不要总结，不要添加图片中不存在的内容。
- 如果页面没有文字，只输出空字符串。"""


def eprint(*args):
    print(*args, file=sys.stderr)


def parse_pages(spec: Optional[str], page_count: int) -> List[int]:
    """Parse 1-based page spec like '1,3-5' into 0-based indices."""
    if not spec:
        return list(range(page_count))
    pages = set()
    for part in spec.split(','):
        part = part.strip()
        if not part:
            continue
        if '-' in part:
            a, b = part.split('-', 1)
            start, end = int(a), int(b)
            if start > end:
                start, end = end, start
            for p in range(start, end + 1):
                pages.add(p - 1)
        else:
            pages.add(int(part) - 1)
    bad = [p + 1 for p in pages if p < 0 or p >= page_count]
    if bad:
        raise ValueError(f"page(s) out of range: {bad}; PDF has {page_count} pages")
    return sorted(pages)


def page_has_text(page: fitz.Page, min_chars: int = 20) -> bool:
    txt = page.get_text("text") or ""
    txt = re.sub(r"\s+", "", txt)
    return len(txt) >= min_chars


def render_page_png_b64(page: fitz.Page, dpi: int) -> str:
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    png_bytes = pix.tobytes("png")
    return base64.b64encode(png_bytes).decode("ascii")


def siliconflow_ocr_page(
    image_b64: str,
    api_key: str,
    model: str,
    prompt: str,
    max_tokens: int,
    temperature: float,
    timeout: int,
    retries: int,
) -> str:
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{image_b64}"},
                    },
                ],
            }
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    last_error = None
    for attempt in range(1, retries + 1):
        req = urllib.request.Request(API_URL, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
            data = json.loads(raw)
            return data["choices"][0]["message"].get("content", "") or ""
        except urllib.error.HTTPError as exc:
            err_body = exc.read().decode("utf-8", errors="replace")
            last_error = f"HTTP {exc.code}: {err_body[:1000]}"
            if exc.code not in (429, 500, 502, 503, 504):
                break
        except Exception as exc:
            last_error = repr(exc)
        if attempt < retries:
            time.sleep(min(2 ** attempt, 10))
    raise RuntimeError(f"SiliconFlow OCR request failed after {retries} attempt(s): {last_error}")


def add_invisible_text(page: fitz.Page, text: str) -> None:
    """Add a searchable invisible text layer over the page.

    Without OCR bounding boxes we cannot align every word perfectly. We use a tiny
    invisible textbox covering the whole page so search/copy works while the
    original scanned page appearance remains untouched.
    """
    if not text.strip():
        return
    rect = page.rect + (8, 8, -8, -8)
    clean = text.replace("\x00", "")
    # render_mode=3 means invisible text in PDF. Small font maximizes fit.
    remaining = clean
    font_size = 1.2
    # PyMuPDF insert_textbox returns negative leftover height when it does not fit.
    rc = page.insert_textbox(
        rect,
        remaining,
        fontsize=font_size,
        fontname="helv",
        color=(0, 0, 0),
        render_mode=3,
        overlay=True,
        align=fitz.TEXT_ALIGN_LEFT,
    )
    if rc < 0:
        # Fallback: shrink further and retry once.
        page.insert_textbox(
            rect,
            remaining,
            fontsize=0.6,
            fontname="helv",
            color=(0, 0, 0),
            render_mode=3,
            overlay=True,
            align=fitz.TEXT_ALIGN_LEFT,
        )


def make_output_doc(
    src_doc: fitz.Document,
    ocr_text_by_page: dict[int, str],
    selected_pages: Iterable[int],
) -> fitz.Document:
    out = fitz.open()
    selected = set(selected_pages)
    for i, src_page in enumerate(src_doc):
        out_page = out.new_page(width=src_page.rect.width, height=src_page.rect.height)
        out_page.show_pdf_page(out_page.rect, src_doc, i)
        if i in selected:
            add_invisible_text(out_page, ocr_text_by_page.get(i, ""))
    return out


def run_ocrmypdf_postprocess(input_pdf: Path, output_pdf: Path, extra_args: str = "") -> None:
    """Optionally run OCRmyPDF after our VLM OCR layer is created.

    OCRmyPDF is used here as a PDF postprocessor/optimizer, not as the OCR
    engine. `--skip-text` preserves pages that already contain our text layer.
    """
    if subprocess.run(["bash", "-lc", "command -v ocrmypdf >/dev/null 2>&1"]).returncode != 0:
        raise RuntimeError("ocrmypdf is not installed or not on PATH")
    tmp = output_pdf.with_suffix(output_pdf.suffix + ".ocrmypdf-tmp.pdf")
    cmd = [
        "ocrmypdf",
        "--skip-text",
        "--output-type", "pdf",
        "--optimize", "1",
    ]
    if extra_args.strip():
        cmd.extend(shlex.split(extra_args))
    cmd.extend([str(input_pdf), str(tmp)])
    eprint("[ocrmypdf]", " ".join(shlex.quote(x) for x in cmd))
    proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if proc.returncode != 0:
        if tmp.exists():
            tmp.unlink()
        raise RuntimeError(f"ocrmypdf postprocess failed with exit {proc.returncode}:\n{proc.stdout}")
    tmp.replace(output_pdf)


def existing_text_to_markdown(doc: fitz.Document, pages: Iterable[int]) -> dict[int, str]:
    return {i: doc[i].get_text("text") or "" for i in pages}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Use SiliconFlow PaddleOCR-VL to OCR scanned PDFs and produce searchable PDF + Markdown sidecar."
    )
    parser.add_argument("pdf", nargs="?", help="Input PDF path")
    parser.add_argument("-o", "--output", help="Output searchable PDF path. Default: <input>_ocr.pdf")
    parser.add_argument("--md-output", help="Markdown/text sidecar path. Default: <output>.md")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"SiliconFlow model. Default: {DEFAULT_MODEL}")
    parser.add_argument("--api-key", default=os.environ.get("SILICONFLOW_API_KEY"), help="API key; prefer env SILICONFLOW_API_KEY")
    parser.add_argument("--pages", help="1-based pages to OCR, e.g. '1,3-5'. Default: all pages")
    parser.add_argument("--dpi", type=int, default=180, help="Render DPI for OCR image. Default: 180")
    parser.add_argument("--max-tokens", type=int, default=4096, help="Max output tokens per page")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--force-ocr", action="store_true", help="OCR even pages that already have a text layer")
    parser.add_argument("--skip-existing-text", action="store_true", help="Do not include existing text-layer pages in sidecar")
    parser.add_argument("--prompt-file", help="Custom OCR prompt file")
    parser.add_argument("--postprocess-ocrmypdf", action="store_true", help="Run OCRmyPDF after VLM OCR to optimize/normalize the output PDF; uses --skip-text")
    parser.add_argument("--ocrmypdf-args", default="", help="Extra arguments appended to ocrmypdf postprocess, e.g. '--rotate-pages --deskew'")
    parser.add_argument("--self-test", action="store_true", help="Run local dependency/syntax smoke test; no API call")
    args = parser.parse_args()

    if args.self_test:
        print(json.dumps({"ok": True, "pymupdf": fitz.VersionBind, "model_default": DEFAULT_MODEL}, ensure_ascii=False))
        return 0

    if not args.pdf:
        parser.error("pdf is required unless --self-test is used")
    if not args.api_key:
        raise SystemExit("Missing API key. Set SILICONFLOW_API_KEY or pass --api-key.")

    in_path = Path(args.pdf).expanduser().resolve()
    if not in_path.exists():
        raise SystemExit(f"Input PDF not found: {in_path}")
    out_path = Path(args.output).expanduser().resolve() if args.output else in_path.with_name(in_path.stem + "_ocr.pdf")
    md_path = Path(args.md_output).expanduser().resolve() if args.md_output else out_path.with_suffix(out_path.suffix + ".md")
    prompt = Path(args.prompt_file).read_text(encoding="utf-8") if args.prompt_file else DEFAULT_PROMPT

    doc = fitz.open(in_path)
    pages = parse_pages(args.pages, doc.page_count)
    ocr_text: dict[int, str] = {}
    skipped_existing = []

    for idx in pages:
        page_no = idx + 1
        page = doc[idx]
        if page_has_text(page) and not args.force_ocr:
            skipped_existing.append(page_no)
            if not args.skip_existing_text:
                ocr_text[idx] = page.get_text("text") or ""
            eprint(f"[page {page_no}/{doc.page_count}] existing text layer detected; skipped OCR")
            continue
        eprint(f"[page {page_no}/{doc.page_count}] rendering at {args.dpi} dpi")
        image_b64 = render_page_png_b64(page, args.dpi)
        eprint(f"[page {page_no}/{doc.page_count}] calling {args.model}")
        text = siliconflow_ocr_page(
            image_b64=image_b64,
            api_key=args.api_key,
            model=args.model,
            prompt=prompt,
            max_tokens=args.max_tokens,
            temperature=args.temperature,
            timeout=args.timeout,
            retries=args.retries,
        )
        ocr_text[idx] = text.strip()
        eprint(f"[page {page_no}/{doc.page_count}] OCR chars: {len(ocr_text[idx])}")

    out_doc = make_output_doc(doc, ocr_text, pages)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_doc.save(out_path, garbage=4, deflate=True)
    out_doc.close()

    ocrmypdf_postprocessed = False
    if args.postprocess_ocrmypdf:
        run_ocrmypdf_postprocess(out_path, out_path, args.ocrmypdf_args)
        ocrmypdf_postprocessed = True

    md_lines = [f"# OCR: {in_path.name}", "", f"Model: `{args.model}`", ""]
    if skipped_existing:
        md_lines += [f"Skipped existing text-layer pages unless included from source: {skipped_existing}", ""]
    for idx in pages:
        text = ocr_text.get(idx, "")
        md_lines += [f"## Page {idx + 1}", "", text, ""]
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    print(json.dumps({
        "ok": True,
        "input": str(in_path),
        "output_pdf": str(out_path),
        "output_markdown": str(md_path),
        "pages_requested": [p + 1 for p in pages],
        "skipped_existing_text_pages": skipped_existing,
        "ocrmypdf_postprocessed": ocrmypdf_postprocessed,
        "model": args.model,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
