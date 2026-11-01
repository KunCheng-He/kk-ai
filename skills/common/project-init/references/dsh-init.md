# DSH（DeepSeek Harness）初始化细节

本文约定来自 DSH 自身实现（`dsh-skill` / `dsh-skill-filesystem` / `dsh-agent-instructions` 包文档与源码），
已在本机 DSH 会话中实测。

## Skill 发现根与优先级

DSH 按 rank 顺序扫描以下根，**数字小的优先**（同名 skill 先命中者生效）：

| Rank | 来源 | 路径 |
|---|---|---|
| 100 | `project-dsh` | `<projectRoot>/.dsh/skills` |
| 200 | `project-agents` | `<projectRoot>/.agents/skills` |
| 300 | `custom` | `Config.customSkillDirs` |
| 400 | `user-dsh` | `$DSH_HOME/skills`（默认 `~/.dsh/skills`） |
| 500 | `user-agents` | `$DSH_AGENTS_HOME/skills`（默认 `~/.agents/skills`） |
| 600 | `bundled` | 内置 skill 目录（如 `office*`，随安装包分发） |

关键点：

- **projectRoot = 最近一个含 `.git` 的祖先目录**；没有 `.git` 就退化为当前工作目录。
  → 所以 `project-init` 默认执行 `git init`：否则 `.dsh/skills` 可能不在 DSH 认定的项目根下。
- `user-dsh` 根会跳过其 `.system` 子目录。
- 目录下每个 skill 一个子目录，含 `SKILL.md`（agent-skills 约定，frontmatter 至少 `name` + `description`）。

## Agent：没有文件式定义

DSH 的 subagent 是运行时服务（`ctx.agents`），**不扫描 `.dsh/agents`**。
因此：

- `opencode-agents/shared/*.md` 无法链接给 DSH
- 目标 harness 只有 DSH 时，把 agent 职责改写为 skill（推荐），或写进 `AGENTS.md` 清单由主 agent 参照执行

## 指令文件（AGENTS.md）链

DSH 首个请求会注入一条持久基线消息，顺序为：

1. 用户级：`$DSH_HOME/AGENTS.md` → `<agentsHome>/AGENTS.md`
2. 项目级：从项目根到会话工作目录，逐层加载已存在的 `AGENTS.md` / `CLAUDE.md`（broad → specific）

细节：

- `CLAUDE.md` 与同名 `AGENTS.md` 内容重复时只渲染一次
- 不是实时监听：只有成功执行 `read` / `write` / `edit` 后，更深层的指令文件才会在下一个请求中出现
- 所以"刚写好的 AGENTS.md 立刻生效"不成立；换一个请求轮次即可

## 初始化命令

```bash
~/Code/kk-ai/skills/common/project-init/scripts/init.sh plan  ~/Code/my-proj \
  --harness dsh --skill research-workflow --type python      # 先预览

~/Code/kk-ai/skills/common/project-init/scripts/init.sh init  ~/Code/my-proj \
  --harness dsh --skill research-workflow --type python
```

产物：

```
my-proj/
├── .git/                     # 必需：DSH 用它判定项目根
├── .dsh/skills/<skill>       # → ~/Code/kk-ai/skills/{shared,common}/<skill>
├── AGENTS.md                 # 含 project-init 受管区块（skill 清单）
└── .gitignore                # 忽略 .dsh/skills/
```

## 验证

```bash
ls -l ~/Code/my-proj/.dsh/skills                 # 链接应可解析到 kk-ai
test -d ~/Code/my-proj/.git && echo "git ok"      # DSH 项目根判定
```

然后在 DSH 中打开该项目，让 agent 列出可用 skill（或直接请求使用某个 skill）确认发现成功。

## 全局（用户级）配置

让 `skills/common` 与全局规则对**所有** DSH 项目生效：

```bash
# 目录级链接：目标位置需先不存在
mv ~/.dsh/skills ~/.dsh/skills.bak          # 现存真实目录（内含 mermaid 单链接）
ln -s ~/Code/kk-ai/skills/common ~/.dsh/skills

# 全局代理规则
ln -sf ~/Code/kk-ai/AGENTS.global.md ~/.dsh/AGENTS.md
```

`ln -s` 目录级链接一旦建立，新增 `common` skill 自动可见，无需再动 DSH 配置。

## 常见问题

| 现象 | 原因与处理 |
|---|---|
| 项目里的 skill 不出现 | 项目不是 git 仓库 → DSH 把 cwd 当项目根；`git init` 后重启会话 |
| 两个同名 skill 都装了 | 按 rank 取最小者：`.dsh/skills` > `.agents/skills` > 自定义 > 用户级 |
| 改了 AGENTS.md 没生效 | DSH 不监听外部编辑；触发一次文件读写或换一轮请求 |
| agent 没链接上 | DSH 无文件式 agent，属预期行为 |
