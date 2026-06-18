# OpenCode 项目初始化执行细节

当用户选择创建 OpenCode 项目时，按以下步骤执行。

## 目录结构

```
{项目名称}/
├── .opencode/
│   ├── agents/
│   └── skills/
```

## 执行命令

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

# 创建 .gitignore（见下方规则）
# 提交初始化
cd {项目路径} && git add . && git commit -m "chore: OpenCode 项目初始化完成"
```

## .gitignore 规则

**基础规则（必须包含）**：
```
# OpenCode 配置目录（符号链接）
.opencode/
```

**根据项目类型追加**：

| 项目类型 | 追加规则 |
|----------|----------|
| Node.js | `node_modules/`, `dist/`, `.env`, `*.log` |
| Python | `__pycache__/`, `*.pyc`, `.venv/`, `.env` |
| Go | `*.exe`, `*.test`, `vendor/` |
| Rust | `target/`, `Cargo.lock` |
| Java | `*.class`, `*.jar`, `target/` |
| 通用 | `.DS_Store`, `.idea/`, `.vscode/` |

## 展示计划模板

```
## 项目初始化计划（OpenCode）

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

## 输出格式

```
✅ OpenCode 项目初始化完成！

📁 项目目录：{项目路径}

📦 已配置 Agents：
   - {agent-name}

📦 已配置 Skills：
   - {skill-name}

🚀 下一步：cd {项目路径}
```
