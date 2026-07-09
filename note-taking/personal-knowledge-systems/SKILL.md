---
name: personal-knowledge-systems
description: Unified guidance for personal notes, notebooks, knowledge bases, saved web clips, and lightweight personal information stores. Use when searching, reading, creating, appending, organizing, or publishing content into a user's note system or personal knowledge base across IMA, Flomo, Notion, and related tools.
---

# Personal Knowledge Systems

## Overview
This umbrella skill consolidates personal notes and knowledge-base workflows that were previously split by app or sub-API.

## Core workflow
1. Determine whether the user wants notes, notebook management, knowledge-base ingestion, or lightweight external note capture. For the user-specific source-to-destination routing, no-Obsidian default, Graphiti/TencentDB/wiki boundaries, and raw-content handling, load `knowledge-ingestion-routing` first.
2. Separate read/search flows from write/append flows.
3. For writes, confirm the destination object when ambiguity could mutate existing user content.
4. Preserve titles, encodings, and attachment constraints for the target platform.

## Consolidated subsections
### Personal notes
Create, search, browse, read, and append to user notes and notebooks.

### SiYuan / self-hosted note backend
When the user asks to install SiYuan, use SiYuan as a WSL-local knowledge backend, or connect a fresh workspace to an existing S3 sync repo, follow `references/siyuan-wsl-s3-sync.md`. Key safeguards: import the data repo key before S3 config, back up the workspace, start with pull/download only, and never push an empty fresh workspace to an existing cloud repo.

### Knowledge bases
Upload files, import URLs, search libraries, browse folders, and retrieve source material from personal knowledge stores.

For the user's local filesystem wiki, first read and follow `references/the user-filesystem-wiki.md` before searching, editing, or answering wiki-backed questions. For the recurring weekly digest that distills daily English emails into the wiki, follow `references/weekly-english-digest-cron-collector.md`: use the deterministic pre-run collector, one canonical txt per day, and do not run the cron immediately unless the user explicitly wants a backfill. The canonical active wiki root is `~/wiki`; do not mistake legacy/cache-like locations such as `~/.hermes/data/wiki` for the real wiki. When the user asks to view/sync the wiki in SiYuan, follow `references/siyuan-wiki-readable-mirror.md`: create a one-way readable `the assistant Wiki` mirror in SiYuan, keep `~/wiki` as source of truth, and never set up bidirectional sync from SiYuan back into the wiki. When the user asks to improve the wiki's own LLM-Wiki/compiler-style architecture after an ingest, also read `references/the user-wiki-compiler-ops-upgrade.md` for the source-dependency / answer-path / ingestion-eval upgrade pattern. If the user asks about a domain already represented in the wiki (especially 408/math/kaoyan planning, AI/Agent concepts, or previously ingested article conclusions), search/read the relevant wiki pages before giving a timeline, recommendation, or explanation; do not answer from generic memory when the wiki is the established source of truth. Use the ingestion workflow in that reference: preserve raw source material under `raw/`, extract information useful to the user into a durable formal concept/entity/comparison/query page, update `index.md`, append `log.md`, maintain manifest/hot context when relevant, and move temporary extraction folders to trash rather than hard-deleting. For raw files, compute/verify sha from the exact final written file body after the wiki frontmatter, matching `scripts/wiki_lint.py`; if a precomputed extractor-body hash differs after final formatting, update both raw frontmatter and `.manifest.json` before claiming only legacy warnings remain. For lightweight study-planning metadata such as course-hour tables extracted from screenshots, avoid over-ingesting: save the durable structured data under `~/.hermes/data/study/` and create at most one concise wiki/Obsidian reference page with total time, per-lesson durations, and scheduling caveats; do not create one page per lecture until actual study notes are produced. For WeChat/mp.weixin.qq.com article ingestion specifically, also read `references/the user-wechat-article-ingestion.md`: use the local extractor, verify the output is not a control/risk page, summarize the useful takeaways for the user, then save canonical raw + formal page + index/manifest/log/hot updates and run `scripts/wiki_lint.py`. For the current roadmap to upgrade that wiki into an LLM-Wiki/GBrain-style learning and agent knowledge hub, see `references/the user-agent-knowledge-system-improvements.md`. When the task is to make the wiki more usable/queryable rather than ingesting a new source, follow `references/the user-wiki-usage-layer-upgrade.md`: add natural-question routing, Feishu-task routing, core-page usage cues, lightweight query/lint scripts, and a full verification pass.

### Quick-capture note sinks
Use lightweight append-only systems when the user wants fast capture more than rich structure.

### External workspace stores
Use workspace APIs when the note destination is a structured external system such as Notion. For the absorbed Notion curl/API guide, use `references/notion-curl-api.md`; supporting block and permission notes from the old standalone package are re-homed as `references/notion-block-types.md` and `references/notion-permissions-and-verification.md`.

### Filesystem-first Obsidian vaults
Use `references/obsidian-filesystem-vault.md` when the user explicitly asks for Obsidian, an Obsidian vault, local markdown notes, wikilinks, or app/vault availability checks. Keep the user-specific routing intact: formal durable knowledge defaults to `~/wiki`, while explicit Obsidian scratch/draft requests route to `/mnt/e/Obsidian/Warehouse/Study`.

## Absorbed specialized skills
- `ima-skill` — unified IMA notes + knowledge-base API surface.
- `ima-note` and `notes` — note search/read/create/append workflows.
- `knowledge-base` — knowledge-base upload, browse, and retrieval flows.
- `contact-manager` — lightweight contact/address-book storage plus email-to-saved-contact workflows.
- `flomo-notes` — lightweight quick-capture note sink.
- `notion-api` and `notion` — external workspace note/database destination.
- `obsidian` — filesystem-first Obsidian vault reading, writing, search, wikilinks, and the user vault-routing notes.

### Contact and lightweight people records
When the user is maintaining a small personal contact list, saving name/email/notes, or looking up a saved contact before an email action, keep that under the personal knowledge umbrella rather than spinning up a separate address-book skill. Store operational detail in `references/contact-manager.md`.

## Navigation
App-specific details from absorbed note/knowledge-base skills live under `references/`. For the user wiki ingestion verification, `scripts/verify_user_wiki_ingest.py` provides a reusable raw-hash/manifest/index/source-author check to run after the wiki's own `scripts/wiki_lint.py`.

## Common pitfalls
- Appending to an existing note without explicit target confirmation.
- Confusing note storage with knowledge-base ingestion.
- Ignoring platform encoding or attachment limitations.
- Exposing private note content too broadly in shared contexts.

## Verification checklist
- [ ] Destination system confirmed.
- [ ] Read vs write path clearly chosen.
- [ ] Existing-note mutations confirmed when ambiguous.
- [ ] Platform-specific limits checked in `references/` if applicable.
