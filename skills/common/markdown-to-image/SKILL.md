---
name: markdown-to-image
description: "将 Markdown 文本或代码片段转换为美观的 PNG/SVG 图片，支持 5 种主题（github, github-dark, notion, carbon, minimal）和代码语法高亮。当用户要求将 Markdown、代码片段、表格转为图片，或提到'生成代码截图'、'markdown to image'、'convert markdown to image'、'代码转图片'、'表格转图片'、'截图分享代码'时使用此技能。即使用户只是想分享一段代码或表格的截图，也应主动使用。"
---

# markdown-to-image

将 Markdown 文本转换为美观的图片，支持多种主题和代码语法高亮。

## 前置条件

首次使用需要在 `scripts` 目录安装依赖：

```bash
cd scripts && npm install
```

> **注意**：puppeteer 需下载 Chromium（约 200MB），`npm install` 可能较慢甚至超时。如遇超时，请手动执行安装，或使用镜像加速：
> ```bash
> PUPPETEER_DOWNLOAD_HOST=https://registry.npmmirror.com/mirrors npm install
> ```

## 使用方式

脚本位于 `skills/common/markdown-to-image/scripts/cli.mjs`，所有命令从 skill 根目录执行。

### 转换 Markdown 文本

```bash
node scripts/cli.mjs --text "# Hello\n\nWorld" -o hello.png
```

### 转换代码片段

```bash
node scripts/cli.mjs --code "console.log('hello')" --lang js -o code.png --theme carbon
```

### 转换 Markdown 文件

```bash
node scripts/cli.mjs input.md -o output.png
```

### 批量转换

```bash
node scripts/cli.mjs *.md -o ./output/ --theme notion
```

## 主题

| 主题 | 描述 | 适用场景 |
|------|------|----------|
| `github` | GitHub 风格，简洁专业 | 通用文档（默认） |
| `github-dark` | GitHub 暗色主题 | 暗色环境 |
| `notion` | Notion 风格，圆角卡片 | 美观展示 |
| `carbon` | 渐变背景 + 窗口红绿灯装饰 | 代码片段分享 |
| `minimal` | 纯白底黑字 | 打印、嵌入 |

## CLI 参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-o, --output <path>` | 输出文件路径或目录 | `output.png` |
| `-t, --theme <theme>` | 主题名称 | `github` |
| `-f, --format <format>` | 输出格式 (png/svg) | `png` |
| `--text <text>` | Markdown 文本 | - |
| `--code <code>` | 代码片段 | - |
| `--lang <lang>` | 代码语言 | 自动检测 |
| `--detect` | 自动检测代码语言 | `false` |

## 示例

**转换表格：**
```bash
node scripts/cli.mjs --text "| Name | Age |
|------|-----|
| Alice | 25 |
| Bob | 30 |" -o table.png --theme notion
```

**转换代码（carbon 主题）：**
```bash
node scripts/cli.mjs --code "def greet(name):
    print(f'Hello, {name}!')" --lang python -o code.png --theme carbon
```

## 注意事项

- 图片宽度自适应内容，无需手动指定
- 图片以 2 倍分辨率输出，确保清晰度
- 代码块自动显示行号
- `carbon` 主题会自动添加窗口装饰（红黄绿按钮）
- 首次运行 puppeteer 启动浏览器需 2-5 秒，后续调用复用实例更快
