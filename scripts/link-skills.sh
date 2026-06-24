#!/bin/bash
# link-skills.sh
# 链接共享 skill/agent 到指定项目（同时支持 OpenCode 和 Pi）

set -e

SKILLS_ROOT="$HOME/Code/kk-ai"

link_shared_skill() {
  local skill_name=$1
  local project_path=$2
  
  if [ -z "$skill_name" ] || [ -z "$project_path" ]; then
    echo "用法: link-skills.sh shared <skill-name> <project-path>"
    exit 1
  fi
  
  skill_dir="$SKILLS_ROOT/skills/shared/$skill_name"
  
  if [ ! -d "$skill_dir" ]; then
    echo "❌ Skill 不存在: $skill_name"
    exit 1
  fi
  
  target="$project_path/.opencode/skills/$skill_name"
  
  mkdir -p "$project_path/.opencode/skills"
  
  if [ -e "$target" ] || [ -L "$target" ]; then
    rm -rf "$target"
  fi
  
  ln -s "$skill_dir" "$target"
  echo "✅ 已链接 skill $skill_name 到 $project_path"
}

link_opencode_agent() {
  local agent_name=$1
  local project_path=$2
  
  if [ -z "$agent_name" ] || [ -z "$project_path" ]; then
    echo "用法: link-skills.sh opencode-agent <agent-name> <project-path>"
    exit 1
  fi
  
  agent_file="$SKILLS_ROOT/opencode-agents/shared/$agent_name"
  
  if [ ! -f "$agent_file" ]; then
    echo "❌ OpenCode Agent 不存在: $agent_name"
    echo "   可用 Agent:"
    ls "$SKILLS_ROOT/opencode-agents/shared/" 2>/dev/null || echo "   (无)"
    exit 1
  fi
  
  target="$project_path/.opencode/agents/$agent_name"
  
  mkdir -p "$project_path/.opencode/agents"
  
  if [ -e "$target" ] || [ -L "$target" ]; then
    rm -rf "$target"
  fi
  
  ln -s "$agent_file" "$target"
  echo "✅ 已链接 OpenCode Agent $agent_name 到 $project_path"
}

link_pi_agent() {
  local agent_name=$1
  local project_path=$2
  
  if [ -z "$agent_name" ] || [ -z "$project_path" ]; then
    echo "用法: link-skills.sh pi-agent <agent-name> <project-path>"
    exit 1
  fi
  
  agent_file="$SKILLS_ROOT/pi-agents/shared/$agent_name"
  
  if [ ! -f "$agent_file" ]; then
    echo "❌ Pi Agent 不存在: $agent_name"
    echo "   可用 Agent:"
    ls "$SKILLS_ROOT/pi-agents/shared/" 2>/dev/null || echo "   (无)"
    exit 1
  fi
  
  target="$project_path/.pi/main-agents/$agent_name"
  
  mkdir -p "$project_path/.pi/main-agents"
  
  if [ -e "$target" ] || [ -L "$target" ]; then
    rm -rf "$target"
  fi
  
  ln -s "$agent_file" "$target"
  echo "✅ 已链接 Pi Agent $agent_name 到 $project_path"
}

link_pi_subagent() {
  local agent_name=$1
  local project_path=$2
  
  if [ -z "$agent_name" ] || [ -z "$project_path" ]; then
    echo "用法: link-skills.sh pi-subagent <agent-name> <project-path>"
    exit 1
  fi
  
  agent_file="$SKILLS_ROOT/pi-subagents/shared/$agent_name"
  
  if [ ! -f "$agent_file" ]; then
    echo "❌ Pi Subagent 不存在: $agent_name"
    echo "   可用 Subagent:"
    ls "$SKILLS_ROOT/pi-subagents/shared/" 2>/dev/null || echo "   (无)"
    exit 1
  fi
  
  target_dir="$project_path/.pi/agents"
  target="$target_dir/$agent_name"
  
  mkdir -p "$target_dir"
  
  # pi-subagent rejects project-scope file symlinks whose realpath escapes the
  # project .pi/agents root ("agent symlink escapes root"). Therefore shared
  # subagents must be COPIED into the project, not symlinked.
  rm -f "$target"
  cp "$agent_file" "$target"
  echo "✅ 已复制 Pi Subagent $agent_name 到 $project_path/.pi/agents/"
}

link_pi_extension() {
  local extension_name=$1
  local project_path=$2
  
  if [ -z "$extension_name" ] || [ -z "$project_path" ]; then
    echo "用法: link-skills.sh pi-extension <extension-name> <project-path>"
    exit 1
  fi
  
  extension_src="$SKILLS_ROOT/pi-extensions/shared/$extension_name"
  
  if [ ! -e "$extension_src" ]; then
    echo "❌ Pi Extension 不存在: $extension_name"
    echo "   可用 Extension:"
    ls "$SKILLS_ROOT/pi-extensions/shared/" 2>/dev/null || echo "   (无)"
    exit 1
  fi
  
  target="$project_path/.pi/extensions/$extension_name"
  
  mkdir -p "$project_path/.pi/extensions"
  
  if [ -e "$target" ] || [ -L "$target" ]; then
    rm -rf "$target"
  fi
  
  ln -s "$extension_src" "$target"
  echo "✅ 已链接 Pi Extension $extension_name 到 $project_path"
}

case "$1" in
  shared)
    link_shared_skill "$2" "$3"
    ;;
  opencode-agent)
    link_opencode_agent "$2" "$3"
    ;;
  pi-agent)
    link_pi_agent "$2" "$3"
    ;;
  pi-subagent)
    link_pi_subagent "$2" "$3"
    ;;
  pi-extension)
    link_pi_extension "$2" "$3"
    ;;
  *)
    echo "用法:"
    echo "  $0 shared <skill> <project>            # 链接共享 skill 到 OpenCode 项目"
    echo "  $0 opencode-agent <agent> <project>    # 链接 OpenCode Agent 到 OpenCode 项目"
    echo "  $0 pi-agent <agent> <project>          # 链接 Pi 主 Agent 到 Pi 项目"
    echo "  $0 pi-subagent <agent> <project>       # 复制 Pi 子 Agent 到 Pi 项目 (.pi/agents/)"
    echo "  $0 pi-extension <extension> <project>  # 链接 Pi Extension 到 Pi 项目"
    ;;
esac
