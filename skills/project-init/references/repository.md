# 仓库结构与 harness 注册表

`project-init` 只认两件事：**仓库怎么分层**，以及**脚本里那份 harness 注册表**。没有额外的配置文件。

## 两层结构

```
kk-ai/
├── skills/<name>/               通用 skill —— 任何 harness 都能链接
│   ├── SKILL.md                 必需，frontmatter 含 name + description
│   ├── references/              按需读的细则
│   ├── scripts/                 可选，可执行脚本
│   └── （无元数据文件）          版本号写在 SKILL.md frontmatter 的 version 里
│
└── <harness>/                   工具专属 —— 依赖该工具才能工作
    ├── agents/*.md              → 该工具的 agent 目录
    ├── cmds/*.md                → 该工具的 command 目录（脚本不自动链接）
    ├── skills/<name>/           → 该工具专属的 skill
    └── extends/                 扩展/插件源码，不被链接
```

判断某个资源该放哪一层，只有一个问题：**把它单独拷给另一个项目、换一个 harness，还能不能用？**

- 能（纯指令、纯脚本、纯模板）→ `skills/`
- 不能（用到该工具专属的目录约定、frontmatter 字段、运行时 API）→ `<harness>/`

## 什么是「注册」、什么不是

这里有个容易混淆的点，先说清楚：

| | 谁负责 | 需要登记吗 |
|---|---|---|
| `skills/<name>/` | 通用层 | **不用**：脚本扫描目录即得 |
| `<harness>/agents/`、`cmds/`、`skills/` **里的文件** | harness 专属资源 | **不用**：脚本扫描目录即得 |
| `<harness>/` 对应工具的**项目级目录约定** | 工具本身的事 | **要**：写进脚本的注册表 |

也就是说：往 `opencode/agents/` 里加三个 agent，什么都不用改，`index` 立刻能列出来；
但「OpenCode 项目的 skill 应该放在 `.opencode/skills`」这条规律，脚本必须知道，否则不知道往哪儿链。

## 注册表在哪

就在 `scripts/init.sh` 的「harness 注册表」一段，核心是一个 case 分派：

```bash
ALL_HARNESSES="opencode pi"

h_skills_dir() {
  case "$1" in
    opencode) echo ".opencode/skills" ;;
    *)        echo "" ;;          # 空 = 该工具没有 skill 机制
  esac
}

h_agent_dirs() {
  case "$1" in
    opencode) printf '%s\n' ".opencode/agents" ;;
    pi)       printf '%s\n' ".pi/k-subagents" ".pi/k-priagent" ;;
    *)        : ;;
  esac
}
```

| 函数 | 回答什么 | 空值含义 |
|---|---|---|
| `ALL_HARNESSES` | 支持哪些 harness | — |
| `h_skills_dir` | 项目级 skill 目录放哪 | 没有 skill 机制 |
| `h_skills_verified` | 这条路径在真机上核实过吗 | 未核实 → 不链接通用 skill |
| `h_agent_dirs` | 项目级 agent 目录有哪些（可多个） | 没有文件式 agent |
| `h_instructions` | 项目级指令文件叫什么 | 不写指令文件 |
| `h_instructions_mode` | `block`（受管区块）或 `mdc`（Cursor 带 frontmatter） | 默认 block |
| `harness_status` | `index` 里展示的核实状态 | — |

`h_skills_verified` 是这个注册表里最值得留神的一项：**没核实过的路径不要装作能工作。** Pi 就是这种情况——目录写进去了，但技能机制没确认，所以 `false`，脚本不会往 Pi 项目里链 skill。

## 新增一个 harness

以新增 `foo` 为例：

1. 建 `foo/`，放好它专属的资源（`agents/`、`cmds/`、`skills/` 按需）
2. 在 `ALL_HARNESSES` 加 `foo`
3. 补 `h_skills_dir` / `h_agent_dirs` / `h_instructions` 的分支；路径没核实就把 `h_skills_verified` 留成 `false`
4. 补 `harness_status`
5. `./scripts/init.sh index` — 确认新 harness 出现、路径正确
6. `./scripts/init.sh plan /tmp/demo-foo --harness foo --skill mermaid` — 确认落点
7. 真机打开项目，确认它能发现 skill/agent
8. 核实通过后：`h_skills_verified` 改 `true`，在 [harnesses.md](harnesses.md) 表格补一行并标 ✅

改动只落在注册表那一段（约 60 行），主流程逻辑不用动。

## 仓库内容会变

`index` 与 `discover` 存在的意义就是**不要缓存记忆**：

```bash
./scripts/init.sh index              # 当前仓库有什么
./scripts/init.sh discover <项目>     # 当前项目接了什么
```

skill 会被删除、合并、改名（例如旧的三件套 `ob_*` 被合并成 `kk-obsidian`）。初始化前跑一遍 `index`，就能避免把已经不存在的名字写进计划。