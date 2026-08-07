---
name: gzh-cover
description: 根据中文主标题 + 画面含义 + 风格，自动生成微信公众号 2.35:1 封面图（默认暖色黏土风，标题文字嵌入画面）。当用户提供"主标题/画面含义/风格"要求生成公众号头图，或说"生成封面/做张封面图/给这篇配个头图"时触发。底层用 nano banana 2（gemini-3.1-flash-image）文生图，模型参数存于本技能目录 config.json。
version: 1.1
author: 陈恩
---

# 公众号封面图生成（gzh-cover）

把"一句话封面需求"变成一张可直接发公众号的 2.35:1 头图。底层用 **nano banana 2 = gemini-3.1-flash-image** 文生图（该模型能稳定渲染中文标题文字，所以封面主标题直接嵌进画面，不另做贴字）。

## 技能目录
`SKILL_DIR` = 本 SKILL.md 所在目录，脚本路径 = `${SKILL_DIR}/gen_cover.py`。

## 触发场景
- 用户说"给这篇生成封面 / 做张头图 / 封面用 XX 风格"
- 用户提供封面需求：`标题文字需要嵌入画面，<风格>` + `主标题：<文章主标题>` + `画面含义：<摘要+情绪>`
- 不触发：正文插图（gzh-illustration / baoyu-image-gen 职责，16:9，不进封面）

## 输入格式（用户给或你代填）
| 字段 | 说明 | 示例 |
|------|------|------|
| 风格 | 视觉风格，默认「暖色黏土风」 | 暖色黏土风 / 手绘卡通科技风 / 极简扁平 |
| 主标题 | 嵌进画面的中文标题（通常=文章标题） | 申报材料清单：一表理清 8 大类 |
| 画面含义 | 一句话摘要+情绪，用来转译视觉 | 高企申报最怕临门一脚缺材料，并成可勾选自查清单 |

## 工作流程
1. **确认输入**：拿到 风格/主标题/画面含义，缺哪个就问用户；只说"配个封面"时从当前草稿取标题和摘要自动填。
2. **视觉转译（核心，必须做）**：把「画面含义」翻成英文视觉描述，按 4 要素——
   - **主体**：画面核心物件/角色
   - **背景**：场景、氛围底
   - **艺术风格**：暖色黏土风（暖白底 #F5F0E8 / 奶白黏土 #F0E8DC / 金黄 #FFD700 / 橙红 #FF6B35）/ 手绘卡通 / 圆角白卡 / 柔和投影；默认暖色黏土，用户指定科技风才换科技蓝紫
   - **光影**：温暖、明亮、干净、专业、友好
   硬性规定：**21:9 超宽横幅（实测 1584×672≈2.357:1，符合公众号 2.35:1）**、**2K 画质**、**主标题中文清晰嵌画面顶部/居中**、**不出现无关文字**。
3. **写英文 prompt 到文件**：存成纯文本（如 `F:/wbx/<文章目录>/cover_prompt.txt`）。脚本只认 `--prompt-file`（读文件），**没有** `--prompt` 直传。
4. **调用生成脚本**（python3，或 Windows `C:/Users/Administrator/.workbuddy/binaries/python/versions/3.13.12/python.exe`）：
   ```
   SKILL_DIR="C:/Users/Administrator/.workbuddy/skills/gzh-cover"
   python3 "$SKILL_DIR/gen_cover.py" --prompt-file "F:/wbx/<文章目录>/cover_prompt.txt" --out "F:/wbx/<文章目录>/cover.jpg" --role cover
   ```
   脚本从 `config.json` 的 `providers.cover` 读 endpoint/api_key/model/size（`21:9`）。**输出扩展名随意**：nano banana 2 返回 JPEG，脚本按真实文件头校正为 `.jpg` 落盘（写 `.png` 也存成 `.jpg`）。
5. **交付**：回传 `cover.jpg` 路径预览；要微调（风格/构图/标题位置）改 prompt 文件重跑。

## 角色选择（config.json 的 providers 键）
| role | 用途 | 模型 | size |
|------|------|------|------|
| `cover` | 公众号 2.35:1 头图 | gemini-3.1-flash-image | 21:9 |
| `illustration` | 正文 16:9 插图 | gpt-image-2 | 16:9 |
封面只用 `--role cover`；正文插图请用 baoyu-image-gen。

## Options（gen_cover.py）
| 参数 | 说明 |
|------|------|
| `--prompt-file <path>` | 英文 prompt 文本文件（**必填**，无 `--prompt` 直传） |
| `--out <path>` | 输出路径（脚本校正扩展名） |
| `--role <key>` | providers 键：`cover`/`illustration` |
| `--base-url`/`--api-key`/`--model` | 覆盖 provider 配置 |
| `--size` | 覆盖画幅：`16:9`/`21:9` |

## 模型参数（config.json）
首用需配 `providers.cover`：endpoint、api_key、model（默认 `gemini-3.1-flash-image`）、size（默认 `21:9`，实测 1584×672≈2.357:1 符合 2.35:1；**勿用像素尺寸如 2352x1000**，中继不支持会报错）。未配置脚本报错「api_key not set / provider 缺少 base_url」，停下向用户索取，不猜测。

## 错误处理
- **缺 key/endpoint**：脚本报错退出并提示缺哪个 → 停下索取，不猜测。
- **429 限频**：脚本内置退避重试（gpt-image-2 中继 1 分钟限 1 次，等 65s×N 重试，最多 6 次；nano banana 2 一般不限频，遇 429 同样重试）。
- **返回无图像**：脚本打印完整返回并退出，便于排查。
- **格式校正**：按真实文件头（JPEG/PNG）校正扩展名，落盘格式与内容一致。

## 与发布流程衔接
封面 2.35:1、不进正文、仅作头图。生成后配合 gzh-draft 的 `--cover` 推草稿箱（见用户长期记忆「发布工作流习惯」）。
