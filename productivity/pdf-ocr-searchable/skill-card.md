---
title: PDF OCR Searchable
slug: pdf-ocr-searchable
version: 1.0.2
author: Eone
license: MIT
tags:
  - pdf
  - ocr
  - searchable-pdf
  - ocrmypdf
  - paddleocr
  - siliconflow
  - baidu-qianfan
  - hermes-skill
---

# PDF OCR Searchable

Convert scanned/image PDFs into searchable PDFs with OCRmyPDF/Tesseract, plus optional PaddleOCR-VL structured Markdown and layout extraction.

## Highlights

- Coordinate-aligned searchable PDF output via OCRmyPDF.
- Chinese + English default OCR language configuration (`chi_sim+eng`).
- Official PaddleOCR-VL async job client for page Markdown, JSONL, layout blocks, tables, formulas, and extracted images. Uses Baidu Qianfan / AI Studio by default (`PaddleOCR-VL-1.6`).
- Legacy SiliconFlow VLM fallback via `PaddlePaddle/PaddleOCR-VL-1.5`.
- Hybrid OCRmyPDF + PaddleOCR pattern for stronger Chinese phrase search on study PDFs.
- Public-safe packaging: no API tokens, personal paths, generated OCR outputs, or private config files.

## Main files

- `SKILL.md` — agent-facing workflow instructions at repository root.
- `scripts/ocrmypdf_searchable_pdf.sh` — OCRmyPDF wrapper.
- `scripts/paddleocr_official_job.py` — official PaddleOCR-VL job client.
- `scripts/siliconflow_pdf_ocr.py` — legacy VLM fallback.
- `references/ocrmypdf-paddleocr-hybrid.md` — hybrid searchable PDF pattern.

## Best for

- Scanned Chinese/English study PDFs.
- Image-only PDFs that need search, copy, and selection behavior.
- Workflows that need both a searchable PDF and structured Markdown sidecar.
