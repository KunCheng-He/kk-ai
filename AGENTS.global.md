# AGENTS.global.md

全局代理规则，适用于所有项目。

## 小红书帖子详情访问

使用 `ego-browser` skill 访问小红书并获取帖子详情时，**不能直接将不带参数的帖子链接交给 ego 浏览器打开**，否则通常无法正常访问帖子详情。必须采用以下方式之一：

1. 仍然使用 ego-browser 打开详情，但必须将帖子 ID、`xsec_token` 和 `xsec_source=pc_feed` 拼入详情 URL：`https://www.xiaohongshu.com/explore/{帖子ID}?xsec_token={xsec_token}&xsec_source=pc_feed`。`xsec_token` 应从小红书搜索结果或帖子元数据中获取。
2. 使用 ego-browser 模拟用户点击，从小红书页面中的帖子入口打开详情。
