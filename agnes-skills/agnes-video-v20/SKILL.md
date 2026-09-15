---
name: agnes-video-v20
description: "【Agnes AI 视频生成技能 · agnes-video-v20】调用 Sapiens AI 的 Agnes-Video-V2.0 模型，通过 Agnes API Gateway 生成视频。支持文生视频、图生视频、多图视频、关键帧动画四类工作流；异步任务式 API（先创建任务再用 video_id 轮询）。触发词：agnes 生视频、agnes-video、用 agnes 做视频、Agnes Video V2.0、把图片做成视频、关键帧动画、图生视频。"
version: 1.0.0
metadata:
  homepage: https://agnes-ai.com/doc/agnes-video-v20
  requires:
    anyBins:
      - python3
      - python
---

# Agnes-Video-V2.0 技能

调用 Agnes-Video-V2.0 生成视频。异步任务式 API：**先创建任务 → 用 `video_id` 轮询 → 下载视频**。

## 🚨 血泪踩坑（来自实测，务必遵守）

1. **模型名称带小数点：`agnes-video-v2.0`**（不是 `agnes-video-v20`）。拼错直接报错。
2. **🔴 视频地址在 `url` 字段，不是 `remixed_from_video_id`！** 官方文档里 `remixed_from_video_id` 实测**恒为 null**，所有脚本若读这个字段永远拿不到视频。完成时取 `result["url"]` 才是真实 mp4 地址。
3. **队列满 503 `video_queue_full`**：退避重试即可，别当成失败。
4. **轮询时偶发 SSL 错误 `UNEXPECTED_EOF_WHILE_READING`**：瞬时错误，重试即可。
5. **本地图片不能传路径**，必须转成 base64 Data URI 再放入 `image` / `extra_body.image`。
6. **任务状态还有 `pending`（排队中）阶段**，不等于失败；继续轮询。
7. **尺寸会被自动映射**：请求 `1152x768` 可能被映射成 `1088x832`（720p/4:3）。以返回结果的 `size` 字段为准，不要强依赖请求尺寸。
8. **`num_frames` 必须 ≤ 441 且满足 `8n+1`**（如 81/121/161/241/441）。
9. API Key 用环境变量 `AGNES_API_KEY`，不要写死。

## API 信息

- Base URL：`https://apihub.agnes-ai.com`
- 创建任务：`POST https://apihub.agnes-ai.com/v1/videos`
- 查询（推荐）：`GET https://apihub.agnes-ai.com/agnesapi?video_id=<VIDEO_ID>`
- 查询（兼容旧版）：`GET https://apihub.agnes-ai.com/v1/videos/{task_id}`
- 认证：`Authorization: Bearer $AGNES_API_KEY`
- 模型名：`agnes-video-v2.0`

## 何时用本技能

- "用 agnes / agnes-video 帮我做个视频" → 文生视频。
- "把这张图做成视频/动起来" + 给图 → 图生视频。
- "用多张图生成视频 / 关键帧动画" → 多图视频 / keyframes。

## 调用方式（推荐用脚本）

自带 `scripts/generate_video.py`，仅用 Python 标准库，含重试/轮询/下载，**已修复 `url` 字段问题**。

```bash
# 文生视频（约 3 秒：81 帧 @ 24fps）
python "$SKILL_DIR/scripts/generate_video.py" \
  --prompt "一只橘猫在沙滩上奔跑，夕阳，电影感，真实运动" \
  --num-frames 81 --frame-rate 24 --output cat_run.mp4

# 图生视频（本地图会自动转 base64 Data URI）
python "$SKILL_DIR/scripts/generate_video.py" \
  --prompt "小猫用爪子拍打球，眼睛跟随弹跳的球，尾巴兴奋摇摆" \
  --image cute_orange_cat.jpg --num-frames 81 --output cat_play.mp4

# 多图视频
python "$SKILL_DIR/scripts/generate_video.py" \
  --prompt "在两张参考图之间平滑过渡" \
  --images https://ex.com/a.png https://ex.com/b.png

# 关键帧动画
python "$SKILL_DIR/scripts/generate_video.py" \
  --prompt "在关键帧之间平滑转场，保持角色一致" \
  --images k1.png k2.png --mode keyframes
```

参数：
- `--prompt`（必填）、`--image`（单图 URL/本地路径）、`--images`（多图 URL 列表）
- `--mode`（如 `keyframes`）、`--width/--height`、`--num-frames`、`--frame-rate`、`--seed`、`--negative-prompt`
- `--output`（默认 `agnes_video.mp4`）、`--api-key`（可选，默认读 `AGNES_API_KEY`）
- `--interval`（轮询间隔秒，默认 5）、`--max-wait`（最长等待秒，默认 1800）

> 视频生成通常 1–5 分钟，脚本会每 `--interval` 秒轮询直到 `completed` 或 `failed`。

## 直接 curl（对照参考）

创建（文生视频）：
```bash
curl -X POST https://apihub.agnes-ai.com/v1/videos \
  -H "Authorization: Bearer $AGNES_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"agnes-video-v2.0","prompt":"A cat walking on the beach at sunset, cinematic","height":768,"width":1152,"num_frames":121,"frame_rate":24}'
```
返回含 `task_id` 与 `video_id`（推荐用 `video_id` 查询）。

轮询（推荐）：
```bash
curl "https://apihub.agnes-ai.com/agnesapi?video_id=<VIDEO_ID>" \
  -H "Authorization: Bearer $AGNES_API_KEY"
```
`status` 为 `completed` 时，取 **`url`** 字段下载视频。

## 请求参数（创建任务）

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| model | string | 是 | `agnes-video-v2.0` |
| prompt | string | 是 | 视频文本描述 |
| image | string/array | 否 | 单图 URL（图生视频）；多图用 `extra_body.image` |
| mode | string | 否 | 如 `ti2vid`、`keyframes` |
| height | int | 否 | 默认 768 |
| width | int | 否 | 默认 1152 |
| num_frames | int | 否 | ≤441，需满足 8n+1 |
| frame_rate | number | 否 | 1–60 |
| seed | int | 否 | 复现结果 |
| negative_prompt | string | 否 | 负向提示词 |
| extra_body.image | array | 否 | 多图/关键帧输入图片 URL |
| extra_body.mode | string | 否 | 关键帧模式设 `keyframes` |

## 常用时长参数

| 时长 | num_frames | frame_rate |
| --- | --- | --- |
| ~3s | 81 | 24 |
| ~5s | 121 | 24 |
| ~10s | 241 | 24 |
| ~18s | 441 | 24 |

## Prompt 最佳实践

- 文生视频：`[主体]+[动作]+[场景]+[镜头运动]+[光照]+[风格]`
- 图生视频：说明"要运动什么" + "要保持什么"（角色/构图一致）
- 多图/关键帧：描述图片间关系与过渡方式

## 价格

视频时长 $0.005 / 秒（当前活动价 $0 / 秒）。
