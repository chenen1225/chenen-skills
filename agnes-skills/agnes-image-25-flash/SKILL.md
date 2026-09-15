---
name: agnes-image-25-flash
description: "【Agnes AI 最新一代生图技能 · agnes-image-25-flash】调用 Agnes Image 2.5 Flash 模型（能力全面超过 2.1 Flash），通过 Agnes API Gateway (apihub.agnes-ai.com) 生成图片。支持文生图、图生图、多图合成；size 用 1K/2K/3K/4K 档位配合 ratio 宽高比；输出可为 URL 或 Base64。触发词：agnes 生图、agnes-image-2.5、用 agnes 画一张、东方少女、图生图、多图合成、图片风格转换、生成封面/壁纸/海报。"
version: 1.0.0
metadata:
  homepage: https://agnes-ai.com/zh-Hans/docs/agnes-image-25-flash
  requires:
    anyBins:
      - python3
      - python
---

# Agnes Image 2.5 Flash 技能

Agnes 最新一代图像模型，整体能力全面超过 Agnes Image 2.1 Flash。请求/响应参数、支持尺寸、价格与计费方式与 2.1 Flash 保持一致，另外**新增多图合成**与**档位式尺寸（1K/2K/3K/4K + ratio）**。

## ⚠️ 必须牢记的坑

1. **模型名称：`agnes-image-2.5-flash`**（带小数点）。
2. **🔴 图生图 / 多图合成的输入图必须放 `extra_body.image`（数组）**，不是顶层 `image`。官方文档反复强调，所有示例一致。
3. **`response_format` 绝不能放在请求体顶层**（会 400）。URL 输出用 `extra_body.response_format: "url"`；图生图 Base64 用 `extra_body.response_format: "b64_json"`；文生图 Base64 用顶层 `return_base64: true`。
4. **不需要传 `tags: ["img2img"]`**。
5. **返回图片地址在 `data[0].url`**（URL 输出）或 `data[0].b64_json`（Base64 输出）。
6. API Key 用环境变量 `AGNES_API_KEY`，不要写死在脚本/文档里。
7. 生成耗时数秒到几十秒，客户端超时建议 **60s–360s**。
8. 不受支持的精确尺寸（如 `1920x1080`、`2560x1440`）会被自动标准化映射到最接近档位。想要 16:9 素材，请请求 `size:"2K"` + `ratio:"16:9"`（实际输出 2624×1472），再在下游裁剪。

## API 信息

- 接口：`POST https://apihub.agnes-ai.com/v1/images/generations`
- 认证：`Authorization: Bearer $AGNES_API_KEY`
- Content-Type：`application/json`
- 模型名：`agnes-image-2.5-flash`

## 请求参数

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `model` | string | 是 | `agnes-image-2.5-flash` |
| `prompt` | string | 是 | 生成或编辑的文本指令 |
| `size` | string | 是 | 档位 `1K`/`2K`/`3K`/`4K`（推荐）；兼容 `1024x768` 等历史精确写法 |
| `ratio` | string | 否 | 宽高比：`1:1`、`3:4`、`4:3`、`16:9`、`9:16`、`2:3`、`3:2`、`21:9`，默认 `1:1` |
| `image` | string[] | 图生图/多图必填 | **放在 `extra_body.image`**，支持公网 URL 或 Data URI Base64 |
| `return_base64` | boolean | 否 | 文生图 Base64 输出 |
| `extra_body` | object | 否 | 附加参数，含 `image`、`response_format` |

## 输出尺寸参考

| Ratio | 1K | 2K | 3K | 4K |
| --- | --- | --- | --- | --- |
| 1:1 | 1024×1024 | 2048×2048 | 3072×3072 | 4096×4096 |
| 3:4 | 864×1152 | 1728×2304 | 2592×3456 | 3456×4608 |
| 4:3 | 1152×864 | 2304×1728 | 3456×2592 | 4608×3456 |
| 16:9 | 1312×736 | 2624×1472 | 3936×2208 | 5248×2944 |
| 9:16 | 736×1312 | 1472×2624 | 2208×3936 | 2944×5248 |
| 2:3 | 832×1248 | 1664×2496 | 2496×3744 | 3328×4992 |
| 3:2 | 1248×832 | 2496×1664 | 3744×2496 | 4992×3328 |
| 21:9 | 1568×672 | 3136×1344 | 4704×2016 | 6272×2688 |

## 何时用本技能

- "用 agnes / agnes-image 画一张…" → 文生图。
- 给了图片要"转换风格/重绘/局部优化" → 图生图。
- 给了多张图要"合成/把两张图合在一起" → 多图合成。
- 要壁纸/横幅 → `size 2K` + `ratio 16:9`；要手机竖屏 → `ratio 9:16`；要公众号封面 → `ratio 2.35:1` 用 `21:9`（1568×672 @1K）近似。

## 调用方式（推荐用脚本）

自带 `scripts/generate_image.py`，仅用 Python 标准库（`urllib`），无需 pip 安装。

```bash
# 文生图（默认 1K / 1:1）
python "$SKILL_DIR/scripts/generate_image.py" \
  --prompt "一位优雅的东方少女，乌黑长发，淡青色汉服，江南水乡，柔和晨光，唯美写实，高细节" \
  --size 1K --ratio 3:4 --output girl.png

# 16:9 壁纸（2K 档位 → 2624×1472）
python "$SKILL_DIR/scripts/generate_image.py" \
  --prompt "A cinematic product hero image, clean lighting, high detail" \
  --size 2K --ratio 16:9 --output wallpaper.png

# 图生图（输入图可为公网 URL 或本地路径，本地自动转 Data URI）
python "$SKILL_DIR/scripts/generate_image.py" \
  --prompt "把场景改成雨夜赛博朋克风，霓虹倒影，保持原构图" \
  --image input.png --size 1K --ratio 16:9 --output out.png

# 多图合成（传入多张图）
python "$SKILL_DIR/scripts/generate_image.py" \
  --prompt "将第一张图的人物与第二张图的产品合成为一张电影级活动海报" \
  --image char.png product.png --size 2K --ratio 16:9 --output poster.png

# 文生图 + Base64 输出（不下载）
python "$SKILL_DIR/scripts/generate_image.py" --prompt "..." --size 1K --base64
```

参数：
- `--prompt`（必填）、`--size`（默认 `1K`）、`--ratio`（不传则由服务端默认 `1:1`）
- `--image`（可传多个，图生图/多图合成；本地文件自动转 base64 Data URI）
- `--base64`、`--output`（默认 `agnes_image.png`）、`--api-key`（默认读 `$AGNES_API_KEY`）

## 直接 curl（对照参考）

文生图 URL 输出：
```bash
curl https://apihub.agnes-ai.com/v1/images/generations \
  -H "Authorization: Bearer $AGNES_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"agnes-image-2.5-flash","prompt":"A luminous floating city above a misty canyon at sunrise, cinematic realism","size":"2K","ratio":"16:9","extra_body":{"response_format":"url"}}'
```

图生图（输入图在 `extra_body.image`）：
```bash
curl https://apihub.agnes-ai.com/v1/images/generations \
  -H "Authorization: Bearer $AGNES_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"agnes-image-2.5-flash","prompt":"Transform into a rain-soaked cyberpunk night, keep composition","size":"1024x768","extra_body":{"image":["https://example.com/input.png"],"response_format":"url"}}'
```

多图合成：
```bash
-d '{"model":"agnes-image-2.5-flash","prompt":"Combine the two characters into a fantasy battle scene","size":"1K","extra_body":{"image":["https://ex.com/a.png","https://ex.com/b.png"],"response_format":"url"}}'
```

## 响应格式

```json
{"created":1780000000,"data":[{"url":"https://storage.googleapis.com/agnes-aigc/xxx.png","b64_json":null,"revised_prompt":null}]}
```

## 提示词最佳实践

- 文生图：`[主体] + [场景/环境] + [风格] + [光照] + [构图] + [质量要求]`
- 图生图：`[改变要求] + [新风格/场景] + [要添加或移除的元素] + [要保留的元素]`
- 多图合成：`[参考图角色] + [目标场景] + [图间关系] + [风格/光照/构图]`，并说明每张参考图的角色
- 高信息密度：明确描述视觉层次（主体 / 背景 / 次要细节 / 风格 / 光照 / 构图约束）

## 定价

与 2.1 Flash 相同；**当前所有输出分辨率档位和输入参考图片均免费**（刊例价：1K \$0.010/张、2K \$0.018/张、3K \$0.021/张、4K \$0.024/张，第 4 张起输入参考图 \$0.003/张）。

## 接入检查清单

- [x] 用 `agnes-image-2.5-flash` 作为模型名称
- [x] 用 `https://apihub.agnes-ai.com/v1/images/generations` 作为端点
- [x] 文生图必带 `model`、`prompt`、`size`
- [x] 建议用 `1K`/`2K` 档位 + `ratio`
- [x] 图生图/多图合成的图放 `extra_body.image`
- [x] `response_format` 不放顶层，不传 `tags`
