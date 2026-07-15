---
name: xhs-k-search
description: |
  小红书数据搜索与调研工具。通过浏览器自动化技术获取小红书搜索结果、帖子详情和评论数据。当用户需要从小红书获取信息时务必使用此技能，包括：搜索小红书关键词获取帖子列表、获取某篇帖子的详细内容和评论、进行产品调研或竞品分析需要从小红书收集数据。触发关键词："小红书"、"xhs"、"小红书搜索"、"小红书帖子"、"小红书调研"、"小红书评论"、"XHS search"。即使用户未明确提及"小红书"，但上下文暗示需要中文社交媒体数据或消费类产品调研时，也应考虑使用。
---

# 小红书数据搜索与调研

通过 Playwright 浏览器自动化获取小红书数据，支持关键词搜索和帖子详情获取。

## 环境准备

**CDP 模式（默认）**：只需 Python 依赖，无需安装 Chromium：

```bash
cd scripts && uv sync
```

**Launch 模式（仅 `--no-cdp` 时）**：额外需要 Chromium，且仅当未安装时才安装：

```bash
# 检测是否已安装
uv run playwright install chromium --dry-run 2>&1 | grep -q "already" || uv run playwright install chromium
```

## 工作流程

### 0. 环境检测与初始化

**默认流程（CDP 模式）**：只需检测 Python 依赖：

```bash
ls scripts/.venv 2>/dev/null
```

若检测失败，执行：

```bash
cd scripts && uv sync
```

**注意**：CDP 模式下 **绝不安装 Chromium**。只有用户显式使用 `--no-cdp` 切到 Launch 模式时，才检测并安装 Chromium。

**Launch 模式流程**：除 Python 依赖外，还需检测 Chromium 浏览器：

```bash
uv run python -c "from playwright.sync_api import sync_playwright; p=sync_playwright().start(); print(p.chromium.executable_path); p.stop()" 2>/dev/null
```

若检测失败（Chromium 未安装），执行：

```bash
cd scripts && uv run playwright install chromium
```

### 1. 确保浏览器就绪（CDP 模式）

默认使用 CDP 模式，连接已有浏览器，无需单独登录。

**检测 CDP 端口**：

```bash
curl --noproxy '*' -s http://localhost:9222/json/version
```

**处理策略**：
- CDP 端口就绪 → 直接执行搜索/详情命令
- CDP 端口未就绪 → 提示用户："需要启动浏览器的远程调试模式。请退出当前浏览器，然后以调试模式重新启动它。" 
  - 若用户不知道如何操作，询问："你使用的是什么浏览器？（Chrome / Brave / Edge / ...）"
  - 根据用户回答，给出对应启动命令：
    - **Chrome**: `open -a "Google Chrome" --args --remote-debugging-port=9222`（macOS）或 `google-chrome --remote-debugging-port=9222`（Linux）
    - **Brave**: `open -a "Brave Browser" --args --remote-debugging-port=9222`（macOS）
    - **Edge**: `open -a "Microsoft Edge" --args --remote-debugging-port=9222`（macOS）或 `microsoft-edge --remote-debugging-port=9222`（Linux）
  - 等待用户确认浏览器已启动后，重新检测端口
- 无法使用 CDP → 使用 `--no-cdp` 切回 Launch 模式

### 2. Launch 模式登录（仅 --no-cdp 时需要）

Launch 模式下需要单独登录小红书。登录状态存储在 `scripts/auth.json`。

```bash
# 检查认证文件
ls scripts/auth.json
# 检查认证是否有效
cd scripts && uv run python main.py login --check
```

**处理策略**：
- 认证文件不存在 → 提示用户"需要完成小红书登录认证"，然后执行登录命令
- 认证已失效 → 提示用户"认证已失效，需要重新登录"，然后执行登录命令

**登录命令**：

```bash
cd scripts && uv run python main.py login
```

浏览器窗口会打开，提示用户在浏览器中完成登录（扫码或账号密码），登录成功后自动保存状态。

### 3. 执行搜索

**CDP 模式（默认）**：
```bash
cd scripts && uv run python main.py search "关键词" --limit 20
```

**Launch 模式**：
```bash
cd scripts && uv run python main.py search "关键词" --limit 20 --no-cdp
```

**保存结果到文件**：
```bash
# 保存到 /tmp/xhs-cache/（自动命名）
cd scripts && uv run python main.py search "关键词" --save

# 保存到指定路径
cd scripts && uv run python main.py search "关键词" -o /path/to/output.json
```

**参数说明**：
- `keyword`: 搜索关键词（必需）
- `--limit, -l`: 返回数量，默认 20
- `--save, -s`: 保存结果到 `/tmp/xhs-cache/`（自动命名）
- `--output, -o`: 指定输出文件路径（JSON）

### 4. 获取详情

**CDP 模式（默认）**：
```bash
cd scripts && uv run python main.py detail "帖子ID" --xsec-token "token值"
```

**Launch 模式**：
```bash
cd scripts && uv run python main.py detail "帖子ID" --xsec-token "token值" --no-cdp
```

**仅传入帖子 ID（无 xsec_token）**：
```bash
cd scripts && uv run python main.py detail "帖子ID"
```

**保存详情到文件**：
```bash
# 保存到 /tmp/xhs-cache/（自动命名）
cd scripts && uv run python main.py detail "帖子ID" --save

# 保存到指定路径
cd scripts && uv run python main.py detail "帖子ID" -o /path/to/output.json
```

**参数**：
- `note_id`: 帖子 ID（必需）
- `--xsec-token`: 帖子 xsec_token
- `--save, -s`: 保存结果到 `/tmp/xhs-cache/`（JSON 格式）
- `--output, -o`: 指定输出文件路径（JSON）

## 数据结构

### SearchResult（搜索结果）

| 字段 | 说明 |
|------|------|
| items | 帖子列表 |
| total | 总数 |
| has_more | 是否有更多 |

### Note（帖子摘要）

| 字段 | 说明 |
|------|------|
| note_id | 帖子ID |
| xsec_token | 访问token |
| title | 标题 |
| cover | 封面图URL |
| author | 作者（user_id, nickname, avatar） |
| liked_count | 点赞数 |
| comment_count | 评论数 |
| collect_count | 收藏数 |
| url | 帖子链接 |

### NoteDetail（帖子详情）

| 字段 | 说明 |
|------|------|
| desc | 正文内容 |
| image_list | 图片URL列表 |
| tag_list | 标签列表 |
| create_time | 创建时间戳 |

### Comment（评论）

| 字段 | 说明 |
|------|------|
| comment_id | 评论ID |
| user | 评论者信息 |
| content | 评论内容 |
| liked_count | 点赞数 |

完整数据模型见 `references/data-models.md`。

## 输出处理

调用脚本后，解析输出并整理：

1. **搜索结果**：汇总标题、作者、互动数据、链接
2. **帖子详情**：展示正文、标签、互动数据、图片
3. **评论分析**：整理热门评论和用户反馈

## 注意事项

- **CDP 模式**（默认）：连接到已有浏览器，无需单独登录，日常推荐使用
- **Launch 模式**（`--no-cdp`）：启动独立 Chromium，需要先执行 `login` 命令保存认证状态
- CDP 模式下帖子详情会自动弹出浏览器窗口（反爬限制），这是正常现象
- 登录状态有时效，Launch 模式下失效时重新执行 `login` 命令
- 帖子详情功能不支持无头模式，Launch 模式下会自动使用有头模式
- 仅供个人学习研究使用，遵守小红书用户协议
