---
name: douban-k-research
description: |
  豆瓣数据搜索与调研工具。当用户需要从豆瓣获取书籍、电影、音乐信息时务必使用此技能。支持：搜索条目、获取详情、查看短评。触发场景：用户提到"豆瓣"、"douban"、需要查询书籍/电影/音乐的评分或评价、想了解某本书/电影/专辑的详细信息。即使未明确提及"豆瓣"，但上下文暗示需要中文社区评分或文化产品调研时，也应使用。例如："查一下这本书的评分"、"这部电影好看吗"、"帮我调研一下某专辑的评价"。
---

# 豆瓣数据搜索与调研

通过 HTTP 请求和 Playwright 浏览器自动化获取豆瓣数据，支持书籍、电影、音乐三个类目。

## 环境准备

**CDP 模式（默认）**：只需 Python 依赖，无需安装 Chromium：

```bash
cd scripts && uv sync
```

**Launch 模式（仅 `--no-cdp` 时）**：额外需要 Chromium，且仅当未安装时才安装：

```bash
# 检测是否已安装
uv run playwright install chromium --dry-run 2>&1 | grep -q "already" || uv run playwright install chromium
```

## 工作流程

### 0. 环境检测与初始化

**默认流程（CDP 模式）**：只需检测 Python 依赖：

```bash
ls scripts/.venv 2>/dev/null
```

若检测失败，执行：

```bash
cd scripts && uv sync
```

**注意**：CDP 模式下 **绝不安装 Chromium**。只有用户显式使用 `--no-cdp` 切到 Launch 模式时，才检测并安装 Chromium。

**Launch 模式流程**：除 Python 依赖外，还需检测 Chromium 浏览器：

```bash
uv run python -c "from playwright.sync_api import sync_playwright; p=sync_playwright().start(); print(p.chromium.executable_path); p.stop()" 2>/dev/null
```

若检测失败（Chromium 未安装），执行：

```bash
cd scripts && uv run playwright install chromium
```

### 1. 确保浏览器就绪（CDP 模式）

默认使用 CDP 模式，连接已有浏览器，无需单独安装 Chromium。

**检测 CDP 端口**：

```bash
curl --noproxy '*' -s http://localhost:9222/json/version
```

**处理策略**：
- CDP 端口就绪 → 直接执行搜索/详情命令
- CDP 端口未就绪 → 提示用户："需要启动浏览器的远程调试模式。请退出当前浏览器，然后以调试模式重新启动它。" 
  - 若用户不知道如何操作，询问："你使用的是什么浏览器？（Chrome / Brave / Edge / ...）"
  - 根据用户回答，给出对应启动命令：
    - **Chrome**: `open -a "Google Chrome" --args --remote-debugging-port=9222`（macOS）或 `google-chrome --remote-debugging-port=9222`（Linux）
    - **Brave**: `open -a "Brave Browser" --args --remote-debugging-port=9222`（macOS）
    - **Edge**: `open -a "Microsoft Edge" --args --remote-debugging-port=9222`（macOS）或 `microsoft-edge --remote-debugging-port=9222`（Linux）
  - 等待用户确认浏览器已启动后，重新检测端口
- 无法使用 CDP → 使用 `--no-cdp` 切回 Launch 模式

### 2. 执行搜索

搜索功能使用 HTTP 请求，无需浏览器：

```bash
cd scripts && uv run python main.py search "关键词" --category <book|movie|music>
```

**保存结果到文件**：
```bash
cd scripts && uv run python main.py search "关键词" --category book -o /path/to/output.json
```

**参数说明**：
- `query`: 搜索关键词（必需）
- `--category, -c`: 类目 - `book`、`movie`、`music`（默认 `book`）
- `--limit, -l`: 返回数量，默认 10

### 3. 获取详情

详情获取根据类目使用不同策略：
- **书籍、音乐**：使用 HTTP 请求（无反爬）
- **电影**：默认使用 CDP 模式连接已有浏览器（应对 POW 验证）

**CDP 模式（默认）**：
```bash
# 详情
cd scripts && uv run python main.py detail <ID> --category <book|movie|music>

# 详情+短评
cd scripts && uv run python main.py detail <ID> --category <book|movie|music> --comments
```

**Launch 模式**：
```bash
cd scripts && uv run python main.py detail <ID> --category movie --comments --no-cdp
```

**保存详情到文件**：
```bash
cd scripts && uv run python main.py detail <ID> --category movie --comments -o /path/to/output.json
```

**参数**：
- `subject_id`: 条目 ID（必需）
- `--category, -c`: 类目（`book`/`movie`/`music`）
- `--comments`: 获取短评
- `--output, -o`: 输出文件路径（JSON）
- `--no-cdp`: 使用 Launch 模式（自启 Chromium），而非默认的 CDP 模式
- `--cdp-url`: CDP 调试端点 URL（默认 `http://localhost:9222`）

## 板块指南

根据需求阅读对应板块的详细文档：

| 需求 | 文档 |
|------|------|
| 搜索书籍、获取书籍详情/短评 | [docs/book.md](docs/book.md) |
| 搜索电影、获取电影详情/短评 | [docs/movie.md](docs/movie.md) |
| 搜索音乐、获取音乐详情/短评 | [docs/music.md](docs/music.md) |

## 数据结构

### SearchResult（搜索结果）

| 字段 | 说明 |
|------|------|
| id, category, title | 内容标识和类型 |
| url, cover_url | 链接和封面 |
| rating_value, rating_count | 评分和评价人数 |
| abstract | 内容摘要 |

### Book（书籍）

| 字段 | 说明 |
|------|------|
| id, title, subtitle | 书籍标识 |
| author, publisher, producer | 作者、出版社、出品方 |
| publish_date, isbn, pages | 出版信息 |
| rating_value, rating_count | 评分 |
| summary, author_intro | 简介 |

### Movie（电影）

| 字段 | 说明 |
|------|------|
| id, title, original_title | 电影标识 |
| director, writers, actors | 主创人员 |
| genres, countries, languages | 分类信息 |
| release_date, runtime | 上映信息 |
| rating_value, rating_count | 评分 |
| summary | 剧情简介 |

### Music（音乐）

| 字段 | 说明 |
|------|------|
| id, title | 音乐标识 |
| artist, release_date | 表演者、发行时间 |
| genres | 流派 |
| rating_value, rating_count | 评分 |

### Comment（短评）

| 字段 | 说明 |
|------|------|
| id, user_name | 用户信息 |
| rating, content | 评分和内容 |
| votes, created_at | 有用数和时间 |

## 输出处理

调用脚本后，解析输出并整理：

1. **搜索结果**：汇总标题、评分、摘要、链接
2. **详情**：展示完整信息，格式化输出
3. **短评**：列出用户评价和评分
4. **调研报告**：综合多个结果，生成分析摘要

## 注意事项

- **CDP 模式**（默认）：连接已有浏览器，无需安装 Chromium，日常推荐使用
- **Launch 模式**（`--no-cdp`）：启动独立 Chromium，需要先安装 `playwright install chromium`
- 无需登录即可使用全部功能
- 请求频率控制：HTTP 请求自动间隔 1.5 秒
- 电影页面有 POW 验证（SHA-512），CDP 模式下浏览器会自动处理
- 仅供个人学习研究使用，遵守豆瓣用户协议
