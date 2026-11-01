# AGENTS.md

OpenCode Skills & Agents 统一管理仓库开发指南。

## 目录结构

- `skills/common/` - 通用 skills，链接到全局 `~/.config/opencode/skills/`
- `skills/shared/` - 共享 skills，按需链接到项目
- `opencode-agents/common/` - OpenCode 通用 agents，链接到全局 `~/.config/opencode/agents/`
- `opencode-agents/shared/` - OpenCode 共享 agents，按需链接到项目
- `opencode-commands/common/` - OpenCode 通用 commands，链接到全局 `~/.config/opencode/commands/`
- `pi-extensions/common/pi-agent-switcher/`
- `pi-extensions/common/pi-k-subagent/`
- `scripts/` - 辅助脚本
- `AGENTS.global.md` - OpenCode 全局代理规则，链接到 `~/.config/opencode/AGENTS.md`

## 关键命令

```bash
# 链接共享 skill 到指定 OpenCode 项目
~/Code/kk-ai/scripts/link-skills.sh shared <skill-name> /path/to/project

# 链接 OpenCode Agent 到指定项目
~/Code/kk-ai/scripts/link-skills.sh opencode-agent <agent-name> /path/to/project

# 更新所有外部 skill（从上游仓库拉取）
~/Code/kk-ai/scripts/update-external-skills.sh

# 多 harness 项目初始化（建目录 + 链接 skill/agent + 指令文件 + .gitignore + git init）
~/Code/kk-ai/skills/common/project-init/scripts/init.sh list
~/Code/kk-ai/skills/common/project-init/scripts/init.sh plan <项目> --harness dsh,opencode --skill <skill>
~/Code/kk-ai/skills/common/project-init/scripts/init.sh init <项目> --harness dsh,opencode --skill <skill>
```

## 全局链接

通用 skills/agents/commands 通过目录级符号链接到全局：

```bash
# 一次性设置（已完成）
ln -s ~/Code/kk-ai/skills/common ~/.config/opencode/skills
ln -s ~/Code/kk-ai/opencode-agents/common ~/.config/opencode/agents
ln -s ~/Code/kk-ai/opencode-commands/common ~/.config/opencode/commands

# DSH（DeepSeek Harness）：同样目录级链接，新增 common skill 自动可见
ln -s ~/Code/kk-ai/skills/common ~/.dsh/skills
```

DSH 的全局规则文件（可选，尚未建立）：`ln -sf ~/Code/kk-ai/AGENTS.global.md ~/.dsh/AGENTS.md`

其他 harness 的全局位置（DSH：`~/.dsh/skills`、`~/.dsh/AGENTS.md`；Claude Code：`~/.claude/...`；
Codex/Gemini CLI/Cursor：`~/.agents/...`）见
`skills/common/project-init/references/harnesses.md`。

## Skill 结构规范

每个 skill 目录必须包含：
- `SKILL.md` - Skill 定义文件（必需）
- `upstream.json` - 上游信息（外部 skill 必需，自开发 skill 填 `"source": "self-developed"`）

## 外部 Skill 更新流程

外部 skill 在 `~/Code/GitHub-Skills/` 目录追踪上游仓库。更新流程：
1. `update-external-skills.sh` 从追踪目录 `git pull`
2. 拷贝文件到本仓库对应 skill 目录
3. 更新 `upstream.json` 中的 `last_update`
4. 手动检查并提交变更

## 新增 Skill/Agent/Command

- 通用 skill/agent/command 放入 `skills/common/`、`opencode-agents/common/` 或 `opencode-commands/common/`，自动生效（全局目录已链接）
- 共享 skill/agent 放入 `skills/shared/` 或 `opencode-agents/shared/`，按需链接到项目
- **跨 harness 支持**：harness 差异只登记在 `skills/common/project-init/scripts/init.sh` 的
  `harness_spec()` 与 `skills/common/project-init/references/harnesses.md`；新增 harness 时两处同步，
  并在真机验证后把该文档的「验证状态」改为 ✅

## 完成后自动更新文档

**重要**：新增或修改 Skill/Agent 后，必须在用户确认开发完成后自动执行以下操作：

1. 更新 `README.md` 中的技能列表和描述
2. 更新本文件（`AGENTS.md`）中的相关章节（如有必要）
3. 更新对应的 `upstream.json` 文件中的相关信息（如有必要）

这是强制性步骤，确保文档与实际代码保持同步。

## Python 项目约定

部分 skill（如 `woaile-gzh-publisher`）包含 Python 脚本：
- 代码放在 `scripts/` 子目录
- 使用 `uv` 作为包管理器
- 详见各 skill 目录下的 `AGENTS.md`
