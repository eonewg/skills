#!/usr/bin/env python3
"""Refresh the user's one-way ~/wiki -> SiYuan `the assistant Wiki` readable mirror.

Source of truth remains ~/wiki. This script replaces the SiYuan notebook copy.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import subprocess
import sys
from pathlib import Path

WIKI = Path('~/wiki')
SIYUAN_WS = Path('~/SiYuan')
MIRROR = Path('~/.hermes/out/siyuan-wiki-import')
NOTEBOOK_NAME = 'the assistant Wiki'
HOMEPAGE_FILE = '00 the assistant Wiki 首页.md'
GENERATED_PAGE_FILES = [
    HOMEPAGE_FILE,
    '01 考研驾驶舱.md',
    '02 Agent 工程入口.md',
    '05 最近更新.md',
]
INCLUDE_TOP = ['index.md', 'hot.md', 'log.md']
INCLUDE_DIRS = ['concepts', 'entities', 'comparisons', 'queries']
EXPECTED_TOP = {'00 the assistant Wiki 首页', '01 考研驾驶舱', '02 Agent 工程入口', '05 最近更新', 'README', 'Wiki Index', 'Hot Context', 'log', 'concepts', 'entities', 'comparisons', 'queries'}


def run(cmd: list[str], *, cwd: Path | None = None, timeout: int = 600, capture: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None, text=True, capture_output=capture, timeout=timeout)


def run_ok(cmd: list[str], *, cwd: Path | None = None, timeout: int = 600) -> str:
    p = run(cmd, cwd=cwd, timeout=timeout)
    if p.returncode != 0:
        raise RuntimeError(f"command failed: {' '.join(cmd)}\nstdout={p.stdout}\nstderr={p.stderr}")
    return p.stdout.strip()


def json_cmd(cmd: list[str], *, timeout: int = 600):
    out = run_ok(cmd, timeout=timeout)
    return json.loads(out) if out else None


def lint_wiki() -> dict:
    out = run_ok(['python3', 'scripts/wiki_lint.py'], cwd=WIKI, timeout=180)
    data = json.loads(out)
    if data.get('issue_count') != 0:
        raise RuntimeError(f"wiki lint has issues: {json.dumps(data, ensure_ascii=False, indent=2)}")
    return data


def extract_recent_hot(limit: int = 5) -> list[str]:
    hot = WIKI / 'hot.md'
    if not hot.exists():
        return []
    items = []
    for line in hot.read_text(encoding='utf-8').splitlines():
        if line.startswith('## ') and '近期摄入' in line:
            title = line[3:].strip()
            items.append(title)
            if len(items) >= limit:
                break
    return items


def wiki_counts() -> dict[str, int]:
    return {d: sum(1 for _ in (WIKI / d).rglob('*.md')) if (WIKI / d).exists() else 0 for d in INCLUDE_DIRS}


def write_homepage() -> None:
    counts = wiki_counts()
    recent = extract_recent_hot()
    recent_lines = '\n'.join(f'- {item}' for item in recent) if recent else '- 暂无最近摄入条目。'
    now = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    content = f"""# 00 the assistant Wiki 首页

生成时间：{now}

这里是 `~/wiki` 的思源可读镜像入口。它方便你在手机和另一台电脑上读、搜、翻，但不是源仓库。

## 先记住

- 正式写入和归档仍由 the assistant 写到 `~/wiki`。
- 思源里的 `the assistant Wiki` 是阅读副本，不建议直接改。
- 如果你在思源里临时写了想法，之后可以让我迁回 wiki 正式沉淀。

## 当前主线入口

- 考研驾驶舱：[[01 考研驾驶舱]]
- Agent 工程入口：[[02 Agent 工程入口]]
- 最近更新：[[05 最近更新]]
- 考研总览：[[kaoyan-overview]]
- 每日执行系统：[[kaoyan-daily-execution-system]]
- 408：[[cs408-prep]]
- 数学：[[math-prep]]、[[zhangyu-math-learning-track]]
- 英语：[[english-prep]]、[[english-writing-advanced-expressions-2026-06]]
- 政治：[[politics-prep]]

## Agent / AI 入口

- Agent 知识工程：[[agent-knowledge-engineering]]
- Agent 上下文管理：[[agent-context-management]]
- Harness 评测系统：[[agent-harness-evaluation-system]]
- Agent 成本经济学：[[agent-cost-economics]]
- 最小 Agent 框架：[[minimal-ai-agent-framework]]
- LLM Wiki 知识编译器：[[llm-wiki-knowledge-compiler]]

## 个人操作系统入口

- 个人日看板：[[personal-daily-dashboard]]
- 学习系统：[[learning-system]]
- 自我价值与行动：[[self-worth-and-action]]
- 清醒决策系统：[[clear-thinking-decision-system]]
- 长期人生策略：[[long-term-life-strategy]]
- 能量边界维护：[[energy-boundary-maintenance-loop]]

## 兴趣 / 阅读入口

- 王者打野时间轴：[[wangzhe-jungle-time-axis]]
- 王者三段论：[[wangzhe-sanduanlun-practice]]
- 王者复盘三步法：[[wangzhe-review-three-step]]
- 微信读书主题地图：[[weread-theme-map]]
- 阅读书单：[[reading-list]]

## 最近摄入

{recent_lines}

## 适合直接搜索的词

- 考研、408、操作系统、张宇、英语作文、政治
- Agent、Harness、Context、Skill、Memory、RAG、Token
- 王者、打野、时间轴、三段论、复盘
- 自我价值、能量、边界、长期策略、清醒决策

## 当前镜像规模

- concepts：{counts.get('concepts', 0)}
- entities：{counts.get('entities', 0)}
- comparisons：{counts.get('comparisons', 0)}
- queries：{counts.get('queries', 0)}

## 常用原始入口

- [[Wiki Index]]：完整目录
- [[Hot Context]]：近期上下文
- [[log]]：wiki 操作记录
"""
    (MIRROR / HOMEPAGE_FILE).write_text(content, encoding='utf-8')


def extract_recent_log(limit: int = 12) -> list[str]:
    candidates = [WIKI / 'log.md'] + sorted((WIKI / 'log').glob('*.md'), reverse=True)
    items = []
    for log in candidates:
        if not log.exists():
            continue
        for line in log.read_text(encoding='utf-8').splitlines():
            if line.startswith('- `'):
                items.append(line)
        if len(items) >= limit:
            break
    return items[-limit:][::-1]


def write_generated_pages() -> None:
    recent_hot = extract_recent_hot(limit=8)
    recent_log = extract_recent_log(limit=12)
    recent_hot_lines = '\n'.join(f'- {item}' for item in recent_hot) if recent_hot else '- 暂无。'
    recent_log_lines = '\n'.join(recent_log) if recent_log else '- 暂无。'

    (MIRROR / '01 考研驾驶舱.md').write_text(f"""# 01 考研驾驶舱

这是给手机端/跨设备快速查看的考研入口页。正式规划仍以 the assistant 和 `~/wiki` 为准。

## 今日优先入口

- 每日执行系统：[[kaoyan-daily-execution-system]]
- 考研总览：[[kaoyan-overview]]
- 个人日看板：[[personal-daily-dashboard]]
- 学习系统：[[learning-system]]

## 科目入口

- 数学：[[math-prep]]
- 张宇数学学习主线：[[zhangyu-math-learning-track]]
- 408：[[cs408-prep]]
- 英语：[[english-prep]]
- 政治：[[politics-prep]]

## 经验共识

- 408 经验共识：[[cs408-experience-consensus-zhihu]]
- 考研收藏经验共识：[[kaoyan-favorites-experience-consensus-zhihu]]
- 公共课规划：[[kaoyan-public-subjects-plan-zhihu]]
- 复旦计算机考研样本：[[fudan-computer-kaoyan-2026]]
- 考研三战与奥德赛时期：[[odyssey-period-growth-loop]]

## 公式 / 速查

- 基本导数公式：[[basic-derivative-formulas]]
- 基本积分公式：[[basic-integral-formulas]]
- 常用等价无穷小：[[common-equivalent-infinitesimals]]
- 常用泰勒展开：[[common-taylor-expansions]]
- 常见高阶导数：[[common-higher-order-derivatives]]
- 三角恒等式：[[trigonometric-identities]]

## 英语表达

- 英语写作高级表达 2026-06：[[english-writing-advanced-expressions-2026-06]]
- 英语邮件杂志风格：[[english-email-magazine-style]]
- 外语学习与认知重构：[[foreign-language-cognition-restructuring]]

## 最近和考研相关的摄入

{recent_hot_lines}
""", encoding='utf-8')

    (MIRROR / '02 Agent 工程入口.md').write_text("""# 02 Agent 工程入口

这是 Agent / AI 工程相关页面的阅读入口。适合快速进入 Context、Memory、Skill、Harness、Eval、Cost、Knowledge Engineering 等主题。

## 基础地图

- Agent 核心概念地图：[[ai-agent-core-concept-map]]
- 从 0 开发 Agent 的十模块：[[ai-agent-10-core-modules]]
- 极简 AI Agent 框架：[[minimal-ai-agent-framework]]
- Agent 架构控制流模式：[[agent-architecture-control-flow-patterns]]
- Agent 工作范式：[[agent-era-work-paradigm]]

## Context / Memory / Skill

- Agent 上下文管理：[[agent-context-management]]
- Agent 上下文压缩策略：[[agent-context-compaction-strategies]]
- Agent 记忆与工作区统一上下文：[[agent-memory-workspace-unified-context]]
- Agent Memory Context Offloading：[[agent-memory-context-offloading]]
- Skill 编写工程：[[skill-authoring-engineering]]
- Skill 自进化工程：[[skill-self-evolution-engineering]]
- Skill 蒸馏：[[skill-distillation]]

## Harness / Eval / Runtime

- Agentic Engineering 操作回路：[[agentic-engineering-operating-loop]]
- AI Harness 工程实践：[[ai-harness-engineering-practice]]
- Agent Harness 评测系统：[[agent-harness-evaluation-system]]
- Agent Skill 测评框架：[[agent-skill-evaluation-framework]]
- Agent 状态感知 Runtime：[[agent-state-aware-runtime]]
- Loop Engineering 实操手册：[[loop-engineering-practical-manual]]

## Cost / 安全 / 治理

- Agent 成本经济学：[[agent-cost-economics]]
- AI Coding Harness Token 经济学：[[ai-coding-harness-token-economics]]
- AI Coding Agent Token 成本控制：[[ai-coding-agent-token-cost-control]]
- Agent 零信任安全框架：[[agent-zero-trust-security-framework]]
- Agent Loop 治理未解问题：[[agent-loop-governance-open-questions]]

## 知识工程 / Wiki

- Agent 知识工程：[[agent-knowledge-engineering]]
- LLM Wiki 知识编译器：[[llm-wiki-knowledge-compiler]]
- AI 研发自动化 Wiki + Skill Pack：[[ai-rd-automation-wiki-skill-pack]]
- SQL-RAG / SAG：[[sql-retrieval-augmented-generation-sag]]

## 代表案例

- Claude Code 上下文注入：[[claude-code-context-injection]]
- Codex Agent 操作系统：[[codex-agent-operating-system]]
- Codex 研究工作流：[[codex-research-workflow]]
- Goal Hive 多 Agent 组织：[[goal-hive-multi-agent-organization]]
- Minimal Agent Framework：[[minimal-ai-agent-framework]]
""", encoding='utf-8')

    (MIRROR / '05 最近更新.md').write_text(f"""# 05 最近更新

这个页面从 `hot.md` 和 `log.md` 自动生成，用来快速找“最近好像归档过但忘了名字”的东西。

## 最近摄入

{recent_hot_lines}

## 最近 wiki 操作

{recent_log_lines}

## 原始入口

- Hot Context：[[Hot Context]]
- Wiki Log：[[log]]
- Wiki Index：[[Wiki Index]]
""", encoding='utf-8')


def build_mirror() -> int:
    if MIRROR.exists():
        shutil.rmtree(MIRROR)
    MIRROR.mkdir(parents=True, exist_ok=True)
    write_homepage()
    write_generated_pages()
    landing = MIRROR / 'README.md'
    landing.write_text(f"""# the assistant Wiki 可读镜像

来源：`~/wiki`
生成时间：{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

这是给思源阅读/跨设备查看用的单向镜像，不是源仓库。正式写入、归档、lint、v2 build 仍以 `~/wiki` 为准。

包含：`index.md`、`hot.md`、`log.md`、`concepts/`、`entities/`、`comparisons/`、`queries/`。

排除：`raw/`、`facts/`、`graph/`、`reports/`、`scripts/`、`state/`、`.manifest.json`、`SCHEMA.md`。
""", encoding='utf-8')
    count = 5
    for name in INCLUDE_TOP:
        src = WIKI / name
        if src.exists():
            shutil.copy2(src, MIRROR / name)
            count += 1
    for d in INCLUDE_DIRS:
        root = WIKI / d
        if not root.exists():
            continue
        for src in root.rglob('*.md'):
            rel = src.relative_to(WIKI)
            dest = MIRROR / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            count += 1
    return count


def list_notebooks() -> list[dict]:
    return json_cmd(['siyuan-kernel', 'notebook', 'list', '-w', str(SIYUAN_WS), '-f', 'json'], timeout=60)


def create_backup() -> Path:
    ts = dt.datetime.now().strftime('%Y%m%d%H%M%S')
    backup = Path(f'~/SiYuan-backup-before-aki-wiki-refresh-{ts}.tar.gz')
    # SiYuan repo/temp can change while the kernel is running. Back up the durable workspace
    # layers needed for rollback, while excluding volatile sync/cache layers to avoid tar
    # `file changed as we read it` failures.
    run_ok([
        'tar', '-czf', str(backup),
        '--exclude=SiYuan/temp',
        '--exclude=SiYuan/repo',
        '-C', '~', 'SiYuan'
    ], timeout=600)
    return backup


def remove_existing_notebooks() -> list[str]:
    removed = []
    for nb in list_notebooks():
        if nb.get('name') == NOTEBOOK_NAME:
            run_ok(['siyuan-kernel', 'notebook', 'remove', '-w', str(SIYUAN_WS), '--id', nb['id'], '-f', 'json'], timeout=120)
            removed.append(nb['id'])
    return removed


def create_notebook() -> str:
    out = run_ok(['siyuan-kernel', 'notebook', 'create', '-w', str(SIYUAN_WS), '--name', NOTEBOOK_NAME, '-f', 'json'], timeout=60)
    nb_id = out.strip().splitlines()[-1].strip()
    if not nb_id:
        raise RuntimeError(f'cannot parse notebook id from: {out!r}')
    run_ok(['siyuan-kernel', 'notebook', 'open', '-w', str(SIYUAN_WS), '--id', nb_id, '-f', 'json'], timeout=60)
    # book icon, non-critical
    run(['siyuan-kernel', 'notebook', 'set-icon', '-w', str(SIYUAN_WS), '--id', nb_id, '--icon', '1f4da', '-f', 'json'], timeout=30)
    return nb_id


def import_mirror(nb_id: str) -> None:
    # Import content first, then generate/import homepage with real SiYuan block links.
    run_ok(['siyuan-kernel', 'import', 'md', '-w', str(SIYUAN_WS), '--file', str(MIRROR / 'README.md'), '--notebook', nb_id, '-f', 'json'], timeout=120)
    for name in INCLUDE_TOP:
        p = MIRROR / name
        if p.exists():
            run_ok(['siyuan-kernel', 'import', 'md', '-w', str(SIYUAN_WS), '--file', str(p), '--notebook', nb_id, '-f', 'json'], timeout=180)
    for d in INCLUDE_DIRS:
        p = MIRROR / d
        if p.exists():
            run_ok(['siyuan-kernel', 'import', 'md', '-w', str(SIYUAN_WS), '--file', str(p), '--notebook', nb_id, '-f', 'json'], timeout=300)
    generated_without_home = [name for name in GENERATED_PAGE_FILES if name != HOMEPAGE_FILE]
    write_linked_generated_pages_for_notebook(nb_id, generated_without_home)
    for name in generated_without_home:
        run_ok(['siyuan-kernel', 'import', 'md', '-w', str(SIYUAN_WS), '--file', str(MIRROR / name), '--notebook', nb_id, '-f', 'json'], timeout=120)
    write_linked_generated_pages_for_notebook(nb_id, [HOMEPAGE_FILE])
    run_ok(['siyuan-kernel', 'import', 'md', '-w', str(SIYUAN_WS), '--file', str(MIRROR / HOMEPAGE_FILE), '--notebook', nb_id, '-f', 'json'], timeout=120)


def frontmatter_title(path: Path) -> str:
    text = path.read_text(encoding='utf-8')
    if text.startswith('---\n'):
        end = text.find('\n---\n', 4)
        if end != -1:
            for line in text[4:end].splitlines():
                if line.startswith('title:'):
                    return line.split(':', 1)[1].strip().strip('"\'')
    return path.stem


def slug_title_map() -> dict[str, str]:
    mapping = {
        'Wiki Index': 'Wiki Index',
        'Hot Context': 'Hot Context',
        'log': 'log',
        '00 the assistant Wiki 首页': '00 the assistant Wiki 首页',
        '01 考研驾驶舱': '01 考研驾驶舱',
        '02 Agent 工程入口': '02 Agent 工程入口',
        '05 最近更新': '05 最近更新',
    }
    for d in INCLUDE_DIRS:
        root = WIKI / d
        if not root.exists():
            continue
        for p in root.rglob('*.md'):
            mapping[p.stem] = frontmatter_title(p)
    return mapping


def notebook_title_id_map(nb_id: str) -> dict[str, str]:
    root = SIYUAN_WS / 'data' / nb_id
    mapping: dict[str, str] = {}
    for p in root.rglob('*.sy'):
        try:
            data = json.loads(p.read_text(encoding='utf-8'))
        except Exception:
            continue
        title = (data.get('Properties') or {}).get('title')
        doc_id = data.get('ID')
        if title and doc_id:
            mapping[title] = doc_id
    return mapping


def linkify_wikilinks(markdown: str, slug_to_id: dict[str, str], slug_to_title: dict[str, str]) -> str:
    import re
    pattern = re.compile(r'\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|([^\]]+))?\]\]')

    def repl(match: re.Match) -> str:
        target = match.group(1).strip()
        label = (match.group(2) or slug_to_title.get(target) or target).strip()
        block_id = slug_to_id.get(target)
        if not block_id:
            return match.group(0)
        return f'[{label}](siyuan://blocks/{block_id})'

    return pattern.sub(repl, markdown)


def write_linked_generated_pages_for_notebook(nb_id: str, page_files: list[str]) -> None:
    slug_to_title = slug_title_map()
    title_to_id = notebook_title_id_map(nb_id)
    slug_to_id = {slug: title_to_id[title] for slug, title in slug_to_title.items() if title in title_to_id}
    for name in page_files:
        path = MIRROR / name
        raw = path.read_text(encoding='utf-8')
        path.write_text(linkify_wikilinks(raw, slug_to_id, slug_to_title), encoding='utf-8')


def verify(nb_id: str) -> dict:
    docs = json_cmd(['siyuan-kernel', 'document', 'list', '-w', str(SIYUAN_WS), '--notebook', nb_id, '-f', 'json'], timeout=120)
    top_names = {d.get('name') for d in docs}
    missing = sorted(EXPECTED_TOP - top_names)
    if missing:
        raise RuntimeError(f'missing top-level docs: {missing}; got={sorted(top_names)}')
    child_counts = {d.get('name'): d.get('subFileCount', 0) for d in docs}
    sy_count = int(run_ok(['bash', '-lc', f"find {SIYUAN_WS / 'data' / nb_id} -name '*.sy' | wc -l"], timeout=60))
    mirror_count = int(run_ok(['bash', '-lc', f"find {MIRROR} -type f -name '*.md' | wc -l"], timeout=60))
    smoke = {}
    for query in ['agent', '考研']:
        data = json_cmd(['siyuan-kernel', 'search', query, '-w', str(SIYUAN_WS), '--notebook', nb_id, '-f', 'json'], timeout=120)
        smoke[query] = {'matchedBlockCount': data.get('matchedBlockCount'), 'blocks': len(data.get('blocks', []))}
        if not data.get('blocks'):
            raise RuntimeError(f'smoke search returned no blocks for {query!r}')
    homepage_id = None
    for d in docs:
        if d.get('name') == '00 the assistant Wiki 首页':
            homepage_id = d.get('id')
            break
    homepage_links_ok = False
    if homepage_id:
        km = run_ok(['siyuan-kernel', 'block', 'kramdown', '-w', str(SIYUAN_WS), '--id', homepage_id, '-f', 'json'], timeout=60)
        homepage_links_ok = 'siyuan://blocks/' in km and '[[kaoyan-overview]]' not in km
    if not homepage_links_ok:
        raise RuntimeError('homepage internal links were not converted to SiYuan block links')
    return {'top_docs': sorted(top_names), 'child_counts': child_counts, 'sy_count': sy_count, 'mirror_md_count': mirror_count, 'smoke': smoke, 'homepage_links_ok': homepage_links_ok}


def install_aki_wiki_css_snippet() -> str:
    """Install/update a lightweight CSS snippet for the assistant Wiki reading pages."""
    import urllib.request

    css = r'''
/* the assistant Wiki 阅读增强：只做轻量视觉优化，不改内容数据 */
.protyle-wysiwyg [data-node-id] span[data-type~="a"] {
  text-decoration-thickness: 1.5px;
  text-underline-offset: 3px;
}
.protyle-wysiwyg [data-node-id][data-type="NodeHeading"] {
  scroll-margin-top: 84px;
}
.protyle-wysiwyg [data-node-id][data-type="NodeList"] {
  line-height: 1.72;
}
.protyle-wysiwyg [data-node-id][data-type="NodeHeading"][data-subtype="h1"] {
  padding-bottom: 0.35em;
  border-bottom: 1px solid var(--b3-border-color);
}
.protyle-wysiwyg [data-node-id][data-type="NodeHeading"][data-subtype="h2"] {
  margin-top: 1.25em;
}
.protyle-wysiwyg [data-node-id] code {
  border-radius: 6px;
  padding: 0.08em 0.35em;
}
@media (max-width: 720px) {
  .protyle-wysiwyg {
    font-size: 16px;
    line-height: 1.72;
  }
}
'''.strip()
    conf = json.loads((SIYUAN_WS / 'conf' / 'conf.json').read_text(encoding='utf-8'))
    token = (conf.get('api') or {}).get('token', '')

    def post(path: str, payload: dict) -> dict:
        req = urllib.request.Request(
            'http://127.0.0.1:6806' + path,
            data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
            headers={'Content-Type': 'application/json', 'Authorization': 'Token ' + token},
            method='POST',
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        if data.get('code') != 0:
            raise RuntimeError(f'{path} failed: {data}')
        return data

    snippets = post('/api/snippet/getSnippet', {'type': 'all', 'enabled': 2}).get('data', {}).get('snippets', [])
    target = None
    for item in snippets:
        if item.get('name') == 'the assistant Wiki 阅读增强':
            target = item
            break
    new_item = {
        'id': target.get('id') if target else '',
        'name': 'the assistant Wiki 阅读增强',
        'type': 'css',
        'enabled': True,
        'disabledInPublish': False,
        'content': css,
    }
    if target:
        target.update(new_item)
    else:
        snippets.append(new_item)
    post('/api/snippet/setSnippet', {'snippets': snippets})
    post('/api/setting/setSnippet', {'enabledCSS': True, 'enabledJS': bool(conf.get('snippet', {}).get('enabledJS', True))})
    return 'the assistant Wiki 阅读增强'


def verify_css_snippet() -> bool:
    conf_path = SIYUAN_WS / 'data' / 'snippets' / 'conf.json'
    if not conf_path.exists():
        return False
    snippets = json.loads(conf_path.read_text(encoding='utf-8'))
    return any(item.get('name') == 'the assistant Wiki 阅读增强' and item.get('type') == 'css' and item.get('enabled') for item in snippets)


def sync_push() -> dict:
    run_ok(['siyuan-kernel', 'sync', 'push', '-w', str(SIYUAN_WS), '-f', 'json'], timeout=600)
    status = json_cmd(['siyuan-kernel', 'sync', 'status', '-w', str(SIYUAN_WS), '-f', 'json'], timeout=60)
    return status


def prune_old_refresh_backups(keep_path: Path, keep_last: int = 1) -> list[str]:
    """Move old the assistant Wiki refresh backups to Trash, keeping only the newest N.

    Does not touch the older S3-import baseline backup; that is a different rollback point.
    """
    trash = Path('~/.local/share/Trash/files')
    info = Path('~/.local/share/Trash/info')
    trash.mkdir(parents=True, exist_ok=True)
    info.mkdir(parents=True, exist_ok=True)
    backups = sorted(Path('~').glob('SiYuan-backup-before-aki-wiki-refresh-*.tar.gz'), key=lambda p: p.stat().st_mtime, reverse=True)
    keep = set(backups[:keep_last]) | {keep_path}
    moved = []
    for p in backups:
        if p in keep:
            continue
        dest = trash / p.name
        i = 1
        while dest.exists():
            dest = trash / f'{p.stem}.{i}{p.suffix}'
            i += 1
        shutil.move(str(p), str(dest))
        (info / (dest.name + '.trashinfo')).write_text(
            '[Trash Info]\nPath=' + str(p) + '\nDeletionDate=' + dt.datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + '\n',
            encoding='utf-8',
        )
        moved.append(str(dest))
    return moved


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--no-sync', action='store_true', help='do not push SiYuan S3 after import')
    ap.add_argument('--no-backup', action='store_true', help='skip SiYuan backup tarball (not recommended)')
    args = ap.parse_args()

    if not WIKI.exists():
        raise SystemExit(f'wiki not found: {WIKI}')
    if not SIYUAN_WS.exists():
        raise SystemExit(f'SiYuan workspace not found: {SIYUAN_WS}')

    lint = lint_wiki()
    mirror_count = build_mirror()
    backup = None if args.no_backup else create_backup()
    removed = remove_existing_notebooks()
    nb_id = create_notebook()
    import_mirror(nb_id)
    css_snippet = install_aki_wiki_css_snippet()
    verification = verify(nb_id)
    verification['css_snippet_ok'] = verify_css_snippet()
    sync_status = None if args.no_sync else sync_push()
    pruned_backups = [] if backup is None else prune_old_refresh_backups(backup, keep_last=1)

    print(json.dumps({
        'ok': True,
        'source': str(WIKI),
        'mirror': str(MIRROR),
        'notebook': {'name': NOTEBOOK_NAME, 'id': nb_id, 'removed_ids': removed},
        'backup': str(backup) if backup else None,
        'pruned_backups': pruned_backups,
        'css_snippet': css_snippet,
        'lint': {'formal_pages': lint.get('formal_pages'), 'issue_count': lint.get('issue_count'), 'warning_count': lint.get('warning_count')},
        'mirror_md_count': mirror_count,
        'verification': verification,
        'sync_status': sync_status,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as e:
        print(json.dumps({'ok': False, 'error': str(e)}, ensure_ascii=False, indent=2), file=sys.stderr)
        raise SystemExit(1)
