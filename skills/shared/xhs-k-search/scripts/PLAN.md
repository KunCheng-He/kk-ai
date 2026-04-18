# 小红书搜索脚本技术方案 (xhs-k-search)

本项目旨在实现一个小红书（XHS）搜索脚本，通过浏览器自动化技术模拟用户行为，获取搜索结果、帖子内容及评论数据。该脚本后续将封装为 SKILL 供 Agent 使用。

## 1. 技术栈选型

*   **编程语言**: Python 3.10+
*   **包管理工具**: `uv` (高性能 Python 包管理器)
*   **自动化库**: `Playwright` (强大的浏览器控制库)
*   **反爬插件**: `playwright-stealth` (隐藏自动化特征，规避人机校验)
*   **数据模型**: `Pydantic` (用于结构化搜索结果和帖子数据)

## 2. 核心技术流程

### 2.1 身份认证持久化
*   **手动登录**: 首次运行时，脚本以“有头模式（Headed）”启动内置 Chromium 浏览器。
*   **状态保存**: 用户扫码或账号登录成功后，利用 Playwright 的 `context.storage_state()` 功能，将所有的 Cookie、LocalStorage 和 SessionStorage 导出并保存为项目根目录下的 `auth.json` 文件。
*   **免密复用**: 后续脚本运行时，直接加载 `auth.json` 初始化浏览器上下文，实现无需重复登录的身份校验。

### 2.2 数据采集方案
*   **网络请求拦截**: 相比于解析复杂的 HTML 结构，脚本将监听浏览器的网络流量。
*   **JSON 提取**: 当浏览器滚动加载或跳转搜索页时，直接拦截小红书后端返回的 API 响应（JSON 格式）。这种方式数据最完整、结构最清晰，且对页面 UI 变动的容错性更高。
*   **无头运行**: 在身份信息有效的情况下，脚本将以“无头模式（Headless）”运行，不弹出窗口，适合作为后台服务或 SKILL 调用。

## 3. 项目目录结构建议

```text
xhs-k-search/
├── .python-version      # Python 版本声明
├── pyproject.toml       # 项目依赖配置 (uv 管理)
├── auth.json            # 【身份认证信息】存储登录状态（本地存储）
├── main.py              # 脚本入口，分发搜索与抓取任务
├── login_helper.py      # 专门负责处理首次登录及身份校验逻辑
├── xhs_utils/           # 核心业务逻辑模块
│   ├── browser.py       # 封装 Playwright 启动与反爬配置
│   ├── api_handler.py   # 拦截并处理 XHS API 请求
│   └── data_models.py   # 定义数据解析结构 (Pydantic Models)
└── PLAN.md              # 本技术方案文档
```

## 4. 后续 SKILL 封装考虑

*   **接口标准化**: 脚本将提供统一的 JSON 输出格式，方便 Agent 解析。
*   **稳定性保障**: 
    *   增加随机延迟和模拟人类滚动行为。
    *   异常处理机制：当 `auth.json` 失效时，能够及时触发报警或重新提示登录。
*   **性能优化**: SKILL 调用时，复用浏览器上下文，减少启动开销。

## 5. 开发步骤建议

1.  使用 `uv init` 初始化项目并添加 `playwright` 依赖。
2.  编写 `login_helper.py` 实现 `auth.json` 的获取与保存。
3.  实现 `browser.py` 的基础封装，集成 `stealth` 插件。
4.  开发搜索功能，通过拦截网络请求获取搜索列表 JSON。
5.  开发详情页功能，获取帖子正文及高赞评论。
