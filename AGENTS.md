# AGENTS.md

OpenCode Skills & Agents 统一管理仓库开发指南。

## 目录结构

- `skills/common/` - 通用 skills，链接到全局 `~/.config/opencode/skills/`
- `skills/shared/` - 共享 skills，部分已链接到全局，部分按需链接到项目
- `opencode-agents/common/` - OpenCode 通用 agents，链接到全局 `~/.config/opencode/agents/`
- `opencode-agents/shared/` - OpenCode 共享 agents，按需链接到项目
- `pi-agents/common/` - Pi 通用主 agent，链接到全局 `~/.pi/agent/main-agents/`（供 pi-agent-switcher 识别）
- `pi-agents/shared/` - Pi 共享主 agent，按需链接到项目 `.pi/main-agents/`
- `pi-subagents/common/` - Pi 通用子 agent，链接到全局 `~/.pi/agent/agents/`（供 @agwab/pi-subagent 识别）
- `pi-subagents/shared/` - Pi 共享子 agent，按需复制到项目 `.pi/agents/`（注意：pi-subagent 拒绝跨根符号链接，必须复制不能用软链接）
- `pi-extensions/common/` - Pi 通用扩展，链接到全局 `~/.pi/agent/extensions/`
- `pi-extensions/shared/` - Pi 共享扩展，按需链接到项目 `.pi/extensions/`
- `scripts/` - 辅助脚本
- `AGENTS.global.md` - 全局代理规则，链接到 `~/.config/opencode/AGENTS.md` 和 `~/.pi/agent/AGENTS.md`

## 关键命令

```bash
# 链接共享 skill 到指定 OpenCode 项目
~/Code/kk-ai/scripts/link-skills.sh shared <skill-name> /path/to/project

# 链接 OpenCode Agent 到指定项目
~/Code/kk-ai/scripts/link-skills.sh opencode-agent <agent-name> /path/to/project

# 链接 Pi Agent 到指定项目
~/Code/kk-ai/scripts/link-skills.sh pi-agent <agent-name> /path/to/project

# 链接 Pi Subagent 到指定项目
~/Code/kk-ai/scripts/link-skills.sh pi-subagent <agent-name> /path/to/project

# 链接 Pi Extension 到指定项目
~/Code/kk-ai/scripts/link-skills.sh pi-extension <extension-name> /path/to/project

# 更新所有外部 skill（从上游仓库拉取）
~/Code/kk-ai/scripts/update-external-skills.sh
```

## 全局链接

通用 skills/agents/extensions 通过目录级符号链接到全局：

```bash
# 一次性设置（已完成）
ln -s ~/Code/kk-ai/skills/common ~/.config/opencode/skills
ln -s ~/Code/kk-ai/opencode-agents/common ~/.config/opencode/agents
ln -s ~/Code/kk-ai/pi-extensions/common ~/.pi/agent/extensions
```

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
## Pi Agent 迁移

OpenCode `opencode-agents/shared/` 下的 Agent 已迁移为 Pi 格式。Pi 区分两类 agent，读取不同目录，互不干扰：

- **主 agent（primary）** — 主会话角色，由 `pi-agent-switcher` 扩展管理，读取 `~/.pi/agent/main-agents/`（项目级 `.pi/main-agents/`）
- **子 agent（subagent）** — 被 `@agwab/pi-subagent` 委派的子代理，读取 `~/.pi/agent/agents/`（项目级 `.pi/agents/`，且根目录不能是符号链接）

仓库目录对应：

- `pi-agents/common/` → 链接为 `~/.pi/agent/main-agents`（全局主 agent）
- `pi-agents/shared/` → 按需链接到项目 `.pi/main-agents/`（主 agent）
- `pi-subagents/common/` → 链接为 `~/.pi/agent/agents`（全局子 agent）
- `pi-subagents/shared/` → 按需**复制**到项目 `.pi/agents/`（子 agent；pi-subagent 拒绝跨根符号链接，必须复制）

全局目录链接（已完成）：

```bash
ln -s ~/Code/kk-ai/pi-agents/common ~/.pi/agent/main-agents
ln -s ~/Code/kk-ai/pi-subagents/common ~/.pi/agent/agents
```

Pi 重启后生效，使用 `/agents` 查看、`/agent <name>` 切换（主 agent）。

Pi Agent 格式与 OpenCode 的区别：
- 不支持 `mode: subagent`（Pi 无子 agent 概念），改为 primary agent
- 不支持 `permission` 字段，用 `tools` 字段限制工具集
- `temperature` 映射为 `thinking` 级别（off/low/medium/high）

## 新增 Skill/Agent

- 通用 skill/agent 放入 `skills/common/`、`opencode-agents/common/`、`pi-agents/common/` 或 `pi-extensions/common/`，自动生效（全局目录已链接）
- 共享 skill/agent 放入 `skills/shared/`、`opencode-agents/shared/`、`pi-agents/shared/` 或 `pi-extensions/shared/`，按需链接到项目
- Pi agent 分主/子两类，仓库目录分别为 `pi-agents/`（主）和 `pi-subagents/`（子）；主 agent 全局链接到 `~/.pi/agent/main-agents/`，子 agent 全局链接到 `~/.pi/agent/agents/`。新增/修改后必须同步仓库文件；`pi-agents/common` 与 `pi-subagents/common` 已通过目录级符号链接全局生效，无需手动复制
- Pi 扩展新增/修改后，必须同步更新 `pi-extensions/` 和对应的 `~/.pi/agent/extensions/` 或项目 `.pi/extensions/` 中的符号链接

## 完成后自动更新文档

**重要**：新增或修改 Skill/Agent 后，必须在用户确认开发完成后自动执行以下操作：

1. 更新 `README.md` 中的技能列表和描述
2. 更新本文件（`AGENTS.md`）中的相关章节（如有必要）
3. 更新对应的 `upstream.json` 文件中的相关信息（如有必要）

这是强制性步骤，确保文档与实际代码保持同步。

## Python 项目约定

部分 skill（如 `douban-k-search`、`xhs-k-search`、`zhihu-k-search`、`images-k-generation`）包含 Python 脚本：
- 代码放在 `scripts/` 子目录
- 使用 `uv` 作为包管理器
- 详见各 skill 目录下的 `AGENTS.md`

## Node.js 项目约定

部分 skill（如 `html-ppt`）包含 Node.js 脚本：
- 代码放在 `scripts/` 子目录
- 使用 `npm` 作为包管理器
- 首次使用需在 `scripts/` 目录执行 `npm install`
