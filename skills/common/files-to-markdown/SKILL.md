---
name: files-to-markdown
description: |
  将任意文件格式（PDF、Word、PPT、Excel、图片、HTML、CSV、JSON、XML、EPUB、ZIP、音频、YouTube 等）转换为 LLM 可读的 Markdown，基于 Microsoft MarkItDown。当用户需要读取、分析、提取文档/附件内容，或提到文件转markdown、文档解析、附件转换、提取内容时，先调用此 skill 转换再读取结果。即使用户只是说"帮我看看这个文件"或"读一下这个附件"，没有明确说要转换，也应主动使用。
---

# Files to Markdown 转换技能

将多种文件格式转换为 Markdown，方便 LLM 读取内容。基于 Microsoft MarkItDown，自动识别文件类型并选择最佳转换策略。

## 支持格式

| 类别 | 格式 |
|------|------|
| 办公文档 | PDF、Word (.docx)、PowerPoint (.pptx)、Excel (.xlsx/.xls) |
| 图片 | PNG、JPG、JPEG、GIF、BMP、TIFF、WebP（EXIF + OCR） |
| 音频 | WAV、MP3（EXIF + 语音转文字） |
| 网页 | HTML、HTM |
| 数据格式 | CSV、JSON、XML |
| 电子书 | EPUB |
| 压缩包 | ZIP（遍历内容） |
| 在线链接 | YouTube URL（获取字幕） |

## 工作流程

1. **确认文件路径**：从上下文中获取用户提到的文件路径（支持相对路径和绝对路径）
2. **运行转换脚本**（在项目工作目录下执行，确保输出落在项目内）：
   ```bash
   uv run --project <skill-path>/scripts python <skill-path>/scripts/convert.py "<file-path>" -o markdown-conversions
   ```
   如果已知该文件已转换过且未修改，可跳过转换直接读取 Markdown
3. **读取生成的 Markdown**：用 Read 工具读取 `markdown-conversions/<file-name>/<file-name>.md`

## 输出结构

```
<项目目录>/markdown-conversions/
└── <文件名>/
    └── <文件名>.md         # 转换后的 Markdown 文件
```

## 转换脚本参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `file` | 文件路径（必需） | - |
| `-o, --output-dir` | 转换输出父目录 | `markdown-conversions` |

### 示例

命令统一为：`uv run --project <skill-path>/scripts python <skill-path>/scripts/convert.py <文件>`

```bash
# 办公文档
uv run --project <skill-path>/scripts python <skill-path>/scripts/convert.py report.pdf
uv run --project <skill-path>/scripts python <skill-path>/scripts/convert.py proposal.docx
uv run --project <skill-path>/scripts python <skill-path>/scripts/convert.py data.xlsx

# 指定输出目录
uv run --project <skill-path>/scripts python <skill-path>/scripts/convert.py paper.pdf -o ./output
```

## 首次使用

首次使用需先安装 Python 依赖：

```bash
cd <skill-path>/scripts && uv sync
```

## 重要规则

1. **转换目录（`markdown-conversions/`）应加入 `.gitignore`**，避免将临时转换文件提交到仓库
2. 如果文件已经转换过且在 `markdown-conversions/` 中存在对应的 Markdown，可直接读取。如果源文件修改过，应重新转换
3. 转换完成后，优先使用 Read 工具局部读取 Markdown 中需要的章节，而不是一次性加载整个文件，以节省上下文
4. 如果转换失败或输出质量差，可根据错误信息调整后重试
5. MarkItDown 基于文件扩展名自动选择转换器，无需手动指定文件类型

## 常见问题

| 问题 | 解决方案 |
|------|----------|
| `ModuleNotFoundError` | `cd <skill-path>/scripts && uv sync` |
| 大文件转换慢 | 正常现象，MarkItDown 会按需加载相关转换器 |
| 转换结果为空或内容不完整 | 检查是否安装了完整依赖（`'markitdown[all]'`），或文件是否损坏 |
| 音频转文字需要 API key | 音频转录依赖 OpenAI Whisper API，需设置 `OPENAI_API_KEY` 环境变量 |
