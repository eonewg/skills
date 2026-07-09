# Skills

A public collection of reusable AI-agent skills, templates, scripts, and workflow notes.

This repository is organized by category so each skill can be copied into a compatible agent skill directory while keeping its supporting files together.

## Layout

```text
skills/
├── productivity/
│   ├── pdf-ocr-searchable/
│   └── teach-web-lesson/
└── personal/
    └── README.md
```

## Skills

### productivity/pdf-ocr-searchable

A workflow skill for turning scanned/image PDFs into searchable PDFs and/or structured OCR Markdown. It combines OCRmyPDF/Tesseract for coordinate-aligned PDF text layers with PaddleOCR-VL-style structured extraction when available.

### productivity/teach-web-lesson

A research-first, browser-first teaching page system for generating beautiful standalone HTML lessons with sidebar navigation, KaTeX, quizzes, review sections, and course continuity.

Attribution: the teach system was inspired by and evolved from Matt Pocock's `teach` skill in [`mattpocock/skills`](https://github.com/mattpocock/skills/tree/main/skills/productivity/teach). This repository's implementation adds a warm editorial HTML template system, standalone attachment delivery, validation scripts, and stateful course-building conventions.

## Install a skill into Hermes Agent

Copy one skill directory into your Hermes skills folder, for example:

```bash
mkdir -p ~/.hermes/skills/productivity
cp -R productivity/teach-web-lesson ~/.hermes/skills/productivity/
```

Then start a fresh Hermes session and load the skill by name.

## License

MIT.
