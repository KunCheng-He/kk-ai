---
name: zhihu-k-research
description: |
  知乎数据搜索与调研工具。当用户需要从知乎获取信息时务必使用此技能，包括：搜索知乎内容、获取问题详情、查看回答全文、读取知乎文章、进行产品调研或竞品分析。触发关键词："知乎"、"zhihu"、"知乎搜索"、"知乎问题"、"知乎回答"、"知乎文章"、"知乎调研"。即使用户未明确提及"知乎"，但上下文暗示需要中文社区观点或问答平台数据时，也应考虑使用。
---

# 知乎数据搜索与调研

通过 Playwright 浏览器自动化获取知乎数据。知乎是中国最大的问答社区，包含高质量的用户生成内容，适合产品调研、竞品分析、观点收集等场景。

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

默认使用 CDP 模式，连接已有浏览器，无需单独登录。

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

### 2. Launch 模式登录（仅 --no-cdp 时需要）

Launch 模式下需要单独登录知乎。登录状态存储在 `scripts/auth.json`。

```bash
# 检查认证文件
ls scripts/auth.json
# 检查认证是否有效
cd scripts && uv run python main.py login --check
```

**处理策略**：
- 认证文件不存在 → 提示用户"需要完成知乎登录认证"，然后执行登录命令
- 认证已失效 → 提示用户"认证已失效，需要重新登录"，然后执行登录命令

**登录命令**：

```bash
cd scripts && uv run python main.py login
```

浏览器窗口会打开，提示用户在浏览器中完成登录（扫码或账号密码），登录成功后自动保存状态。

### 3. 执行搜索

**CDP 模式（默认）**：
```bash
cd scripts && uv run python main.py search "关键词" --limit 10
```

**Launch 模式**：
```bash
cd scripts && uv run python main.py search "关键词" --limit 10 --no-cdp
```

**保存结果到文件**：
```bash
# 保存到 /tmp/zhihu-cache/（自动命名）
cd scripts && uv run python main.py search "关键词" --save

# 保存到指定路径
cd scripts && uv run python main.py search "关键词" -o /path/to/output.json
```

**参数说明**：
- `query`: 搜索关键词（必需）
- `--type, -t`: 类型过滤 - `all`(默认)、`question`、`answer`、`article`、`people`
- `--limit, -l`: 返回数量，默认 10
- `--save, -s`: 保存结果到 `/tmp/zhihu-cache/`（自动命名）
- `--output, -o`: 指定输出文件路径（JSON）

脚本会拦截知乎 API 响应，返回结构化的搜索结果。

### 4. 获取详情

**CDP 模式（默认）**：
```bash
# 问题及回答
cd scripts && uv run python main.py detail "https://www.zhihu.com/question/123456" --answer-limit 5
```

**Launch 模式**：
```bash
cd scripts && uv run python main.py detail "https://www.zhihu.com/question/123456" --no-cdp
```

**直接查看详情（不保存）**：
```bash
# 问题及回答
cd scripts && uv run python main.py detail "https://www.zhihu.com/question/123456" --answer-limit 5

# 单篇回答
cd scripts && uv run python main.py detail "https://www.zhihu.com/question/123456/answer/789012"

# 文章
cd scripts && uv run python main.py detail "https://zhuanlan.zhihu.com/p/123456"
```

**保存详情到文件**：
```bash
# 保存到 /tmp/zhihu-cache/（自动命名）
cd scripts && uv run python main.py detail "https://www.zhihu.com/question/123456" --save

# 保存到指定路径
cd scripts && uv run python main.py detail "https://www.zhihu.com/question/123456" -o /path/to/output.md
```

**参数**：
- `--answer-limit, -a`: 获取回答数量
- `--save, -s`: 保存结果到 `/tmp/zhihu-cache/`（Markdown 格式）
- `--output, -o`: 指定输出文件路径（Markdown）

## 数据结构

### SearchResult（搜索结果）

| 字段 | 说明 |
|------|------|
| id, type, title | 内容标识和类型 |
| excerpt | 内容摘要 |
| author, url | 作者和链接 |
| vote_count, comment_count | 互动数据 |

### Question（问题）

| 字段 | 说明 |
|------|------|
| id, title, detail | 问题标识、标题、描述 |
| answer_count, follower_count | 回答数、关注数 |

### Answer（回答）

| 字段 | 说明 |
|------|------|
| id, question_id | 回答和问题标识 |
| content | 回答内容（HTML） |
| author_name, vote_count | 作者和赞同数 |

### Article（文章）

| 字段 | 说明 |
|------|------|
| id, title | 文章标识和标题 |
| content | 文章内容（HTML） |
| author_name, vote_count | 作者和赞同数 |

## 输出处理

调用脚本后，解析输出并整理：

1. **搜索结果**：汇总标题、作者、互动数据、链接
2. **问题详情**：展示问题，列出热门回答摘要
3. **回答/文章**：将 HTML 内容转换为可读格式
4. **调研报告**：综合多个结果，生成分析摘要

## 注意事项

- **CDP 模式**（默认）：连接到已有浏览器，无需单独登录，日常推荐使用
- **Launch 模式**（`--no-cdp`）：启动独立 Chromium，需要先执行 `login` 命令保存认证状态
- 登录状态有时效，失败时重新执行 `login` 命令
- 内容为 HTML 格式，需转换为 Markdown 展示
- 仅供个人学习研究使用，遵守知乎用户协议
