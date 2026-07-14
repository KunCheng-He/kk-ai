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

判断产品类别，记录类型：
- **技术软件**（开发工具/运行时/框架）
- **消费软件**（浏览器/应用/服务）
- **硬件设备**
- **AI/ML 产品**
- **云服务/基础设施**

## 阶段 2：并行数据收集

数据收集分为两类：**browser-researcher subagent**（浏览器/CDP/skill 操作）和 **general subagent**（仅 webfetch，≤200 字摘要）。

**任务分配**：需要 CDP 浏览器或专用 skill（zhihu-k-search、douban-k-search、playwright-cli）的任务合并到单个 `browser-researcher` subagent。它在独立上下文中串行加载 skill、执行 CDP 操作，避免多路 session 冲突，最后返回结构化摘要。仅需 webfetch 的简单采集任务委托给 `general` subagent 并行执行。

### 并发任务

| 任务 | 工具 | 执行者 | 具体操作 |
|------|------|:---:|------|
| T0+T2+T3. 中文社区+截图 | playwright-cli CDP, zhihu-k-search, douban-k-search | **browser-researcher subagent** | 串行加载 skill：(1) playwright-cli 截图产品首页+定价页保存到 assets/，(2) zhihu-k-search 搜索产品相关问答提取高赞观点，(3) douban-k-search 搜索评分短评（**仅书籍/电影/音乐产品**，否则跳过）。返回所有结论的整合摘要+截图路径 |
| T1. 官方信息 | webfetch | general subagent | 访问官网/文档，提取核心功能、目标用户、定价、差异化特点 |
| T4. 通用社区 | webfetch | general subagent | 根据产品类型选择 V2EX/掘金/GitHub/HN/Reddit，搜索讨论 |
| T5. 竞品识别 | webfetch | general subagent | 搜索"X vs"或"X alternatives"，识别 2-3 个主要竞品，对比关键维度 |

**执行方式**：4 路 subagent **同时启动** — 1 个 `browser-researcher`（T0+T2+T3，内部串行管理 CDP）+ 3 个 `general`（T1+T4+T5）。browser-researcher 自行管理内部 skill 加载顺序和 CDP 连接，确保不冲突。主 Agent 只负责收集返回的摘要，原始 CDP/搜索数据全部隔离在 subagent 上下文中。

### 数据源优先级规则

1. **首先检查项目 AGENTS.md 中的数据源规则**，遵守所有平台使用限制
2. 如果 AGENTS.md 禁止某平台，跳过对应任务
3. 每个任务必须返回有效结论（至少 3 条实质信息），否则标记为"数据不足"
4. T3（豆瓣）仅在调研书籍/电影/音乐产品时执行，其他产品类型跳过

### 信息获取策略

- 简单静态页面 → `webfetch`
- 动态渲染（React/Next.js/Vue）、反爬拦截、网络无法访问 → `playwright-cli` CDP 模式：
  ```bash
  playwright-cli attach --cdp=http://localhost:9222
  ```
  若 CDP 端口未就绪 → 提示用户启动浏览器调试模式，等待确认后重试。

## 阶段 3：汇总与报告生成

1. 汇总 browser-researcher 和所有 general subagent 返回的结论摘要
2. 调用 **ResearchReporter** subagent，传入：
   - 产品类型
   - 所有收集结论（仅摘要，不含原始数据）
   - 工作目录路径
3. ResearchReporter 生成 `README.md`
4. 注意：不要让原始网页内容进入报告生成 context，只传结论摘要

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
- 优先社区：V2EX, 知乎, 豆瓣, Bilibili, Reddit
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
- 所有引用需附来源 URL
