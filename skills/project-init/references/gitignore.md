# .gitignore 规则

## 原则

**只忽略"机器本地的符号链接目录"，让指令文件入库。**

理由：链接指向 `~/Code/kk-ai/...`——仓库在本机哪个路径、别人是不是放在同一处，都不确定；换台机器链接就失效，不该入库。
而 `AGENTS.md` / `CLAUDE.md` / `GEMINI.md` / `.cursor/rules/` 里的资源清单是团队协作信息，应该跟仓库走。

## 由脚本写入的规则

脚本按所选 harness **实际链了什么**生成，不是照着 harness 名字硬套：

```gitignore
# project-init: harness 链接目录（机器本地链接，不入库）
__pycache__/
*.pyc
.venv/
.env
.DS_Store
.idea/
.vscode/
.opencode/skills/
.opencode/agents/
.pi/k-subagents/
.pi/k-priagent/
```

以 `--harness opencode,pi --type python` 为例。去重写入：已是同样内容的行不会重复追加。

注意几点：

- 只有**真的建了链接的**目录才会被忽略。比如只选 Pi 且没链 agent 时，`.pi/*` 不会被写进 `.gitignore`
- **skill 目录未核实的 harness 不会产生 skill 忽略项**（Pi 就是这种情况）
- `--dry-run` / `plan` 会逐行列出将要追加的内容

## 基础规则（按项目类型）

| 类型 | 追加规则 |
|---|---|
| `node` | `node_modules/`、`dist/`、`.env`、`*.log` |
| `python` | `__pycache__/`、`*.pyc`、`.venv/`、`.env` |
| `go` | `*.exe`、`*.test`、`vendor/` |
| `rust` | `target/` |
| `java` | `*.class`、`*.jar`、`target/` |
| `universal` | （仅通用） |

所有类型都会带上：`.DS_Store`、`.idea/`、`.vscode/`。

## 不该忽略的东西

| 路径 | 为什么 |
|---|---|
| `AGENTS.md` / `CLAUDE.md` / `GEMINI.md` | 资源清单要入库，团队与 agent 都看它 |
| `.opencode/opencode.json`、`.opencode/plugin/` | 真实配置，不是链接；旧版整目录忽略 `.opencode/` 把它们误伤了 |
| `.cursor/rules/*.mdc` | 项目规则，要入库 |

## 与旧版的差异

| | v3 | v4 |
|---|---|---|
| harness 覆盖 | 硬编码 7 档 | 只按仓库里真实存在的 `harness_meta.json` |
| skill 源 | `skills/shared` + `skills/common` | 只有 `skills/` |
| 忽略项来源 | 按 harness 名字套 | 按**实际建立的链接目录** |
| 未核实路径 | 也照链 | 不链、也不写忽略项 |