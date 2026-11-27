# OpenCode 适配

对应版本：以当前 OpenCode 文档与本仓库既有用法为准（`task`、文件式 agent、`permission` 白名单）。以下为落地步骤，不是平台承诺。

## 加载方法（`load_rules`）

- 技能放 `.opencode/skills/research-workflow/`；项目约定写在 `AGENTS.md`。
- 若某版本不加载技能目录，退化为：把 `SKILL.md` 内容并入 `AGENTS.md`，其余文件仍按相对路径引用。

## 角色实例化

OpenCode 是**文件式 agent**，角色契约要落成 `.opencode/agents/<name>.md`：

```markdown
---
description: 交互式采集角色。隔离搜索、页面交互与截图，只回传结构化证据与产物路径。
mode: subagent
steps: 80
permission:
  edit: allow
  read: allow
  webfetch: allow
  skill:
    "*": deny
    "<浏览器技能名>": allow
  bash:
    "*": ask
    "<浏览器命令前缀>*": allow
  task: deny
  question: deny
  external_directory:
    "*": allow
---

遵守 <包路径>/roles/browser-collector.md 的全部约束。本次 brief 如下：
…
```

要点：

- **正文不要复制角色契约**，引用 `roles/*.md`，避免两处维护。
- `task: deny` 对应"不能派生下级"；`question: deny` 对应"不能向用户提问"。
- `permission` 是这个平台上唯一**真正生效**的边界；不要在 prompt 里写"我只用 X 工具"就以为拦住了。

## 派生与续接（`spawn` / `resume`）

- `spawn`：用任务工具调用上面声明的子 agent，从返回内容里取出任务 id 并记录。
- `resume`：携带该任务 id 继续同一会话。**返回的 id 与传入不一致时**，说明平台静默新建了会话：忽略这次增量结果，改为把已完成任务、证据、失败上下文与待办一次带全，重新派发并记录新 id。
- 采集子 agent 只派一个，串行跑完；补采续接同一任务，不重开。

## 取数与写文件（`fetch_*` / `fs_scoped`）

- `fetch_static`：内置抓取工具。
- `fetch_interactive`：项目指定的浏览器通道（skill + bash 前缀白名单）。
- `fs_scoped`：`edit: allow` 加 `external_directory` 决定可写范围；子 agent 不要写项目目录之外。

## 已知限制

| 限制 | 影响 | 降级 |
|---|---|---|
| 平台可能静默新建任务会话 | 续接失败会丢上下文 | 每次续接后比对任务 id；不一致就重整上下文重派 |
| 子 agent 权限来自 frontmatter | 改约束要改文件，不是改 prompt | 角色契约变化时同步改 agent 文件 |
| 技能加载时机按平台版本 | 可能出现"写了没生效" | 用一句话验证：新会话里能否 `skill` 加载到本包 |

## 一句话启动

> 加载 `research-workflow`，按六阶段执行；派采集用 `browser-collector` 子 agent；证据冻结前不要派写作。
