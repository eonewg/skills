#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  ocrmypdf_searchable_pdf.sh input.pdf [output.pdf] [extra ocrmypdf args...]

Coordinate-accurate searchable PDF workflow using OCRmyPDF/Tesseract.
Default language: chi_sim+eng
Default options: --rotate-pages --deskew --clean --skip-text --output-type pdfa

Examples:
  ocrmypdf_searchable_pdf.sh scan.pdf
  ocrmypdf_searchable_pdf.sh scan.pdf scan_ocr.pdf --jobs 4
  ocrmypdf_searchable_pdf.sh scan.pdf scan_ocr.pdf --force-ocr

Install if missing:
  sudo apt-get update
  sudo apt-get install -y ocrmypdf tesseract-ocr tesseract-ocr-chi-sim tesseract-ocr-eng
EOF
}

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  usage
  exit 0
fi

if [[ $# -lt 1 ]]; then
  usage >&2
  exit 2
fi

if ! command -v ocrmypdf >/dev/null 2>&1; then
  echo "ERROR: ocrmypdf is not installed." >&2
  echo "Install with:" >&2
  echo "  sudo apt-get update && sudo apt-get install -y ocrmypdf tesseract-ocr tesseract-ocr-chi-sim tesseract-ocr-eng" >&2
  exit 127
fi

input="$1"
shift

if [[ ! -f "$input" ]]; then
  echo "ERROR: input PDF not found: $input" >&2
  exit 2
fi

if [[ $# -gt 0 && "${1:-}" != --* ]]; then
  output="$1"
  shift
else
  dir="$(dirname "$input")"
  base="$(basename "$input")"
  stem="${base%.*}"
  output="$dir/${stem}_ocr.pdf"
fi

ocrmypdf \
  -l chi_sim+eng \
  --rotate-pages \
  --deskew \
  --clean \
  --skip-text \
  --output-type pdfa \
  "$@" \
  "$input" \
  "$output"

printf '{"ok":true,"input":%q,"output":%q,"engine":"ocrmypdf+tesseract","language":"chi_sim+eng"}\n' "$input" "$output"
