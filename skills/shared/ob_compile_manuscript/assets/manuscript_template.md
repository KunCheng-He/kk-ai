---
id: {{note_id}}
title: {{note_id}} 「{{emoji_title}}」
tags:
{{#each tags}}
  - {{this}}
{{/each}}
nodeType: 知识
created: {{date}}
updated: {{date}}
---

<!--
  本模板由 ob_compile_manuscript SKILL 驱动。SKILL 在步骤一中已加载：
  - author_voice.md（人格注入）
  - style_guide.md（格式规范）
  
  三个铁律：
  - 永远用"我"下判断，不要躲到"我们"后面
  - 核心概念优先尝试用生活化比喻拆解，但不自然别硬塞
  - 至少有一处血泪教训（我试了X → 翻车 → 用Y解决）
-->

# 1. {{hook_section_title}}

> [!NOTE] {{hook_callout_title}}
> {{hook_callout_content}}

{{hook_body}}

# 2. {{concept_section_title}}

## 2.1 {{concept_subsection_1}}

{{concept_body_1}}

| {{table_header_1}} | {{table_header_2}} | {{table_header_3}} |
|:-------------------:|:-------------------:|:-------------------:|
| {{row_1_col_1}} | {{row_1_col_2}} | {{row_1_col_3}} |

> [!WARNING]
> {{warning_callout_content}}

## 2.2 {{concept_subsection_2}}

{{concept_body_2}}

> [!TIP]
> {{tip_callout_content}}

# 3. {{case_section_title}}

{{case_intro}}

## 3.1 {{case_subsection_1}}

| 🧱 层级 | {{case_table_col_2}} |
|:------:|:---------------------|
| {{layer_1}} | {{layer_1_detail}} |
| {{layer_2}} | {{layer_2_detail}} |

{{case_detail_1}}

> [!NOTE]
> {{case_note_content}}

> [!WARNING]
> {{case_warning_content}}

{{case_detail_2}}

## 3.2 {{case_subsection_2}}

{{case_closing_body}}

# 4. {{conclusion_section_title}}

{{conclusion_opening}}

## 4.1 {{conclusion_subsection_1}}

| 年份 | {{year_col_2_title}} | 核心问题 |
|:-----|:---------------------|:--------|
| {{year_1}} | {{year_1_desc}} | {{year_1_question}} |
| {{year_2}} | {{year_2_desc}} | {{year_2_question}} |

{{conclusion_body_1}}

## 4.2 {{conclusion_subsection_2}}

{{conclusion_body_2}}

> [!NOTE]
> {{conclusion_note_content}}

> [!TIP]
> {{conclusion_tip_content}}

{{conclusion_body_3}}

## 4.3 {{conclusion_subsection_3}}

{{conclusion_final}}

---

<!--
  交付前自查（全部通过才能写入文件）：

  格式层：
  - [ ] 标题有 emoji 且口语化
  - [ ] 章节用 # N. 数字编号
  - [ ] callout 框 ≥ 3-5 个/千字
  - [ ] 该对比的地方用了表格
  - [ ] 代码块语言标签完整
  - [ ] 没有 --- 分割线代替文字过渡

  语言层：
  - [ ] 开头不是"本文将..."
  - [ ] 没有"综上所述""双刃剑""不仅...而且""随着...的发展"
  - [ ] 结尾不是"希望本文对你有帮助"

  人格层（不过则整篇重写）：
  - [ ] 全文有"我" ≥ 3 处
  - [ ] 有中心比喻 ≥ 1 个（实操/推导类可跳过）
  - [ ] 有血泪教训 ≥ 1 处
  - [ ] 有态度判断 ≥ 2 处
  - [ ] 有"说人话"落地 — 每个抽象概念后都有口语化翻译
  - [ ] 读起来像人说话，不像论文
-->

> [!quote] 参考资料
> {{references}}
