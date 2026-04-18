# AGENTS.md - 图像生成脚本项目指南

本文档为 AI 编码代理提供项目开发指南，包含构建、测试、代码风格等规范。

## 项目概述

本项目是一个图像生成 CLI 工具，提供统一的命令行接口，支持火山引擎、智谱AI、阿里云百炼三个提供商。项目已封装为 OpenCode Skill (`image-generation`)，可供 AI Agent 直接调用。

**技术栈**：
- Python 3.14+
- 包管理：`uv`
- HTTP 客户端：httpx
- 环境变量：python-dotenv

## 重要约定

**所有代码文件必须存放在 `scripts/` 目录下**，包括：
- 源代码文件（`.py`）
- 配置文件（`pyproject.toml`、`.python-version`）

## 项目结构

```text
images-k-generation/
├── SKILL.md                 # Skill 定义文件
├── AGENTS.md                # 本文件 - AI Agent 开发指南
├── upstream.json            # 上游信息
└── scripts/                 # 主要代码目录（所有代码在此）
    ├── pyproject.toml       # 项目依赖配置
    ├── .python-version      # Python 版本声明
    ├── generate.py          # CLI 入口
    └── providers/           # 提供商实现
        ├── __init__.py
        ├── base.py          # 基类定义
        └── providers.py     # 各提供商实现
```

## 构建与运行命令

### 环境设置

```bash
# 进入项目目录
cd scripts

# 安装依赖
uv sync
```

### 运行脚本

```bash
# 文生图
uv run python generate.py --provider zhipu --prompt "一只可爱的橘猫"

# 指定尺寸
uv run python generate.py --provider volcengine --prompt "山水画" --size 2048x2048

# 图生图
uv run python generate.py --provider volcengine --prompt "转换为油画风格" --image https://example.com/cat.jpg

# 查看支持的尺寸
uv run python generate.py --provider aliyun --list-sizes
```

## API Keys 配置

API Key 存储在 `scripts/../.env` 文件中（即 skill 根目录下的 `.env`），脚本会自动读取。

```bash
# .env 文件示例
VOLCENGINE_API_KEY=your_volcengine_key
ZHIPU_API_KEY=your_zhipu_key
ALIYUN_API_KEY=your_aliyun_key
```

## 代码风格指南

### 导入规范

```python
# 标准库导入
import argparse
import base64
import os
from pathlib import Path
from typing import Literal

# 第三方库导入
from dotenv import load_dotenv
import httpx

# 本地模块导入
from providers import VolcengineProvider, GenerateParams
```

### 类型注解

项目使用 Python 3.14+，应充分利用现代类型注解：

```python
# 使用内置泛型
def generate(prompt: str, size: str = "1024x1024") -> list[ImageResult]:
    ...

# 使用 | 语法
def load_api_key(provider_name: str) -> str | None:
    ...
```

### 命名规范

| 类型 | 命名风格 | 示例 |
|------|----------|------|
| 模块/包 | snake_case | `generate.py` |
| 函数 | snake_case | `load_api_key()` |
| 类名 | PascalCase | `VolcengineProvider` |
| 常量 | UPPER_SNAKE_CASE | `PROVIDERS` |

## 错误处理

### 常见错误及处理

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| API key not found | .env 中未配置对应 key | 检查 .env 文件配置 |
| 余额不足 | 账户余额耗尽 | 充值或更换提供商 |
| 请求超时 | 网络问题 | 检查网络，必要时配置代理 |
| 图片尺寸不支持 | 尺寸不在支持列表 | 使用 --list-sizes 查看支持尺寸 |

### 代理配置

如遇网络问题，可通过环境变量配置代理：

```bash
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890
```

或使用 network-proxy skill 获取代理配置帮助。

## 扩展新提供商

1. 在 `providers/base.py` 中确认基类定义
2. 在 `providers/providers.py` 中实现新提供商类
3. 在 `generate.py` 的 `PROVIDERS` 字典中注册
4. 更新 SKILL.md 文档

## 敏感信息处理

- `.env` 文件已在 .gitignore 中排除
- 不要在代码中硬编码任何 API Key
- 使用环境变量管理敏感信息
