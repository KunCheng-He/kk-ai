---
name: workflow-designer
description: 当用户需要设计 AI 编码 Agent 的工作流时使用，覆盖 DSH / OpenCode / Claude Code 等 harness，平台平级、按目标平台的原语分析推荐。用户描述一个开发场景后，基于四层架构（主 Agent / Subagent / 批量编排 / Skill）和五项设计原则，判断该用内置子代理、独立上下文、批量编排还是自定义 agent，以及是否该固化成 skill。当用户提到"工作流"、"agent 编排"、"subagent"、"skill 设计"、"该用 agent 还是 skill"、"自动化流程"时触发。
---

# 工作流设计技能

帮助用户判断：给定一个开发场景，应该用什么方案（内置子代理 / 独立上下文 / 批量编排 / skill / 自定义 agent）来搭建工作流。

各 harness **平级**：先确认目标平台，再按该平台的原语给建议。不同平台的 agent 形态、权限模型、skill 机制差异明显，**不要把一个平台的概念当成通用事实**。

## 步骤 0：确认目标平台

分析前先问用户（用当前平台的提问工具：DSH `ask_user_question`；OpenCode `question`；其他以其文档为准）：

> 这个工作流要在哪个 harness 里落地？

选项：
- **当前会话所在 harness**（最省事，但仍需用户确认，不默认选中）
- **DSH**
- **OpenCode**
- **Claude Code**
- **其他**（Codex、Gemini CLI、Cursor 等）
- **多平台通用**（只给跨平台成立的建议，平台专属能力标注"视平台而定"）

规则：
- 用户选"当前会话"时，先判断当前 harness，再按该平台给结论，并注明"该结论仅对该平台成立"。
- 无法确认某平台的能力（例如它是否有原生子代理、是否有 hot reload）时，先读该平台文档或直接问用户，不臆造。
- 用户要求多平台通用时，先给通用骨架（哪些步骤该隔离、哪些该固化），再分平台补差异。

## 四层架构（跨平台通用模型）

```
工作流 = 主 Agent + Subagent（隔离上下文） + 批量编排 + Skill（可复用指令）
```

- **主 Agent**：理解意图 → 分解 → 委派 → 汇总。各平台都有，定制方式不同（见下）。
- **Subagent**：独立上下文窗口，执行具体任务后回传结论。各平台的调用形态不同。
- **批量编排**：同一套流程跑很多输入 / 起很多子代理时用的编排层。有的平台有专用工具（如 DSH 的 `workflow`），没有的就退化为多次子代理调用。
- **Skill**：可复用指令，注入当前 agent，不隔离上下文。

### 各平台原语对照（对称，无默认位）

| 维度 | DSH | OpenCode | Claude Code |
|---|---|---|---|
| 主 agent 定制 | Agent preset（`${DSH_HOME}/.agent-presets/<id>/`，用「创造模式」编写）+ `AGENTS.md` | agent 文件 + `AGENTS.md` | agent 文件 + `CLAUDE.md` |
| 全新上下文子代理 | `subagent` | Task（内置 Explore / General，可自定义） | Task |
| 承接当前对话 | `subagent_fork` | 以该平台文档为准 | 以该平台文档为准 |
| 批量编排 | `workflow`（JS 脚本 + schema 校验 + 阶段） | 多次 Task 调用 | 多次 Task 调用 |
| 技能目录 | `.dsh/skills`、`~/.dsh/skills` | `.opencode/skills`、`~/.config/opencode/skills` | `.claude/skills`、`~/.claude/skills` |
| 项目规范 | `AGENTS.md` | `AGENTS.md` | `CLAUDE.md` |
| 向用户提问 | `ask_user_question` | `question` | 以该平台文档为准 |
| 按任务选模型 | `workflow` 的 `agent(..., { model })` | agent 文件里指定 | agent 文件里指定 |

> 未列出的平台：多数没有原生子代理，工作流退化为"主 agent + 脚本 + 指令文件"；skill 走便携目录 `.agents/skills`。

## 平台差异说明

### DSH

- 内置 4 个 preset：标准模式、PTC 模式（Code Mode）、极简模式、创造模式（写 preset / 插件）。
- 没有文件式 agent；定制 = `AGENTS.md`（会注入 `$DSH_HOME/AGENTS.md` 与项目根到 cwd 的链，单份上限 64KB）或 Agent preset。
- `subagent` 只有一种通用形态，没有 Explore / General 这类命名；只读性靠 prompt 约定 + 部署层 `toolFilter`（模型调用时改不了），**prompt 不是安全边界**。
- `subagent` 无 per-call 模型参数；按任务换模型只能走 `workflow` 的 `agent(..., { model })` 或部署配置。
- 权限：会话 permission preset（`workspace-write` / `danger-full-access`，`/permissionPresets` 可切换）。
- 技能写后即刻生效（文件监听）。

### OpenCode

- 内置 Explore（只读）/ General（读写执行）子代理，按任务类型选；不满足时再自定义 agent 文件。
- 子代理通过 Task 调用，可指定类型。
- 权限在 agent 配置里声明；skill 目录 `.opencode/skills` 或 `~/.config/opencode/skills`。

### Claude Code

- Task 子代理 + `.claude/agents` 自定义 agent；项目规范是 `CLAUDE.md`；skill 在 `.claude/skills`。
- 具体工具名与字段以该平台文档为准。

### 其他平台（Codex、Gemini CLI、Cursor 等）

- 通常没有原生子代理与 skill 机制：用指令文件 + 便携 `.agents/skills` 做桥。
- 工作流设计要相应简化：并行改为主 agent 顺序执行或外部脚本。

## Subagent 与 Skill 的区别（平台无关）

| 维度           | Subagent                 | Skill                       |
| -------------- | ------------------------ | --------------------------- |
| 独立上下文窗口 | 是                       | 否，注入到当前 agent        |
| 并行执行       | 是                       | 否，顺序执行                |
| 适合           | 需要隔离噪声的任务       | 需要遵循固定流程/规范的任务 |
| 例子           | "帮我搜索所有数据库调用" | "发 PR 的标准流程"          |

## 五项设计原则（平台无关）

### 原则一：信息不回流

子代理产生的中间信息（grep 结果、测试日志、lint 输出、构建错误）**不能回流到主对话**。只回传结论和行动摘要。这是子代理对抗 context rot 的核心机制。

平台若支持结构化返回（如 DSH `workflow` 的 `schema`），优先用它约束返回结构。

### 原则二：读多写少，先读后写

探索阶段并行起只读子代理收集信息，确定路径后**只让一个 agent 写代码**。多个 agent 同时写同一个文件 = 冲突地狱。

### 原则三：权限逐步收紧

按目标平台的权限模型落地，不要假设某种机制到处都有：

- 主 agent：按平台默认（DSH 是会话 permission preset；OpenCode / Claude Code 在 agent 配置里）
- 探索/审查类子代理：prompt 声明只读；平台若支持工具裁剪（如 DSH 的 `toolFilter`）就在部署层真裁
- 写入类：一次只派一个，限定工作区
- 平台只支持"prompt 约定"时，要明确告诉用户这是约定，不是强制边界

### 原则四：模型与任务匹配

不要把旗舰模型用在 grep 搜索上。但**能否按子代理选模型取决于平台**：

- 支持按调用指定模型（如 DSH `workflow`）→ 按任务分模型
- 只能按 agent/实例配置（OpenCode、Claude Code 的 agent 文件）→ 在定义里分
- 完全不支持 → 不要给出做不到的建议

### 原则五：Skill 用于流程固化，Subagent 用于任务隔离

每次判断场景时问自己：这件事需要"自己的上下文窗口"还是"一套清晰指令"？

- 需要隔离 → 子代理
- 需要复用指令 → skill
- 两者都要 → 子代理，并在 prompt 里要求它先加载对应 skill

## 分析框架

当用户描述一个工作流场景时，按以下步骤分析：

### 第一步：确认平台与主 Agent 是否需要定制

1. **目标平台是什么？**（步骤 0）这决定后面所有推荐能不能落地。
2. **这个工作流是否长期反复执行？**
    - 一次性任务 → 平台默认 agent 即可
    - 反复执行 → 考虑定制（注入规范 / persona / skill 指引）
3. **是否需要注入固定的项目上下文？**
    - 是 → 先写项目规范文件（DSH/OpenCode 是 `AGENTS.md`，Claude Code 是 `CLAUDE.md`），最便宜
4. **是否需要固定角色视角或工具面？**
    - 是 → 自定义 agent（DSH 是 Agent preset；OpenCode / Claude Code 是 agent 文件）
    - **加法定制安全**（注入规范、视角、默认 skill）；**减法定制危险**（裁掉子代理/委派工具会让主 agent 失去协调能力）

### 第二步：先决判断 — 是否需要引入子代理？

1. 是一次性简单任务（改一个函数、修一个 bug、加一个简单功能）？
2. 不需要并行探索多个模块？
3. 不会产生大量中间噪声（搜索结果、日志、lint 输出）？
4. 不需要隔离上下文（父对话很长，或子任务会污染父对话）？

四条全是"是" → 不引入子代理，推荐"主 agent only"（可搭配 skill）。

### 第三步：拆解任务

把场景拆成独立步骤，标注性质（探索 / 实现 / 审查 / 流程 / ...）。

### 第四步：对每一步做判断

1. **会产生大量中间噪声吗？** 是 → 子代理隔离；否 → 主 agent 内完成。
2. **需要读父对话的上下文吗？** 需要且平台支持承接（如 DSH `subagent_fork`）→ 用它；否则退化为把必要背景写进 prompt。
3. **并行度多大？** 1–2 个 → 直接子代理；很多个或同一流程跑 N 个输入 → 批量编排（平台有专用工具就用，没有就用多次子代理 + 脚本）。
4. **要复用吗？** 是 → 固化成 skill（路径按目标平台）；否 → 内联指令。
5. **需要常驻角色 / 固定工具面吗？** 是 → 自定义 agent（平台相关）；否 → 默认 agent + prompt。
6. **该平台是否真的支持第 2–5 步要用的能力？** 不确定就先查文档或问用户，不要假设。

### 第五步：输出建议

```
目标平台: [DSH / OpenCode / Claude Code / 其他 / 多平台通用]

场景: [一句话描述]

推荐方案:
- 主 agent: [平台默认 / 需要定制（平台对应的定制方式）]
- Subagent: [全新上下文 / 承接当前对话 / 批量编排 / 不需要]
- Skill: [需要 xxx / 不需要]

理由:
1. [基于原则 x 的解释]
2. [基于原则 y 的解释]

实施建议:
[具体 prompt、编排脚本骨架、SKILL.md 骨架或项目规范片段，用目标平台的原语写]

平台注意事项:
[该平台做不到的部分，或需要换方案的地方]
```

## 反模式警告

以下情况应主动提醒用户：

- **替用户预设平台**：不确认平台就给平台专属建议，等于给了一个可能落不了地的方案
- **把一个平台的概念当成通用事实**：例如把 OpenCode 的 Explore / General 说成所有平台都有
- **过度设计**：场景不需要子代理时不要建议加
- **用重编排跑 2 个 agent**：直接两次子代理更简单
- **多个子代理同时写文件**：串行，或让主 agent 做唯一写入者
- **减法式定制主 agent**：裁掉委派工具会直接拆掉协调能力
- **把"只读约定"当强制隔离**：平台不支持工具裁剪时，必须说明这只是约定
- **Skill 里塞大量指令**：SKILL.md 超过 500 行就该拆，或升级为"skill 指路 + 编排执行"

## 从零搭建工作流的推荐路径（按目标平台落地）

1. 先写项目规范文件（`AGENTS.md` / `CLAUDE.md`）
2. 直接用平台默认 agent + 内置子代理，不加自定义，感受瓶颈
3. 发现"每次都说同样的话" → 固化成 skill（路径按平台）
4. 发现"同一套流程要跑很多输入" → 用平台的编排能力（有专用工具就用，没有就多次子代理）
5. 发现"某个任务总需要特定角色/工具/模型组合" → 自定义 agent（平台相关）
6. 不要一开始就造一堆自定义 agent
