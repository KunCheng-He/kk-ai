# .gitignore 规则

## 原则

**只忽略"机器本地的符号链接目录"，让指令文件入库。**

理由：链接指向 `~/Code/kk-ai/...`，换台机器就失效，不该入库；而 `AGENTS.md` / `CLAUDE.md` /
`GEMINI.md` / `.cursor/rules/` 里的 skill 清单是团队协作信息，应该跟仓库走。

## 由脚本写入的规则

脚本按所选 harness 自动生成，示例（`--harness dsh,opencode --type python`）：

```gitignore
# project-init: harness 链接目录（机器本地，不入库）
__pycache__/
*.pyc
.venv/
.env
.DS_Store
.idea/
.vscode/
.dsh/skills/
.opencode/skills/
.opencode/agents/
```

去重写入：已存在的行不会重复追加。

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

## 与旧版的差异

| | 旧版（v2） | 新版（v3） |
|---|---|---|
| 忽略范围 | 整个 `.opencode/` | 只忽略 `.opencode/skills/`、`.opencode/agents/` |
| 多 harness | 无 | 按实际所选 harness 生成 |
| 指令文件 | 未生成 | 生成并**入库** |
| `.gitignore` 已有内容 | 追加 | 逐行去重追加 |
