---
name: files-to-markdown
description: |
  将文件（PDF、Word、PPT、Excel、图片、HTML、CSV、JSON、XML、EPUB、ZIP、音频、YouTube）转换为 LLM 可读的 Markdown，基于 Microsoft MarkItDown。当用户要读取、查看、分析、提取或总结任何文件/附件/文档内容时必须使用 —— 包括"帮我看下这个文件"、"读一下这个 PDF"、"这 PPT 写了啥"、"Excel 汇总一下"、"图片里的文字提出来"等日常说法。即使用户没提到"转换"，只要涉及读取文件内容就主动使用。切勿直接读取非纯文本文件。Convert files to Markdown for LLM reading. Always use when users want to read/view/analyze any file — even casual requests. Never read non-plain-text files directly.
---

# Files to Markdown 转换技能

将多种文件格式转换为 Markdown，方便 LLM 读取内容。基于 Microsoft MarkItDown，自动识别文件类型并选择最佳转换策略。

## 支持格式

| 类别 | 格式 |
|------|------|
| 办公文档 | PDF、Word (.docx)、PowerPoint (.pptx)、Excel (.xlsx/.xls) |
| 图片 | PNG、JPG、JPEG、GIF、BMP、TIFF、WebP（EXIF + OCR） |
| 音频 | WAV、MP3（EXIF + 语音转文字，需要 OpenAI API key，**会产生费用**） |
| 网页 | HTML、HTM |
| 数据格式 | CSV、JSON、XML |
| 电子书 | EPUB |
| 压缩包 | ZIP（遍历内容） |
| 在线链接 | YouTube URL（获取字幕） |

## 工作流程

1. **确认文件路径**：从上下文中获取用户提到的文件路径（支持相对路径和绝对路径）
2. **运行转换脚本**（在项目工作目录下执行，确保输出落在项目内）：
   ```bash
   uv run --project <skill-path>/scripts python <skill-path>/scripts/convert.py "<file-path>"
   ```
   脚本会自动检测输出是否已存在且是最新的，跳过重复转换。如需强制重转，加 `-f` 参数。
3. **读取生成的 Markdown**：用 Read 工具读取 `markdown-conversions/<file-name>/<file-name>.md`

## 输出结构

```
<项目目录>/markdown-conversions/
└── <文件名>/
    └── <文件名>.md         # 转换后的 Markdown 文件
```

## 首次使用

首次使用需先安装 Python 依赖：

```bash
cd <skill-path>/scripts && uv sync
```

如需 OCR 功能，额外安装：

```bash
cd <skill-path>/scripts && uv sync --extra llm-image
```

## 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `file` | 文件路径（必需） | - |
| `-o, --output-dir` | 转换输出父目录 | `markdown-conversions` |
| `-f, --force` | 强制重新转换（即使已是最新） | `false` |
| `--ocr` | 启用 LLM-based OCR（需安装 `markitdown[llm-image]`） | `false` |
| `--llm-model` | 指定 OCR 所用的 LLM 模型 | - |
| `--version` | 显示版本号 | - |

### 示例

```bash
# 办公文档
uv run --project <skill-path>/scripts python <skill-path>/scripts/convert.py report.pdf
uv run --project <skill-path>/scripts python <skill-path>/scripts/convert.py proposal.docx
uv run --project <skill-path>/scripts python <skill-path>/scripts/convert.py data.xlsx

# 指定输出目录
uv run --project <skill-path>/scripts python <skill-path>/scripts/convert.py paper.pdf -o ./output

# 启用 OCR（图片中的文字识别）
uv run --project <skill-path>/scripts python <skill-path>/scripts/convert.py scan.png --ocr --llm-model gpt-4o

# 强制重新转换
uv run --project <skill-path>/scripts python <skill-path>/scripts/convert.py report.pdf -f
```

## 重要规则

1. **`.gitignore`**：确保 `markdown-conversions/` 已加入项目的 `.gitignore`，避免将临时文件提交到仓库。脚本会检查 `.gitignore` 并在缺失时发出警告
2. **缓存机制**：脚本会比较源文件修改时间和输出文件时间，自动跳过未变化的文件。使用 `-f` 可强制重转
3. **按需读取**：转换完成后，优先使用 Read 工具局部读取 Markdown 中需要的章节，而不是一次性加载整个文件，以节省上下文
4. **音频转录费用**：音频转文字依赖 OpenAI Whisper API，会**产生 API 费用**。仅在用户明确需要音频内容时才转换，并在转换前提醒用户
5. MarkItDown 基于文件扩展名自动选择转换器，无需手动指定文件类型

## 常见问题

| 问题 | 解决方案 |
|------|----------|
| `ModuleNotFoundError` | `cd <skill-path>/scripts && uv sync` |
| 大文件转换慢 | 正常现象，MarkItDown 会按需加载相关转换器。如超时可尝试 `-f` 跳过缓存强制重试 |
| 转换结果为空或内容不完整 | 检查是否安装了完整依赖（`'markitdown[all]'`），或文件是否损坏。图片文件可尝试 `--ocr` 启用 LLM OCR |
| 音频转文字需要 API key | 音频转录依赖 OpenAI Whisper API，需设置 `OPENAI_API_KEY` 环境变量。**此过程会产生 API 费用** |
| 图片文字识别效果差 | 安装 `markitdown[llm-image]` 并使用 `--ocr` 参数启用 LLM OCR |
| 文件未找到 | 确保路径正确，支持相对和绝对路径。脚本会尝试列出当前目录中的近似文件名 |
