---
name: project-init
description: |
  多 harness 项目初始化工具。当用户需要创建新项目、初始化项目、设置项目结构、接入新的 AI 编码工具时使用。根据项目需求推荐 kk-ai 仓库中 shared 目录下的 agent 和 skill，为 DSH / OpenCode / Claude Code / Codex / Gemini CLI / Cursor 等 harness 创建正确的配置目录与符号链接。触发关键词："初始化项目"、"创建项目"、"新建项目"、"项目初始化"、"设置项目"、"init project"。即使用户未明确提及，但上下文暗示需要开始一个新项目或给项目接入新 harness 时，也应主动使用。
version: 3.0.0
---

# 项目初始化（多 harness）

根据项目需求筛选并配置适合的 agent 和 skill，为目标 harness 创建项目级目录结构、符号链接、指令文件清单与 `.gitignore`。

**核心机制**：`scripts/init.sh` 内置 harness 注册表，把「harness 差异」收敛到一处；本文件只描述工作流，具体约定见 `references/`。

## 适配的 harness

| harness | skill 目录 | agent 目录 | 指令文件 |
|---|---|---|---|
| `dsh` | `.dsh/skills/` | — （无文件式 agent） | `AGENTS.md` |
| `opencode` | `.opencode/skills/` | `.opencode/agents/` | `AGENTS.md` |
| `claude-code` | `.claude/skills/` | `.claude/agents/` | `CLAUDE.md` |
| `codex` | `.agents/skills/`（便携） | — | `AGENTS.md` |
| `gemini-cli` | `.agents/skills/`（便携） | — | `GEMINI.md` |
| `cursor` | `.agents/skills/`（便携） | — | `.cursor/rules/project-init.mdc` |
| `generic` | `.agents/skills/` | — | `AGENTS.md` |

细节、验证状态与全局安装命令见 [references/harnesses.md](references/harnesses.md)；DSH 专项见 [references/dsh-init.md](references/dsh-init.md)；OpenCode 专项见 [references/opencode-init.md](references/opencode-init.md)；`.gitignore` 规则见 [references/gitignore.md](references/gitignore.md)。

## 工作流程

### 1. 确定目标 harness

优先自动探测，再让用户确认：

- 当前会话是 DSH → `$DSH_SESSION_ID` / `$DSH_HOME` 存在
- Claude Code → `$CLAUDECODE` 存在
- OpenCode → `$PWD/.opencode` 存在
- 其余不明确时**直接问用户**，不要猜

用户可能同时要多个（如「DSH 和 OpenCode 都要」），也允许 `all`。已经配置过某 harness 时不要重复初始化，改为增量。

### 2. 收集需求

询问用户：

- **项目名称/路径**（`{项目路径}`）
- **项目类型**（node / python / go / rust / java / universal）— 决定 `.gitignore` 模板
- **项目需求**（功能、技术栈、目标），用于推荐资源

### 3. 读取资源清单

不要凭记忆列资源，直接读仓库（单一数据源）：

```bash
~/Code/kk-ai/skills/common/project-init/scripts/init.sh list            # harness + skills + agents 全清单
~/Code/kk-ai/skills/common/project-init/scripts/init.sh list skill      # 只看 skills
```

等价于人工读取 `~/Code/kk-ai/README.md` 的 `Skills - Shared` 与 `OpenCode Agents - Shared` 两张表（脚本是唯一实现，README 是对外摘要）。

### 4. 分析与推荐

按项目需求匹配说明中的关键词：

| 项目类型 | 推荐 Skills | 推荐 Agents |
|----------|-------------|-------------|
| 内容创作/知识管理 | `ob_architect_structure` / `ob_capture_insight` / `ob_refine_card` | `Knowledge Co-Creator` |
| 产品调研 | `research-workflow` | `ResearchReporter` |
| 前端/Web 开发 | `frontend-design` | — |
| 社交媒体运营 | `gzh-workflow` / `woaile-gzh-publisher` | `woaile-gzh-writer` |
| 需要图像素材 | `image-prompt` / `woaile-gzh-imagegen` | — |
| 需要图表 | `mermaid` | — |
| 需要翻译 | — | `universal-translator` |

**agent 兼容性**：`opencode-agents/shared/*.md` 只能在 `opencode` / `claude-code` 下链接。目标只有 `dsh` / `codex` / `gemini-cli` / `cursor` 时，二选一并在计划里说明：

1. 把该 agent 的职责改写进 skill（推荐，DSH 下也可用）
2. 只写进指令文件清单，由主 agent 参照执行

### 5. 展示计划并确认

先 `plan` 预览（不落盘），再把结果整理成计划给用户勾选确认：

```bash
~/Code/kk-ai/skills/common/project-init/scripts/init.sh plan {项目路径} \
  --harness dsh,opencode \
  --skill research-workflow \
  --agent ResearchReporter \
  --type python
```

计划模板：

```
## 项目初始化计划

### 目标 harness
- [x] dsh —— .dsh/skills + AGENTS.md
- [x] opencode —— .opencode/skills + .opencode/agents + AGENTS.md

### 推荐 Skills（来自 README）
- [ ] research-workflow — 产品调研工作流
- [ ] mermaid — Mermaid 图表生成

### 推荐 Agents（来自 README）
- [ ] ResearchReporter.md — 调研报告生成（仅 opencode/claude-code）
```

使用 question 工具让用户确认，并允许调整勾选项。

### 6. 执行初始化

用户确认后，把 `plan` 换成 `init` 执行同一条命令：

```bash
~/Code/kk-ai/skills/common/project-init/scripts/init.sh init {项目路径} \
  --harness dsh,opencode \
  --skill research-workflow,mermaid \
  --agent ResearchReporter \
  --type python
```

常用开关：

| 开关 | 作用 |
|---|---|
| `--force` | 已存在的**符号链接**重建为目标路径（不会删除真实文件/目录） |
| `--no-git` | 跳过 git init / commit |
| `--no-commit` | 只 init，不提交 |
| `--repo-root` | 指定 kk-ai 仓库根（默认自动推断为 skill 上三级目录） |
| `--dry-run` | 同 `plan` |

脚本行为要点：

- **幂等**：已就绪的链接跳过；受管区块（`<!-- project-init:begin/end -->`）原地刷新，不重复追加
- **预检**：skill/agent 不存在时直接失败，不留半成品目录
- **安全**：目标位置已有真实文件/目录时只警告，不覆盖
- **指令文件**：把已链接的 skill/agent 写成清单区块，方便其他协作者与 agent 发现

### 7. 校验结果

```bash
ls -l {项目路径}/.dsh/skills {项目路径}/.opencode/skills    # 链接是否可解析
cat {项目路径}/AGENTS.md                                     # 清单区块
cat {项目路径}/.gitignore
```

检查：链接指向 kk-ai 源目录、指令文件只有一份受管区块、`.gitignore` 只忽略链接目录。

### 8. 汇报

```
✅ 项目初始化完成：{项目路径}

📦 harness：dsh（.dsh/skills）、opencode（.opencode/skills + agents）
📦 Skills：research-workflow, mermaid
📦 Agents：ResearchReporter.md（opencode/.claude 可用）
📄 指令文件：AGENTS.md（已写入清单区块）

🚀 下一步：cd {项目路径}
```

## 注意事项

1. **数据源唯一**：资源清单从 `README.md` / `init.sh list` 读取，避免多处维护
2. **只处理 shared**：`skills/common`、`opencode-agents/common`、`opencode-commands/common` 已全局生效；`--skill` 解析 shared 优先、common 回退（临时项目级固定版本时才用 common）
3. **符号链接**：`ln -s` 绝对路径，便于仓库统一更新
4. **路径验证**：创建前确认目标路径；已有真实文件绝不覆盖
5. **增量添加**：目录已存在时增量补链接与区块，不整体覆盖
6. **Git 初始化**：默认 `git init` + 初始提交；DSH 依赖「最近含 `.git` 的祖先」判定项目根，因此 DSH 项目务必是 git 仓库
7. **harness 差异只在注册表**：新增 harness 只改 `scripts/init.sh` 的 `harness_spec()` 与 `references/harnesses.md` 表格
