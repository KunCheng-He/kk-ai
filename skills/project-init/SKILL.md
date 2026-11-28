---
name: project-init
description: |
  多 harness 项目初始化工具。当用户需要创建新项目、初始化项目、设置项目结构、接入新的 AI 编码工具时使用。按 kk-ai 仓库约定初始化：skills/ 下的通用 skill 与 <harness>/ 下的工具专属资源，通过符号链接按需进入项目。触发关键词："初始化项目"、"创建项目"、"新建项目"、"项目初始化"、"设置项目"、"init project"。即使用户未明确提及，但上下文暗示需要开始一个新项目或给项目接入新 harness 时，也应主动使用。
version: 4.1.0
---

# 项目初始化（多 harness）

给一个项目接上该用的 skill 与 agent：从 kk-ai 仓库挑选资源，用**符号链接**放进目标 harness 的项目级目录，并写清库存清单与 `.gitignore`。

本技能只做**项目级**初始化；全局（用户级）链接按需手工维护，不在本技能范围内。

## 仓库结构

kk-ai 仓库只有两层含义，判断的方法很简单：**把它单独拷给别的项目还能用吗？**

| 目录 | 含义 | 谁能用 |
|---|---|---|
| `skills/<name>/` | 通用 skill（纯指令 + 可选脚本/模板） | 任何 harness |
| `<harness>/` | 该工具专属资源，依赖该工具工作 | 只有那个工具 |

`<harness>/` 里放该工具专属的资源（agent、command、专属 skill），**其中的文件增删不需要登记**，脚本直接扫目录。各工具的**项目级目录约定**（skill 放哪、agent 放哪、指令文件叫什么）记在 `scripts/init.sh` 的注册表里，当前支持 `opencode` 和 `pi`。

```
kk-ai/
├── skills/                      # 通用：任何 harness 都可链接
│   ├── research-workflow/
│   ├── mermaid/
│   └── project-init/            # 本 skill
├── opencode/                    # OpenCode 专属
│   ├── agents/                  # → .opencode/agents/
│   ├── cmds/                    # → .opencode/commands/（手动按需）
│   └── skills/                  # → .opencode/skills/（如 loop-by-herdr）
└── pi/                          # Pi 专属
    └── extends/                 # pi-k-subagent / pi-agent-switcher 扩展
```

两层结构、注册表位置、新增 harness 的步骤见 [references/repository.md](references/repository.md)。

## 使用思路

**通用 skill 是"货"，harness 目录是"货架"，符号链接是"取货"。** 初始化做的事就是决定取哪些货、摆到哪个货架：

- 全局要用的 skill → 链接到各 harness 的用户级目录（手工维护）
- 本项目的 skill → 链接到 `<项目>/.opencode/skills/`、`<项目>/.dsh/skills/` 等
- 只对某个工具成立的资源 → 只链到那个工具的目录

链接**用绝对路径**，指向仓库源目录。这样仓库更新一处，所有项目同步生效；换机器时重新初始化即可（所以链接目录不进 git）。

## 工作流程

### 1. 确认目标 harness

先看会话环境自动判断，再让用户确认：

| 线索 | harness |
|---|---|
| `$DSH_SESSION_ID` / `$DSH_HOME` 存在 | `dsh` |
| `$CLAUDECODE` / `$CLAUDE_CODE_ENTRYPOINT` 存在 | `claude-code` |
| `$OPENCODE` 非空且不为 `0` | `opencode` |
| `$GEMINI_CLI` / `$GEMINI_SESSION_ID` 存在 | `gemini-cli` |
| `$PI_SESSION_ID` / `$PI_HOME` 存在 | `pi` |

都不明确时**直接问用户，不要猜**。用户可能要多个（「DSH 和 OpenCode 都要」），也可能只要一个。

### 2. 巡检现状，再决定链什么

**不要凭记忆列资源。** 两件事都要实际读当前仓库和当前项目，因为这两个目录的内容都会变：

```bash
./scripts/init.sh index              # 仓库里现在有哪些 skill、每个 harness 有哪些专属资源
./scripts/init.sh discover {项目路径}  # 项目里现在接了哪些东西（只读，不改文件）
```

`index` 看的是仓库现状，`discover` 看的是项目现状。两者都跑过，才知道是**新建**还是**增量补**，也不会把一个已经不存在的 skill 写进计划。

### 3. 收集需求

- **项目名称/路径**
- **项目类型**（node / python / go / rust / java / universal）— 只影响 `.gitignore` 模板
- **项目要做什么** — 用来判断该挂哪些 skill

### 4. 推荐资源

按项目需求匹配 `index` 的实际输出。下表的「来源」一列就是要用的参数写法：

| 项目情况 | 资源 | 来源 |
|---|---|---|
| 内容创作 / 知识管理（Obsidian、kk-brain） | `kk-obsidian` | 通用 `skills/` |
| 需要调研、竞品分析、选型对比 | `research-workflow` | 通用 `skills/` |
| 需要图表（流程图、时序图、架构图） | `mermaid` | 通用 `skills/` |
| 需要配图、海报提示词 | `image-prompt` | 通用 `skills/` |
| 「我AI了」公众号相关 | `woaile-gzh` | 通用 `skills/` |
| 想把某段流程固化成技能 | `skillify` | 通用 `skills/` |
| 需要设计 agent 工作流 | `workflow-designer` | 通用 `skills/` |
| 需要切换 DSH 会话角色 | `诸葛亮`、`universal-translator` | `opencode/agents/` |
| 需要在 herdr 里跑「执行→审查→优化」循环 | `opencode/loop-by-herdr` | `opencode/skills/` |

**agent 的跨 harness 问题**：`opencode/agents/*.md` 是 markdown + frontmatter，OpenCode 与 Claude Code 原生支持；Pi 的 `k-subagents`/`k-priagent` 也读同格式，脚本会按目标目录改写扩展名。但 **DSH 没有文件式 agent**——只有 DSH 时，二选一并在计划里写明：

1. 把该 agent 的职责改写进一个 skill（推荐）
2. 只把职责写进 `AGENTS.md`,由主 agent 参照执行

### 5. 展示计划并确认

先用 `plan` 预览（不落盘），把结果整理成勾选清单交给用户：

```bash
./scripts/init.sh plan {项目路径} \
  --harness opencode,pi \
  --skill research-workflow,mermaid \
  --agent 诸葛亮 \
  --type python
```

```
## 项目初始化计划

### 目标 harness
- [x] opencode —— .opencode/skills + .opencode/agents + AGENTS.md
- [x] pi —— .pi/k-subagents + .pi/k-priagent + AGENTS.md（skill 目录未核实，不链 skill）

### Skills（源：kk-ai/skills/）
- [ ] research-workflow —— 证据驱动的调研工作流
- [ ] mermaid —— Mermaid 图表

### Agents（源：kk-ai/opencode/agents/）
- [x] 诸葛亮.md —— 思维军师
```

用当前 harness 的提问能力（DSH：`ask_user_question`；OpenCode：`question`）确认，允许调整勾选项。

### 6. 执行初始化

确认后把 `plan` 换成 `init`，参数不变：

```bash
./scripts/init.sh init {项目路径} \
  --harness opencode,pi \
  --skill research-workflow,mermaid \
  --agent 诸葛亮 \
  --type python
```

| 开关 | 作用 |
|---|---|
| `--harness <列表>` | 目标 harness，逗号分隔；缺省自动探测 |
| `--skill <列表>` | 通用 skill 名；带前缀 `opencode/loop-by-herdr` 表示 harness 专属 skill |
| `--agent <列表>` | agent 名，可带前缀 `opencode/诸葛亮`，`.md` 可省略 |
| `--command <列表>` | 只写进清单，不建链接（OpenCode 的 command 按需手动链） |
| `--type <类型>` | `.gitignore` 模板，见 [references/gitignore.md](references/gitignore.md) |
| `--repo-root <路径>` | kk-ai 仓库根（默认由脚本位置推断，也可用 `$KK_AI_ROOT`） |
| `--force` | 已存在的**链接**重建为目标路径；真实文件/目录永不覆盖 |
| `--no-git` / `--no-commit` | 跳过 git init / 初始提交 |

脚本行为要点：

- **先预检**：任一 skill/agent 不存在就直接失败，不留半成品目录
- **幂等**：已就绪的链接跳过；指令文件的受管区块原地刷新，不重复追加
- **不覆盖**：目标位置是真实文件/目录时只告警，`--force` 也不动它
- **按核实状态链接**：注册表里 `h_skills_verified` 为 `false` 的 harness（当前是 Pi）不会收到 skill 链接，并在输出里告警

### 7. 校验

```bash
./scripts/init.sh discover {项目路径}    # 链接是否都指向 kk-ai，有没有断链
cat {项目路径}/AGENTS.md                 # 只有一份受管区块
cat {项目路径}/.gitignore                # 只忽略链接目录
```

### 8. 汇报

```
✅ 项目初始化完成：{项目路径}

🧩 harness：opencode（.opencode/skills + agents）、pi（.pi/k-subagents + k-priagent）
📦 Skills：research-workflow, mermaid          （源 kk-ai/skills/）
📦 Agents：诸葛亮.md                           （源 kk-ai/opencode/agents/）
📄 指令文件：AGENTS.md（已写入受管区块）
⚙️  依赖：mermaid 需要 mmdc（npx @mermaid-js/mermaid-cli）

🚀 下一步：cd {项目路径}
```

汇报里要写清三件事：**东西从仓库哪个位置来**、**落到了项目哪个目录**、**这些 skill 有什么外部依赖**（`mmdc`、Node ≥18、Python 包等，按 `index` 里的说明确认后再说）。

## 注意事项

1. **仓库是唯一数据源**：资源清单一律来自 `index`，不要凭记忆或旧文档列资源
2. **项目现状先巡检**：已有项目一律先 `discover`，避免重复链接或覆盖别人手动放的文件
3. **通用与专属分开**：`skills/` 里的可以给任何 harness；`<harness>/` 里的只给那个 harness,混着链会让别的工具拿到无法工作的文件
4. **只用绝对路径符号链接**：相对链接随目录移动失效；链接目录必须进 `.gitignore`
5. **不删用户内容**：真实文件/目录永不覆盖，`--force` 只作用于链接
6. **DSH 项目必须是 git 仓库**：DSH 用「最近含 `.git` 的祖先目录」判定项目根，再在其中找 `.dsh/skills`
7. **只做项目级**：全局链接是用户级配置，本技能不改

## 参考

- 仓库结构与字段约定 → [references/repository.md](references/repository.md)
- 各 harness 适配矩阵与核实状态 → [references/harnesses.md](references/harnesses.md)
- DSH 专项 → [references/dsh-init.md](references/dsh-init.md)
- OpenCode 专项 → [references/opencode-init.md](references/opencode-init.md)
- Pi 专项 → [references/pi-init.md](references/pi-init.md)
- `.gitignore` 规则 → [references/gitignore.md](references/gitignore.md)