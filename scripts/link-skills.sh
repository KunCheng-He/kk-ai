#!/bin/bash
# link-skills.sh
# 创建 skill/agent 的 symlink

set -e

SKILLS_ROOT="$HOME/Code/opencode-skills"
GLOBAL_SKILLS="$HOME/.config/opencode/skills"
GLOBAL_AGENTS="$HOME/.config/opencode/agents"

link_common_skills() {
  echo "🔗 链接通用 skills 到全局目录..."
  
  for skill_dir in "$SKILLS_ROOT/skills/common"/*/; do
    if [ -d "$skill_dir" ]; then
      skill_name=$(basename "$skill_dir")
      target="$GLOBAL_SKILLS/$skill_name"
      
      # 如果已存在，先删除
      if [ -e "$target" ] || [ -L "$target" ]; then
        rm -rf "$target"
      fi
      
      ln -s "$skill_dir" "$target"
      echo "   ✅ $skill_name"
    fi
  done
}

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
  echo "✅ 已链接 $skill_name 到 $project_path"
}

link_common_agents() {
  echo "🔗 链接通用 agents 到全局目录..."
  
  for agent_file in "$SKILLS_ROOT/agents/common"/*.md; do
    if [ -f "$agent_file" ]; then
      agent_name=$(basename "$agent_file")
      target="$GLOBAL_AGENTS/$agent_name"
      
      if [ -e "$target" ] || [ -L "$target" ]; then
        rm -rf "$target"
      fi
      
      ln -s "$agent_file" "$target"
      echo "   ✅ $agent_name"
    fi
  done
}

case "$1" in
  common)
    link_common_skills
    link_common_agents
    ;;
  shared)
    link_shared_skill "$2" "$3"
    ;;
  *)
    echo "用法:"
    echo "  $0 common              # 链接所有通用 skills/agents 到全局"
    echo "  $0 shared <skill> <project>  # 链接共享 skill 到指定项目"
    ;;
esac
