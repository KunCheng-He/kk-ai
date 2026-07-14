---
name: gzh-workflow
description: |
  公众号文章全流程运营工作流。从选题调研到发布草稿箱的完整流水线。

  触发场景：
  - 用户要求写公众号文章
  - 用户要求运营公众号
  - 用户提到"发公众号""写一篇公众号""公众号文章"

  注意：本 skill 由默认通用主 Agent 加载，不应作为自定义 primary agent 使用。
  主 Agent 加载本 skill 后按流程协调各 subagent 和 skill 完成任务。
---

# 公众号运营工作流

你是主 Agent 的公众号运营工作指南。主 Agent 加载你后，按以下流程将任务分解为独立的 subagent 调用和 skill 加载，确保噪声隔离、权限收紧、用户确认。

## 核心原则

1. **主 Agent 只做编排**：亲自调研、写长文、审查长文都会污染上下文
2. **噪声隔离**：调研和写作通过 subagent 隔离，只回流传结论和文件路径
3. **用户确认关口**：大纲、成稿、发布三个节点必须用户确认后才能继续。**例外**：如果用户明确要求"自动执行""不需要确认""跳过确认"，则关口自动通过
4. **修改即重跑**：任何修改意见必须触发完整阶段重跑，不可在当前文件上局部修补

## Subagent 能力约束

- **explorer** subagent 为只读权限，不能加载 skill
- **general** 和 **browser-researcher** subagent 可以加载 skill
- GZH-Writer 和 ResearchReporter 为自定义 subagent，已内嵌所需规范，无需加载 skill

---

## Phase 1: INIT — 初始化

当用户提供主题时：

1. 创建工作目录 `{YYYYMMDD}_{主题}/`，含子目录 `素材/`
2. 向用户汇报目录已创建，确认是否开始调研
3. 用户确认后 → Phase 2。**如果用户已要求自动执行，跳过确认直接进入 Phase 2**

---

## Phase 2: RESEARCH — 调研

根据主题类型选择调研方式，产出 `调研报告.md`。

### 方式 A：互联网产品/服务（使用新 product-research 工作流）

加载 `research-workflow` skill，按其 4-phase 流程执行：
- Phase 1: 识别产品类型
- Phase 2: 并行数据收集（T0+T2+T3 通过 browser-researcher subagent，T1+T4+T5 通过 general subagent）
- Phase 3: ResearchReporter subagent 生成报告
- Phase 4: 可选 research-to-blueprint

**注意**：research-workflow 产出的是 `README.md`，主 Agent 需要将其重命名或复制为 `调研报告.md`（如果用户项目约定要求此文件名）。

### 方式 B：本地项目/内部材料

主 Agent 直接分析本地文件（代码、文档、资料），必要时用 webfetch 补充信息。产出符合以下标准的 `调研报告.md`：
- 字数 > 1500
- 含核心观点和数据支撑
- 结构化分节

### 方式 C：混合场景

先本地分析产出笔记，再按方式 A 补充网络信息，合并为 `调研报告.md`。

### 验证检查点 1

- [ ] `调研报告.md` 存在且非空
- [ ] 字数 > 1500
- [ ] 包含核心观点和数据支撑

验证通过后向用户汇报调研结论（200 字以内），询问是否开始写作。用户确认后 → Phase 3。**自动模式下跳过确认直接进入 Phase 3。**

---

## Phase 3: DRAFTING — 写作

**使用 GZH-Writer subagent 隔离长文上下文。**

### 步骤 3a：生成大纲

派 GZH-Writer subagent（task_id 避免冲突）：
- 子指令：`只生成文章大纲，不要写全文。输入：调研报告路径={工作目录}/调研报告.md`
- GZH-Writer 已内嵌全部写作规范（callout、风格、格式），无需加载其他 skill
- 返回：文章大纲（含标题、章节结构、每节要点）

主 Agent 将大纲展示给用户，询问是否满意。用户确认后进入步骤 3b。**自动模式下跳过确认，直接派 GZH-Writer 撰写成文。**

### 步骤 3b：撰写成文

派 GZH-Writer subagent（新一轮 task）：
- 子指令：`基于已确认的大纲撰写完整文章。输入：调研报告路径 + 已确认大纲，输出：成稿.md 路径 + 200 字摘要`
- GZH-Writer 已内嵌全部写作规范，成文后会自动执行风格自查

### 验证检查点 2

- [ ] `成稿.md` 存在且非空
- [ ] Markdown 字符数 ≤ 10000（超限精简或询问拆分）
- [ ] 如含 Markdown 表格 → 进入 IMAGE_GEN 处理
- [ ] 如含长代码块（> 20 行）→ 进入 IMAGE_GEN 处理
- [ ] 架构图/流程图已用图表 skill 生成并保存到 `素材/`

验证通过后：
- 需要表格/代码转图 → Phase 4
- 无需转图 → Phase 5

---

## Phase 4: IMAGE_GEN — 等待用户手动生图

本阶段为**暂停等待状态**。主 Agent 生成提示词后等待用户手动完成生图。

**自动模式**：生成提示词文件后即视为本阶段完成，不等待手动生图。后续验证检查点中图片文件存在性检查改为仅检查提示词文件存在性。

### 表格/代码块转图

1. 扫描 `成稿.md`，识别所有 Markdown 表格和长代码块
2. 逐个调用 `image-prompt` skill 生成提示词
3. 保存提示词到 `素材/{描述}-prompt.md`
4. 暂停并提示用户手动生图，粘贴到网页版 AI（Gemini/ChatGPT）
5. 用户确认后验证 `素材/{描述}.png` 存在
6. 将成稿中的表格/代码块替换为 `![描述](素材/{描述}.png)`
7. → Phase 5

### 封面图（Phase 5 通过后执行）

1. 调用 `image-prompt` skill 生成封面提示词
2. 保存到 `素材/封面-prompt.md`
3. 暂停并提示用户手动生图（推荐 900x383，比例 2.35:1）
4. 用户确认后验证 `素材/封面.png` 存在
5. → Phase 6

---

## Phase 5: REVIEW — 审阅

### 步骤 5a：自动审查

派 **general subagent** 审查 `成稿.md`（避免全文回流主上下文）：
- 口语化程度（是否过于书面）
- 段落长度（2-4 行，手机友好）
- 金句密度（是否有粗体突出的关键观点）
- WeChat 格式兼容性（特殊字符、Markdown 语法）
- 只返回 PASS/FAIL + 具体问题列表

### 步骤 5b：用户审阅

主 Agent 汇总审查结果，向用户展示：
1. 审查结论
2. 文章标题和摘要
3. 成稿文件路径
4. 素材清单和字数统计

询问用户是否满意。

用户反馈处理：
| 反馈 | 处理 | 回退到 |
|------|------|--------|
| 满意，继续 | 进入封面生图 | Phase 4 封面部分 |
| 需要补充调研 | 完整重跑调研 | Phase 2 |
| 修改内容 | 完整重跑写作 | Phase 3 |
| 修改表格/配图 | 重新生成提示词 | Phase 4 |

**禁止**：直接修改 `成稿.md` 中个别字句后跳过验证 → 必须完整重跑对应阶段。

---

## Phase 6: PUBLISH — 发布

**必须用户明确确认发布后才能执行。自动模式下跳过本阶段。**

调用 `wechat-gzh-skill`：
```bash
cd {wechat-gzh-skill scripts 目录} && uv run main.py publish {成稿.md 绝对路径} --cover {素材/封面.png 绝对路径}
```

### 验证检查点 4

- [ ] 成功获取 media_id
- [ ] 无错误码

向用户汇报发布结果（media_id + 后台查看提示）。

---

## 文件结构约定

```
{YYYYMMDD}_{主题}/
├── 调研报告.md          # Phase 2 产出
├── 成稿.md              # Phase 3 产出
└── 素材/
    ├── 封面-prompt.md
    ├── 封面.png
    ├── {描述}-prompt.md
    └── {描述}.png
```

---

## 可用资源汇总

### Subagents

| Subagent | 角色 | 权限 | 使用阶段 |
|----------|------|------|----------|
| explorer (内置) | 只读信息收集 | 只读 | RESEARCH (via research-workflow) |
| ResearchReporter | 调研报告生成 | 写工作区 | RESEARCH (via research-workflow) |
| GZH-Writer | 调研→成稿 | 写工作区 | DRAFTING |

### Skills

| Skill | 用途 | 加载方 | 使用阶段 |
|-------|------|--------|----------|
| research-workflow | 产品调研编排（4-phase 并行） | 主 Agent | RESEARCH |

| image-prompt | 生图提示词生成 | 主 Agent | IMAGE_GEN |
| wechat-gzh-skill | Markdown→发布草稿箱 | 主 Agent | PUBLISH |

---

## 反模式提醒

以下行为**严格禁止**：
- ❌ 主 Agent 亲自写长文（应派 GZH-Writer subagent）
- ❌ 跳过审查直接发布
- ❌ 直接修改成稿个别字句后发布（必须完整重跑 DRAFTING）
- ❌ 未经用户确认自动发布
- ❌ 自动调用生图 API（生图由用户手动在网页版完成）
