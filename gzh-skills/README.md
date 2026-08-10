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

## 一键安装（推荐）

合集根目录提供了安装脚本，**一条命令把所有 `gzh-*` 技能装进你的 Agent 平台**，并自动从 `config.example.json` 生成 `config.json` 模板。脚本会自动覆盖同名旧技能，可反复运行用于升级。

### Windows（PowerShell）

```powershell
# 在 gzh-skills 目录下执行（右键"用 PowerShell 运行"也可）：
powershell -ExecutionPolicy Bypass -File install.ps1
```

### macOS / Linux / Windows Git Bash

```bash
bash install.sh
```

### 自定义目标目录（可选）

```bash
bash install.sh /path/to/your/skills        # bash
powershell -ExecutionPolicy Bypass -File install.ps1 D:\skills   # PowerShell
```

默认目标：`~/.workbuddy/skills`（Windows 为 `%USERPROFILE%\.workbuddy\skills`）。

## 手动安装（备选）

如果你不想跑脚本，也可以把需要的技能文件夹整个复制到 Agent 平台的 `skills/` 目录，例如 WorkBuddy：

```
~/.workbuddy/skills/gzh-ops/
~/.workbuddy/skills/gzh-topic/
~/.workbuddy/skills/gzh-write/
~/.workbuddy/skills/gzh-image/
~/.workbuddy/skills/gzh-html/
~/.workbuddy/skills/gzh-draft/
```

## 配置注意（只需一份文件）

所有 gzh 凭证统一收口在 **`gzh-image/config.json`** 这一个文件，复制 `gzh-image/config.example.json` 为 `config.json` 填入即可：

- `providers.cover`：封面 nano banana 2（`gemini-3.1-flash-image`）
- `providers.illustration`：正文插图 / 图解 gpt-image-2（16:9）
- `wechat`：微信公众号 `app_id` / `app_secret`（供 gzh-draft 读取）

`config.json` 已加入 `.gitignore`（`**/config.json`），真实密钥不会误提交。gzh-draft 优先读这份文件，也兼容环境变量与 `~/.baoyu-skills/.env` 兜底。

- **gzh-html** 运行时需要 `bun` 或 `npx`，首次会按需拉取依赖。

> 公众号「我是陈恩」作者陈恩的 AI 运营实践沉淀。
