---
name: research-to-blueprint
description: |
  将调研报告转换为视觉蓝图 JSON。当用户需要从调研报告提取语义、生成 visual_blueprint.json、或进行数据锚点校验时使用此技能。
  触发关键词：视觉蓝图、visual blueprint、语义提取、数据锚点、调研转JSON、蓝图生成、anchor checker。
  即使未明确提及，但上下文涉及"从报告提取关键信息"、"生成结构化视觉数据"、"校验数据一致性"时也应触发。
---

# Research to Visual Blueprint

从调研报告中提取语义信息，生成结构化视觉蓝图 JSON，并进行数据锚点校验。

## 输入输出规范

- **输入**：调研报告文件（Markdown 格式，路径由调用方指定）
- **输出**：`visual_blueprint.json`（固定命名，与输入文件同目录）

## 工作流程

### Step 1: 读取调研报告

读取指定路径的调研报告文件，提取以下核心信息：

1. **核心结论** (`core_conclusion`) - 报告的主要发现和结论
2. **关键数据点** (`data_points`) - 所有数字、百分比、统计数据
3. **视觉联想** (`visual_metaphor`) - 适合视觉化呈现的隐喻或场景
4. **情绪基调** (`emotional_tone`) - 内容的情感色彩

### Step 2: 生成视觉蓝图

按照 `references/blueprint_schema.json` 的结构生成 JSON 文件，保存为 `visual_blueprint.json`，与输入文件放在同一目录。

### Step 3: 数据锚点校验

**关键步骤** - 对比原文与生成的 JSON 中的数字数据：

1. 提取原文中所有数字（百分比、绝对值、比率等）
2. 与 JSON 中 `data_points` 数组逐一比对
3. **发现不一致时自动修正**：以原文为准，更新 JSON

### Step 4: 输出校验报告

在 JSON 中添加 `validation` 字段记录校验结果：

```json
{
  "validation": {
    "status": "passed|corrected",
    "corrections": [
      {
        "field": "data_points[0].value",
        "original": "50%",
        "corrected": "80%",
        "source": "输入文件:42"
      }
    ],
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

## 数据提取规则

### 数字识别模式

- 百分比：`增长 80%`、`下降 15.5%`
- 绝对值：`用户数 1200 万`、`营收 3.5 亿元`
- 比率：`转化率 1:5`、`ROI 为 3.2`
- 时间范围：`2023 年`、`Q4`、`过去 6 个月`

### 视觉联想提取

从报告中识别适合视觉化的概念：

- 增长/下降趋势 → 上升/下降箭头、曲线图
- 对比数据 → 并排柱状图、天平
- 流程/步骤 → 漏斗、时间线、流程图
- 占比/分布 → 饼图、树状图

### 情绪基调判断

根据报告内容判断整体基调：

- `positive`: 增长、成功、突破、领先
- `negative`: 下降、风险、挑战、问题
- `neutral`: 客观数据、平衡分析
- `urgent`: 紧急、警告、需立即行动

## 使用示例

**输入**:
```
请从 ./workspace/research/task-001/调研报告.md 生成视觉蓝图
```

**输出**:
- 生成 `./workspace/research/task-001/visual_blueprint.json`
- 控制台输出校验结果摘要

## 注意事项

1. **数据准确性优先** - 宁可多花时间校验，不可输出错误数据
2. **保持原文语义** - 提取时不可歪曲原意，不确定时标注 `uncertain`
3. **完整记录来源** - 每个 data_point 必须标注在原文中的行号
