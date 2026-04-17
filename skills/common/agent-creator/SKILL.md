---
name: agent-creator
description: 创建 OpenCode Agent 的交互式工具。当用户想要创建新的 agent（主代理或子代理）、配置代理、设置工具权限、或提到"创建代理"、"agent"、"subagent"、"代理配置"时使用此技能。支持 JSON 和 Markdown 两种配置方式，引导用户完成名称、描述、模型、工具权限等配置项的设置。
---

# Agent Creator

帮助用户创建符合 OpenCode 规范的 Agent 配置文件，支持主代理（primary）和子代理（subagent）两种类型。

## 工作流程

### 第一步：选择代理类型

询问用户要创建哪种类型的代理：

1. **主代理（primary）**
   - 通过 Tab 键切换使用
   - 作为主要对话助手
   - 示例：Build（全工具）、Plan（受限只读）

2. **子代理（subagent）**
   - 通过 `@` 提及调用
   - 由主代理自动调用执行专门任务
   - 示例：Explore（代码探索）、General（通用任务）

### 第二步：选择配置方式

询问用户希望使用哪种配置方式：

1. **Markdown 方式**（推荐）
   - 文件位置：`~/.config/opencode/agents/`（全局）或 `.opencode/agents/`（项目级）
   - 格式：YAML frontmatter + Markdown 内容
   - 优点：结构清晰，易于维护

2. **JSON 方式**
   - 文件位置：`opencode.json` 配置文件
   - 格式：JSON 对象
   - 优点：集中管理所有配置

### 第三步：选择保存位置

询问用户配置文件的保存位置：

- **全局**：`~/.config/opencode/agents/` - 所有项目可用
- **项目级**：`.opencode/agents/` - 仅当前项目可用

### 第四步：收集基本信息

必填信息：

1. **名称（name）**
   - Markdown 方式：文件名即为代理名称（如 `review.md` 创建名为 `review` 的代理）
   - JSON 方式：在 `agent` 对象下的键名
   - 命名建议：使用简短、有意义的英文名称

2. **描述（description）**
   - 简要说明代理的功能和使用场景
   - 这是**必填项**
   - 主代理：用于用户了解代理用途
   - 子代理：用于主代理判断何时调用此子代理
   - 示例：`Reviews code for best practices and potential issues`

### 第五步：配置可选项

根据用户的使用场景，询问以下可选项：

#### 模型（model）

```
是否为此代理指定特定模型？
- 不指定
  - 主代理：使用全局配置的模型
  - 子代理：使用调用它的主代理的模型
- 指定模型（如 anthropic/claude-sonnet-4-20250514）
```

#### 温度（temperature）

```
控制响应的随机性和创造力：
- 0.0-0.2：非常集中和确定性（代码分析、规划）
- 0.3-0.5：平衡（一般开发任务）
- 0.6-1.0：更有创造力（头脑风暴、探索）
- 不指定（使用模型默认值）
```

#### 工具权限（tools）

```
控制代理可访问的工具：
- write：文件写入
- edit：文件编辑
- bash：执行命令
- read：文件读取
- glob：文件搜索
- grep：内容搜索
- webfetch：网络请求
- task：调用其他子代理

可设置为 true（启用）或 false（禁用）
```

#### 权限控制（permission）

```
对特定操作设置审批级别：
- ask：执行前提示用户审批
- allow：允许所有操作，无需审批
- deny：禁用该工具

可配置的工具：edit、bash、webfetch
bash 权限支持 glob 模式匹配特定命令
```

#### 隐藏（hidden）

```
是否从 @ 自动补全菜单中隐藏？
- 否（默认，用户可通过 @ 提及调用）
- 是（仅能通过 Task 工具以编程方式调用）

注意：仅适用于子代理（subagent）
```

#### 最大步数（steps）

```
限制代理的最大迭代次数：
- 不限制（默认）
- 指定步数（如 5、10）
```

#### 颜色（color）

```
自定义代理在 UI 中的显示颜色：
- 不指定（使用默认）
- 十六进制颜色（如 #FF5733）
- 主题颜色：primary、secondary、accent、success、warning、error、info
```

#### 任务权限（permission.task）

```
控制代理可以通过 Task 工具调用哪些子代理：
使用 glob 模式进行灵活匹配

示例：
- "*": deny（禁止所有）
- "code-reviewer": allow（允许特定代理）
- "review-*": allow（允许匹配模式的代理）

注意：最后匹配的规则优先
```

### 第六步：编写系统提示词

引导用户编写代理的系统提示词：

- Markdown 方式：在 YAML frontmatter 下方直接编写
- JSON 方式：使用 `prompt` 字段，支持 `{file:./path/to/prompt.txt}` 引用外部文件

提示词编写建议：
- 明确代理的角色和职责
- 说明关注点和限制
- 提供输出格式要求（如需要）

### 第七步：生成配置文件

根据收集的信息生成配置文件。

## 配置文件模板

### 主代理 Markdown 模板

```markdown
---
description: <代理描述>
mode: primary
model: <可选，模型ID>
temperature: <可选，0.0-1.0>
tools:
  write: <true/false>
  edit: <true/false>
  bash: <true/false>
permission:
  edit: <ask/allow/deny>
  bash:
    "*": <ask/allow/deny>
steps: <可选，最大步数>
color: <可选，颜色>
permission:
  task:
    "*": <ask/allow/deny>
---
<系统提示词内容>
```

### 子代理 Markdown 模板

```markdown
---
description: <代理描述>
mode: subagent
model: <可选，模型ID>
temperature: <可选，0.0-1.0>
tools:
  write: <true/false>
  edit: <true/false>
  bash: <true/false>
permission:
  edit: <ask/allow/deny>
  bash:
    "*": <ask/allow/deny>
hidden: <可选，true/false>
steps: <可选，最大步数>
---
<系统提示词内容>
```

### JSON 模板

```json
{
  "$schema": "https://opencode.ai/config.json",
  "agent": {
    "<代理名称>": {
      "description": "<代理描述>",
      "mode": "<primary/subagent>",
      "model": "<可选，模型ID>",
      "temperature": <可选，数值>,
      "prompt": "<提示词或 {file:./path/to/prompt.txt}>",
      "tools": {
        "write": <true/false>,
        "edit": <true/false>,
        "bash": <true/false>
      },
      "permission": {
        "edit": "<ask/allow/deny>",
        "bash": {
          "*": "<ask/allow/deny>"
        },
        "task": {
          "*": "<ask/allow/deny>"
        }
      },
      "hidden": <可选，true/false，仅子代理>,
      "steps": <可选，数值>,
      "color": "<可选，颜色>"
    }
  }
}
```

## 示例场景

### 主代理示例

#### 场景1：开发代理（类似 Build）

- 全工具访问
- 用于日常开发工作
- 完全自主执行

#### 场景2：规划代理（类似 Plan）

- 只读访问，不修改文件
- 用于分析和规划
- 所有写操作需审批

### 子代理示例

#### 场景1：代码审查代理

- 只读访问，不修改文件
- 关注代码质量、安全性和最佳实践
- 通过 `@code-reviewer` 调用

#### 场景2：文档编写代理

- 可写入文件
- 禁用 bash 命令
- 专注于文档生成

#### 场景3：安全审计代理

- 只读访问
- 专注于安全漏洞检测
- 使用特定模型

## 主代理与子代理的区别

| 特性 | 主代理 (primary) | 子代理 (subagent) |
|------|------------------|-------------------|
| 调用方式 | Tab 键切换 | @ 提及或主代理自动调用 |
| 隐藏选项 | 不适用 | 可设置 hidden: true |
| 任务权限 | 可配置 permission.task | 不适用 |
| 默认模型 | 全局配置模型 | 继承主代理模型 |

## 注意事项

1. **描述的重要性**：description 是必填项
   - 主代理：帮助用户了解代理用途
   - 子代理：主代理根据描述判断何时调用
2. **权限优先级**：代理级配置会覆盖全局配置
3. **工具通配符**：支持 `mymcp_*` 格式控制 MCP 服务器工具
4. **bash 权限模式**：支持 glob 模式，最后匹配的规则优先
5. **隐藏代理**：hidden 仅适用于子代理，仅影响 UI 可见性，不影响 Task 工具调用
6. **任务权限规则**：最后匹配的规则优先

## 验证配置

创建完成后，建议用户：

1. 重启 OpenCode 或重新加载配置
2. 主代理：使用 Tab 键切换测试
3. 子代理：使用 `@<代理名称>` 测试调用
4. 检查代理是否按预期工作
