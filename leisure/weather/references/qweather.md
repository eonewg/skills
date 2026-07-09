---
name: qweather
description: Get weather using QWeather (和风天气) API. Supports city search and real-time weather data.
metadata: {"openclaw":{"emoji":"🌤️","requires":{"bins":["python3"],"env":["QWEATHER_API_KEY"]},"primaryEnv":"QWEATHER_API_KEY"}}
---

# QWeather 和风天气

和风天气 API，支持城市搜索和实时天气查询。

## Usage

```bash
# 查询城市天气
python3 skills/qweather/scripts/weather.py <城市名称>

# 示例
python3 skills/qweather/scripts/weather.py 北京
python3 skills/qweather/scripts/weather.py 兰州
python3 skills/qweather/scripts/weather.py 榆中
```

## Environment

- `QWEATHER_API_KEY` - 和风天气 API Key (必填)

## Features

- 城市模糊搜索（支持中文）
- 实时天气数据：温度、体感温度、天气状况、风向风力、湿度、气压、能见度
- 多结果提示（当有重名城市时）

## API Limits

- 免费版：1000 次/天
- 实时天气 + 城市搜索各算一次请求
