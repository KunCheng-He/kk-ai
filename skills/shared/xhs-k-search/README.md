# xhs-k-search

小红书数据搜索与调研 SKILL，通过浏览器自动化技术获取小红书搜索结果、帖子详情和评论数据。专为 AI Agent 调用设计。

## 功能特性

- **关键词搜索**：搜索小红书关键词，获取帖子列表（标题、作者、互动数据、链接）
- **帖子详情**：获取帖子的完整正文、图片列表、标签及评论
- **CDP 模式（默认）**：连接已有浏览器，无需安装 Chromium、无需单独登录
- **Launch 模式**：自启 Chromium，支持登录持久化
- **结果保存**：支持保存搜索结果和帖子详情到 JSON 文件

## 技术栈

- Python 3.10+
- [Playwright](https://playwright.dev/) - 浏览器自动化
- [playwright-stealth](https://github.com/AtinyOne/Playwright-stealth) - 反爬检测规避
- [Pydantic](https://docs.pydantic.dev/) - 数据模型

## 安装

### CDP 模式（默认，推荐）

只需 Python 依赖，无需安装 Chromium：

```bash
cd scripts && uv sync
```

### Launch 模式（可选）

额外需要 Chromium 浏览器：

```bash
cd scripts && uv sync && uv run playwright install chromium
```

## 使用方法

### 前置条件：启动浏览器调试模式（CDP 模式）

CDP 模式需要浏览器以远程调试模式运行：

```bash
# Chrome
open -a "Google Chrome" --args --remote-debugging-port=9222

# Brave
open -a "Brave Browser" --args --remote-debugging-port=9222

# Edge
open -a "Microsoft Edge" --args --remote-debugging-port=9222
```

检测 CDP 端口是否就绪：

```bash
curl --noproxy '*' -s http://localhost:9222/json/version
```

### 登录（仅 Launch 模式需要）

```bash
cd scripts && uv run python main.py login
```

打开浏览器窗口，完成扫码登录。登录状态保存到 `~/.cache/xhs-k-search/auth.json`。

CDP 模式直接复用已有浏览器的登录状态，无需此步骤。

### 搜索

```bash
# CDP 模式（默认）
cd scripts && uv run python main.py search "Python" --limit 20

# Launch 模式
cd scripts && uv run python main.py search "Python" --limit 20 --no-cdp

# 保存结果
cd scripts && uv run python main.py search "Python" --save
cd scripts && uv run python main.py search "Python" -o /path/to/output.json
```

### 获取帖子详情

```bash
# CDP 模式（默认）
cd scripts && uv run python main.py detail "帖子ID" --xsec-token "token值"

# Launch 模式
cd scripts && uv run python main.py detail "帖子ID" --xsec-token "token值" --no-cdp

# 保存结果
cd scripts && uv run python main.py detail "帖子ID" --save
```

> 帖子详情功能因反爬限制，强制使用有头模式。

## 项目结构

```
xhs-k-search/
├── SKILL.md              # SKILL 定义文件
├── README.md             # 项目说明
├── AGENTS.md             # AI Agent 开发指南
├── upstream.json         # 上游信息
├── references/           # 参考文档
│   └── data-models.md    # 数据结构说明
└── scripts/              # 脚本目录
    ├── pyproject.toml    # 依赖配置
    ├── main.py           # CLI 入口（子命令式）
    ├── commands.py       # 命令实现
    ├── login_helper.py   # 认证管理
    └── xhs_utils/        # 核心模块
        ├── browser.py    # 浏览器管理（CDP/Launch）
        ├── api_handler.py # API 拦截与解析
        └── data_models.py # 数据模型
```

## 作为 SKILL 使用

将 `xhs-k-search.skill` 文件安装到你的 AI Agent 工具目录。Agent 会在需要搜索小红书数据时自动调用此 SKILL。

触发场景：
- 搜索小红书关键词
- 获取某篇帖子的详细内容和评论
- 进行产品调研或竞品分析

## 运行模式

| 模式 | 命令 | Chromium | 登录 | 适用场景 |
|------|------|----------|------|----------|
| CDP（默认） | 无额外参数 | 不需要 | 不需要 | 日常使用 |
| Launch | `--no-cdp` | 需要 | 需要先 login | CDP 不可用时 |

---

## 学习目的声明

本项目**仅供学习和研究使用**，旨在帮助开发者了解：

- 浏览器自动化技术（Playwright）的应用
- 网络请求拦截与数据解析方法
- Python 异步编程实践
- Pydantic 数据建模

通过学习本项目，你可以掌握现代 Web 自动化和数据处理技术。

## 免责声明

**使用本项目前，请务必阅读并同意以下条款：**

1. 本项目**仅供个人学习研究使用**，严禁用于任何商业用途。

2. 请遵守小红书用户协议及相关法律法规。使用本项目所产生的一切后果由使用者自行承担。

3. 严禁将本项目用于：
   - 数据倒卖、非法爬取
   - 侵犯他人隐私
   - 任何违法活动

4. 项目作者不对因使用本项目造成的任何损失、法律纠纷或第三方索赔负责。

5. 使用本代码即表示您已阅读、理解并同意以上声明。如您不同意，请勿使用本项目。

---

**License**: MIT
