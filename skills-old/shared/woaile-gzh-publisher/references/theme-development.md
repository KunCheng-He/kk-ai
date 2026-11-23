# 主题系统开发指南

> 阅读时机：需要新增主题、修改现有主题样式、或理解 Markdown → 公众号 HTML 的转换机制时。

主题样式通过 CSS 文件定义（`scripts/themes/css/` 目录），辅以 YAML 配置文件描述卡片、贴图等元信息。

## 主题文件结构

```
themes/css/
├── ai-bubble.css        # 主题 CSS 样式
└── ai-bubble.yaml       # 主题元信息（名称、描述、卡片配置、贴图配置）
```

## CSS 文件规范

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

## YAML 配置项

```yaml
name: ai-bubble
description: Logo 同款气泡标题，纯白底与藏蓝品牌色
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

## 新增主题

创建新主题只需在 `themes/css/` 下添加两个文件：
1. `主题名.css` — 定义所有元素的样式
2. `主题名.yaml` — 填写名称、描述，可选配置卡片和贴图

无需编写任何 Python 代码。

## 转换流程

```
Markdown → Python-markdown → HTML (无样式)
    → 添加 .article-content 容器
    → premailer 将 CSS 内联化
    → 列表标记转换（<ul>/<ol>/<li> → <section>）
    → 代码块转换（<pre><code> → <section>）
    → 提取容器样式、移除包装 div
    → wrap_content 添加卡片/贴图装饰
    → 最终公众号 HTML
```

## 微信编辑器适配机制

微信公众号后台编辑器会清洗多种内联样式和 HTML 结构，以下转换均为此设计。

### 列表标记转换

微信编辑器会破坏 `<ul>/<ol>/<li>` 的内联样式，导致分点叙述内容在编辑后格式错乱。本工具在 premailer 内联化之后，自动将列表标记转换为 `<section>` 结构：

- `<ul>/<li>` → `<section>` 容器 + 带 `• ` 前缀的 `<section>` 项
- `<ol>/<li>` → `<section>` 容器 + 带 `1. 2. 3.` 前缀的 `<section>` 项
- 每个列表项使用 `padding-left` + `text-indent` 实现悬挂缩进
- 自动继承 `line-height`、`color`、`letter-spacing` 等排版属性
- 列表项显式补齐 `text-align: left`：微信编辑器对无显式对齐的块级元素默认应用两端对齐（justify），多行列表项的词间距会被撑开
- 支持嵌套列表（自底向上逐层转换）
- 保留 `<li>` 内的 `<strong>`、`<code>`、`<a>` 等行内元素

### 代码块转换

微信编辑器会剥离 `white-space` 属性并破坏 `<pre><code>` 结构，导致代码缩进和换行全部丢失。本工具自动将代码块转换为逐行 `<section>` 结构：

- `<pre><code>` → 容器 `<section>`（保留背景色、字体、圆角等样式）+ 逐行 `<section>`
- 缩进空格转为 `\u00a0`（不换行空格），防止编辑器压缩
- 空行用 `\u00a0` 占位，防止被编辑器折叠
- 每行带 `line-height` + `white-space: nowrap`，配合容器 `overflow-x: auto` 实现**长行横向滑动**；若微信剥离 `white-space` 则优雅退化为自动换行
- 每行显式 `text-align: left`，防止微信编辑器默认的两端对齐（justify）拉伸代码行
- 行内 `<code>` 标签保持不变

### 表格样式增强

主题可为表格定义圆角描边风格（如 ai-bubble 的藏蓝 2px 描边 + 12px 圆角）。由于微信编辑器会剥离 `:nth-child` 等伪类选择器，转换器（`_wechat_safe_tables`）在内联化后对表格做后处理：

- **`<table>` → `<section>` 网格**（核心机制）：所有表格会被转换为 `<section>` 网格（`display: table / table-row / table-cell`），单元格样式原样保留。微信网页编辑器在用户**编辑**草稿时会归一化外来 `<table>`，将其分裂为「空壳（`<caption>`+`<tfoot>` 占位行，保留原表格样式）+ 新内容表」，空壳在表格顶部渲染为空行；改为 section 网格后编辑器只当它是普通 section，彻底绕过归一化，且 CSS table 布局的渲染效果与真表格完全一致
- **边框/圆角在包裹容器上**：表格的 `border`/`border-radius`/`margin` 放到外层包裹的 `<section>`（带 `overflow: hidden`）
- **交替行背景色**：斑马纹颜色自动从表格描边色派生（6% 透明度），适配任意主题配色
- **角落圆角**：表头两角、末行两角自动补齐内圆角（表格圆角 − 描边宽度），末行底部分隔线自动移除
- 仅对主题设置了 `border-radius` 的表格应用描边包裹和斑马纹/圆角增强，其他表格只做网格化转换

## ai-bubble 主题装饰细节

`ai-bubble` 主题自动使用贴图装饰：

- 顶部添加 Logo 同款气泡轮廓（**前面留一个可编辑空行**，方便在公众号网页编辑器中定位光标插入内容，如公众号名片）
- 二级标题使用 Logo 同款气泡轮廓（手绘感不对称圆角 + J 形弯钩尾巴，**不依赖 position 定位**，微信清洗后仍保留）
- 文章底部添加藏蓝色叶子分隔线（**前后各留一个可编辑空行**，方便手工插入二维码、关注引导等内容）

> [!IMPORTANT] 装饰贴图实现说明
> 微信公众号后台编辑器会剥离 `<div>` 上的 `text-align` 等内联样式，导致装饰图标居中失效。顶部装饰和底部分隔线必须使用 `<section style="text-align: center; ...">` 实现居中（base.py `wrap_content`、stickers.py `get_sticker_html`/`get_section_divider`）。可编辑空行为 `<section><br/></section>`。

> [!IMPORTANT] 气泡实现约定
> 微信服务端保存时会清洗 `position:relative/absolute` 等定位样式，因此气泡标题使用**纯 CSS 边框 + 不对称 border-radius** 实现，弯钩尾巴是一个**普通块级内联 SVG**（非定位叠加层），通过负 margin 与气泡边框咬合（converter.py `_inject_h2_bubble`）。修改主题时请保持此约定：不使用 `position`、`transform`，椭圆 slash 圆角语法也有被清洗的风险，避免使用。
