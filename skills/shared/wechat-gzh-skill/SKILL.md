---
name: wechat-gzh-skill
description: |
  微信公众号草稿发布工具。将 Markdown 文档转换为公众号友好格式并发布到草稿箱。
  
  触发场景：
  - 用户要求将文档/文章发布到微信公众号
  - 用户提到"公众号"、"微信文章"、"草稿箱"
  - 用户需要 Markdown 转微信公众号格式
  
  支持的功能：
  - Markdown 转公众号风格 HTML（8 种主题）
  - 自动上传图片到微信 CDN
  - 自动提取标题、摘要、封面图
  - 支持 YAML frontmatter 元信息
  - 表格检测与发布确认提醒
  - 发布到公众号草稿箱
  
  注意：本工具不提供表格转图片功能。如文档包含表格，会提醒用户确认后再发布。
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

如果文档包含表格，发布会被拦截并返回提醒。确认后使用 `--force` 强制发布：

```bash
uv run main.py publish article.md --force
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

### 仅转换为 HTML

```bash
uv run main.py convert article.md
uv run main.py convert article.md --output output.html
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
| autumn-warm | 秋日暖光，橙色调 | 生活随笔 |
| spring-fresh | 春日清新，绿色调 | 科技、教程 |
| wenxin-crimson | 温心深红，品牌色高亮标题 + 深灰正文，简洁克制 | 写作笔记、深度分享 |
| xuanfei-sunshine | 轩飞阳光，金黄标题 + 蓝色点缀，活泼温暖 | 运营分享、生活随笔 |
| juanran-pastel | 娟然粉彩，柔和暖色卡片 + 圆角贴图感 | 新手教程、轻松分享 |
| **xiumi-style** | **秀米风格，SVG贴图装饰 + 卡片式布局** | **教程、分享、笔记** |

## 主题系统

主题样式通过 CSS 文件定义（`scripts/themes/css/` 目录），辅以 YAML 配置文件描述卡片、贴图等元信息。

### 主题文件结构

```
themes/css/
├── default.css          # 主题 CSS 样式
├── default.yaml         # 主题元信息（名称、描述、卡片配置、贴图配置）
├── elegant-gold.css
├── elegant-gold.yaml
└── ...
```

### CSS 文件规范

所有元素样式通过 `.article-content` 选择器定义，转换时由 `premailer` 库自动将 CSS class 内联化为 inline style：

```css
.article-content { /* 容器样式 */ }
.article-content h1 { /* 一级标题 */ }
.article-content h2 { /* 二级标题 */ }
.article-content p { /* 段落 */ }
.article-content blockquote { /* 引用块 */ }
.article-content pre { /* 代码块 */ }
.article-content code { /* 行内代码 */ }
/* ... 其他元素 */
```

### YAML 配置项

```yaml
name: elegant-gold
description: 金色系，层次丰富的描述
card:
  enabled: true
  max-width: "800px"
  margin: "0 auto"
  padding: "25px"
  background-color: "#ffffff"
  border-radius: "18px"
  border: "1px solid rgba(0, 0, 0, 0.05)"
  box-shadow: "..."
sticker:
  top_decoration: flower      # 顶部装饰贴图
  top_decoration_color: "#8bc99a"
  top_decoration_size: 32
  bottom_divider: true        # 底部分隔线
  bottom_divider_color: "#5a9b6b"
```

### 新增主题

创建新主题只需在 `themes/css/` 下添加两个文件：
1. `主题名.css` — 定义所有元素的样式
2. `主题名.yaml` — 填写名称、描述，可选配置卡片和贴图

无需编写任何 Python 代码。

### 转换流程

```
Markdown → Python-markdown → HTML (无样式)
    → 添加 .article-content 容器
    → premailer 将 CSS 内联化
    → 提取容器样式、移除包装 div
    → wrap_content 添加卡片/贴图装饰
    → 最终公众号 HTML
```

## 工作流程

1. 读取环境变量配置
2. 解析 Markdown 文件（提取 frontmatter、标题、摘要、图片）
3. 转换 Markdown 为公众号风格 HTML（CSS 模板 → premailer 内联化）
4. 检测文档是否包含表格，如有则提醒用户确认
5. 上传本地图片到微信 CDN
6. 上传封面图到微信永久素材库
7. 调用微信 API 创建草稿
8. 返回草稿 media_id

## 返回格式

所有命令返回 JSON 格式：

### 正常发布

```json
{
  "success": true,
  "media_id": "xxx",
  "title": "文章标题",
  "theme": "elegant-gold",
  "images_uploaded": 3,
  "has_tables": false,
  "content_length": 5000
}
```

### 包含表格时（未使用 --force）

```json
{
  "success": false,
  "needs_confirmation": true,
  "warning": "文档包含表格，在手机端可能显示不全。建议先将表格转换为图片再发布。如确认直接发布，请使用 --force 参数。",
  "title": "文章标题",
  "theme": "elegant-gold",
  "content_length": 5000
}
```

---

## SVG 贴图素材库

本工具内置丰富的 SVG 贴图素材，可用于装饰文章。贴图以代码形式嵌入，无需本地存储文件。

### 可用贴图分类

| 分类 | 贴图 | 说明 |
|------|------|------|
| **装饰** | star, heart, sparkle, flower, leaf | 星星、爱心、闪光、花朵、叶子 |
| **箭头** | arrow_right, arrow_down, arrow_curved | 右箭头、下箭头、弯曲箭头 |
| **标签** | tag, bookmark, flag | 标签、书签、旗帜 |
| **形状** | circle_ring, diamond, hexagon | 圆环、菱形、六边形 |
| **特殊** | ribbon, crown, lightning, chat_bubble, music_note, gift | 丝带、皇冠、闪电、对话气泡、音符、礼物 |

### 在 Markdown 中使用贴图

在 Markdown 中使用特殊语法插入贴图：

```markdown
# :star: 标题前加星星

正文内容 :heart: 可以在行内插入

::divider::  # 插入分隔线装饰

::tip:: 这是提示框内容

::important:: 这是重要标记
```

### 贴图主题

`xiumi-style` 主题自动使用贴图装饰：
- 标题前自动添加旗帜图标
- 章节间自动添加叶子分隔线
- 顶部自动添加花朵装饰

---

## 注意事项

### 1. 表格显示问题

表格在手机端可能显示不全。本工具会检测文档中的表格并提醒用户，但**不提供表格转图片功能**。

**建议**：
- 发布前使用其他工具（如 markdown-to-image skill）将表格转换为图片
- 在 Markdown 中直接使用图片替代表格
- 确认表格在手机端可接受后，使用 `--force` 参数强制发布

### 2. 内容长度限制

微信草稿 API 限制 **content < 20,000 字符**。

**建议**：
- 长文章拆分为多篇发布
- 使用简洁主题（如 `minimal-blue`）可减少样式体积

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