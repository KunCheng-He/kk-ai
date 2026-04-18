# AGENTS.md - 小红书搜索脚本项目指南

本文档为 AI 编码代理提供项目开发指南，包含构建、测试、代码风格等规范。

## 项目概述

本项目是一个小红书搜索脚本，通过浏览器自动化技术（Playwright）模拟用户行为，获取搜索结果、帖子内容及评论数据。项目已封装为 OpenCode Skill (`xhs-k-research`)，可供 AI Agent 直接调用。

**技术栈**：
- Python 3.10+
- 包管理：`uv`
- 浏览器自动化：Playwright + playwright-stealth
- 数据模型：Pydantic

## 重要约定

**所有代码文件必须存放在 `scripts/` 目录下**，包括：
- 源代码文件（`.py`）
- 配置文件（`pyproject.toml`、`.python-version`）

## 项目结构

```text
xhs-k-search/
├── SKILL.md                 # Skill 定义文件
├── README.md                # 项目说明文档
├── AGENTS.md                # 本文件 - AI Agent 开发指南
├── upstream.json            # 上游信息
├── references/              # 参考文档
│   └── data-models.md       # 数据模型定义
└── scripts/                 # 主要代码目录（所有代码在此）
    ├── pyproject.toml       # 项目依赖配置
    ├── main.py              # CLI 入口
    ├── login_helper.py      # 登录逻辑
    ├── auth.json            # 登录状态存储（gitignore）
    └── xhs_utils/           # 核心业务逻辑模块
        ├── __init__.py
        ├── browser.py       # Playwright 启动与反爬配置
        ├── api_handler.py   # API 请求处理
        └── data_models.py   # Pydantic 数据模型
```

## 构建与运行命令

### 环境设置

```bash
# 进入项目目录
cd scripts

# 安装依赖
uv sync

# 安装 Playwright 浏览器
uv run playwright install chromium
```

### 运行脚本

```bash
# 登录
uv run python main.py --login

# 搜索
uv run python main.py --keyword "搜索关键词" --headless

# 获取帖子详情
uv run python main.py --note-id <帖子ID> --xsec-token <token>
```

## 代码风格指南

### 导入规范

```python
# 标准库导入
import asyncio
import json
from pathlib import Path

# 第三方库导入
from playwright.async_api import BrowserContext, Page
from pydantic import BaseModel

# 本地模块导入
from xhs_utils.browser import XHSBrowser
from xhs_utils.data_models import SearchResult, Note
```

### 类型注解

项目使用 Python 3.10+，应使用现代类型注解：

```python
# 使用内置泛型
def search(keyword: str, limit: int = 20) -> SearchResult:
    ...

# 使用 | 语法
def get_note_detail(note_id: str, xsec_token: str | None = None) -> NoteDetailWithComments:
    ...
```

### 命名规范

| 类型 | 命名风格 | 示例 |
|------|----------|------|
| 模块/包 | snake_case | `api_handler.py` |
| 函数 | snake_case | `get_search_results()` |
| 类名 | PascalCase | `XHSBrowser`, `SearchResult` |
| 常量 | UPPER_SNAKE_CASE | `DEFAULT_TIMEOUT` |

## 敏感信息处理

- `auth.json`：存储登录状态，已在 .gitignore 中排除
- 不要在代码中硬编码任何凭证
- 使用环境变量或配置文件管理敏感信息

## 注意事项

1. **身份认证**：首次运行需要手动登录，登录状态保存在 `auth.json`
2. **反爬策略**：使用 `playwright-stealth` 隐藏自动化特征
3. **API 优先**：优先拦截 API 响应获取数据，DOM 提取作为备用方案
4. **无头模式**：搜索支持无头模式，帖子详情强制有头模式（反爬限制）
5. **分页支持**：当前版本通过滚动加载更多结果，`has_more` 字段指示是否有更多数据
