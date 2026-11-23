---
name: external-skills-updater
description: 更新外部开发的 skill。当用户要求更新外部 skill、同步上游 skill、或提到"更新 skill"、"同步 skill"、"pull skill"时使用此技能。
---

# External Skills Updater

## 概述

更新本仓库中来自外部 GitHub 仓库的 skill。

## 更新流程

### 1. 拉取上游更新

在 `~/Code/GitHub-Skills/` 目录下对各追踪仓库执行 `git pull`。

### 2. 运行更新脚本

```bash
~/Code/kk-ai/scripts/update-external-skills.sh
```

脚本会自动：
- 扫描所有包含 `upstream.json` 的 skill
- 从追踪目录同步文件到本仓库
- 更新 `last_update` 时间戳

### 3. 检查并提交

```bash
cd ~/Code/kk-ai
git status
git diff
```

## upstream.json 格式

### 自动更新（外部 GitHub 仓库追踪）

```json
{
  "source": "https://github.com/xxx/repo.git",
  "path": "skills/xxx-skill",
  "last_update": "2026-04-28",
  "tracking_dir": "~/Code/GitHub-Skills/common/xxx"
}
```

### 手动更新

对于通过 npm、pip 等包管理器安装的 skill，设置 `"update_method": "manual"` 以跳过自动更新：

```json
{
  "source": "npm",
  "update_method": "manual",
  "install_command": "npm install -g @xxx/cli@latest",
  "last_update": "2026-05-28"
}
```

