# JS 通道兜底流程

> 阅读时机：API 发布失败（如错误码 45002 内容超长、40164 IP 白名单），需要改用官方 JS 通道发布时。

API 失败时，提示用户改用官方 JS 通道（`__MP_Editor_JSAPI__`），流程如下：

## 操作步骤

1. **AI 打开** ego 浏览器微信公众号链接：`https://mp.weixin.qq.com/cgi-bin/home`
2. **交还操作权给用户**（`handOffTaskSpace`），请用户配合：
   - 扫码登录（如未登录）
   - 进入「草稿箱 → 新建图文」，打开一个编辑器页面
3. 用户操作完成后反馈 AI，**AI 拿回操作权**（`takeOverTaskSpace`）
4. **AI 执行 JS API 注入内容**：
   - 找到编辑器 tab（URL 含 `appmsg_edit`）
   - 等待编辑器就绪：
     ```js
     window.__MP_Editor_JSAPI__.invoke({
       apiName: 'mp_editor_get_isready',
       sucCb: (res) => { /* res.isNew === true 时才可注入 */ },
       errCb: (err) => { /* 报错则重试 */ }
     })
     ```
   - 注入完整 HTML（HTML 由 `convert` 命令生成）：
     ```js
     window.__MP_Editor_JSAPI__.invoke({
       apiName: 'mp_editor_set_content',
       apiParam: { content: '<完整HTML>' },
       sucCb: (res) => { /* 文章内容设置成功 */ },
       errCb: (err) => { /* 注入失败 */ }
     })
     ```
   - 注入后可通过 `mp_editor_get_content` 验证内容完整
5. **AI 操作完成，交还操作权给用户**，后续「保存为草稿 / 预览 / 发表」由用户自行完成

## 注意事项

> [!NOTE] JS 通道注意事项
> - 必须等 `mp_editor_get_isready` 返回 `isNew: true` 才能注入
> - 注入的是转换器产出的 HTML 文件内容（如 `/tmp/article.html`），通过 `convert --output` 生成
> - JS 通道不受 2 万字符限制，但样式清洗规则与 API 相同（气泡等依赖定位的样式会被剥，见「theme-development.md → 气泡实现约定」）
> - 编辑器页面刷新后 `__MP_Editor_JSAPI__` 需要重新就绪等待

## 内容长度限制背景

微信草稿 API（`draft/add`）限制 **content < 20,000 字符**。

**API 超限时（错误码 45002）**，按上述流程走 JS 通道兜底：
- JS 通道（`__MP_Editor_JSAPI__.mp_editor_set_content`）实测无 2 万字符限制

**其他建议**：
- 代码块/表格转图片可大幅压缩字符占用（图片仅 ~80 字符）
- 长文章拆分为多篇发布
- 使用简洁的 `ai-bubble` 主题可减少样式体积
