---
name: project-init
description: |
  项目初始化工具，同时支持 OpenCode 和 Pi 两种 AI 编程助手。当用户需要创建新项目、初始化项目、设置项目结构时使用此技能。根据项目需求智能推荐 shared 目录下的 agent 和 skill，自动创建项目目录和对应 harness 配置。触发关键词："初始化项目"、"创建项目"、"新建项目"、"项目初始化"、"设置项目"、"init project"。即使用户未明确提及，但上下文暗示需要开始一个新项目时，也应主动使用。
version: 2.0.0
---

# 项目初始化（OpenCode / Pi）

根据项目需求智能筛选并配置适合的 agent 和 skill，自动创建项目目录结构。同时支持 OpenCode 和 Pi 两种 AI 编程助手。

## 数据源

从 `~/Code/kk-ai/README.md` 读取可用的 shared 资源清单：

- **Skills - Shared** 章节：读取 `skills/shared/` 下的可用 skill
- **Agents - Shared** 章节：读取 `opencode-agents/shared/` 下的可用 agent

解析 README 中的表格，提取名称和说明，作为推荐依据。

## 工作流程

### 1. 收集需求

询问用户：
- **项目名称**：用于创建项目目录
- **项目需求**：项目的功能、技术栈、目标等描述
- **目标 Harness**：OpenCode 还是 Pi？（如果用户未明确指定，使用 ask 工具确认或者直接询问用户）

### 2. 读取资源清单

读取 `~/Code/kk-ai/README.md`，解析以下章节：

```markdown
### Skills - Shared（共享，项目按需链接）

| Skill | 来源 | 说明 |
|-------|------|------|
| `skill-name` | ... | 说明文字 |

### Agents - Shared（共享，项目按需链接）

| Agent | 说明 |
|-------|------|
| `agent-name` | 说明文字 |
```

### 3. 分析与推荐

根据项目需求匹配资源说明中的关键词，推荐规则：

| 项目类型 | 推荐 Skills | 推荐 Agents |
|----------|-------------|-------------|
| 内容创作/知识管理 | ob_* 系列 | Knowledge Co-Creator |
| 产品调研 | xhs-k-search, zhihu-k-search, douban-k-search, research-workflow | ResearchReporter |
| 前端/Web 开发 | frontend-design | - |
| 社交媒体运营 | baoyu-xhs-images, xhs-k-search | - |
| 需要图像素材 | images-k-generation | - |

> **注意**：Agents 仅对 OpenCode 项目推荐。Pi 使用 Prompt Templates 而非 Agents，初始化 Pi 项目时只推荐 Skills。

### 4. 展示计划并确认

向用户展示初始化计划，使用 question 工具让用户勾选确认。展示项目的目录结构和推荐的资源清单。

### 5. 执行初始化

用户确认后，**根据目标 harness 读取对应的参考文件来执行**：

- **OpenCode 项目** → 读取 `references/opencode-init.md`，按其指令执行
- **Pi 项目** → 读取 `references/pi-init.md`，按其指令执行

## 注意事项

1. **数据源唯一**：所有资源信息从 README 读取，避免多处维护
2. **只处理 shared**：common 目录已在全局生效，无需链接
3. **符号链接**：使用 ln -s 便于统一更新
4. **路径验证**：创建前检查目标路径是否已存在
5. **增量添加**：配置目录已存在时增量添加而非覆盖
6. **Git 初始化**：项目初始化后自动执行 git init
7. **Skills 跨 harness 兼容**：OpenCode 和 Pi 的 SKILL.md 格式基于同一标准，符号链接可直接复用
