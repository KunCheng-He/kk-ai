# OpenCode Skills & Agents 统一管理仓库

统一管理所有 OpenCode 的 Skills 和 Agents 资源。

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
└── README.md
```

## 使用方式

### 通用 Skill/Agent

链接到全局目录，所有项目自动可用：

```bash
# Skill
ln -s ~/Code/opencode-skills/skills/common/xxx-skill ~/.config/opencode/skills/xxx-skill

# Agent
ln -s ~/Code/opencode-skills/agents/common/xxx-agent.md ~/.config/opencode/agents/xxx-agent.md
```

### 共享 Skill/Agent

在需要的项目中链接：

```bash
cd /path/to/project
mkdir -p .opencode/skills
ln -s ~/Code/opencode-skills/skills/shared/xxx-skill .opencode/skills/xxx-skill
```

## 外部 Skill 更新

外部来源的 skill 包含 `upstream.json` 文件，记录上游信息：

```json
{
  "source": "https://github.com/xxx/some-repo.git",
  "path": "skills/xxx-skill",
  "last_update": "2026-04-17",
  "tracking_dir": "~/Code/GitHub-Skills/common/some-repo"
}
```

更新方式：

```bash
# 手动更新
./scripts/update-external-skills.sh

# 或告诉 AI
# "请帮我更新 xxx-skill"
```

## 相关文档

- [OpenCode Skills 官方文档](https://opencode.ai/docs/skills/)
- [OpenCode Agents 官方文档](https://opencode.ai/docs/agents/)
