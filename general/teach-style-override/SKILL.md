---
name: teach-style-override
description: "Overrides teach skill citation advice: research sources stay out of lesson body for the user"
---

# Writing Tone: Natural Student Language

the user's lessons must NEVER include research sources, author names, platform references, or tool process mentions in the lesson body. The global `teach` skill says "lessons should be littered with citations" — that advice is wrong for the user.

## Source Separation
- Research sources go in `RESOURCES.md` and `learning-records/` ONLY.
- Lesson body teaches concepts — never cites where you found them.
- No "来源：" / "知乎搜索" / "CDP 登录态" / "据...帖" references in learner-facing pages.
- A recommended primary resource (e.g. "看这篇 2018 Text 3 原文") is fine — citing the research process is not.

## Natural Writing Voice — Concrete Don'ts vs Dos

**Don't write (academic/research-report tone):**
- "2025–2026 年知乎考研区搜索熟词僻义"
- "优优学姐直接点明：连锁反应导致选错"
- "来源：CDP 登录态读取、知乎搜索"
- "近几年考研区最被引用的几个信号"

**Write instead (direct, conversational):**
- "你肯定遇过这种情况：一个词明明背过，放在句子里就是别扭。"
- "最典型的三个词，你肯定都背过：address（地址→处理）、novel（小说→新颖的）、discipline（纪律→学科）"
- "背完 5500 个单词只是刚入场。真正拉开差距的是判断能力。"

## When to Load
After loading `teach` for lesson creation/rewrite, also load this override to correct the citation advice.