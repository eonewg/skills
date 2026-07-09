---
name: humanize-ppt
description: Use when turning raw material, notes, links, transcripts, documents, or old decks into a human-centered presentation outline before generating PPT/HTML slides. Produces AST-based production contracts for downstream slide renderers.
version: 0.1.0-local
source: https://github.com/LearnPrompt/humanize-ppt
source_commit: bc172e0ade41ed66c9d3de022cc805c2f17830bc
author: LearnPrompt / Hermes local adaptation
license: MIT
metadata:
  hermes:
    tags: [presentation, ppt, html-slides, humanizer, ast, workflow]
    related_skills: [powerpoint, claude-design, popular-web-designs, frontend-design, humanizer-zh]
---

# Humanize PPT

## Overview

Humanize PPT is an **Outline Director**, not a slide renderer.

Use it before asking any PPT / HTML-slide generator to render pages. Its job is to convert raw, noisy material into a clean AST production contract so the renderer does not inherit AI summary voice, reasoning traces, over-explanation, or random structure noise.

Core principle:

> PPT is not an information container. PPT is an audience state-transfer artifact.

## When to Use

Use this skill when the user wants to:

- turn notes, documents, links, voice transcripts, research material, or an old deck into a presentation;
- make a PPT more “像人讲的”, more persuasive, or less AI-ish;
- prepare an HTML deck, keynote-style talk, courseware, product demo, pitch, report, or public sharing;
- generate slide content but the real problem is narrative, audience path, or speaking intent;
- create a reusable production brief before calling downstream slide skills.

Do **not** use this as the final rendering layer. After this skill produces the contract, hand off to a renderer such as PowerPoint tooling, HTML slide design, `claude-design`, `popular-web-designs`, `frontend-design`, or another deck generator.

## AST Theory

AST = **Audience — State — Transfer**.

### Audience

Identify:

- who is listening;
- what they already know;
- what they do not realize yet;
- what they resist;
- why they would keep listening;
- what judgment, emotion, or action they should leave with.

### State

A deck should change an audience state.

```yaml
initial_state: "Before seeing the deck"
desired_state: "After seeing the deck"
core_tension: "The main cognitive resistance"
state_shift: "The transition the deck must create"
```

### Transfer

Transfer is not a table of contents. It is the audience's psychological path.

A default five-part arc:

```yaml
transfer_path:
  - role: hook
    purpose: grab attention
  - role: conflict
    purpose: break the old frame
  - role: method
    purpose: explain the new frame
  - role: proof
    purpose: build trust with evidence / demo
  - role: takeaway
    purpose: leave a portable judgment
```

Adapt the arc to the situation. A research report, investor pitch, course lecture, and product launch should not share the same page rhythm.

## Required Output Contract

For every Humanize PPT run, produce these six artifacts, either as explicit sections in the reply or as files if the task is project-like:

1. `deck_brief.md` — audience, goal, tension, success criteria.
2. `ast_outline.md` — AST map and narrative arc.
3. `slide_plan.json` — slide-by-slide plan.
4. `speaker_intent.md` — what the speaker should do on each slide.
5. `asset_manifest.md` — screenshots, charts, images, video needs.
6. `video_slots.json` — optional HyperFrames / video insertion plan.

Minimum shape for `slide_plan.json`:

```json
[
  {
    "slide_id": "S01",
    "role": "hook",
    "title": "...",
    "message": "one clean sentence",
    "visible_content": ["what appears on the page"],
    "speaker_intent": "what the speaker should make the audience feel/realize/do",
    "asset_need": "none / screenshot / chart / diagram / video",
    "recommended_renderer": "powerpoint / html / zara-style / guizang-style / custom"
  }
]
```

## OPC Workflow

Use the OPC chain:

```text
O — Outline Director
  Humanize PPT: raw material → AST outline + production brief

P — Presentation Production
  Downstream renderer: PowerPoint, HTML deck, guizang-style, Zara-style, custom design system

C — Complete / Control
  Presenter adapter, video adapter, deploy/export adapter, QA checklist
```

Rules:

- Do not let slide renderers consume raw material directly when this skill can first produce the AST contract.
- Keep presenter mode as a post-processing adapter, not a visual style.
- Separate deployment/export from presenter mode.
- Use humanizer cleanup principles, but do not reduce this to text polishing.
- Prefer a small verified workflow over a broad unverified promise.

## Operating Procedure

1. **Ingest material**
   - Read the source fully when available.
   - Extract concrete facts, claims, examples, data, screenshots, and named entities.
   - Mark gaps instead of inventing details.

2. **Define AST**
   - Audience: name the exact audience segment.
   - Initial state: what they think/feel before the deck.
   - Desired state: what should change after the deck.
   - Core tension: the one contradiction that makes the talk worth listening to.

3. **Build the transfer path**
   - Avoid a table-of-contents deck.
   - Each slide must move the audience state forward.
   - Give every slide one job and one message.

4. **Create production artifacts**
   - Write `deck_brief.md`, `ast_outline.md`, `slide_plan.json`, `speaker_intent.md`, `asset_manifest.md`, and `video_slots.json`.
   - If the user only needs a quick answer, compress them into clearly labeled sections.
   - If the user is building an actual deck, write them to an output directory.

5. **Hand off to renderer**
   - Recommend a rendering path based on audience and style.
   - Do not start visual production until the outline contract is coherent.

6. **QA before final rendering**
   - Check every slide against the AST path.
   - Remove AI-ish filler, generic summaries, fake significance, and mechanical rhythm.
   - Verify assets exist or are clearly marked as needed.

## Quality Bar

A valid Humanize PPT outline answers:

- Who is the audience?
- What is the initial state?
- What is the desired state?
- What is the core tension?
- How does each slide move the state forward?
- Which renderer / adapter should complete the job?

If any answer is vague, do not render yet. Tighten the outline first.

## Local Demo Runner

The upstream repository includes a minimal demo script. It validates the file-output chain but is not a mature arbitrary-material intelligence layer yet; its default five-slide roles are partly hard-coded.

```bash
git clone https://github.com/LearnPrompt/humanize-ppt.git
cd humanize-ppt
python3 scripts/humanize_ppt_v1.py \
  --source examples/01-ai-tool-update/source.md \
  --out .humanize-ppt-runs/ai-tool-update \
  --title "AI 工具更新，不只是功能清单"
```

Expected output tree:

```text
out/
  deck_brief.md
  ast_outline.md
  slide_plan.json
  speaker_intent.md
  asset_manifest.md
  video_slots.json
  styles/
    index.html
    guizang-stable.html
    zara-editorial.html
    zara-contrast.html
  presenter/
    index.html
    notes.json
  deploy/
    index.html
    presenter.html
```

## Security / Provenance Notes

- Source inspected: `https://github.com/LearnPrompt/humanize-ppt`
- Commit inspected: `bc172e0ade41ed66c9d3de022cc805c2f17830bc`
- License file: MIT.
- `scripts/humanize_ppt_v1.py` writes local output files only; no network calls observed in the script.
- The public demo contains bundled static media and a minified `motion.min.js`; do not import demo assets blindly into Hermes skills unless needed.

## Common Pitfalls

1. **Treating this as a PPT template library.** It is a director layer. Rendering comes later.
2. **Letting raw material flow into the renderer.** This recreates the exact AI-PPT problem the skill tries to solve.
3. **Producing a table of contents instead of a state-transfer path.** Every slide needs a psychological function.
4. **Confusing presenter mode with deck style.** Presenter mode is a control/notes adapter after the deck exists.
5. **Overfitting to the demo script.** The upstream script is useful for testing the contract shape, not for high-quality arbitrary presentations by itself.
6. **Keeping AI writing traces.** Remove “首先/其次/综上所述” stuffing, fake grand conclusions, generic bullets, and model-like explanation rhythm.

## Verification Checklist

- [ ] Raw material was read or key assumptions were labeled.
- [ ] Audience, initial state, desired state, and core tension are explicit.
- [ ] Every slide has one role, one message, and one speaker intent.
- [ ] `slide_plan.json` is valid JSON if written as a file.
- [ ] Asset needs are concrete and not invented as if already available.
- [ ] Renderer recommendation is separated from the outline contract.
- [ ] Final deck production, presenter mode, and deployment/export are separate stages.
