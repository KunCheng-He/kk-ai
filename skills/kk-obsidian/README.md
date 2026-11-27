---
id: kk-obsidian
title: kk-obsidian
type: skill
created: 2026-11-27
version: 1.0
---

# kk-obsidian

hkc 的 Obsidian 学习与记笔记工作流。合并自旧的三个 skill（`ob_capture_insight` / `ob_architect_structure` / `ob_refine_card`）与 `Knowledge Co-Creator` agent 的阶段门禁表。

## 为什么合并

旧结构的三个问题：

1. **状态靠外部维护**。`stage` 字段由 agent 的 25 行阶段切换表驱动，state 坏了整条链就断。
2. **路径与体例硬编码重复**。`06-AI共建/[项目]/` 在三个 SKILL.md 里各写一遍；`nodeType` 用了原子/结构/输出三套标识。
3. **成稿和入库脱节**。`LOOP-xxx` 输出卡片是独立体例，与 01-万象火锅 不兼容，"迁移"那一步只有一句提示、没人执行。

## 改成了什么

| 旧 | 新 |
|---|---|
| 按"阶段"选 skill | 按"想要什么产出"选动作（A 捕获 / B 卡片 / C 骨架 / D 成稿 / E 入库） |
| `stage` 字段驱动 | 只探测目录（`知识卡片/` → `骨架/` → `输出卡片/`） |
| 三条硬门禁 + 回退链 | 缺东西就报告缺口 + 给默认动作，不拦 |
| 成稿是 `LOOP-xxx` 特体例 | 成稿**直接就是 01 体例**，`nodeType` 写最终类型 |
| "迁移到 01"是指示性提示 | **动作 E** 承担，含 ID 分配、标题抽取、链接校验 |

## 文件结构

```
kk-obsidian/
├── SKILL.md                      # 主入口：仓库地图、动作选择、五动作细则、全局禁止
├── assets/
│   ├── flash-note.md             # A 捕获 → 00-闪念胶囊
│   ├── atomic-card.md            # B 卡片 → 06/知识卡片
│   ├── skeleton.md               # C 骨架 → 06/骨架
│   └── output-note.md            # D 成稿 → 01 体例模板
└── references/
    ├── writing-rules.md          # 人格（hkc 的声音）
    ├── style-guide.md            # 格式规范 + §13 四层审计清单（唯一权威源）
    └── thinking-models.md        # 结构模型库
```

## 变更记录

### v1.0 — 2026-11-27 初版

- 三合一，去掉阶段状态机
- 成稿体例统一到 01-万象火锅（原 LOOP 体例废弃）
- 新增动作 E（入库），补上原来缺失的迁移环节
- 修正标题 emoji 位置的规则自相矛盾（规则说放前面，示例却有放结尾的）
- `author_voice.md` → `writing-rules.md`，`skeleton_template.md` → `skeleton.md`，其余改名对齐 kebab-case

## 待办

- [ ] 在 DSH 中注册（`ln -s ~/Code/kk-ai/skills/kk-obsidian ~/.dsh/skills/kk-obsidian`）
- [ ] `02-南城BK`（主题涌现）与 `03-0101=100`（跨主题升华）的 skill 仍待建设