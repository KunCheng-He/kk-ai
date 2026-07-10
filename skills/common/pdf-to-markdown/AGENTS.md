# AGENTS.md - PDF to Markdown 转换工具开发指南

本文档为 AI 编码代理提供项目开发指南，包含构建、测试、代码风格等规范。

## 项目概述

本项目是一个 PDF 转 Markdown CLI 工具，基于 pymupdf4llm，提供统一的命令行接口用于将 PDF 转换为 LLM 可读的 Markdown 格式。已封装为 OpenCode Skill (`pdf-to-markdown`)。

**技术栈**：
- Python 3.11+（受限于 onnxruntime 依赖）
- 包管理：`uv`
- 核心依赖：`pymupdf4llm`（基于 PyMuPDF）
- OCR 可选依赖：`tesserocr`

## 重要约定

**所有代码文件必须存放在 `scripts/` 目录下**，包括：
- 源代码文件（`.py`）
- 配置文件（`pyproject.toml`、`.python-version`）

## 项目结构

```text
pdf-to-markdown/
├── SKILL.md                 # Skill 定义文件
├── AGENTS.md                # 本文件 - AI Agent 开发指南
├── upstream.json            # 上游信息
└── scripts/                 # 主要代码目录（所有代码在此）
    ├── pyproject.toml       # 项目依赖配置
    ├── .python-version      # Python 版本声明
    └── convert.py           # CLI 入口
```

## 构建与运行命令

### 环境设置

```bash
# 进入项目目录
cd scripts

# 安装基础依赖
uv sync

# 安装含 OCR 支持的全部依赖
uv sync --extra ocr
```

### 运行脚本

```bash
# 普通 PDF
uv run python convert.py document.pdf

# 指定输出目录
uv run python convert.py document.pdf -o ./output

# 扫描版 PDF（OCR）
uv run python convert.py scanned.pdf --ocr

# 指定 OCR 语言
uv run python convert.py english-doc.pdf --ocr --ocr-lang eng
```

## 代码风格指南

### 导入规范

```python
# 标准库导入
import argparse
import os
import sys
from pathlib import Path

# 第三方库导入
import pymupdf4llm
import fitz  # PyMuPDF

# 可选导入（OCR）
# import tesserocr
```

### 类型注解

项目使用 Python 3.11+：

```python
def convert_pdf(
    pdf_path: Path,
    output_dir: Path,
    *,
    ocr: bool = False,
    ocr_lang: str = "chi_sim+eng",
) -> Path:
    ...
```

### 命名规范

| 类型 | 命名风格 | 示例 |
|------|----------|------|
| 模块/包 | snake_case | `convert.py` |
| 函数 | snake_case | `convert_pdf()` |
| 类名 | PascalCase | 暂无需类 |

### 输出目录约定

转换输出统一放在项目根目录的 `pdf-conversions/` 下：
- `pdf-conversions/<pdf-name>/<pdf-name>.md` — 转换后的 Markdown
- `pdf-conversions/<pdf-name>/images/` — 提取的嵌入图片

`pdf-conversions/` 应加入项目的 `.gitignore`。

## 错误处理

### 常见错误及处理

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| PDF file not found | 文件路径错误 | 检查路径是否正确 |
| No text layer warning | PDF 是扫描版 | 使用 `--ocr` 参数，安装 tesseract |
| ImportError: tesserocr | OCR 依赖未安装 | 运行 `uv sync --extra ocr` |
| tesseract not found | 系统未安装 tesseract | `brew install tesseract tesseract-lang` |

## 扩展功能

1. 在 `convert.py` 中修改 `convert_pdf()` 函数的 `pymupdf4llm.to_markdown()` 调用参数
2. 添加新的 CLI 参数到 `argparse` 配置
3. 更新 SKILL.md 文档
