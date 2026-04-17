# AGENTS.md - 知乎搜索脚本项目指南

本文档为 AI 编码代理提供项目开发指南，包含构建、测试、代码风格等规范。

## 项目概述

本项目是一个知乎搜索脚本，通过浏览器自动化技术（Playwright）模拟用户行为，获取搜索结果、问题内容及回答数据。项目已封装为 OpenCode Skill (`zhihu-k-research`)，可供 AI Agent 直接调用。

**项目状态：已完成开发，可投入使用。**

**技术栈**：
- Python 3.14+
- 包管理：`uv`（高性能 Python 包管理器）
- 浏览器自动化：Playwright
- 数据模型：Pydantic
- HTML 解析：BeautifulSoup4（备用）

## 重要约定

**所有代码文件必须存放在 `scripts/` 目录下**，包括：
- 源代码文件（`.py`）
- 测试文件（`tests/` 子目录）
- 配置文件（`pyproject.toml`、`.python-version`）

## 项目结构

```text
zhihu-k-search/
├── SKILL.md                 # Skill 定义文件
├── README.md                # 项目说明文档
├── AGENTS.md                # 本文件 - AI Agent 开发指南
├── PLAN.md                  # 技术方案文档
└── scripts/                 # 主要代码目录（所有代码在此）
    ├── pyproject.toml       # 项目依赖配置
    ├── .python-version      # Python 版本声明
    ├── main.py              # CLI 入口
    ├── commands.py          # 命令实现
    ├── login_helper.py      # 登录及身份校验逻辑
    ├── tests/               # 测试目录
    │   └── test_*.py        # 测试文件
    └── zhihu_utils/         # 核心业务逻辑模块
        ├── __init__.py
        ├── browser.py       # Playwright 启动与反爬配置
        ├── api_handler.py   # API 请求处理
        ├── data_models.py   # Pydantic 数据模型
        ├── extractors.py    # DOM 提取器
        ├── url_parser.py    # URL 解析器
        └── formatters.py    # 输出格式化
```

## 构建与运行命令

### 环境设置

```bash
# 进入项目目录
cd scripts

# 安装依赖（使用 uv）
uv sync

# 安装 Playwright 浏览器
uv run playwright install chromium
```

### 运行脚本

```bash
# 在 scripts 目录下运行
cd scripts
uv run python main.py
```

### 测试命令

```bash
# 运行所有测试
cd scripts
uv run pytest

# 运行单个测试文件
uv run pytest tests/test_search.py

# 运行单个测试函数
uv run pytest tests/test_search.py::test_function_name

# 运行测试并显示详细输出
uv run pytest -v tests/test_search.py

# 运行测试并显示打印输出
uv run pytest -s tests/test_search.py
```

### 代码检查

```bash
# 使用 ruff 进行 lint 检查（需先安装：uv add --dev ruff）
cd scripts
uv run ruff check .

# 自动修复可修复的问题
uv run ruff check --fix .

# 格式化代码
uv run ruff format .

# 类型检查（如使用 mypy）
uv run mypy .
```

## 代码风格指南

### 导入规范

```python
# 标准库导入
import os
import sys
from typing import Optional, List, Dict

# 第三方库导入
from playwright.async_api import async_playwright, Page, Browser
from pydantic import BaseModel, Field

# 本地模块导入
from zhihu_utils.browser import create_browser_context
from zhihu_utils.data_models import SearchResult, Answer
```

**导入顺序**：
1. 标准库（按字母排序）
2. 第三方库（按字母排序）
3. 本地模块（按字母排序）

每组之间空一行分隔。

### 类型注解

项目使用 Python 3.14+，应充分利用现代类型注解：

```python
# 使用内置泛型（无需 typing 导入）
def search(query: str, limit: int = 10) -> list[SearchResult]:
    ...

# 使用 Optional 或 | 语法
def get_answer(answer_id: int) -> Answer | None:
    ...

# 使用 TypeAlias 定义类型别名
type JsonDict = dict[str, Any]

# 函数参数使用默认值
def create_context(
    headless: bool = True,
    storage_state: str | None = None,
) -> BrowserContext:
    ...
```

### 命名规范

| 类型 | 命名风格 | 示例 |
|------|----------|------|
| 模块/包 | snake_case | `api_handler.py` |
| 函数 | snake_case | `get_search_results()` |
| 方法 | snake_case | `extract_content()` |
| 变量 | snake_case | `answer_list` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRIES`, `DEFAULT_TIMEOUT` |
| 类名 | PascalCase | `SearchResult`, `ZhihuClient` |
| 异常类 | PascalCase + Error | `AuthenticationError` |

### 文档字符串

使用 Google 风格的文档字符串：

```python
def search_zhihu(query: str, limit: int = 10) -> list[SearchResult]:
    """搜索知乎内容。

    Args:
        query: 搜索关键词。
        limit: 返回结果数量限制，默认为 10。

    Returns:
        搜索结果列表。

    Raises:
        AuthenticationError: 当登录状态失效时抛出。
    """
    ...
```

### 错误处理

```python
# 定义自定义异常
class ZhihuError(Exception):
    """知乎相关错误的基类。"""
    pass


class AuthenticationError(ZhihuError):
    """认证失败异常。"""
    pass


# 使用上下文管理器处理资源
async with async_playwright() as p:
    browser = await p.chromium.launch()
    try:
        context = await browser.new_context()
        # ... 业务逻辑
    finally:
        await browser.close()

# 使用具体的异常类型
try:
    result = await api_handler.fetch_data(url)
except httpx.HTTPStatusError as e:
    if e.response.status_code == 401:
        raise AuthenticationError("登录状态已过期，请重新登录") from e
    raise
```

### 异步代码规范

项目使用 Playwright 的异步 API：

```python
# 使用 async/await
async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ...

# 入口点
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### Pydantic 模型定义

```python
from pydantic import BaseModel, Field
from datetime import datetime


class SearchResult(BaseModel):
    """搜索结果数据模型。"""
    id: int
    title: str
    excerpt: str = Field(default="", description="内容摘要")
    author: str | None = None
    url: str
    created_at: datetime | None = None


class Answer(BaseModel):
    """回答数据模型。"""
    id: int
    question_id: int
    content: str
    author_name: str
    vote_count: int = 0
    comment_count: int = 0
```

## 配置文件

### pyproject.toml 配置建议

```toml
[project]
name = "zhihu-k-search"
version = "0.1.0"
requires-python = ">=3.14"

[tool.ruff]
line-length = 100
target-version = "py314"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
```

## 敏感信息处理

- `auth.json`：存储登录状态，已在 .gitignore 中排除
- `.env`：环境变量文件，已在 .gitignore 中排除
- 不要在代码中硬编码任何凭证或密钥
- 使用环境变量或配置文件管理敏感信息

## 注意事项

1. **身份认证**：首次运行需要手动登录，登录状态保存在 `auth.json`
2. **反爬策略**：使用 `playwright-stealth` 隐藏自动化特征
3. **API 优先**：优先拦截 API 响应获取数据，DOM 提取作为备用方案
4. **无头模式**：生产环境使用 headless 模式，调试时可使用有头模式

## Skill 使用

项目已封装为 OpenCode Skill，详细使用说明请参考 `SKILL.md`。

**快速使用**：
1. 将本项目目录添加到 OpenCode 的 skills 配置
2. Skill 名称：`zhihu-k-research`
3. 触发关键词：知乎、zhihu、知乎搜索、知乎问题等
