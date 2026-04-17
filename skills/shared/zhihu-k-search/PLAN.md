# 知乎搜索脚本技术方案 (zhihu-k-search)

本项目实现了一个知乎搜索脚本，通过浏览器自动化技术模拟用户行为，获取搜索结果、问题内容及回答数据。项目已封装为 OpenCode Skill (`zhihu-k-research`)，可供 AI Agent 直接调用。

**项目状态：已完成开发，可投入使用。**

## 1. 技术栈选型

*   **编程语言**: Python 3.14+
*   **包管理工具**: `uv` (高性能 Python 包管理器)
*   **自动化库**: `Playwright` (强大的浏览器控制库)
*   **反爬插件**: `playwright-stealth` (隐藏自动化特征，规避人机校验)
*   **数据模型**: `Pydantic` (用于结构化搜索结果和问答数据)
*   **HTML解析**: `BeautifulSoup4` (备用方案，用于补充解析部分服务端渲染内容)

## 2. 核心技术流程

### 2.1 身份认证持久化
*   **手动登录**: 首次运行时，脚本以"有头模式（Headed）"启动内置 Chromium 浏览器。
*   **状态保存**: 用户扫码或账号登录成功后，利用 Playwright 的 `context.storage_state()` 功能，将所有的 Cookie、LocalStorage 和 SessionStorage 导出并保存为项目根目录下的 `auth.json` 文件。
*   **免密复用**: 后续脚本运行时，直接加载 `auth.json` 初始化浏览器上下文，实现无需重复登录的身份校验。
*   **Token刷新机制**: 知乎的 `z_c0` (Authorization Token) 有时效性，脚本需检测 401 状态码并提示重新登录。

### 2.2 数据采集方案
*   **混合采集策略**:
    *   **主方案 - 网络请求拦截**: 监听浏览器网络流量，拦截知乎后端 API 响应（JSON 格式）。知乎的搜索、问题详情、回答列表均有对应的 GraphQL/REST API。
    *   **备用方案 - DOM 提取**: 对于部分服务端渲染的内容（如富文本回答），结合 Playwright 的页面元素提取作为补充。
*   **API 端点识别**:
    *   搜索接口: `https://www.zhihu.com/api/v4/search_v3` 或 `graphql` 查询
    *   问题详情: `https://www.zhihu.com/api/v4/questions/{id}`
    *   回答列表: `https://www.zhihu.com/api/v4/questions/{id}/answers`
    *   用户主页: `https://www.zhihu.com/api/v4/members/{url_token}`
*   **无头运行**: 在身份信息有效的情况下，脚本将以"无头模式（Headless）"运行，不弹出窗口，适合作为后台服务或 SKILL 调用。

## 3. 项目目录结构

```text
zhihu-k-search/
├── SKILL.md              # Skill 定义文件（OpenCode Skill 配置）
├── README.md             # 项目说明文档
├── AGENTS.md             # AI Agent 开发指南
├── PLAN.md               # 技术方案文档（本文件）
└── scripts/              # 核心代码目录
    ├── .python-version   # Python 版本声明 (3.14+)
    ├── pyproject.toml    # 项目依赖配置 (uv 管理)
    ├── auth.json         # 身份认证信息（本地存储，gitignore）
    ├── main.py           # CLI 入口，分发搜索与抓取任务
    ├── commands.py       # 命令实现模块
    ├── login_helper.py   # 登录及身份校验逻辑
    ├── zhihu_utils/      # 核心业务逻辑模块
    │   ├── __init__.py
    │   ├── browser.py       # Playwright 启动与反爬配置
    │   ├── api_handler.py   # API 请求处理
    │   ├── data_models.py   # Pydantic 数据模型
    │   ├── extractors.py    # DOM 提取器（备用方案）
    │   ├── url_parser.py    # URL 解析器
    │   └── formatters.py    # 输出格式化
    └── tests/               # 测试目录
        └── test_*.py
```

## 4. 已实现功能

### 4.1 CLI 命令

| 命令 | 功能 | 示例 |
|------|------|------|
| `login` | 交互式登录 | `uv run python main.py login` |
| `login --check` | 检查登录状态 | `uv run python main.py login --check` |
| `search` | 搜索知乎内容 | `uv run python main.py search "关键词" -l 10` |
| `detail` | 获取详情 | `uv run python main.py detail "https://..."` |

### 4.2 数据模型

- **SearchResult**: 搜索结果
- **Question**: 问题详情
- **Answer**: 回答内容
- **Article**: 文章内容
- **SearchResponse**: 搜索响应（含分页信息）

### 4.3 输出格式

- 搜索结果：终端输出 + 可选 JSON 文件
- 详情内容：终端输出 + 可选 Markdown 文件

## 5. Skill 集成

项目已封装为 OpenCode Skill，配置文件为 `SKILL.md`。

**Skill 名称**: `zhihu-k-research`

**触发场景**:
- 搜索知乎关键词
- 获取问题详情和回答
- 获取文章内容
- 产品调研或竞品分析

**使用方式**: 将本项目目录添加到 OpenCode 的 skills 配置中即可自动识别。
