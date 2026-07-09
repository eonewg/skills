---
name: baidu-search-router
description: 百度搜索智能调度器 - 自动根据查询类型选择最合适的百度系搜索 skill
metadata:
  openclaw:
    emoji: 🎯
    requires:
      bins:
        - python3
      env:
        - BAIDU_API_KEY
    primaryEnv: BAIDU_API_KEY
---

# 百度搜索智能调度器

自动根据查询内容选择最合适的百度系搜索 skill，无需手动选择。

## 支持的 Skill

| Skill | 触发条件 | 说明 |
|-------|----------|------|
| **baike** | 名词/概念/人物/地点查询 | "OpenClaw是什么"、"谁是爱因斯坦" |
| **scholar** | 学术/论文查询 | "Transformer论文"、"深度学习综述" |
| **trending** | 热点/热搜查询 | "今天热搜"、"微博热榜" |
| **vertical** | 垂直领域热点 | "美食推荐"、"美妆热榜" |
| **web_search** | 原始搜索需求 | "原始结果"、"不要总结"、或 `--raw` 参数 |
| **web_summary** | 通用搜索（默认） | 复杂问题，需要深度功能 |
| **web_summary_pro** | 简单快速查询 | "今天天气"、"现在几点" |
| **ppt** | PPT生成 | "做个AI介绍的PPT" |
| **video_notes** | 视频笔记 | "整理这个视频" |

## 使用方法

### 1. 直接搜索（自动路由）

```bash
# 自动选择最合适的 skill
python3 skills/baidu-search-router/scripts/router.py "今天天气"
# → 路由到: web_summary_pro (简单查询)

python3 skills/baidu-search-router/scripts/router.py "OpenClaw是什么"
# → 路由到: baike (百科查询)

python3 skills/baidu-search-router/scripts/router.py "Transformer论文"
# → 路由到: scholar (学术查询)

python3 skills/baidu-search-router/scripts/router.py "今天微博热搜"
# → 路由到: trending (热榜查询)

python3 skills/baidu-search-router/scripts/router.py "2025年AI发展趋势"
# → 路由到: web_summary (通用搜索，启用深度功能)

# 强制使用原始搜索（baidu-search）
python3 skills/baidu-search-router/scripts/router.py "OpenClaw" --raw
# → 路由到: web_search (原始搜索结果)
```

### 2. 预览路由决策

```bash
# 只看会路由到哪个 skill，不实际执行
python3 skills/baidu-search-router/scripts/router.py "今天天气" --preview
```

输出示例：
```json
{
  "query": "今天天气",
  "will_route_to": "智能搜索高性能版 (qianfan-web-summary-pro)",
  "skill_type": "web_summary_pro",
  "confidence": 0.7,
  "reason": "简单查询，使用高性能版"
}
```

### 3. 强制使用特定功能

```bash
# 启用深度搜索
python3 skills/baidu-search-router/scripts/router.py "AI发展趋势" --deep

# 使用简化输出
python3 skills/baidu-search-router/scripts/router.py "今天新闻" --simple

# 强制使用原始搜索
python3 skills/baidu-search-router/scripts/router.py "OpenClaw" --raw
```

### 4. Python SDK 使用

```python
from skills.baidu_search_router.scripts.router import SearchRouter

router = SearchRouter()

# 自动路由并执行
result = router.route("今天天气")
print(result["routed_to"])  # 实际使用的 skill
print(result["output"])     # 搜索结果

# 预览路由决策
preview = router.preview("OpenClaw是什么")
print(preview["will_route_to"])  # 百度百科 (baidu-baike-data)
print(preview["reason"])         # 检测到百科查询需求

# 带参数路由
result = router.route(
    "AI发展趋势",
    deep_search=True,    # 启用深度搜索
    model="deepseek-r1-250528"  # 指定模型
)
```

## 路由规则

### 优先级（从高到低）

1. **视频笔记** - 包含"视频笔记"、"整理视频"等
2. **PPT生成** - 包含"生成PPT"、"做幻灯片"等
3. **百度百科** - 包含"是什么"、"是谁"、"介绍"等
4. **百度学术** - 包含"论文"、"文献"、"学术"等
5. **热榜** - 包含"热搜"、"热榜"、"热点"等
6. **垂直热榜** - 美食/美妆/汽车 + 热榜
7. **高性能版** - 简单查询（天气、时间等）
8. **普通版** - 默认，通用搜索

### 置信度说明

- `0.9` - 非常确定（视频、PPT、明确的百科/学术）
- `0.85` - 高置信（百科、学术关键词匹配）
- `0.8` - 中等置信（热榜、垂直领域）
- `0.7` - 低置信（简单查询判断）
- `0.6` - 默认（通用搜索）

## 返回格式

```json
{
  "query": "原始查询",
  "routed_to": "实际使用的 skill 类型",
  "confidence": 0.85,
  "reason": "路由原因说明",
  "output": "搜索结果",
  "error": null
}
```

## 环境配置

```bash
export BAIDU_API_KEY=<redacted>
```

## 使用建议

### 什么时候用这个？

- ✅ 不确定该用哪个 skill
- ✅ 希望自动化选择
- ✅ 批量处理不同类型的查询
- ✅ 构建智能助手

### 什么时候直接调用具体 skill？

- ✅ 明确知道需要什么功能
- ✅ 需要精细控制参数
- ✅ 性能敏感（路由有轻微开销）

## 扩展

如需添加新的路由规则，编辑 `router.py` 中的 pattern 列表：

```python
# 添加新的匹配模式
NEW_PATTERNS = [
    r"你的匹配正则",
]
```
