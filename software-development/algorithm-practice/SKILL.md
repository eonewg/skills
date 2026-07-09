---
name: algorithm-practice
description: Use when the user wants to start LeetCode/algorithm practice, finish a problem, review due problems, or maintain a lightweight spaced-repetition loop for coding interview / CS algorithm practice. Adapted from beyondaprilzjl-lab/leetcode-skill for Hermes + WSL + local study data, without Obsidian dependency.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [leetcode, algorithms, study, spaced-repetition, coding-practice]
    related_skills: [test-driven-development, structured-problem-solving]
source:
  upstream: https://github.com/beyondaprilzjl-lab/leetcode-skill
  upstream_commit: f09452b
  adapted_for: Hermes Agent user-local skill library
  data_dir: ~/.hermes/data/study/leetcode
---

# Algorithm Practice

## Overview

This skill runs a small local LeetCode / algorithm-practice loop for the user. It is adapted from `beyondaprilzjl-lab/leetcode-skill`, but reshaped for Hermes:

- data lives under `~/.hermes/data/study/leetcode/`, not Obsidian by default;
- one umbrella skill covers the three flows instead of installing three separate Claude Code skills;
- all date math assumes Linux / WSL (`date -d`), not macOS `date -v`;
- practice is positioned as algorithm hand-feel / CS interview ability, not as something that should displace math or 408 mainline study;
- the user's current plan is to start this after the December postgraduate entrance exam, around January next year. Until then, do not proactively schedule LeetCode into the考研 mainline unless he explicitly asks.

Core loop:

```text
start → pick due review + next new problem
finish → Socratic recall + write note + schedule 3-day review
review → active recall first + compare note + schedule 7/15-day intervals or graduate
```

## When to Use

Use this skill when the user says things like:

- “开始刷题” / “今天刷什么” / “lc go” / `/lc-go`
- “这题做完了” / “复盘这道题” / “lc done” / `/lc-done`
- “复习旧题” / “今天该复习什么” / “考考我” / `lc review` / `/lc-review`
- asks to initialize or repair the local LeetCode practice files

Do not use it for:

- 408 course scheduling or exam-study prioritization — use the existing study/task workflow first;
- generic coding-project debugging;
- silently creating Feishu tasks unless the user asks to schedule reminders.

## Local Data Layout

Default directory:

```bash
DIR="${LC_DATA_DIR:-~/.hermes/data/study/leetcode}"
```

Files:

```text
$DIR/
├── _题单.md       # Hot 100 checklist with links/slugs/topics
├── _复习表.md     # review ledger + streak metadata
└── 题解/          # one Markdown note per solved problem
```

If `LC_DATA_DIR` is set, respect it. Otherwise use the default above.

## Flow: Start Practice (`lc-go`)

Goal: remove decision friction. This flow is read-only.

1. Run `date +%Y-%m-%d` for today. Do not rely on memory for dates.
2. Resolve `DIR="${LC_DATA_DIR:-~/.hermes/data/study/leetcode}"`.
3. If `_题单.md` or `_复习表.md` is missing, initialize from this skill's templates or tell the user the exact missing file.
4. Read `_复习表.md`; in “待复习 / 进行中”, select rows where `下次复习 <= today`.
5. Read `_题单.md`; choose the first unchecked `- [ ]` problem as the next new problem.
6. Output a compact practice card:

```text
连续打卡 N 天｜已完成 X/100

今日复习：M 题到期
- 49. 字母异位词分组｜阶段0｜https://leetcode.cn/problems/group-anagrams/

今日新题：
1. 两数之和｜哈希｜https://leetcode.cn/problems/two-sum/

做完回来发：lc done
```

Rules:

- Do not explain the problem here.
- If due reviews > 3, suggest doing the oldest 2–3 first.
- If no review is due, say so and push the new problem.
- If all 100 problems are checked, switch to pure review / graduation mode.

## Flow: Finish a Problem (`lc-done`)

Goal: prevent fake understanding. Do not directly write the note before the user has explained the solution.

1. Confirm problem number/title and ask for AC code if not provided.
2. Ask 3–4 specific Socratic questions in one message:
   - Why this data structure / algorithm?
   - What was the key invariant or transition?
   - What boundary case is easy to miss?
   - What are time and space complexity?
   - For DP: state definition, transition, base case, answer position.
3. If the answer is vague, push once more before writing the note.
4. Write a concise note to `$DIR/题解/NNNN-题名.md` using the template below.
5. In `_题单.md`, mark that problem `- [x]`.
6. In `_复习表.md`, add/update a row in “待复习 / 进行中”:

```text
| 题号 | 题名 | 专题 | 笔记 | 阶段 | 下次复习 | 掌握度 | 复习次数 |
| N | 题名 | 专题 | [[题解/NNNN-题名]] | 0 | <today+3> | 🌱 | 0 |
```

7. Update frontmatter:
   - `total_done += 1` only if the checklist was previously unchecked.
   - `last_active == today`: keep streak unchanged.
   - `last_active == yesterday`: `streak += 1`.
   - otherwise: `streak = 1`.
   - set `last_active` to today.

Linux date commands:

```bash
today=$(date +%Y-%m-%d)
yesterday=$(date -d "yesterday" +%Y-%m-%d)
next=$(date -d "+3 days" +%Y-%m-%d)
```

### Problem Note Template

```markdown
---
tags:
  - leetcode
题号: <N>
难度: <简单/中等/困难>
专题: <专题>
created: <YYYY-MM-DD>
source: https://leetcode.cn/problems/<slug>/
---

# N. 题名

> [!abstract] 一句话本质
> <这题的核心判断，不是背代码，而是抓住结构。>

## 题目
<一两句话复述。>

## 思路
<从朴素想法到优化；DP/回溯/图论题写清状态、边界、转移或搜索剪枝。>

## 关键卡点
- <用户真实卡点>
- <易错边界>

## 代码
```python
<AC code>
```

## 复杂度
- 时间：O(...)
- 空间：O(...)

## 一句话记忆点
> <下次看到类似题时能触发回忆的一句话。>
```

## Flow: Review Due Problems (`lc-review`)

Goal: active recall first, answer later.

1. Resolve today and data dir.
2. Read `_复习表.md`, select due rows where `下次复习 <= today`, oldest first.
3. For one problem at a time, give only title + link first. Do not show the note yet.
4. Ask the user to recall:
   - approach / data structure;
   - invariant or core transition;
   - complexity;
   - optionally re-code or AC it again.
5. Then read the problem note and compare against the answer.
6. Decide pass/fail:
   - pass stage 0 → 1: next review `+7 days`, mastery `🌿`;
   - pass stage 1 → 2: next review `+15 days`, mastery `🌳`;
   - pass stage 2 → 3: graduate; move from “待复习 / 进行中” to “已毕业 🎓” with graduation date;
   - fail: reset stage 0, next review `+3 days`, mastery `🌱`.
7. Increment review count and update streak/last_active using the same rule as `lc-done`.

Linux date commands:

```bash
date -d "+7 days" +%Y-%m-%d
date -d "+15 days" +%Y-%m-%d
```

## Initialization / Repair

If the data directory is missing:

```bash
mkdir -p ~/.hermes/data/study/leetcode/题解
```

Then copy the templates from this skill:

```text
templates/hot100.md     → _题单.md
templates/review-ledger.md → _复习表.md
```

Never overwrite existing `_题单.md`, `_复习表.md`, or `题解/*.md` without explicitly saying what would be overwritten.

## Common Pitfalls

- Do not install upstream `install.sh` directly into `~/.claude/skills/`; this adapted skill is for Hermes.
- Do not write into Obsidian unless the user explicitly asks; the user's default is local study data under `~/.hermes/data/study/`.
- Do not let LeetCode practice steal the whole morning from math / 408 when those are the active exam priorities.
- Do not use macOS `date -v`; this host is WSL/Linux, use `date -d`.
- Do not trust guessed LeetCode slugs when the checklist already contains links. Prefer the link in `_题单.md`.
- Do not mark a problem complete before the user has actually solved it or clearly asked you to record past completion.

## Verification Checklist

- [ ] `_题单.md` exists and has 100 unchecked/checked Hot 100 items.
- [ ] `_复习表.md` exists and has `streak`, `last_active`, and `total_done` frontmatter.
- [ ] `题解/` exists.
- [ ] `lc-go` reads only and does not mutate files.
- [ ] `lc-done` updates note + checklist + review ledger.
- [ ] `lc-review` uses active recall before revealing notes.
- [ ] Date math uses live `date` command output.
