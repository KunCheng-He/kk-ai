# AGENTS.global.md

全局代理规则，适用于所有项目。

## 浏览器自动化

当需要使用浏览器（如浏览网页、自动化操作、截图等）时：

1. **使用 `playwright-cli` SKILL** — 加载该 skill 后通过 CDP 连接用户的默认浏览器，**不要安装浏览器**（不要运行 `npx playwright install` 或 `npm install playwright`）。
2. **CDP 连接方式**：
   - 默认使用 `playwright-cli attach --cdp=http://localhost:9222`
   - 如果连接失败，执行命令 `brave-debug`（位于 `~/.my_shell/brave-debug`），它会以调试模式启动 Brave 浏览器并开启远程调试端口。启动后重试上一步的连接命令。
   - 如果 `brave-debug` 也失败，应主动询问用户希望使用哪种方式连接到浏览器（如指定其他 CDP 端口、使用其他浏览器等）。
3. **清理标签页**：浏览器操作完成后，必须关闭本次任务过程中由自动化打开的所有标签页（仅关闭新开的、保留用户原有的标签页），避免遗留一堆空标签页。建议在任务结束前统一关闭，不要依赖浏览器自动回收。


