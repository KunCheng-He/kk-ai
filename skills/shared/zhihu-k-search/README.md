# 知乎数据搜索与调研工具

基于 Playwright 的知乎数据搜索与采集工具，通过浏览器自动化技术获取搜索结果、问题、回答和文章数据。本项目封装为 OpenCode Skill，可供 AI Agent 调用。

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
- Chromium 浏览器

## 快速开始

### 安装依赖

```bash
cd scripts
uv sync
uv run playwright install chromium
```

### 登录

首次使用需要登录：

```bash
uv run python main.py login
```

### 搜索

```bash
# 基本搜索
uv run python main.py search "Python"

# 指定类型和数量
uv run python main.py search "Python" -t article -l 20

# 保存为 JSON
uv run python main.py search "Python" -o results.json
```

### 获取详情

```bash
# 获取问题及回答
uv run python main.py detail "https://www.zhihu.com/question/123456"

# 获取文章
uv run python main.py detail "https://zhuanlan.zhihu.com/p/123456"
```

## 项目结构

```
zhihu-k-search/
├── SKILL.md              # Skill 定义文件
├── README.md             # 项目说明
├── AGENTS.md             # AI Agent 开发指南
├── PLAN.md               # 技术方案文档
└── scripts/              # 核心代码目录
    ├── main.py           # CLI 入口
    ├── commands.py       # 命令实现
    ├── login_helper.py   # 登录辅助
    ├── pyproject.toml    # 项目配置
    └── zhihu_utils/      # 核心模块
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

## 作为 Skill 使用

本项目已封装为 OpenCode Skill，可在 OpenCode 中直接调用。将本项目目录添加到 OpenCode 的 skills 配置中，即可使用 `zhihu-k-research` 技能。

详细使用说明请参考 [SKILL.md](./SKILL.md)。

## 注意事项

- 首次运行需要手动登录
- `auth.json` 包含敏感信息，请勿提交到版本控制
- 建议合理控制请求频率，避免触发反爬机制

---

## 免责声明

**本项目仅供个人学习和研究使用，不得用于任何商业用途。**

1. **学习目的**：本项目旨在帮助开发者学习浏览器自动化技术、数据采集方法和 Python 编程实践。使用者应将本项目用于技术学习和研究目的。

2. **遵守协议**：使用本项目时，请遵守知乎的用户协议、服务条款以及相关法律法规。不得利用本项目进行任何违反知乎平台规则或法律法规的行为。

3. **数据权益**：知乎平台上的内容版权归相关作者和知乎平台所有。通过本项目获取的数据仅供个人学习分析，不得用于商业用途、不得二次分发、不得侵犯原作者的知识产权。

4. **使用风险**：使用者需自行承担使用本项目的风险。作者不对因使用本项目而产生的任何直接或间接损失负责，包括但不限于账号被封禁、数据丢失、法律纠纷等。

5. **反爬虫**：本项目包含反爬虫规避技术仅供技术学习。使用者应合理控制请求频率，避免对知乎服务器造成过大压力。因滥用导致的任何后果由使用者自行承担。

6. **法律合规**：使用者应确保其使用行为符合所在地区的法律法规。作者不对使用者的违法行为承担任何责任。

**使用本项目即表示您已阅读、理解并同意遵守以上免责声明。如您不同意，请勿使用本项目。**
