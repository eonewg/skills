# OCRmyPDF + PaddleOCR Hybrid Searchable PDF Pattern

Use this when OCRmyPDF/Tesseract is installed and runs successfully, but Chinese phrase search from the Tesseract-only text layer is noisy because Tesseract inserts spaces or misrecognizes Chinese/math-heavy textbook content.

## Pattern

1. Run OCRmyPDF first to produce the coordinate-aligned searchable PDF and preserve the original page visuals:

```bash
ocrmypdf -l chi_sim+eng \
  --deskew \
  --rotate-pages \
  --skip-text \
  --output-type pdfa \
  input.pdf input_ocrmypdf.pdf
```

2. Run official PaddleOCR-VL separately to produce `result.jsonl` and `combined.md`.

3. Create the delivered PDF from `input_ocrmypdf.pdf`, not from the original PDF. Parse PaddleOCR `result.jsonl`, read each page's:

```text
result.layoutParsingResults[].prunedResult.width
result.layoutParsingResults[].prunedResult.height
result.layoutParsingResults[].prunedResult.parsing_res_list[].block_bbox
result.layoutParsingResults[].prunedResult.parsing_res_list[].block_content
```

4. Map each `block_bbox` from OCR image coordinates to PDF page coordinates:

```python
sx = page.rect.width / ocr_width
sy = page.rect.height / ocr_height
rect = fitz.Rect(x0 * sx, y0 * sy, x1 * sx, y1 * sy)
```

5. Insert PaddleOCR text invisibly with a Chinese-capable built-in font:

```python
page.insert_textbox(
    rect,
    text,
    fontname="china-s",
    fontsize=max(4, min(12, rect.height * 0.42)),
    render_mode=3,
    overlay=True,
)
```

If `insert_textbox` reports overflow, fall back to `page.insert_text((rect.x0, rect.y0 + fontsize), ...)`.

## Why

OCRmyPDF/Tesseract gives better coordinate-level selection and copy behavior, but for Chinese textbooks it may insert spaces between characters and weaken exact phrase search. PaddleOCR-VL Markdown/block text is usually cleaner for semantic Chinese phrases. Overlaying both layers gives:

- OCRmyPDF/Tesseract: coordinate fit and PDF/A normalization.
- PaddleOCR-VL: cleaner Chinese phrase search and better formulas/tables in Markdown.

## Verification

Use PyMuPDF to verify:

```python
doc = fitz.open("output.pdf")
print(doc.page_count)
for needle in ["多元函数", "偏导数", "极值"]:
    print(needle, sum(1 for p in doc if needle in p.get_text()))
```

return only the final searchable PDF named with `(ocr)` before the extension, e.g. `第十三讲(ocr).pdf`. Keep PaddleOCR `combined.md`/renamed `.md` as an internal artifact unless the user explicitly asks for Markdown or troubleshooting requires it. Mention a caveat only if the user asks about precision: the delivered PDF has OCRmyPDF's coordinate layer plus a block-level PaddleOCR semantic layer, so search is stronger than pure Tesseract while selection may include overlapping hidden text layers.
