# pi-agent-switcher

Pi 扩展：通过 Markdown 定义的 Agent 文件，在主会话中手动切换 Agent 角色。

每个 Agent 拥有独立的系统提示词、工具集、模型和思考级别。Agent 定义为简单的 Markdown 文件 + YAML frontmatter。

## 功能特性

- **Markdown 定义 Agent** — 用 `.md` 文件 + YAML frontmatter 定义 Agent 角色
- **两级作用域** — 全局 Agent（`~/.pi/agent/main-agents/`）和项目 Agent（`.pi/main-agents/`）
- **项目覆盖全局** — 同名项目 Agent 优先于全局 Agent
- **与 subagent 分离** — 本扩展只管主会话角色（primary agent），读取 `main-agents/`；`~/.pi/agent/agents/` 留给 [@agwab/pi-subagent](https://github.com/AgwaB/pi-subagent) 等子代理运行时独占，互不干扰
- **系统提示词切换** — Agent 身份前置，Pi 内置上下文包裹在 `<environment_context>` 中
- **工具集切换** — 按 Agent 限制可用工具
- **模型切换** — 按 Agent 切换模型/提供商（如 `anthropic/claude-sonnet-4-20250514`）
- **思考级别切换** — 按 Agent 设置思考级别（`off` / `low` / `medium` / `high`）
- **会话持久化** — Agent 状态在会话分支间持久保存
- **交互式选择器 UI** — 搜索、导航、数字快捷选择

## 安装

```bash
pi install npm:pi-agent-switcher
```

## 使用方式

### 命令

| 命令            | 说明                    |
| --------------- | ----------------------- |
| `/agent <name>` | 切换到指定 Agent        |
| `/agent`        | 打开交互式 Agent 选择器 |
| `/agent reset`  | 重置为 Pi 默认行为      |
| `/agents`       | 列出所有可用 Agent      |

### 快捷键

| 按键    | 动作                    |
| ------- | ----------------------- |
| `Alt+A` | 打开交互式 Agent 选择器 |

### 交互式选择器

选择器 UI 支持：

- **↑↓ 方向键** — 列表导航
- **1-9 数字键** — 快捷选择
- **Enter** — 确认选择
- **Esc** — 取消
- **输入过滤** — 按名称/描述模糊搜索

## 定义 Agent

在以下目录创建 `.md` 文件：

- **全局 Agent**：`~/.pi/agent/main-agents/` — 所有项目可用
- **项目 Agent**：`.pi/main-agents/` — 仅当前项目可用

### Agent 文件格式

```markdown
---
name: my-agent
description: 简短描述此 Agent 的职责
tools: read,write,bash,edit
model: anthropic/claude-sonnet-4-20250514
thinking: medium
---

你是一个专注于 [特定任务] 的专业 Agent。

你的职责：

- ...
- ...

规范：

- ...
```

### Frontmatter 字段

| 字段          | 必需 | 说明                                                                       |
| ------------- | ---- | -------------------------------------------------------------------------- |
| `name`        | ✅   | Agent 唯一标识（用于 `/agent <name>`）                                     |
| `description` | ✅   | 简短描述，显示在 Agent 列表中                                              |
| `tools`       | ❌   | 逗号分隔的允许工具列表（如 `read,write,bash,edit`）                        |
| `model`       | ❌   | 模型，格式为 `provider/modelId`（如 `anthropic/claude-sonnet-4-20250514`） |
| `thinking`    | ❌   | 思考级别：`off`、`low`、`medium`、`high`                                   |

Markdown 正文（frontmatter 之后的内容）即为 Agent 的系统提示词。

### 示例 Agent

**代码审查员**（`~/.pi/agent/main-agents/code-reviewer.md`）：

```markdown
---
name: code-reviewer
description: 专注于代码审查和质量
tools: read,bash
thinking: high
---

你是一位资深代码审查员。关注以下方面：

- 代码正确性与边界情况
- 性能影响
- 安全漏洞
- 可读性与可维护性

始终提供可操作的建议和具体代码示例。
```

**前端开发**（`.pi/main-agents/frontend.md`）：

```markdown
---
name: frontend
description: 前端专家，精通 React/Vue
model: anthropic/claude-sonnet-4-20250514
tools: read,write,bash,edit
---

你是一位前端开发专家，精通 React、Vue 和现代 CSS。
偏好组件化架构，遵循无障碍最佳实践。
```

## 工作原理

当 Agent 激活时，扩展通过 `before_agent_start` 事件修改 Pi 的行为：

1. **系统提示词**：Agent 的系统提示词前置（高注意力位置），Pi 内置上下文包裹在 `<environment_context>` 标签中
2. **工具**：若 Agent 定义了 `tools` 列表，则仅启用这些工具
3. **模型**：若 Agent 定义了 `model`，Pi 切换到该模型
4. **思考级别**：若 Agent 定义了 `thinking`，Pi 使用该思考配置

会话启动时，扩展从会话历史中恢复上次激活的 Agent。

## 调试

如果想查看 Agent 切换后最终拼装出的完整系统提示词（Agent 身份 + `<environment_context>`），可以使用 [pi-message-capture](https://github.com/KunCheng-He/pi-message-capture)，它能捕获并展示每次发送给模型的完整消息内容。

## 许可证

MIT
