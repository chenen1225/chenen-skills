# gzh-skills · 陈恩公众号运营技能集

把「公众号日常运营」拆成一套标准技能，统一以 `gzh-` 前缀命名，覆盖从选题到推送草稿箱的全流程。每个技能自包含，复制到任意 Agent 平台的 `skills/` 目录即可使用。

## 标准工作流（SOP）

```
选题 gzh-topic → 撰写 gzh-write → 插图 gzh-illustration(+baoyu-image-gen 暖色黏土)
   → 封面 gzh-cover(2.35:1) → HTML gzh-html → 推送 gzh-draft(草稿箱)
总指挥：gzh-ops（串起以上环节）
```

## 技能清单

| 技能 | 环节 | 说明 |
|------|------|------|
| [gzh-ops](./gzh-ops) | 运营总流程 | 总指挥，把一篇文从 0 跑到草稿箱，定义各环节产物与交接 |
| [gzh-topic](./gzh-topic) | 选题 | 从读者痛点/个人实践/热点收敛出"一个能写的角度"，产出标题+导读+大纲 |
| [gzh-write](./gzh-write) | 文章撰写 | 固化「恩嗲 8 条公众号写作规矩」：导读先行、文末金句、第一人称真实数据、分章编号、加粗抛结论、口语感、先价值后带货、按文类区分互动钩子 |
| [gzh-illustration](./gzh-illustration) | 插图/图解 | 给导读+每章生成 16:9 带标注图解（暖色黏土风可选） |
| [gzh-cover](./gzh-cover) | 封面生成 | 生成公众号 2.35:1 头图（暖色黏土，标题嵌画面） |
| [gzh-html](./gzh-html) | HTML 生成 | Markdown 转适配微信的带内联样式 HTML |
| [gzh-draft](./gzh-draft) | 推送草稿箱 | 通过 API/CDP 把文章推送到公众号草稿箱 |
| [baoyu-image-gen](./baoyu-image-gen) | 正文插图引擎 | 通用生图工具（暖色黏土正文插图），本流程固定搭档，未纳入 gzh- 命名 |

## 安装

把需要的技能文件夹整个复制到你的 Agent 平台 `skills/` 目录，例如 WorkBuddy：

```
~/.workbuddy/skills/gzh-ops/
~/.workbuddy/skills/gzh-topic/
~/.workbuddy/skills/gzh-write/
~/.workbuddy/skills/gzh-illustration/
~/.workbuddy/skills/gzh-cover/
~/.workbuddy/skills/gzh-html/
~/.workbuddy/skills/gzh-draft/
~/.workbuddy/skills/baoyu-image-gen/
```

## 配置注意

- **gzh-cover** 需要密钥：复制 `gzh-cover/config.example.json` 为 `config.json` 并填入你的 `api_key`（见技能内说明）。`config.json` 已加入 `.gitignore`，不会误提交。
- **gzh-draft** 需要微信公众号 API 凭证，放在用户级 `~/.baoyu-skills/.env`（`WECHAT_APP_ID` / `WECHAT_APP_SECRET`）。
- **gzh-html / gzh-illustration** 运行时需要 `bun` 或 `npx`，首次会按需拉取依赖。

> 公众号「我是陈恩」作者陈恩的 AI 运营实践沉淀。
