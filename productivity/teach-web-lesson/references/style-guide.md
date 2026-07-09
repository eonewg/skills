# Teach Web Lesson Template

定位：`~/teach/` 教学 HTML 的统一模板。它不是打印讲义模板，而是 **Windows 浏览器优先** 的轻量网页课程系统。不绑定任何特定考试或科目。

## 视觉方向：Claude-like warm editorial + local-first Source/Noto font stack

后续课程页默认保留 Claude 网页聊天的阅读气质，但字体方案必须适合单文件 HTML 附件交付：不依赖 Google Fonts；优先使用用户本地安装的 Source/Noto 字体，未安装时回退到系统字体：

- 普通中英混排：`Source Sans 3`, `Noto Sans SC`, `Noto Sans CJK SC`, `system-ui`, `Segoe UI`, `Microsoft YaHei UI`, `Microsoft YaHei`, `PingFang SC`, Arial, sans-serif。
- 字重：正文 `400`，重点/词汇 `600`，标题 `600–700`；避免 700/800 让英文词汇压过中文。
- 正文字号：默认 `17px`，行高 `1.7`；长英文段落可 `17.5px / 1.75`。
- 正文宽度：主布局 grid 直接约束正文列。当前课程页采用四列 grid：`.layout { grid-template-columns:164px 56px minmax(0,720px) 164px; justify-content:center; gap:0 24px; }`；折叠态为 `0px 56px 720px 0px` 且 `gap:0`。第 1 列是 `.sidebar-content`（164px ↔ 0px），第 2 列是固定按钮列（56px），第 3 列是正文（720px），第 4 列是与左面板对称的 164px 固定列。展开时面板把正文自然推右；折叠时两侧固定列都收为 0，整组 grid 居中，按钮不会卡在一段空白里。`sidebar` 用 `display:contents` 不参与布局；按钮放在 `.sidebar-content` 外，正文 `.content { grid-column:3; min-width:0; }`。
- 较长英文原文：使用 `Source Serif 4`, `Noto Serif SC`, `Georgia`, `Times New Roman`, `Songti SC`, `SimSun`, serif；短例句不要频繁切 serif。
- 暖白/奶油底：页面主背景固定使用 `#faf9f5`；正文大面仍可用 `#fffdf8`；卡片/练习/表格等聚合块使用 `#efe9de`。避免冷灰蓝背景。
- Hero 必须轻：不使用大背景色块、装饰圆、统计四宫格；eyebrow 用纯文字 `科目 · 主题 · Lesson`，h1 用 serif 大标题，hero 高度控制在约 140–160px。
- 标题 editorial 化：`.hero h1` 和 `.section h2` 使用 serif；section 序号用纯文字 accent 色（如 `01 —`），不用方形徽章/色块。
- 小标题 editorial 化：`.section h3` 也使用 serif，和 h1/h2 保持同一标题层级气质。
- 少阴影、弱边框：不用重卡片、重阴影、渐变大色块；能用留白和字体层级解决的，不用容器。
- 珊瑚橙点缀：英语和通用强调色固定使用 `#cc785c`，用于按钮、链接、标签、左线和交互反馈；不要大面积铺色。
- 文字层级：标题/强标题使用 `#141413`，正文使用 `#3d3d3a`，辅助文字使用 `#6c6a64`。
- **文字强调硬规则**：课件设计禁止使用高饱和红/蓝/绿/紫那种“语法教辅标注色”。所有教学标注统一收束到 Claude 风格暖棕色阶：`#141413` 近黑、`#3d3d3a` 深棕灰、`#6c6a64` 暖灰、`#7a6e60` 暖褐、`#5f5146` 深暖褐、`#9a8778` 浅暖褐；`#cc785c` 赤陶色只作为少量 accent/谓语动词锚点。
- **强调优先级**：先用字重、斜体、serif/sans、留白和句法位置区分；颜色只做辅助。主干/结论用近黑加粗；谓语动词用赤陶色加粗；介词短语/普通修饰用深棕灰正常体；从句/次级修饰用暖褐斜体；旁注/弱信息用暖灰。可以多用几个暖棕明度，但不要引入新的鲜艳色相。
- 可用文字工具类：`.ink-core` / `.text-green` = 近黑加粗（骨架/结论）；`.ink-predicate` / `.text-red` = 赤陶色加粗（谓语）；`.ink-modifier` / `.text-blue` = 深棕灰正常体（修饰）；`.ink-clause` / `.text-purple` = 暖褐斜体（从句）；`.ink-brown`、`.ink-brown-deep`、`.ink-brown-light`、`.ink-soft` 用于不同强弱的暖棕层级。旧 `.text-red/.text-blue/.text-green/.text-purple` 只是兼容别名，不代表真的使用红蓝绿紫。轻强调可用 `.em-strong/.em-accent/.em-clause/.em-soft` 或 `<strong>/<em>`，默认不加色块背景。
- 段落节奏：普通 `p` 保留 `margin-bottom:.8em`；`.lead` 用 `var(--text)` 加深，不靠加粗制造层级。
- 英文长句：`.english-block` / `.english-passage` 用 serif，`17.5px / 1.85`，营造外文引用段落感。
- 表格减重：`table` 背景透明，仅 `th` 使用极浅背景区分表头。
- 进度条减重：纯色 `var(--accent)`，高度 `4px`，不要渐变产品感。
- sidebar 正文是辅助信息，默认 `15px`，与 TOC 链接保持一致；桌面端 sidebar 在左侧，像书的目录页。HTML 中 `<aside class="sidebar">` 只做语义容器，内部按钮后必须包一层 `<div class="sidebar-content">...</div>`。`.sidebar-toggle` 在第 2 列，`position:sticky; top:20px`，字号 `22px`，`padding-top:4px`；`.sidebar-content` 在第 1 列，`position:sticky; top:20px`，展开 164px，折叠 `width:0` 且 `overflow:hidden`。移动端 `.sidebar` 恢复 `display:block`，`.sidebar-content` 静态宽 100%，toggle 隐藏，TOC 变为一行可点击的 flex 导航，课程信息/进度/建议动作隐藏。
- 内容自然流：不要把每个段落、步骤、目录项都做成卡片；侧栏导航/建议动作/普通步骤/普通易错点默认与页面同底色、无边界，只通过字号、暖棕色阶、留白和 hover 字色变化区分。公式、例题、callout 可用左侧 2–3px accent 竖线 + 缩进，而不是完整边框/圆角/标题色带。选择题选项用安静列表式按钮，hover 只变色不位移，正确/错误状态要有 ✓ / ✗ 文字符号；正确/错误也不要用亮绿/亮红，正确用近黑/加粗，错误用赤陶色/加粗即可。
- Section 间距靠留白形成“翻页感”：默认 48–60px 纵向间距，不用密集分割线。
- 移动端不要隐藏 TOC；改为 hero 下方/正文前方的普通导航块。
- 页面像“可阅读的聊天长文/讲义”，不是 PPT，也不是 SaaS 管理台。

## 文件结构

```text
this skill package / templates/
├── STYLE-GUIDE.md
├── lesson-template.html              # 课程页模板，复制到 <topic>/lessons/
├── reference-template.html           # 速查页模板，复制到 <topic>/reference/
├── assets/
|   │   ├── teach-components.css           # 通用布局/组件/主题
|   │   └── teach-lesson.js                # KaTeX、目录、测验交互
├── make-standalone.py                # 发送前把本地 CSS/JS 内联成单文件 HTML
└── examples/
    └── math-de-first-order-linear-demo.html
```

## 使用方式

课程页复制到：

```text
your course workspace / <topic>/lessons/000X-xxx.html
```

速查页复制到：

```text
your course workspace / <topic>/reference/xxx.html
```

模板内资源路径默认：

```html
<link rel="stylesheet" href="../../_templates/assets/teach-components.css">
<script defer src="../../_templates/assets/teach-lesson.js"></script>
```

这个相对路径适用于 `your course workspace / <topic>/lessons/*.html` 和 `your course workspace / <topic>/reference/*.html` 的本机编辑/预览。

**但发送前必须转成单文件自包含 HTML**，因为HTML attachments不会携带 `../../_templates/assets/` 里的 CSS/JS：

```bash
python3 this skill package / templates/make-standalone.py your course workspace / <topic>/lessons/000X-xxx.html
python3 this skill package / templates/validate-template.py your course workspace / <topic>/lessons/000X-xxx.html
```

交付版必须包含 `data-standalone="true"`、内联 CSS 和内联 JS；不能只发引用本地资源的 HTML。

## 设计优先级

1. Windows 浏览器可读性
2. 复习导航效率
3. 交互练习体验
4. 科目视觉统一
5. 移动端基本可看
6. 打印兼容可选

不要为了打印牺牲网页体验。

## 科目主题

在 `<body>` 使用主题类：

```html
<body class="theme-math lesson-page">      <!-- 数学一：克制蓝灰 -->
<body class="theme-cs lesson-page">        <!-- 408：克制绿青 -->
<body class="theme-english lesson-page">   <!-- 英语一：Claude-like 珊瑚橙 -->
<body class="theme-politics lesson-page">  <!-- 政治：克制红棕 -->
```

## LaTeX 规范

数学/408 页面公式必须使用 LaTeX，并由 KaTeX 渲染。

推荐：

```latex
\( y' + P(x)y = Q(x) \)

\[
y = e^{-\int P(x)\,dx}\left(\int Q(x)e^{\int P(x)\,dx}\,dx + C\right)
\]
```

不推荐：

```text
y = e^(-∫Pdx)(∫Qe^(∫Pdx)dx + C)
```

默认不要用 `$...$`，避免和普通文本、价格符号冲突。

## 页面骨架

- Hero：科目 / 章节 / 难度 / 用时 / 学习目标
- 主体：核心结论、概念、公式/算法卡、例题拆解、易错点、即时自测、复盘清单
- 侧栏：目录、阅读进度、建议动作
- 底部导航：footer-nav 必须同时包含 `← 上一课` 和 `下一课 →` 两个链接，链接到真实课程文件（下一课即使未写也填入路径而非锚点）。

## 公式卡片格式

每个重要公式必须绑定：

- 公式名
- 标准形式
- 通解 / 结论
- 适用条件
- 识别关键词
- 易错点

## 发送前检查

- 文件在目标路径存在
- 标题、科目、章节正确
- 数学公式使用 `\(...\)` / `\[...\]`
- 页面包含 KaTeX CDN
- 已运行 `python3 this skill package / templates/make-standalone.py /absolute/path.html`
- 页面包含 `data-standalone="true"`、内联 `Kaoyan Teaching Web Lesson Components` CSS 和内联 `Kaoyan Teaching Web Lesson JS`
- 页面没有裸奔公式字符串，如 `e^(-∫Pdx)`
- 已运行 `python3 this skill package / templates/validate-template.py /absolute/path.html`
- share the standalone HTML file
