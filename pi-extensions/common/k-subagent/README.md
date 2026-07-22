# k-subagent

Pi 编码代理的子代理（subagent）扩展。允许主 Agent 将复杂、隔离的任务委托给独立的子代理进程执行，每个子代理拥有独立的上下文窗口。

## 功能

- **子代理定义**：通过 Markdown 文件（YAML frontmatter + 系统提示词正文）定义子代理
- **双模式执行**：单任务模式（`agent` + `task`）和并行模式（`tasks[]` 数组）
- **头less 进程隔离**：每个子代理运行在独立的 `pi` 进程中，上下文完全隔离
- **产出物约定**：简单任务直接回答；大型交付物写入报告文件，返回摘要 + 文件路径
- **TUI 深度集成**：`Ctrl+O` 展开查看完整执行记录；`/subagents` 命令浏览所有运行记录
- **实时进度**：支持流式更新，并行任务实时显示各子代理进度

## 安装

```bash
npm install pi-k-subagent
```

或作为 Pi 扩展链接到全局：

```bash
# 放入 ~/.pi/agent/extensions/k-subagent/
# Pi 启动时自动加载
```

## 子代理定义

子代理定义为 Markdown 文件，存放在：

| 范围 | 路径 |
|------|------|
| 全局 | `~/.pi/agent/k-subagents/` |
| 项目 | `.pi/k-subagents/` |

### 文件格式

```markdown
---
name: my-agent
description: 执行 X 和 Y 任务
model: anthropic/claude-sonnet-4-5
tools: read,bash,grep,find
thinking: medium
---

你的系统提示词正文…
```

### Frontmatter 字段

| 字段 | 必需 | 说明 |
|------|------|------|
| `name` | 是 | 唯一标识符 |
| `description` | 是 | 描述，显示给 LLM 和用户 |
| `model` | 否 | 模型覆盖（provider/model 格式） |
| `tools` | 否 | 工具允许列表（逗号分隔），默认 `read,bash,grep,find,ls,edit,write` |
| `thinking` | 否 | 思考级别：`off` / `minimal` / `low` / `medium` / `high` / `xhigh` |
| `systemPromptMode` | 否 | `"append"`（默认，追加到输出约定后）或 `"replace"` |

嵌套目录会生成点号分隔的名称，例如 `coding/review.md` → `coding.review`。

## 使用方式

主 Agent 通过 `subagent` 工具调用子代理：

```json
// 单任务模式
{
  "agent": "my-agent",
  "task": "分析这个项目的代码结构"
}

// 并行模式
{
  "tasks": [
    { "agent": "researcher", "task": "调研 X" },
    { "agent": "reviewer", "task": "审查 Y" }
  ],
  "concurrency": 4
}
```

### 参数

| 参数 | 说明 |
|------|------|
| `agent` | 子代理名称（单任务模式） |
| `task` | 委托任务描述（单任务模式） |
| `tasks` | 并行任务数组 `[{agent, task, cwd?}]` |
| `agentScope` | 代理发现范围：`"global"` / `"project"` / `"both"`（默认） |
| `cwd` | 工作目录覆盖 |
| `concurrency` | 并行上限（默认 4，最大 8） |
| `failFast` | 首个失败后停止调度 |
| `cancelSiblingsOnFailure` | 首个失败后取消正在运行的任务 |
| `async` | 异步执行，立即返回 |
| `onComplete` | 异步完成动作：`"return"` / `"notify"` / `"detach"` |
| `timeoutMs` | 超时时间（毫秒） |

### 生命周期操作

| action | 说明 |
|--------|------|
| `run` | 默认，执行任务 |
| `status` | 查询异步任务状态 |
| `wait` | 等待异步任务完成并返回结果 |
| `interrupt` | 中断异步任务 |

### 子代理产出约定

每个子代理遵循以下约定：

1. **简单答案**：直接作为最终消息返回
2. **大型交付物**：写入临时目录（`/tmp/k-subagent/<runId>-<agent>/`）的报告文件，最终消息返回摘要 + 文件路径

主 Agent 可根据摘要决定是否需要读取完整报告。

## 运行记录

每次子代理运行都会在 `/tmp/k-subagent/` 下生成：

```
/tmp/k-subagent/<runId>-<agent>/
├── transcript.md   # 完整执行记录（Markdown）
└── messages.json   # 原始消息数组（JSON）
```

## TUI 交互

- **`Ctrl+O`**：在工具结果上展开，查看子代理的完整执行过程
- **`/subagents`**：打开交互式浏览器，可点击进入任意历史运行记录查看完整转录

## 许可证

MIT
