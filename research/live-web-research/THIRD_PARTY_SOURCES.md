# Third-party sources and attribution for `live-web-research`

This file is generated during public packaging to keep upstream references visible. Verify upstream licenses before redistributing modified scripts or templates.

## Source/license lines found in the skill files

- `homepage: https://baike.baidu.com/`
- `homepage: https://xueshu.baidu.com/`
- `homepage: https://cloud.baidu.com/doc/qianfan/s/Amhcvzqs0`
- `该组件为付费功能，具体计费请参考[官方文档](https://cloud.baidu.com/doc/qianfan/s/Umh4sv6gb)。`
- `homepage: https://cloud.baidu.com/doc/qianfan/s/Lmhcvvxb2`
- `description: 使用火山引擎融合信息搜索 API 进行联网搜索，返回适合 AI 使用的网页或图片结果。当用户需要在线查资料、确认最新信息、搜索新闻、百科、公告、政策、价格、产品动态、查官网或文档站内容、找来源链接、核实某个说法、比较不同网站的说法、限定站点搜索，或需要搜图、找配图、找某个主题的图片结果时使用。常见表达包括“查一下”“搜一下”“帮我看看”“有没有最新消息”“给我官网链接”“确认一下是不是真的”“找下出处”“搜几张图”“找相关图片”。即使用户没有明确说“联网搜索”，只要任务依赖在线事实、时效性或来源引用，也应优先使用本 skill。支持 API Key 和 AK/SK 两种鉴权方式。`
- `homepage: https://www.volcengine.com/docs/85508/1650263`
- `- 需要给回答附上来源链接`
- `- 用户没有明确说“联网”，但任务本质上需要最新信息、在线查证或来源支撑时`
- `- `--auth-level 1`：优先权威来源`
- `# 查权威来源`
- `- 涉及高可信度主题时，优先使用权威来源过滤`
- `## 参考资料`
- `# 返回AI总结+参考链接`
- `# 获取完整响应（包含AI总结和参考链接）`
- `print(result["references"])  # 参考链接`
- `# 获取总结+参考链接`
- `- 具体费率请参考百度千帆官方文档`
- `| 返回内容 | 原始搜索结果列表 | AI总结 + 参考链接 |`
- `- [API 参考](https://cloud.baidu.com/doc/qianfan-api/s/wmjqtqr7w)`
- `# 返回总结+参考链接`
- `homepage: https://tavily.com`
- `CLI 返回的每条新闻通常包含标题、摘要、来源、链接等字段。输出时**必须**按以下结构展示：`
- `来源：作者或媒体名称`
- `**来源：腾讯新闻**`
- `- **来源**：`来源：` 后跟 CLI 返回的作者或媒体名称；CLI 无该字段时可省略。`
- `- **摘要**：来源下方紧跟；CLI 无摘要字段时可省略。`
- `- 其他有价值字段（发布时间、标签等）可在来源下方补充。`
- `- **列表末尾**：所有新闻条目之后，另起一行加粗展示 `**来源：腾讯新闻**`。`
