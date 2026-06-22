---
name: pi-agent-creator
description: |
  创建 Pi 主 Agent 定义文件，供 pi-agent-switcher 扩展使用。
  当用户需要创建新的 agent 角色、定义 agent、制作 agent、新增 agent、写 agent，
  或提到 "创建一个 agent"、"定义 agent 角色"、"新增角色" 时触发。
  也应在用户表示想为 pi 添加特定工作模式/身份时主动使用。
---

# Pi Agent Creator

为 [pi-agent-switcher](https://github.com/earendil-works/pi-coding-agent) 创建 Agent 定义文件。
Agent 定义是带 YAML 前置元数据的 Markdown 文件，定义了一个角色的系统提示词、工具集、模型和思考级别。

## Agent 文件格式

每个 Agent 是一个 `.md` 文件，包含：

```markdown
---
name: agent-name
description: 简要描述
tools: read, write, edit, bash
model: provider/model-id
thinking: high
---

系统提示词的正文，用 Markdown 编写。
这部分会成为 agent 的核心身份定义。
```

### 前置元数据字段

| 字段 | 必需 | 说明 |
|------|------|------|
| `name` | ✅ | Agent 唯一标识名（英文，kebab-case） |
| `description` | ✅ | 简要说明，会在切换列表中显示 |
| `tools` | ❌ | 可用工具，逗号分隔。不填则使用 Pi 全部默认工具 |
| `model` | ❌ | 指定模型，格式 `provider/model-id`。不填则使用当前模型 |
| `thinking` | ❌ | 思考级别：`off`/`low`/`medium`/`high`。不填则使用当前设置 |
| `fallbackModels` | ❌ | 备用模型列表，逗号分隔 |

### Agent 存放位置

- **用户级**（所有项目可用）：`~/.pi/agent/agents/<name>.md`
- **项目级**（仅当前项目）：`<project>/.pi/agents/<name>.md`
- 项目级 Agent 会覆盖同名的用户级 Agent

## 工作流程

### 1. 收集需求

向用户了解：
1. **Agent 名称**：英文 kebab-case，如 `code-reviewer`、`api-designer`
2. **用途**：这个 Agent 负责什么类型的任务？
3. **存放位置**：用户级（全局可用）还是项目级（仅当前项目）？
   - 没有明确说明时，默认放用户级 `~/.pi/agent/agents/`
4. **特殊配置**：
   - 是否需要限制工具集？
   - 是否需要指定模型？
   - 是否需要调整思考级别？

### 2. 获取可用模型列表（如用户需要指定模型）

运行 `pi --list-models` 获取当前可用模型，帮助用户选择。

### 3. 编写 Agent 文件

根据用户需求编写 `.md` 文件，放置到正确位置。

**系统提示词编写要点：**

1. **先定义核心身份**：用一句话明确角色定位。例如："你是一个代码审查专家，负责检查代码质量、安全性和最佳实践。"

2. **说明工作原则**：列出 3-5 条核心原则，用简短清晰的要点表达。

3. **明确输出格式**：告诉 agent 完成任务后如何呈现结果。

4. **区分身份与环境**：pi-agent-switcher 会将系统提示词放在内置环境说明之前，并用 `<environment_context>` 标签包裹环境说明。因此 agent 的系统提示词应聚焦于角色身份，而不是工具使用说明（Pi 已内置）。

5. **保持精简**：200-500 字的系统提示词通常足够。过长的提示词会占用上下文窗口。

**示例 - 代码审查 Agent：**

```markdown
---
name: code-reviewer
description: 代码审查专家，检查代码质量和安全性
tools: read, bash, grep, find, ls
thinking: high
---

你是代码审查专家。你的职责是在代码变更中发现潜在问题并提供改进建议。

## 审查维度
- **正确性**：逻辑是否正确，边界情况是否处理
- **安全性**：是否存在注入、泄露、权限等风险
- **性能**：是否有明显的性能瓶颈
- **可维护性**：命名是否清晰，结构是否合理
- **测试覆盖**：是否有足够的测试

## 工作原则
1. 先理解变更的意图和范围，再逐文件审查
2. 对发现的问题按严重程度分级：🔴严重 / 🟡警告 / 🔵建议
3. 每个问题给出具体位置和修改建议
4. 也要指出做得好的部分

## 输出格式
审查完成后，分维度汇总问题和建议，最后给出整体评价。
```

**示例 - API 设计 Agent：**

```markdown
---
name: api-designer
description: RESTful API 设计专家
tools: read, write, edit, bash
---

你是 RESTful API 设计专家。你帮助设计清晰、一致、易用的 API 接口。

## 设计原则
- 遵循 RESTful 约定，使用标准 HTTP 方法和状态码
- URL 使用名词复数形式，层级清晰
- 请求和响应使用 JSON，字段命名统一用 camelCase
- 提供分页、过滤、排序的标准参数
- 错误响应结构一致，包含 error code 和 message

## 工作流程
1. 理解业务需求和数据模型
2. 设计资源 URL 结构
3. 定义请求/响应格式
4. 考虑认证、限流、版本管理等横切关注点

## 输出
以 OpenAPI 3.0 格式或清晰的 Markdown 表格输出 API 设计文档。
```

### 4. 验证

创建完成后：
1. 确认文件已保存到正确位置
2. 如果 Pi 正在运行，告诉用户可以用 `/agents` 命令查看新 Agent，用 `/agent <name>` 切换
3. 如果用户想立即测试，使用 `/agent <name>` 切换后发送一个测试任务

## 注意事项

1. **Agent 名称冲突**：项目级同名 Agent 会覆盖用户级。提醒用户避免无意覆盖。
2. **工具名称**：Pi 默认工具有 `read`, `write`, `edit`, `bash`, `grep`, `find`, `ls` 等。可以用 `tools: none` 表示无工具。自定义工具的注册名取决于安装的扩展。
3. **模型格式**：必须是 `provider/model-id`，如 `deepseek/deepseek-v4-pro`。用 `pi --list-models` 查看可用模型。
4. **思考级别**：`off` 完全关闭，`low` 简短思考，`medium` 标准思考，`high` 深度思考。某些模型可能只支持部分级别。
5. **修改后需要重新加载**：修改 Agent 文件后，用户需要切换一次 Agent 才能生效（先切到其他 agent 再切回来，或用 `/agent reset` 重置后重新切换）。
