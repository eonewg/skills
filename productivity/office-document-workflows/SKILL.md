---
name: office-document-workflows
description: Unified guidance for creating, editing, converting, extracting, and validating DOCX, XLSX, PPTX, PDF, OCR, and document-intelligence workflows. Use when working with Office files, PDFs, Markdown conversion, OCR/document extraction, or provider-specific document generation pipelines.
---

# Office Document Workflows

## Overview
This umbrella skill consolidates document-format-specific skills into one class-level entry organized by file type and operation class.

## Core workflow
1. Identify the source and target format.
2. Decide whether the job is create, edit, convert, extract, validate, or OCR.
3. Prefer format-native tooling for editable outputs; prefer OCR/document-intelligence only when layout extraction or scanned content is involved.
4. Verify output fidelity with a read-back or spot-check.

## Consolidated subsections
### Word / DOCX
Creation, editing, formatting preservation, and provider-specific DOCX pipelines.

### Spreadsheets / XLSX
Open, create, analyze, validate, and export spreadsheet data while preserving types and formulas where possible.

### PowerPoint / PPTX
Generate or edit slide decks, templates, and presentation structures. The absorbed standalone PowerPoint package is preserved under `references/powerpoint/` with its original `SKILL.md`, `editing.md`, `pptxgenjs.md`, and license; its reusable helper scripts and schemas are re-homed under `scripts/powerpoint/`. When following the absorbed docs, adjust old paths from `scripts/...` to `scripts/powerpoint/...`.

### PDF and visual document output
Use PDF pipelines when visual fidelity and final-form output matter more than editability.

### OCR, conversion, and document intelligence
Use OCR/extraction tools for scanned documents, layout understanding, image/PDF question answering, or broad format-to-Markdown conversion.

## Absorbed specialized skills
- `DOCX`, `docx-cn`, and `minimax-docx` — Word document creation/editing pipelines.
- `XLSX` and `minimax-xlsx` — spreadsheet read/write/analysis workflows.
- `pptx-generator`, `ai-ppt-generator`, and `powerpoint` — presentation generation/editing flows, including the preserved standalone PowerPoint helper package.
- `minimax-pdf` — high-fidelity PDF production.
- `markdown-converter` and `markdown-formatter` — format-to-Markdown conversion plus Markdown cleanup/beautification before publishing.
- `nutrient-openclaw` and `qianfanocr-document-intelligence` — OCR, extraction, and document-intelligence operations.

## Navigation
Absorbed format- and provider-specific notes are stored in `references/`.
- `references/headless-chrome-html-to-pdf.md` — fallback for polished PDF deliverables: author self-contained HTML/CSS, render via headless Chrome, verify, then copy into an email-allowed directory if needed.

## Common pitfalls
- If Python PDF libraries/converters are missing, don't stall: generate a self-contained HTML handout and render it with headless Chrome; see `references/headless-chrome-html-to-pdf.md`.
- Using OCR on born-digital documents that should be parsed natively.
- Converting to Markdown when native editing is required.
- Treating PDF as an editable source of truth.
- Skipping output verification on tables, dates, formulas, and layouts.

## Verification checklist
- [ ] Correct file type and operation class identified.
- [ ] Native parser/editor chosen when available.
- [ ] OCR/document-intelligence used only when justified.
- [ ] Output spot-checked for structure, formatting, and data fidelity.
