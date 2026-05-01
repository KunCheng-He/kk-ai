---
name: zhihu-k-research
description: |
  知乎数据搜索与调研工具。当用户需要从知乎获取信息时务必使用此技能，包括：搜索知乎内容、获取问题详情、查看回答全文、读取知乎文章、进行产品调研或竞品分析。触发关键词："知乎"、"zhihu"、"知乎搜索"、"知乎问题"、"知乎回答"、"知乎文章"、"知乎调研"。即使用户未明确提及"知乎"，但上下文暗示需要中文社区观点或问答平台数据时，也应考虑使用。
---

# 知乎数据搜索与调研

通过 Playwright 浏览器自动化获取知乎数据。知乎是中国最大的问答社区，包含高质量的用户生成内容，适合产品调研、竞品分析、观点收集等场景。

## 环境准备

首次使用需安装依赖：

```bash
cd scripts && uv sync && uv run playwright install chromium
```

## 工作流程

### 0. 环境检测与初始化

执行任何操作前，先检测环境是否就绪：

```bash
ls scripts/.venv 2>/dev/null && ls scripts/.venv/lib/*/site-packages/playwright 2>/dev/null
```

若检测失败（目录不存在），执行自动初始化：

```bash
cd scripts && uv sync && uv run playwright install chromium
```

**处理策略**：
- 自动初始化成功 → 继续执行后续步骤
- 自动初始化失败 → 提示用户手动执行上述命令，等待用户确认完成后再继续

### 1. 检查并确保登录状态

知乎需要登录才能获取完整数据。登录状态存储在 `scripts/auth.json`。

**检测步骤**：

```bash
# 检查认证文件是否存在
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

### 2. 执行搜索

**直接查看结果（不保存）**：
```bash
cd scripts && uv run python main.py search "关键词" --limit 10
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

### 3. 获取详情

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

- 登录状态有时效，失败时重新执行 `login` 命令
- 内容为 HTML 格式，需转换为 Markdown 展示
- 仅供个人学习研究使用，遵守知乎用户协议
