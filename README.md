# chenen-skills

陈恩（[@chenen1225](https://github.com/chenen1225)）的个人 Agent 技能集合。

这里收集我日常使用、打磨、并逐步开源的技能（Skills）。每个技能是一个独立文件夹，内含 `SKILL.md`（技能定义）及相关资源。

## 技能合集

本仓库按主题分合集（子目录）组织：

| 合集 | 主题 | 说明 |
|------|------|------|
| [hum-socratic](./hum-socratic) | 自我探索 | 人本主义苏格拉底对话引擎，跨平台通用 |
| [gzh-skills](./gzh-skills) | 公众号运营 | 选题 → 撰写 → 图像(gzh-image 统一封面/插图/图解) → HTML → 推送草稿箱 全流程标准技能 |

各合集内含若干技能，详见对应合集的 README。

> 💡 `gzh-skills` 现提供**一键安装脚本**（`install.sh` / `install.ps1`），一条命令装完全部技能并生成配置模板，详见[合集 README](./gzh-skills/README.md#一键安装推荐)。

## 如何安装一个技能

把对应技能文件夹复制到你的 Agent 平台的 `skills` 目录下即可，例如：

- **WorkBuddy**：`~/.workbuddy/skills/<技能名>/`
- **Hermes**：`~/.hermes/skills/<技能名>/`
- 其他兼容 skills 协议的平台：对应 `skills/` 目录

复制后无需改任何路径——技能的状态数据存放在自身目录内的 `state/` 下，随平台自动定位（见各技能 `SKILL.md` 的「文件路径」一节）。

## 仓库约定

- 每个技能一个文件夹，必须有 `SKILL.md`
- 技能运行产生的个人数据存放在 `<技能>/state/`，**不纳入版本库**（已在 `.gitignore` 中排除）
- 欢迎提 Issue / PR 一起完善

> 公众号「我是陈恩」作者陈恩的 AI 实践沉淀。
