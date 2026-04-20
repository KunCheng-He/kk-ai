# 书籍搜索与详情

搜索豆瓣读书、获取书籍详情和短评。

## 搜索书籍

```bash
cd scripts && uv run python main.py search "三体" --category book --limit 10
```

**参数**：
- `query`: 搜索关键词
- `--limit, -l`: 返回数量，默认 10
- `--table`: 表格格式输出（默认 JSON）

## 获取书籍详情

```bash
cd scripts && uv run python main.py detail 2567698 --category book
```

## 获取书籍短评

```bash
cd scripts && uv run python main.py detail 2567698 --category book --comments
```

## 数据结构

### 搜索结果

| 字段 | 说明 |
|------|------|
| id | 条目 ID |
| title | 书名 |
| rating_value | 评分 |
| rating_count | 评价人数 |
| abstract | 摘要（作者/出版社/年份/定价） |
| url | 链接 |

### 书籍详情

| 字段 | 说明 |
|------|------|
| id, title, subtitle | 标识和标题 |
| author | 作者列表 |
| publisher, producer | 出版社、出品方 |
| publish_date, pages, price | 出版年、页数、定价 |
| binding, series, isbn | 装帧、丛书、ISBN |
| rating_value, rating_count | 评分数据 |
| rating_distribution | 评分分布（5星到1星占比） |
| summary | 内容简介 |
| author_intro | 作者简介 |

### 短评

| 字段 | 说明 |
|------|------|
| id, user_name | 评论 ID 和用户名 |
| rating | 评分（1-5星） |
| content | 评论内容 |
| votes | 有用数 |

## 技术方案

HTTP 请求 + HTML 解析，无反爬限制。
