# DeepSeek Harness（DSH）适配

本文件只写「在这套工具上怎么做到」。流程规则一律在 `SKILL.md`，这里不新增任何流程规则。

## 加载方式

- skill 由项目 `.dsh/skills/` 或用户级技能目录发现；触发关键词命中后主 Agent 加载本 skill。
- 角色加载：用 `subagent` 派生子代理，prompt 里把 `roles/writer.md` 或 `roles/reviewer.md` 的**绝对路径**给它，要求先读该文件再执行，并声明「先调用 `skill` 加载 `woaile-gzh`」以取得项目上下文。
- 不要复制规范正文进 prompt：规范只在 `roles/` 维护，prompt 里只放路径与任务输入。
- 主 Agent 负责关口：子代理不能向用户提问，三个关口都用 `ask_user_question` 在主会话完成。

## 派生与续接

| 动作 | DSH 写法 |
|---|---|
| 派生执行者 | `subagent`，立即返回 `agent_id`，结果稍后以完成通知到达 |
| 等结果 | 必须等子代理返回或收到运行时通知，才能向用户展示大纲/成稿或进下一阶段 |
| 续接 | `send_message(agent_id, …)` 唤醒原会话，上下文与浏览器 task space 都保留 |
| 补采 | 一律续接同一个采集子代理；不要新建，新建会丢掉 ego 登录态 |

子代理约束（DSH 实际行为，按此设计任务）：

- 不能再派生 subagent → 浏览器采集只能由一个子代理串行做完，不做多层委派
- 不能向用户提问、不能请求审批 → 任何需要审批的操作会被自动拒绝
- 只派项目内读写、`web_fetch`、`ego-browser` 这类无需审批的任务；不要让子代理 `sudo`、装软件、写工作区外路径
- 「只读」只能靠 prompt 约束，没有权限等价物 → 审查后自己 `git diff` 确认没改稿

## 取数

- **静态页面**：`web_fetch`。页面少时主 Agent 直接取，但不要把整页 HTML 留在主上下文。
- **搜索、登录态、动态渲染、翻页、截图**：`ego-browser`。子代理 prompt 要求先 `skill` 加载 `ego-browser`，用 heredoc 方式执行；与用户共用浏览器配置，用户登录后即可用。
- 图片初审：`read_image` 能读才读；读不了就退回可编程校验（`sips -g pixelWidth -g pixelHeight`、`file`、`stat -f%z`）。

## 发布

先解析发布器目录，再执行。不要用 `uv run`（会读写工作区外的 uv 缓存）。

```bash
PUB="$(realpath woaile-gzh)/scripts/publisher"
test -x "$PUB/.venv/bin/python" && echo "venv ok"
```

```bash
# 配置检查（输出自动脱敏）
PYTHONDONTWRITEBYTECODE=1 "$PUB/.venv/bin/python" "$PUB/main.py" config check

# 转换预检：不产生草稿、不上传素材
PYTHONDONTWRITEBYTECODE=1 "$PUB/.venv/bin/python" "$PUB/main.py" publish "{成稿绝对路径}" --cover "{封面绝对路径}" --dry-run
```

真实发布要把 `HOME` 指到临时目录：发布器把 token 缓存在 `~/.cache/woaile-gzh-publisher`，Workspace Write 下工作区外不可写。

```bash
HOME="${TMPDIR:-/tmp}/woaile-gzh-home" \
PYTHONDONTWRITEBYTECODE=1 \
"$PUB/.venv/bin/python" "$PUB/main.py" publish "{成稿绝对路径}" --cover "{封面绝对路径}"
```

每次 bash 调用都是新 shell，`PUB` 必须在同一条命令里重新解析。

## 已知限制

| 限制 | 采取的降级 |
|---|---|
| 子代理不能提问 | 阻塞项写进子代理返回，由主 Agent 用 `ask_user_question` 统一问 |
| 子代理不能再派生 | 采集任务一次给全；需要补采取续接而非拆任务 |
| 无「只读」权限硬约束 | prompt 声明 + 事后 `git diff` 验收 |
| 桌面版不继承终端 shell 环境变量 | 缺 `WOAILE_GZH_APPID/SECRET` 时请用户注入，不要 echo 值 |
| 工作区外不可写 | token 缓存用 `HOME` 覆盖到 `$TMPDIR` |