# AGENTS.md - Files to Markdown 转换工具开发指南

本文档为 AI 编码代理提供项目开发指南，包含构建、测试、代码风格等规范。

## 项目概述

本项目是一个多格式文件转 Markdown CLI 工具，基于 Microsoft MarkItDown，提供统一的命令行接口用于将多种文件格式转换为 LLM 可读的 Markdown 格式。已封装为 OpenCode Skill (`files-to-markdown`)。

**技术栈**：
- Python 3.12+
- 包管理：`uv`
- 核心依赖：`markitdown[all]`（Microsoft 出品）

## 重要约定

**所有代码文件必须存放在 `scripts/` 目录下**，包括：
- 源代码文件（`.py`）
- 配置文件（`pyproject.toml`、`.python-version`）

## 项目结构

```text
files-to-markdown/
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
```

### 运行脚本

```bash
# 基本用法（在项目工作目录下执行，输出落在当前目录）
uv run --project <skill-path>/scripts python <skill-path>/scripts/convert.py document.pdf

# 指定输出目录
uv run --project <skill-path>/scripts python <skill-path>/scripts/convert.py document.pdf -o ./output

# 支持任意格式
uv run --project <skill-path>/scripts python <skill-path>/scripts/convert.py slides.pptx
```

> **注意**：使用 `--project` 而非 `cd`，确保相对路径（如 `-o markdown-conversions`）解析到用户的项目目录，而非 skill 的 scripts 目录。

## 代码风格指南

### 导入规范

```python
# 标准库导入
import argparse
import sys
from pathlib import Path

# 第三方库导入
from markitdown import MarkItDown
```

### 类型注解

项目使用 Python 3.12+：

```python
def convert_file(file_path: Path, output_dir: Path) -> Path:
    ...
```

### 命名规范

| 类型 | 命名风格 | 示例 |
|------|----------|------|
| 模块/包 | snake_case | `convert.py` |
| 函数 | snake_case | `convert_file()` |
| 类名 | PascalCase | 暂无需类 |

### 输出目录约定

转换输出统一放在项目根目录的 `markdown-conversions/` 下：
- `markdown-conversions/<file-name>/<file-name>.md` — 转换后的 Markdown

`markdown-conversions/` 应加入项目的 `.gitignore`。

## 错误处理

### 常见错误及处理

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| File not found | 文件路径错误 | 检查路径是否正确 |
| `ModuleNotFoundError` | 依赖未安装 | 运行 `uv sync` |
| MarkItDown not installed | markitdown 未正确安装 | 检查 `pyproject.toml` 中的依赖配置 |
| 转换结果为空 | 文件损坏或格式不支持 | 检查文件是否可正常打开 |

## 依赖说明

MarkItDown (`markitdown[all]`) 包含了以下主要子依赖：
- **PDF**: pdfminer.six
- **Word**: mammoth
- **PowerPoint**: python-pptx
- **Excel**: openpyxl, xlrd
- **Image**: Pillow
- **Audio**: speechrecognition, pydub
- **YouTube**: youtube-transcript-api
- **HTML**: beautifulsoup4

## 扩展功能

1. 在 `convert.py` 中添加新的 CLI 参数（如 LLM client 支持）
2. 安装 `markitdown-ocr` 插件可获得基于 LLM Vision 的 OCR 能力
3. 更新 SKILL.md 文档
