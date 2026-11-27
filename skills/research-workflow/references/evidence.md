# 证据规范

## 一条证据

每条证据都是提炼后的记录，不含 DOM、原始 HTML、快照或抓取日志：

```yaml
- evidence_id: zhihu-01          # 前缀-两位序号，全流程唯一
  claim: 可直接写入报告的事实或观点
  source_title: 具体页面或帖子标题
  source_url: https://...        # 具体内容页，禁止首页或搜索页
  platform: 来源平台
  published_at: 2026-11-20       # 无发布时间写 not stated
  retrieved_at: 2026-11-25       # 实际抓取日期
  evidence_type: official | community | repository | review
  engagement: null               # 点赞/评论/Stars，无则 null
  confidence: high | medium | low
```

可选字段：`quote`（原文关键句，≤120 字）、`cross_ref`（与哪条证据互相印证或冲突）。

写法约定：

- `source_url` 是标准字段名。旧文件里的 `url:` 仍可用，门禁会通过但给一条警告，迁移时统一为 `source_url`。
- `confidence` 只写三档之一。需要解释理由时写进 `claim` 或 `quote`，不要在字段值里追加括号说明（门禁容忍但会警告）。
- `evidence_type` 建议用上面四个值，允许更细的后缀（如 `official_pricing`、`official_blog`）。门禁只依赖 `community` 判定首页与日期规则。

规则：

- 不确定的字段写 `not stated` 或 `null`，**不得猜测**。
- `source_url` 必须带路径；`https://www.zhihu.com/` 这种首页不算来源。
- 编号在整个调研内唯一；**补采顺延**，不复用、不重排已有编号。
- 竞品对比另需记录：对比维度、该维度上的取数口径（谁测的、什么环境）。

## 证据文件头（机读）

每份证据文件的第一段必须是 YAML front-matter，供 `scripts/check-evidence.mjs` 判定：

```markdown
---
run: 20261125_example-topic
status: collecting            # collecting | complete
frozen_at: null               # status 为 complete 时必填，格式 YYYY-MM-DD HH:MM
counts:
  zhihu: 6
  v2ex: 4
  off: 3
failures:
  - 某内容平台：登录墙，首轮未登录搜索为空，已请用户登录后补采
  - 豆瓣：不适用（非书籍/影视/音乐产品）
---
```

- `counts` 的数字必须等于正文实际条数，门禁脚本会逐前缀核对。
- `failures` 必须存在；没有失败就写空列表 `[]`，不能省略。
- 旧格式（`> status: complete` 引用块）不再接受，脚本会提示改写。

## 冻结协议

1. 采集过程中 `status: collecting`，每次补采都更新 `counts` 与 `failures`。
2. 只有协调者宣布"这是最终采集轮次"后，采集方才写 `status: complete` 和 `frozen_at`。
3. 写 `complete` 后**不得再追加证据**。确需追加 → 改回 `collecting`，重跑门禁，重新冻结。
4. 冻结前必须跑一次 `scripts/check-evidence.mjs`，退出码 0 才算冻结完成。
5. 写作阶段只能读冻结后的文件；期间新增的内容一律不进入报告。

## 多份证据文件

允许拆分（例如交互式采集、静态官方、竞品各一份），但每份都要有头，且：

- `run` 字段相同；
- 编号前缀不重叠；
- 门禁脚本按前缀合并计数，总表与各文件的 `counts` 之和一致。

协调者汇总时以"合并后的总数"为准，并在报告附录里按平台分组。

## 冲突证据

两条证据互相矛盾时（版本号、价格、口径、体验差异）：

- **都保留**，不要择一丢弃；
- 在 `claim` 里写清分歧点，`confidence` 降级一档；
- 报告里并列呈现，标注「口径冲突」并说明来源差异（时间、地区、版本）；
- 若冲突影响核心结论，写进「数据局限」。

## 失败记录

每条失败写清四件事：来源、失败类型（登录墙／验证码／反爬／无结果／超时／页面不存在）、尝试过的入口、是否已降级。

- **空结果不等于没有内容**：未登录状态下搜索为空是账号态问题，不是平台无讨论。
- 站外检索（搜索引擎 `site:` 查询）只能作为降级路径，证据里标注 `confidence: low/medium` 与「非站内搜索」。
- 降级后必须回写三处：证据文件的 `failures`、报告里的样本量、「数据局限」中的首轮结论是否被推翻。

## 禁止

- 不返回浏览器快照、accessibility tree、DOM、原始 HTML、控制台或网络日志。
- 不把平台首页、搜索页、只含关键词的链接当来源。
- 不为凑数把同一内容页拆成多条证据。
- 不在证据里记录账号昵称、头像等身份信息；互动数只记数字。
