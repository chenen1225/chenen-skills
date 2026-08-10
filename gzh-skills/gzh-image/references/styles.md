# 图像风格库（gzh-image）

`gzh-image` 不绑定单一视觉风格。**默认暖色黏土**；可按文章内容选其他风格，**选定后封面 / 插图 / 图解全部套同一风格的「英文片段」**，保证整篇视觉统一。

## 何时选风格

1. **用户指定风格名** → 直接用对应预设（见下）。
2. **用户未指定但内容明显适配某风格** → agent 读文章（主题 / 调性 / 受众），推 2–3 款最搭的预设（各附一句理由），用 AskUserQuestion 让用户选，再出图。
3. **用户完全没提** → 用默认「暖色黏土」，不阻断流程。

## 预设清单

### 1. 暖色黏土（warm-clay）· 默认
- **色板**：暖白底 `#F5F0E8` / 奶白黏土 `#F0E8DC` / 金黄 `#FFD700` / 橙红 `#FF6B35`
- **质感**：软陶 / 黏土雕塑感，无黑线轮廓，圆润，柔和漫射光
- **最适合**：个人故事、人文、生活、情感、随笔、亲子
- **英文片段**：`warm clay art style, cream background (#F5F0E8), soft clay-like forms in milk-white (#F0E8DC) and warm accents golden (#FFD700) / orange-red (#FF6B35), rounded shapes, no black outlines, soft diffuse light`
- **图解处理**：黏土块 + 圆润箭头，标签放白底圆牌
- **封面处理**：暖色黏土场景托住中文标题

### 2. 扁平极简（flat-minimal）
- **色板**：米白底 `#F7F7F5` / 主色 IKB 蓝 `#002FA7` / 辅助灰 `#9AA0A6` / 强调橙 `#FF6B35`
- **质感**：纯色块、无渐变、细几何、大量留白、2px 描边
- **最适合**：职场报告、商业分析、方法论、效率工具、SaaS
- **英文片段**：`flat minimal illustration, off-white background (#F7F7F5), solid color blocks, no gradients, thin 2px geometric outlines, generous white space, one IKB blue (#002FA7) accent with orange (#FF6B35) highlights`
- **图解处理**：几何图形 + 细线箭头，标签白底方牌
- **封面处理**：大色块 + 中文标题，极简留白

### 3. 科技蓝紫（tech-bluepurple）
- **色板**：深蓝底 `#0B1026` / 霓虹蓝 `#3B82F6` / 紫 `#8B5CF6` / 青 `#22D3EE`
- **质感**：发光描边、网格、玻璃拟态、暗色科技感
- **最适合**：AI / 代码 / 数据 / 产品 / 互联网
- **英文片段**：`dark tech style, deep navy background (#0B1026), glowing neon blue (#3B82F6) and purple (#8B5CF6) edges, cyan (#22D3EE) data flows, glassmorphism, subtle grid, luminous thin lines`
- **图解处理**：发光节点 + 数据流线，标签发光字
- **封面处理**：暗色科技场景 + 发光中文标题（务必确保标题高对比可读）

### 4. 国风水墨（ink-traditional）
- **色板**：宣纸底 `#F4EFE6` / 墨黑 `#1A1A1A` / 朱砂 `#C0392B` / 石青 `#2E5C8A`
- **质感**：水墨晕染、留白、毛笔笔触、远山 / 云纹
- **最适合**：文化 / 历史 / 哲学 / 传统 / 茶道 / 非遗
- **英文片段**：`Chinese ink wash painting style, rice-paper background (#F4EFE6), soft ink brush strokes in sumi black (#1A1A1A), vermillion seal red (#C0392B) and mineral blue (#2E5C8A) accents, generous negative space, misty mountains`
- **图解处理**：水墨意象 + 印章式标签，慎用过多几何
- **封面处理**：水墨留白 + 中文标题（可竖排）

### 5. 水彩手绘（watercolor）
- **色板**：水彩纸底 `#FBF8F1` / 浅蓝 `#A7C7E7` / 暖粉 `#F4C2C2` / 草绿 `#B5D99C`
- **质感**：水彩晕染、手绘笔触、不规则边缘、通透
- **最适合**：旅行 / 生活方式 / 情感 / 亲子 / 美食
- **英文片段**：`loose watercolor illustration, watercolor paper background (#FBF8F1), soft bleeds in pastel blue (#A7C7E7), warm pink (#F4C2C2) and sage green (#B5D99C), hand-painted brush texture, irregular edges, airy and translucent`
- **图解处理**：手绘图标 + 手写感标签
- **封面处理**：水彩场景 + 中文标题

## 使用方式

写 prompt 时，把所选风格的「英文片段」嵌进 prompt 的 `Style/medium` 位置（替换原先写死的暖色黏土 / Swiss 3D 描述）。**标签与构图结构仍按 `visual-style.md` + `prompt-patterns.md` 的方法论**，风格只影响视觉质感，不替代标签 / 结构要求。未选风格时默认暖色黏土片段。

## 注意事项
- **插图**：尽量不生成文字（字交给 gzh-html / 正文），风格只管视觉。
- **图解**：必须带中文标签，风格只影响视觉质感，不改变"带标签 + 结构"的硬要求。
- **封面**：中文标题必须清晰嵌画面；暗色风格（科技蓝紫）需确保标题高对比、不糊。
- **统一**：同一篇文章一旦选定风格，封面 / 插图 / 图解不得混用其他风格。
