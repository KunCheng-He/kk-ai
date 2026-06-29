---
id: {{timestamp}}-{{project_slug}}-structure-{{strategy_slug}}
title: {{project_name}} 知识骨架 — {{strategy_name}}
tags:
  - {{project_tag}}
  - 知识骨架
nodeType: 结构
created: {{date}}
source_cards:
{{#each source_cards}}
  - {{this}}
{{/each}}
---

# {{project_name}} 知识骨架 — {{strategy_name}}

> 结构策略：{{strategy_description}}
> 素材来源：{{source_summary}}。{{excluded_cards_note}}

---

## 逻辑骨架

{{#each modules}}
### 【模块{{index}}：{{module_title}}】

【 核心观点{{#if core_claim_source}}（卡片{{core_claim_source}}）{{/if}} → {{core_claim}} 】

  → {{#each evidence_chain}}{{this_type}}（{{this_source}}）：{{this_content}}
  → {{/each}}

{{#if module_transition}}
  → 过渡钩子：{{module_transition}}
{{/if}}

---
{{/each}}

> [!note] 使用说明
> 本骨架按「{{strategy_name}}」编排，适合输出为一篇{{target_audience}}的文章。
> 素材卡片：{{source_card_list}}。{{excluded_summary}}
> 每个【核心观点 → 支撑案例 → 理论依据 → 延伸推论】单元可独立扩写为一个章节。
