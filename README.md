# Public AI Agent Skills

A curated public collection of original or substantially adapted Hermes/OpenClaw-style agent skills. Directly downloaded third-party skills and thin marketplace/vendor wrappers are intentionally excluded.

Each skill lives at `category/skill-name/SKILL.md` with optional `references/`, `scripts/`, `templates/`, `assets/`, and `examples/`.

## Curation policy

- Kept: skills authored in this library, or skills substantially refactored/adapted into Hermes-native workflows.
- Removed: direct downloads, unmodified marketplace skills, vendor demo wrappers, and skills whose main value is simply exposing a third-party service.
- Attribution: adapted skills keep upstream references in `THIRD_PARTY_SOURCES.md` and the root `NOTICE.md`.
- Privacy: local usernames, private emails, chat IDs, absolute machine paths, and real-looking tokens are redacted before publication.

## Skills index

### autonomous-ai-agents

- [`agent-memory-systems`](autonomous-ai-agents/agent-memory-systems/SKILL.md) — Unified guidance for agent memory, recall, active-memory plugins, structured knowledge stores, and self-improvement loops. Use when configuring or operating long-term memory, memory recall before replies, knowledge graphs, reflection/evolution workflows, or...
- [`ai-coding-agent-orchestration`](autonomous-ai-agents/ai-coding-agent-orchestration/SKILL.md) — Orchestrate autonomous coding CLIs (Claude Code, Codex, OpenCode) from Hermes for implementation, refactoring, PR review, and parallel work.
- [`hermes-agent`](autonomous-ai-agents/hermes-agent/SKILL.md) — Configure, extend, or contribute to Hermes Agent.
- [`model-routing-and-provider-config`](autonomous-ai-agents/model-routing-and-provider-config/SKILL.md) — Unified guidance for configuring multi-model agents, provider fallback chains, and task-based model routing. Use when setting up provider selection, fallback behavior, workload-specific model assignment, or router policies across AI providers.
- [`modular-memory-routing`](autonomous-ai-agents/modular-memory-routing/SKILL.md) — Route the user/the assistant tasks to modular cold-memory files under ~/.hermes/memory-modules and ~/.hermes/user-modules before answering or acting. Use when the current task depends on the user-specific study state, user profile, process semantics, style...

### creative

- [`humanizer-zh`](creative/humanizer-zh/SKILL.md) — 去除文本中的 AI 生成痕迹。适用于编辑或审阅文本，使其听起来更自然、更像人类书写。 基于维基百科的"AI 写作特征"综合指南。检测并修复以下模式：夸大的象征意义、 宣传性语言、以 -ing 结尾的肤浅分析、模糊的归因、破折号过度使用、三段式法则、 AI 词汇、否定式排比、过多的连接性短语。

### devops

- [`hermes-kanban-workflows`](devops/hermes-kanban-workflows/SKILL.md) — Operate Hermes Kanban boards, orchestrators, workers, task handoffs, retries, and specialist lanes.
- [`hermes-tencentdb-memory`](devops/hermes-tencentdb-memory/SKILL.md) — Configure, migrate, re-embed, and troubleshoot Hermes TencentDB Agent Memory, including SiliconFlow Qwen3 embeddings, SenseNova extraction, and legacy Volcengine Ark compatibility.
- [`linux-desktop-app-operations`](devops/linux-desktop-app-operations/SKILL.md) — Install, expose, and verify Linux desktop/Electron apps inside WSL or Linux hosts, especially when a headless/web-kernel mode is more reliable than launching a GUI. Use for AppImage/tarball/deb installs, wrapper commands under ~/.local/bin, workspace initia...
- [`openclaw-operations`](devops/openclaw-operations/SKILL.md) — Operate and maintain a local OpenClaw installation: update, back up, verify gateway/systemd health, and handle common post-update warnings.

### education

- [`anki-card-making`](education/anki-card-making/SKILL.md) — Create high-quality Anki/APKG cards for the user's exam study from PDFs, courseware, notes, exercises, wrong-question reviews, or English intensive reading. Use when the user asks to 制卡 / 生成 Anki / 导出 APKG / 整理为卡片 / 优化卡片 / 继续制卡. Do not trigger for ordinary...
- [`concept-investigation-loop`](education/concept-investigation-loop/SKILL.md) — Use when the user is stuck at memorizing a definition or wants to understand a math/408/CS concept by tracing its origin, prerequisites, relationships, dependent applications, and next learning clue. Adapted from SarkAzia/baiyueguang-learning-skill without...
- [`sijiao-learning-workflows`](education/sijiao-learning-workflows/SKILL.md) — Stateful private-tutor workflow for turning “I want to learn X” into a durable learning path with curriculum DAG, learner state, spaced repetition, mastery checks, and Hermes teach-workspace integration. Use for “私教 skill”, “学 X”, “继续学 X”, “考我 X”, “做一个 X 学习...
- [`teach-html-design`](education/teach-html-design/SKILL.md) — Use when creating or revising HTML lesson/reference pages under ~/teach/<topic>/. Defines browser-first visual design, layout, LaTeX/KaTeX formula rendering, and page quality gates. Not specific to any exam.

### general

- [`imap-smtp-mail`](general/imap-smtp-mail/SKILL.md) — Read and send email via IMAP/SMTP using local Node scripts. Use when the agent needs to check inboxes, fetch email content, search messages, download attachments, or send emails with optional attachments from configured mailboxes. Includes optional inbox wa...
- [`lifesimulator`](general/lifesimulator/SKILL.md) — Simulate alternative life paths and decision outcomes through variable-driven narrative scenarios.
- [`ponytail`](general/ponytail/SKILL.md) — Forces the laziest solution that actually works, simplest, shortest, most minimal. Channels a senior dev who has seen everything: question whether the task needs to exist at all (YAGNI), reach for the standard library before custom code, native platform fea...
- [`teach`](general/teach/SKILL.md) — Teach the user a new skill or concept, within this workspace.
- [`teach-style-override`](general/teach-style-override/SKILL.md) — Overrides teach skill citation advice: research sources stay out of lesson body for the user

### github

- [`github-repo-management`](github/github-repo-management/SKILL.md) — Clone/create/fork repos; manage remotes, releases.

### leisure

- [`midnight-companion`](leisure/midnight-companion/SKILL.md) — 深夜书房的守灯人 —— 存在主义对话伴侣。当用户表达消极情绪、虚无感、存在主义困惑、深夜emo、对人生意义的追问时触发。专门处理情绪迷雾，用诗性语言陪伴穿越，不提供标准答案，不强制乐观，不鸡汤。

### mcp

- [`mcp-integration`](mcp/mcp-integration/SKILL.md) — Use Model Context Protocol servers to access external tools and data sources. Enable AI agents to discover and execute tools from configured MCP servers (legal databases, APIs, database connectors, weather services, etc.).

### media

- [`bili-note`](media/bili-note/SKILL.md) — Extract Bilibili videos and opus/article posts into readable Markdown knowledge notes. Use when the user asks to 提取/提炼/总结/整理 B站 or bilibili video/图文/动态/opus content, save a B站 note to a local knowledge base, include useful comments, handle multi-part videos...
- [`douyin-note`](media/douyin-note/SKILL.md) — Use when extracting, archiving, transcribing, or summarizing Douyin/TikTok China short-video, image-note, gallery, share-link, or local downloaded media into reusable Markdown notes. Handles Douyin-specific parsing routes, fallback downloaders, local-file f...
- [`media-ingestion-and-transcription`](media/media-ingestion-and-transcription/SKILL.md) — Unified guidance for turning videos, audio, images, and URLs into usable text or inspectable inputs. Use when the user needs transcripts, summaries, video notes, or a reliable path for loading media into downstream workflows.

### note-taking

- [`knowledge-ingestion-routing`](note-taking/knowledge-ingestion-routing/SKILL.md) — Use when deciding how to ingest, summarize, verify, and archive external content into the user's local knowledge system, wiki, Graphiti, TencentDB memory, or skills. Encodes default no-Obsidian policy, confirm-first link handling (summarize → ask → write),...
- [`personal-knowledge-systems`](note-taking/personal-knowledge-systems/SKILL.md) — Unified guidance for personal notes, notebooks, knowledge bases, saved web clips, and lightweight personal information stores. Use when searching, reading, creating, appending, organizing, or publishing content into a user's note system or personal knowledg...
- [`siyuan-wiki-readable-mirror`](note-taking/siyuan-wiki-readable-mirror/SKILL.md) — Generate a clean one-way readable mirror of the user's filesystem wiki and import it into SiYuan as the `the assistant Wiki` notebook for cross-device reading via SiYuan S3 sync. Use when the user asks to sync/export/mirror `~/wiki` into SiYuan, update the...

### productivity

- [`feishu-lark-workflows`](productivity/feishu-lark-workflows/SKILL.md) — Unified guidance for Feishu/Lark workspace operations: docs, interactive cards, CLI setup, and task workflows. Use when the user needs to configure or operate Feishu/Lark documents, tasks, messaging UX, or the official CLI.
- [`feishu-task-routing`](productivity/feishu-task-routing/SKILL.md) — Use when operating the user's Feishu/Lark task and reminder workflow: checking unfinished tasks, creating tasks with deadlines, assigning tasks to the user, routing study tasks to the exam-prep grouping, handling bulk reschedules, and interpreting task-lang...
- [`humanize-ppt`](productivity/humanize-ppt/SKILL.md) — Use when turning raw material, notes, links, transcripts, documents, or old decks into a human-centered presentation outline before generating PPT/HTML slides. Produces AST-based production contracts for downstream slide renderers.
- [`office-document-workflows`](productivity/office-document-workflows/SKILL.md) — Unified guidance for creating, editing, converting, extracting, and validating DOCX, XLSX, PPTX, PDF, OCR, and document-intelligence workflows. Use when working with Office files, PDFs, Markdown conversion, OCR/document extraction, or provider-specific docu...
- [`pdf-ocr-searchable`](productivity/pdf-ocr-searchable/SKILL.md) — Use when converting scanned/image PDFs into coordinate-aligned searchable PDFs and structured Markdown. Prefer OCRmyPDF/Tesseract for PDF text layers; use official PaddleOCR-VL job API for Markdown/layout extraction. Legacy SiliconFlow VLM path remains a fa...
- [`skill-library-operations`](productivity/skill-library-operations/SKILL.md) — Unified guidance for discovering, evaluating, vetting, updating, publishing, and maintaining agent skills as a library. Use when searching for skills, assessing skill quality or safety, installing from hubs, publishing skills, or maintaining the overall ski...
- [`structured-problem-solving`](productivity/structured-problem-solving/SKILL.md) — Unified guidance for breaking down complex work, exploring ambiguous problems, and tracking execution. Use when the user needs decomposition, exploratory questioning, a to-do structure, or persistent task-tracking for multi-step work.
- [`study-habits`](productivity/study-habits/SKILL.md) — Build effective study habits with spaced repetition, active recall, and session tracking

### research

- [`cangjie-content-skill-distillation`](research/cangjie-content-skill-distillation/SKILL.md) — Distill high-value source content—books, long videos, podcasts, interviews, courses, long essays, or document corpora—into a staged pack of executable Hermes skills. Use when the user asks “仓颉”, “cangjie”, “把这本书/长视频/播客蒸馏成 skills”, “把内容里的方法论做成可调用 skill”, or...
- [`cognitive-distillation-workflows`](research/cognitive-distillation-workflows/SKILL.md) — Create or evaluate Hermes-native skills that distill a person, persona, teammate/colleague, public thinker, theme, or niche industry into a reusable cognitive operating system. Use for requests like “蒸馏某人/某行业”, “造一个人物视角 skill”, “做大师/同事/女娲类 skill”, “把某领域变成 m...
- [`exa-search-api`](research/exa-search-api/SKILL.md) — Use when searching the web through Exa's direct APIs instead of MCP. Provides Search API retrieval/synthesis and Contents API extraction with explicit parameters, highlights, text caps, summaries, structured outputs, domain/category/date filters, freshness...
- [`live-web-research`](research/live-web-research/SKILL.md) — Unified guidance for live web search, Chinese web research, news/trend lookup, academic search, source routing, and AI-generated search summaries. Use when the task requires current online information, multi-provider web research, search routing, trend/news...
- [`search-routing`](research/search-routing/SKILL.md) — Use when choosing between Exa, Tavily, and AnySearch for live web research, technical documentation lookup, news/current information, Chinese/official/PDF searches, and multi-source fact verification. Encodes the user's default search-tool routing policy an...
- [`tavily-search-cli`](research/tavily-search/SKILL.md) — Search the web via Tavily API and extract article content. Use when users ask for live web research, current information, source gathering, news lookup, or URL content extraction through Tavily.
- [`zhihu-search`](research/zhihu-search/SKILL.md) — 搜索知乎站内内容，返回脚本整理后的结构化结果（标题、链接、作者、摘要等）

### software-development

- [`algorithm-practice`](software-development/algorithm-practice/SKILL.md) — Use when the user wants to start LeetCode/algorithm practice, finish a problem, review due problems, or maintain a lightweight spaced-repetition loop for coding interview / CS algorithm practice. Adapted from beyondaprilzjl-lab/leetcode-skill for Hermes + W...
- [`book-to-skill`](software-development/book-to-skill/SKILL.md) — Use when converting a technical book/document PDF, EPUB, DOCX, HTML, Markdown, TXT, RTF, MOBI/AZW into a Hermes Agent skill. Extracts frameworks, concepts, chapter summaries, glossary, patterns, and cheatsheet into a reusable skill under ~/.hermes/skills/.
- [`browser-automation-and-scraping`](software-development/browser-automation-and-scraping/SKILL.md) — Unified guidance for browser automation, cloud/browser-session orchestration, anti-bot scraping, and web interaction tooling. Use when an agent needs to navigate websites, automate clicks/forms, manage browser sessions, or scrape dynamic pages with browser-...
- [`simplify-code`](software-development/simplify-code/SKILL.md) — Parallel 3-agent cleanup of recent code changes.
- [`static-site-operations`](software-development/static-site-operations/SKILL.md) — Maintain and deploy small static websites served from a Linux/Nginx server, including copy-editing personal homepages, safe backups, cache-busted verification, and visual QA.

## Install/use

Copy a skill directory into your agent skill path, or point your agent runtime at the desired `category/skill-name` directory. Some skills require additional tools or API credentials; check each `SKILL.md` and `README.md`.

## License

Repository packaging is MIT unless a skill directory states a different upstream license. Third-party files remain under their original licenses.
