---
name: mermaid
description: |
  使用 Mermaid 语法生成图表，并通过 mmdc CLI 渲染为 SVG/PNG/PDF 文件。当用户要求创建流程图、时序图、类图、状态图、ER 图、甘特图、饼图、思维导图、时间线、Git 图、架构图、看板、象限图，或任何 Mermaid 支持的图表类型时使用此技能。当用户提到 "mermaid"、".mmd"、"mmdc"，或希望将关系、流程、架构、数据流等可视化为图表时也触发。即使用户只是说"画个图"、"画个流程图"、"画个时序图"、"做个图"而未指定工具，也应主动使用。
---

# Mermaid 画图技能

使用 Mermaid 的文本语法创建图表，并通过 `mmdc` CLI 工具渲染为图片文件（SVG/PNG/PDF）。

## 工作流程

1. **识别图表类型**：根据用户需求对照[图表类型表](#图表类型)
2. **查阅语法参考**：仅读取 `references/syntax.md` 中对应类型的章节。该文件带目录，用 grep 定位章节标题行号后再用 read 的 offset/limit 按区间加载，不要一次性读入整个文件（详见[查阅语法参考](#查阅语法参考)）
3. **编写 Mermaid 语法**：用 Write 工具写入当前工作目录下的 `.mmd` 文件
4. **渲染为指定格式**：用 `mmdc` 命令渲染（见[渲染输出](#渲染输出)）
5. **打开结果**（见[打开结果](#打开结果)）
6. **保留 `.mmd` 文件**：渲染成功后保留 `.mmd` 文件，便于用户不满意时修改重渲
7. **删除中间文件**：仅当用户明确确认满意后，才删除 `.mmd` 文件

## 图表类型

根据用户意图选择图表类型。确定类型后，仅从 `references/syntax.md` 读取对应章节的语法，不需要加载其他章节。

| 用户意图 | 图表类型 | Mermaid 关键字 |
|---------|---------|----------------|
| 流程、决策、工作流 | 流程图 | `graph` / `flowchart` |
| 参与者之间的时序交互 | 时序图 | `sequenceDiagram` |
| 类/对象结构、继承关系 | 类图 | `classDiagram` |
| 状态转换、生命周期 | 状态图 | `stateDiagram-v2` |
| 数据库表与关系 | ER 图 | `erDiagram` |
| 项目排期、里程碑、任务 | 甘特图 | `gantt` |
| 占比、百分比 | 饼图 | `pie` |
| Git 分支/合并历史 | Git 图 | `gitGraph` |
| 用户体验步骤（含满意度打分） | 用户旅程图 | `journey` |
| 围绕中心主题的层级结构 | 思维导图 | `mindmap` |
| 按时间排列的事件/路线图 | 时间线图 | `timeline` |
| 2x2 战略定位 | 象限图 | `quadrantChart` |
| C4 架构 / 桑基图 / 看板 / 树状图 / 韦恩图 / 石川图 等 | 见 `references/syntax.md` 中的"其他图表类型" | 不定 |

## 查阅语法参考

`references/syntax.md` 收录了完整的图表语法，文件较长（>400 行）。为节省上下文，只加载当前需要的章节，不要整文件读入。

推荐的区间加载方法（以"用户旅程图"为例）：

1. 用 grep 定位目标章节起始行：
   ```bash
   grep -n "^## 用户旅程图" references/syntax.md
   ```
2. 用 grep 列出所有 `## ` 标题行，找到紧随目标章节之后的下一个标题，得到结束行：
   ```bash
   grep -n "^## " references/syntax.md
   ```
3. 用 read 的 `offset` / `limit` 只读取该区间：
   - `offset` = 目标章节起始行
   - `limit` = 下一章节起始行 - 目标章节起始行

`references/syntax.md` 顶部已提供目录，可先读取前 ~25 行了解章节命名，再按上述方法精确定位。

## 选择输出格式

根据用户请求判断：

- `画个流程图` / 未指定格式 → 默认 **SVG**
- `png 流程图` / `导出为 png` → PNG
- `画个甘特图，要 pdf` → PDF

SVG 为默认格式：可缩放、清晰、适合文档嵌入。

| 格式 | 扩展名 | 适用场景 |
|------|--------|---------|
| SVG | `.svg` | 默认。可缩放，任意分辨率都清晰，适合文档 |
| PNG | `.png` | 幻灯片 / 不支持 SVG 的文档场景 |
| PDF | `.pdf` | 打印场景 |

## 渲染输出

### 前置检测

渲染前必须先用 `which mmdc` 检测 CLI 是否已安装：

```bash
which mmdc
```

- **已安装**：返回路径，直接进入下一步渲染
- **未安装**：命令无输出或返回非零。此时**不要**自行执行 `npm install` 等安装命令，应停止流程并提示用户：

  > 未检测到 `mmdc`（Mermaid CLI）。请先安装后再使用本技能：
  >
  > ```bash
  > npm install -g @mermaid-js/mermaid-cli
  > ```
  >
  > 或使用 npx 免安装运行（每次执行会临时下载）：
  >
  > ```bash
  > npx -p @mermaid-js/mermaid-cli mmdc -i diagram.mmd -o diagram.svg
  > ```
  >
  > 安装完成后告知我，我会继续渲染。

  等待用户确认安装完成后再继续，避免擅自改动用户环境。

> 仓库地址：https://github.com/mermaid-js/mermaid-cli ；官方文档：https://mermaid.nodejs.cn/

### 基本命令

```bash
mmdc -i <输入.mmd> -o <输出.svg>
```

### 常用参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `-i, --input` | 输入 `.mmd` 文件（`-` 表示从 stdin 读取） | `-i diagram.mmd` |
| `-o, --output` | 输出文件路径 | `-o diagram.svg` |
| `-t, --theme` | 主题：`default`、`forest`、`dark`、`neutral` | `-t dark` |
| `-b, --backgroundColor` | 背景色（仅 PNG/SVG） | `-b transparent` |
| `-w, --width` | 页面宽度 px（默认 800） | `-w 1200` |
| `-H, --height` | 页面高度 px（默认 600） | `-H 900` |
| `-s, --scale` | Puppeteer 缩放因子（默认 1） | `-s 2` |
| `-c, --configFile` | Mermaid JSON 配置文件 | `-c config.json` |
| `-C, --cssFile` | 自定义 CSS 文件 | `-C style.css` |
| `-q, --quiet` | 静默模式，不输出日志 | `-q` |
| `-f, --pdfFit` | PDF 自动缩放以适应图表（仅 PDF） | `-f` |

### 示例

```bash
# 渲染为 SVG（默认）
mmdc -i flowchart.mmd -o flowchart.svg

# 渲染为 PNG，暗色主题，透明背景
mmdc -i flowchart.mmd -o flowchart.png -t dark -b transparent

# 渲染为 PDF，自动缩放适配
mmdc -i gantt.mmd -o gantt.pdf -f

# 静默模式，保持终端整洁
mmdc -q -i diagram.mmd -o diagram.svg

# 通过 stdin 输入，无需中间文件（适合小型图表）
mmdc -i - -o diagram.svg <<'EOF'
graph TD
    A[客户端] --> B[负载均衡]
EOF
```

### 高级配置

需要自定义主题变量、布局选项或时序图设置时，创建 JSON 配置文件：

```json
{
  "theme": "base",
  "themeVariables": {
    "primaryColor": "#4A90D9",
    "lineColor": "#888"
  },
  "flowchart": { "curve": "basis" }
}
```

```bash
mmdc -c config.json -i diagram.mmd -o diagram.svg
```

完整配置项见 [Mermaid 配置 Schema](https://mermaid.nodejs.cn/config/schema-docs/config.html)。

### 处理 Markdown 文件

如果 Markdown 文件中包含 ```mermaid 代码块，`mmdc` 可以一次性提取并渲染其中所有图表：

```bash
mmdc -i document.md -o document-rendered.md
```

## 打开结果

| 环境 | 命令 |
|------|------|
| macOS | `open <文件>` |
| Linux | `xdg-open <文件>` |
| WSL2 | `cmd.exe /c start "" "$(wslpath -w <文件>)"` |
| Windows | `start <文件>` |

打开后，输出文件的绝对路径也一并打印，以便打开命令失败时用户能手动定位。

## 文件命名

- 基于图表内容的有意义命名：`login-flow`、`database-schema`、`deployment-architecture`
- 多词名称使用小写加连字符
- 扩展名反映格式：`login-flow.svg`、`gantt-chart.png`

## 渲染前校验

Mermaid 对语法要求严格。写入 `.mmd` 文件前先在心里检查：

- 第一行是合法的图表关键字（`graph`、`sequenceDiagram`、`classDiagram` 等）
- 节点 ID 不含空格（用方括号/引号包裹的 label 来显示文本）
- 标签中的特殊字符用引号包裹：`A["节点 (含括号)"]`
- 箭头类型合法（`-->`、`->>`、`-->>`、`-.-`、`==>`）
- 流程图关键字后需跟方向（`TD`、`LR`、`BT`、`RL`）

如果 `mmdc` 报解析错误，根据错误信息定位行号、修正 `.mmd` 文件后重试。

## 主题

用 `-t` 切换视觉主题，无需修改图表内容：

| 主题 | 适用场景 |
|------|---------|
| `default` | 默认，清爽文档风格，多数场景适用 |
| `forest` | 绿色调，自然/环保主题 |
| `dark` | 暗色幻灯片 / 夜间模式文档 |
| `neutral` | 灰度，正式 / 印刷报告 |

## 排错

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 解析错误 / unknown error | Mermaid 语法不合法 | 阅读错误信息，修正 `.mmd` 文件后重试 |
| 输出空白 | 图表关键字缺失或拼写错误 | 第一行必须以合法关键字开头 |
| 含特殊字符的标签出错 | 字符未转义 | 用引号包裹标签：`A["节点 (文本)"]` |
| 节点 ID 含空格失败 | ID 必须是单个标识符 | 用 camelCase 或下划线做 ID，文本放在 label 中 |
| Puppeteer/Chrome 启动报错 | 无头浏览器不可用 | 创建 `puppeteer-config.json` 加 `{"args": ["--no-sandbox"]}`，通过 `-p` 传入 |
| 大图被截断 | 默认页面过小 | 增大 `-w` / `-H`，或用 `-s` 缩放 |