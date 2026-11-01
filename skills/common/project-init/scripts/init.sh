#!/usr/bin/env bash
# project-init.sh — 多 harness 项目初始化驱动脚本
#
# 用法：
#   ./init.sh init  <项目路径> --harness dsh,opencode --skill a,b --agent x.md --type python
#   ./init.sh plan  <项目路径> --harness all --skill research-workflow   # 只打印，不落盘
#   ./init.sh list                                                        # 列出 harness / skill / agent
#
# 设计原则：
#   1. harness 约定集中在本文件的 harness_spec() 中，新增 harness 只改一处
#   2. 幂等：已存在的链接默认跳过，--force 才重建
#   3. 链接用绝对路径符号链接，便于统一更新
#   4. 指令文件中的清单写入受管区块（<!-- project-init:begin/end -->），可重复执行

set -euo pipefail

# macOS 自带 bash 3.2 + awk/sed 需要 UTF-8 locale 才能正确按字符切分中文
if [ -z "${LC_ALL:-}" ] && [ -z "${LANG:-}" ]; then
  export LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
DFT_REPO_ROOT="$(cd "$SKILL_DIR/../../.." && pwd)"
REPO_ROOT="${KK_AI_ROOT:-$DFT_REPO_ROOT}"

BLOCK_BEGIN='<!-- project-init:begin 由 project-init 生成，请勿手动编辑本区块 -->'
BLOCK_END='<!-- project-init:end -->'

# ---------------------------------------------------------------- 输出
ok()   { printf '  ✅ %s\n' "$*"; }
info() { printf '  ·  %s\n' "$*"; }
warn() { printf '  ⚠️  %s\n' "$*" >&2; }
err()  { printf '  ❌ %s\n' "$*" >&2; }
hdr()  { printf '\n%s\n' "$*"; }

usage() {
  cat <<'EOF'
用法：
  init.sh init <项目路径> [选项]     创建多 harness 项目配置
  init.sh plan <项目路径> [选项]     同 init，但不写任何文件（dry-run）
  init.sh list [harness|skill|agent] 列出内置清单

选项：
  --harness <列表>   目标 harness，逗号/空格分隔，或 all
                     可用：dsh opencode claude-code codex gemini-cli cursor generic
                     默认：自动探测（当前会话的 harness）
  --skill <列表>     要链接的 skill（skills/shared，缺失时回退 skills/common）
  --agent <列表>     要链接的 agent（opencode-agents/shared），.md 可省略
  --type <类型>      .gitignore 模板：node|python|go|rust|java|universal（默认 universal）
  --repo-root <路径> kk-ai 仓库根（默认自动推断）
  --no-git           跳过 git init / commit
  --no-commit        只 git init，不创建初始提交
  --force            已存在的链接重建为目标路径
  --dry-run          等价于 plan
  -h, --help         帮助

示例：
  # 在 DSH 与 OpenCode 双开的新项目里挂载调研工作流
  init.sh init ~/Code/my-project --harness dsh,opencode \
      --skill research-workflow --agent ResearchReporter --type python

  # 只给 DSH 用，并先预览
  init.sh plan ~/Code/demo --harness dsh --skill mermaid
EOF
}

# ---------------------------------------------------------------- harness 注册表
# 改动这里 = 支持新 harness；references/harnesses.md 需同步文档
harness_spec() {
  H_SKILLS=""        # 项目级 skill 目录
  H_AGENTS=""        # 项目级 agent 目录（空=不支持文件式 agent）
  H_DOC=""           # 指令文件
  H_DOC_TITLE=""     # 指令文件写区块时的标题前缀
  case "$1" in
    dsh)
      H_SKILLS=".dsh/skills"; H_AGENTS=""; H_DOC="AGENTS.md" ;;
    opencode)
      H_SKILLS=".opencode/skills"; H_AGENTS=".opencode/agents"; H_DOC="AGENTS.md" ;;
    claude-code)
      H_SKILLS=".claude/skills"; H_AGENTS=".claude/agents"; H_DOC="CLAUDE.md" ;;
    codex)
      H_SKILLS=".agents/skills"; H_AGENTS=""; H_DOC="AGENTS.md" ;;
    gemini-cli)
      H_SKILLS=".agents/skills"; H_AGENTS=""; H_DOC="GEMINI.md" ;;
    cursor)
      H_SKILLS=".agents/skills"; H_AGENTS=""; H_DOC=".cursor/rules/project-init.mdc" ;;
    generic)
      H_SKILLS=".agents/skills"; H_AGENTS=""; H_DOC="AGENTS.md" ;;
    *) return 1 ;;
  esac
  return 0
}

ALL_HARNESSES="dsh opencode claude-code codex gemini-cli cursor generic"

harness_desc() {
  case "$1" in
    dsh)         echo "DeepSeek Harness（.dsh/skills + AGENTS.md，无文件式 agent）" ;;
    opencode)    echo "OpenCode（.opencode/skills + .opencode/agents + AGENTS.md）" ;;
    claude-code) echo "Claude Code（.claude/skills + .claude/agents + CLAUDE.md）" ;;
    codex)       echo "Codex CLI（AGENTS.md；skill 走 .agents/skills 便携目录）" ;;
    gemini-cli)  echo "Gemini CLI（GEMINI.md；skill 走 .agents/skills 便携目录）" ;;
    cursor)      echo "Cursor（.cursor/rules + AGENTS.md；skill 走 .agents/skills）" ;;
    generic)     echo "通用/未知 harness（.agents/skills + AGENTS.md）" ;;
    *) return 1 ;;
  esac
}

detect_harness() {
  if [ -n "${DSH_SESSION_ID:-}${DSH_HOME:-}" ]; then echo dsh; return 0; fi
  if [ -n "${CLAUDECODE:-}${CLAUDE_CODE_ENTRYPOINT:-}" ]; then echo claude-code; return 0; fi
  case "${OPENCODE:-}" in ""|0) ;; *) echo opencode; return 0 ;; esac
  if [ -n "${GEMINI_CLI:-}${GEMINI_SESSION_ID:-}" ]; then echo gemini-cli; return 0; fi
  if [ -d "$PWD/.opencode" ]; then echo opencode; return 0; fi
  if [ -d "$PWD/.claude" ]; then echo claude-code; return 0; fi
  if [ -d "$PWD/.dsh" ]; then echo dsh; return 0; fi
  echo generic
}

# ---------------------------------------------------------------- 资源解析
# 输出 skill 源目录（shared 优先，回退 common）；找不到则空
skill_src() {
  local name="$1"
  if [ -d "$REPO_ROOT/skills/shared/$name" ]; then
    echo "$REPO_ROOT/skills/shared/$name"
  elif [ -d "$REPO_ROOT/skills/common/$name" ]; then
    echo "$REPO_ROOT/skills/common/$name"
  else
    echo ""
  fi
}

skill_origin() {
  if [ -d "$REPO_ROOT/skills/shared/$1" ]; then
    echo "shared"
  elif [ -d "$REPO_ROOT/skills/common/$1" ]; then
    echo "common"
  else
    echo ""
  fi
}

# SKILL.md front-matter 的 description，压成一行（不截断，避免切坏中文）
skill_desc() {
  local dir="$1" f d
  f="$dir/SKILL.md"
  if [ ! -f "$f" ]; then echo ""; return 0; fi
  d="$(awk '
    /^description:[[:space:]]*\|/ { multi=1; next }
    /^description:/ {
      sub(/^description:[[:space:]]*/, "")
      print; exit
    }
    multi && /^[[:space:]]+[^[:space:]]/ {
      sub(/^[[:space:]]+/, ""); buf = (buf == "" ? $0 : buf " " $0); next
    }
    multi && /^[[:space:]]*$/ { next }
    multi { print buf; exit }
    END { if (multi && buf != "") print buf }
  ' "$f" 2>/dev/null | head -1)"
  d="$(printf '%s' "$d" | sed -e 's/[[:space:]]\+/ /g' -e 's/^ //' -e 's/ $//')"
  [ -z "$d" ] && d="（无描述）"
  printf '%s' "$d"
}

agent_src() {
  local name="$1" base="${1%.md}"
  if [ -f "$REPO_ROOT/opencode-agents/shared/$base.md" ]; then
    echo "$REPO_ROOT/opencode-agents/shared/$base.md"
  else
    echo ""
  fi
}

agent_desc() {
  local f="$1" d
  [ -f "$f" ] || { echo ""; return 0; }
  d="$(grep -m1 '^description:' "$f" 2>/dev/null | sed -e 's/^description:[[:space:]]*//' || true)"
  [ -z "$d" ] && d="（无描述）"
  printf '%s' "$d"
}

list_all() {
  local what="${1:-all}" h s a
  if [ "$what" = "all" ] || [ "$what" = "harness" ]; then
    hdr "Harnesses（kk-ai 仓库：${REPO_ROOT}）"
    for h in $ALL_HARNESSES; do
      harness_spec "$h"
      printf '  %-12s %s\n' "$h" "$(harness_desc "$h")"
      printf '  %-12s   skills=%s  agents=%s  instructions=%s\n' "" \
        "${H_SKILLS:--}" "${H_AGENTS:--}" "${H_DOC:--}"
    done
  fi
  if [ "$what" = "all" ] || [ "$what" = "skill" ]; then
    hdr "Skills - shared（项目按需链接）"
    for s in "$REPO_ROOT"/skills/shared/*/; do
      [ -d "$s" ] || continue
      s="$(basename "$s")"
      printf '  %-26s %s\n' "$s" "$(skill_desc "$REPO_ROOT/skills/shared/$s")"
    done
    hdr "Skills - common（已全局生效，一般无需链接）"
    for s in "$REPO_ROOT"/skills/common/*/; do
      [ -d "$s" ] || continue
      s="$(basename "$s")"
      printf '  %-26s %s\n' "$s" "$(skill_desc "$REPO_ROOT/skills/common/$s")"
    done
  fi
  if [ "$what" = "all" ] || [ "$what" = "agent" ]; then
    hdr "Agents - shared（OpenCode 格式，仅 opencode/claude-code 可链接）"
    for a in "$REPO_ROOT"/opencode-agents/shared/*.md; do
      [ -f "$a" ] || continue
      printf '  %-26s %s\n' "$(basename "$a")" "$(agent_desc "$a")"
    done
  fi
}

# ---------------------------------------------------------------- 工具函数
run() {
  if [ "$DRY_RUN" -eq 1 ]; then printf '  [plan] %s\n' "$*"; else "$@"; fi
}

uniq_words() { echo "$*" | tr ' ' '\n' | awk 'NF && !seen[$0]++' | tr '\n' ' ' | sed 's/ $//'; }

in_list() { case " $2 " in *" $1 "*) return 0;; esac; return 1; }

link_path() {
  local src="$1" dst="$2"
  if [ -L "$dst" ]; then
    if [ "$(readlink "$dst")" = "$src" ]; then
      info "已就绪：$(basename "$dst") → $src"
      return 0
    fi
    if [ "$FORCE" -eq 1 ]; then
      run rm -f "$dst"
    else
      warn "已存在不同链接，跳过（--force 可覆盖）：$dst"
      return 1
    fi
  elif [ -e "$dst" ]; then
    warn "已存在真实文件/目录，跳过（不动用户内容）：$dst"
    return 1
  fi
  run ln -s "$src" "$dst"
  if [ "$DRY_RUN" -eq 0 ]; then
    if [ -e "$dst" ]; then ok "链接 $(basename "$dst") → $src"
    else err "链接失败（源不存在？）：$src"; return 1; fi
  fi
  return 0
}

# 受管区块写入/替换
write_block() {
  local file="$1" block="$2"
  if [ "$DRY_RUN" -eq 1 ]; then
    printf '  [plan] 写入受管区块 %s（%s 行）\n' "$file" "$(wc -l < "$block" | tr -d ' ')"
    return 0
  fi
  mkdir -p "$(dirname "$file")"
  if [ ! -f "$file" ]; then
    case "$file" in
      *.mdc) { printf -- '---\ndescription: 项目规则（project-init 生成）\nglobs: **/*\nalwaysApply: true\n---\n\n'; cat "$block"; } > "$file" ;;
      *)     cat "$block" > "$file" ;;
    esac
    ok "创建指令文件 $file"
    return 0
  fi
  if grep -q 'project-init:begin' "$file" 2>/dev/null; then
    awk -v bf="$block" '
      /project-init:begin/ { inblk=1; while ((getline line < bf) > 0) print line; close(bf); next }
      /project-init:end/   { inblk=0; next }
      inblk != 1           { print }
    ' "$file" > "$file.pi.tmp" && mv "$file.pi.tmp" "$file"
    ok "刷新指令文件受管区块 $file"
  else
    { printf '\n'; cat "$block"; } >> "$file"
    ok "追加受管区块到 $file"
  fi
}

# 从 stdin 读取逐行规则，去重后追加
append_gitignore() {
  local proj="$1"
  local gi="$proj/.gitignore" line n=0
  if [ "$DRY_RUN" -eq 1 ]; then
    while IFS= read -r line; do [ -n "$line" ] && printf '  [plan] .gitignore += %s\n' "$line"; done
    return 0
  fi
  touch "$gi"
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    grep -qxF -- "$line" "$gi" 2>/dev/null || { printf '%s\n' "$line" >> "$gi"; n=$((n+1)); }
  done
  ok ".gitignore 已更新（新增 ${n} 条）"
}

gitignore_lines() {
  local type="$1"
  printf '%s\n' "# project-init: harness 链接目录（机器本地，不入库）"
  case "$type" in
    node)      printf '%s\n' "node_modules/" "dist/" ".env" "*.log" ;;
    python)    printf '%s\n' "__pycache__/" "*.pyc" ".venv/" ".env" ;;
    go)        printf '%s\n' "*.exe" "*.test" "vendor/" ;;
    rust)      printf '%s\n' "target/" ;;
    java)      printf '%s\n' "*.class" "*.jar" "target/" ;;
    universal|*) : ;;
  esac
  printf '%s\n' ".DS_Store" ".idea/" ".vscode/"
}

# ---------------------------------------------------------------- 主流程
CMD="init"; DRY_RUN=0; DRY_RUN_SUFFIX=""; FORCE=0; DO_GIT=1; DO_COMMIT=1; PROJ_TYPE="universal"; PROJECT=""
HARNESSES=""; SKILLS=""; AGENTS=""

while [ $# -gt 0 ]; do
  case "$1" in
    init|plan)      CMD="$1"; [ "$1" = plan ] && DRY_RUN=1; shift ;;
    list)           CMD="list"; shift ;;
    --harness)      HARNESSES="$HARNESSES $(echo "${2:-}" | tr ',' ' ')"; shift 2 ;;
    --skill)        SKILLS="$SKILLS $(echo "${2:-}" | tr ',' ' ')"; shift 2 ;;
    --agent)        AGENTS="$AGENTS $(echo "${2:-}" | tr ',' ' ')"; shift 2 ;;
    --type)         PROJ_TYPE="${2:-universal}"; shift 2 ;;
    --repo-root)    REPO_ROOT="${2:?}"; shift 2 ;;
    --no-git)       DO_GIT=0; shift ;;
    --no-commit)    DO_COMMIT=0; shift ;;
    --force)        FORCE=1; shift ;;
    --dry-run)      DRY_RUN=1; shift ;;
    -h|--help)      usage; exit 0 ;;
    -*)             err "未知参数：$1"; usage; exit 2 ;;
    *)              PROJECT="$1"; shift ;;
  esac
done

if [ "$CMD" = "list" ]; then list_all "${PROJECT:-all}"; exit 0; fi
[ "$DRY_RUN" -eq 1 ] && DRY_RUN_SUFFIX=", 仅预览"
[ -n "$PROJECT" ] || { err "缺少项目路径"; usage; exit 2; }

# 解析项目路径（允许尚不存在）
case "$PROJECT" in
  "~")   PROJECT="$HOME" ;;
  "~/"*) PROJECT="$HOME/${PROJECT#\~/}" ;;
esac
if [ -d "$PROJECT" ]; then
  PROJECT="$(cd "$PROJECT" && pwd)"
else
  case "$PROJECT" in /*) : ;; *) PROJECT="$PWD/$PROJECT" ;; esac
fi
PROJECT_NAME="$(basename "$PROJECT")"

# 归一化 harness 列表
HARNESSES="$(uniq_words "${HARNESSES:-}")"
if [ -z "$HARNESSES" ]; then
  HARNESSES="$(detect_harness)"
  info "未指定 harness，自动探测为：$HARNESSES"
fi
if in_list "all" "$HARNESSES"; then
  HARNESSES="$(uniq_words "$ALL_HARNESSES")"
  info "--harness all：$HARNESSES"
fi
for h in $HARNESSES; do
  harness_spec "$h" || { err "未知 harness：${h}（可用：${ALL_HARNESSES}）"; exit 2; }
done

SKILLS="$(uniq_words "${SKILLS:-}")"
AGENTS="$(uniq_words "${AGENTS:-}")"

hdr "📋 初始化计划（${CMD}${DRY_RUN_SUFFIX}）"
info "项目路径：$PROJECT"
info "harness ：$HARNESSES"
[ -n "$SKILLS" ] && info "skills  ：$SKILLS"
[ -n "$AGENTS" ] && info "agents  ：$AGENTS"
info "gitignore 类型：$PROJ_TYPE"

# 0) 预检：资源不存在就不要留下半成品目录
if [ -n "$SKILLS" ] || [ -n "$AGENTS" ]; then
  missing=0
  for s in $SKILLS; do
    if [ -z "$(skill_src "$s")" ]; then
      err "skill 不存在：${s}（查 ${REPO_ROOT}/skills/{shared,common}/）"; missing=1
    fi
  done
  for a in $AGENTS; do
    if [ -z "$(agent_src "$a")" ]; then
      err "agent 不存在：${a}（查 ${REPO_ROOT}/opencode-agents/shared/）"; missing=1
    fi
  done
  if [ "$missing" -eq 1 ]; then
    err "预检失败：未创建任何文件。用 list 子命令查看可用资源"
    exit 3
  fi
fi

# 1) 目录
hdr "1. 创建目录结构"
[ "$DRY_RUN" -eq 0 ] && mkdir -p "$PROJECT"
dirs=""
for h in $HARNESSES; do
  harness_spec "$h"
  [ -n "$H_SKILLS" ] && dirs="$dirs $H_SKILLS"
  [ -n "$H_AGENTS" ] && dirs="$dirs $H_AGENTS"
done
for d in $(uniq_words "$dirs"); do
  case "$d" in
    .agents/skills) [ -d "$PROJECT/.agents/skills" ] && continue ;;
  esac
  run mkdir -p "$PROJECT/$d"; [ "$DRY_RUN" -eq 0 ] && ok "mkdir -p $d"
done

# 2) skills
LINKED_SKILLS=""
if [ -n "$SKILLS" ]; then
  hdr "2. 链接 skills"
  for s in $SKILLS; do
    src="$(skill_src "$s")"
    if [ -z "$src" ]; then
      err "skill 不存在：${s}（查 ${REPO_ROOT}/skills/{shared,common}/）"; exit 3
    fi
    origin="$(skill_origin "$s")"
    linked=0
    for h in $HARNESSES; do
      harness_spec "$h"
      [ -z "$H_SKILLS" ] && continue
      link_path "$src" "$PROJECT/$H_SKILLS/$s" && linked=1
    done
    [ "$linked" -eq 1 ] && LINKED_SKILLS="$LINKED_SKILLS $s"
    info "${s}（来源 ${origin}）"
  done
fi

# 3) agents
LINKED_AGENTS=""
if [ -n "$AGENTS" ]; then
  hdr "3. 链接 agents"
  for a in $AGENTS; do
    src="$(agent_src "$a")"
    base="$(basename "${a%.md}").md"
    if [ -z "$src" ]; then
      err "agent 不存在：${a}（查 ${REPO_ROOT}/opencode-agents/shared/）"; exit 3
    fi
    linked=0
    for h in $HARNESSES; do
      harness_spec "$h"
      if [ -z "$H_AGENTS" ]; then continue; fi
      link_path "$src" "$PROJECT/$H_AGENTS/$base" && linked=1
    done
    if [ "$linked" -eq 0 ]; then
      warn "agent ${base} 未链接：所选 harness 均不支持文件式 agent（${HARNESSES}）"
      info "  建议：把该 agent 的职责写进 SKILL.md 或指令文件，或改用 opencode/claude-code"
    fi
    [ "$linked" -eq 1 ] && LINKED_AGENTS="$LINKED_AGENTS $base"
  done
fi

# 4) 指令文件受管区块
hdr "4. 写入指令文件"
docs=""
for h in $HARNESSES; do
  harness_spec "$h"
  [ -n "$H_DOC" ] && docs="$docs $H_DOC"
done
docs="$(uniq_words "$docs")"
if [ -n "$(uniq_words "$LINKED_SKILLS$LINKED_AGENTS")" ]; then
  blockfile="$(mktemp)"
  {
    echo "$BLOCK_BEGIN"
    echo "## 本项目的 Skill 与 Agent"
    echo
    if [ -n "${LINKED_SKILLS// /}" ]; then
      echo "### Skills"
      echo
      for s in $(uniq_words "$LINKED_SKILLS"); do
        src="$(skill_src "$s")"
        path=""
        for h in $HARNESSES; do
          harness_spec "$h"; path="${H_SKILLS:-$path}"
        done
        echo "- \`$s\` — $(skill_desc "$src")"
      done
      echo
      echo "使用方式：需要时读取对应目录下的 \`SKILL.md\` 并按其指令执行。"
    fi
    if [ -n "${LINKED_AGENTS// /}" ]; then
      echo
      echo "### Agents"
      echo
      for a in $(uniq_words "$LINKED_AGENTS"); do
        echo "- \`$a\` — $(agent_desc "$REPO_ROOT/opencode-agents/shared/$a")"
      done
    fi
    echo "$BLOCK_END"
  } > "$blockfile"
  for d in $docs; do
    write_block "$PROJECT/$d" "$blockfile"
  done
  rm -f "$blockfile"
else
  info "无 skill/agent，跳过指令文件区块"
fi

# 5) .gitignore
hdr "5. .gitignore"
gi=()
gi+=("$(gitignore_lines "$PROJ_TYPE")")
for h in $HARNESSES; do
  harness_spec "$h"
  [ -n "$H_SKILLS" ] && gi+=("$H_SKILLS/")
  [ -n "$H_AGENTS" ] && gi+=("$H_AGENTS/")
done
printf '%s\n' "${gi[@]}" | awk 'NF && !seen[$0]++' | append_gitignore "$PROJECT"

# 6) git
hdr "6. Git"
if [ "$DO_GIT" -eq 1 ]; then
  if [ -d "$PROJECT/.git" ]; then
    info "已是 git 仓库，跳过 git init"
  else
    run git -C "$PROJECT" init -q && [ "$DRY_RUN" -eq 0 ] && ok "git init"
  fi
  if [ "$DO_COMMIT" -eq 1 ] && [ "$DRY_RUN" -eq 0 ]; then
    if [ -n "$(git -C "$PROJECT" status --porcelain 2>/dev/null)" ]; then
      if [ -z "$(git -C "$PROJECT" config user.email 2>/dev/null)" ]; then
        warn "git 未配置 user.email，跳过初始提交"
      else
        git -C "$PROJECT" add -A >/dev/null 2>&1 || true
        if git -C "$PROJECT" commit -qm "chore: 项目初始化（project-init: ${HARNESSES}）" >/dev/null 2>&1; then
          ok "初始提交已创建"
        else
          warn "初始提交失败（可稍后手动提交）"
        fi
      fi
    fi
  fi
else
  info "已跳过 git 初始化（--no-git）"
fi

# 7) DSH 特别提示
if in_list dsh "$HARNESSES"; then
  if [ ! -d "$PROJECT/.git" ]; then
    warn "DSH 以「最近含 .git 的祖先目录」为项目根来扫描 .dsh/skills；当前不是 git 仓库，请确保在项目根启动会话"
  fi
fi

# 8) 结果
hdr "✅ 完成：$PROJECT"
printf '  %s\n' "$PROJECT"
for h in $HARNESSES; do
  harness_spec "$h"
  printf '   ├─ %-12s skills=%s\n' "$h" "$([ -n "$H_SKILLS" ] && echo "$H_SKILLS" || echo '(不支持)')"
  [ -n "$H_AGENTS" ] && printf '   │  %-12s agents=%s\n' "" "$H_AGENTS"
  printf '   │  %-12s docs=%s\n' "" "$H_DOC"
done
[ -n "${LINKED_SKILLS// /}" ] && printf '   ├─ skills: %s\n' "$(uniq_words "$LINKED_SKILLS")"
[ -n "${LINKED_AGENTS// /}" ] && printf '   ├─ agents: %s\n' "$(uniq_words "$LINKED_AGENTS")"
printf '   └─ 下一步：cd %s\n' "$PROJECT"
