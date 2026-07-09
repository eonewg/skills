---
name: concept-investigation-loop
description: Use when the user is stuck at memorizing a definition or wants to understand a math/408/CS concept by tracing its origin, prerequisites, relationships, dependent applications, and next learning clue. Adapted from SarkAzia/baiyueguang-learning-skill without the meme-heavy wording.
version: 1.0.0
author: Hermes Agent, adapted from SarkAzia/baiyueguang-learning-skill
license: MIT-compatible-adaptation
metadata:
  hermes:
    tags: [study, concept-learning, kaoyan, math, cs408]
---

# Concept Investigation Loop

## Purpose

Turn an abstract concept from “definition to memorize” into an object to investigate.

This is useful for the user when a concept feels dry, disconnected, or only memorized verbally. It is especially suited for:

- Math: limits, derivatives, rank, basis, linear independence, eigenvalues, convergence.
- 408: recursion, interrupt, pipeline, cache, virtual memory, deadlock, TCP congestion control.
- CS/AI: embeddings, attention, compiler phases, scheduling, indexing, transaction isolation.

Do **not** use this as a replacement for problem practice, active recall, or exam-oriented error analysis. It is an understanding starter and concept-network builder.

## Memory preflight

For the user study tasks, read:

```bash
~/.hermes/scripts/memory_route.py study
```

Normally this returns `memory-modules/study-memory.md` and `user-modules/study-profile.md`. Use those to calibrate subject priority and exam timing.

## Trigger conditions

Use this when the user says or implies:

- “这个概念到底是什么 / 有什么用？”
- “我只会背定义。”
- “这个和前后知识怎么连？”
- “帮我把这个概念串起来。”
- “数学/408 这个点学不进去。”

Avoid it when the user needs fast exam drilling, a direct answer, or a proof/problem solution unless concept confusion is the bottleneck.

## Core investigation questions

For a concept `X`, answer in this order:

1. **它是谁？** — Plain-language identity: what is X actually describing?
2. **它为什么被发明？** — What problem or inconvenience made X necessary?
3. **没有它会卡在哪里？** — What breaks or becomes hard if X does not exist?
4. **前置线索** — What must be understood before X?
5. **关系网** — What concepts often appear with X, and what is the relation?
6. **谁依赖它？** — Which later concepts, applications, or question types depend on X?
7. **典型题型/应用** — Where does X show up in exam problems or real systems?
8. **重复信息 vs 新信息** — Which facts are just rephrasings, and which add real understanding?
9. **下一条线索** — What should be investigated next, and why?

## Output format for the user

Keep the output direct and not too theatrical. Use this structure:

```text
结论：<one-sentence useful understanding>

1. 它是谁
<plain explanation>

2. 它为什么出现
<origin/problem>

3. 没有它会怎样
<failure/inconvenience>

4. 关系网
A → X：<relation>
X → B：<relation>
X ↔ C：<relation>

5. 谁依赖它
- <later concept/application/question type>

6. 考试/做题里怎么出现
- <question pattern>
- <trap>

7. 重复信息 / 新信息
- 重复信息：<what is merely another wording>
- 新信息：<what actually changes understanding>

8. 下一条线索
<next concept + why>
```

## Quality rules

- Start with one clear conclusion before the sections.
- Use concrete examples, not only slogans like “建立关系网”.
- For math, include a minimal formula only after the intuition is clear.
- For 408, connect the concept to hardware/software/system behavior and typical exam traps.
- End with exactly one next concept unless the user asks for a map.
- If the concept requires prerequisite knowledge the user likely lacks, say that plainly and route to the prerequisite first.

## Example: linear independence

结论：线性无关不是“背一个定义”，而是在问：这组向量里有没有人是多余的。

1. 它是谁
线性无关描述一组向量之间有没有“重复贡献”。如果其中一个向量能由其他向量拼出来，它就不是新的方向。

2. 它为什么出现
我们需要判断一组向量能不能作为坐标系统、基底、解空间骨架。如果有多余向量，维数和秩都会被虚高。

3. 没有它会怎样
你会分不清“真的有几个独立方向”，也就没法可靠地谈基、维数、秩、方程组自由变量。

4. 关系网
向量组 → 线性无关：判断向量是否提供新方向。
线性无关 → 基：既无冗余又能张成空间时成为基。
线性无关 ↔ 秩：最大线性无关组的个数就是秩。

5. 谁依赖它
- 基与维数
- 矩阵的秩
- 方程组解结构
- 特征向量组判断

6. 考试/做题里怎么出现
- 判断向量组是否线性无关。
- 给参数，求让向量组相关/无关的取值。
- 陷阱：只看向量个数，不看所在空间维数和行列式/秩。

7. 重复信息 / 新信息
- 重复信息：“不能互相表示”“没有冗余”“每个方向都有新贡献”本质上在说同一件事。
- 新信息：它和秩、基、维数、方程组自由变量是同一条链上的节点。

8. 下一条线索
秩。因为秩就是把“最多有多少个独立方向”变成一个可计算的数。

## Attribution

This skill adapts the useful core of SarkAzia/baiyueguang-learning-skill: transforming knowledge from static definitions into investigative relationship networks. The meme-heavy framing is intentionally removed for the user's long-term study system.
