# agnes-skills

Agnes AI（[agnes-ai.com](https://agnes-ai.com)）生图 / 生视频技能的合集，封装为 WorkBuddy Skill。

> API Key 通过环境变量 `AGNES_API_KEY` 提供，或在调用脚本时传 `--api-key`。
> **切勿把真实 key 写进任何技能文件**——`config.json` 已被 `.gitignore` 忽略。

## 技能清单

| 技能 | 模型 | 能力 |
|---|---|---|
| `agnes-image-21-flash` | `agnes-image-2.1-flash` | 文生图 / 图生图 |
| `agnes-image-25-flash` | `agnes-image-2.5-flash` | 文生图 / 图生图 / 多图合成（size 档位 1K–4K + ratio） |
| `agnes-video-v20` | `agnes-video-v2.0` | 文生视频 / 图生视频 / 多图 / 关键帧（旧版异步 API） |
| `agnes-video-25-flash` | `agnes-video-2.5-flash` | 文生视频 / 首尾帧 / 参考图·音频（OpenAI Videos 兼容异步 API） |

## 用法

每个技能自带 `scripts/` 下的 Python 脚本（仅用标准库，无需 `pip install`）。

```bash
# 文生图
python agnes-image-25-flash/scripts/generate_image.py \
  --prompt "一位优雅的东方少女，淡青色汉服，江南水乡，柔和晨光" \
  --size 1K --ratio 3:4 --output girl.png

# 文生视频（2.5 Flash）
python agnes-video-25-flash/scripts/generate_video.py \
  --prompt "雨后的未来城市街道，霓虹倒映地面，电影级运镜" \
  --mode text --seconds 5 --aspect-ratio 16:9 --output city.mp4
```

## 踩坑提醒（来自真实调试）

- **视频地址字段**：2.0 / 2.5 的视频最终地址都在顶层 `url` 字段；`remixed_from_video_id` 恒为 `null`，文档里写的 `metadata.url` 在真实接口里并不存在。
- **模型名带小数点**：`agnes-image-2.1-flash` / `agnes-image-2.5-flash` / `agnes-video-v2.0` / `agnes-video-2.5-flash`，拼错直接报错。
- **2.5 视频 API 与 2.0 完全不同**：用 `mode` + `seconds`(字符串 "4"–"12") + `size:"720P"` + `aspect_ratio`；没有 `num_frames`/`frame_rate`，旧参数传进去会 400。
- 异步轮询时查询 URL 带 `model_name=agnes-video-2.5-flash`；对 429 / SSL-EOF 做退避重试。
