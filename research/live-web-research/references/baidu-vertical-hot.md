---
name: baidu-vertical-hot
description: 百度垂类热榜查询工具，支持查询抖音、小红书等平台的美食、美妆、汽车类热榜数据
homepage: https://cloud.baidu.com/doc/qianfan/s/Lmhcvvxb2
metadata: { "openclaw": { "emoji": "🔥", "requires": { "bins": ["python3"], "env": ["BAIDU_API_KEY"] }, "primaryEnv": "BAIDU_API_KEY" } }
---

# 百度垂类热榜查询

查询抖音、小红书等平台的美食、美妆、汽车类热榜数据。

## 功能特点

- 支持多平台：抖音、小红书
- 支持多垂类：美食、美妆、汽车
- 支持多时间范围：近1天、近3天、近7天
- 返回热度值、点赞量、浏览量等详细数据

## 使用方法

### 命令行

```bash
# 查询抖音美食类近一天热榜
python3 scripts/vertical_hot.py --category 美食 --platform 抖音 --time 1

# 查询小红书美妆类近7天热榜
python3 scripts/vertical_hot.py --category 美妆 --platform 小红书 --time 7

# 查询汽车类热榜，显示前5条
python3 scripts/vertical_hot.py --category 汽车 --platform 抖音 --limit 5

# 输出原始 JSON
python3 scripts/vertical_hot.py --category 美食 --platform 抖音 --json
```

### 参数说明

| 参数 | 简写 | 必填 | 可选值 | 说明 |
|------|------|------|--------|------|
| `--category` | `-c` | 是 | 美食/美妆/汽车 | 垂类类型 |
| `--platform` | `-p` | 是 | 抖音/小红书 | 媒体平台 |
| `--time` | `-t` | 否 | 1/3/7 | 时间范围 (默认: 1) |
| `--limit` | `-l` | 否 | 数字 | 显示条数 (默认: 10) |
| `--json` | `-j` | 否 | - | 输出 JSON 格式 |

## 配置

```bash
export BAIDU_API_KEY="your_api_key"
```

或在 `openclaw.json` 中配置：

```json
{
  "skills": {
    "entries": {
      "baidu-vertical-hot": {
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
| `title` | String | 视频标题 |
| `hotNum` | String | 热度值 |
| `likeCount` | Long | 点赞量 |
| `collectedCount` | Long | 收藏量 |
| `commentsCount` | Long | 评论量 |
| `sharedCount` | Long | 分享量 |
| `readCount` | Long | 浏览量 |
| `url` | String | 视频链接 |
| `thumbnail` | String | 缩略图链接 |
| `businessTime` | String | 发布时间 |

## API 文档

- 官方文档: https://cloud.baidu.com/doc/qianfan/s/Lmhcvvxb2
- 接口地址: `POST https://qianfan.baidubce.com/v2/tools/trending_lists/vertical`

## 计费说明

该组件为付费功能，具体计费请参考[官方文档](https://cloud.baidu.com/doc/qianfan/s/Umh4sv6gb)。
