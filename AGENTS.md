# AGENTS.md

OpenCode Skills & Agents 统一管理仓库开发指南。

## 目录结构

- `skills/common/` - 通用 skills，链接到全局 `~/.config/opencode/skills/`
- `skills/shared/` - 共享 skills，部分已链接到全局，部分按需链接到项目
- `opencode-agents/common/` - OpenCode 通用 agents，链接到全局 `~/.config/opencode/agents/`
- `opencode-agents/shared/` - OpenCode 共享 agents，按需链接到项目
- `pi-agents/shared/` - Pi 共享 agents（已迁移），手动复制到 `~/.pi/agents/` 使用
- `pi-agents/common/` - Pi 通用 agents（预留）
- `pi-extensions/common/` - Pi 通用扩展，链接到全局 `~/.pi/agent/extensions/`
- `pi-extensions/shared/` - Pi 共享扩展，按需链接到项目 `.pi/extensions/`
- `scripts/` - 辅助脚本
- `AGENTS.global.md` - 全局代理规则，链接到 `~/.config/opencode/AGENTS.md` 和 `~/.pi/agent/AGENTS.md`

## 关键命令

```bash
# 链接共享 skill 到指定 OpenCode 项目
~/Code/opencode-skills/scripts/link-skills.sh shared <skill-name> /path/to/project

# 链接 OpenCode Agent 到指定项目
~/Code/opencode-skills/scripts/link-skills.sh opencode-agent <agent-name> /path/to/project

# 链接 Pi Agent 到指定项目
~/Code/opencode-skills/scripts/link-skills.sh pi-agent <agent-name> /path/to/project

# 链接 Pi Extension 到指定项目
~/Code/opencode-skills/scripts/link-skills.sh pi-extension <extension-name> /path/to/project

# 更新所有外部 skill（从上游仓库拉取）
~/Code/opencode-skills/scripts/update-external-skills.sh
```

## 全局链接

通用 skills/agents/extensions 通过目录级符号链接到全局：

```bash
# 一次性设置（已完成）
ln -s ~/Code/opencode-skills/skills/common ~/.config/opencode/skills
ln -s ~/Code/opencode-skills/opencode-agents/common ~/.config/opencode/agents
ln -s ~/Code/opencode-skills/pi-extensions/common ~/.pi/agent/extensions
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

OpenCode `opencode-agents/shared/` 下的 Agent 已迁移为 Pi 格式，存放在 `pi-agents/shared/` 目录。

迁移到 Pi 使用：

```bash
# 复制到 Pi 全局 agents 目录
cp ~/Code/opencode-skills/pi-agents/shared/*.md ~/.pi/agents/

# Pi 重启后生效，使用 /agents 查看、/agent <name> 切换
```

Pi Agent 格式与 OpenCode 的区别：
- 不支持 `mode: subagent`（Pi 无子 agent 概念），改为 primary agent
- 不支持 `permission` 字段，用 `tools` 字段限制工具集
- `temperature` 映射为 `thinking` 级别（off/low/medium/high）

## 新增 Skill/Agent

- 通用 skill/agent 放入 `skills/common/`、`opencode-agents/common/`、`pi-agents/common/` 或 `pi-extensions/common/`，自动生效（全局目录已链接）
- 共享 skill/agent 放入 `skills/shared/`、`opencode-agents/shared/`、`pi-agents/shared/` 或 `pi-extensions/shared/`，按需链接到项目
- Pi agent 新增/修改后，必须同步更新 `pi-agents/shared/` 和 `~/.pi/agents/` 两处文件
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

部分 skill（如 `markdown-to-image`、`html-ppt`）包含 Node.js 脚本：
- 代码放在 `scripts/` 子目录
- 使用 `npm` 作为包管理器
- 首次使用需在 `scripts/` 目录执行 `npm install`
