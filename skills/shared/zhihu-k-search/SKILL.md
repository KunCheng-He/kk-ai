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

### 1. 检查并确保登录状态

知乎需要登录才能获取完整数据。登录状态存储在 `scripts/auth.json`。

```bash
ls scripts/auth.json  # 检查登录文件是否存在
```

若文件不存在或已过期，执行登录：

```bash
cd scripts && uv run python main.py login
```

浏览器窗口会打开，用户扫码或账号密码登录后自动保存状态。

### 2. 执行搜索

```bash
cd scripts && uv run python main.py search "关键词" --limit 10
```

**参数说明**：
- `query`: 搜索关键词（必需）
- `--type, -t`: 类型过滤 - `all`(默认)、`question`、`answer`、`article`、`people`
- `--limit, -l`: 返回数量，默认 10
- `--output, -o`: 保存为 JSON 文件

脚本会拦截知乎 API 响应，返回结构化的搜索结果。

### 3. 获取详情

**问题及回答**：
```bash
cd scripts && uv run python main.py detail "https://www.zhihu.com/question/123456" --answer-limit 5
```

**单篇回答**：
```bash
cd scripts && uv run python main.py detail "https://www.zhihu.com/question/123456/answer/789012"
```

**文章**：
```bash
cd scripts && uv run python main.py detail "https://zhuanlan.zhihu.com/p/123456"
```

**参数**：`--answer-limit, -a` 控制获取回答数量，`--output, -o` 保存为 Markdown。

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
