#!/bin/bash
# link-skills.sh
# 链接共享 skill 到指定项目

set -e

SKILLS_ROOT="$HOME/Code/opencode-skills"

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

case "$1" in
  shared)
    link_shared_skill "$2" "$3"
    ;;
  *)
    echo "用法:"
    echo "  $0 shared <skill> <project>  # 链接共享 skill 到指定项目"
    ;;
esac
