---
name: qianfan-web-summary-pro
description: 百度千帆智能搜索生成高性能版(Pro) - 整合大模型与实时搜索能力，直接返回AI总结的内容，支持思考模式、人设指令等高级功能
metadata:
  openclaw:
    emoji: 🧠
    requires:
      bins:
        - python3
      env:
        - BAIDU_API_KEY
    primaryEnv: BAIDU_API_KEY
---

# 百度千帆智能搜索生成高性能版 (Pro)

基于百度千帆平台的智能搜索生成 API（`/v2/ai_search/web_summary`），整合大模型与实时搜索能力，直接返回AI总结的内容。

## 功能特点

- **AI 总结**: 直接返回大模型总结的搜索结果
- **实时搜索**: 基于百度搜索的实时信息检索
- **多模态支持**: 支持网页、视频、图片搜索
- **高级功能**: 支持思考模式、人设指令、时间过滤、采样参数等
- **简单计费**: 不再区分搜索费用和大模型费用，仅按调用量收费

## 使用方法

### 1. 命令行使用

```bash
# 简单搜索（返回AI总结的文本）
python3 skills/qianfan-web-summary/scripts/summarize.py '{"query":"今天天气","simple":true}'

# 返回AI总结+参考链接
python3 skills/qianfan-web-summary/scripts/summarize.py '{"query":"OpenClaw 是什么","with_refs":true}'

# 指定返回搜索结果数量
python3 skills/qianfan-web-summary/scripts/summarize.py '{"query":"人工智能","top_k":5}'

# 使用人设指令
python3 skills/qianfan-web-summary/scripts/summarize.py '{"query":"新闻","instruction":"请用一句话总结"}'

# 使用思考模式
python3 skills/qianfan-web-summary/scripts/summarize.py '{"query":"复杂问题","thinking":true}'

# 返回完整响应
python3 skills/qianfan-web-summary/scripts/summarize.py '{"query":"今天天气"}'
```

### 2. Python SDK 使用

```python
from skills.qianfan_web_summary.scripts.summarize import QianfanWebSummary

# 初始化
search = QianfanWebSummary()  # 从环境变量读取 API Key

# 获取完整响应（包含AI总结和参考链接）
result = search.search("今天天气")
print(result["choices"][0]["message"]["content"])  # AI总结的内容
print(result["references"])  # 参考链接

# 只获取AI总结的文本
summary = search.search_simple("近日油价调整", top_k=5)
print(summary)

# 获取总结+参考链接
result = search.search_with_references("OpenClaw 是什么", top_k=5)
print(result["summary"])     # AI总结
print(result["references"])  # 参考链接

# 多模态搜索
result = search.search_multimodal(
    query="猫咪视频",
    web_count=10,
    video_count=5,
    image_count=10
)

# 使用人设指令
result = search.search_with_instruction(
    query="新闻",
    instruction="请用简洁的语言回答",
    top_k=5
)

# 按时间范围搜索（最近一周）
result = search.search_with_time_range(
    query="最新新闻",
    gte="now-1w/d",
    lt="now/d",
    top_k=5
)

# 使用思考模式
result = search.search_with_thinking("复杂问题", top_k=5)
```

## API 参数说明

### 搜索方法参数

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| query | str | 是 | - | 搜索查询词 |
| instruction | str | 否 | - | 人设指令，限制输出风格（最长4000字符） |
| resource_filters | List[ResourceFilter] | 否 | web:20 | 资源类型过滤器 |
| search_filter | SearchFilter | 否 | - | 搜索过滤条件（站点、时间范围） |
| temperature | float | 否 | - | 采样参数，范围(0, 1] |
| top_p | float | 否 | - | 采样参数，范围(0, 1] |
| response_format | ResponseFormat | 否 | text | 输出格式控制 |
| model | str | 否 | non_thinking | 思考模式：thinking/auto_thinking/non_thinking |
| stream | bool | 否 | false | 是否使用流式返回 |

### 资源类型限制

| 类型 | 最大数量 | 说明 |
|------|----------|------|
| web | 50 | 网页搜索 |
| video | 10 | 视频搜索 |
| image | 30 | 图片搜索 |

### 思考模式

| 模式 | 说明 |
|------|------|
| thinking | 开启思考能力，返回 reasoning_content |
| auto_thinking | 自动判断是否需要思考 |
| non_thinking | 不开启思考（默认） |

### 时间范围参数

支持 `gte`, `gt`, `lte`, `lt` 参数：

- `now/d` - 今天
- `now-1w/d` - 一周前
- `now-1M/d` - 一个月前
- `now-3M/d` - 三个月前
- `now-6M/d` - 六个月前
- `now-1y/d` - 一年前

## 返回结果格式

```json
{
  "request_id": "xxx",
  "choices": [
    {
      "index": 0,
      "finish_reason": "stop",
      "message": {
        "role": "assistant",
        "content": "AI总结的内容...",
        "reasoning_content": "思考过程（仅thinking模式）"
      }
    }
  ],
  "references": [
    {
      "id": 1,
      "url": "https://example.com/article",
      "title": "文章标题",
      "content": "原文摘要...",
      "date": "2026-02-20 12:00:00",
      "website": "网站名称",
      "type": "web"
    }
  ]
}
```

## 环境配置

需要设置环境变量：

```bash
export BAIDU_API_KEY=<redacted>
```

或在代码中传入：

```python
search = QianfanWebSummary(api_key="your-api-key")
```

## 计费说明

- 每日免费额度：100次
- 不再区分搜索费用和大模型费用
- 仅按调用量收费
- 具体费率请参考百度千帆官方文档

## 与 baidu-search 的区别

| 特性 | baidu-search | qianfan-web-summary-pro |
|------|--------------|-------------------------|
| API 端点 | `/v2/ai_search/chat/completions` | `/v2/ai_search/web_summary` |
| 返回内容 | 原始搜索结果列表 | AI总结 + 参考链接 |
| 思考模式 | ❌ | ✅ |
| 人设指令 | ❌ | ✅ |
| 时间过滤 | ❌ | ✅ |
| 采样参数 | ❌ | ✅ |
| 适用场景 | 需要原始搜索结果 | 需要AI总结的内容 |

## 相关链接

- [百度千帆官方文档](https://cloud.baidu.com/doc/qianfan/s/Kmiy99ziv)
- [API 参考](https://cloud.baidu.com/doc/qianfan-api/s/wmjqtqr7w)
