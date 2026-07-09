---
name: teach-html-design
description: Use when creating or revising HTML lesson/reference pages under ~/teach/<topic>/. Defines browser-first visual design, layout, LaTeX/KaTeX formula rendering, and page quality gates. Not specific to any exam.
---

# Teach Web Lesson Design Spec

Use this skill whenever generating or improving HTML teaching files under `~/teach/<topic>/`, including `lessons/*.html` and `reference/*.html`.

## Memory preflight

Before creating or rewriting a lesson, route memory with:

```bash
~/.hermes/scripts/memory_route.py teaching
~/.hermes/scripts/memory_route.py style
```

Read the returned modules, normally `memory-modules/style-memory.md`, `user-modules/workflow-profile.md`, and `user-modules/preferences.md`. They contain the user-specific rules for natural student-language prose, no source/tool provenance in lesson body, no rigid fill-in template tone, delivery conventions, and current teaching workflow preferences.

**Routing guard:** for lesson creation/rewrite requests, this skill is the visual/HTML companion, not the teaching parent. Load `teach` first to decide mission, zone of proximal development, observable skill, retrieval loop, and pass evidence; then load `teach-html-design` for layout, standalone delivery, and visual QA. Do not let design rules substitute for pedagogy.

## Canonical Template Files

The current reusable template pack lives at:

Additional style references:
- `references/claude-like-warm-editorial.md` — Claude-like teach-page visual language: warm cream canvas, Source Sans 3 + Noto Sans SC mixed Chinese-English typography, serif only for display/long English passages, weak borders/no heavy shadows, sparse coral accents, and Chinese paragraph alignment pitfalls.
- `references/lightweight-editorial-html-design.md` — session-derived concrete rules for reducing over-designed HTML lessons: light hero, serif h1/h2, plain text section numbers, borderless examples/quizzes, rare explicit left-rule callouts only, quiet quiz choices, and mobile-visible TOC.
- `references/course-workflow.md` — reusable workflow for continuing a course in `~/teach/<topic>/`: artifact trio, official-source discipline, footer navigation, and delivery convention.
- `references/obsidian-claudian-course-migration.md` — how to package and prompt a teach course for Obsidian + Claudian on another machine; includes the key distinction from wiki migration, portable course layout, and first read-only Claudian test prompt.

```text
~/teach/_templates/
├── STYLE-GUIDE.md
├── lesson-template.html
├── reference-template.html
├── assets/teach-components.css
├── assets/teach-lesson.js
├── examples/math-de-first-order-linear-demo.html
└── validate-template.py
```

When creating a new lesson/reference page, start from these templates instead of hand-writing a one-off HTML page. During authoring, files under `~/teach/<topic>/lessons/` or `~/teach/<topic>/reference/` may link local template assets with:

```html
<link rel="stylesheet" href="../../_templates/assets/teach-components.css">
<script defer src="../../_templates/assets/teach-lesson.js"></script>
```

**Critical delivery rule:** Feishu/Lark attachments do not carry local relative CSS/JS files. Before sending any HTML lesson/reference as `MEDIA:/...`, convert it to a standalone single file with local CSS and JS inlined:

```bash
python3 ~/teach/_templates/make-standalone.py /path/to/page.html
python3 ~/teach/_templates/validate-template.py /path/to/page.html
```

The delivered HTML must contain `data-standalone="true"`, an inline `/* Teach Web Lesson Components ... */` style block, and an inline `// Teach Web Lesson JS ...` script block. Never send a lesson that only links `../../_templates/assets/...`; it will render as plain unstyled HTML on the recipient's side.

Run the validator before sending:

```bash
python3 ~/teach/_templates/validate-template.py /path/to/page.html
```

Current validator is KaTeX-conditional: pages with real LaTeX/formula components must include `katex.min.css`, `katex.min.js`, `auto-render.min.js`, and valid delimiters; non-math pages such as English/politics lessons should omit KaTeX assets entirely and must not add fake LaTeX markers just to satisfy tooling.

## Positioning

These HTML files are **browser-first learning pages**, not print-first handouts.

Priority order:

1. Windows browser readability
2. Review/navigation efficiency
3. Interactive practice experience
4. Consistent subject visual identity
5. Basic mobile readability
6. Optional print compatibility

Do **not** sacrifice web reading and interaction quality for print layout. Printing may degrade gracefully, but is not a hard requirement.

## Layout Standard

Use a modern course-page layout rather than a temporary plain HTML note. Default to a Claude-like warm editorial reading style: page background `#faf9f5`, card/aggregated block background `#efe9de`, coral accent `#cc785c`, near-black heading text `#141413`, body text `#3d3d3a`, and a local-first Source/Noto font stack for Chinese-English mixed notes: `Source Sans 3`, `Noto Sans SC`, `Noto Sans CJK SC`, then system fallbacks (`system-ui`, `Segoe UI`, `Microsoft YaHei UI`, `Microsoft YaHei`, `PingFang SC`, Arial, sans-serif). Do not depend on Google Fonts/CDN imports; if Source/Noto are not installed, the page must still fall back cleanly. Use Source Serif 4 / Noto Serif SC / Georgia-style serif only for longer English passages; short examples and vocabulary should remain in the sans stack. Text emphasis must stay within Claude-like warm brown values rather than saturated textbook colors. Do not use high-chroma red/blue/green/purple for grammar or teaching annotations. Use a warm ink scale instead: near-black `#141413` for skeleton/conclusion, deep brown-gray `#3d3d3a` for ordinary modifiers, warm gray `#6c6a64` for weak notes, warm brown `#7a6e60` / `#5f5146` / `#9a8778` for secondary emphasis, and terracotta `#cc785c` only as a sparse accent or predicate-verb anchor. Prefer weight, italic, serif/sans contrast, spacing, and syntactic position before adding color. Legacy `.text-red/.text-blue/.text-green/.text-purple` classes are compatibility aliases mapped to this warm scale; they do not mean real red/blue/green/purple should appear. Prefer the semantic `.ink-*` classes directly (`.ink-clause`, `.ink-accent`, `.ink-modifier`, `.ink-core`, `.ink-strong`, `.ink-soft`, `.ink-brown*`). Keep these colors on text only; keep page backgrounds, card backgrounds, borders, buttons, and links visually fixed. **Pitfall: do not wrap `<em>` around text that already has a `.ink-clause` or `.text-purple` class — the CSS already provides `font-style: italic`. Nesting `<em>` inside produces double-italic rendering that the user called out as a mistake.** Avoid turning every paragraph, step, navigation item, or minor note into a card. Side navigation, suggested actions, ordinary steps, and ordinary trap lists should usually share the page background with no border; distinguish them through typography, spacing, muted/accent text color, and hover color changes. Hero must stay lightweight: no large background block, no decorative pseudo-element circles, no badge pills; use plain text eyebrow and a serif h1. On desktop, enable `.hero-grid` when metadata is useful: treat it like a book colophon / magazine sidebar with four quiet columns, a dashed top rule, small uppercase labels, and accent-colored values. Hide it on mobile. Section headings should use serif typography and plain accent text numbers, not boxed badges; h3 subheads should also use serif for editorial consistency. Keep the main content column around 720px on wide screens to avoid overlong Chinese lines. The main layout grid should directly constrain the content column. For courses using the sidebar layout, use a four-column grid with symmetric fixed side columns so collapsed content recenters cleanly: `.layout { grid-template-columns:164px 56px minmax(0,720px) 164px; justify-content:center; gap:0 24px; transition:grid-template-columns .3s ease, gap .3s ease; }`, with a collapsible state `.layout[data-sidebar="collapsed"] { grid-template-columns:0px 56px minmax(0,720px) 0px; gap:0; }`. Place `<aside class="sidebar" id="sidebar">` before `<main class="content">`; make `.sidebar { display:contents; }`; put `#sidebar-toggle` as the first child in grid column 2; wrap the course info, TOC, progress, and action boxes in `<div class="sidebar-content">...</div>` in grid column 1. In collapsed state, set `.sidebar-content { width:0; overflow:hidden; }`; do not hide or move the toggle. Keep `.content { grid-column:3; min-width:0; }`. The right 164px column balances the left panel when expanded; both side columns collapse to 0 and the grid group is centered. Formula/example/callout blocks should be used sparingly; do not make every teaching block a left-rule card. For the user's lesson pages, prefer plain editorial paragraphs, transparent tables, numbered steps, and subtle horizontal separators. By default, examples and quizzes are borderless or separated with a weak horizontal rule; a 2–3px accent left rule is reserved only for rare high-signal callouts that use an explicit `.rule` class. Avoid repeated long vertical coral lines down the page. Important nuance: removing long left-rule/card lines must NOT flatten all semantic emphasis. Labels such as “本课结论：”“备考信号：”“错题诊断模板：”“过关证据：” and example/quiz titles should keep the subject accent color (English: coral `#cc785c`) and strong weight, while their containers stay borderless or minimally separated. Target balance: colored text labels + clean editorial flow, not gray undifferentiated prose and not stacked warning strips. English long-sentence blocks should use serif at about 17.5px / 1.85. Tables should follow modern editorial typesetting: transparent background, no full box grid and no vertical rules; use only horizontal dividers, with a slightly stronger accent-border rule under the table header. Wrap every content table in `<div class="table-wrap">...</div>`; mobile must scroll horizontally with `-webkit-overflow-scrolling: touch`, and `.table-wrap table` should use `min-width:620px; margin:0;`. Code blocks must also stay editorial: no hard-coded dark-blue/black background in light mode; use `var(--surface-soft)`, `var(--text)`, a `1px solid var(--border)` hairline, and a restrained 12px radius. Progress bars should be a quiet 4px solid accent line, not gradients. Sidebar prose should be auxiliary-sized, about 15px; the desktop sidebar should read like a book table-of-contents on the left, with the toggle as a sticky 56px column (`grid-column:2`, 22px toggle glyph, `top:20px`) and `.sidebar-content` as a sticky 164px column (`grid-column:1`). Use JS to show the sidebar toggle as a directional arrow only: `←` when expanded (clicking collapses the left sidebar) and `→` when collapsed (clicking expands it). Do not include the word `导航` in the toggle; keep accessible `aria-label`/`title` text for screen readers. On mobile, set `.layout { grid-template-columns:1fr !important; }`, restore `.sidebar { display:block; }`, hide the toggle, set `.sidebar-content` to static width 100%, hide nonessential side boxes, hide the desktop TOC, and render navigation as a collapsed `<details class="mobile-toc"><summary>本页导航</summary>...</details>` before the main sections so it does not consume the whole first screen. Mobile section spacing should tighten to about 30px. Quiz choices should use lightweight paper-card buttons for stronger interaction feedback: 1px warm border, 8px radius, `var(--surface)` background, hover with `var(--accent-soft)`, accent border, and a very restrained `translateY(-1px)` lift. Correct/wrong states must include textual ✓ / ✗ markers for accessibility. Avoid bright green/red; use muted ecological green for correct and terracotta soft/danger colors for wrong. Add accessible interaction feedback: `:focus-visible` outlines for links/buttons/summary/inputs, quiz feedback with `role="status" aria-live="polite"`, and active TOC links updated with `aria-current="true"`. Section rhythm should come from 48–60px desktop whitespace rather than dense borders.

Recommended page structure:

- Hero header: subject, chapter, difficulty, estimated time, learning outcome
- Sticky/side table of contents on wide screens
- Core conclusion card
- Concept/method explanation
- Formula/process/algorithm cards
- Worked example
- Common traps
- Retrieval practice / mini quiz
- Next step links

Desktop width target: `1100–1280px`. Avoid narrow A4-like pages unless explicitly requested.

## Subject Themes

Use a consistent color identity per subject, but keep all subjects within the warm editorial system rather than saturated dashboard colors:

- 数学一: restrained blue-gray
- 408: restrained green-cyan
- 英语一: Claude-like coral / warm orange
- 政治: restrained red-brown

Use tags, anchors, progress indicators, and collapsible explanations where helpful. Shadows should be absent or extremely subtle; Claude-like flat surfaces with hairline borders are preferred. Do not use saturated green success blocks in review/conclusion areas; success/summary callouts should stay neutral or use the subject accent color. Use CSS variables throughout and include `@media (prefers-color-scheme: dark)` for a warm dark mode: black-chocolate `#141413`, charcoal surfaces around `#1c1c1a`/`#262522`, cream text, warm muted browns, and weakened `accent-soft` values so late-night studying stays low-glare.

## Math / LaTeX Requirements

For math-heavy pages, correct formula rendering is a **hard quality gate**.

- Write formulas in LaTeX source, not plain text approximations and not screenshots.
- Prefer KaTeX for local HTML pages; MathJax is acceptable when KaTeX cannot render needed syntax.
- Support both inline and display delimiters:
  - Inline: `\\( ... \\)`
  - Display: `\\[ ... \\]`
- Avoid `$...$` by default in HTML pages because it can conflict with ordinary text.
- Long display formulas must not break the layout; wrap them in horizontally scrollable containers.
- Use `throwOnError: false` for KaTeX auto-render so one bad formula does not blank the page.

Recommended KaTeX imports:

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>
<script>
  document.addEventListener("DOMContentLoaded", function () {
    renderMathInElement(document.body, {
      delimiters: [
        { left: "\\\\[", right: "\\\\]", display: true },
        { left: "\\\\(", right: "\\\\)", display: false }
      ],
      throwOnError: false
    });
  });
</script>
```

## Formula Card Pattern

Math formulas should not appear as isolated decorative equations. Use formula cards with:

- Formula name
- Standard form
- Formula / theorem
- Preconditions / applicable conditions
- Recognition cues
- Procedure
- Common traps

## 408 Page Requirements

408 pages should support structures beyond formulas:

- Pseudocode blocks with syntax-like highlighting
- Complexity tables
- Memory/layout diagrams
- Tree/graph visuals
- OS scheduling timelines / Gantt-style diagrams
- Network protocol stack diagrams
- Collapsible reasoning steps

## Restarting a Course From Scratch

## Writing Voice: Natural Student Language (User Preference)

the user's lessons must NEVER include research sources, author names, platform references, or tool process mentions in the lesson body.

**Don't write (academic/research-report tone):**
- "2025–2026 年知乎考研区搜索熟词僻义"
- "优优学姐直接点明：连锁反应导致选错"
- "来源：CDP 登录态读取、知乎搜索"
- "近几年考研区最被引用的几个信号"

**Write instead (direct, conversational):**
- "你肯定遇过这种情况：一个词明明背过，放在句子里就是别扭。"
- "最典型的三个词，你肯定都背过：address（地址→处理）、novel（小说→新颖的）、discipline（纪律→学科）"

**Anti-pattern: rigid structured fill-in formats.** Do NOT use templates like "原词【____】；最近搭配【____】；上下文方向【____】；本句义【____】；原误读【____】" in learner-facing content. The user called these "胡言乱语." Replace with natural questions that walk through the same logic:
- "这个词和谁搭在一起？"
- "前后文告诉你它往哪个方向走？"
- "你原本的第一反应是什么？"

Same for practice reveal answers: do NOT write "原词：sound；最近搭配：evidence was sound；上下文方向：surprisingly 暗示...；本句义：可靠的；原误读：声音." Write natural explanations instead:
- "sound 在这句话里搭配的是 The evidence was... surprisingly。surprisingly 暗示'本以为是负面'，所以 sound = '可靠的/经得起推敲的'，不是'声音'。"

The key test: if the text reads like somuser filling out a form or writing a table row, it's wrong. Lesson prose should sound like a senior student talking to a junior — direct, specific, and not in bullet-point data format.

Research sources go in `RESOURCES.md` and `learning-records/` ONLY. Lesson body teaches — it does not cite where you found the information.

When creating or rewriting a lesson, also load `teach-style-override` after `teach` to reinforce these rules.

When the user explicitly says to restart a course and delete previous lessons/records (e.g. “之前的都不要了 / 全部删了 / 重头开始”), treat that as authorization to clear the course workspace, not merely archive it. Delete old `lessons/`, `learning-records/`, old backups/archived lesson directories, generation scripts, audit files, and stale resource notes under that course root, while preserving the course root directory and then recreating only the minimal fresh structure (`lessons/`, `learning-records/`, plus new `MISSION.md`/`RESOURCES.md` if needed). After deletion, verify the remaining file list before writing the new first lesson. The new first lesson should not depend on old navigation, old learning-record claims, or old roadmap assumptions.

## Continuing or Rewriting an Existing Course

When continuing an established `~/teach/<topic>/` workspace, do not ask what to teach if the learning records already identify the next step. Continue the course statefully.

When the user asks to “rewrite / redo / 重写 / 重做” an existing numbered HTML lesson, rebuild that lesson in place instead of creating the next lesson. Preserve the lesson number and canonical filename, re-read the current page plus mission/resources/learning records, and aim the rewrite at a narrower observable action rather than a broader coverage page. Update the matching learning record and resource provenance, then run the same standalone + validator + browser QA gates as a new page.

For rewrites prompted by visual or pedagogy complaints, explicitly verify the thing they objected to before delivery (e.g. repeated left rules, over-carded layout, vague teaching action, missing practice loop). Treat this as a regression check, not a nice-to-have.

When continuing without a rewrite request:

1. Read `MISSION.md`, `RESOURCES.md`, the latest `learning-records/*.md`, and existing lesson/reference filenames. Treat learning records as evidence, not a coverage log: if the latest record says prior lessons were rebuilt or archived but not proven mastered, do not assume the user has learned them just because files exist.
2. Choose the next lesson from the recorded 后续方向 / course roadmap, but only at the next smallest verifiable step. When mastery evidence is missing, design the next page around one observable diagnostic/action loop and make the learning record state the evidence gap rather than claiming the user learned it.
3. For every subject and every teach session, gather and calibrate sources before writing or orally teaching content. Do not teach from parametric memory, a quick local-file skim, or lightly paraphrased old courseware. Start with official or high-trust sources for factual correctness, then broaden when useful: combine syllabus/textbooks/standard references with learner-facing material. For Chinese exam-learning topics that benefit from real learner pain points (especially 知乎/小红书/B站/公众号), use the CDP Chrome approach — not generic web_search — to access logged-in platforms. The tooling is in the `browser-automation-and-scraping` skill's `kimi-webbridge` reference (search for "CDP fallback" / "workaround" section): launch `chrome-cdp` (starts a dedicated Chrome profile with CDP on port 9222) and extract page text with `cdp-text text <URL>`. This bypasses the known Kimi WebBridge currentWindow bug on WSL+Chrome 148. If CDP is unavailable, fall back to web_search + web_extract for general web content, and record the fallback explicitly in RESOURCES.md or the learning record. Extract recurring confusion points, examples, mnemonics, and practical study advice from the pages, then reconcile them against authoritative sources before writing. Treat social-platform material as teaching-signal and misconception-mining, not as unchecked facts. If platform access is blocked or requires verification, record the attempted path and then use accessible mirrors/pages plus ordinary search only as fallback/cross-check; do not present fallback snippets as if original posts were opened. If time is short, do a minimal source pass first and explicitly say what was checked; never invent a lesson without research.
4. Produce the lean artifact set by default: `lessons/000X-*.html` plus `learning-records/000X-*.md`. Do not create `reference/*.html` by default; only create a reference/速查 page when explicitly asked for, when dense formulas/procedures/templates/checklists need long-term lookup, or when the lesson would otherwise become too long/noisy. Lean does **not** mean abstract or content-thin: every lesson should still contain enough teaching mass for self-study — real context, concrete examples, step-by-step explanation, common traps/false moves, and a practice loop. If the page reads like a planning memo, method slogan, or sparse prompt list rather than an actual course, rewrite it before delivery. For the user's exam lessons, treat “拳拳到肉” as a quality gate: each page must include (1) a concrete error现场 showing how a learner actually gets trapped, (2) at least one full sentence/problem with bad handling vs corrected handling, (3) explicit扣分/错因 consequences, (4) a transfer practice on a fresh example, and (5) observable pass evidence. Write learner-facing pages in student language, not教研/课程设计 language: translate abstract models into plain questions first (e.g. “我读明白了吗？” “我答准确了吗？”), then list the checks. Avoid piling up terms such as 层级、边界、输出、断点、模型校准 in the lesson body; if a term is necessary, immediately attach a concrete action the student can perform. Use genuinely different examples for transfer: do not merely swap vocabulary in the same structure. If a lesson introduces a diagnostic model, separate understanding-layer failures from answer/output-layer failures when applicable, and end with a result-to-next-training mapping rather than only assigning homework. Avoid vague authority phrases such as “近年经验表明” unless a source and year are recorded; prefer mechanism-based explanations in the learner-facing page. For current exam-prep courses, social-platform pain-point mining must also pass a freshness gate: prioritize recent 2024–2026 posts, current-cycle experience posts, and recent真题解析; older Zhihu/小红书/B站 posts may be used only as background if the same pain point is confirmed by recent material or official sources. Keep research/tool provenance out of the lesson body: do not write “I used Kimi WebBridge”, browser/login status, search query paths, validation steps, or other internal workflow notes in the learner-facing课件. Put those details in RESOURCES.md / learning records / final status notes instead. Do not ship pages that only name methods such as “证据链/找主干/暂放修饰” without demonstrating the method on real material, and do not cite old experience posts as if they reflect the current exam cycle.
5. **Footer navigation (critical):** Patch the previous lesson's `<nav class="footer-nav">` so it has both a `← 上一课` link AND a `下一课 →` link. Never leave the right link as an anchor (`#review`) or placeholder. In the **new lesson itself**, also add a "下一课 →" link pointing to the next planned filename (e.g. `0005-<topic>.html`), even though that file does not exist yet — it keeps the navigation chain continuous end-to-end. Also update the review-section paragraph that mentions "下一课" to include a clickable `<a href="...">` to the new lesson.
   - **Pitfall learned:** A malformed review-section link can corrupt the footer layout even when `.footer-nav` CSS is correct. Example failure: `<a href="0006-reading-part-a.html">阅读 Part A 精读方法</strong>` leaves the `<a>` unclosed, so the browser swallows following footer nodes into the link tree and the `← 上一课` button appears as a middle item. Always close review links with `</a>` before `</p>`, then verify the browser accessibility tree shows exactly two footer-nav links and no empty link before them.
6. Run `python3 ~/teach/_templates/validate-template.py` on the patched previous lesson plus all new HTML pages.
7. Browser-open at least the new lesson; verify title/sections, KaTeX render count, footer links, and at least one quiz interaction via JS if normal click feedback is ambiguous. For footer-nav specifically, inspect the rendered bottom section or browser snapshot: it should show exactly two navigation links (`← 上一课 ...` and `下一课 → ...`) with no extra empty link or swallowed paragraph link.
8. If the page uses `example-card`, `quiz-card`, `callout`, or `feedback`, verify computed styles do not create repeated left vertical rules. Default `border-left` for ordinary examples/quizzes/callouts/feedback should be `0px`; use explicit `.callout.rule` only for rare high-signal blocks.

## Quality Gates Before Sending

Before sending a generated HTML file:

1. Check the file exists at the intended path.
2. Verify it contains the expected title and subject.
3. If it includes formulas, verify KaTeX/MathJax imports and delimiters are present. If it has no formulas, verify KaTeX assets are absent.
4. Avoid raw ugly formula strings like `e^(-∫Pdx)` when LaTeX should be used.
5. For course continuations, verify previous/next navigation links are real files, not `#review` placeholders. Both left (`← 上一课`) and right (`下一课 →`) links must exist in the footer-nav.
6. In the final reply, send the main lesson HTML as a Feishu attachment using `MEDIA:/absolute/path.html`. Do not merely list its path. Do not attach every generated artifact by default: reference/速查 pages should be mentioned as generated, and only attached when the user explicitly asks for them or when the reference page is the primary deliverable.
