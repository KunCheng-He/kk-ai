#!/usr/bin/env bash
# init.sh — 多 harness 项目初始化驱动脚本（project-init）
#
# 仓库模型（kk-ai）：
#   skills/<name>/              通用 skill 源，任何 harness 都能用
#   <harness>/                  harness 专属资源（opencode/、pi/ …），只对该工具有效
#                               └── 其项目级目录约定写在下方 harness 注册表里
#   项目引用的方式只有一个：ln 符号链接。全局链接哪些、项目链接哪些，都由调用方决定。
#
# 用法：
#   ./init.sh index                        列出本仓库的 skill 与各 harness 的专属资源
#   ./init.sh discover <项目路径>          巡检目标项目现有的 harness 配置
#   ./init.sh plan <项目路径> [选项]       只打印计划，不写任何文件
#   ./init.sh init <项目路径> [选项]       落实目录、链接、指令文件、.gitignore、git
#
# 设计原则：
#   1. skill 只有一份源（skills/），不区分 shared/common
#   2. 所有 harness 差异集中在本文件的「harness 注册表」一段，新增只改那一处
#   3. 幂等：已就绪的链接跳过，受管区块原地刷新；--force 只重建链接
#   4. 绝不覆盖目标位置的真实文件/目录

set -euo pipefail

# macOS 自带 bash 3.2 + BSD awk/sed 需要 UTF-8 locale 才能正确处理中文
if [ -z "${LC_ALL:-}" ] && [ -z "${LANG:-}" ]; then
  export LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
DFT_REPO_ROOT="$(cd "$SKILL_DIR/../.." && pwd)"
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
  init.sh index                       列出仓库内容（skill + 各 harness 专属资源）
  init.sh discover <项目路径>         巡检项目现有配置（只读）
  init.sh plan  <项目路径> [选项]     打印计划，不写文件
  init.sh init  <项目路径> [选项]     执行初始化

选项：
  --harness <列表>   目标 harness，逗号/空格分隔
                     可用：见脚本内 ALL_HARNESSES（当前 opencode pi）
                     默认：探测当前会话的 harness
  --skill <列表>     通用 skill 名（<repo>/skills/<name>），可省略 .md
  --agent <列表>     harness 专属 agent，可带前缀：opencode/诸葛亮 或裸名 诸葛亮
  --command <列表>   指令文件里要提及的 command（不建链接）
  --type <类型>      .gitignore 模板：node|python|go|rust|java|universal（默认 universal）
  --repo-root <路径> kk-ai 仓库根（默认由脚本位置推断，也可用 KK_AI_ROOT）
  --no-git           跳过 git init / commit
  --no-commit        只 git init，不创建初始提交
  --force            已存在的链接重建为目标路径
  -h, --help         帮助

示例：
  init.sh index
  init.sh discover ~/Code/my-app
  init.sh plan ~/Code/my-app --harness opencode --skill research-workflow --agent 诸葛亮 --type python
  init.sh init ~/Code/my-app --harness opencode,pi --skill mermaid --agent opencode/诸葛亮
EOF
}

# ---------------------------------------------------------------- harness 注册表
# 仓库里每个 <harness>/ 目录的工具专属资源（agents/、cmds/、skills/）都是自动扫描的，
# 不用登记。这里只登记「这个工具的项目级目录约定」——
# 那是工具本身的事，目录里的文件增删不影响它。
#
# 新增一个 harness：
#   1. ALL_HARNESSES 加名字
#   2. 补 h_skills_dir / h_agent_dirs / h_instructions 的分支
#   3. 补 harness_status（index 里展示的核实状态）
#   4. 在 references/harnesses.md 表格加一行
# 其余逻辑不用动。

ALL_HARNESSES="opencode pi"

# 该 harness 在仓库里的资源目录（缺省 = 名字本身）
h_source_dir() { echo "$1"; }

# 项目级 skill 目录；空 = 该 harness 没有 skill 机制
h_skills_dir() {
  case "$1" in
    opencode) echo ".opencode/skills" ;;
    *)        echo "" ;;
  esac
}

# skill 目录是否已在真机核实；未核实的不链接通用 skill
h_skills_verified() {
  case "$1" in
    opencode) echo "true" ;;
    *)        echo "false" ;;
  esac
}

# 项目级 agent 目录，每行一个；空 = 无文件式 agent
h_agent_dirs() {
  case "$1" in
    opencode) printf '%s\n' ".opencode/agents" ;;
    pi)       printf '%s\n' ".pi/k-subagents" ".pi/k-priagent" ;;
    *)        : ;;
  esac
}

# 目标项目里 agent 文件的扩展名（按目录）
h_agent_ext() {
  case "$2" in
    .opencode/agents|.claude/agents|.pi/k-subagents|.pi/k-priagent) echo ".md" ;;
    *)                                                             echo ".md" ;;
  esac
}

# 项目级指令文件；空 = 不写
h_instructions() {
  case "$1" in
    opencode|pi) echo "AGENTS.md" ;;
    *)           echo "" ;;
  esac
}

# 指令文件的写入方式：block（受管区块）| mdc（Cursor 规则格式，带 frontmatter）
h_instructions_mode() {
  case "$1" in
    *) echo "block" ;;
  esac
}

# 展示名
harness_label() {
  case "$1" in
    opencode) echo "OpenCode" ;;
    pi)       echo "Pi" ;;
    *)        echo "$1" ;;
  esac
}

# 一句话核实状态（index 会打印）
harness_status() {
  case "$1" in
    opencode) echo "skill / agent / 指令文件均已在真机使用中核实；command 不自动链接" ;;
    pi)       echo "agent 目录来自 pi-k-subagent / pi-agent-switcher 扩展；Pi 核心是否有 skill 机制未核实" ;;
    *)        echo "" ;;
  esac
}

detect_harness() {
  if [ -n "${DSH_SESSION_ID:-}${DSH_HOME:-}" ]; then echo dsh; return 0; fi
  if [ -n "${CLAUDECODE:-}${CLAUDE_CODE_ENTRYPOINT:-}" ]; then echo claude-code; return 0; fi
  case "${OPENCODE:-}" in ""|0) ;; *) echo opencode; return 0; ;; esac
  if [ -n "${GEMINI_CLI:-}${GEMINI_SESSION_ID:-}" ]; then echo gemini-cli; return 0; fi
  if [ -n "${PI_SESSION_ID:-}${PI_HOME:-}" ]; then echo pi; return 0; fi
  if [ -d "$PWD/.opencode" ]; then echo opencode; return 0; fi
  if [ -d "$PWD/.pi" ]; then echo pi; return 0; fi
  if [ -d "$PWD/.claude" ]; then echo claude-code; return 0; fi
  if [ -d "$PWD/.dsh" ]; then echo dsh; return 0; fi
  echo generic
}

# ---------------------------------------------------------------- 资源解析
# 解析 skill 名。返回 "<kind>\t<源目录>"，kind = shared（通用）| harness
#   research-workflow        → skills/research-workflow            （通用）
#   opencode/loop-by-herdr  → opencode/skills/loop-by-herdr        （harness 专属）
resolve_skill() {
  local n="$1" h s
  if has_slash "$n"; then
    h="${n%%/*}"; s="${n#*/}"
    if in_list "$h" "$ALL_HARNESSES" && [ -d "$REPO_ROOT/$h/skills/$s" ]; then
      printf 'harness\t%s\n' "$REPO_ROOT/$h/skills/$s"; return 0
    fi
    return 1
  fi
  [ -d "$REPO_ROOT/skills/$n" ] && { printf 'shared\t%s\n' "$REPO_ROOT/skills/$n"; return 0; }
  return 1
}

# SKILL.md front-matter 的 description，压成一行
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
  d="$(printf '%s' "$d" | sed -e 's/[[:space:]]\+/ /g' -e 's/^ //' -e 's/ $//' -e 's/^["'\'']//' -e 's/["'\'']$//')"
  [ -z "$d" ] && d="（无描述）"
  printf '%s' "$d"
}

# 仓库内某 harness 目录下按约定可链接的资源（相对路径）：
#   <harness>/agents/ → --agent 的源（单数 agent/ 也认）
#   <harness>/cmds/   → command（只写进清单，脚本不建链接；单数 cmd/ 也认）
#   <harness>/skills/ → 该 harness 专属 skill
AGENT_SUBDIRS="agents agent"
CMD_SUBDIRS="cmds cmd"
harness_agent_files() {
  local h="$1" src d
  src="$REPO_ROOT/$(h_source_dir "$h")"
  for d in $AGENT_SUBDIRS $CMD_SUBDIRS skills; do
    [ -d "$src/$d" ] || continue
    find "$src/$d" \( -name '*.md' -o -name 'SKILL.md' \) -not -path '*/node_modules/*' \
      | sed "s|^$src/||" | sort
  done
}

# 解析 --agent 实参：支持 opencode/xxx、xxx.md、xxx
resolve_agent() {
  local raw="$1" q="${1%.md}" h sub src only=""
  local found_h="" found_rel="" found_src=""
  # 允许前缀：opencode/诸葛亮
  if has_slash "$q"; then only="${q%%/*}"; q="${q#*/}"; fi
  for h in $ALL_HARNESSES; do
    [ -n "$only" ] && [ "$h" != "$only" ] && continue
    for sub in $AGENT_SUBDIRS; do
      src="$REPO_ROOT/$(h_source_dir "$h")/$sub"
      [ -f "$src/$q.md" ] && { found_h="$h"; found_rel="$q.md"; found_src="$src/$q.md"; break; }
      [ -f "$src/$q" ]   && { found_h="$h"; found_rel="$q";    found_src="$src/$q";    break; }
    done
    [ -n "$found_h" ] && break
  done
  [ -z "$found_h" ] && return 1
  printf '%s\t%s\t%s\n' "$found_h" "$found_rel" "$found_src"
}

agent_desc() {
  local f="$1" d
  [ -f "$f" ] || { echo ""; return 0; }
  d="$(grep -m1 '^description:' "$f" 2>/dev/null | sed -e 's/^description:[[:space:]]*//' || true)"
  [ -z "$d" ] && d="$(basename "$f")"
  printf '%s' "$d"
}

# ---------------------------------------------------------------- index
list_all() {
  local what="${1:-all}" h s d src
  if [ "$what" = "all" ] || [ "$what" = "harness" ]; then
    hdr "通用 Skills（${REPO_ROOT}/skills/ —— 任何 harness 都可链接）"
    for s in "$REPO_ROOT"/skills/*/; do
      [ -d "$s" ] || continue
      s="$(basename "$s")"
      printf '  %-24s %s\n' "$s" "$(skill_desc "$REPO_ROOT/skills/$s")"
    done
  fi
  if [ "$what" = "all" ] || [ "$what" = "harness" ]; then
    hdr "Harness 专属资源（${REPO_ROOT}/<harness>/ —— 只对该工具有效）"
    for h in $ALL_HARNESSES; do
      src="$REPO_ROOT/$(h_source_dir "$h")"
      printf '\n  %-14s %s\n' "$h" "$(harness_label "$h")"
      printf '  %-14s status: %s\n' "" "$(harness_status "$h")"
      d="$(h_skills_dir "$h")"
      if [ -n "$d" ]; then
        if [ "$(h_skills_verified "$h")" = "true" ]; then
          printf '  %-14s skill 目录 %s（已核实，链接 skills/<name>）\n' "" "$d"
        else
          printf '  %-14s skill 目录 %s（⚠️ 未核实）\n' "" "$d"
        fi
      fi
      while IFS= read -r d; do
        [ -n "$d" ] || continue
        printf '  %-14s agent 目录 %s\n' "" "$d"
      done < <(h_agent_dirs "$h")
      printf '  %-14s 指令文件 %s\n' "" "$(h_instructions "$h")"
      [ -d "$src" ] || continue
      while IFS= read -r s; do
        [ -n "$s" ] || continue
        printf '  %-14s 资源 %s\n' "" "$s"
      done < <(harness_agent_files "$h")
    done
    if [ -z "$ALL_HARNESSES" ]; then
      info "未发现任何 harness（在 scripts/init.sh 的 ALL_HARNESSES 里声明）"
    fi
  fi
}

# ---------------------------------------------------------------- discover
discover_project() {
  local proj="$1" h d n hit first=1 tgt
  hdr "🔍 巡检现有配置：${proj}"
  if [ ! -d "$proj" ]; then info "目录不存在（全新项目）"; return 0; fi
  if [ -d "$proj/.git" ]; then info "git 仓库：是"; else info "git 仓库：否"; fi
  for h in $ALL_HARNESSES; do
    hit=0; d=""
    :
    [ -n "$(h_skills_dir "$h")" ] && [ -d "$proj/$(h_skills_dir "$h")" ] && hit=1
    while IFS= read -r d; do [ -n "$d" ] && [ -d "$proj/$d" ] && hit=1; done < <(h_agent_dirs "$h")
    [ "$hit" -eq 0 ] && continue
    [ "$first" -eq 0 ] && echo
    first=0
    printf '%s（%s）\n' "$h" "$(harness_label "$h")"
    for d in $(h_skills_dir "$h") $(h_agent_dirs "$h"); do
      [ -n "$d" ] || continue
      [ -d "$proj/$d" ] || continue
      printf '  %s/\n' "$d"
      for n in "$proj/$d"/*; do
        [ -e "$n" ] || [ -L "$n" ] || continue
        if [ -L "$n" ]; then
          tgt="$(readlink "$n")"
          case "$tgt" in
            "$REPO_ROOT"/*) printf '    · %s → kk-ai/%s（仓库链接）\n' "$(basename "$n")" "${tgt#"$REPO_ROOT"/}" ;;
            *)              printf '    · %s → %s\n' "$(basename "$n")" "$tgt" ;;
          esac
        else
          printf '    · %s（真实文件/目录，脚本不会改动）\n' "$(basename "$n")"
        fi
      done
    done
  done
  # 指令文件单独汇报：多个 harness 共用同一个 AGENTS.md 时只报一次
  local seen=""
  for h in $ALL_HARNESSES; do
    d="$(h_instructions "$h")"
    [ -n "$d" ] || continue
    [ -f "$proj/$d" ] || continue
    # 多个 harness 共用同一个指令文件时只报一次
    printf '%s\n' "$seen" | grep -qxF -- "$d" && continue
    seen="$seen $d"
    if grep -q 'project-init:begin' "$proj/$d" 2>/dev/null; then
      printf '\n指令文件 %s（含 project-init 受管区块，重跑会原地刷新）\n' "$d"
    else
      printf '\n指令文件 %s（无受管区块，重跑只追加区块，原有内容保留）\n' "$d"
    fi
  done
}

# ---------------------------------------------------------------- 工具函数
run() {
  if [ "$DRY_RUN" -eq 1 ]; then printf '  [plan] %s\n' "$*"; else "$@"; fi
}

has_slash() { [[ "$1" == */* ]]; }

uniq_words() { echo "$*" | tr ' ' '\n' | awk 'NF && !seen[$0]++' | tr '\n' ' ' | sed 's/ $//'; }

in_list() { case " $2 " in *" $1 "*) return 0;; esac; return 1; }

link_path() {
  # 形参名带下划线前缀，避免与调用方的 src/dst/base 等同名变量互相覆盖
  local _src="$1" _dst="$2"
  [ -n "$_dst" ] || return 1
  if [ -L "$_dst" ]; then
    if [ "$(readlink "$_dst")" = "$_src" ]; then
      info "已就绪：$_dst → $_src"
      return 0
    fi
    if [ "$FORCE" -eq 1 ]; then
      run rm -f "$_dst"
    else
      warn "已存在不同链接，跳过（--force 可重建）：$_dst → $(readlink "$_dst")"
      return 1
    fi
  elif [ -e "$_dst" ]; then
    warn "已存在真实文件/目录，跳过（不动用户内容）：$_dst"
    return 1
  fi
  run ln -s "$_src" "$_dst"
  if [ "$DRY_RUN" -eq 0 ]; then
    if [ -e "$_dst" ]; then ok "链接 $_dst → $_src"
    else err "链接失败（源不存在？）：$_src"; return 1; fi
  fi
  return 0
}

# 受管区块写入/替换
write_block() {
  local file="$1" block="$2" mode="$3"
  if [ "$DRY_RUN" -eq 1 ]; then
    printf '  [plan] 写入受管区块 %s（%s 行）\n' "$file" "$(wc -l < "$block" | tr -d ' ')"
    return 0
  fi
  mkdir -p "$(dirname "$file")"
  if [ ! -f "$file" ]; then
    case "$mode" in
      mdc|MDC) { printf -- '---\ndescription: 项目规则（project-init 生成）\nglobs: **/*\nalwaysApply: true\n---\n\n'; cat "$block"; } > "$file" ;;
      *)   cat "$block" > "$file" ;;
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
  printf '%s\n' "# project-init: harness 链接目录（机器本地链接，不入库）"
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
CMD="init"; DRY_RUN=0; FORCE=0; DO_GIT=1; DO_COMMIT=1; PROJ_TYPE="universal"; PROJECT=""
TARGET_HARNESSES=""; SKILLS=""; AGENTS=""; COMMANDS=""

while [ $# -gt 0 ]; do
  case "$1" in
    index|list)     CMD="index"; shift ;;
    discover)       CMD="discover"; shift ;;
    plan)           CMD="plan"; DRY_RUN=1; shift ;;
    init)           CMD="init"; shift ;;
    --harness)      TARGET_HARNESSES="$TARGET_HARNESSES $(echo "${2:-}" | tr ',' ' ')"; shift 2 ;;
    --skill)        SKILLS="$SKILLS $(echo "${2:-}" | tr ',' ' ')"; shift 2 ;;
    --agent)        AGENTS="$AGENTS $(echo "${2:-}" | tr ',' ' ')"; shift 2 ;;
    --command)      COMMANDS="$COMMANDS $(echo "${2:-}" | tr ',' ' ')"; shift 2 ;;
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


case "$CMD" in
  index) list_all "${PROJECT:-all}"; exit 0 ;;
  discover)
    [ -n "$PROJECT" ] || { err "缺少项目路径"; usage; exit 2; }
    discover_project "$PROJECT"; exit 0 ;;
esac

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

TARGET_HARNESSES="$(uniq_words "${TARGET_HARNESSES:-}")"
if [ -z "$TARGET_HARNESSES" ]; then
  TARGET_HARNESSES="$(detect_harness)"
  info "未指定 harness，自动探测为：$TARGET_HARNESSES"
fi
for h in $TARGET_HARNESSES; do
  if ! in_list "$h" "$ALL_HARNESSES"; then
    err "未知 harness：${h}（可用：${ALL_HARNESSES}）"
    exit 2
  fi
done

SKILLS="$(uniq_words "${SKILLS:-}")"
AGENTS="$(uniq_words "${AGENTS:-}")"
COMMANDS="$(uniq_words "${COMMANDS:-}")"

hdr "📋 初始化计划（${CMD}$([ "$DRY_RUN" -eq 1 ] && echo '，仅预览')）"
info "项目路径：$PROJECT"
info "harness ：$TARGET_HARNESSES"
[ -n "$SKILLS" ]   && info "skills  ：$SKILLS"
[ -n "$AGENTS" ]   && info "agents  ：$AGENTS"
[ -n "$COMMANDS" ] && info "commands：${COMMANDS}（仅写入清单）"
info ".gitignore 类型：$PROJ_TYPE"

# 0) 预检：资源不存在就不留半成品目录
missing=0
linkable_skills=""         # 通用 skill（落到每个有 skill 目录的 harness）
harness_skills=""          # harness 专属 skill，每行：harness<TAB>名字<TAB>源目录
for s in $SKILLS; do
  s="${s%.md}"
  if res="$(resolve_skill "$s")"; then
    kind="${res%%$(printf '\t')*}"; src="${res#*$(printf '\t')}"
    if [ "$kind" = "harness" ]; then
      harness_skills="$harness_skills
${s%%/*}$(printf '\t')${s#*/}$(printf '\t')$src"
    else
      linkable_skills="$linkable_skills $s"
    fi
  else
    err "skill 不存在：${s}（查 ${REPO_ROOT}/skills/，或 ${REPO_ROOT}/<harness>/skills/）"; missing=1
  fi
done
AGENT_OWNERS=""       # 空格分隔，与 AGENT_SRCS 一一对应
AGENT_SRCS=""
TAB_CHAR="$(printf '\t')"
for a in $AGENTS; do
  if res="$(resolve_agent "$a")"; then
    AGENT_OWNERS="$AGENT_OWNERS ${res%%"$TAB_CHAR"*}"
    tmp="${res#*"$TAB_CHAR"}"          # 去掉首段后：相对路径<TAB>源路径
    AGENT_SRCS="$AGENT_SRCS ${tmp#*"$TAB_CHAR"}"   # 再去掉相对路径，只留源路径
  else
    err "agent 不存在：${a}（查 ${REPO_ROOT}/<harness>/agents/）"; missing=1
  fi
done
if [ "$missing" -eq 1 ]; then
  err "预检失败：未创建任何文件。用 index 子命令查看可用资源"
  exit 3
fi
linkable_skills="$(uniq_words "$linkable_skills")"

# 每个 skill 能落到哪些 harness
skills_linkable=""    # 实际写出了链接的 harness
for h in $TARGET_HARNESSES; do
  d="$(h_skills_dir "$h")"
  if [ -n "$d" ] && [ "$(h_skills_verified "$h")" = "true" ]; then
    skills_linkable="$skills_linkable $h"
  elif [ -n "$d" ]; then
    warn "$h 的 skill 目录（${d}）未核实：默认不链接；核实后改 scripts/init.sh 的 h_skills_verified"
  fi
done

# 1) 目录
hdr "1. 创建目录结构"
[ "$DRY_RUN" -eq 0 ] && mkdir -p "$PROJECT"
dirs=""
for h in $TARGET_HARNESSES; do
  in_list "$h" "$skills_linkable" && [ -n "$linkable_skills" ] && dirs="$dirs $(h_skills_dir "$h")"
  while IFS= read -r d; do
    [ -n "$d" ] && dirs="$dirs $d"
  done < <(h_agent_dirs "$h")
done
for d in $(uniq_words "$dirs"); do
  case "$d" in
    .agents/skills) [ -d "$PROJECT/.agents/skills" ] && continue ;;
  esac
  run mkdir -p "$PROJECT/$d"; [ "$DRY_RUN" -eq 0 ] && ok "mkdir -p $d"
done

# 2) skills（通用源，逐 harness 落到各自的 skill 目录）
LINKED_SKILLS=""            # "名字|来源说明"
if [ -n "$linkable_skills" ] || [ -n "$(echo "$harness_skills" | tr -d ' \n')" ]; then
  hdr "2. 链接 skills"
  if [ -z "$skills_linkable" ]; then
    warn "所选 harness 均无已核实的 skill 目录，跳过通用 skill"
  else
    for s in $linkable_skills; do
      src="$REPO_ROOT/skills/$s"
      for h in $skills_linkable; do
        link_path "$src" "$PROJECT/$(h_skills_dir "$h")/$s" && LINKED_SKILLS="$LINKED_SKILLS
$s|kk-ai/skills"
      done
      info "${s}（通用，源 skills/${s}）"
    done
  fi
  while IFS="$(printf '\t')" read -r hs name src; do
    [ -n "$hs" ] || continue
    hdir="$(h_skills_dir "$hs")"
    if [ -z "$hdir" ] || [ "$(h_skills_verified "$hs")" != "true" ]; then
      warn "$name 是 ${hs} 专属 skill，但 ${hs} 的 skill 目录未核实，未链接"
      continue
    fi
    if in_list "$hs" "$TARGET_HARNESSES"; then
      link_path "$src" "$PROJECT/$hdir/$name" && LINKED_SKILLS="$LINKED_SKILLS
$name|kk-ai/$hs/skills"
    else
      warn "$name 是 ${hs} 专属 skill，只对 ${hs} 生效；本次 harness 为 ${TARGET_HARNESSES}"
    fi
  done <<EOF
$harness_skills
EOF
fi

# 3) agents（harness 专属）
LINKED_AGENTS=""      # 每行：文件名|来源harness
if [ -n "${AGENT_SRCS// /}" ]; then
  hdr "3. 链接 agents"
  # 本次要落到的 (harness, 目录, 扩展名) 三元组
  AD_H=""; AD_D=""; AD_E=""
  for h in $TARGET_HARNESSES; do
    for d in $(h_agent_dirs "$h"); do
      [ -n "$d" ] || continue
      AD_H="$AD_H $h"; AD_D="$AD_D $d"; AD_E="$AD_E $(h_agent_ext "$h" "$d")"
    done
  done
  i=0
  for asrc in $AGENT_SRCS; do
    i=$((i+1))
    ah="$(echo $AGENT_OWNERS | cut -d' ' -f"$i")"
    abase="$(basename "$asrc")"
    linked_here=0
    n=0
    for d in $AD_D; do
      n=$((n+1))
      ext="$(echo $AD_E | cut -d' ' -f"$n")"
      [ -n "$ext" ] || ext=".md"
      case "$abase" in
        *"$ext") dest="$PROJECT/$d/$abase" ;;
        *)       dest="$PROJECT/$d/${abase%.md}$ext" ;;
      esac
      if link_path "$asrc" "$dest"; then
        linked_here=1
        LINKED_AGENTS="$LINKED_AGENTS
$abase|$ah"
      fi
    done
    if [ "$linked_here" -eq 0 ] && [ -z "$AD_D" ]; then
      warn "agent ${abase} 无处可落：${TARGET_HARNESSES} 都没有 agent 目录"
    fi
    if in_list "$ah" "$TARGET_HARNESSES"; then
      info "${abase}（来自 ${ah}）"
    else
      warn "${abase} 属于 ${ah} 的约定，已按通用 frontmatter 落到本次目标目录；如需原样生效请加 --harness ${ah}"
    fi
  done
fi

# 4) 指令文件受管区块
hdr "4. 写入指令文件"
docs=""
for h in $TARGET_HARNESSES; do
  d="$(h_instructions "$h")"
  [ -n "$d" ] && docs="$docs $d"
done
docs="$(uniq_words "$docs")"
if [ -n "$(echo "$LINKED_SKILLS$LINKED_AGENTS" | tr -d ' \n')${COMMANDS// /}" ]; then
  blockfile="$(mktemp)"
  {
    echo "$BLOCK_BEGIN"
    echo "## 本项目的 Skill 与 Agent"
    echo
    if [ -n "$(echo "$LINKED_SKILLS" | tr -d ' \n')" ]; then
      echo "### Skills"
      echo
      echo "$LINKED_SKILLS" | awk -F'|' 'NF && !seen[$1]++ { printf "- `%s` — 源 %s\n", $1, $2 }'
      echo
      echo "使用方式：需要时读取对应目录下的 \`SKILL.md\` 并按其指令执行。"
    fi
    if [ -n "$(echo "$LINKED_AGENTS" | tr -d ' \n')" ]; then
      echo
      echo "### Agents（harness 专属）"
      echo
      echo "$LINKED_AGENTS" | awk -F'|' 'NF && !seen[$0]++ { printf "- `%s` — 来自 %s\n", $1, $2 }'
    fi
    if [ -n "${COMMANDS// /}" ]; then
      echo
      echo "### Commands（按需手动链接，未自动建立）"
      echo
      for c in $(uniq_words "$COMMANDS"); do echo "- \`$c\`"; done
    fi
    echo "$BLOCK_END"
  } > "$blockfile"
  for d in $docs; do
    write_block "$PROJECT/$d" "$blockfile" "$(h_instructions_mode "$(for h in $TARGET_HARNESSES; do [ "$(h_instructions "$h")" = "$d" ] && { echo "$h"; break; }; done)")"
  done
  rm -f "$blockfile"
else
  info "无 skill/agent，跳过指令文件区块"
fi

# 5) .gitignore（只忽略链接目录）
hdr "5. .gitignore"
{
  gitignore_lines "$PROJ_TYPE"
  for h in $TARGET_HARNESSES; do
    in_list "$h" "$skills_linkable" && [ -n "$linkable_skills" ] && echo "$(h_skills_dir "$h")/"
    while IFS= read -r d; do
      [ -n "$d" ] && echo "$d/"
    done < <(h_agent_dirs "$h")
  done
} | awk 'NF && !seen[$0]++' | append_gitignore "$PROJECT"

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
        if git -C "$PROJECT" commit -qm "chore: 项目初始化（project-init: ${TARGET_HARNESSES}）" >/dev/null 2>&1; then
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

# 7) DSH 项目根提示
if in_list dsh "$TARGET_HARNESSES" && [ ! -d "$PROJECT/.git" ]; then
  warn "DSH 以「最近含 .git 的祖先目录」为项目根扫描 .dsh/skills；当前不是 git 仓库，请确保在项目根启动会话"
fi

# 8) 结果
hdr "✅ 完成：$PROJECT"
for h in $TARGET_HARNESSES; do
  printf '   ├─ %s\n' "$(harness_label "$h")"
  if in_list "$h" "$skills_linkable"; then
    printf '   │    skills → %s\n' "$(h_skills_dir "$h")"
  elif [ -n "$(h_skills_dir "$h")" ]; then
    printf '   │    skills → %s（未核实，未链接）\n' "$(h_skills_dir "$h")"
  else
    printf '   │    skills → 无\n'
  fi
  while IFS= read -r d; do
    [ -n "$d" ] && printf '   │    agents → %s\n' "$d"
  done < <(h_agent_dirs "$h")
  printf '   │    docs   → %s\n' "$(h_instructions "$h")"
done
if [ -n "$(echo "$LINKED_SKILLS" | tr -d ' \n')" ]; then
  printf '   ├─ skills: %s\n' "$(echo "$LINKED_SKILLS" | awk -F'|' 'NF && !seen[$1]++ { printf "%s ", $1 }')"
fi
if [ -n "$(echo "$LINKED_AGENTS" | tr -d ' \n')" ]; then
  printf '   ├─ agents: %s\n' "$(echo "$LINKED_AGENTS" | awk -F'|' 'NF && !seen[$0]++ { printf "%s ", $1 }')"
fi
printf '   └─ 下一步：cd %s\n' "$PROJECT"