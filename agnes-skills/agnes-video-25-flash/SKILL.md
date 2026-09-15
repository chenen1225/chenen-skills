---
name: agnes-video-25-flash
description: "【Agnes AI 视频生成技能 · agnes-video-25-flash】调用 Agnes Video 2.5 Flash 模型，通过 OpenAI Videos 兼容异步 API 生成视频。支持三种模式：text（纯文生视频）、keyframe（首尾帧控制）、reference（图片/音频参考生成）。固定 720P，时长 4–12 秒，支持 16:9/9:16/1:1 等画幅。触发词：agnes 生视频、agnes-video-2.5、用 agnes 做视频、文生视频、首尾帧、图生视频、把图片做成视频、生成短视频。"
version: 1.0.0
metadata:
  homepage: https://agnes-ai.com/zh-Hans/docs/agnes-video-25-flash
  requires:
    anyBins:
      - python3
      - python
---

# Agnes Video 2.5 Flash 技能

OpenAI Videos 兼容 API 的异步视频生成。**创建任务 → 用 `video_id` 轮询 → 从顶层 `url` 下载视频**。

> ⚠️ 这是**新一套 API**，与旧的 `agnes-video-v2.0`（`agnes-video-v20` 技能）**完全不同**：没有 `num_frames`/`frame_rate`/`width`/`height`，改用 `mode` + `seconds` + `size:"720P"` + `aspect_ratio`。旧参数传进来会直接 400。

## 🚨 必须牢记的坑

1. **模型 ID：`agnes-video-2.5-flash`**（带小数点）。
2. **🔴 最终视频地址在顶层 `url`**！不是 `metadata.url`（2.5 的查询响应里根本没有 `metadata` 字段），更不是 `remixed_from_video_id`（恒为 null）。只有当 `status == "completed"` 时 `url` 才可交付。脚本已两种都兜底尝试。
3. **`size` 固定字符串 `"720P"`**，其他任何值 → HTTP 400 `size must be 720P`。别写成 `1280x720`。
4. **`seconds` 是字符串** `"4"`–`"12"`（默认 `"5"`），不是数字。
5. **轮询必须带 `model_name`**：`keyframe` 和 `reference` 模式的查询 URL 必须加 `&model_name=agnes-video-2.5-flash`，否则可能资源识别错误；不带 `model_name` 的纯 `video_id` 查询**仅适用于 `text` 模式**。本脚本一律带上。
6. **Flash 专属上限**：`images` ≤ 5 张、`audios` ≤ 3 段、`videos` 不支持（传了 400）。
7. **模式与媒体字段必须匹配**（见下表），不匹配会 400。
8. **不要传** `width`/`height`/`fps`/`num_frames`/`quality`/`num_inference_steps`，会 400。
9. **轮询间隔 1–2 秒**，并对 429/网络超时做退避重试。
10. API Key 用环境变量 `AGNES_API_KEY`，不要写死、不要进日志/前端/公开仓库。

## API 信息

- 创建：`POST https://apihub.agnes-ai.com/v1/videos`
- 查询：`GET https://apihub.agnes-ai.com/agnesapi?video_id=<VIDEO_ID>&model_name=agnes-video-2.5-flash`
- 认证：`Authorization: Bearer $AGNES_API_KEY`

## 三种模式

| mode | 用途 | 必需媒体 | 禁止的字段 |
|---|---|---|---|
| `text` | 纯文本生成 | 无 | `first_frame`、`last_frame`、`images`、`audios`、`videos` |
| `keyframe` | 首帧/尾帧/首尾帧控制 | `first_frame` 与 `last_frame` 至少一个 | `images`、`audios`、`videos` |
| `reference` | 图片或音频参考生成 | `images` 或 `audios` 至少一类非空 | `first_frame`、`last_frame`、`videos` |

`reference` 模式可在 prompt 中用 `<Picture N>` / `<Audio N>` 指代素材。

## 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `model` | string | 是 | `agnes-video-2.5-flash` |
| `prompt` | string | 是 | 视频内容描述 |
| `mode` | string | 是 | `text` / `keyframe` / `reference` |
| `seconds` | string | 否 | `"4"`–`"12"`，默认 `"5"` |
| `size` | string | 否 | Flash 固定 `"720P"` |
| `aspect_ratio` | string | 否 | 默认 `16:9`，见下表 |
| `seed` | integer | 否 | 随机种子 |
| `n` | integer | 否 | 仅支持 `1` |
| `first_frame` / `last_frame` | string | keyframe | 首尾帧图片 URL |
| `images` | string[] | reference | 参考图 ≤5 张 |
| `audios` | string[] | reference | 参考音频 ≤3 段 |

### 画幅 → 输出像素

| aspect_ratio | 输出 |
|---|---|
| 21:9 | 1680×720 |
| 16:9 | 1280×704 |
| 4:3 | 960×720 |
| 1:1 | 720×720 |
| 3:4 | 720×960 |
| 9:16 | 720×1280 |

## 调用方式（推荐用脚本）

自带 `scripts/generate_video.py`，仅用 Python 标准库。脚本会在**发送前**本地校验 Flash 规则（size/图片数/音频数/模式匹配），省掉 400 往返。

```bash
# 文生视频（默认 text 模式 / 5 秒 / 720P / 16:9）
python "$SKILL_DIR/scripts/generate_video.py" \
  --prompt "雨后的未来城市街道，霓虹倒映地面，银色跑车缓慢驶过，电影级运镜" \
  --seconds 5 --output city.mp4

# 竖屏短视频
... --prompt "..." --seconds 8 --aspect-ratio 9:16 --output reels.mp4

# 首尾帧控制
python "$SKILL_DIR/scripts/generate_video.py" \
  --mode keyframe \
  --prompt "人物从首帧姿态自然转身走向窗边，镜头缓慢推进" \
  --first-frame https://ex.com/first.png --last-frame https://ex.com/last.png \
  --seconds 5 --output kf.mp4

# 图片参考生成
python "$SKILL_DIR/scripts/generate_video.py" \
  --mode reference \
  --prompt "以 <Picture 1> 中的角色和美术风格为参考，角色在花田中奔跑，保持外观一致" \
  --images https://ex.com/character.png --seconds 5 --output ref.mp4
```

参数：`--prompt`、`--mode`（默认 `text`）、`--seconds`、`--size`（默认 `720P`）、`--aspect-ratio`、`--first-frame`、`--last-frame`、`--images`（可多张，≤5）、`--audios`（≤3）、`--seed`、`--output`、`--api-key`、`--interval`（默认 2 秒）、`--max-wait`。

> 本地图片文件会自动转成 Data URI；但官方文档要求媒体可被 Agnes 服务公开访问，**公网 HTTPS URL 更可靠**（Data URI 是从旧版 v2.0 沿用下来的经验，2.5 未明确承诺支持）。

## 直接 curl（对照参考）

```bash
export AGNES_API_KEY="YOUR_API_KEY"
export AGNES_BASE_URL="https://apihub.agnes-ai.com/v1"

curl -sS -X POST "$AGNES_BASE_URL/videos" \
  -H "Authorization: Bearer $AGNES_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"agnes-video-2.5-flash","prompt":"夜晚森林中三只猫组成微型铜管乐队向前行进","seconds":"5","mode":"text","size":"720P","aspect_ratio":"16:9"}'

curl -sS "https://apihub.agnes-ai.com/agnesapi?video_id=VIDEO_ID&model_name=agnes-video-2.5-flash" \
  -H "Authorization: Bearer $AGNES_API_KEY"
```

## 响应字段

创建：`{"id":"task_..","task_id":"task_..","video_id":"video_..","object":"video","model":"agnes-video-2.5-flash","status":"queued","progress":0,"created_at":..,"seconds":"5","size":"720P"}`

查询完成（实测真实结构，地址在顶层 `url`）：
```json
{"id":"task_..","object":"video","status":"completed","progress":100,"seconds":"4","size":"720P","url":"https://platform-outputs.agnes-ai.space/videos/agnes-video-2.5/task_..mp4","remixed_from_video_id":null,"completed_at":..,"started_at":..}
```
取 **`url`** 下载（`metadata` 字段在本接口响应中不存在，`remixed_from_video_id` 恒为 null）。

失败：`{"status":"failed","error":{"message":"Invalid reference media"}}`

`status` 取值：`queued` / `in_progress` / `completed` / `failed`。

## 错误码

| 码 | 原因 | 处理 |
|---|---|---|
| 400 | 参数缺失、模式与媒体不匹配、时长/画幅非法、size 非 720P | 按返回 `detail` 修正 |
| 401/403 | Key 无效/过期/无权限 | 换 key |
| 404 | video_id 不存在 | 用创建响应里的 `video_id` |
| 429 | 频率超限 | 指数退避，降低轮询频率 |
| 500 | 服务端错误 | 稍后重试 |

多个 Flash 参数错误时，按 `size` → `images` → `audios` → `videos` 顺序返回首个错误。

## 价格

720P `$0.025 / 秒`，**当前限时 `$0 / 秒`（免费）**。

## 接入检查清单

- [x] 模型 ID 用 `agnes-video-2.5-flash`
- [x] `size` 固定 `"720P"`
- [x] `reference` 模式 `images` ≤5、`audios` ≤3，不传 `videos`
- [x] `seconds` 用字符串 `"4"`–`"12"`，`n` 固定 1
- [x] 查询带 `model_name=agnes-video-2.5-flash`
- [x] 从顶层 `url` 取视频（`metadata` 字段不存在，`remixed_from_video_id` 恒为 null）
