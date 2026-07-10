---
name: pdf-to-markdown
description: |
  PDF 转 Markdown 工具，将 PDF 文件内容提取为 LLM 可读的 Markdown 文件。当用户需要读取、分析、提取 PDF 内容时，先调用此 skill 将 PDF 转为 Markdown，再读取生成的 Markdown 文件。支持图文混合 PDF、含表格 PDF、扫描版 PDF（需 OCR）。使用 pymupdf4llm + uv 管理依赖。触发关键词："pdf"、"read pdf"、"pdf转markdown"、"提取pdf"、"阅读pdf"、"看pdf"、"读取pdf"、"翻pdf"、"pdf内容"、"PDF"。
---

# PDF to Markdown 转换技能

将 PDF 文件转换为 Markdown，方便 LLM 读取内容。基于 `pymupdf4llm`，自动处理文本、图片、表格。

## 工作流程

1. **确认 PDF 文件路径**：从上下文中获取用户提到的 PDF 文件路径（支持相对路径和绝对路径）
2. **运行转换脚本**：
   ```bash
   cd <skill-path>/scripts && uv run python convert.py "<pdf-path>" -o pdf-conversions
   ```
   如果已知该 PDF 已转换过且未修改，可跳过转换直接读取 Markdown
3. **读取生成的 Markdown**：用 Read 工具读取 `pdf-conversions/<pdf-name>/<pdf-name>.md`
4. **（如有）查看图片附件**：图片保存在 `pdf-conversions/<pdf-name>/images/` 下

## 输出结构

```
<项目目录>/pdf-conversions/
└── <pdf文件名>/
    ├── <pdf文件名>.md        # 转换后的 Markdown 文件
    └── images/               # 提取的嵌入图片
        ├── img_001.png
        ├── img_002.png
        └── ...
```

Markdown 中的图片引用使用相对路径（`images/img_001.png`），确保文件可移植。

## 转换脚本参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `pdf` | PDF 文件路径（必需） | - |
| `-o, --output-dir` | 转换输出父目录 | `pdf-conversions` |
| `--ocr` | 启用 OCR 模式（扫描版 PDF） | 关闭 |
| `--ocr-lang` | OCR 语言代码 | `chi_sim+eng` |

### 示例

```bash
# 普通 PDF
uv run python convert.py ~/Documents/report.pdf

# 扫描版 PDF（需先安装 tesseract）
uv run python convert.py scanned.pdf --ocr

# 指定输出目录
uv run python convert.py paper.pdf -o ./output

# 指定 OCR 语言（纯英文）
uv run python convert.py english-doc.pdf --ocr --ocr-lang eng
```

## OCR 支持

对于没有文字层的扫描版 PDF，需要启用 OCR。前置条件：

```bash
# macOS 安装 tesseract 及语言包
brew install tesseract tesseract-lang

# 安装后，脚本会自动安装 tesserocr Python 包
cd <skill-path>/scripts && uv sync --extra ocr
```

然后使用 `--ocr` 参数运行转换。

## 首次使用

首次使用需先安装 Python 依赖：

```bash
cd <skill-path>/scripts && uv sync
```

如需 OCR 支持：

```bash
cd <skill-path>/scripts && uv sync --extra ocr
```

## 重要规则

1. **转换目录（`pdf-conversions/`）应加入 `.gitignore`**，避免将临时转换文件提交到仓库
2. 如果 PDF 已经转换过且在 `pdf-conversions/` 中存在对应的 Markdown，可直接读取。如果 PDF 文件修改过，应重新转换
3. 转换完成后，优先使用 Read 工具局部读取 Markdown 中需要的章节，而不是一次性加载整个文件，以节省上下文
4. 如果转换失败或输出质量差（如扫描版 PDF 未启用 OCR），应根据错误信息/输出结果调整参数重试
