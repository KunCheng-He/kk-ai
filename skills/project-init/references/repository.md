# 仓库结构与 harness 声明

`project-init` 不硬编码任何 harness 的路径。它读仓库现状，所以仓库怎么长,它就怎么工作。

## 两层结构

```
kk-ai/
├── skills/<name>/               通用 skill —— 任何 harness 都能链接
│   ├── SKILL.md                 必需，frontmatter 含 name + description
│   ├── references/              按需读的细则
│   ├── scripts/                 可选，可执行脚本
│   └── upstream.json            可选，来源与版本元数据
│
└── <harness>/                   工具专属 —— 依赖该工具才能工作
    ├── harness_meta.json        必需，声明项目级目录约定（见下）
    ├── agents/*.md              → 该工具的 agent 目录
    ├── cmds/*.md                → 该工具的 command 目录（脚本不自动链接）
    ├── skills/<name>/           → 该工具专属的 skill
    └── extends/                 扩展/插件源码，不被链接
```

判断某个资源该放哪一层，只有一个问题：**把它单独拷给另一个项目、换一个 harness，还能不能用？**

- 能（纯指令、纯脚本、纯模板）→ `skills/`
- 不能（用到该工具专属的目录约定、frontmatter 字段、运行时 API）→ `<harness>/`

## harness_meta.json

每个 harness 目录下的这份文件是**唯一**的约定来源。脚本与文档都从中读，改这里就够。

```json
{
  "label": "OpenCode",
  "source_dir": "opencode",
  "skills_dir": ".opencode/skills",
  "skills_verified": true,
  "agents": [
    { "dir": ".opencode/agents", "ext": ".md", "verified": true }
  ],
  "instructions": "AGENTS.md",
  "instructions_mode": "block",
  "status": "一句话说明核实到什么程度",
  "notes": "给使用者看的补充说明"
}
```

| 字段 | 必填 | 说明 |
|---|---|---|
| `label` | 否 | 展示名，缺省用目录名 |
| `source_dir` | 否 | 仓库内该 harness 的资源目录，缺省 = 目录名 |
| `skills_dir` | 否 | 项目级 skill 目录；**空字符串 = 该 harness 没有 skill 机制** |
| `skills_verified` | 否 | `false` 时脚本**不会**把通用 skill 链进来，只告警。未在真机确认前一律写 `false` |
| `agents` | 否 | 数组，每项 `{dir, ext, verified}`；可列多个目录（如 Pi 有两个 agent 目录） |
| `instructions` | 否 | 项目级指令文件路径 |
| `instructions_mode` | 否 | `block`（写受管区块，默认）或 `mdc`（额外补 Cursor 的 YAML frontmatter） |
| `status` / `notes` | 否 | 给人看的说明，`index` 会打印出来 |

`skills_verified` 与 `agents[].verified` 是这个文件的重点：**没核实过的路径不要装作能工作。** 核实之后把它改成 `true`，并在 [harnesses.md](harnesses.md) 同步验证状态。

## 新增一个 harness

以新增 `foo` 为例：

1. 建目录 `foo/`，放好它专属的资源（`agents/`、`cmds/`、`skills/` 按需）
2. 写 `foo/harness_meta.json`，`skills_verified` 先填 `false`
3. `./scripts/init.sh index` — 确认新 harness 出现、路径正确
4. `./scripts/init.sh plan /tmp/demo-foo --harness foo --skill mermaid` — 确认落点
5. 在真机上打开项目，确认它能发现 skill/agent
6. 核实通过后：把 `skills_verified` / `verified` 改成 `true`，在 [harnesses.md](harnesses.md) 表格补一行，验证状态标 ✅

**不需要改 `scripts/init.sh`。** 脚本只认目录与这份 JSON；没有任何 harness 名字硬编码在逻辑里。

## 脚本如何看仓库

`init.sh` 启动时扫描仓库根下所有含 `harness_meta.json` 的一级目录，把它们当作可用 harness。所以：

- 目录没有 `harness_meta.json` → 完全不被识别（比如只放文档的目录）
- `--harness` 给了不存在的名字 → 报错并列出当前可用项
- 仓库根由脚本位置推断（`skills/project-init/scripts/init.sh` 上三级），也可以用 `--repo-root` 或 `$KK_AI_ROOT` 覆盖

## 仓库内容会变

`index` 与 `discover` 子命令存在的意义就是**不要缓存记忆**：

```bash
./scripts/init.sh index              # 当前仓库有什么
./scripts/init.sh discover <项目>     # 当前项目接了什么
```

skill 会被删除、合并、改名（例如旧的三件套 `ob_*` 被合并成 `kk-obsidian`）。初始化前跑一遍 `index`，就能避免把已经不存在的名字写进计划。