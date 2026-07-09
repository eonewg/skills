# Third-party sources and attribution for `personal-knowledge-systems`

This file is generated during public packaging to keep upstream references visible. Verify upstream licenses before redistributing modified scripts or templates.

## URLs

- https://github.com/dogiladeveloper

## Source/license lines found in the skill files

- `4d-2. For **Zhihu public search synthesis batches** where the user asks to “去知乎搜最新两三年帖子 / 选好学校上岸经验贴 / 下岸教训也归档” but the useful evidence is spread across search-result snippets plus already-ingested Zhihu raw captures, treat the chat synthesis itself as the source: record a consolidated raw under `raw/articles/` with `source_url: hermes-session:<date>-<topic>` and `source_type: session-search-summary`, explicitly list the search hits/snippets and cite any existing raw evidence reused. Then create one durable concept/plan page (e.g. `concepts/kaoyan-public-subjects-plan-zhihu.md`) instead of one page per Zhihu post. Patch all affected active subject hubs (`concepts/english-prep.md`, `concepts/politics-prep.md`, `concepts/cs408-prep.md`, `concepts/math-prep.md`, `concepts/kaoyan-overview.md`) so later study-planning questions route through the distilled page. Do not encode transient access failures as rules; the durable pattern is indexed-snippet + existing-raw + session-summary ingestion with full wiki verification.`
- `18g-2. For **Li Jigang / short high-signal essays about cognitive coordinates, reference frames, spatial metaphors, Thousand Brains, model voting, or “理解=挂坐标/移动/预测”** (e.g. 《参考系》), treat them as a reusable cognition/learning model rather than a quote archive. Pattern: raw under `raw/articles/life-weekly-reference-frame-cognition-2026.md`, focused concept page `concepts/reference-frame-cognition.md`, patch `concepts/viewing-and-constraint-frame.md`, `concepts/learning-system.md`, `concepts/agent-knowledge-engineering.md`, and `concepts/personal-operating-system.md`. Extract the operational loop: “它在我的哪个参考系里 → 和已有坐标点的关系是什么 → 下次遇到什么输入可用它预测什么.” For the user, ground it in kaoyan/Agent use: math/408 concepts must have chapter position, neighboring concepts, and predictable problem interfaces; wiki ingestion should hang new ideas onto existing concept coordinates instead of producing isolated summaries.`
- `18i. For social-science / philosophy / epistemology public articles about **post-truth, fact decay, scientific credibility, media viruses, relativism, actor-network theory, source-chain reasoning, or truth verification**, treat them as medium/high signal when they yield a reusable information-judgment tool. Pattern from “后真相的哲学根源与反思”: raw under `raw/articles/post-truth-philosophical-roots-2026.md`, focused concept page `concepts/post-truth-epistemic-network.md`, patch `concepts/clear-thinking-decision-system.md` and `concepts/cognitive-sovereignty-ai.md`. Extract the operational loop: “事实主张 → 来源链 → 行动者网络强度”；reliable networks have data, methods, peer review, institutions, funding/accountability, and critique norms, while weak post-truth networks lean on short evidence chains, emotional identity buttons, suspicious funding/source opacity, and platform amplification. Keep the chat takeaway practical for the user: when reading hotspots, kaoyan experience posts, AI technical claims, or social-media controversies, lower confidence when the source chain is short and the emotion button is strong.`
- `19d. For follow-up articles about the **same model or topic** but from a different author/source, do not automatically create another parallel concept page. Treat the new source as a supplemental source: first update the existing focused concept page with any genuinely new mechanism/parameter/trade-off; if the source contains concrete model/product facts (model variants, API names, pricing, deployment notes, benchmark/real-task boundaries), create or update an `entities/<model-or-tool>.md` page (e.g. `entities/deepseek-v4.md`) to separate "specific model facts" from "architecture paradigm". The index should usually contain the entity once in the AI section, not duplicated under entity pages unless there is a strong navigation reason. Targeted verification after this pattern: raw hash matches, entity exists, existing concept page sources include the new raw, and the new wikilink appears in `index.md` exactly once.`
- `homepage: https://ima.qq.com`
- `**每次调用 notes 写入类 API（`import_doc`/`append_doc`）之前，必须对 `content`、`title` 等所有字符串字段执行 UTF-8 编码校验/转换。** 无论内容来源如何——用户直接输入、从文件读取、WebFetch 抓取、剪贴板粘贴、外部 API 返回——都不能假设已经是合法 UTF-8，必须显式确认。`
- `*Contributed by [@dogiladeveloper](https://github.com/dogiladeveloper)*`
- `license: MIT`
- `homepage: https://developers.notion.com`
- `来源：`~/wiki``

## License signals

- `license: MIT`
