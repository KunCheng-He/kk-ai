# Harness 适配矩阵

`project-init` 用一张注册表驱动：每个 harness 只需声明 **项目级 skill 目录**、**项目级 agent 目录**、**指令文件**。
注册表实现在 `scripts/init.sh` 的 `harness_spec()`，本文件是它的文档镜像——改一处要同步另一处。

## 一览

| harness | skill 目录 | agent 目录 | 指令文件 | 文件式 agent | 验证状态 |
|---|---|---|---|---|---|
| `dsh` | `.dsh/skills/` | — | `AGENTS.md` | ❌ | ✅ DSH 源码 + 本机实测 |
| `opencode` | `.opencode/skills/` | `.opencode/agents/` | `AGENTS.md` | ✅ | ✅ 本机已长期使用 |
| `claude-code` | `.claude/skills/` | `.claude/agents/` | `CLAUDE.md` | ✅ | ⚠️ 公共约定，未在本机复核 |
| `codex` | `.agents/skills/`（便携，非原生） | — | `AGENTS.md` | ❌ | ⚠️ 指令文件高置信，skill 走便携目录 |
| `gemini-cli` | `.agents/skills/`（便携） | — | `GEMINI.md` | ❌ | ⚠️ 同上 |
| `cursor` | `.agents/skills/`（便携） | — | `.cursor/rules/project-init.mdc` | ❌ | ⚠️ 规则文件带 frontmatter |
| `generic` | `.agents/skills/` | — | `AGENTS.md` | ❌ | ✅ 结构通用，未知 harness 的兜底 |

验证状态含义：

- ✅：从该 harness 的实现源码或本机实际配置确认过
- ⚠️：遵循公开约定，但本机没有该 CLI，**首次在真机使用时请复核**（复核方式：初始化后用该 harness 打开项目，确认它能发现 skill/agent，再回来修正本表）

## 为什么有的 harness 用 `.agents/skills`

`.agents/skills/` 是 agent-skills 生态的便携位置，**DSH 自己也扫描它**（见 [dsh-init.md](dsh-init.md) 的根目录表，rank 200）。
因此对没有原生 skill 机制的 harness（codex / gemini-cli / cursor / 未知工具），策略是：

1. skill 实体链接到 `.agents/skills/` —— 位置稳定、可被任何支持该约定的工具读到
2. 在该 harness 的指令文件里写一份清单区块 —— 让只读 `AGENTS.md`/`GEMINI.md` 的 agent 也能发现这些 skill

这不是"假装支持"，而是**用指令文件做桥**：skill 目录本身是真实可读的，只是发现入口换成了指令文件。

## 各 harness 细节

### dsh（DeepSeek Harness）

- 项目级 skill 根：`<projectRoot>/.dsh/skills`，**projectRoot 取最近含 `.git` 的祖先目录**；没有 `.git` 时退化为当前工作目录
- 无文件式 agent 目录：subagent 是运行时服务，不从 `.dsh/agents` 加载
- 指令文件：`AGENTS.md`（项目链 + `$DSH_HOME/AGENTS.md` 用户级链，`CLAUDE.md` 兼容并去重）
- 专项说明见 [dsh-init.md](dsh-init.md)

### opencode

- skill：`.opencode/skills/<name>/SKILL.md`
- agent：`.opencode/agents/<name>.md`（frontmatter 含 `description`、`mode`、`tools` 等）
- command：`.opencode/commands/<name>.md`（本 skill 不自动链接 command）
- 指令文件：`AGENTS.md`
- 专项说明见 [opencode-init.md](opencode-init.md)

### claude-code

- skill：`.claude/skills/<name>/SKILL.md`
- agent：`.claude/agents/<name>.md`（同样是 markdown + frontmatter，因此 kk-ai 的 OpenCode agent 可直接复用）
- 指令文件：`CLAUDE.md`
- 注意：Claude Code 的项目根发现基于当前目录与其配置，不要求 git 仓库

### codex

- 指令文件：`AGENTS.md`（Codex 的原生上下文文件）
- 无原生项目级 skill 机制 → skill 走 `.agents/skills/`

### gemini-cli

- 指令文件：`GEMINI.md`
- 无原生项目级 skill 机制 → skill 走 `.agents/skills/`

### cursor

- 指令文件：`.cursor/rules/project-init.mdc`，脚本会自动补 YAML frontmatter：

  ```yaml
  ---
  description: 项目规则（project-init 生成）
  globs: **/*
  alwaysApply: true
  ---
  ```

- 无原生项目级 skill 机制 → skill 走 `.agents/skills/`

### generic

给不出结论的 harness 用这一档：`.agents/skills/` + `AGENTS.md`。
先按通用结构落地，确认对方约定后再补专用 harness 条目。

## agent 跨 harness 可移植性

| 源 | 可链接到 | 说明 |
|---|---|---|
| `opencode-agents/shared/*.md` | `opencode`、`claude-code` | 都是 markdown + frontmatter，字段高度重合 |
| 同上 | `dsh` / `codex` / `gemini-cli` / `cursor` | ❌ 无文件式 agent；改写成 skill 或写进指令文件清单 |

脚本对不支持 agent 的 harness 会给出警告而不是静默跳过。

## 全局（用户级）安装对照

项目级是"按需链接"；全局除 DSH 外整体链接 `common` 目录，DSH 采用逐 skill 链接。各 harness 的全局位置：

| harness | 全局 skill 链接 | 全局指令文件链接 |
|---|---|---|
| opencode | `~/.config/opencode/skills` → `~/Code/kk-ai/skills/common` | `~/.config/opencode/AGENTS.md` → `AGENTS.global.md` |
| dsh | 逐 skill：`~/.dsh/skills/<skill>` → `~/Code/kk-ai/skills/common/<skill>` | `~/.dsh/AGENTS.md` → `AGENTS.global.md` |
| claude-code | `~/.claude/skills` → `~/Code/kk-ai/skills/common` | `~/.claude/CLAUDE.md` → `AGENTS.global.md` |
| codex / gemini-cli / cursor | `~/.agents/skills` → `~/Code/kk-ai/skills/common` | `~/.agents/AGENTS.md` → `AGENTS.global.md` |

注意：`ln -s` 目录级链接要求目标位置**不存在**同名目录。DSH 不使用目录级链接——`~/.dsh/skills` 是真实目录，里面逐 skill 建链接（当前为 `mermaid`、`project-init`、`skillify`、`workflow-designer`）。新增 common skill 后若不补链接，DSH 侧不会出现该 skill。

## 新增一个 harness

1. 在 `scripts/init.sh` 的 `harness_spec()` 里加分支，设置 `H_SKILLS` / `H_AGENTS` / `H_DOC`
2. 把名字加入 `ALL_HARNESSES` 与 `harness_desc()`
3. 在本文件表格加一行（含验证状态）
4. `./scripts/init.sh list harness` 自检，再 `plan` 一个临时项目确认路径
5. 真机打开项目验证能发现 skill/agent，把验证状态改成 ✅
