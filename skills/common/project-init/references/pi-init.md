# Pi 项目初始化执行细节

当用户选择创建 Pi 项目时，按以下步骤执行。

## 目录结构

```
{项目名称}/
├── .pi/
│   └── skills/
```

> **关于 Agents**：Pi 没有 Agent 概念，对应的是 Prompt Templates（`.pi/prompts/`）。如果用户后续需要，可以手动将 Agent 的 `.md` 文件复制到 `.pi/prompts/` 并调整格式（Pi prompt templates 支持 `description` 和 `argument-hint` 字段，文件名即命令名）。

## 执行命令

```bash
# 创建目录
mkdir -p {项目路径}/.pi/skills

# 链接 skills（Pi 使用相同的 SKILL.md 格式，直接符号链接即可）
ln -s ~/Code/opencode-skills/skills/shared/{skill-name} {项目路径}/.pi/skills/

# 初始化 git 仓库
cd {项目路径} && git init

# 创建 .gitignore（见下方规则）
# 提交初始化
cd {项目路径} && git add . && git commit -m "chore: Pi 项目初始化完成"
```

## .gitignore 规则

**基础规则（必须包含）**：
```
# Pi 配置目录（符号链接）
.pi/
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
## 项目初始化计划（Pi）

### 项目目录
{项目名称}/
├── .pi/
│   └── skills/

### 推荐 Skills（来自 README）
- [ ] Skill 1 - 说明
- [ ] Skill 2 - 说明

> 💡 Pi 使用 Prompt Templates 而非 Agents。如需将 Agent 转为 Prompt Template，可在初始化后手动操作。
```

## 输出格式

```
✅ Pi 项目初始化完成！

📁 项目目录：{项目路径}

📦 已配置 Skills：
   - {skill-name}

🚀 下一步：cd {项目路径}
```
