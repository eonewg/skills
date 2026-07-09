---
name: pdf-ocr-searchable
description: Use when converting scanned/image PDFs into coordinate-aligned searchable PDFs and structured Markdown. Prefer OCRmyPDF/Tesseract for PDF text layers; use official PaddleOCR-VL job API for Markdown/layout extraction. Legacy SiliconFlow VLM path remains a fallback only.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [pdf, ocr, searchable-pdf, ocrmypdf, paddleocr, vlm]
    related_skills: [ocr-and-documents]
---

# Searchable PDF + PaddleOCR-VL Extraction

## Overview

There are three PDF OCR workflows:

- **Coordinate-first / preferred for real searchable PDFs:** use `~/.hermes/scripts/ocrmypdf_searchable_pdf.sh`, which wraps OCRmyPDF + Tesseract. This produces a text layer with word/line coordinates that tracks scanned glyphs closely, so search, selection, and copy/paste behave like a normal OCRed book.
- **Official PaddleOCR-VL extraction / preferred for structured Markdown:** use `~/.hermes/scripts/paddleocr_official_job.py`, which calls Baidu AI Studio's official `PaddleOCR-VL-1.6` async job API, downloads JSONL, page Markdown, combined Markdown, and extracted images. Token comes from `PADDLEOCR_TOKEN`, `--token`, or local private env file `~/.hermes/secrets/paddleocr.env`.
- **Legacy SiliconFlow VLM fallback:** use `~/.hermes/scripts/siliconflow_pdf_ocr.py` only if the official API is unavailable. SiliconFlow chat-completions returns text/Markdown rather than word-level boxes, so it is not the preferred PDF text-layer engine.

Best combined pipeline:

1. Run OCRmyPDF with Tesseract (`chi_sim+eng` by default) to produce the coordinate-aligned searchable PDF.
2. Separately run the official PaddleOCR-VL job API to produce Markdown/layout assets for study notes, tables/formulas, and QA.
3. For Chinese/math-heavy study PDFs, deliver a hybrid searchable PDF when useful: start from OCRmyPDF output, then overlay PaddleOCR-VL block text invisibly via PyMuPDF to improve exact Chinese phrase search while retaining OCRmyPDF's coordinate layer. See `references/ocrmypdf-paddleocr-hybrid.md`.
4. Do **not** use plain VLM text as the authoritative hidden PDF text layer unless the API returns word-level boxes and a mapper is implemented.

## Default User-Facing Behavior

When the user sends a PDF and asks for OCR, process it without asking extra questions unless the file is missing or the OCR pipeline is blocked. Default delivery is only the processed searchable PDF:

- Output filename should append `(ocr)` to the original title before the extension, e.g. `第十三讲.pdf` → `第十三讲(ocr).pdf`.
- Send only the processed PDF back to chat by default.
- Generate Markdown only if explicitly requested, needed for troubleshooting, or useful as an internal intermediate; do not send the Markdown by default.

Keep the response short: mention success, output filename, and any major OCR caveat only if verification found one.

## When to Use

- User sends a scanned PDF and wants OCR output to remain a PDF.
- User asks for a searchable/copyable PDF rather than only `.txt` / `.md` extraction.
- Chinese, mixed Chinese-English, tables, formulas, or layout-heavy PDFs need structured Markdown extraction.
- The original PDF is image-only or has poor/missing text layer.

Do not use this when:

- The PDF already has a good text layer and the user only needs text extraction; use lightweight PyMuPDF extraction instead.
- User needs legal/archive-grade perfect OCR coordinates beyond what Tesseract/OCRmyPDF can provide; manually spot-check or use a bbox-capable OCR engine.

## Coordinate-Aligned Searchable PDF

Install once if missing:

```bash
sudo apt-get update
sudo apt-get install -y ocrmypdf tesseract-ocr tesseract-ocr-chi-sim tesseract-ocr-eng
```

Default wrapper:

```bash
~/.hermes/scripts/ocrmypdf_searchable_pdf.sh input.pdf
```

Direct command:

```bash
ocrmypdf -l chi_sim+eng \
  --deskew \
  --rotate-pages \
  --skip-text \
  --output-type pdfa \
  input.pdf input_ocr.pdf
```

Use `--force-ocr` only when the PDF has a bad existing text layer and should be redone:

```bash
ocrmypdf -l chi_sim+eng --deskew --rotate-pages --force-ocr --output-type pdfa input.pdf input_ocr.pdf
```

Use `--clean` cautiously. It is usually helpful for black/white scans, but can damage visual details in colorful textbooks or diagrams.

## Official PaddleOCR-VL Structured Extraction

Run:

```bash
~/.hermes/venvs/siliconflow-ocr/bin/python \
  ~/.hermes/scripts/paddleocr_official_job.py \
  input.pdf \
  -o input_paddleocr
```

The script reads token in this priority:

1. `--token TOKEN`
2. `PADDLEOCR_TOKEN` environment variable
3. `~/.hermes/secrets/paddleocr.env`

Official API outputs:

- `input_paddleocr/result.jsonl` — raw official result JSONL.
- `input_paddleocr/job_result.json` — final job metadata.
- `input_paddleocr/page_0000.md`, `page_0001.md`, ... — page Markdown.
- `input_paddleocr/combined.md` — merged Markdown.
- `input_paddleocr/markdown_images/` and `output_images/` — downloaded extracted images.

Useful official API options:

```bash
~/.hermes/venvs/siliconflow-ocr/bin/python \
  ~/.hermes/scripts/paddleocr_official_job.py input.pdf \
  -o input_paddleocr \
  --use-doc-orientation-classify true \
  --use-doc-unwarping true \
  --use-chart-recognition true
```

## Legacy SiliconFlow Fallback

Only use this if official PaddleOCR API is unavailable and the user mainly needs text/Markdown rather than coordinate-accurate PDF selection:

```bash
export SILICONFLOW_API_KEY='***'
~/.hermes/scripts/siliconflow_pdf_ocr.py input.pdf
```

Outputs:

- `input_ocr.pdf` — original visual PDF plus invisible page-level searchable text layer.
- `input_ocr.pdf.md` — page-by-page OCR sidecar for quality inspection.

## Verification Checklist

After processing a real PDF:

- [ ] Confirm OCRmyPDF output PDF exists.
- [ ] Open the output PDF and search for a known phrase.
- [ ] For Chinese study PDFs, verify exact Chinese phrase hits with PyMuPDF, e.g. `多元函数`, `偏导数`, `极值`; if Tesseract spacing/noise hurts search, apply the hybrid PaddleOCR overlay from `references/ocrmypdf-paddleocr-hybrid.md`.
- [ ] Try selecting/copying text on several pages to check coordinate fit.
- [ ] Use PyMuPDF `page.get_text()` if CLI verification is needed.
- [ ] Confirm PaddleOCR output `combined.md` exists when structured extraction was requested.
- [ ] Spot-check formulas/tables/images manually.
- [ ] Never paste API tokens into skills, wiki pages, scripts, or logs.

## Common Pitfalls

1. **Hardcoding tokens.** Keep PaddleOCR token in `~/.hermes/secrets/paddleocr.env` or environment variables, not in skills/scripts.
2. **Using VLM text as PDF text layer.** Official PaddleOCR-VL Markdown is great for reading, but unless bbox data is mapped to PDF coordinates, OCRmyPDF remains the PDF text-layer engine.
3. **No sudo / missing OCRmyPDF.** If `ocrmypdf` / `tesseract` are missing and sudo is blocked, still deliver: run official PaddleOCR-VL, parse `result.jsonl` `layoutParsingResults[].prunedResult.parsing_res_list`, map each `block_bbox` from OCR image coordinates to PDF page coordinates, and insert invisible Chinese-capable text with PyMuPDF `fontname='china-s'`, `render_mode=3`. This produces a searchable PDF using block-level coordinates; mention the caveat if coordinate precision matters.
4. **OCRing already-text PDFs unnecessarily.** Use `--skip-text` by default; use `--force-ocr` only for bad existing text layers.
5. **Over-cleaning color documents.** `--clean` may alter visual details; start without it for color textbooks and diagram-heavy PDFs.
6. **Assuming OCR is perfect.** For exam/study material, spot-check formulas, tables, and unusual symbols.
