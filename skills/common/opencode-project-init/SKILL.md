---
name: opencode-project-init
description: |
  OpenCode 项目初始化工具。当用户需要创建新项目、初始化项目、设置项目结构时使用此技能。根据项目需求智能推荐 shared 目录下的 agent 和 skill，并自动创建项目目录和 .opencode 配置。触发关键词："初始化项目"、"创建项目"、"新建项目"、"项目初始化"、"设置项目"、"init project"。即使用户未明确提及，但上下文暗示需要开始一个新项目时，也应主动使用。
version: 1.1.0
---

# OpenCode 项目初始化

根据项目需求智能筛选并配置适合的 agent 和 skill，自动创建项目目录结构。

## 数据源

从 `~/Code/opencode-skills/README.md` 读取可用的 shared 资源清单：

- **Skills - Shared** 章节：读取 `skills/shared/` 下的可用 skill
- **Agents - Shared** 章节：读取 `agents/shared/` 下的可用 agent

解析 README 中的表格，提取名称和说明，作为推荐依据。

## 工作流程

### 1. 收集需求

询问用户：
- **项目名称**：用于创建项目目录
- **项目需求**：项目的功能、技术栈、目标等描述

### 2. 读取资源清单

读取 `~/Code/opencode-skills/README.md`，解析以下章节：

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
| 产品调研 | xhs-k-search, zhihu-k-search, douban-k-search | ProductResearch |
| 前端/Web 开发 | frontend-design | - |
| 社交媒体运营 | baoyu-xhs-images, xhs-k-search | - |
| 需要图像素材 | images-k-generation | - |

### 4. 展示计划

向用户展示初始化计划，使用 question 工具让用户勾选确认：

```
## 项目初始化计划

### 项目目录
{项目名称}/
├── .opencode/
│   ├── agents/
│   └── skills/

### 推荐 Agents（来自 README）
- [ ] Agent 1 - 说明
- [ ] Agent 2 - 说明

### 推荐 Skills（来自 README）
- [ ] Skill 1 - 说明
- [ ] Skill 2 - 说明
```

### 5. 执行初始化

用户确认后执行：

```bash
# 创建目录
mkdir -p {项目路径}/.opencode/agents
mkdir -p {项目路径}/.opencode/skills

# 链接 agents
ln -s ~/Code/opencode-skills/agents/shared/{agent-name}.md {项目路径}/.opencode/agents/

# 链接 skills
ln -s ~/Code/opencode-skills/skills/shared/{skill-name} {项目路径}/.opencode/skills/

# 初始化 git 仓库
cd {项目路径} && git init

# 创建 .gitignore 文件
# 根据项目类型生成相应的 .gitignore，必须包含：
# - .opencode/ （链接目录不需要纳入版本控制）
# - 其他根据项目技术栈的忽略规则

# 提交初始化
cd {项目路径} && git add . && git commit -m "chore: OpenCode 项目初始化完成"
```

### 6. 生成 .gitignore

根据项目类型智能生成 `.gitignore` 文件：

**基础规则（所有项目必须包含）**：
```
# OpenCode 配置目录（符号链接）
.opencode/
```

**根据项目类型追加规则**：

| 项目类型 | 追加规则 |
|----------|----------|
| Node.js | `node_modules/`, `dist/`, `.env`, `*.log` |
| Python | `__pycache__/`, `*.pyc`, `.venv/`, `.env` |
| Go | `*.exe`, `*.test`, `vendor/` |
| Rust | `target/`, `Cargo.lock` |
| Java | `*.class`, `*.jar`, `target/` |
| 通用 | `.DS_Store`, `.idea/`, `.vscode/` |

### 7. 完成提交

初始化完成后，自动创建首次提交：

```bash
git commit -m "chore: OpenCode 项目初始化完成"
```

## 输出格式

```
✅ 项目初始化完成！

📁 项目目录：{项目路径}

📦 已配置 Agents：
   - {agent-name}

📦 已配置 Skills：
   - {skill-name}

🚀 下一步：cd {项目路径}
```

## 注意事项

1. **数据源唯一**：所有资源信息从 README 读取，避免多处维护
2. **只处理 shared**：common 目录已在全局生效，无需链接
3. **符号链接**：使用 ln -s 便于统一更新
4. **路径验证**：创建前检查目标路径是否已存在
5. **增量添加**：.opencode 已存在时增量添加而非覆盖
6. **Git 初始化**：项目初始化后自动执行 git init
7. **.gitignore**：必须包含 `.opencode/` 目录，链接配置不纳入版本控制
8. **首次提交**：初始化完成后自动创建 git commit
