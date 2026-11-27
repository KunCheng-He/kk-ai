# OpenCode 适配

本文件只写「在这套工具上怎么做到」。流程规则一律在 `SKILL.md`，这里不新增任何流程规则。

## 加载方式

- skill 放在 `.opencode/skills/`（或用户级 skills 目录），命中触发关键词后主 Agent 加载。
- 角色加载：用 `task` 派生文件式 agent。`.opencode/agents/` 下建两个薄壳角色文件，**正文只写一句「先读 `<本 skill 绝对路径>/roles/writer.md`（或 `reviewer.md`）并按其执行」**，不复制规范内容。
  - 规范仍只在 `roles/` 维护；agent 文件是平台必需的入口，不含规则，改规范不必同步 agent 文件。
  - 若平台支持角色文件内直接引用外部路径，用引用；不支持时必须保留人工 diff 检查。
- 主 Agent 负责关口：三个关口都用 `question` 工具在主会话完成。

## 派生与续接

| 动作 | OpenCode 写法 |
|---|---|
| 派生执行者 | `task`，调用 `woaile-gzh-writer` / `woaile-gzh-reviewer`，返回 `task_id` |
| 等结果 | 必须等 task 返回，才能向用户展示大纲/成稿或进下一阶段 |
| 续接 | 用同一个 `task_id` 继续原任务，保留上下文 |
| 补采 | 续接同一个 `browser-researcher`，不新建，否则 ego task space 与登录态丢失 |

角色能力约束（OpenCode 侧）：

- agent frontmatter 里用 `permission` 收紧权限：审查 agent 设 `edit: deny`、`write: deny`，只读才真正被硬约束
- 写作 agent 设 `task: deny`，使其不能再派生
- 采集 agent 允许加载 skill，以便使用 `ego-browser`

## 取数

- **静态页面**：`webfetch`。不要把整页 HTML 留在主上下文。
- **搜索、登录态、动态渲染、翻页、截图**：`browser-researcher` agent + `ego-browser`，串行执行。
- 图片初审：能读图才读；读不了就退回可编程校验（`sips`、`file`、`stat`）。

## 发布

命令与 DSH 完全相同，见 `harness/dsh.md`「发布」一节（发布器是纯 Python 脚本，与 Harness 无关）。唯一差异：

- OpenCode 通常直接继承终端环境变量，**不需要**覆盖 `HOME`
- 若沙箱限制写 `~/.cache`，按 DSH 的做法把 `HOME` 指到 `$TMPDIR/woaile-gzh-home`

## 已知限制

| 限制 | 采取的降级 |
|---|---|
| 角色必须是文件式 agent | agent 文件写成只含「读 roles/*.md 并执行」的薄壳，规范只维护一份 |
| 内置 `explorer` 只读但不能加载 skill | 需要 skill 的角色一律用自定义 agent |
| 无 OpenCode 侧实测记录 | 首次运行前先用一个短主题走通阶段 3，确认 `task` 续接语义 |