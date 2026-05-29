# AGENTS.md - 豆瓣搜索脚本项目指南

本文档为 AI 编码代理提供项目开发指南。

## 项目概述

豆瓣数据搜索与调研工具，支持书籍、电影、音乐三个类目的搜索和详情获取。通过 HTTP 请求和 Playwright 浏览器自动化相结合的方式获取数据。**默认使用 CDP 模式连接已有浏览器**，无需安装 Chromium。

**项目状态：已完成**

**技术栈**：
- Python 3.10+
- 包管理：`uv`
- HTTP 请求：httpx
- 浏览器自动化：Playwright + playwright-stealth（CDP 模式默认，Launch 模式备用）
- 数据模型：Pydantic
- HTML 解析：BeautifulSoup4

## 重要约定

**所有代码文件必须存放在 `scripts/` 目录下**。

## 项目结构

```text
douban-k-search/
├── SKILL.md                 # Skill 定义文件
├── AGENTS.md                # 本文件
├── upstream.json            # 上游信息
├── docs/                    # 板块文档（book/movie/music）
└── scripts/
    ├── pyproject.toml       # 项目依赖配置
    ├── .python-version      # Python 版本
    ├── main.py              # CLI 入口
    ├── commands.py          # 命令实现
    └── douban_utils/
        ├── __init__.py
        ├── data_models.py   # Pydantic 数据模型
        ├── http_client.py   # HTTP 请求客户端
        ├── html_parser.py   # HTML 解析器
        ├── browser.py       # Playwright 浏览器管理（CDP + Launch）
        ├── api_handler.py   # 数据获取逻辑
        └── formatters.py    # 输出格式化
```

## 构建与运行命令

### 环境设置

**CDP 模式（默认）**：
```bash
cd scripts && uv sync
```

**Launch 模式（`--no-cdp`）**：
```bash
cd scripts && uv sync && uv run playwright install chromium
```

### 运行脚本

```bash
# CDP 模式（默认）
cd scripts && uv run python main.py search "三体" --category book
cd scripts && uv run python main.py detail 2567698 --category book --comments

# Launch 模式
cd scripts && uv run python main.py detail 2567698 --category movie --comments --no-cdp
```

### 测试命令

```bash
cd scripts && uv run pytest
```

### 代码检查

```bash
cd scripts && uv run ruff check .
cd scripts && uv run ruff format .
```

## 代码风格

参考 `skills/shared/zhihu-k-search/AGENTS.md` 中的代码风格指南。

## 技术方案

| 场景 | 技术方案 | 说明 |
|------|----------|------|
| 搜索（书/影/音） | HTTP + 提取 `window.__DATA__` | 页面嵌入 JSON，正则提取 |
| 书籍详情 | HTTP + HTML 解析 | 无反爬，直接访问 |
| 书籍短评 | HTTP + HTML 解析 | 无反爬，直接访问 |
| 电影详情 | **CDP 浏览器**（默认）/ HTTP 备用 | CDP 连接已有浏览器处理 POW 验证 |
| 电影短评 | **CDP 浏览器**（默认）/ Launch 备用 | 触发 SHA-512 POW 验证 |
| 音乐详情 | HTTP + HTML 解析 | 无反爬 |
| 音乐短评 | HTTP + HTML 解析 | 无反爬 |

### CDP 模式架构

CDP（Chrome DevTools Protocol）模式通过连接已有浏览器的调试端口，
直接复用用户的浏览器会话：

```
┌─────────────────┐     CDP (9222)     ┌──────────────────┐
│  douban-k-search │ ──────────────────> │  用户浏览器       │
│  (Python 脚本)   │ <────────────────── │  (Chrome/Brave)  │
└─────────────────┘     响应/页面内容    └──────────────────┘
```

优势：
- 无需安装 Chromium
- 复用已有浏览器会话，降低反爬风险
- 无需单独维护登录状态

### Launch 模式（`--no-cdp`）

当 CDP 不可用时，回退到启动独立 Chromium 实例，使用 playwright-stealth 隐藏自动化特征。

## 注意事项

1. **无登录需求** - 所有功能在未登录状态下可用
2. **CDP 模式默认** - 需要先以远程调试模式启动浏览器
3. **请求频率控制** - 间隔 1.5 秒，避免 IP 被封
4. **错误处理** - HTTP 失败自动切换 Playwright
5. **输出格式** - 默认 JSON 格式，`--table` 输出表格
