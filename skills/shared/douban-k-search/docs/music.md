# 音乐搜索与详情

搜索豆瓣音乐、获取音乐详情和短评。

## 搜索音乐

```bash
cd scripts && uv run python main.py search "周杰伦" --category music --limit 10
```

**参数**：
- `query`: 搜索关键词（建议搜索专辑名或艺人名）
- `--limit, -l`: 返回数量，默认 10
- `--table`: 表格格式输出（默认 JSON）

## 获取音乐详情

```bash
cd scripts && uv run python main.py detail 1403307 --category music
```

## 获取音乐短评

```bash
cd scripts && uv run python main.py detail 1403307 --category music --comments
```

## 数据结构

### 搜索结果

| 字段 | 说明 |
|------|------|
| id | 条目 ID |
| title | 专辑名 |
| rating_value | 评分 |
| rating_count | 评价人数 |
| abstract | 摘要（表演者/发行时间/介质） |
| url | 链接 |

### 音乐详情

| 字段 | 说明 |
|------|------|
| id, title | 标识和标题 |
| artist | 表演者 |
| release_date | 发行时间 |
| genres | 流派列表 |
| rating_value, rating_count | 评分数据 |
| rating_distribution | 评分分布 |

### 短评

| 字段 | 说明 |
|------|------|
| id, user_name | 评论 ID 和用户名 |
| rating | 评分（1-5星） |
| content | 评论内容 |
| votes | 有用数 |

## 技术方案

HTTP 请求 + HTML 解析，无反爬限制。

## 注意事项

豆瓣音乐主要收录专辑，单曲可能搜索不到。建议搜索专辑名或艺人名。
