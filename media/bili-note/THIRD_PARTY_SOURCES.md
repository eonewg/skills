# Third-party sources and attribution for `bili-note`

This file is generated during public packaging to keep upstream references visible. Verify upstream licenses before redistributing modified scripts or templates.

## URLs

- https://github.com/Rimagination/bili-note
- https://github.com/Rimagination/bili-note`，安装检查
- https://github.com/SYSTRAN/faster-whisper
- https://github.com/modelscope/FunASR
- https://github.com/openai/whisper
- https://github.com/yt-dlp/yt-dlp

## Source/license lines found in the skill files

- `- 来源、覆盖与局限`
- `https://github.com/Rimagination/bili-note`
- `Bili Note 的设计和实现参考、依托了这些主要项目与生态：`
- `- [Bilibili](https://www.bilibili.com/)：视频、字幕、评论和互动数据来源。`
- `- [yt-dlp](https://github.com/yt-dlp/yt-dlp)：可选音频下载兜底。`
- `- [OpenAI Whisper](https://github.com/openai/whisper)、[faster-whisper](https://github.com/SYSTRAN/faster-whisper)、[FunASR](https://github.com/modelscope/FunASR)：可选 ASR 转写后端。`
- `本 skill 已安装在 Hermes 当前 profile：`~/.hermes/skills/media/bili-note`。下面上游文档里的 PowerShell / `.codex` 路径只作原始参考；在本机优先使用：`
- `上游来源：`https://github.com/Rimagination/bili-note`，安装检查 commit：`5202bb06d2afc78facd19e70d19af1ac86ce87cf`。`
- `9. 按预算写 Markdown：默认写成“学习型笔记”，目标是让人或 Agent 像学完一节课或读完一篇教程一样获得概念、方法、判断标准、实践步骤和自测题；根据预算决定详略，不要把长课和短视频写成差不多字数。来源、覆盖范围和归档路径放到后半部分。正文证据默认用论文式编号 `[1][2]`，不直接堆长证据 ID。`
- `当用户问 B站/网课课程总时长、每章时长、分P目录，尤其同时要求“去知乎搜”时：先用相关搜索技能获取知乎上的定性评价和学习建议，再回到原始课程源（优先 B站 metadata）核算时长。不要把知乎或网页搜索摘要当作精确时长来源。用 `extract_bilibili.py <BVID> --out <tmpdir> --parts all --force` 读取 `metadata.json` 的 `data.pages[].duration` 和 `part`，按秒求和；如果分P标题只有“基础精讲-1~12”而没有章名，必须标注“章映射为按常见课程模块推断”。详细流程见 `references/course-playlist-duration.md`。`
- `13. `## 来源、覆盖与局限`：URL、BVID、UP、发布时间、字幕/评论覆盖、原始材料路径和局限放在后面。`
- `- 在 `## 来源、覆盖与局限` 之前放 `## 证据脚注`。脚注用有序列表写明编号和证据链接，例如 `1. [图文证据 E006](原始材料/O.../indexes/图文证据索引.md#O...-E006)`；列表后再放 reference-style 链接定义，例如 `[1]: 原始材料/O.../indexes/图文证据索引.md#O...-E006 "图文证据 E006"`，让正文里的 `[1]` 也能点击跳转。`
- `- 开头大段来源信息，读者看半天还不知道学到了什么。`
- `return "元数据、来源说明、运行摘要和字幕探测记录均已归档。"`
- `f"- source: `{source_desc}`",`
- `def extract_bvid(source: str) -> str:`
- `audio_source: str = "auto",`
- `source: str | None = None,`
- `f"- Source: {raw['source']}",`
- `def extract_opus_id(source: str) -> str:`
- `def fetch_initial_state(source: str) -> dict[str, Any]:`
- `def build_outputs(state: dict[str, Any], source: str) -> dict[str, Any]:`
- `def find_bvid(source: str) -> str:`
- `def source_kind(source: str) -> str:`
- `def find_source_id(source: str) -> str:`
- `for marker in ("\n## 证据与原文位置", "\n## 来源、覆盖与局限", "\n## 核心观点"):`
- `updated = re.sub(r"\n{3,}(## 来源、覆盖与局限)", r"\n\n\1", updated)`
