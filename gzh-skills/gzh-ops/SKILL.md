---
name: gzh-ops
version: 1.0.0
author: 陈恩
description: "【公众号运营技能 · 总流程编排 gzh-ops】把公众号日常运营串成标准 SOP：选题(gzh-topic) → 撰写(gzh-write) → 插图与图解(gzh-image：--role illustration 正文插图 / --role diagram 带标注图解) → 封面(gzh-image 2.35:1) → HTML(gzh-html) → 推送草稿箱(gzh-draft)。当用户说'走一遍公众号流程 / 发篇文章 / 运营 SOP / 今天发什么'时触发，作为总指挥按顺序调用各 gzh 技能。"
---

# 公众号运营总流程（gzh-ops）

总指挥技能：把一篇公众号文章从 0 跑到草稿箱。按顺序调用下面的 gzh 技能，每个环节交出标准产物，下一环节接力。

## 标准 SOP

| 环节 | 技能 | 产物 | 交接 |
|------|------|------|------|
| 1 选题 | gzh-topic | 标题候选 + 导读口径 + 分章大纲 | Markdown 大纲 |
| 2 撰写 | gzh-write | 正文 Markdown（含导读 / 分章 / 金句 / 钩子） | article.md |
| 3 插图 | gzh-image --role diagram（带标注图解 16:9）+ gzh-image --role illustration（正文插图暖色黏土 gpt-image-2） | imgs/&lt;主题&gt;/ 下图片 + 独立图注段落 | 图注 `<p align="center">` |
| 4 封面 | gzh-image | 2.35:1 头图 cover.jpg（暖色黏土，标题嵌画面） | cover.jpg |
| 5 HTML | gzh-html | 适配微信的 article.html（--theme default） | article.html |
| 6 推送 | gzh-draft | 草稿箱草稿（--author 陈恩 --cover cover.jpg --summary 导读） | 草稿 media_id |

## 关键约定（来自发布工作流习惯）

- **图解 / 配图**：用 gzh-image --role diagram 给导读 + 每章做 16:9 带标注图解，插到对应章后。
- **正文插图**：暖色黏土风用 gzh-image --role illustration（gpt-image-2，16:9，中文清晰），与封面共用同一份 config.json；用户审美偏好暖色黏土，否定纯卡通科技蓝紫。
- **封面**：gzh-image 走 nano banana 2（gemini-3.1-flash-image），21:9≈2.35:1，返回 JPG；不进正文。
- **HTML**：gzh-html 用 `--theme default`；外链要转底部引用加 `--cite`。
- **推送**：gzh-draft 自动上传本地图到微信 CDN；**草稿箱只增不覆盖**，重推产生新版本，提醒用户删旧版。
- **路径坑**：文章放**不含中文路径**的目录，否则 gzh-draft 的 `data-local-path` 中文绝对路径会导致破图。

## 触发

- "走一遍公众号流程""发篇文章""运营 SOP""今天发什么"

## 与其他 gzh 技能关系

- gzh-topic → gzh-write → gzh-image → gzh-html → gzh-draft
- 全部图像（封面/正文插图/带标注图解）统一由 gzh-image 承担，单一技能、单一 config.json。
