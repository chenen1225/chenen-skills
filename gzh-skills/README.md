# gzh-skills · 陈恩公众号运营技能集

把「公众号日常运营」拆成一套标准技能，统一以 `gzh-` 前缀命名，覆盖从选题到推送草稿箱的全流程。每个技能自包含，复制到任意 Agent 平台的 `skills/` 目录即可使用。

## 标准工作流（SOP）

```
选题 gzh-topic → 撰写 gzh-write → 图像 gzh-image(插图 --role illustration / 图解 --role diagram / 封面 --role cover)
   → HTML gzh-html → 推送 gzh-draft(草稿箱)
总指挥：gzh-ops（串起以上环节）
```

> 图像生成已统一为**单一技能 `gzh-image`**：封面、正文插图、带标注图解共用一个 `config.json`，不再分散到多个技能。

## 技能清单

| 技能 | 环节 | 说明 |
|------|------|------|
| [gzh-ops](./gzh-ops) | 运营总流程 | 总指挥，把一篇文从 0 跑到草稿箱，定义各环节产物与交接 |
| [gzh-topic](./gzh-topic) | 选题 | 从读者痛点/个人实践/热点收敛出"一个能写的角度"，产出标题+导读+大纲 |
| [gzh-write](./gzh-write) | 文章撰写 | 固化「恩嗲 8 条公众号写作规矩」：导读先行、文末金句、第一人称真实数据、分章编号、加粗抛结论、口语感、先价值后带货、按文类区分互动钩子 |
| [gzh-image](./gzh-image) | 图像生成（封面/插图/图解） | 公众号全部图像：2.35:1 封面（nano banana 2）、16:9 暖色黏土正文插图（gpt-image-2）、带标注图解（process/loop/system，复用 gpt-image-2）。三种产物共用一份 `config.json` |
| [gzh-html](./gzh-html) | HTML 生成 | Markdown 转适配微信的带内联样式 HTML |
| [gzh-draft](./gzh-draft) | 推送草稿箱 | 通过 API/CDP 把文章推送到公众号草稿箱 |
| [baoyu-image-gen](./baoyu-image-gen) | 可选高级生图引擎 | 支持并发/参考图；默认正文插图已改走 gzh-image --role illustration，不再强制依赖；未纳入 gzh- 命名 |

## 安装

把需要的技能文件夹整个复制到你的 Agent 平台 `skills/` 目录，例如 WorkBuddy：

```
~/.workbuddy/skills/gzh-ops/
~/.workbuddy/skills/gzh-topic/
~/.workbuddy/skills/gzh-write/
~/.workbuddy/skills/gzh-image/
~/.workbuddy/skills/gzh-html/
~/.workbuddy/skills/gzh-draft/
~/.workbuddy/skills/baoyu-image-gen/   # 可选
```

## 配置注意（只需一份文件）

所有 gzh 凭证统一收口在 **`gzh-image/config.json`** 这一个文件，复制 `gzh-image/config.example.json` 为 `config.json` 填入即可：

- `providers.cover`：封面 nano banana 2（`gemini-3.1-flash-image`）
- `providers.illustration`：正文插图 / 图解 gpt-image-2（16:9）
- `wechat`：微信公众号 `app_id` / `app_secret`（供 gzh-draft 读取）

`config.json` 已加入 `.gitignore`（`**/config.json`），真实密钥不会误提交。gzh-draft 优先读这份文件，也兼容环境变量与 `~/.baoyu-skills/.env` 兜底。

- **gzh-html** 运行时需要 `bun` 或 `npx`，首次会按需拉取依赖。
- **baoyu-image-gen** 为可选高级引擎（并发/参考图），默认流程不需要；若单独使用，仍按它的 `.env` 方式配置。

> 公众号「我是陈恩」作者陈恩的 AI 运营实践沉淀。
