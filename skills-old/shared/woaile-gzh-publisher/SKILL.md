---
name: woaile-gzh-publisher
description: |
  「我AI了」微信公众号定制发布工具。将 Markdown 文档转换为公众号友好格式并发布到草稿箱。严格定制适用于「我AI了」公众号（ai-bubble 主题即「我AI了」品牌视觉）。
  
  触发场景：
  - 用户要求将文档/文章发布到「我AI了」微信公众号
  - 用户提到"公众号"、"微信文章"、"草稿箱"
  - 用户需要 Markdown 转微信公众号格式
  
  支持的功能：
  - Markdown 转公众号风格 HTML（ai-bubble 主题）
  - 自动上传图片到微信 CDN
  - 自动提取标题、摘要、封面图
  - 支持 YAML frontmatter 元信息
  - 表格检测与发布确认提醒
  - 发布到公众号草稿箱
  
  注意：本工具不提供表格转图片功能。如文档包含表格，会提醒用户确认后再发布。Agent 应自行判断如何将表格转为图片。
---

# 微信公众号草稿发布工具

将 Markdown 文档转换为微信公众号友好格式，并发布到草稿箱。

## 环境变量配置

使用前需配置以下环境变量：

```bash
export WOAILE_GZH_APPID="「我AI了」公众号AppID"
export WOAILE_GZH_SECRET="「我AI了」公众号Secret"
```

获取方式：
1. 登录微信公众平台 mp.weixin.qq.com
2. 进入「设置与开发」→「基本配置」
3. 获取 AppID 和 AppSecret
4. **将服务器 IP 添加到白名单**（否则 API 调用会返回 40164 错误）

> [!IMPORTANT] 密钥安全（Agent 必须遵守）
> 验证配置**只能**运行 `uv run main.py config check`，其输出已自动脱敏。严禁：
> - 执行 `echo $WOAILE_GZH_APPID`、`env`、`printenv`、`set` 等会输出变量值的命令来「验证配置」
> - 读取 `~/.zshrc` 等 shell 配置文件查看密钥内容
> - 在对话回复、日志或任何文件中复述完整 AppID/AppSecret
>
> 若工具输出的错误信息中出现疑似密钥的字符串（正常情况下已脱敏），不要原样转述给用户。

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
uv run main.py publish article.md --theme ai-bubble
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
theme: ai-bubble
---

# 正文开始...
```

> [!IMPORTANT] 标题是必填项
> 文章**必须提供标题**，否则发布将失败（微信 API 返回 44004 错误）。标题来源有两个途径（按优先级）：
> 1. frontmatter 中的 `title` 字段
> 2. 正文中的第一个 `# ` 一级标题（注意：`## ` 二级标题不会被提取为文章标题）
>
> 如果两者都没有，请 Agent 在发布前提醒用户补充标题。

## 可用主题

| 主题名 | 描述 | 适用场景 |
|--------|------|----------|
| **ai-bubble** | **AI 对话气泡，极简公众号风，标题使用「我AI了」Logo 同款气泡轮廓（手绘感不对称圆角 + 左下弯钩尾巴），纯白底 + 藏蓝品牌色** | **AI 工具介绍、普通人 AI 实践分享、技术教程** |

## 工作流程

1. 读取环境变量配置
2. 解析 Markdown 文件（提取 frontmatter、标题、摘要、图片）
3. 转换 Markdown 为公众号风格 HTML（CSS 模板 → premailer 内联化）
4. 检测文档是否包含表格、代码块，如有则**询问用户是否转图片，由用户决定**
5. 上传本地图片到微信 CDN
6. 上传封面图到微信永久素材库
7. **优先调用微信 API 创建草稿**（`draft/add`）
8. 返回草稿 media_id；**API 失败时按「JS 通道兜底流程」处理**

## 发布策略（重要）

成稿确定后，按以下优先级发布：

1. **代码块/表格转图片确认**：转换完成后，如检测到代码块或表格（返回 `needs_confirmation: true`），**必须询问用户**是否渲染为图片后发布，由用户决定；用户选择直接发布时使用 `--force`
2. **优先尝试 API**：`uv run main.py publish article.md --force` → 成功返回 `media_id`，完成
3. **API 失败 → JS 通道兜底**：提示用户改用官方编辑器 JS 通道注入内容，完整操作步骤见 [references/publishing-fallback.md](references/publishing-fallback.md)

## 按需阅读参考文档

以下细节文档仅在对应场景下阅读，无需默认加载：

| 场景 | 文档 |
|------|------|
| 新增/修改主题，理解转换机制与微信样式清洗规则 | [references/theme-development.md](references/theme-development.md) |
| API 发布失败（45002 超长等），走 JS 通道兜底 | [references/publishing-fallback.md](references/publishing-fallback.md) |
| 使用 SVG 贴图装饰或参考文献样式 | [references/writing-syntax.md](references/writing-syntax.md) |
| 排查错误码、查看命令返回 JSON 格式、平台限制 | [references/troubleshooting.md](references/troubleshooting.md) |
