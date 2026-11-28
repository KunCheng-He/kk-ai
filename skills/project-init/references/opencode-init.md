# OpenCode 初始化细节

OpenCode 是仓库里约定最完整的目标：skill、agent、command 三类资源都有项目级目录，
OpenCode 的目录约定已在注册表里核实（`h_skills_verified: true`），脚本可直接初始化。

## 目录结构

```
{项目}/
├── .opencode/
│   ├── skills/          # 每个 skill 一个子目录（含 SKILL.md）→ kk-ai/skills/<name> 或 kk-ai/opencode/skills/<name>
│   ├── agents/          # → kk-ai/opencode/agents/<name>.md
│   └── commands/        # → kk-ai/opencode/cmds/<name>.md（脚本不自动链接）
├── AGENTS.md            # 项目规则 + project-init 受管区块
└── .gitignore           # 只忽略 links 目录
```

## 用脚本初始化（推荐）

```bash
# 先看仓库和项目现状
./scripts/init.sh index
./scripts/init.sh discover ~/Code/my-proj

# 预览
./scripts/init.sh plan ~/Code/my-proj \
  --harness opencode --skill research-workflow --agent 诸葛亮 --type node

# 执行
./scripts/init.sh init ~/Code/my-proj \
  --harness opencode --skill research-workflow --agent 诸葛亮 --type node
```

脚本依次做：预检 → 建目录 → 链接 skill/agent → 写 `AGENTS.md` 受管区块 → 更新 `.gitignore` → `git init` + 初始提交。

## 手动等价命令

```bash
mkdir -p {项目}/.opencode/{skills,agents}

# 通用 skill
ln -s ~/Code/kk-ai/skills/{skill-name}          {项目}/.opencode/skills/{skill-name}

# OpenCode 专属 skill
ln -s ~/Code/kk-ai/opencode/skills/{skill-name} {项目}/.opencode/skills/{skill-name}

# agent：链接单个 .md 文件
ln -s ~/Code/kk-ai/opencode/agents/{agent}.md   {项目}/.opencode/agents/{agent}.md

# command（按需手动）
ln -s ~/Code/kk-ai/opencode/cmds/{cmd}.md       {项目}/.opencode/commands/{cmd}.md
```

## 资源位置对照

| 资源 | 仓库位置 | 参数写法 |
|---|---|---|
| 通用 skill | `skills/<name>/` | `--skill <name>` |
| OpenCode 专属 skill | `opencode/skills/<name>/` | `--skill opencode/<name>` |
| agent | `opencode/agents/<name>.md` | `--agent <name>` 或 `--agent opencode/<name>.md` |
| command | `opencode/cmds/<name>.md` | `--command <name>`（只写清单，手动链接） |

**通用 skill 与专属 skill 的区别**：通用的一拷就能用；专属的用到 OpenCode 的目录约定或前端字段（例如 `loop-by-herdr` 需要运行在 `HERDR_ENV=1` 的 herdr 会话里，且按 OpenCode 的 skill 布局维护），链到别的工具里即使被读到也可能不工作。

## `.gitignore`

只忽略链接目录，`AGENTS.md` 要入库：

```gitignore
.opencode/skills/
.opencode/agents/
```

旧版 `project-init` 直接忽略整个 `.opencode/`，会把同目录下真实的 `opencode.json`、`plugin/` 也排除掉。
模板总表见 [gitignore.md](gitignore.md)。

## 校验

```bash
./scripts/init.sh discover {项目}            # 列出所有链接及其指向
cat {项目}/AGENTS.md                          # 只有一份受管区块
git -C {项目} log --oneline | head -3
```

在 OpenCode 中打开项目，确认：

- skill 出现在可用列表里（需要时能被调用）
- agent 可从 subagent 选择器调用（`@agent-name`）

## 注意

- `--force` 只重建**链接**；如果目标位置是你手动放的真实 agent 文件，脚本不会碰它，需要自己决定怎么处理冲突
- OpenCode 能原生读 `.opencode/agents/`，所以同一个 agent 文件也可以链到 `.claude/agents/` 给 Claude Code 用；但字段（`mode`、`temperature`、`permission`）各工具支持程度不同，跨用时看一眼