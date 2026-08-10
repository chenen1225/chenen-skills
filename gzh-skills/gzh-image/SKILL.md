---
name: gzh-image
description: "【公众号运营技能 · 统一图像 gzh-image】公众号图文所需的全部图像生成：2.35:1 封面（nano banana 2）、16:9 暖色黏土正文插图（gpt-image-2）、带标注图解（process/loop/system 结构图，复用 gpt-image-2）。三种产物共用一份 config.json。触发词：生成封面、做头图、配插图、带字插图、解释图、图解插画、概念拆解图、图表美化、process/loop/system diagrams。"
version: 1.2
author: 陈恩
---

# 公众号统一图像技能（gzh-image）

把"一句话图像需求"变成可直接发公众号的图片。本技能整合了原先分散的封面、正文插图、带标注图解三类产物，**三者的密钥统一收口在本技能目录 `config.json` 一份文件**，不再需要任何外部 `.env`。

底层出图引擎：
- 封面 / 正文插图 / 图解 均通过 `gen_cover.py` 调用 OpenAI 兼容图像接口（`POST {base_url}/images/generations`）。
- 封面用 **nano banana 2 = gemini-3.1-flash-image**（稳定渲染中文标题，标题直接嵌画面）。
- 正文插图、图解用 **gpt-image-2**（中文清晰，暖色黏土风稳出 PNG）。

## 技能目录
`SKILL_DIR` = 本 SKILL.md 所在目录，脚本 = `${SKILL_DIR}/gen_cover.py`，密钥 = `${SKILL_DIR}/config.json`。

## 三种角色（config.json 的 providers 键）
| role | 产物 | 模型 | size | 说明 |
|------|------|------|------|------|
| `cover` | 公众号 2.35:1 头图 | gemini-3.1-flash-image | 21:9 | 标题中文嵌画面，仅作头图 |
| `illustration` | 正文 16:9 暖色黏土插图 | gpt-image-2 | 16:9 | 装饰性配图（**导语固定插图；正文每章插图/图解二选一**），不进封面 |
| `diagram` | 带标注图解（结构解释图） | gpt-image-2 | 16:9 | 复用 illustration 供应商；含中文标签；与插图**每章二选一** |

> `diagram` 与 `illustration` 共用同一供应商（gpt-image-2 / 16:9），区别只在**提示词结构**：diagram 走下方"图解规划方法论"，产出带中文标签的 process/loop/system 结构图。**正文每章按性质在两者中二选一（不叠加）；导读固定用插图定调。**

## 模型参数（config.json）
首用需配 `providers.cover` 与 `providers.illustration`（见 `config.example.json`）：
```json
{
  "providers": {
    "cover":       { "base_url": "https://<你的中继>/v1", "api_key": "YOUR_KEY", "model": "gemini-3.1-flash-image", "size": "21:9" },
    "illustration":{ "base_url": "https://<你的中继>/v1", "api_key": "YOUR_KEY", "model": "gpt-image-2", "size": "16:9" }
  },
  "wechat": { "app_id": "YOUR_APPID", "app_secret": "YOUR_SECRET" }
}
```
未配置脚本报错「api_key not set / provider 缺少 base_url」，停下向用户索取，不猜测。`config.json` 已加入 `.gitignore`，不会误提交。

> gzh-skills 合集所有密钥统一在 **gzh-image/config.json**：`providers.cover`（封面）、`providers.illustration`（正文插图 + 图解）、`wechat`（公众号 AppID/Secret，供 gzh-draft 读取）。只维护这一份即可。

## 调用方式（gen_cover.py）
脚本只认 `--prompt-file`（读文件），**没有** `--prompt` 直传。
```
SKILL_DIR="C:/Users/Administrator/.workbuddy/skills/gzh-image"
python3 "$SKILL_DIR/gen_cover.py" --prompt-file "<prompt>.txt" --out "<out>.jpg" --role <cover|illustration|diagram>
```
| 参数 | 说明 |
|------|------|
| `--prompt-file <path>` | 英文图像 prompt 文本文件（**必填**） |
| `--out <path>` | 输出路径（脚本按真实文件头校正扩展名） |
| `--role <key>` | `cover` / `illustration` / `diagram` |
| `--base-url`/`--api-key`/`--model` | 覆盖 provider 配置 |
| `--size` | 覆盖画幅：`16:9`/`21:9` |

## 工作流

### 1) 封面（--role cover）
1. 拿到 风格/主标题/画面含义，缺哪个就问用户；只说"配个封面"时从当前草稿取标题和摘要自动填。
2. **视觉转译（核心）**：把「画面含义」翻成英文视觉描述，按 4 要素——主体 / 背景 / 艺术风格（默认暖色黏土风）/ 光影。
   - 硬性规定：**21:9 超宽横幅（实测 1584×672≈2.357:1）**、**主标题中文清晰嵌画面顶部/居中**、**不出现无关文字**。
3. 写英文 prompt 到文件 → 调 `gen_cover.py --role cover`。
4. 回传 `cover.jpg` 预览；微调改 prompt 重跑。

### 2) 正文插图（--role illustration）
1. **按章二选一**：导读固定配一张总览式暖色黏土插图定调；正文每一章按性质二选一——概念 / 故事 / 观点类用插图（暖色黏土装饰），流程 / 步骤 / 对比 / 机制类用图解（带中文标签结构图）。**每章只出一张，不叠加**。插入位置：导语插图在导读后、各章所选图在对应章后。
2. 写英文 prompt：暖色黏土风（暖白底 #F5F0E8 / 奶白黏土 #F0E8DC / 金黄 #FFD700 / 橙红 #FF6B35），柔和卡通科学家融入暖色场景；16:9。
3. 调 `gen_cover.py --role illustration` → 落盘 PNG。

### 3) 带标注图解（--role diagram）
本模式复用 `illustration` 供应商（gpt-image-2 / 16:9），但提示词走"图解规划方法论"，产出带中文标签的结构解释图。与插图**二选一**（正文每章只取其一，不叠加；导读不用图解）。流程：
1. 读源文本/截图/数据，识别值得配图的概念或图表。
2. 自选视觉结构（无需问用户，除非选择会实质改变结果）：
   - **Cycle** 循环/反馈/迭代 · **Pipeline** 有序步骤/工作流 · **Hub-and-spoke** 中心协调多分支
   - **Before/after** 状态变化/对比 · **Layer stack** 架构/层级/依赖 · **Data-first** 图表嵌入场景 · **Scientific** 对象/部件/机制
3. 把每个概念压成一句大白话解释 + 3-5 个可见标签（标签 2-5 字最佳，最多 6 字；用具体词如 `用户提示`/`AI 执行`/`结果检查`，不用 `输入阶段`这类抽象词）。
4. 写英文 prompt：描述精确标签文字、画幅、安全边距、共享暖色黏土视觉风格（覆盖 references/visual-style.md 原 guizang 3D Swiss 风格）。
5. 调 `gen_cover.py --role diagram`。
6. 逐图检查：中文标签清晰、位置指对、无多余英文/水印；不对则加约束重生成。

> 图解规划的方法论文档在 `references/`：`visual-style.md`（视觉系统）、`prompt-patterns.md`（结构提示词模板）、`chart-beautify.md`（图表美化）、`qa-checklist.md`（交付前核对）、`reference-gathering.md`（陌生概念查证）、`use-cases-and-routing.md`（按输入选图类型）。本合集**默认暖色黏土风**，references 仅作提示词结构与标签方法论参考。

## 错误处理
- **缺 key/endpoint**：脚本报错退出并提示缺哪个 → 停下索取，不猜测。
- **429 限频**：脚本内置退避重试（gpt-image-2 中继约 1 分钟限 1 次，等 65s×N 重试，最多 6 次；nano banana 2 一般不限频，遇 429 同样重试）。
- **返回无图像**：脚本打印完整返回并退出，便于排查。
- **格式校正**：按真实文件头（JPEG/PNG）校正扩展名，落盘格式与内容一致。

## 与发布流程衔接
封面 2.35:1 仅作头图；正文每章按性质二选一配插图或图解（导语固定插图），均插到对应位置（导语插图在导读后、各章所选图在章后）。生成后配合 gzh-draft 的 `--cover` 推草稿箱（见用户长期记忆「发布工作流习惯」）。
