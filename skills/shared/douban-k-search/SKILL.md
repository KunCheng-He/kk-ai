---
name: douban-k-research
description: |
  豆瓣数据搜索与调研工具。当用户需要从豆瓣获取书籍、电影、音乐信息时务必使用此技能。支持：搜索条目、获取详情、查看短评。触发场景：用户提到"豆瓣"、"douban"、需要查询书籍/电影/音乐的评分或评价、想了解某本书/电影/专辑的详细信息。即使未明确提及"豆瓣"，但上下文暗示需要中文社区评分或文化产品调研时，也应使用。例如："查一下这本书的评分"、"这部电影好看吗"、"帮我调研一下某专辑的评价"。
---

# 豆瓣数据搜索与调研

通过 HTTP 请求和 Playwright 浏览器自动化获取豆瓣数据，支持书籍、电影、音乐三个类目。

## 环境准备

```bash
cd scripts && uv sync && uv run playwright install chromium
```

## 板块指南

根据需求阅读对应板块的详细文档：

| 需求 | 文档 |
|------|------|
| 搜索书籍、获取书籍详情/短评 | [docs/book.md](docs/book.md) |
| 搜索电影、获取电影详情/短评 | [docs/movie.md](docs/movie.md) |
| 搜索音乐、获取音乐详情/短评 | [docs/music.md](docs/music.md) |

## 快速命令

```bash
# 搜索
uv run python main.py search "关键词" --category <book|movie|music>

# 详情
uv run python main.py detail <ID> --category <book|movie|music>

# 详情+短评
uv run python main.py detail <ID> --category <book|movie|music> --comments
```

## 通用参数

- `--category, -c`: 类目（book/movie/music）
- `--limit, -l`: 搜索返回数量，默认 10
- `--comments`: 获取短评
- `--table`: 表格格式输出（默认 JSON）
- `--output, -o`: 保存到文件

## 注意事项

- 无需登录即可使用全部功能
- 请求频率控制：自动间隔 1.5 秒
- 仅供学习研究使用，遵守豆瓣用户协议
