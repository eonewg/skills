# the user 微信公众号文章入库 workflow

Use this when the user sends a WeChat article link and expects it to be summarized and saved into the local wiki.

## Trigger
- User sends `https://mp.weixin.qq.com/...` with no extra instruction.
- Memory preference: shared articles/videos/PDFs should usually be summarized first, then organized into local wiki when useful. AI/Agent articles go under the AI/Agent part of `~/wiki`.

## Extraction
1. Try the local extractor first:
   ```bash
   ~/.hermes/scripts/wechat_article_to_md.sh '<URL>'
   ```
2. If generic extraction or browser access hits a WeChat captcha/risk page, try a direct mobile User-Agent fetch before giving up. This often returns the real article HTML even when desktop browser automation is challenged. Minimal pattern:
   ```python
   import urllib.request
   url = '<mp.weixin.qq.com URL>'
   headers = {
       'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.50 NetType/WIFI Language/zh_CN',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
       'Referer': 'https://mp.weixin.qq.com/',
   }
   data = urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30).read().decode('utf-8', 'ignore')
   ```
   Save the HTML under `~/.hermes/data/wechat-articles/_raw-html/<id>.html`, extract metadata from JS variables such as `msg_title`, `ct`, `msg_cdn_url`, `user_name`, then extract text from `id="js_content"`. Verify this is real article text, not a control page, before summarizing or archiving.
3. Verify the output is the real article, not a login/risk/control page:
   - title, author, date, body length, and image count are present;
   - saved markdown path under `~/.hermes/data/wechat-articles/<title>/<title>.md` or the fallback `_raw-html/<id>.txt` extraction path;
   - read enough of the file to identify the article structure and key claims.

## User-facing digest before/with ingestion
Give the user the useful distilled takeaways, not a generic abstract. For AI/Agent engineering articles, prefer:
- one-line thesis;
- 5–8 durable mechanisms/principles;
- direct implications for Hermes/wiki/Graphiti/OpenClaw;
- then list saved paths and verification result.

## Wiki ingestion pattern
Follow `references/the user-filesystem-wiki.md` and the current `~/wiki/SCHEMA.md`.

For a high-signal AI/Agent article, typical updates are:
1. Save raw source under `raw/articles/<slug>-2026.md` with YAML. Preserve extractor metadata exactly when present — especially `source_author`; do not leave placeholder values like `***` in raw frontmatter or log entries when the article author/account is known.
   ```yaml
   ---
   source_url: <url>
   ingested: YYYY-MM-DD
   sha256: <sha256 of raw body after frontmatter>
   source_title: <article title>
   source_author: <author/account>
   published: "YYYY-MM-DD HH:MM:SS"
   source_type: wechat-article
   ---
   ```
2. Create or update a durable formal page under `concepts/`, `entities/`, `comparisons/`, or `queries/`.
3. Patch related concept pages that should absorb the new idea. Examples:
   - Chromium AI Coding / repo-agent engineering articles naturally patch:
     - `concepts/agent-prompt-skill-runtime-architecture.md`
     - `concepts/agent-harness-evaluation-system.md`
     - `concepts/agent-knowledge-engineering.md`
   - Agent model / post-training / continual-learning articles naturally patch:
    - `concepts/agentic-rl-infrastructure.md`
    - `concepts/agent-memory-context-offloading.md`
    - `concepts/agent-harness-evaluation-system.md`
    - `concepts/agent-knowledge-engineering.md`
    - relevant model/entity pages such as `entities/glm-5.md` when the source names a concrete base model/ecosystem
   - LeCun / world-model / JEPA / objective-driven-AI articles that reposition LLMs as language interfaces rather than complete intelligence naturally create/update:
    - `concepts/objective-driven-ai-architecture.md` for the reusable architecture: world model predicts action consequences, cost functions encode goals/safety, search picks action sequences
    - `concepts/world-models-comprehensive-review.md` for JEPA, VLA boundary, representation collapse/SIGReg, and action-conditioned latent prediction
    - `concepts/ai-large-model-fundamentals.md` for the corrected LLM boundary: next-token prediction is powerful but not a full action-planning architecture
    - `concepts/deep-learning-research-track.md` for research-reading questions: action consequence modeling, state-space planning, representation collapse, and whether safety is post-hoc or built into the objective
    - Extract the practical rule for the user's Agent systems: side effects should have pre-action consequence prediction, read-back verification as a cost/acceptance function, and safety constraints should be excluded before execution rather than patched after failure.
   - Goal Hive / multi-Agent project-team articles (Master/Worker, BBS/task ledger, split-dispatch-verify, budgeted iteration, organization tax) naturally create/update:
    - `concepts/goal-hive-multi-agent-organization.md`
   - Classic design-pattern articles reframed for AI/Agent engineering (Singleton, Factory, Observer, Strategy, Adapter, Proxy, Command, Composite, Iterator; e.g. “设计模式已死？”) naturally create/update:
    - `concepts/software-design-patterns-agent-systems.md`
    - `concepts/agent-architecture-control-flow-patterns.md` for the distinction between Agent control-flow patterns and software boundary patterns
    - `concepts/minimal-ai-agent-framework.md` for how minimal loops still need registry/factory, command, adapter, proxy, observer, and strategy boundaries when they touch real tools
    - `concepts/agent-architecture-control-flow-patterns.md` for Multi-Agent/Blackboard/PEV control-flow implications
    - `concepts/multi-agent-organization-diagnostics.md` for organization tax, independent-judgment and consensus risks
    - `concepts/codex-agent-operating-system.md` for combining strong single-agent goal mode with an upper project-management layer
    - `concepts/agent-harness-evaluation-system.md` for task-ledger-as-trace/grader
    - `concepts/agent-knowledge-engineering.md` for ledgerized wiki/coding/research workflows
    - Extract the practical rule: do not open more agents first; first ledgerize goal, subdeliverables, evidence, risks, acceptance criteria, and read-back verification. Use a hive only when the task has 3+ independent subtasks, needs multi-perspective verification, runs longer than about 30 minutes, and benefits from traceable process records.
   - Claude Code / AI Native engineering organization articles (Fiona Fung / Claude Code team principles, bottleneck shift, `Taste is scarce, typing is not`, trust-but-verify, deleting obsolete processes, Routines/async-agent collaboration) naturally create/update:
     - `concepts/ai-native-engineering-organization.md`
     - `concepts/ai-era-talent-traits.md` for taste, verification, and choosing what to build
     - `concepts/codex-agent-operating-system.md` for work-agent dispatch, Routines/cron boundaries, async PR-candidate queues, and workflow bottleneck redesign
     - `concepts/agent-harness-evaluation-system.md` for repo spec / TDD / review-as-verification framing
     - `concepts/agentic-engineering-operating-loop.md` for parallel-Agent checking-in load, human-signal queueing, and when to pause/merge low-priority branches
     - `concepts/agent-knowledge-engineering.md` for “automation must earn its place; delete stale flows instead of stacking new ones” and “action volume is not progress”
     - Extract the practical rule: Agent speed moves scarce human work from typing/coding to verification, review, safety, taste, responsibility, metric choice, and process pruning. For the user’s Hermes system, connect this to cron/heartbeat/wiki automation: background sync can stay when it preserves facts and produces reviewable candidate queues, but noisy/stale proactive briefings or unchecked parallel Agent branches should be paused, merged, or removed.
   - Anthropic / Claude Code internal Skills lessons (skill taxonomy, progressive disclosure, verification skills, gotchas, usage measurement, marketplace/distribution) usually should **not** create a narrow one-off skill. Update the existing skill-system pages instead:
     - `concepts/skill-authoring-engineering.md` for SKILL.md-as-directory, gotchas, setup, and progressive disclosure
     - `concepts/agent-prompt-skill-runtime-architecture.md` for the nine skill classes as runtime capability routing
     - `concepts/agent-harness-evaluation-system.md` for verification skills and state evidence
     - `concepts/agent-knowledge-engineering.md` for skill governance, usage measurement, and pruning
     - Preserve a durable `queries/` page only when the article changes the user's operating model. Operationally, patch the `skill-library-operations` reference rather than adding a micro-skill.
   - Agent / Skill evaluation articles (deterministic graders, Rubric/LLM-as-judge, human calibration, trace, baselines, pass@k/pass^k, regression suites, cost/latency reports) naturally create/update:
     - `concepts/agent-skill-evaluation-framework.md` for the reusable evaluation method: deterministic scorer > Rubric scorer > human scorer, four case classes, baseline, pass^k, cost report
     - `concepts/agent-harness-evaluation-system.md` for Trace/Grader/state-check/process evidence implications
     - `concepts/skill-authoring-engineering.md` for description trigger eval and effect eval after SKILL.md/script/template changes
     - `concepts/agent-prompt-skill-runtime-architecture.md` for prompt/skill/runtime regression testing after model/tool/context changes
     - `concepts/agent-knowledge-engineering.md` for turning wiki/skill workflows into repeatable eval cases rather than one-off successful runs
     - Extract the practical rule: for the user/Hermes, start with lightweight eval cases for WeChat ingestion, Feishu task changes, PDF OCR, skill edits, and coding-agent dispatch; do not build a heavy platform before fixed inputs, traces, graders, read-back checks, and reports exist.
   - Codex / OpenClaw / Claude Code articles about ordinary office users, “普通人能不能上手”, command-line friction, video editing, Feishu message watch, high-fidelity prototypes, or “relationship changed from tool to coworker” naturally create/update:
     - `concepts/codex-office-agent-accessibility.md` for the reusable product/entry-layer idea: Agent capability is not enough; adoption depends on hiding terminal/dependency/plugin/error friction behind a conversational work entry while preserving verification.
     - `concepts/codex-agent-operating-system.md` for the work-agent side: durable threads, steering/queuing, tools, artifact workbench, and acceptance criteria.
     - `concepts/agent-era-work-paradigm.md` for Human Channel / Agent Channel: CLI/API remains the machine channel, but the human entry should be natural-language and inspectable, not a raw black terminal.
     - `concepts/ai-native-engineering-organization.md` when the article changes the organizational adoption story: AI-native spread is blocked by entry friction as well as review/taste/security.
     - Extract the practical rule: keep CLI/API/read-back verification in the bottom layer, but expose common operations (tasks, rescheduling, ingestion, message watching, prototypes) as natural-language flows with preview/confirmation for side effects.
4. Update `index.md` with the new formal page entry.
5. Update `hot.md` only when the article changes the active working context or current agent-system roadmap.
6. Update `.manifest.json` with raw sha, source URL, status, and impacted pages.
7. Append `log.md` with source URL, raw path, created pages, updated pages, and one concise note.

## Verification
Run the wiki lint script from the wiki root:
```bash
cd ~/wiki && python3 scripts/wiki_lint.py
```
Then verify the newly ingested item specifically. You can either run an inline check or reuse this skill's helper script. The helper requires both the canonical raw file and the formal page:
```bash
python3 ~/.hermes/skills/note-taking/personal-knowledge-systems/scripts/verify_user_wiki_ingest.py \
  --wiki ~/wiki \
  --raw raw/articles/<raw-file>.md \
  --page concepts/<page>.md \
  --link '[[<page>]]' \
  --updated concepts/<related-1>.md concepts/<related-2>.md
```
Success criteria:
- `issue_count` is 0, or any issues are clearly pre-existing and unrelated;
- new formal page exists and is indexed exactly once;
- raw source appears in `.manifest.json`;
- raw sha in frontmatter and manifest both match the recomputed hash of the raw body according to the current `scripts/wiki_lint.py` parser. If lint reports a mismatch on a newly-created raw file, recompute exactly from the body returned by the lint parser (`parse_fm(text)[1]`, including the leading newline after frontmatter when present) and update both raw frontmatter and `.manifest.json`;
- raw frontmatter preserves the known `source_author` / account name, with no placeholders such as `***`;
- related pages contain the expected wikilinks/source citations, and updated pages do not cite missing raw paths.

If lint reports an unrelated `index_missing` / orphan query page from an earlier run, do not ignore it silently. If it is safe and obvious, add the missing page to `index.md`, correct the formal page count/date, rerun lint, and mention it as an incidental cleanup. This keeps the final verification truly clean without conflating the old issue with the new article.

Historical warning note: the wiki may have legacy raw hash mismatch warnings. Do not treat those as blockers for a new article if the new raw's hash verifies and `issue_count` remains 0.

## Pitfalls
- Do not stop at saving the extractor output in `.hermes/data/wechat-articles`; that is only a temporary/extraction copy, not canonical wiki ingestion.
- Do not mirror the whole article into a concept page. Raw preserves the original; formal pages extract reusable structure and the user-specific implications.
- Do not make one narrow skill per article. Add article-specific notes to this reference or the relevant umbrella concept pages.
