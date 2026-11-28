# Pi 初始化细节

Pi 在仓库里以 `pi/extends/` 的两个扩展存在，所以它的约定来自**扩展**而不是 Pi 核心：

| 扩展 | 提供什么 | 项目级目录 |
|---|---|---|
| `pi-k-subagent` | 子代理：独立进程、独立上下文 | `.pi/k-subagents/` |
| `pi-agent-switcher` | 主会话角色切换（`/agent`、`Alt+A`） | `.pi/k-priagent/` |

全局对应位置是 `~/.pi/agent/k-subagents/` 与 `~/.pi/agent/k-priagent/`；项目级同名角色优先于全局。

## 关键事实

- **agent 是文件式的**：markdown + YAML frontmatter（`name`、`description`、`model`、`tools`、`thinking`、`systemPromptMode`）
- **两个目录用途不同**，别混：`k-subagents` 给子代理运行时读，`k-priagent` 给主会话角色选择器读
- 扩展没装时，这些目录存在也不会生效
- **Pi 核心是否有 skill 目录机制尚未核实** → `pi/harness_meta.json` 里 `skills_dir` 为空、`skills_verified: false`，脚本**不会**把通用 skill 链进 Pi 项目

所以 Pi 版 `project-init` 当前只做三件事：建 agent 目录、链接 agent、写 `AGENTS.md` 清单。

## 用脚本初始化

```bash
./scripts/init.sh plan ~/Code/my-proj --harness pi --agent 诸葛亮
./scripts/init.sh init ~/Code/my-proj --harness pi --agent 诸葛亮
```

产物：

```
my-proj/
├── .pi/k-subagents/<agent>.md     # → kk-ai/opencode/agents/<agent>.md
├── .pi/k-priagent/<agent>.md      # 同上
├── AGENTS.md                      # 受管区块列出已链接的 agent
└── .gitignore                     # 忽略 .pi/k-subagents/、.pi/k-priagent/
```

如果同时指定 `--harness opencode,pi`，同一个 agent 文件会落到三处（`.opencode/agents/`、`.pi/k-subagents/`、`.pi/k-priagent/`）。脚本会提示该 agent 原本属于 OpenCode 的约定。

## 手动等价命令

```bash
mkdir -p {项目}/.pi/k-subagents {项目}/.pi/k-priagent

ln -s ~/Code/kk-ai/opencode/agents/{agent}.md {项目}/.pi/k-subagents/{agent}.md
ln -s ~/Code/kk-ai/opencode/agents/{agent}.md {项目}/.pi/k-priagent/{agent}.md
```

## agent 字段差异

OpenCode 的 frontmatter 是 `description` / `mode` / `temperature` / `permission`；
Pi 只认 `name` / `description` / `model` / `tools` / `thinking` / `systemPromptMode`。

直接链接**能跑**（多出的字段被忽略），但要注意：

- `mode: subagent` / `mode: primary` 在 Pi 里没有意义——落在哪个目录就由哪个扩展管
- `permission` 白名单在 Pi 里没有等价物，Pi 用 `tools` 做白名单
- 长期在 Pi 用某个角色，值得为它单独写一份 Pi 版定义放进 `pi/agents/`

## skill 机制待核实

核实方法：装好 Pi 后，看它是否扫描某个目录下的 `SKILL.md`（类似 `.pi/skills/` 或 `.agents/skills/`），
能否在会话里被触发。确认后：

1. 把 `pi/harness_meta.json` 的 `skills_dir` 填上真实路径，`skills_verified` 改 `true`
2. 在 [harnesses.md](harnesses.md) 更新 Pi 一行
3. 不需要改 `init.sh`

在那之前，Pi 项目想用通用 skill，只能手动把 `SKILL.md` 内容并进 `AGENTS.md`，其余文件按相对路径引用。这是降级做法，不要写成"Pi 支持 skill"。

## 校验

```bash
./scripts/init.sh discover {项目}
```

在 Pi 里确认：`/agents` 能列出角色（`k-priagent`），`/subagents` 能触发子代理（`k-subagents`）。