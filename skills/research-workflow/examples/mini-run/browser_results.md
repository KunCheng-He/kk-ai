---
run: mini-run
status: complete
frozen_at: 2026-11-25 21:40
counts:
  off: 2
  zhihu: 1
  v2ex: 1
failures:
  - 小红书：登录墙，本轮未登录搜索为空，已降级为站外检索并标注低置信度
---

# 证据：示例主题

## 官方

- evidence_id: off-01
  claim: 产品定位为"面向个人开发者的本地优先笔记工具"，提供免费版与每月 19 元的专业版
  source_title: 产品定价页
  source_url: https://example.com/pricing
  platform: 官方网站
  published_at: not stated
  retrieved_at: 2026-11-25
  evidence_type: official
  engagement: null
  confidence: high

- evidence_id: off-02
  claim: 1.4.0 版本新增端到端加密，正式版发布于 2026-11-20
  source_title: 1.4.0 Release Notes
  source_url: https://example.com/docs/releases/1.4.0
  platform: 官方文档
  published_at: 2026-11-20
  retrieved_at: 2026-11-25
  evidence_type: official
  engagement: null
  confidence: high

## 社区

- evidence_id: zhihu-01
  claim: 有用户反馈 1.4.0 的同步在弱网下会卡住，需手动重试
  source_title: 如何评价这款笔记工具 1.4？
  source_url: https://www.zhihu.com/question/100000/answer/200000
  platform: 知乎
  published_at: 2026-11-18
  retrieved_at: 2026-11-25
  evidence_type: community
  engagement: 128 赞
  confidence: medium

- evidence_id: v2ex-01
  claim: 讨论区普遍认为本地优先是主要卖点，但插件生态落后于同类产品
  source_title: 本地优先笔记工具的使用体验
  source_url: https://www.v2ex.com/t/900001
  platform: V2EX
  published_at: 2026-11-20
  retrieved_at: 2026-11-25
  evidence_type: community
  engagement: 32 回复
  confidence: medium
