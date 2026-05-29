# 电影搜索与详情

搜索豆瓣电影、获取电影详情和短评。

## 搜索电影

```bash
cd scripts && uv run python main.py search "星际穿越" --category movie --limit 10
```

**参数**：
- `query`: 搜索关键词
- `--limit, -l`: 返回数量，默认 10
- `--table`: 表格格式输出（默认 JSON）

## 获取电影详情

```bash
cd scripts && uv run python main.py detail 1889243 --category movie
```

## 获取电影短评

```bash
cd scripts && uv run python main.py detail 1889243 --category movie --comments
```

## 数据结构

### 搜索结果

| 字段 | 说明 |
|------|------|
| id | 条目 ID |
| title | 片名 |
| rating_value | 评分 |
| rating_count | 评价人数 |
| abstract | 摘要（国家/类型/年份） |
| url | 链接 |

### 电影详情

| 字段 | 说明 |
|------|------|
| id, title, original_title | 标识和标题 |
| director | 导演列表 |
| writers | 编剧列表 |
| actors | 主演列表 |
| genres | 类型列表 |
| countries | 国家/地区列表 |
| languages | 语言列表 |
| release_date | 上映日期 |
| runtime | 片长（分钟） |
| rating_value, rating_count | 评分数据 |
| rating_distribution | 评分分布 |
| summary | 剧情简介 |

### 短评

| 字段 | 说明 |
|------|------|
| id, user_name | 评论 ID 和用户名 |
| rating | 评分（1-5星） |
| content | 评论内容 |
| votes | 有用数 |

## 技术方案

- 搜索：HTTP 请求 + 提取 `window.__DATA__`
- 详情：**CDP 浏览器**（默认）/ Launch 备用 — 处理 POW 验证
- 短评：**CDP 浏览器**（默认）/ Launch 备用 — 处理 SHA-512 POW 验证
- `--no-cdp` 切回 Launch 模式（自启 Chromium + playwright-stealth）
