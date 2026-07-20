---
name: research-workflow
description: |
  产品调研工作流。当用户要求研究、调研、了解某个产品时加载此技能。
  提供完整的产品调研流程指导：识别产品类型→并行收集多源数据→竞品分析→生成结构化报告。
  触发关键词：调研、研究、产品调研、research、竞品分析、产品分析、市场调研。
---

# 产品调研工作流

你是产品调研工作流的协调者。按此流程将任务分解为并行探索任务，最后汇总并生成报告。

## 工作目录

首先创建：`{YYYYMMDD}_{Topic}/`，如 `20260709_AI-PPT-Research`
- 报告：`README.md`
- 资源：`assets/`
- 蓝图：`visual_blueprint.json`（由 research-to-blueprint skill 生成）

## 阶段 1：识别产品类型

判断产品类别并记录类型。产品可同时拥有多个标签，不强制归入单一类别：
- **技术软件**（开发工具/运行时/框架）
- **消费软件**（浏览器/应用/服务）
- **硬件设备**
- **AI/ML 产品**
- **云服务/基础设施**

## 阶段 2：按访问方式调度数据收集

并行是性能优化，不得以牺牲数据完整性为代价。先判断页面访问方式，再分配执行者：

- **已知 URL、静态页面、无需交互**：交给内置 `general` subagent 使用 `webfetch`，此类任务可以并行。
- **需要搜索发现 URL、动态渲染、登录态、翻页、展开内容、截图或专用 skill**：进入唯一的 `browser-researcher` 队列，串行执行。
- `webfetch` 返回内容不完整、被拦截或无法访问时，将任务追加到 browser 队列，不得以空结果结束。
- 禁止为了维持固定并发数而限制任务只能使用 `webfetch`。

### 逻辑任务

| 任务 | 首选方式 | 具体操作 |
|------|------|------|
| T0. 产品截图 | browser 队列 | 截取产品首页和定价页，保存到指定工作目录的 `assets/`，返回实际相对路径 |
| T1. 官方信息 | 静态 URL 可用 `webfetch`，否则 browser 队列 | 获取核心功能、目标用户、定价、差异化特点、文档和 Release Notes |
| T2. 中文社区 | browser 队列 | 依次执行 `zhihu-k-search` 和 `xhs-k-search`；书籍、电影、音乐产品再执行 `douban-k-search` |
| T3. 通用社区 | browser 队列 | 根据产品类型搜索 V2EX、掘金、InfoQ、GitHub、HN、Reddit 等平台 |
| T4. 竞品识别 | browser 队列；已有候选竞品的静态官网可并行 `webfetch` | 搜索 "X vs"、"X alternatives"，识别 2-3 个主要竞品并验证定位 |

### 执行顺序

1. 主 Agent 创建工作目录并列出已知官方 URL、待搜索平台和待截图页面。
2. 同时启动静态 `webfetch` 并行池和一个 `browser-researcher`。从首次 browser Task 结果的 `<task id="...">` 中提取并记录 `task_id`；browser-researcher 内部严格串行执行 T0、T2、T3、T4 以及已知动态页面。
3. 汇总第一轮结果；任何 `webfetch` 失败或内容不完整的任务，必须携带首次返回的 `task_id` 续接同一个 browser-researcher 会话。续接完成后比较返回结果中的 `<task id="...">` 与传入值：相同才视为成功续接；不同则说明 Task 静默创建了新会话，必须忽略该增量结果，使用完整的已完成任务、证据、失败上下文和待办任务重新创建 browser Task，并记录新的 `task_id`。
4. browser-researcher 不得并发操作同一个 CDP 浏览器，不得再委派新的浏览器 subagent。

调用 `browser-researcher` 时，prompt 必须提供工作目录绝对路径、逻辑任务列表和预期证据格式。要求其直接使用指定目录，例如将截图保存到 `{工作目录}/assets/`；禁止自行创建新的工作目录。

调用每个内置 `general` subagent 时，prompt 必须完整包含以下契约，不能假设它会继承本 skill 正文：

- 只访问主 Agent 给出的确切静态 URL，并逐一列出 URL；禁止搜索、发现或扩展到其他页面
- 明确要提取的字段和问题范围，不得补充任务范围外的信息
- 为该 Task 指定独立的 `evidence_id` 前缀
- 要求按本 skill 的“证据返回格式”返回，并填写实际抓取日期 `retrieved_at`
- 只返回结构化证据摘要，不返回原始 HTML、长篇网页正文或抓取日志
- 访问失败、内容为空或疑似动态渲染时，返回 URL、失败类型和原因，不得猜测内容；主 Agent 将其转入 browser 队列

### 数据源优先级规则

1. **首先检查项目 AGENTS.md 中的数据源规则**，遵守所有平台使用限制
2. 如果 AGENTS.md 禁止某平台，跳过对应任务
3. 每个实际选择的数据源至少返回 3 条实质信息；社区数据必须对应至少 3 个独立的具体内容 URL，同一页面拆出的多条 claim 只计为 1 个来源。不足时对该数据源标记为"数据不足"，不能用其他平台的数量补足
4. 豆瓣仅在调研书籍、电影、音乐产品时执行，其他产品类型跳过
5. 知乎和小红书默认都要覆盖；仅在与调研主题明显无关或不可访问时跳过，并记录原因

### 信息获取策略

- 已知 URL 的简单静态页面 → `webfetch`
- 动态渲染（React/Next.js/Vue）、反爬拦截、网络无法访问 → `playwright-cli` CDP 模式：
  ```bash
  playwright-cli attach --cdp=http://localhost:9222
  ```
  若 CDP 端口未就绪，先执行 `brave-debug` 启动调试浏览器并重试。仍然失败时再询问用户希望使用其他 CDP 端口还是其他浏览器。

**浏览器底线**：只允许 CDP 模式复用用户已有浏览器，禁止执行 `playwright install`、`npx playwright install`、`--no-cdp` 或任何下载/安装 Chromium 的命令。本规则覆盖各专用 skill 中关于 Launch 模式和安装浏览器的通用回退说明。因坚持 CDP 模式而无法访问的平台，记录尝试过程和失败原因，在最终报告的“数据局限”中说明，不得静默跳过。

### 证据返回格式

所有 subagent 只返回提炼后的证据记录，不返回 DOM、原始 HTML 或完整搜索输出。每条记录必须包含：

```yaml
- evidence_id: 平台缩写加序号，例如 zhihu-01
  claim: 可直接写入报告的事实或观点
  source_title: 具体页面或帖子标题
  source_url: 具体内容 URL，禁止只写平台首页或搜索关键词
  platform: 来源平台
  published_at: 发布时间；官方常青页面未标注时写 "not stated"
  retrieved_at: 抓取日期
  evidence_type: official | community | repository | review
  engagement: 点赞、评论、Stars 等；无数据时写 null
  confidence: high | medium | low
```

无法确认的字段必须明确写 `not stated` 或 `null`，不得猜测。`evidence_id` 在本次调研中必须唯一。竞品记录还需包含对比维度和支持该对比的证据 ID。

## 阶段 3：汇总与报告生成

1. 汇总 browser-researcher 和所有 general subagent 返回的结构化证据摘要
2. 执行质量门禁：
   - 每个实际选择的数据源是否有至少 3 条有效信息；社区数据是否来自至少 3 个独立具体内容 URL，或已明确标记数据不足及原因
   - 社区证据是否包含具体内容 URL 和发布时间
   - 官方常青页面是否包含具体 URL 和抓取日期
   - 是否包含至少 2 个竞品和至少 3 个有证据支持的对比维度
   - 报告中的关键数字是否能映射到证据记录
   - 所有计划引用的截图路径是否相对于最终 README 所在目录，并能从该目录解析到真实文件
3. 门禁失败时，优先重试一次或改用替代来源。仍失败时只能生成明确标注"部分完成/数据不足"的报告，不得输出无证据的确定性结论。
4. 调用 **ResearchReporter** subagent，从返回结果的 `<task id="...">` 中提取并记录 `task_id`，传入：
   - 产品类型
   - 所有结构化证据记录（不含原始网页数据）
   - 各数据源覆盖状态和质量门禁结果
   - 截图相对于最终 README 所在目录的实际路径，例如 `assets/home.png`
   - 工作目录路径
5. ResearchReporter 校验输入后生成 `README.md`，关键结论、数字、社区观点和竞品对比必须标注对应的 `evidence_id`。
6. README 写入后，主 Agent 必须执行最终报告门禁：
   - 逐项检查关键结论、数字、社区观点和竞品矩阵是否引用有效的 `evidence_id`
   - 检查引用 URL 是否为具体内容页，社区来源是否标注发布时间
   - 以 README 所在目录为基准解析所有 Markdown 图片链接，并确认文件存在
   - 检查所有采集失败或不足的数据源是否出现在“数据局限”中
7. 最终门禁失败时，携带失败项和第 4 步记录的 `task_id` 续接同一个 ResearchReporter 修正一次。续接后比较返回结果中的 `<task id="...">` 与传入值：相同则重新检查报告；不同则说明 Task 静默创建了新会话，忽略该增量结果，使用完整证据、覆盖状态、截图路径、工作目录、原报告内容和门禁失败项重新创建 ResearchReporter Task。修正后仍失败则停止交付正式报告，向用户说明未通过项；不得将未通过报告描述为完整报告。
8. 注意：不要让原始网页内容进入报告生成 context，只传结构化证据摘要

## 阶段 4：后处理（可选）

报告完成后，**如需要结构化输出**，调用 `research-to-blueprint` skill 生成 `visual_blueprint.json`：
- 输入：刚生成的 README.md
- 输出：同目录下的 `visual_blueprint.json`（含数据锚点校验报告）
- 默认不执行。用户明确要求或下游需要机器可读数据时才调用
- 如果用户未要求且 research-to-blueprint skill 不可用，跳过

## 产品类型与社区策略

### 技术软件（开发工具/运行时/框架）
- 优先社区：Hacker News, V2EX, Reddit (r/programming), GitHub Discussions
- 官方来源：官方文档, GitHub 仓库, Release Notes

### 消费软件（浏览器/应用/服务）
- 优先社区：小红书, 知乎, V2EX, Bilibili, Reddit
- 官方来源：产品页面, 博客, 帮助中心

### 硬件设备
- 优先社区：V2EX, 知乎, Bilibili (视频评测), Reddit
- 官方来源：产品规格页, 新闻稿

### AI/ML 产品
- 优先社区：Hacker News, Twitter/X, Reddit (r/MachineLearning), V2EX
- 官方来源：研究论文, 技术博客, API 文档

### 云服务/基础设施
- 优先社区：Hacker News, Reddit (r/devops), V2EX
- 官方来源：官方文档, 状态页, 案例研究

## 内容质量标准

- 高互动量内容优先（点赞、评论多）
- 时效性优先（近 12 个月内）
- 深度分析优于简短提及
- 可信来源优先（知名评测者、资深成员）
- 竞品至少 2 个，覆盖 3+ 对比维度
- 社区引用必须附具体内容 URL 和发布时间
- 每个社区数据源至少覆盖 3 个独立具体内容 URL
- 官方常青页面必须附具体 URL 和抓取日期
- 关键数字和判断必须能映射到证据记录
