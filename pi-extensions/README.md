# Pi Extensions

存储 [Pi](https://github.com/earendil-works/pi-mono) 扩展（TypeScript 模块），扩展 Pi 的行为，包括自定义工具、命令、事件拦截、UI 组件等。

## 目录结构

- `common/` - 通用扩展，已通过目录级符号链接到全局 `~/.pi/agent/extensions/`，所有项目自动加载
- `shared/` - 共享扩展，按需链接到指定项目的 `.pi/extensions/` 目录

## 使用方式

### 全局扩展（common）

`common/` 目录已链接为 `~/.pi/agent/extensions/`，扩展放入即可全局生效，无需额外操作。

如需在其他机器上设置：

```bash
ln -s ~/Code/opencode-skills/pi-extensions/common ~/.pi/agent/extensions
```

### 项目级扩展（shared）

将扩展文件放入 `shared/` 目录，然后按需链接到项目的 `.pi/extensions/` 目录：

```bash
# 使用脚本链接
~/Code/opencode-skills/scripts/link-skills.sh pi-extension <extension-name> /path/to/project

# 或手动链接
ln -s ~/Code/opencode-skills/pi-extensions/shared/my-extension.ts /path/to/project/.pi/extensions/my-extension.ts
```

## 扩展规范

每个扩展目录应包含：

- `index.ts` 或单文件 `.ts` - 扩展入口（必需）
- `upstream.json` - 上游信息（外部扩展必需，自开发扩展填 `"source": "self-developed"`）
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
