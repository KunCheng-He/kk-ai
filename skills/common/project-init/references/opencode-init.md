# OpenCode 初始化细节

OpenCode 是 kk-ai 仓库的原生目标，约定最完整：skill、agent、command 三类资源都有项目级目录。

## 目录结构

```
{项目}/
├── .opencode/
│   ├── agents/          # subagent 定义（markdown + frontmatter）
│   ├── skills/          # 每个 skill 一个子目录（含 SKILL.md）
│   └── commands/        # 自定义命令（本 skill 不自动链接，按需手动）
└── AGENTS.md            # 项目规则 + project-init 受管区块（skill/agent 清单）
```

## 用脚本执行（推荐）

```bash
~/Code/kk-ai/skills/common/project-init/scripts/init.sh plan  ~/Code/my-proj \
  --harness opencode --skill research-workflow --agent ResearchReporter --type node

~/Code/kk-ai/skills/common/project-init/scripts/init.sh init  ~/Code/my-proj \
  --harness opencode --skill research-workflow --agent ResearchReporter --type node
```

脚本做到：建目录 → 链接 skill/agent → 写 `AGENTS.md` 受管区块 → 更新 `.gitignore` → `git init` + 初始提交。

## 手动等价命令

```bash
mkdir -p {项目}/.opencode/{agents,skills}

# skill：链接整个目录（common 已全局生效，这里通常是 shared）
ln -s ~/Code/kk-ai/skills/shared/{skill-name} {项目}/.opencode/skills/{skill-name}

# agent：链接单个 .md 文件
ln -s ~/Code/kk-ai/opencode-agents/shared/{agent-name}.md {项目}/.opencode/agents/{agent-name}.md

# command（按需）
ln -s ~/Code/kk-ai/opencode-commands/common/{cmd}.md {项目}/.opencode/commands/{cmd}.md

cd {项目} && git init
```

> 也可以用 `~/Code/kk-ai/scripts/link-skills.sh shared <skill> <项目>` 单条链接；
> 但多 harness、指令文件清单、`.gitignore`、git 初始化这些动作只有 `init.sh` 会一并处理。

## skill 与 agent 的位置约定

| 资源 | 源目录 | 说明 |
|---|---|---|
| skill（按需） | `skills/shared/<name>/` | 项目级链接的主力 |
| skill（通用） | `skills/common/<name>/` | 已通过 `~/.config/opencode/skills` 全局生效，**一般不需要**再链接 |
| agent | `opencode-agents/shared/<name>.md` | 仅 opencode / claude-code 可链接 |
| command | `opencode-commands/common/<name>.md` | 全局已生效 |

## `.gitignore`

只忽略链接目录，`AGENTS.md` 要入库：

```gitignore
.opencode/skills/
.opencode/agents/
```

旧版 `project-init` 直接忽略整个 `.opencode/`，会把同目录下真实的 `opencode.json`、`plugin/` 等一并排除，
故改成只忽略符号链接目录。模板总表见 [gitignore.md](gitignore.md)。

## 校验

```bash
ls -l {项目}/.opencode/skills {项目}/.opencode/agents
cat {项目}/AGENTS.md
git -C {项目} log --oneline | head -3
```

在 OpenCode 中打开项目，确认：
- skill 出现在可用列表里（能在需要时被调用）
- agent 可在 subagent 选择器中出现（`@agent-name`）
