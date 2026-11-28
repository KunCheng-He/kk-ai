# research-workflow

证据驱动的调研工作流包：方法、类型模板、角色契约、平台适配、可执行门禁。

它不是某个 harness 的配置，而是一套**可搬走的方法**。方法层正文里没有工具名、没有平台名、没有项目路径——所以换平台只改一份适配文件，不重写流程。

## 设计原则

1. **方法层只写能力，不写实现。** 派发、续接、提问、取数这些动作以能力动词描述（见 `harness/_contract.md`），具体工具名只在 `harness/<平台>.md` 出现。
2. **角色与流程分离。** 流程是"先采集、冻结、再写作"；角色是"我是谁、交什么"。前者在 `SKILL.md` 与 `references/`，后者在 `roles/`，由各平台自己实例化（agent 文件、子代理 prompt、子代理定义）。
3. **门禁可执行。** "证据完整""引用可追溯"不靠自觉：`scripts/` 下两个零依赖脚本判定，退出码非 0 就不许进下一步。

## 目录

```
research-workflow/
├── SKILL.md                     # 入口：阶段总览 + 三条硬规则 + 文件索引（约 80 行）
├── references/
│   ├── brief.md                 # 简报、范围档位、停止条件
│   ├── tasks.md                 # 逻辑任务 T0–T5 与派发契约
│   ├── evidence.md              # 证据 schema、编号、冻结协议、冲突合并
│   ├── writing.md               # 通用版式与引用规范
│   ├── screenshot.md            # 截图分级与图表获取
│   ├── gates.md                 # 门禁判据
│   └── templates/               # _skeleton + product / selection / local / learning / industry
├── roles/                       # browser-collector / report-writer / fact-checker
├── harness/                     # _contract + dsh / opencode / pi
├── scripts/                     # check-evidence.mjs / check-report.mjs
└── examples/mini-run/           # 最小可运行示例（用于验证脚本与结构）
```

## 接入（3 步）

通用流程：**放包 → 写项目约定 → 选平台适配**。

### 1. 放包

放到你的技能目录，或任意路径后由项目约定指出位置：

| 平台 | 技能目录（按你的平台当前文档为准） |
|---|---|
| DSH | `<项目根>/.dsh/skills/research-workflow/`，或 `<项目根>/.agents/skills/`（DSH 实测会扫） |
| OpenCode | `.opencode/skills/research-workflow/` |
| Claude Code | `.claude/skills/research-workflow/` |
| 无技能机制的平台 | 任意目录，把 `SKILL.md` 内容并入项目指令文件 |

### 2. 写项目约定

方法层不知道自己在这个项目里该怎么落地。**至少**在项目 `AGENTS.md` 里补这 6 项：

1. 工作目录与文件命名（报告、证据、资源各自叫什么、放哪）。
2. 语言与读者（报告语言、术语偏好）。
3. 数据源政策（平台优先级、禁用平台、平台特有的打开方式）。
4. 浏览器/取数通道（用哪个工具，是否禁止安装其他浏览器）。
5. 默认模板类型（`product` / `selection` / `local` / `learning` / `industry`）。
6. 交付物形态（只要报告，还是另有 PPT、蓝图、发布稿）。

### 3. 选平台适配

读 `harness/<平台>.md`，按里面 3–5 条完成实例化：

- **DSH**：`harness/dsh.md` — 子代理派生与续接、子代理不能派生/不能提问的规避、角色怎么随 prompt 传递。
- **OpenCode**：`harness/opencode.md` — 文件式 agent 加 `permission`、任务续接、权限白名单。
- **Pi**：`harness/pi.md` — `k-subagents` 定义、无续接时的降级。
- **其他平台**：`harness/_contract.md` 里有能力清单和新建适配文件的模板。

## 依赖与运行

Node.js ≥ 18，无第三方包。

```bash
# 证据冻结门禁：全部通过才退出 0
node scripts/check-evidence.mjs <证据文件...>

# 报告终审：结构、引用、URL、日期、表格、图片
node scripts/check-report.mjs <报告文件> [--evidence <证据文件...>] [--strict]
```

两个脚本都有 `--json` 输出，便于接 CI。用 `examples/mini-run/` 可以先跑通：

```bash
cd examples/mini-run
node ../../scripts/check-evidence.mjs browser_results.md
node ../../scripts/check-report.mjs report.md --evidence browser_results.md
```

## 边界

- 不含：视觉蓝图、PPT 生成、公众号发布、截图渲染。这些是下游环节，按需另接。
- 不含：任何平台专属配置（模型、权限、审批策略）。这些属于适配层或项目层。
- 不含：许可证。发布前请自行选择并补 `LICENSE`。

## 版本

`SKILL.md` frontmatter 的 `version` 记录当前版本；改动方法层视为次版本变更，改动仅适配层视为补丁。
