# 抖音解析工具候选

## 首选接入方向

`jiji262/douyin-downloader`：适合作为 Hermes `douyin-note` 的长期下载/采集底座。它支持单个视频、图文作品、合集、用户主页、评论、直播、Cookie、浏览器 fallback、REST API 和 SQLite 去重。接入前先做安全审查，不要直接在主 Hermes 环境里运行未审查脚本。

## 重型 API 服务

`Evil0ctal/Douyin_TikTok_Download_API`：功能很全，适合自托管 FastAPI 服务。缺点是部署和配置较重，且通常需要配置浏览器 Cookie 来应对抖音风控。

## 底层库研究

`Johnserf-Seed/f2`：适合研究抖音 A-Bogus/X-Bogus、作品、主页、收藏、直播、弹幕等接口。适合作长期封装，不适合作第一次最小落地。

## 文案提取参考

`yzfly/douyin-mcp-server`：很贴近“下载视频、抽音频、SenseVoice 转写、输出 Markdown”，但仓库已归档。适合作参考，不建议直接长期依赖。

## 轻量候选

`moehans-official/DouyinSolver`：API 简单，但仓库很新，活跃度和可靠性未知。只作为实验候选。

## yt-dlp 位置

`yt-dlp` 可做第一尝试和兜底，但抖音 extractor 经常受 Cookie、页面结构和接口变化影响。它失败时不要判定“链接不可用”，要改走浏览器 Cookie、本地文件或专用抖音工具。
