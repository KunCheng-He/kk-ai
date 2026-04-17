# 知乎搜索脚本

基于 Playwright 的知乎数据搜索与采集工具，通过浏览器自动化技术获取搜索结果、问题、回答和文章数据。

## 功能特性

- 搜索知乎内容（支持问题、回答、文章、用户）
- 获取问题详情及回答列表
- 获取单个回答详情
- 获取文章详情
- 支持输出为 JSON 或 Markdown 格式
- 登录状态持久化

## 环境要求

- Python 3.14+
- uv 包管理器

## 安装

```bash
cd scripts
uv sync
uv run playwright install chromium
```

## 使用方法

### 登录

首次使用需要登录：

```bash
uv run python main.py login
```

检查登录状态：

```bash
uv run python main.py login --check
```

### 搜索

```bash
# 基本搜索
uv run python main.py search "Python"

# 指定搜索类型
uv run python main.py search "Python" -t article

# 限制结果数量
uv run python main.py search "Python" -l 20

# 保存为 JSON
uv run python main.py search "Python" -o results.json
```

搜索类型选项：
- `all` - 全部（默认）
- `question` - 问题
- `answer` - 回答
- `article` - 文章
- `people` - 用户

### 获取详情

```bash
# 获取问题及回答
uv run python main.py detail "https://www.zhihu.com/question/123456"

# 获取单个回答
uv run python main.py detail "https://www.zhihu.com/question/123456/answer/789012"

# 获取文章
uv run python main.py detail "https://zhuanlan.zhihu.com/p/123456"

# 限制回答数量并保存为 Markdown
uv run python main.py detail "https://www.zhihu.com/question/123456" -a 10 -o output.md
```

## 项目结构

```
scripts/
├── main.py              # CLI 入口
├── commands.py          # 命令实现
├── login_helper.py      # 登录辅助
├── pyproject.toml       # 项目配置
└── zhihu_utils/         # 核心模块
    ├── __init__.py      # 模块导出
    ├── data_models.py   # 数据模型
    ├── browser.py       # 浏览器管理
    ├── api_handler.py   # API 处理
    ├── extractors.py    # DOM 提取
    ├── url_parser.py    # URL 解析
    └── formatters.py    # 输出格式化
```

## 技术实现

- **API 拦截优先**：通过拦截浏览器网络请求获取知乎 API 响应
- **DOM 提取备用**：当 API 拦截失败时，从页面 DOM 提取数据
- **反爬虫配置**：使用 playwright-stealth 隐藏自动化特征
- **状态持久化**：登录状态保存在 `auth.json` 文件中

## 注意事项

- 首次运行需要手动登录
- `auth.json` 包含敏感信息，请勿提交到版本控制
- 建议合理控制请求频率，避免触发反爬机制
