# woaile-gzh · 单 skill 版架构说明

「我AI了」公众号运营的整合版 skill。替代原来由 `gzh-workflow` + 6 个角色/工具 skill 串联的结构。

当前状态：**已入库**. 本目录是唯一在用的版本，位于 `kk-ai/skills/woaile-gzh`。旧版 `gzh-workflow`、`woaile-gzh-imagegen`、`woaile-gzh-publisher` 已从 `skills-old/shared/` 删除（git 历史可回溯）。

## 结构

```text
woaile-gzh/
├── SKILL.md                 # 唯一入口：六阶段、三关口、硬规则（不含写作/审查规范正文）
├── harness/
│   ├── dsh.md               # DSH：subagent 派生/续接、web_fetch/ego-browser、发布命令
│   └── opencode.md          # OpenCode：task 派生、webfetch、发布命令
├── roles/
│   ├── writer.md            # 写作规范（唯一来源，约 1400 字）
│   └── reviewer.md          # 审查清单（唯一来源，约 500 字）
├── references/
│   ├── research.md          # 调研结果的结构约定与版式门禁
│   ├── image-style.md       # 品牌视觉权威定义（原 imagegen 的 style-guide，含规格速查与质检）
│   └── samples/             # 版式样本 ×3 + 小爱定妆照 ×1（生图时上传）
└── scripts/
    └── publisher/           # 发布器（含 .venv）：Markdown → 公众号草稿箱
```

## 与旧结构的对应

| 旧 skill | 新位置 | 处理 |
|---|---|---|
| `gzh-workflow` | `SKILL.md` | 六阶段与三关口保留，删掉工具名与两套平台写法 |
| `woaile-gzh-writer` | `roles/writer.md` | 全量搬入，措辞未改 |
| `woaile-gzh-reviewer` | `roles/reviewer.md` | A–G 七组保留 |
| `research-workflow` | 外部独立工作流 | 不再内联；本 skill 只规定调用参数、检索对象、结果结构 |
| `research-reporter` | `references/research.md` | 模板与 10 条门禁保留 |
| `browser-researcher` | `SKILL.md` 阶段 2 + `harness/*.md` | 产物规则与证据标准保留，工具用法移到 harness |
| `woaile-gzh-imagegen` | `references/image-style.md` | 风格规范原样搬入；工具选择与质检表补进文末 |
| `woaile-gzh-publisher` | `scripts/publisher/` | 整目录复制，`.venv` 可用（已 `themes` 冒烟通过） |

## 解决的问题

1. **单入口**：原来 7 个 skill 各自有 description，模型容易只加载其中一个就开跑（例如跳过复审直接发布）。现在只有一个入口，流程完整性由同一份文件保证。
2. **工具名收口**：`SKILL.md` 不出现 `subagent` / `task` / `web_fetch` / `ego-browser` 等字眼，只写「派一个独立上下文的执行者」「静态取数」「交互式采集」。具体工具全部在 `harness/<平台>.md`。
3. **跨 Harness**：换平台只需要新增一个 `harness/<平台>.md`，正文不改。DSH 与 OpenCode 两份已写好。
4. **不再依赖 kk-ai**：发布器脚本、图片风格规范、样本图都复制进本目录，不受 `kk-ai` 重组（`skills/shared` → `skills-old/shared`）影响。
5. **只服务这一个号**：账号定位、品牌色板、排版主题、发布通道都写死在 skill 内，不再假装通用。

## 上下文预算

| 文件 | 汉字 | 何时进入上下文 |
|---|---|---|
| `SKILL.md` | ~3400 | 每次触发，常驻 |
| `roles/*.md` | ~1900 | 只进执行者上下文，主 Agent 只传路径 |
| `harness/*.md` | ~1200 | 开跑前读一次 |
| `references/*.md` | ~6900 | 按需 |

对比旧方案：`gzh-workflow` + writer + reviewer 共 8526 字，其中入口 4223 字常驻；新方案入口 3400 字常驻，另两份移到 `roles/` 不进主上下文。

## 审阅要点

- 外部调研工作流的约定是否够用（当前只规定参数、检索对象、结果结构、五项核对）
- 生图原则「有直接能力就直接出图，没有则出提示词」是否够明确，是否需要在 harness 层再细
- `roles/` 拆出来后，OpenCode 侧是否接受「薄壳 agent + 引用 roles」的做法

## 已知未完成

- `.venv` 不入库（已在 `.gitignore` 的 `.venv/` 覆盖范围内）。首次使用或换机器需重建：在 `scripts/publisher/` 执行 `uv sync`；本机 uv 缓存目录被沙箱拦截时改用 `UV_CACHE_DIR=$TMPDIR/uv-cache uv sync`。已重建并验证 `themes`、`convert` 正常。
- `harness/opencode.md` 未经实测：`.opencode/agents/` 下的薄壳角色文件尚未创建，`task` 续接语义未验证。
- 外部调研工作流指向 `kk-ai/skills/research-workflow`（v0.1.0），尚未做一次连通性验证。
- 旧 gzh skill 已删除，不存在双入口问题。