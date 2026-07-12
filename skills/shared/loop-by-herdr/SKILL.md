---
name: loop-by-herdr
description: |
  通过 herdr 实现以目标为循环的迭代优化模式。当用户需要反复测试、评估、优化一个工作流或产出物时使用此技能。
  适用场景：优化 skill/agent 设计、调优 AI 工作流、自动化质量门禁循环、任何需要"执行→评估→优化→重试"的迭代任务。
  触发关键词：循环测试、迭代优化、反复调试、loop、iterate、retry until、多轮测试、自动优化循环。
  即使用户未明确提到"循环"，但上下文中出现了"重复执行直到满足"、"不够好就继续改"等语义时也应主动使用。
---

# loop-by-herdr: Herdr 驱动的迭代优化循环

通过 herdr 管理多个 OpenCode 会话，实现以目标为驱动的"执行→审查→优化→重试"循环模式。

## 为什么需要这个模式

OpenCode 本身不支持以目标为条件的自动重试。但通过 herdr，你可以：
- 在独立 tab/pane 中启动 OpenCode 会话
- 等待任务完成并读取输出
- 评估产出是否达标
- 不达标时修改 skill/agent/规则文件，再开新会话重试
- 最多 N 轮循环，避免无限重试

这样，单次会话做不到的迭代优化，通过 herdr 的多会话编排就能实现。

## 前提条件

- 运行在 herdr 环境中（`HERDR_ENV=1`）
- 项目中已配置 `opencode` 命令
- 了解 herdr 基本操作（`herdr pane run`、`herdr wait agent-status`、`herdr pane read`）

## 工作流

### 第零步：确定目标和成功标准

在开始循环前，明确：
1. **目标**：要完成什么任务？（如"生成符合模板的调研报告"）
2. **成功标准**：怎样的产出算通过？（如"README.md 包含官方介绍/用户评价/竞品对比/数据来源，且截图存在、blueprint 生成"）
3. **最大轮数**：最多迭代几轮？（默认 5）

### 第一步：初始化循环

```
iteration = 1
max_iterations = N
passed = false
```

### 第二步：执行任务

1. 创建 herdr tab（或复用已有 workspace）：
   ```bash
   herdr tab create --workspace 1 --label "Iter-<N>"
   ```
2. 在新 tab 的 pane 中启动 OpenCode：
   ```bash
   herdr pane run <pane_id> "cd /path/to/project && opencode"
   ```
3. 等待 OpenCode 就绪：
   ```bash
   herdr wait agent-status <pane_id> --status idle --timeout 30000
   ```
4. 发送任务：
   ```bash
   herdr pane run <pane_id> "<task description>"
   ```
5. 等待任务完成（`done` 状态表示产出已生成、等待用户查看）：
   ```bash
   herdr wait agent-status <pane_id> --status done --timeout 600000
   ```

### 第三步：审查产出

1. 读取会话输出，了解任务执行摘要：
   ```bash
   herdr pane read <pane_id> --source recent --lines 80
   ```
2. 读取实际生成的文件，对照成功标准逐项检查。使用 `Read` 工具读取项目中的输出文件。
3. 记录通过项和未通过项。

### 第四步：判断

- **全部通过** → `passed = true`，退出循环
- **有未通过项 且 iteration < max_iterations** → 进入第五步优化，然后 `iteration++`，回到第二步
- **iteration >= max_iterations** → 退出循环，报告最终状态

### 第五步：优化

根据审查结果，定位问题根因并优化：

1. **如果是 skill 指令不够明确** → 修改对应的 `SKILL.md`
2. **如果是 agent 权限/工具链问题** → 修改 agent 定义或任务分配（如 explorer 无 playwright-cli 权限，改为由主 Agent 直接执行截图）
3. **如果是项目规则缺失** → 完善 `AGENTS.md`
4. **如果是任务描述不够清晰** → 调整发送给 OpenCode 的任务 prompt

优化后回到第二步，启动新 tab 执行下一轮。

### 第六步：收尾

循环结束后：
1. 汇总每轮的通过/失败情况和优化动作
2. 如果最终通过，确认工作流不需要进一步改动
3. 如果最终未通过，列出已知问题和可能的方向

## 审查策略

审查时不要只看 OpenCode 的输出摘要，要**直接读取生成的文件**验证：

- 文件是否存在（如 `README.md`、`visual_blueprint.json`）
- 关键章节是否完整（如 官方介绍/用户评价/竞品对比）
- 必选附件是否生成（如截图文件大小 > 0）
- 数据引用是否有效（URL 不空、来源标注清晰）

用 `bash` 命令快速验证：
```bash
ls -laR <output_dir>/          # 检查文件结构
wc -l <output_dir>/README.md   # 检查报告长度
grep -c "## " <output_dir>/README.md  # 检查章节数
```

## 注意事项

- 每轮必须在新 tab 中启动新 OpenCode 会话——不能复用旧会话（旧会话已被上一次任务污染）
- 等待超时要设合理值（简单任务 3 分钟，复杂调研 10 分钟）
- 优化动作要精准——修一处测一处，不要一次改多个变量
- 记录每轮的失败原因和修复动作，便于回溯

## 示例：优化产品调研工作流

```
目标: 调研报告必须包含 README.md + 截图 + visual_blueprint.json

第1轮: Cursor 调研 → README ✅, 截图 ❌, blueprint ❌
  → 优化: blueprint 从"可选"改为"必须"

第2轮: Arc 浏览器调研 → README ✅, 截图 ❌, blueprint ✅
  → 根因: explorer subagent 无 playwright-cli 权限，截图委托失败
  → 优化: 截图任务拆为 T0，由主 Agent 直接执行

第3轮: Warp 终端调研 → 全部通过 ✅ → 退出循环
```
