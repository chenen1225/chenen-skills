---
name: agnes-image-21-flash
description: "【Agnes AI 文生图 / 图生图技能 · agnes-image-21-flash】调用 Sapiens AI 的 Agnes Image 2.1 Flash 模型，通过 Agnes API Gateway (apihub.agnes-ai.com) 生成图片。支持文生图（URL / Base64 输出）与图生图（URL 或 Data URI 输入、URL / Base64 输出），针对高信息密度图像优化。触发词：agnes 生图、agnes-image、用 agnes 画一张、Agnes Image 2.1 Flash、帮我生成一张图片、图生图、图片风格转换。"
version: 1.0.0
metadata:
  homepage: https://agnes-ai.com/doc/agnes-image-21-flash
  requires:
    anyBins:
      - python3
      - python
---

# Agnes Image 2.1 Flash 技能

调用 Agnes Image 2.1 Flash 模型生图。支持文生图与图生图，输出可为可访问图片 URL 或直接返回的 Base64 数据。

## ⚠️ 必须牢记的坑（来自实测）

1. **模型名称带小数点：`agnes-image-2.1-flash`**（不是 `agnes-image-21-flash`）。拼错会直接报错。
2. **返回图片地址在 `data[0].url`**（URL 输出时）或 `data[0].b64_json`（Base64 输出时）。直接解析这两个字段即可。
3. **`response_format` 不要放在请求体顶层**，否则可能返回 400。需要 URL 输出时放在 `extra_body.response_format: "url"`；文生图需要 Base64 时用顶层 `return_base64: true`；图生图需要 Base64 时用 `extra_body.response_format: "b64_json"`。
4. **图生图不需要传 `tags: ["img2img"]`**，只需提供输入图。
5. **API Key 存放**：本机密钥统一放在技能目录 `config.json` 的 `api_key` 字段（已在 `.gitignore`，不进版本库）。**脚本不要写死 key，公开文档统一用 `YOUR_API_KEY` 占位**。
   - 读取优先级（高 → 低）：命令行 `--api-key` > 环境变量 `AGNES_API_KEY` > `config.json.api_key`。
   - config.json 还可放 `base_url` / `model` / `default_size` / `cover_size` 等默认参数。
   - 换 key 时只改 config.json；未配置时脚本会明确报错并提示这三种方式，不会猜测。
6. 图片生成可能耗时数秒到几十秒，客户端超时建议设 60s~360s。

## API 信息

- Base URL：`https://apihub.agnes-ai.com`
- 接口：`POST https://apihub.agnes-ai.com/v1/images/generations`
- 认证：`Authorization: Bearer $AGNES_API_KEY`
- Content-Type：`application/json`
- 模型名：`agnes-image-2.1-flash`

## 何时用本技能

- 用户说"用 agnes / agnes-image 帮我画/生成一张图" → 文生图。
- 用户说"用 agnes 把这张图转成…/风格迁移/局部优化"并给了图片 → 图生图。
- 用户提供图片 URL 或本地图片，要求基于它重新生成 → 图生图（`--image`）。

## 调用方式（推荐用脚本）

技能自带 `scripts/generate_image.py`，用 Python 标准库（`urllib`），**无需安装任何第三方包**。密钥已存本机 `config.json`，脚本会自动读取，命令行无需再传。

```bash
# 文生图（默认返回 URL，自动下载保存为本地文件）
python "$SKILL_DIR/scripts/generate_image.py" \
  --prompt "一只橘色小猫坐在窗台上，午后阳光，柔和暖色调，高细节" \
  --size 1024x768 \
  --output cat.png

# 文生图 + 直接返回 Base64（不下载，打印 b64 长度）
python "$SKILL_DIR/scripts/generate_image.py" \
  --prompt "..." --size 1024x768 --base64

# 图生图（输入图可为公网 URL 或本地图片路径，本地图会自动转 Data URI）
python "$SKILL_DIR/scripts/generate_image.py" \
  --prompt "把场景改成雨夜赛博朋克风，霓虹倒影，保持原构图" \
  --size 1024x768 \
  --image https://example.com/input.png \
  --output out.png
```

参数说明：
- `--prompt`：必填，生成/编辑提示词。
- `--size`：必填（文生图），如 `1024x768`。
- `--image`：图生图输入，公网 URL 或本地图片路径（本地自动 base64）。
- `--output`：输出文件名（默认 `agnes_image.png`）。
- `--base64`：文生图返回 Base64 而非 URL。
- `--api-key`：可选，不传则用环境变量 `AGNES_API_KEY`。

> `$SKILL_DIR` 为本技能目录。若脚本与 SKILL.md 同目录，可写 `python "$(dirname "$0")/scripts/generate_image.py"` 或直接使用绝对路径。

## 直接 curl（对照参考）

文生图 URL 输出：
```bash
curl https://apihub.agnes-ai.com/v1/images/generations \
  -H "Authorization: Bearer $AGNES_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"agnes-image-2.1-flash","prompt":"A luminous floating city above a misty canyon at sunrise, cinematic realism","size":"1024x768","extra_body":{"response_format":"url"}}'
```
返回：`{"data":[{"url":"https://storage.googleapis.com/agnes-aigc/xxx.png", ...}]}` → 取 `data[0].url`。

图生图（输入图放 `extra_body.image` 数组，URL 或 Data URI 均可）：
```bash
curl https://apihub.agnes-ai.com/v1/images/generations \
  -H "Authorization: Bearer $AGNES_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"agnes-image-2.1-flash","prompt":"Transform into a rain-soaked cyberpunk night, keep composition","size":"1024x768","extra_body":{"image":["https://example.com/input.png"],"response_format":"url"}}'
```

> **图生图输入图位置（2026-09-10 校正）**：2.1 官方文档参数表写的是"顶层 `image`"，但其所有 curl 示例都放在 `extra_body.image`，而后继的 2.5 Flash 文档明确要求"图生图和多图合成的输入图必须放 `extra_body.image`"，且声明**完整兼容 2.1 Flash 的接入方式**。故本技能脚本默认放 `extra_body.image`；若遇到"缺少 image"类报错，可用 `--top-level-image` 退回顶层 `image`。

## 请求参数

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| model | string | 是 | 固定 `agnes-image-2.1-flash` |
| prompt | string | 是 | 提示词 |
| size | string | 是 | 输出尺寸，如 `1024x768` |
| extra_body.image | string[] | 图生图必填 | 输入图数组，公网 URL 或 Data URI Base64（**默认位置**） |
| image（顶层） | string[] | 备用 | 仅当 extra_body 方式报错时用 `--top-level-image` 切换 |
| return_base64 | boolean | 否 | 文生图要 Base64 时置 true |
| extra_body | object | 否 | 扩展参数，含 `response_format`、`image` |

## 提示词最佳实践

结构：`[主体] + [场景/环境] + [风格] + [光照] + [构图] + [质量要求]`。

- 文生图示例：`A futuristic city marketplace filled with flying vehicles, holographic signs, dense crowds, neon lighting, cinematic realism, ultra-detailed, high-information-density composition`
- 图生图示例：`Convert into a fantasy winter landscape, add snow and warm window lights, while preserving the original building structure and camera angle.`

## 价格

生成图片 $0.003 / 张。
