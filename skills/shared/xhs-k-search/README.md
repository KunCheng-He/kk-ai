# xhs-k-research

小红书数据搜索与调研 SKILL，通过浏览器自动化技术获取小红书搜索结果、帖子详情和评论数据。专为 AI Agent 调用设计。

## 功能特性

- **关键词搜索**：搜索小红书关键词，获取帖子列表（标题、作者、互动数据、链接）
- **帖子详情**：获取帖子的完整正文、图片列表、标签及评论
- **登录持久化**：扫码登录后状态自动保存，无需重复登录
- **无头模式**：搜索功能支持无头模式运行

## 技术栈

- Python 3.10+
- [Playwright](https://playwright.dev/) - 浏览器自动化
- [playwright-stealth](https://github.com/AtinyOne/Playwright-stealth) - 反爬检测规避
- [Pydantic](https://docs.pydantic.dev/) - 数据模型

## 安装

```bash
cd scripts
uv sync
uv run playwright install chromium
```

## 使用方法

### 登录

```bash
cd scripts && uv run python main.py --login
```

打开浏览器窗口，完成扫码登录。登录状态保存到 `auth.json`。

### 搜索

```bash
# 无头模式
cd scripts && uv run python main.py --keyword "Python" --headless

# 有头模式
cd scripts && uv run python main.py --keyword "Python"
```

### 获取帖子详情

```bash
cd scripts && uv run python main.py --note-id <帖子ID> --xsec-token <token>
```

> 帖子详情功能因反爬限制，强制使用有头模式。

## 项目结构

```
xhs-k-search/
├── SKILL.md              # SKILL 定义文件
├── references/           # 参考文档
│   └── data-models.md    # 数据结构说明
└── scripts/              # 脚本目录
    ├── main.py           # 入口脚本
    ├── login_helper.py   # 登录助手
    ├── pyproject.toml    # 依赖配置
    └── xhs_utils/        # 核心模块
        ├── browser.py    # 浏览器管理
        ├── api_handler.py # API 拦截与解析
        └── data_models.py # 数据模型
```

## 作为 SKILL 使用

将 `xhs-k-search.skill` 文件安装到你的 AI Agent 工具目录。Agent 会在需要搜索小红书数据时自动调用此 SKILL。

触发场景：
- 搜索小红书关键词
- 获取某篇帖子的详细内容和评论
- 进行产品调研或竞品分析

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