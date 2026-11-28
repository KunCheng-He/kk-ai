# DSH（DeepSeek Harness）初始化细节

本文的事实来自 DSH 自身实现（`dsh-skill` / `dsh-skill-filesystem` / `dsh-agent-instructions` 包），
并已在本机 DSH 会话中实测。

**注**：仓库当前没有 `dsh/harness_meta.json`，所以 `init.sh --harness dsh` 会报未知 harness。
需要给 DSH 项目做自动初始化时，按 [repository.md](repository.md) 新建 `dsh/harness_meta.json`（内容见文末），脚本即可用。

## Skill 发现根与优先级

DSH 按 rank 顺序扫描以下根，**数字小的优先**（同名 skill 先命中者生效）：

| Rank | 来源 | 路径 |
|---|---|---|
| 100 | `project-dsh` | `<项目根>/.dsh/skills` |
| 200 | `project-agents` | `<项目根>/.agents/skills` |
| 300 | `custom` | `Config.customSkillDirs` |
| 400 | `user-dsh` | `$DSH_HOME/skills`（默认 `~/.dsh/skills`） |
| 500 | `user-agents` | `$DSH_AGENTS_HOME/skills`（默认 `~/.agents/skills`） |
| 600 | `bundled` | 内置 skill（如 `office*`），随安装包分发 |

关键点：

- **项目根 = 最近一个含 `.git` 的祖先目录**；没有 `.git` 就退化为当前工作目录
  → 所以 DSH 项目务必是 git 仓库，否则 `.dsh/skills` 可能不在 DSH 认定的项目根下
- 目录下每个 skill 一个子目录，含 `SKILL.md`（frontmatter 至少 `name` + `description`）
- 只扫描一层：`<root>/<name>/SKILL.md` 或扁平的 `<root>/<name>.md`

## 没有文件式 agent

DSH 的 subagent 是运行时服务（`ctx.agents`），**不扫描 `.dsh/agents`**。因此：

- `<harness>/agents/*.md` 无法真正在 DSH 里注册成 agent
- 只有 DSH 时，二选一：
  1. 把职责改写成 skill（推荐，可复用）
  2. 写进 `AGENTS.md` 的清单，由主 agent 参照执行

## 指令文件链

第一个请求会注入一条持久基线消息，顺序为：

1. 用户级：`$DSH_HOME/AGENTS.md` → `<agentsHome>/AGENTS.md`
2. 项目级：从项目根到会话工作目录，逐层加载已存在的 `AGENTS.md` / `CLAUDE.md`（broad → specific）

- `CLAUDE.md` 与同名 `AGENTS.md` 内容重复时只渲染一次
- **不是实时监听**：只有成功执行 `read` / `write` / `edit` 后，更深层的指令文件才会在下一个请求出现
- 所以"刚写好的 AGENTS.md 立刻生效"不成立，换一轮请求即可

## 手动初始化（脚本支持前的做法）

```bash
mkdir -p ~/Code/my-proj/.dsh/skills
ln -s ~/Code/kk-ai/skills/research-workflow ~/Code/my-proj/.dsh/skills/research-workflow
cd ~/Code/my-proj && git init          # 必需：DSH 用它判定项目根
```

产物：

```
my-proj/
├── .git/                     # 必需
├── .dsh/skills/<skill>       # → ~/Code/kk-ai/skills/<skill>
├── AGENTS.md                 # 可手写 skill 清单
└── .gitignore                # 忽略 .dsh/skills/
```

## 加上 harness 声明后

在仓库根建 `dsh/harness_meta.json`：

```json
{
  "label": "DeepSeek Harness",
  "skills_dir": ".dsh/skills",
  "skills_verified": true,
  "agents": [],
  "instructions": "AGENTS.md",
  "instructions_mode": "block",
  "status": "skill 与指令文件来自 DSH 源码 + 本机实测；无文件式 agent"
}
```

之后即可：

```bash
./scripts/init.sh plan ~/Code/my-proj --harness dsh --skill research-workflow --type python
./scripts/init.sh init ~/Code/my-proj --harness dsh --skill research-workflow --type python
```

`init.sh` 会在 `--no-git` 与项目不是 git 仓库时告警，因为这会破坏 DSH 的项目根判定。

## 验证

```bash
ls -l ~/Code/my-proj/.dsh/skills                 # 链接应可解析到 kk-ai
test -d ~/Code/my-proj/.git && echo "git ok"      # DSH 项目根判定
```

然后在 DSH 里打开该项目，让 agent 列出可用 skill（或直接请求使用某个 skill）确认发现成功。

## 常见问题

| 现象 | 原因与处理 |
|---|---|
| 项目里的 skill 不出现 | 项目不是 git 仓库 → DSH 把 cwd 当项目根；`git init` 后重启会话 |
| 两个同名 skill 都装了 | 按 rank 取最小者：`.dsh/skills` > `.agents/skills` > 自定义 > 用户级 |
| 改了 AGENTS.md 没生效 | DSH 不监听外部编辑；触发一次文件读写或换一轮请求 |
| agent 没链接上 | DSH 无文件式 agent，属预期行为 |