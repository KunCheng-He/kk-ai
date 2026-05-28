---
name: kimi-webbridge
description: |
  Kimi WebBridge 允许 AI 控制用户的真实浏览器 —— 使用用户的实际登录会话进行导航、点击、输入、阅读、截图以及与任何网站交互。当用户想要与网站交互、自动化浏览器任务、抓取网页内容或执行任何需要真实浏览器的操作时，请使用此技能。当用户提到“浏览器”、“网页”、“打开 URL”、“截图”或要求阅读/与任何网站交互时，也请使用此技能。即使是简单的浏览器请求，也请使用它 —— 守护进程会处理所有复杂性。
---

# Kimi WebBridge

通过位于 `http://127.0.0.1:10086` 的本地守护进程控制用户的真实浏览器（包含其登录会话）。

## 健康检查（务必先执行此操作）

```bash
~/.kimi-webbridge/bin/kimi-webbridge status
```

根据结果采取行动：

- **`running: true` 且 `extension_connected: true`** —— 状态健康。继续执行下方的工具调用。
- **其他任何情况**（未找到命令、`running: false`、`extension_connected: false`、错误） —— **阅读此技能目录中的 `references/operations.md`**。它包含安装/启动/诊断路由表。

不要在这里猜测修复方法 —— 所有非健康状态都在 `references/operations.md` 中处理。

## 工具 (Tools)

| 工具 | 参数 | 返回值 | 备注 |
|------|------|---------|------|
| `navigate` | `url`, `newTab`(bool), `group_title` | `{success, url, tabId}` | 首次调用务必使用 `newTab:true`。`group_title` 设置标签组的可见标签 |
| `find_tab` | `url`, `active`(bool) | `{success, url, tabId}` | **复用已打开的标签页** —— 传递任何 URL 或域名；`active:true` 选择用户当前查看的标签页，默认选择最左侧匹配的标签页 |
| `snapshot` | — | `{url, title, tree}` (带 `@e` 引用) | **无障碍树** (文本) —— 使用此工具阅读页面内容并定位元素 |
| `click` | `selector` (@e 引用或 CSS) | `{success, tag, text}` | 模拟 `el.click()` |
| `fill` | `selector`, `value` | `{success, tag, mode}` | 适用于 `<input>`/`<textarea>` 和 `[contenteditable]` (ProseMirror/Lexical/Slate)。`mode` 为 `"value"` 或 `"contenteditable"` |
| `evaluate` | `code` (支持 async/await) | `{type, value}` | |
| `screenshot` | `format`(png\|jpeg), `quality`(0-100), 可选 `selector` (@e/CSS) | `{format, dataLength, data}` (base64) | 全屏截图会使上下文过载 —— 使用辅助脚本（保存到磁盘，返回路径）。使用 `selector` 时仅捕获该元素（体积小，可直接调用 API） |
| `network` | `cmd`(start\|stop\|list\|detail), `filter`, `requestId` | 请求/响应数据 | |
| `upload` | `selector`, `files`(string[]) | `{success, fileCount}` | |
| `save_as_pdf` | `paper_format`, `landscape`, `scale`, `print_background`, `file_name` | `{path, sizeBytes, mimeType, pageTitle}` | 将当前页面渲染为 PDF，保存在 `/tmp/kimi-webbridge-pdfs/` 下 |
| `list_tabs` | — | `{success, tabs:[{tabId, url, title, active, groupTitle}]}` | 检查当前会话中的标签页 |
| `close_tab` | — | `{success, closed: bool}` | 关闭会话中的当前标签页 |
| `close_session` | — | `{success, closed: int}` | 关闭所有标签页 —— `closed` 是数量。务必在任务结束时调用 |

### 使用 find_tab

当用户明确要求对已打开的标签页进行操作时，请使用 `find_tab`。它按域名匹配，因此同一站点上的任何 URL 都有效。不带 `active:true` 时，返回最左侧匹配的标签页；带 `active:true` 时，返回用户当前正在查看的标签页 —— 当用户说“用我打开的 X” / “在我当前的 X 页面上”时请传递此参数。

```bash
curl -s -X POST http://127.0.0.1:10086/command \
  -d '{"action":"find_tab","args":{"url":"https://www.kimi.com","active":true},"session":"kimi"}'
```

如果 `find_tab` 返回 "no open tab found"，则页面未打开 —— 请退而使用 `navigate` 并设置 `newTab:true`。

### 调用格式

```bash
curl -s -X POST http://127.0.0.1:10086/command \
  -H 'Content-Type: application/json' \
  -d '{"action":"navigate","args":{"url":"https://example.com","newTab":true}}'
```

## 会话 (Sessions)

每个会话映射到一个独立的浏览器标签组。为不同的站点使用不同的会话名称，以保持操作隔离。

在请求体中添加 `"session":"name"`：

```bash
curl -s -X POST http://127.0.0.1:10086/command \
  -d '{"action":"navigate","args":{"url":"https://example.com","newTab":true},"session":"my-task"}'
```

并行处理多个站点时，务必分配不同的会话名称。

## 截图：使用辅助脚本

**切勿直接调用截图 API** —— 它会返回 base64 编码的图像数据（数百 KB 的文本），这会淹没上下文窗口。

请使用 `scripts/screenshot.sh` 代替。它会解码图像并将其保存到磁盘，仅返回文件路径：

```bash
# 默认值 —— 保存到 /tmp/kimi-webbridge-screenshots/{timestamp}.png
bash "$(dirname "$SKILL_PATH")/scripts/screenshot.sh"

# 指定会话
bash "$(dirname "$SKILL_PATH")/scripts/screenshot.sh" -s my-task

# 自定义输出路径
bash "$(dirname "$SKILL_PATH")/scripts/screenshot.sh" -o /tmp/page.png

# JPEG 格式，质量 60
bash "$(dirname "$SKILL_PATH")/scripts/screenshot.sh" -f jpeg -q 60
```

获取文件路径后，使用 Read 工具查看图像。

如果 `$SKILL_PATH` 不可用，请通过其绝对路径调用脚本。

## 优先使用 snapshot 而非 CSS/JS 选择器

`snapshot` 返回带有基于语义角色/名称的 `@e` 引用的交互元素。直接在 click/fill 中使用它们 —— 它们在 CSS 类哈希更改（这会破坏手动编写的选择器）后依然有效。

仅在以下情况退而使用 `evaluate` (JS)：
- 目标在快照中没有 `@e` 引用
- 你需要快照中没有的属性（例如 `href`）
- 你需要调度复杂的事件序列，或滚动页面

## Evaluate 技巧

- 务必使用紧凑的 `JSON.stringify(data)` —— 切勿添加 `null, 2` 格式化。缩进和换行符会使响应膨胀数倍，导致传输过程中发生截断。
- `evaluate` 调用共享页面的 JS 领域 —— 在两次调用中重新声明相同的 `const`/`let` 会抛出 `SyntaxError`。请将其封装在 IIFE 中以获得新的作用域：`(() => { const x = ...; return x; })()`。

## 文本输入 —— 使用 fill

`fill` 处理所有三种形状的文本输入。传递选择器（CSS 或 `@e` 引用）+ 值：

| 目标 | `fill` 的操作 | 返回的 `mode` |
|--------|------|------|
| `<input>` / `<textarea>` | 通过原生 setter 设置 `.value`，触发 `input`/`change`。 | `"value"` |
| `[contenteditable]` (ProseMirror / TipTap / Lexical / Slate / Quill 等) | 聚焦，选择所有现有内容，调用 `document.execCommand('insertText', ...)`，这会触发 `beforeinput`/`input`，其 `inputType` 为 `'insertText'`，`data` 为 `value`。 | `"contenteditable"` |
| 其他元素 | 尽力而为的 `.value` + 事件。 | `"value"` |

`fill` 是**清空并插入**：现有内容将被替换。对于“追加到现有文本”，请通过 `evaluate` 读取当前值，拼接，然后使用结果进行 `fill`。

## 表单提交 / 特殊按键

没有单独的“按 Enter 键”工具。要提交表单，请直接点击提交按钮（在 @e 引用或选择器上执行 `click`）。要以编程方式分派按键事件（例如按 Escape 关闭模态框）：

```bash
{"action":"evaluate","args":{"code":"document.activeElement.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}))"}}
```

## 将当前页面保存为 PDF

`save_as_pdf` 将当前页面渲染为 PDF，将其写入 `/tmp/kimi-webbridge-pdfs/`，并返回文件路径（守护进程会剥离 base64 —— Agent 永远不会看到原始 PDF 字节）。

所有参数均为可选：
- `paper_format`: `letter` (默认) \| `a4` \| `legal` \| `a3` \| `tabloid`
- `landscape`: `false` (默认)
- `scale`: `1.0` (默认), 范围 `[0.1, 2.0]`
- `print_background`: `true` (默认) —— 保留背景颜色
- `file_name`: 调用者提供的名称；如果缺失，则派生自页面标题

解码后的 PDF 上限为 100 MB。超过此限制，守护进程将拒绝；请减小 `scale` 或拆分页面。

## 已知局限

- **严格检查 `event.isTrusted` 的站点**（某些银行门户、验证码挑战）会拒绝 `fill` 和 `click`，因为两者都通过 DOM 级合成事件 (`isTrusted=false`)。这是一个产品边界，而不是错误 —— 任何在用户机器上运行而不夺取 OS 焦点的自动化原语都无法在这些站点上产生受信任的事件。
- **跨域 iframe**：`fill`、`click`、`evaluate` 和 `snapshot` 在顶层框架上操作。如果目标元素位于来自不同源的同页 iframe 中（例如嵌入式沙箱演示），请直接导航到该 iframe 的 URL。

## 版本 (Versions)

守护进程、扩展和此技能共享 1:1 的版本字符串。通过以下方式读取两者：

```bash
~/.kimi-webbridge/bin/kimi-webbridge status
# {"version":"<daemon>", "extension_version":"<extension>"}
```

如果工具返回包含 **"Please update the Kimi WebBridge extension"** 的错误，说明用户的扩展版本低于此技能。请告知用户：

> 请更新 Kimi WebBridge 浏览器扩展后重试：https://kimi.com/features/webbridge

不要重试失败的工具。不要根据 `extension_version` 自动切换技能版本 —— 配对协议尚未最终确定。
