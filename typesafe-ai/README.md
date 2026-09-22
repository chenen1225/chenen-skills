# typesafe-ai

TypeSafe 智能体技能（drop-in skill for agent environments）。

通过 TypeSafe 的三种问题原语（Choice / Noul / Score）做结构化判断，替代脆弱的
prompt-and-parse 代码。详见官方文档 https://docs.typesafe.ai 与技能主文档 `SKILL.md`。

## 目录结构

- `SKILL.md` —— 技能主文档（agent 加载时读取）
- `references/typesafe-client.ts` —— 多 key 轮换 HTTP 客户端参考实现
- `.env.example` —— 环境变量模板

## 安装

将整个 `typesafe-ai/` 目录复制到 agent 的 skills 目录（如
`~/.workbuddy/skills/`），新会话即可加载。

## 配置 API Key（.env 用法）

技能与参考客户端都**不存储**密钥，密钥通过环境变量传入。

### 1. 用模板创建你的 .env

复制 `.env.example` 为 `.env`，放在**调用客户端的项目根目录**（不是本技能目录）：

```bash
cp .env.example .env
```

编辑 `.env`，填入你的 key：

```dotenv
# 单 key
TYPESAFE_API_KEY=ts_live_xxxxxxxxxxxxxxxx

# 或多 key 轮换（逗号分隔，推荐高并发 / 抗限流）
TYPESAFE_API_KEYS=ts_live_key1,ts_live_key2,ts_live_key3
```

### 2. 让客户端读到 .env

`references/typesafe-client.ts` 已内置 best-effort dotenv 自动加载：

```ts
import("dotenv/config").catch(() => {});
```

只要**消费项目**安装了 `dotenv`（`npm i dotenv`），就会自动从项目 cwd 加载
`.env`，无需手写加载器。

没装 `dotenv` 也没关系 —— 用真实环境变量（系统环境变量 / 平台密钥管理）仍然生效。

### 3. 安全提醒

- `.env` 含真实密钥，**必须加进 `.gitignore`，绝不提交**；
- 不要在本技能目录里放 `.env`（技能目录是共享的）；
- 多 key 是单 key 维度的限流（`429`），多 key 可横向摊配额。

## 多 key 轮换客户端

见 `references/typesafe-client.ts`：自管 key 池、`401` 自动剔除坏 key、`429 / 529`
指数退避。用法：

```ts
import { askTypeSafe } from "./references/typesafe-client";

const res = await askTypeSafe(
  "I was charged twice. Please fix this ASAP.",
  { billing: { type: "noul", instructions: "Is this about billing?" } }
);
```
