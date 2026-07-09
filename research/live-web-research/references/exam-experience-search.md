# Exam experience post search notes

Use this when the user asks for Chinese exam / postgraduate entrance exam experience posts (经验贴、上岸贴、高分贴), especially from Zhihu or other semi-structured UGC sources.

## Query strategy
- Avoid starting with broad school names or prestige clusters such as `清北复交浙南 408 经验贴`; this returns admissions ads, generic prep plans, institution marketing, and unrelated discussions.
- Start from the user's target taxonomy: department aliases, project aliases, official department names, subject code, and exam code.
- Combine narrow aliases with intent words:
  - `<院系简称> 408 经验贴 知乎`
  - `<院系简称> <exam-target> 上岸 经验 知乎`
  - `<正式院系名> 计算机考研 408 上岸`
  - `<专业/项目名> 初试 专业课 分数 复盘`
- For ambiguous aliases, add official names and negative/clarifying terms. Example: `科软` is easily polluted by `软考`; use `中科大软院`, `中国科学技术大学 软件学院`, `USTC 软件学院`, `<exam-target>`, `计算机技术`, `软件工程专硕`.
- For Zhihu-only requests, constrain sources with `site:zhihu.com OR site:zhuanlan.zhihu.com`, but still expect Tardis/English mirror URLs and validate relevance from title/highlights.

## Filtering rules
Keep results that contain most of:
- first-person or cohort-specific exam experience;
- target school/department/program clearly named;
- 408/<exam-target> or professional course code clearly named;
- score, timeline, resources, mistakes, or retake/reflection details.

Reject or quarantine:
- institution marketing, paid consultation funnels, generic考研规划, soft-ad articles;
-复试模板文 unless the user asks for复试;
-考情分析-only pages unless needed to clarify exam subjects/department mapping;
- unrelated homonyms such as 软考 when searching 科软;
- generic 408 preparation Q&A that lacks the target department.

## Output shape
- Report search quality honestly: `clean personal posts found`, `mostly考情`, `mostly污染`, `needs deeper query`.
- Separate `personal experience`, `考情/院系校准`, and `discarded/noisy hits`.
- Preserve useful URLs and the exact query that found them so later wiki/archive work can reproduce the search.

## Example alias expansion for CS 408 targets
- 北大：软微、软件工程、软件与微电子学院；信科、信息科学技术学院；信工、深圳研究生院/信息工程学院。
- 浙大：浙计、计科院、计算机科学与技术学院；浙软、软件学院；工院、工程师学院。
- 南大：南计、计算机科学与技术系/学院；南软、软件学院；南大智科、人工智能学院、智能科学与技术。
- 中科大：科软、中科大软院、中国科学技术大学软件学院、USTC软件学院。