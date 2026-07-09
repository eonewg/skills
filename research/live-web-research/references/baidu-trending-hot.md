---
name: baidu-trending-hot
description: 百度热榜榜单查询工具，支持查询微博、头条、知乎、抖音、B站、百度、贴吧、快手、小红书等平台热榜数据
homepage: https://cloud.baidu.com/doc/qianfan/s/Amhcvzqs0
metadata: { "openclaw": { "emoji": "📈", "requires": { "bins": ["python3"], "env": ["BAIDU_API_KEY"] }, "primaryEnv": "BAIDU_API_KEY" } }
---

# 百度热榜榜单查询

查询微博、头条、知乎、抖音、B站、百度、贴吧、快手、小红书等平台的热榜数据。

## 功能特点

- 支持9大平台：微博、头条、知乎、抖音、B站、百度、贴吧、快手、小红书
- 实时热榜数据
- 包含热度值、标题、链接

## 使用方法

### 命令行

```bash
# 查询抖音热榜
python3 scripts/trending_hot.py --platform douyin

# 查询微博热榜，显示前10条
python3 scripts/trending_hot.py --platform weibo --limit 10

# 查询知乎热榜
python3 scripts/trending_hot.py --platform zhihu

# 使用类型码查询
python3 scripts/trending_hot.py --type 6

# 输出原始 JSON
python3 scripts/trending_hot.py --platform douyin --json

# 列出支持的平台
python3 scripts/trending_hot.py --list
```

### 参数说明

| 参数 | 简写 | 必填 | 可选值 | 说明 |
|------|------|------|--------|------|
| `--platform` | `-p` | 否 | weibo/toutiao/zhihu/douyin/bilibili/baidu/tieba/kuaishou/xiaohongshu | 平台名称 |
| `--type` | `-t` | 否 | 2/3/4/6/7/8/9/10/14 | 热榜类型码 |
| `--limit` | `-l` | 否 | 数字 | 显示条数 (默认: 20) |
| `--json` | `-j` | 否 | - | 输出 JSON 格式 |
| `--list` | | 否 | - | 列出支持的平台 |

### 平台类型码对照表

| 类型码 | 平台 |
|--------|------|
| 2 | 微博热榜 |
| 3 | 头条热榜 |
| 4 | 百度热榜 |
| 6 | 抖音热榜 |
| 7 | 知乎热榜 |
| 8 | B站热榜 |
| 9 | 贴吧热议榜 |
| 10 | 快手热榜 |
| 14 | 小红书热榜 |

## 配置

```bash
export BAIDU_API_KEY="your_api_key"
```

或在 `openclaw.json` 中配置：

```json
{
  "skills": {
    "entries": {
      "baidu-trending-hot": {
        "env": {
          "BAIDU_API_KEY": "your_api_key"
        }
      }
    }
  }
}
```

## 返回数据字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `title` | string | 热榜标题 |
| `hot` | int | 热度值 |
| `url` | string | 内容链接 |
| `date` | string | 日期 |
| `translateTitle` | string | 翻译标题 |

## API 文档

- 官方文档: https://cloud.baidu.com/doc/qianfan/s/Amhcvzqs0
- 接口地址: `GET https://qianfan.baidubce.com/v2/tools/trending_lists/medium?type={type}`

## 计费说明

该组件为付费功能，具体计费请参考[官方文档](https://cloud.baidu.com/doc/qianfan/s/Umh4sv6gb)。
