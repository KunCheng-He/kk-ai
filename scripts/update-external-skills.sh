#!/bin/bash
# update-external-skills.sh
# 更新所有外部 skill

set -e

SKILLS_ROOT="$HOME/Code/kk-ai"

echo "🔍 查找所有外部 skill..."

# 查找所有包含 upstream.json 的 skill
find "$SKILLS_ROOT/skills" -name "upstream.json" | while read upstream_file; do
  skill_dir=$(dirname "$upstream_file")
  skill_name=$(basename "$skill_dir")
  
  # 读取上游信息
  source_url=$(jq -r '.source' "$upstream_file")
  source_path=$(jq -r '.path' "$upstream_file")
  tracking_dir=$(jq -r '.tracking_dir' "$upstream_file")
  update_method=$(jq -r '.update_method // "auto"' "$upstream_file")
  
  # 跳过手动更新的 skill
  if [ "$update_method" = "manual" ]; then
    echo "⏭️  跳过 $skill_name (手动更新)"
    continue
  fi
  
  # 跳过来源未知的 skill
  if [ "$source_url" = "unknown" ] || [ -z "$tracking_dir" ]; then
    echo "⏭️  跳过 $skill_name (来源未知)"
    continue
  fi
  
  # 展开路径中的 ~
  tracking_dir_expanded="${tracking_dir/#\~/$HOME}"
  
  echo ""
  echo "📦 更新 $skill_name..."
  echo "   来源: $source_url"
  echo "   追踪目录: $tracking_dir"
  
  # 检查追踪目录是否存在
  if [ ! -d "$tracking_dir_expanded" ]; then
    echo "   ⚠️  追踪目录不存在，跳过"
    continue
  fi
  
  # 更新上游仓库
  cd "$tracking_dir_expanded"
  git pull
  
  # 拷贝更新
  if [ -d "$source_path" ]; then
    cp -r "$source_path"/* "$skill_dir/"
  else
    echo "   ⚠️  源路径不存在: $source_path"
    continue
  fi
  
  # 更新时间戳
  jq --arg date "$(date +%Y-%m-%d)" '.last_update = $date' \
    "$upstream_file" > "$upstream_file.tmp"
  mv "$upstream_file.tmp" "$upstream_file"
  
  echo "   ✅ 已更新 $skill_name"
done

echo ""
echo "📝 提交更新到统一仓库..."
cd "$SKILLS_ROOT"
git add skills/
git status

echo ""
echo "✅ 更新完成！请检查变更并手动提交。"
