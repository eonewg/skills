---
name: qianfan-web-summary
description: 百度千帆智能搜索生成（普通版）- 基于百度搜索与AI技术，支持深度搜索、推理模式、知识注入等高级功能
metadata:
  openclaw:
    emoji: 🔍
    requires:
      bins:
        - python3
      env:
        - BAIDU_API_KEY
    primaryEnv: BAIDU_API_KEY
---

# 百度千帆智能搜索生成（普通版）

基于百度千帆平台的智能搜索生成 API（`/v2/ai_search/chat/completions`），整合百度搜索与AI技术，提供强大的搜索和智能总结能力。

## 功能特点

- **AI 总结**: 基于大模型的内容总结，免于信息筛选
- **多模态支持**: 支持网页、视频、图片搜索
- **深度搜索**: 开启后产生10次以内调用，返回更多结果
- **推理模式**: 支持 DeepSeek-R1、文心X1 等思考模型
- **知识注入**: 支持定制化知识内容注入
- **追问推荐**: 自动生成推荐追问问题
- **划词搜索**: 自动抽取实体并挂载百科词条
- **图文混排**: 支持 rich_text 输出格式
- **安全策略**: 支持标准/严格安全等级

## 使用方法

### 1. 命令行使用

```bash
# 基本搜索（必需指定 model）
python3 skills/qianfan-web-summary/scripts/summarize.py '{"query":"今天天气","model":"ernie-3.5-8k"}'

# 简化版（只返回AI总结）
python3 skills/qianfan-web-summary/scripts/summarize.py '{"query":"近日油价调整","model":"ernie-3.5-8k","simple":true}'

# 返回总结+参考链接
python3 skills/qianfan-web-summary/scripts/summarize.py '{"query":"OpenClaw","model":"ernie-3.5-8k","with_refs":true}'

# 深度搜索
python3 skills/qianfan-web-summary/scripts/summarize.py '{"query":"复杂问题","model":"ernie-3.5-8k","deep_search":true}'

# 图文混排输出（适合美食、旅游场景）
python3 skills/qianfan-web-summary/scripts/summarize.py '{"query":"北京烤鸭","model":"ernie-4.5-turbo-32k","rich_text":true}'
```

### 2. Python SDK 使用

```python
from skills.qianfan_web_summary.scripts.summarize import QianfanWebSummary

# 初始化
search = QianfanWebSummary()  # 从环境变量读取 API Key

# 基本搜索（必需指定 model）
result = search.search("今天天气", model="ernie-3.5-8k")
print(result["choices"][0]["message"]["content"])

# 简化版搜索
summary = search.search_simple("近日油价调整", model="ernie-3.5-8k", top_k=5)
print(summary)

# 深度搜索
result = search.search_with_deep_search("复杂问题", model="ernie-3.5-8k", top_k=20)

# 图文混排输出（适合美食、旅游、百科）
result = search.search_with_rich_text("北京烤鸭", model="ernie-4.5-turbo-32k")

# 多模态搜索
result = search.search_multimodal(
    query="猫咪视频",
    model="ernie-3.5-8k",
    web_count=10,
    video_count=5,
    image_count=5
)

# 高级配置
result = search.search(
    query="最新新闻",
    model="deepseek-r1-250528",
    search_source="baidu_search_v2",
    enable_deep_search=True,
    enable_reasoning=True,
    enable_followup_queries=True,
    instruction="请用简洁的语言总结",
    temperature=0.7,
    response_format="rich_text"
)
```

## API 参数说明

### 必需参数

| 参数 | 类型 | 说明 |
|------|------|------|
| query | str | 搜索查询词 |
| model | str | 模型名称（如 ernie-3.5-8k） |

### 可选参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| search_source | str | baidu_search_v2 | 搜索引擎版本：v1/v2 |
| resource_filters | List | web:10 | 资源类型过滤器 |
| search_recency_filter | str | - | 时间过滤：week/month/semiyear/year |
| search_filter | SearchFilter | - | 站点/时间范围过滤 |
| instruction | str | - | 人设指令（最长4000字符） |
| temperature | float | - | 采样参数，范围(0, 1] |
| top_p | float | - | 采样参数，范围(0, 1] |
| prompt_template | str | - | 自定义prompt模板 |
| search_mode | str | auto | 搜索模式：auto/required/disabled |
| enable_reasoning | bool | true | 是否开启深度思考 |
| enable_deep_search | bool | false | 是否开启深度搜索 |
| max_search_query_num | int | 10 | 深搜索最大子query数 |
| additional_knowledge | List | - | 定制化知识（最多10条） |
| safety_level | str | standard | 安全等级：standard/strict |
| enable_web_page_safety | bool | true | 是否开启网页安全检查 |
| max_completion_tokens | int | 2048 | 最大输出token数 |
| response_format | str | text | 输出格式：text/rich_text |
| enable_corner_markers | bool | true | 是否返回角标 |
| enable_followup_queries | bool | false | 是否开启追问推荐 |
| enable_entity_selection_search | bool | false | 是否开启划词搜索 |

### 支持的模型

- `ernie-3.5-8k`（默认推荐）
- `ernie-4.5-turbo-32k`
- `ernie-4.5-turbo-128k`
- `deepseek-v3`
- `deepseek-r1-250528`
- `deepseek-v3.1-250821`
- `deepseek-v3.1-think-250821`
- `qwen3-235b-a22b-instruct-2507`
- `qwen3-235b-a22b-thinking-2507`

### 资源类型限制

| 类型 | V1 最大 | V2 最大 | 说明 |
|------|---------|---------|------|
| web | 10 | 20 | 网页搜索 |
| video | 10 | 10 | 视频搜索 |
| image | 10 | - | 图片搜索（仅V1） |

## 返回结果格式

```json
{
  "request_id": "xxx",
  "choices": [{
    "finish_reason": "stop",
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "AI总结的内容...",
      "reasoning_content": "推理过程（思考模型）"
    }
  }],
  "references": [...],
  "followup_queries": ["追问1", "追问2"],
  "entities": [...],
  "is_safe": true,
  "usage": {
    "prompt_tokens": 1919,
    "completion_tokens": 295,
    "total_tokens": 2214
  }
}
```

## 环境配置

```bash
export BAIDU_API_KEY=<redacted>
```

## 计费说明

- 每日免费额度：100次
- 深度搜索会产生10次以内调用
- 具体费率请参考百度千帆官方文档

## 与 Pro 版的区别

| 特性 | 普通版 (chat/completions) | Pro 版 (web_summary) |
|------|---------------------------|----------------------|
| **模型选择** | ✅ **必需**，支持多种模型 | ❌ 内置模型 |
| **深度搜索** | ✅ 支持 | ❌ |
| **推理模式** | ✅ 支持 | ✅ 通过 model 参数 |
| **知识注入** | ✅ 支持 | ❌ |
| **追问推荐** | ✅ 支持 | ❌ |
| **划词搜索** | ✅ 支持 | ❌ |
| **图文混排** | ✅ 支持 | ❌ |
| **使用复杂度** | 功能丰富，配置灵活 | 简单直接 |
| **适用场景** | 需要高级功能 | 快速获取AI总结 |

## 相关链接

- [百度千帆官方文档](https://console.bce.baidu.com/qianfan/tools/toolsCenter/baidu_ai_search/detail)
