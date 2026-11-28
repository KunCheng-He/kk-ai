# Harness 适配矩阵

每个 harness 的项目级约定写在 `<harness>/harness_meta.json` 里，本文件是它的说明书。
**改一处要同步另一处，但以 JSON 为准**——`init.sh` 只读 JSON。

关于字段含义与新增 harness 的步骤，见 [repository.md](repository.md)。

## 一览

| harness | skill 目录 | agent 目录 | 指令文件 | 文件式 agent | 验证状态 |
|---|---|---|---|---|---|
| `opencode` | `.opencode/skills/` ✅ | `.opencode/agents/` ✅ | `AGENTS.md` | ✅ | ✅ 本机长期使用 |
| `pi` | — （待核实） | `.pi/k-subagents/`、`.pi/k-priagent/` ✅ | `AGENTS.md` | ✅（需装扩展） | ⚠️ agent 目录来自扩展 README；skill 机制未核实 |
| `dsh` | `.dsh/skills/` ✅ | — | `AGENTS.md` | ❌ | ✅ DSH 源码 + 本机实测 |
| `claude-code` | `.claude/skills/` ⚠️ | `.claude/agents/` ⚠️ | `CLAUDE.md` | ✅（markdown + frontmatter） | ⚠️ 公开约定，本机未复核 |
| `codex` | `.agents/skills/` ⚠️ | — | `AGENTS.md` | ❌ | ⚠️ 指令文件高置信，skill 无原生机制 |
| `gemini-cli` | `.agents/skills/` ⚠️ | — | `GEMINI.md` | ❌ | ⚠️ 同上 |
| `cursor` | `.agents/skills/` ⚠️ | — | `.cursor/rules/project-init.mdc` | ❌ | — 规则文件带 frontmatter |

> 只有 `opencode/` 与 `pi/` 在仓库里有 `harness_meta.json`，所以脚本**当前只能初始化这两个**。
> 表里其余的 harness 是已确认的路径约定；要用时新建对应目录和 JSON，按 [repository.md](repository.md) 的步骤走。

验证状态含义：

- ✅：从该 harness 的实现源码或本机实际配置确认过
- ⚠️：遵循公开约定，但本机没有该 CLI 或没有该机制，**首次在真机使用时请复核**（复核方式：初始化后用该 harness 打开项目，确认它能发现 skill/agent，再把 `harness_meta.json` 与本文改对）

## 两个概念的区分

这张表里有两个「agent」含义，别混：

| | 含义 | 归属 |
|---|---|---|
| 文件式 agent | 一份 markdown + frontmatter，定义角色、工具白名单、模型 | `<harness>/agents/` → 各工具自己的 agent 目录 |
| 运行时子代理 | 该工具派发独立上下文执行的机制（DSH 的 `subagent`、OpenCode 的 `task`） | 平台能力，不靠文件 |

DSH 有后者没有前者。这是它唯一的结构性差异，别的地方都只是路径不同。

## 各 harness 细节

### opencode

- skill：`.opencode/skills/<name>/SKILL.md`
- agent：`.opencode/agents/<name>.md`（frontmatter 含 `description`、`mode`、`temperature` 等）
- command：`.opencode/commands/<name>.md`（**脚本不自动链接**，需要时手动 `ln -s`）
- 指令文件：`AGENTS.md`
- 仓库侧：`opencode/agents/`、`opencode/cmds/`、`opencode/skills/`
- 专项说明见 [opencode-init.md](opencode-init.md)

### pi

- agent 目录有两个，用途不同：
  - `.pi/k-subagents/` —— `pi-k-subagent` 扩展的子代理定义
  - `.pi/k-priagent/` —— `pi-agent-switcher` 扩展的主会话角色
- 两级作用域：项目级 `.pi/...` 或全局 `~/.pi/agent/...`
- 指令文件：`AGENTS.md`
- **skill 机制未核实**，所以 `skills_verified: false`，脚本不会把通用 skill 链进 Pi 项目
- 专项说明见 [pi-init.md](pi-init.md)

### dsh

- 项目级 skill 根：`<项目根>/.dsh/skills`，**项目根 = 最近含 `.git` 的祖先目录**
- 无文件式 agent 目录：subagent 是运行时服务，不扫 `.dsh/agents`
- 指令文件：`AGENTS.md`（另兼容 `CLAUDE.md`，同名内容去重）
- 专项说明见 [dsh-init.md](dsh-init.md)

### claude-code

- skill：`.claude/skills/<name>/SKILL.md`
- agent：`.claude/agents/<name>.md`（markdown + frontmatter，与 OpenCode 高度重合）
- 指令文件：`CLAUDE.md`
- 项目根发现不要求 git 仓库

### codex / gemini-cli / cursor

- 都没有原生项目级 skill 机制 → 通用 skill 落到便携目录 `.agents/skills/`
- 靠指令文件做桥：在 `AGENTS.md` / `GEMINI.md` / `.cursor/rules/*.mdc` 里写一份清单，让只读指令文件的 agent 也能发现这些 skill
- `.agents/skills/` 是 agent-skills 生态的便携位置，DSH 自己也扫它（rank 200）
- Cursor 的规则文件需要 YAML frontmatter，`instructions_mode: "mdc"` 会自动补：

  ```yaml
  ---
  description: 项目规则（project-init 生成）
  globs: **/*
  alwaysApply: true
  ---
  ```

## agent 跨 harness 可移植性

| 源 | 可落到 | 说明 |
|---|---|---|
| `opencode/agents/*.md` | `.opencode/agents/`、`.claude/agents/` | 原生同构 |
| `opencode/agents/*.md` | `.pi/k-subagents/`、`.pi/k-priagent/` | 格式兼容（markdown + frontmatter），但 `mode`/`temperature` 等字段 Pi 不认，需按 Pi 字段调整 |
| 以上任一 | `.dsh/` | ❌ 无文件式 agent，改写为 skill 或写进 `AGENTS.md` |

脚本对跨 harness 的 agent 会**告警但仍按其通用格式链接**，因为它只认扩展名。字段差异要自己看一遍。

## 全局（用户级）配置不在本技能范围

`project-init` 只做项目级。全局安装由手工维护，位置参考（**这是约定，不代表本机已经装好**）：

| harness | 全局 skill 位置 | 全局指令文件 |
|---|---|---|
| dsh | `~/.dsh/skills/<skill>`（逐 skill 建链接，目录本身是真实的） | `~/.dsh/AGENTS.md` |
| opencode | `~/.config/opencode/skills/<skill>` | `~/.config/opencode/AGENTS.md` |
| claude-code | `~/.claude/skills/<skill>` | `~/.claude/CLAUDE.md` |
| pi | `~/.pi/agent/k-subagents/`、`~/.pi/agent/k-priagent/` | — |

原则与项目级一样：只链接明确要用的那几个，**不要**把整个 `skills/` 目录链进去——那样以后新增的 skill 会无条件暴露给所有项目。