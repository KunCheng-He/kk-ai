# OpenCode / Pi Skills & Agents 统一管理仓库

统一管理 OpenCode 和 Pi 的 Skills、Agents 及全局规则资源。

## 目录结构

```
kk-ai/
├── skills/
│   ├── common/          # 通用工具类 skill（ln 到全局）
│   └── shared/          # 共享 skill（项目按需 ln）
├── opencode-agents/
│   ├── common/          # OpenCode 通用 agent（ln 到全局）
│   └── shared/          # OpenCode 共享 agent（项目按需 ln）
├── pi-agents/
│   ├── common/          # Pi 通用主 agent（ln 到 ~/.pi/agent/main-agents/）
│   └── shared/          # Pi 共享主 agent（项目按需 ln 到 .pi/main-agents/）
├── pi-subagents/
│   ├── common/          # Pi 通用子 agent（ln 到 ~/.pi/agent/agents/）
│   └── shared/          # Pi 共享子 agent（项目按需 cp 到 .pi/agents/）
├── pi-extensions/
│   ├── common/          # Pi 通用扩展（ln 到 ~/.pi/agent/extensions/）
│   └── shared/          # Pi 共享扩展（项目按需 ln 到 .pi/extensions/）
├── scripts/             # 辅助脚本
├── AGENTS.global.md     # 全局代理规则（ln OpenCode + Pi 双 harness）
├── AGENTS.md            # 本仓库开发指南
└── README.md
```

## 资源清单

### Skills - Common（通用，已链接到全局）

| Skill | 来源 | 说明 |
|-------|------|------|
| `markdown-to-image` | self-developed | Markdown/代码片段转图片 |
| `mermaid` | self-developed | Mermaid 图表生成（mmdc CLI，渲染 SVG/PNG/PDF） |
| `project-init` | self-developed | 项目初始化工具（OpenCode / Pi 双支持） |
| `playwright-cli` | [Playwright](https://www.npmjs.com/package/@playwright/cli) | 浏览器自动化交互工具（手动更新） |
| `pi-agent-creator` | self-developed | 创建 Pi 主 Agent 定义文件（供 pi-agent-switcher 使用） |
| `skill-creator` | [anthropics/skills](https://github.com/anthropics/skills) | 创建新 skill |
| `skillify` | self-developed | 将会话过程捕获为 skill |
| `herdr` | [open-herdr/herdr](https://github.com/open-herdr/herdr) | herdr 终端 agent 多路复用器控制（手动更新） |
| `html-ppt` | [lewislulu/html-ppt-skill](https://github.com/lewislulu/html-ppt-skill) | HTML 演示文稿生成 |

### Skills - Shared（共享，项目按需链接）

| Skill | 来源 | 说明 |
|-------|------|------|
| `baoyu-xhs-images` | [baoyu-skills](https://github.com/JimLiu/baoyu-skills) | 小红书图片生成 |
| `douban-k-search` | self-developed | 豆瓣数据搜索 |
| `external-skills-updater` | self-developed | 更新外部 skill |
| `frontend-design` | [anthropics/skills](https://github.com/anthropics/skills) | 前端界面设计 |
| `images-k-generation` | self-developed | 图像生成 |
| `ob_architect_structure` | self-developed | 整理思路、构建逻辑骨架模板（前置条件 ≥3 张卡片，kk-brain） |
| `ob_capture_insight` | self-developed | 捕捉洞察、结晶知识卡片（含一句话核心观点 + 信息边界，kk-brain） |
| `ob_compile_manuscript` | self-developed | 整合内容、输出文章（含成稿模板 + 四层审计，kk-brain） |
| `ob_polish_prose` | self-developed | 扩写大纲、优化文字（含 author_voice 人格注入 + 四层风格审计，kk-brain） |
| `gzh-article-creator` | self-developed | 公众号文章创作工具 |
| `research-to-blueprint` | self-developed | 调研报告转视觉蓝图 |
| `xhs-k-search` | self-developed | 小红书数据搜索 |
| `zhihu-k-search` | self-developed | 知乎数据搜索 |
| `image-prompt` | self-developed | AI 图像生成提示词生成器，适用于任何模型 |
| `wechat-gzh-skill` | self-developed | 微信公众号草稿发布工具 |

### Agents - Common（OpenCode 通用，已链接到全局）

| Agent | 说明 |
|-------|------|
| `verification.md` | 验证 agent |
| `诸葛亮.md` | 人生导师、思维军师 agent |

### OpenCode Agents - Shared（OpenCode 共享，项目按需链接）

| Agent | 说明 |
|-------|------|
| `Knowledge Co-Creator.md` | 知识共建者主 agent（hkc 第一人称视角，含工作流阶段调度，kk-brain） |
| `ProductResearch.md` | 产品调研 subagent（专属 Skill 优先 → 简单页面 webfetch → 复杂页面 playwright-cli CDP） |
| `universal-translator.md` | 通用翻译 agent（多语言翻译成英语） |
| `WeChat-GZH-Operator.md` | 公众号运营主 agent（状态机管理、IMAGE_GEN 暂停生图、用户确认节点、验证检查点、image-prompt 提示词生成） |

## 使用方式

### 通用 Skill/Agent/Extension

通过目录级符号链接到全局，所有项目自动可用：

```bash
# 已完成的设置
ln -s ~/Code/kk-ai/skills/common ~/.config/opencode/skills
ln -s ~/Code/kk-ai/opencode-agents/common ~/.config/opencode/agents
ln -s ~/Code/kk-ai/pi-agents/common ~/.pi/agent/main-agents     # Pi 主 agent
ln -s ~/Code/kk-ai/pi-subagents/common ~/.pi/agent/agents       # Pi 子 agent（@agwab/pi-subagent）
ln -s ~/Code/kk-ai/pi-extensions/common ~/.pi/agent/extensions

# 查看
ls ~/.config/opencode/skills/
ls ~/.config/opencode/agents/
ls ~/.pi/agent/main-agents/
ls ~/.pi/agent/agents/
ls ~/.pi/agent/extensions/
```

### 全局代理规则

AGENTS.global.md 通过文件级符号链接同时服务于 OpenCode 和 Pi，为所有项目提供统一的代理行为规则：

```bash
# OpenCode
ln -sf ~/Code/kk-ai/AGENTS.global.md ~/.config/opencode/AGENTS.md

# Pi
ln -sf ~/Code/kk-ai/AGENTS.global.md ~/.pi/agent/AGENTS.md
```

### 共享 Skill/Agent

在需要的项目中链接：

```bash
# 链接 skill
cd /path/to/project
mkdir -p .opencode/skills
ln -s ~/Code/kk-ai/skills/shared/xxx-skill .opencode/skills/xxx-skill

# 链接 agent
mkdir -p .opencode/agents
ln -s ~/Code/kk-ai/opencode-agents/shared/xxx-agent.md .opencode/agents/xxx-agent.md

# 或使用脚本
~/Code/kk-ai/scripts/link-skills.sh shared xxx-skill /path/to/project
~/Code/kk-ai/scripts/link-skills.sh opencode-agent xxx-agent.md /path/to/project
~/Code/kk-ai/scripts/link-skills.sh pi-agent xxx-agent.md /path/to/project        # 主 agent → .pi/main-agents/
~/Code/kk-ai/scripts/link-skills.sh pi-subagent xxx-agent.md /path/to/project   # 子 agent → .pi/agents/（复制）
```

## 外部 Skill 更新

外部来源的 skill 通过 `external-skills-updater` skill 进行更新，详见资源清单中标记为外部来源的 skill。

更新方式：告诉 AI "请更新外部 skill"，AI 将自动执行更新流程。

### Pi Main Agents - Common（Pi 通用主 agent，已链接到 ~/.pi/agent/main-agents/）

| Agent | 说明 |
|-------|------|
| `诸葛亮.md` | 人生导师、思维军师，帮助分析复杂处境、认知突破、行动策略（供 pi-agent-switcher 切换） |

### Pi Main Agents - Shared（Pi 共享主 agent，项目按需链接到 .pi/main-agents/）

| Agent | OpenCode 源文件 | 说明 |
|-------|-----------------|------|
| `knowledge-co-creator.md` | `Knowledge Co-Creator.md` | 知识共建者，识别用户思维阶段并协助知识构建 |
| `universal-translator.md` | `universal-translator.md` | 多语言翻译专家，将非英语翻译成自然地道的英语 |
| `wechat-gzh-operator.md` | `WeChat-GZH-Operator.md` | 公众号运营 Agent，从选题到发布全流程管理 |

### Pi Subagents - Common（Pi 通用子 agent，已链接到 ~/.pi/agent/agents/）

| Agent | 说明 |
|-------|------|
| `verification.md` | 验证专家，尝试破坏实现、发现边缘情况和回归问题（被 @agwab/pi-subagent 委派） |

### Pi Subagents - Shared（Pi 共享子 agent，项目按需复制到 .pi/agents/）

| Agent | OpenCode 源文件 | 说明 |
|-------|-----------------|------|
| `product-research.md` | `ProductResearch.md` | 产品调研 Agent，多源调查并输出结构化调研报告 |

### Pi Extensions - Common（Pi 通用扩展，已链接到 ~/.pi/agent/extensions/）

| Extension | 来源 | 说明 |
|-----------|------|------|
| `baishan` | self-developed | 白山云 API 扩展 |
| `huawei-cloud` | self-developed | 华为云 API 扩展 |
| `pi-agent-switcher` | self-developed | Pi Agent 角色切换扩展 |

### Pi Agents 使用方式

Pi 区分两类 agent，读取不同目录：

- **主 agent** — 由 `pi-agent-switcher` 扩展管理，存 `~/.pi/agent/main-agents/`（仓库 `pi-agents/common/` 已链接）；启动时自动加载，`/agents` 查看、`/agent <name>` 切换
- **子 agent** — 被 `@agwab/pi-subagent` 委派，存 `~/.pi/agent/agents/`（仓库 `pi-subagents/common/` 已链接）

两类目录互不干扰。`common/` 已通过目录级符号链接全局生效，新增主/子 agent 文件放入对应 `common/` 即可。

项目级：

```bash
# 主 agent（软链接）
~/Code/kk-ai/scripts/link-skills.sh pi-agent xxx-agent.md /path/to/project   # → .pi/main-agents/

# 子 agent（复制；pi-subagent 拒绝项目符号链接）
~/Code/kk-ai/scripts/link-skills.sh pi-subagent xxx-agent.md /path/to/project  # → .pi/agents/
```

### Pi Extensions 使用方式

Pi 扩展是 TypeScript 模块，存放在 `pi-extensions/` 目录。`common/` 目录已通过目录级符号链接到 `~/.pi/agent/extensions/`，所有项目自动加载。

- **通用扩展**（`common/`）：放入即可全局生效，无需额外操作
- **共享扩展**（`shared/`）：按需链接到项目的 `.pi/extensions/` 目录

```bash
# 链接共享扩展到项目
~/Code/kk-ai/scripts/link-skills.sh pi-extension <extension-name> /path/to/project
```

## 相关目录

- **统一仓库**：`~/Code/kk-ai/`
- **上游追踪**：`~/Code/GitHub-Skills/`
- **全局配置（OpenCode）**：`~/.config/opencode/`
- **全局配置（Pi）**：`~/.pi/agent/main-agents/`（主）、`~/.pi/agent/agents/`（子）、`~/.pi/agent/extensions/`

## 相关文档

- [OpenCode Skills 官方文档](https://opencode.ai/docs/skills/)
- [OpenCode Agents 官方文档](https://opencode.ai/docs/agents/)
- [Pi Skills 文档](https://github.com/badlogic/pi-skills)
- [Agent Skills 标准](https://agentskills.io/specification)
