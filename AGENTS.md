# AGENTS.md

OpenCode Skills & Agents 统一管理仓库开发指南。

## 目录结构

- `skills/common/` - 通用 skills，已链接到全局 `~/.config/opencode/skills/`
- `skills/shared/` - 共享 skills，项目按需链接
- `agents/common/` - 通用 agents，已链接到全局 `~/.config/opencode/agents/`
- `agents/shared/` - 共享 agents，项目按需链接
- `scripts/` - 辅助脚本

## 关键命令

```bash
# 链接所有通用 skills/agents 到全局
~/Code/opencode-skills/scripts/link-skills.sh common

# 链接共享 skill 到指定项目
~/Code/opencode-skills/scripts/link-skills.sh shared <skill-name> /path/to/project

# 更新所有外部 skill（从上游仓库拉取）
~/Code/opencode-skills/scripts/update-external-skills.sh
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

## 新增 Skill/Agent

- 通用 skill/agent 放入 `skills/common/` 或 `agents/common/`，然后运行 `scripts/link-skills.sh common`
- 共享 skill/agent 放入 `skills/shared/` 或 `agents/shared/`，按需链接到项目

## Python 项目约定

部分 skill（如 `xhs-k-search`、`zhihu-k-search`、`images-k-generation`）包含 Python 脚本：
- 代码放在 `scripts/` 子目录
- 使用 `uv` 作为包管理器
- 详见各 skill 目录下的 `AGENTS.md`
