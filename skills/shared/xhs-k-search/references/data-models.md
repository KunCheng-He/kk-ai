# 数据模型

## SearchResult（搜索结果）

```json
{
  "items": [Note],
  "total": 20,
  "has_more": true
}
```

## Note（帖子摘要）

| 字段 | 类型 | 说明 |
|------|------|------|
| note_id | str | 帖子ID |
| xsec_token | str | 访问token |
| title | str | 标题 |
| cover | str | 封面图URL |
| author | User | 作者信息 |
| liked_count | int | 点赞数 |
| comment_count | int | 评论数 |
| collect_count | int | 收藏数 |
| share_count | int | 分享数 |
| url | str | 帖子链接（自动生成） |

## NoteDetail（帖子详情）

| 字段 | 类型 | 说明 |
|------|------|------|
| note_id | str | 帖子ID |
| title | str | 标题 |
| desc | str | 正文内容 |
| image_list | List[str] | 图片URL列表 |
| tag_list | List[str] | 标签列表 |
| author | User | 作者信息 |
| liked_count | int | 点赞数 |
| comment_count | int | 评论数 |
| collect_count | int | 收藏数 |
| create_time | int | 创建时间戳 |

## Comment（评论）

| 字段 | 类型 | 说明 |
|------|------|------|
| comment_id | str | 评论ID |
| user | User | 评论者信息 |
| content | str | 评论内容 |
| liked_count | int | 点赞数 |
| create_time | int | 创建时间戳 |

## User（用户）

| 字段 | 类型 | 说明 |
|------|------|------|
| user_id | str | 用户ID |
| nickname | str | 昵称 |
| avatar | str | 头像URL |