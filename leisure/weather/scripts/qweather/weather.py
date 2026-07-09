#!/usr/bin/env python3
"""
和风天气查询脚本
支持城市搜索 + 实时天气查询
"""

import sys
import json
import urllib.request
import urllib.parse
import os
import time
import random

# API 配置
API_HOST = "https://nw4wcunbkc.re.qweatherapi.com"  # 用户专用 API Host

# 缓存配置
CACHE_DIR = "/tmp/qweather_cache"
CACHE_TTL = 600  # 缓存10分钟


def get_cache_key(path, params):
    """生成缓存 key"""
    import hashlib
    cache_str = f"{path}:{json.dumps(params, sort_keys=True)}"
    return hashlib.md5(cache_str.encode()).hexdigest()


def get_cached_response(cache_key):
    """获取缓存的响应"""
    try:
        import os.path
        cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
        if not os.path.exists(cache_file):
            return None
        
        # 检查是否过期
        mtime = os.path.getmtime(cache_file)
        if time.time() - mtime > CACHE_TTL:
            return None
        
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None


def set_cached_response(cache_key, data):
    """设置缓存"""
    try:
        import os
        if not os.path.exists(CACHE_DIR):
            os.makedirs(CACHE_DIR)
        
        cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f)
    except:
        pass


def qweather_request_with_retry(path, params, max_retries=3):
    """发送和风天气 API 请求（带指数退避重试）"""
    api_key = os.getenv("QWEATHER_API_KEY")
    if not api_key:
        raise Exception("QWEATHER_API_KEY environment variable not set")

    # 构建 URL（手动编码避免中文问题）
    query_parts = []
    for k, v in params.items():
        if isinstance(v, str):
            v = urllib.parse.quote(v.encode('utf-8'))
        query_parts.append(f"{k}={v}")
    query_string = "&".join(query_parts)
    url = f"{API_HOST}{path}?{query_string}"

    # 指数退避重试
    base_delay = 2  # 基础等待2秒
    for attempt in range(max_retries):
        try:
            # 使用 Header 传递 API Key（更安全）
            req = urllib.request.Request(url, headers={
                "X-QW-Api-Key": api_key
            })
            with urllib.request.urlopen(req, timeout=30) as response:
                data = response.read()
                # 和风天气默认使用 gzip 压缩
                import gzip
                data = gzip.decompress(data)
                return json.loads(data.decode("utf-8"))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            # 429 错误使用指数退避
            if e.code == 429 and attempt < max_retries - 1:
                delay = base_delay ** (attempt + 1) + random.randint(0, 2 ** (attempt + 1) - 1)
                time.sleep(delay)
                continue
            raise Exception(f"HTTP Error {e.code}: {error_body}")
        except Exception as e:
            if attempt < max_retries - 1:
                delay = base_delay ** (attempt + 1) + random.randint(0, 2 ** (attempt + 1) - 1)
                time.sleep(delay)
                continue
            raise

    raise Exception("Max retries exceeded")


def qweather_request(path, params, use_cache=True):
    """发送和风天气 API 请求（带缓存）"""
    cache_key = get_cache_key(path, params)
    
    # 尝试读取缓存
    if use_cache:
        cached = get_cached_response(cache_key)
        if cached:
            return cached
    
    # 发送请求
    result = qweather_request_with_retry(path, params)
    
    # 缓存响应
    if use_cache:
        set_cached_response(cache_key, result)
    
    return result


def search_city(location):
    """搜索城市，返回城市列表"""
    result = qweather_request("/geo/v2/city/lookup", {
        "location": location,
        "number": 5,
        "lang": "zh"
    })

    if result.get("code") != "200":
        raise Exception(f"API Error: {result.get('code')}")

    return result.get("location", [])


def get_weather_now(location_id):
    """获取实时天气"""
    result = qweather_request("/v7/weather/now", {
        "location": location_id,
        "lang": "zh"
    })

    if result.get("code") != "200":
        raise Exception(f"API Error: {result.get('code')}")

    return result.get("now", {})


def get_weather_daily(location_id, days=3):
    """获取每日天气预报（3天/7天/10天等）"""
    result = qweather_request(f"/v7/weather/{days}d", {
        "location": location_id,
        "lang": "zh"
    })

    if result.get("code") != "200":
        raise Exception(f"API Error: {result.get('code')}")

    return result.get("daily", [])


def format_weather(city_name, weather, daily=None):
    """格式化天气输出"""
    temp = weather.get("temp", "--")
    feels_like = weather.get("feelsLike", "--")
    text = weather.get("text", "--")
    wind_dir = weather.get("windDir", "--")
    wind_scale = weather.get("windScale", "--")
    humidity = weather.get("humidity", "--")
    pressure = weather.get("pressure", "--")
    vis = weather.get("vis", "--")
    obs_time = weather.get("obsTime", "--")

    lines = [
        f"🌤️ {city_name} 实时天气",
        f"",
        f"天气状况: {text}",
        f"温度: {temp}°C (体感 {feels_like}°C)",
        f"风向风力: {wind_dir} {wind_scale}级",
        f"相对湿度: {humidity}%",
        f"大气压强: {pressure}hPa",
        f"能见度: {vis}km",
        f"观测时间: {obs_time}",
    ]
    
    # 添加今日预报
    if daily and len(daily) > 0:
        today = daily[0]
        temp_max = today.get("tempMax", "--")
        temp_min = today.get("tempMin", "--")
        text_day = today.get("textDay", "--")
        text_night = today.get("textNight", "--")
        uv_index = today.get("uvIndex", "--")
        
        lines.append(f"")
        lines.append(f"📅 今日预报")
        lines.append(f"温度范围: {temp_min}°C ~ {temp_max}°C")
        lines.append(f"白天: {text_day} | 夜间: {text_night}")
        lines.append(f"紫外线指数: {uv_index}")
    
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python weather.py <城市名称>")
        print("Example: python weather.py 北京")
        print("         python weather.py 兰州")
        sys.exit(1)

    location = sys.argv[1]

    try:
        # 1. 搜索城市
        cities = search_city(location)
        if not cities:
            print(f"未找到城市: {location}")
            sys.exit(1)

        # 取第一个结果
        city = cities[0]
        city_name = city.get("name", location)
        city_id = city.get("id")
        adm1 = city.get("adm1", "")
        adm2 = city.get("adm2", "")

        # 只显示城市名，不显示完整路径
        full_name = city_name

        # 2. 获取实时天气和今日预报
        weather = get_weather_now(city_id)
        daily = get_weather_daily(city_id, days=3)

        # 3. 输出
        print(format_weather(full_name, weather, daily))

        # 4. 如果有多个结果，显示其他选项
        if len(cities) > 1:
            print(f"\n其他匹配城市:")
            for i, c in enumerate(cities[1:3], 2):
                name = c.get("name")
                adm = c.get("adm1", "")
                print(f"  {i}. {name} ({adm})")

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
