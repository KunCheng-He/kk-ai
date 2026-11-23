# 故障排查与错误处理

> 阅读时机：发布出错需要定位原因，或需要了解命令返回 JSON 的完整字段含义时。

## 返回格式

所有命令返回 JSON 格式。

### 正常发布

```json
{
  "success": true,
  "media_id": "xxx",
  "title": "文章标题",
  "theme": "ai-bubble",
  "images_uploaded": 3,
  "has_tables": false,
  "has_code_blocks": false,
  "content_length": 5000
}
```

### 包含表格或代码块时（未使用 --force）

```json
{
  "success": false,
  "needs_confirmation": true,
  "confirmations": [
    {
      "type": "table",
      "warning": "文档包含表格，在手机端可能显示不全。建议先将表格转换为图片再发布。"
    },
    {
      "type": "code_block",
      "warning": "文档包含代码块，字符占用大且移动端可读性差。建议先将代码块转换为图片再发布。"
    }
  ],
  "warning": "文档包含需要确认的内容。请询问用户是否将代码块/表格转换为图片，由用户决定。如确认直接发布，请使用 --force 参数。",
  "title": "文章标题",
  "theme": "ai-bubble",
  "content_length": 5000
}
```

## 表格/代码块显示问题

表格在手机端可能显示不全，代码块字符占用大。本工具会检测文档中的表格和代码块并**询问用户是否转图片，由用户决定**（不自动转图）。

**用户决定转图时**：
- Agent 自行选择合适的工具将表格/代码块渲染为图片
- 图片通过 `media/uploadimg` 上传微信 CDN 后以 `<img>` 插入正文（图片不占 content 字符数）

**用户决定不转图时**：
- 使用 `--force` 参数直接发布

## IP 白名单配置

首次使用需在公众号后台添加服务器 IP 到白名单：
- 路径：「设置与开发」→「基本配置」→「IP白名单」
- 错误码 40164 表示 IP 未在白名单

## 图片上传限制

- 仅支持 jpg/png 格式
- 图片大小 < 1MB

## 常见错误码

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 40001 | access_token 无效 | 等待自动刷新或删除缓存 |
| 40164 | IP 不在白名单 | 添加服务器 IP 到白名单 |
| 44004 | 内容为空 | 通常是因为标题缺失（frontmatter 无 title 且正文无 `# ` 一级标题），补充标题后重试 |
| 45002 | 内容长度超限 | 按「publishing-fallback.md」走 JS 通道兜底 |
| 45166 | 内容包含被禁链接 | 微信草稿 API 禁止内容中包含 `mp.weixin.qq.com` 域名链接，移除或替换为文字提示 |
| 40005 | 文件格式不支持 | 使用 jpg/png 格式 |
