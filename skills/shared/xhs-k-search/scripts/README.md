# xhs-k-search

小红书搜索脚本，通过浏览器自动化技术获取搜索结果、帖子内容及评论数据。

## 功能特性

- 搜索关键词获取帖子列表
- 获取帖子详情与评论
- 登录状态持久化
- 支持无头模式（搜索功能）

## 技术栈

- Python 3.10+
- [Playwright](https://playwright.dev/) - 浏览器自动化
- [playwright-stealth](https://github.com/AtinyOne/Playwright-stealth) - 反爬检测规避
- [Pydantic](https://docs.pydantic.dev/) - 数据模型

## 安装

```bash
uv sync
uv run playwright install chromium
```

## 使用方法

### 登录

```bash
uv run python main.py --login
```

打开浏览器窗口，完成扫码登录。登录状态保存到 `auth.json`。

### 搜索

```bash
# 有头模式
uv run python main.py --keyword "Python"

# 无头模式
uv run python main.py --keyword "Python" --headless
```

### 获取帖子详情

```bash
uv run python main.py --note-id <帖子ID> --xsec-token <token>
```

> 帖子详情功能因反爬限制，强制使用有头模式。

## 数据结构

搜索结果返回 `SearchResult`：

```json
{
  "items": [
    {
      "note_id": "...",
      "xsec_token": "...",
      "title": "标题",
      "cover": "封面图",
      "author": {"user_id": "...", "nickname": "..."},
      "liked_count": 100,
      "comment_count": 10,
      "url": "https://www.xiaohongshu.com/explore/..."
    }
  ],
  "total": 20,
  "has_more": true
}
```

帖子详情返回 `NoteDetailWithComments`：

```json
{
  "note": {
    "note_id": "...",
    "title": "标题",
    "desc": "正文",
    "image_list": ["..."],
    "tag_list": ["标签"],
    "author": {...}
  },
  "comment_list": [
    {"comment_id": "...", "content": "...", "user": {...}}
  ]
}
```

## 项目结构

```
xhs-k-search/
├── main.py              # 入口
├── login_helper.py      # 登录
└── xhs_utils/
    ├── browser.py       # 浏览器管理
    ├── api_handler.py   # API 拦截与解析
    └── data_models.py   # Pydantic 模型
```

## 注意事项

- `auth.json` 不纳入版本控制
- 登录失效时删除 `auth.json` 重新登录
- 帖子详情功能不支持无头模式（反爬限制）

## 免责声明

本项目仅供学习研究使用，仅供个人合法合规使用。

- 请遵守小红书用户协议及相关法律法规
- 严禁用于商业用途、数据倒卖、恶意爬取等违法行为
- 使用本项目所产生的一切后果由使用者自行承担
- 项目作者不对因使用本项目造成的任何损失或法律纠纷负责

使用本代码即表示您已阅读并同意以上声明。
