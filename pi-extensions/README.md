# Pi Extensions

存储 [Pi](https://github.com/earendil-works/pi-mono) 扩展（TypeScript 模块），扩展 Pi 的行为，包括自定义工具、命令、事件拦截、UI 组件等。

## 目录结构

- `common/` - 通用扩展目录
- `shared/` - 共享扩展目录，按需放入指定项目的 `.pi/extensions/` 目录

## 扩展规范

每个扩展目录可包含：

- `index.ts` 或单文件 `.ts` - 扩展入口（必需）
- `upstream.json` - 上游信息（外部扩展建议提供）
- `package.json` - 如有 npm 依赖则必需

## 扩展格式

Pi 扩展是 TypeScript 模块，导出一个接收 `ExtensionAPI` 的默认工厂函数：

```typescript
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default function (pi: ExtensionAPI) {
  pi.on("session_start", async (_event, ctx) => {
    ctx.ui.notify("Extension loaded!", "info");
  });
}
```

详细 API 参见 [Pi 扩展文档](https://github.com/earendil-works/pi-mono/blob/main/docs/extensions.md)。
