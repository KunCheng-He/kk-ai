# kk-ai

[![GitHub stars](https://img.shields.io/github/stars/KunCheng-He/kk-ai?style=flat-square)](https://github.com/KunCheng-He/kk-ai/stargazers)
[![Last commit](https://img.shields.io/github/last-commit/KunCheng-He/kk-ai?style=flat-square)](https://github.com/KunCheng-He/kk-ai/commits/main)

一个**跨 harness 的 AI 资源仓库**：集中存放通用 skill、各 AI 编码工具专属的 agent / command / 扩展，供不同项目按需**符号链接**取用。

适配的 harness 包括 DeepSeek Harness（DSH）、OpenCode、Pi，以及以后可能接入的其他工具。

> [!IMPORTANT]
> 本仓库**不是一个可运行的项目**：没有构建、没有依赖安装、没有测试套件。它是一堆被别的项目"取用"的资产。
> 适合的场景：你在用 AI 编码工具，想把自己反复用的工作流沉淀成 skill，并在多个项目间共用；否则它大概不是你要找的库。

---

## 核心思路

三层比喻贯穿整个仓库：

> **通用 skill 是"货"，harness 目录是"货架"，符号链接是"取货"。**

- 需要某个能力时，把仓库里的目录 `ln -s` 到工具会扫描的位置
- 链接一律用**绝对路径**指向仓库源目录：仓库改一处，所有项目同步生效
- 因此链接目录不进 git，换机器重新链接即可

仓库只有两层结构，判断依据只有一句话：**把它单独拷给另一个项目、换一个 harness，还能不能用？**

| 目录 | 含义 | 谁能用 |
|---|---|---|
| [`skills/`](skills/) | 通用 skill（纯指令 + 可选脚本/模板，不依赖某个平台） | 任何 harness |
| [`<harness>/`](opencode/) | 该工具专属资源（agent、command、专属 skill、扩展源码） | 只有那个工具 |

`<harness>/` 里的内容对别的工具没有意义。所以不要把 OpenCode 专属的东西塞进 `skills/`，也不要让 `skills/` 下的技能硬依赖某个平台。

---

## 目录结构

```
kk-ai/
├── skills/                  通用层：任何 harness 都能用的 skill
│   └── <name>/              SKILL.md 必需；references/ scripts/ assets/ 按需
├── opencode/                OpenCode 专属层
│   ├── agents/              agent 定义（markdown + frontmatter）
│   ├── cmds/                command 定义
│   └── skills/              OpenCode 专属 skill
├── pi/                      Pi 专属层
│   └── extends/             扩展源码
├── AGENTS.md                仓库运行手册（给 agent 看的）
└── README.md                本文件（给人看的）
```

内容都在持续增删，所以这里**不列清单**——列出就一定会过期。想知道现在有什么，跑命令：

```bash
skills/project-init/scripts/init.sh index            # 仓库现在有哪些 skill 与 harness 专属资源
skills/project-init/scripts/init.sh discover <项目>   # 某个项目现在接了什么
```

`index` 会扫目录实时生成：通用 skill 及其 description、每个 harness 的项目级目录约定与核实状态、该 harness 下 `agents/` `cmds/` `skills/` 的全部资源。增删文件后立刻可见，**不需要改任何登记文件**。

---

## 快速开始

### 方式一：用 `project-init` 技能（推荐）

[`skills/project-init`](skills/project-init/SKILL.md) 是其他所有 skill 进入项目的方式。给一个项目接上资源：

```bash
# 1. 看仓库里有什么、项目里现在接了什么（只读）
skills/project-init/scripts/init.sh index
skills/project-init/scripts/init.sh discover <项目路径>

# 2. 先预览计划，不落盘
skills/project-init/scripts/init.sh plan <项目路径> --harness opencode --skill mermaid --agent 诸葛亮

# 3. 确认后执行
skills/project-init/scripts/init.sh init <项目路径> --harness opencode --skill mermaid --agent 诸葛亮
```

参数写法：

- 通用 skill 用 `--skill <name>`（如 `--skill mermaid`）
- harness 专属资源要带前缀：`--skill opencode/loop-by-herdr`、`--agent opencode/诸葛亮`

`init` 会建好目录、链接资源、在指令文件里写入受管区块、补 `.gitignore`。脚本是**幂等**的：已就绪的跳过，`--force` 只重建链接，并且绝不覆盖目标位置的真实文件。

完整的推荐资源表、跨 harness 注意事项见 [`skills/project-init/SKILL.md`](skills/project-init/SKILL.md)。

### 方式二：手工建链接

等价操作，一行搞定：

```bash
# 全局（用户级）：让所有项目都能用
ln -s <本仓库>/skills/<name> ~/.dsh/skills/<name>
ln -s <本仓库>/skills/<name> ~/.config/opencode/skills/<name>

# 项目级：只让某个项目用
ln -s <本仓库>/skills/<name> <项目>/.opencode/skills/<name>
ln -s <本仓库>/skills/<name> <项目>/.dsh/skills/<name>
```

> 只链接明确要用的那几个，**不要**把整个 `skills/` 链进去——那样以后新增的 skill 会无条件暴露给所有项目。

---

## 已适配的 harness

各工具的项目级目录约定记在 `skills/project-init/scripts/init.sh` 的「harness 注册表」段，[`harnesses.md`](skills/project-init/references/harnesses.md) 是它的说明书与验证状态表。

| harness | skill 目录 | agent 目录 | 指令文件 |
|---|---|---|---|
| `opencode` | `.opencode/skills/` | `.opencode/agents/` | `AGENTS.md` |
| `pi` | 待核实 | `.pi/k-subagents/`、`.pi/k-priagent/` | `AGENTS.md` |
| `dsh` | `.dsh/skills/` | 无文件式 agent | `AGENTS.md` |
| `claude-code` | `.claude/skills/` | `.claude/agents/` | `CLAUDE.md` |
| `codex` / `gemini-cli` / `cursor` | `.agents/skills/` | 无 | `AGENTS.md` / `GEMINI.md` / `.cursor/rules/` |

**当前注册表里只有 `opencode` 与 `pi`**，所以脚本目前只能初始化这两个；其余是已确认的路径约定，要接入时按 [`repository.md`](skills/project-init/references/repository.md) 的步骤改注册表。

一个容易混淆的区别：**文件式 agent**（一份 markdown + frontmatter，写到工具的 agent 目录）和**运行时子代理**（工具自己派发独立上下文的能力）是两回事。DSH 只有后者、没有前者——在纯 DSH 环境下，agent 的职责要么改写成一个 skill，要么写进 `AGENTS.md`。

---

## 仓库原则

本仓库的规矩都写在 [`AGENTS.md`](AGENTS.md)（新会话会被 agent 自动加载）。对外使用者最需要知道的三条：

1. **如无必要，勿增实体** —— 不加空目录、不加预留字段、不加没人用的抽象层。能删就删。
2. **一个事实只写一处** —— 路径、命令、开关只写在唯一的地方，别处引用而不是复制。
3. **会变的东西，写"怎么查"而不是"是什么"** —— 所以本 README 和 `AGENTS.md` 都不列 skill 清单。

另外，**本仓库只保存自研 skill**。三方 skill 走外部安装（直接 `ln -s` 到用户级或项目级目录，更新靠源仓 `git pull`），不复制进来再靠元数据文件"跟踪上游"。

`AGENTS.md` 里还写了新增 skill、新增 harness、提交规范（Conventional Commits，摘要用中文）等完整流程。

---

## Star 增长

<a href="https://star-history.com/#KunCheng-He/kk-ai&Timeline">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=KunCheng-He/kk-ai&type=Timeline&theme=dark" />
    <img alt="kk-ai 的 Star History（时间线）" src="https://api.star-history.com/svg?repos=KunCheng-He/kk-ai&type=Timeline" width="700" />
  </picture>
</a>
