# OpenCode / Pi Skills & Agents 统一管理仓库

统一管理 OpenCode 和 Pi 的 Skills、Agents 及全局规则资源。

## 目录结构

```
opencode-skills/
├── skills/
│   ├── common/          # 通用工具类 skill（ln 到全局）
│   └── shared/          # 共享 skill（项目按需 ln）
├── agents/
│   ├── common/          # 通用 agent（ln 到全局）
│   └── shared/          # 共享 agent（项目按需 ln）
├── scripts/             # 辅助脚本
├── AGENTS.global.md     # 全局代理规则（ln OpenCode + Pi 双 harness）
├── AGENTS.md            # 本仓库开发指南
└── README.md
```

## 资源清单

### Skills - Common（通用，已链接到全局）

| Skill | 来源 | 说明 |
|-------|------|------|
| `drawio` | [drawio-mcp](https://github.com/jgraph/drawio-mcp) | 图表绘制 |
| `markdown-to-image` | self-developed | Markdown/代码片段转图片 |
| `project-init` | self-developed | 项目初始化工具（OpenCode / Pi 双支持） |
| `playwright-cli` | [Playwright](https://www.npmjs.com/package/@playwright/cli) | 浏览器自动化交互工具（手动更新） |
| `skill-creator` | [anthropics/skills](https://github.com/anthropics/skills) | 创建新 skill |
| `skillify` | self-developed | 将会话过程捕获为 skill |
| `html-ppt` | [lewislulu/html-ppt-skill](https://github.com/lewislulu/html-ppt-skill) | HTML 演示文稿生成 |

### Skills - Shared（共享，项目按需链接）

| Skill | 来源 | 说明 |
|-------|------|------|
| `baoyu-xhs-images` | [baoyu-skills](https://github.com/JimLiu/baoyu-skills) | 小红书图片生成 |
| `douban-k-search` | self-developed | 豆瓣数据搜索 |
| `external-skills-updater` | self-developed | 更新外部 skill |
| `frontend-design` | [anthropics/skills](https://github.com/anthropics/skills) | 前端界面设计 |
| `images-k-generation` | self-developed | 图像生成 |
| `ob_architect_structure` | self-developed | 整理思路、构建大纲（kk-brain） |
| `ob_capture_insight` | self-developed | 捕捉洞察、结晶知识卡片（kk-brain） |
| `ob_compile_manuscript` | self-developed | 整合内容、输出文章（kk-brain） |
| `ob_polish_prose` | self-developed | 扩写大纲、优化文字（kk-brain） |
| `gzh-article-creator` | self-developed | 公众号文章创作工具 |
| `research-to-blueprint` | self-developed | 调研报告转视觉蓝图 |
| `xhs-k-search` | self-developed | 小红书数据搜索 |
| `zhihu-k-search` | self-developed | 知乎数据搜索 |
| `image-prompt` | self-developed | AI 图像生成提示词生成器，适用于任何模型 |
| `wechat-gzh-skill` | self-developed | 微信公众号草稿发布工具 |

### Agents - Common（通用，已链接到全局）

| Agent | 说明 |
|-------|------|
| `verification.md` | 验证 agent |
| `诸葛亮.md` | 人生导师、思维军师 agent |

### Agents - Shared（共享，项目按需链接）

| Agent | 说明 |
|-------|------|
| `Knowledge Co-Creator.md` | 知识共建者主 agent（kk-brain） |
| `ProductResearch.md` | 产品调研 subagent（专属 Skill 优先 → 简单页面 webfetch → 复杂页面 playwright-cli CDP） |
| `universal-translator.md` | 通用翻译 agent（多语言翻译成英语） |
| `WeChat-GZH-Operator.md` | 公众号运营主 agent（状态机管理、IMAGE_GEN 暂停生图、用户确认节点、验证检查点、drawio 架构图、image-prompt 提示词生成） |

## 使用方式

### 通用 Skill/Agent

通过目录级符号链接到全局，所有项目自动可用：

```bash
# 已完成的设置
ln -s ~/Code/opencode-skills/skills/common ~/.config/opencode/skills
ln -s ~/Code/opencode-skills/agents/common ~/.config/opencode/agents

# 查看
ls ~/.config/opencode/skills/
ls ~/.config/opencode/agents/
```

### 全局代理规则

AGENTS.global.md 通过文件级符号链接同时服务于 OpenCode 和 Pi，为所有项目提供统一的代理行为规则：

```bash
# OpenCode
ln -sf ~/Code/opencode-skills/AGENTS.global.md ~/.config/opencode/AGENTS.md

# Pi
ln -sf ~/Code/opencode-skills/AGENTS.global.md ~/.pi/agent/AGENTS.md
```

### 共享 Skill/Agent

在需要的项目中链接：

```bash
# 链接 skill
cd /path/to/project
mkdir -p .opencode/skills
ln -s ~/Code/opencode-skills/skills/shared/xxx-skill .opencode/skills/xxx-skill

# 链接 agent
mkdir -p .opencode/agents
ln -s ~/Code/opencode-skills/agents/shared/xxx-agent.md .opencode/agents/xxx-agent.md

# 或使用脚本
~/Code/opencode-skills/scripts/link-skills.sh shared xxx-skill /path/to/project
```

## 外部 Skill 更新

外部来源的 skill 通过 `external-skills-updater` skill 进行更新，详见资源清单中标记为外部来源的 skill。

更新方式：告诉 AI "请更新外部 skill"，AI 将自动执行更新流程。

## 相关目录

- **统一仓库**：`~/Code/opencode-skills/`
- **上游追踪**：`~/Code/GitHub-Skills/`
- **全局配置（OpenCode）**：`~/.config/opencode/`
- **全局配置（Pi）**：`~/.pi/agent/`

## 相关文档

- [OpenCode Skills 官方文档](https://opencode.ai/docs/skills/)
- [OpenCode Agents 官方文档](https://opencode.ai/docs/agents/)
- [Pi Skills 文档](https://github.com/badlogic/pi-skills)
- [Agent Skills 标准](https://agentskills.io/specification)
