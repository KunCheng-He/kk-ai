---
name: wechat-gzh-skill
description: |
  微信公众号草稿发布工具。将 Markdown 文档转换为公众号友好格式并发布到草稿箱。
  
  触发场景：
  - 用户要求将文档/文章发布到微信公众号
  - 用户提到"公众号"、"微信文章"、"草稿箱"
  - 用户需要 Markdown 转微信公众号格式
  
  支持的功能：
  - Markdown 转公众号风格 HTML（5 种主题）
  - 表格自动转图片（解决手机端显示不全问题）
  - 自动上传图片到微信 CDN
  - 自动提取标题、摘要、封面图
  - 支持 YAML frontmatter 元信息
  - 发布到公众号草稿箱
---

# 微信公众号草稿发布工具

将 Markdown 文档转换为微信公众号友好格式，并发布到草稿箱。

## 环境变量配置

使用前需配置以下环境变量：

```bash
export WECHAT_GZH_APPID="你的公众号AppID"
export WECHAT_GZH_SECRET="你的公众号Secret"
```

获取方式：
1. 登录微信公众平台 mp.weixin.qq.com
2. 进入「设置与开发」→「基本配置」
3. 获取 AppID 和 AppSecret
4. **将服务器 IP 添加到白名单**（否则 API 调用会返回 40164 错误）

## 使用方法

### 发布到草稿箱

```bash
cd scripts && uv run main.py publish article.md
```

### 指定主题

```bash
uv run main.py publish article.md --theme elegant-gold
```

### 指定封面图

```bash
uv run main.py publish article.md --cover cover.jpg
```

### 仅转换不发布（预览）

```bash
uv run main.py publish article.md --dry-run
```

### 列出可用主题

```bash
uv run python main.py themes
```

### 检查配置

```bash
uv run python main.py config check
```

## Markdown Frontmatter 支持

可在 Markdown 文件头部使用 YAML frontmatter：

```markdown
---
title: 文章标题
author: 作者名
digest: 文章摘要（可选，不填则自动提取）
cover: cover.jpg
theme: elegant-gold
---

# 正文开始...
```

## 可用主题

| 主题名 | 描述 | 适用场景 |
|--------|------|----------|
| default | 微信默认风格 | 通用 |
| elegant-gold | 金色系，层次丰富 | 深度文章、情感故事 |
| autumn-warm | 秋日暖光，橙色调 | 生活随笔 |
| minimal-blue | 极简蓝，简洁专业 | 技术文章 |
| spring-fresh | 春日清新，绿色调 | 科技、教程 |

## 工作流程

1. 读取环境变量配置
2. 解析 Markdown 文件（提取 frontmatter、标题、摘要、图片）
3. 上传本地图片到微信 CDN
4. 转换 Markdown 为公众号风格 HTML
5. 表格自动转换为图片（避免手机端显示不全、减少字符占用）
6. 上传封面图到微信永久素材库
7. 调用微信 API 创建草稿
8. 返回草稿 media_id

## 返回格式

所有命令返回 JSON 格式：

```json
{
  "success": true,
  "media_id": "xxx",
  "title": "文章标题",
  "theme": "elegant-gold",
  "images_uploaded": 3,
  "tables_converted": 2,
  "content_length": 5000
}
```

---

## 注意事项

### 1. 内容长度限制

微信草稿 API 限制 **content < 20,000 字符**。

**建议**：
- 长文章拆分为多篇发布
- 使用简洁主题（如 `minimal-blue`）可减少样式体积
- 表格会自动转为图片，大幅减少字符占用

### 2. 表格自动转图片

表格在手机端显示不全，本工具自动将表格转换为图片。

**效果**：
- 解决手机端表格显示不全问题
- 大幅减少内容字符数（表格 HTML 转为一张图片）
- 图片自动上传到微信 CDN

### 3. IP 白名单配置

首次使用需在公众号后台添加服务器 IP 到白名单：
- 路径：「设置与开发」→「基本配置」→「IP白名单」
- 错误码 40164 表示 IP 未在白名单

### 4. 图片上传限制

- 仅支持 jpg/png 格式
- 图片大小 < 1MB

### 5. 常见错误码

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 40001 | access_token 无效 | 等待自动刷新或删除缓存 |
| 40164 | IP 不在白名单 | 添加服务器 IP 到白名单 |
| 45002 | 内容长度超限 | 拆分文章或使用简洁主题 |
| 40005 | 文件格式不支持 | 使用 jpg/png 格式 |
