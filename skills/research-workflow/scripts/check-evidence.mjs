#!/usr/bin/env node
/**
 * check-evidence.mjs — 证据冻结门禁
 *
 * 用法:
 *   node check-evidence.mjs <证据文件...> [--json] [--quiet]
 *
 * 退出码: 0 全部通过 / 1 门禁未通过 / 2 用法或读取错误
 *
 * 判定项见 references/gates.md「门禁 1」。零依赖，Node >= 18。
 */

import fs from 'node:fs';

const USAGE = `用法: node check-evidence.mjs <证据文件...> [--json] [--quiet]

检查每份证据文件的 YAML 头、冻结状态、条数一致性与证据字段完整性。
退出码: 0 通过 / 1 不通过 / 2 用法错误`;

const REQUIRED_FIELDS = ['claim', 'source_url', 'platform', 'retrieved_at', 'confidence'];
const ID_RE = /^[a-z][a-z0-9_]*-\d+$/;
const CONFIDENCE = new Set(['high', 'medium', 'low']);
function parseArgs(argv) {
  const files = [];
  const flags = { json: false, quiet: false, help: false };
  for (const a of argv) {
    if (a === '--json') flags.json = true;
    else if (a === '--quiet') flags.quiet = true;
    else if (a === '-h' || a === '--help') flags.help = true;
    else if (a.startsWith('--')) { /* 忽略未知参数，便于前向兼容 */ }
    else files.push(a);
  }
  return { files, flags };
}

function splitTop(s, sep) {
  const out = [];
  let cur = '';
  let quote = null;
  for (const ch of s) {
    if (quote) {
      cur += ch;
      if (ch === quote) quote = null;
      continue;
    }
    if (ch === '"' || ch === "'") {
      quote = ch;
      cur += ch;
      continue;
    }
    if (ch === sep) {
      out.push(cur);
      cur = '';
      continue;
    }
    cur += ch;
  }
  out.push(cur);
  return out.map((x) => x.trim()).filter((x) => x !== '');
}

function parseScalar(input) {
  const v = String(input).trim();
  if (v === '') return '';
  if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) {
    return v.slice(1, -1);
  }
  if (v.startsWith('{') && v.endsWith('}')) {
    const out = {};
    const inner = v.slice(1, -1).trim();
    if (!inner) return out;
    for (const part of splitTop(inner, ',')) {
      const idx = part.indexOf(':');
      if (idx < 0) continue;
      out[part.slice(0, idx).trim()] = parseScalar(part.slice(idx + 1));
    }
    return out;
  }
  if (v.startsWith('[') && v.endsWith(']')) {
    const inner = v.slice(1, -1).trim();
    if (!inner) return [];
    return splitTop(inner, ',').map((x) => parseScalar(x));
  }
  if (/^(null|~)$/i.test(v)) return null;
  if (/^(true|false)$/i.test(v)) return v.toLowerCase() === 'true';
  if (/^-?\d+(?:\.\d+)?$/.test(v)) return Number(v);
  return v;
}

function parseBlockChildren(lines) {
  const meaningful = lines.filter((l) => l.trim() && !l.trim().startsWith('#'));
  if (!meaningful.length) return null;
  if (meaningful[0].trim().startsWith('-')) {
    return meaningful.map((l) => parseScalar(l.trim().replace(/^-\s*/, '')));
  }
  const map = {};
  for (const l of meaningful) {
    const m = l.match(/^\s*([A-Za-z0-9_-]+)\s*:\s*(.*)$/);
    if (m) map[m[1]] = parseScalar(m[2]);
  }
  return map;
}

/** 解析顶层的 key: value / 内联 map / 内联 list / 缩进块。只覆盖本门禁需要的子集。 */
function parseYaml(raw) {
  const lines = raw.split(/\r?\n/);
  const data = {};
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (!line.trim() || line.trim().startsWith('#')) continue;
    if ((line.match(/^ */) || [''])[0].length > 0) continue;
    const m = line.match(/^([A-Za-z0-9_-]+)\s*:\s*(.*)$/);
    if (!m) continue;
    const key = m[1];
    const rest = m[2].trim();
    if (rest === '' || rest === '|' || rest === '>') {
      const child = [];
      let j = i + 1;
      for (; j < lines.length; j++) {
        const l = lines[j];
        if (!l.trim()) {
          child.push(l);
          continue;
        }
        if ((l.match(/^ */) || [''])[0].length === 0) break;
        child.push(l);
      }
      data[key] = parseBlockChildren(child);
      i = j - 1;
    } else {
      data[key] = parseScalar(rest);
    }
  }
  return data;
}

function splitFrontMatter(text) {
  const m = text.match(/^\uFEFF?\s*---\r?\n([\s\S]*?)\r?\n---[ \t]*(?:\r?\n|$)/);
  if (!m) return null;
  return { raw: m[1], body: text.slice(m[0].length) };
}

function urlIsBareHomepage(rawUrl) {
  try {
    const u = new URL(rawUrl);
    return u.pathname === '' || u.pathname === '/';
  } catch {
    return false;
  }
}

function inspectRecord(block) {
  const e = {};
  const field = (name) => {
    const m = block.match(new RegExp(`(?:^|\\n)\\s*(?:-\\s*)?${name}\\s*:\\s*(.*)`));
    return m ? m[1].trim() : null;
  };
  e.claim = field('claim');
  // 旧文件普遍用 url:，作为 source_url 的兼容别名
  e.source_url = field('source_url') || field('url');
  e.usedLegacyUrlKey = !field('source_url') && Boolean(field('url'));
  e.platform = field('platform');
  e.published_at = field('published_at');
  e.retrieved_at = field('retrieved_at');
  e.evidence_type = field('evidence_type');
  e.confidence = field('confidence');
  return e;
}

function checkFile(file) {
  const errors = [];
  const warnings = [];
  let text;
  try {
    text = fs.readFileSync(file, 'utf8');
  } catch (err) {
    errors.push(`无法读取文件: ${err.message}`);
    return { file, ok: false, errors, warnings };
  }

  const fm = splitFrontMatter(text);
  if (!fm) {
    const legacy = /^>\s*status\s*:/m.test(text) || /^status\s*:/m.test(text);
    errors.push(
      legacy
        ? '缺少 YAML front-matter（检测到旧格式状态块）。按 references/evidence.md 改写为文件头，例如：\n---\nrun: <名称>\nstatus: collecting\nfrozen_at: null\ncounts:\n  <前缀>: <条数>\nfailures: []\n---'
        : '缺少 YAML front-matter。证据文件第一段必须是 --- 包裹的文件头，见 references/evidence.md'
    );
    return { file, ok: false, errors, warnings };
  }

  const head = parseYaml(fm.raw);
  const run = typeof head.run === 'string' ? head.run : null;
  const status = typeof head.status === 'string' ? head.status : null;

  if (!run) errors.push('文件头缺少 run');
  if (!status) errors.push('文件头缺少 status');
  else if (!['collecting', 'complete'].includes(status)) {
    errors.push(`status 取值非法: ${status}（只能是 collecting 或 complete）`);
  }

  if (status === 'complete') {
    if (!head.frozen_at || head.frozen_at === 'null') {
      errors.push('status 为 complete 时必须填写 frozen_at');
    } else if (!/^\d{4}-\d{2}-\d{2}(?:[ T]\d{2}:\d{2})?$/.test(String(head.frozen_at))) {
      errors.push(`frozen_at 格式应为 YYYY-MM-DD 或 YYYY-MM-DD HH:MM，实际: ${head.frozen_at}`);
    }
  }

  if (!Object.prototype.hasOwnProperty.call(head, 'failures') || head.failures === null) {
    errors.push('文件头缺少 failures（无失败也要写空列表 []）');
  }

  // 计数：按正文 evidence_id 前缀统计
  const body = fm.body;
  const idRe = /^[ \t]*(?:-[ \t]*)?evidence_id[ \t]*:[ \t]*(\S+)/gm;
  const matches = [...body.matchAll(idRe)];
  const measured = {};
  const records = [];

  for (let i = 0; i < matches.length; i++) {
    const id = matches[i][1].replace(/[`'"]/g, '');
    const start = matches[i].index + matches[i][0].length;
    const end = i + 1 < matches.length ? matches[i + 1].index : body.length;
    records.push({ id, block: body.slice(start, end) });
    if (!ID_RE.test(id)) {
      errors.push(`evidence_id 格式非法: ${id}（应为 前缀-两位序号，如 zhihu-01）`);
    }
    const prefix = id.split('-')[0];
    measured[prefix] = (measured[prefix] || 0) + 1;
  }

  const totalMeasured = records.length;
  if (totalMeasured === 0) errors.push('正文没有任何 evidence_id 记录');

  // 字段完整性
  let legacyUrlRecords = 0;
  records.forEach(({ id, block }) => {
    const rec = inspectRecord(block);
    if (rec.usedLegacyUrlKey) legacyUrlRecords += 1;
    for (const f of REQUIRED_FIELDS) {
      if (!rec[f]) errors.push(`${id} 缺字段 ${f}`);
    }
    if (rec.source_url && !/^https?:\/\//i.test(rec.source_url)) {
      errors.push(`${id} 的 source_url 不是 http(s) URL: ${rec.source_url}`);
    }
    if (rec.source_url && urlIsBareHomepage(rec.source_url) && rec.evidence_type === 'community') {
      errors.push(`${id} 指向站点首页，社区证据必须是具体内容页: ${rec.source_url}`);
    }
    if (rec.retrieved_at && !/^\d{4}-\d{2}-\d{2}$/.test(rec.retrieved_at)) {
      errors.push(`${id} 的 retrieved_at 应为 YYYY-MM-DD，实际: ${rec.retrieved_at}`);
    }
    if (rec.confidence) {
      const level = rec.confidence.match(/^(high|medium|low)\b/);
      if (!level) errors.push(`${id} 的 confidence 非法: ${rec.confidence}`);
      else if (rec.confidence !== level[1]) {
        warnings.push(`${id} 的 confidence 带说明或复合等级（${rec.confidence.slice(0, 24)}…），规范值只有 high/medium/low`);
      }
    }
  });

  // 声明条数 vs 实测条数
  const declared = head.counts && typeof head.counts === 'object' && !Array.isArray(head.counts)
    ? head.counts
    : null;
  if (!declared) {
    errors.push('文件头缺少 counts（按前缀声明条数）');
  } else {
    const declaredKeys = Object.keys(declared);
    for (const prefix of declaredKeys) {
      if (!(prefix in measured)) errors.push(`counts 声明了 ${prefix}: ${declared[prefix]}，正文没有该前缀的证据`);
      else if (Number(declared[prefix]) !== measured[prefix]) {
        errors.push(`counts.${prefix} 声明 ${declared[prefix]}，实测 ${measured[prefix]}`);
      }
    }
    for (const prefix of Object.keys(measured)) {
      if (!(prefix in declared)) errors.push(`正文有 ${measured[prefix]} 条 ${prefix}-，counts 未声明`);
    }
    const declaredTotal = declaredKeys.reduce((s, k) => s + Number(declared[k] || 0), 0);
    if (declaredTotal !== totalMeasured) {
      errors.push(`counts 合计 ${declaredTotal}，正文实测 ${totalMeasured}`);
    }
  }

  // 空结果却无失败记录
  if (status === 'complete' && Array.isArray(head.failures) && head.failures.length === 0) {
    warnings.push('failures 为空：确认本次确实没有任何失败来源（登录墙/无结果/反爬）');
  }
  if (legacyUrlRecords) {
    warnings.push(`有 ${legacyUrlRecords} 条用 url: 而非 source_url:，字段名请统一为 source_url`);
  }

  return {
    file,
    ok: errors.length === 0,
    run,
    status,
    errors,
    warnings,
    measured,
    declared: declared || {},
    total: totalMeasured,
  };
}

function kindOfWarning(w) {
  if (/confidence 带说明/.test(w)) return 'confidence-annotation';
  if (/用 url: 而非/.test(w)) return 'legacy-url';
  if (/failures 为空/.test(w)) return 'empty-failures';
  return w;
}

function summarizeWarnings(list) {
  const groups = new Map();
  for (const w of list) {
    const k = kindOfWarning(w);
    if (!groups.has(k)) groups.set(k, []);
    groups.get(k).push(w);
  }
  const tail = {
    'confidence-annotation': 'confidence 带说明或复合等级（规范值只有 high/medium/low）',
    'legacy-url': '字段名用 url 而非 source_url',
    'empty-failures': 'failures 为空',
  };
  const out = [];
  for (const [k, arr] of groups) {
    out.push(...arr.slice(0, 3));
    if (arr.length > 3) out.push(`（同类另有 ${arr.length - 3} 条${tail[k] ? `：${tail[k]}` : ''}）`);
  }
  return out;
}

function main() {
  const { files, flags } = parseArgs(process.argv.slice(2));
  if (flags.help) {
    console.log(USAGE);
    process.exit(0);
  }
  if (!files.length) {
    console.error(USAGE);
    process.exit(2);
  }

  const results = files.map(checkFile);
  const ok = results.every((r) => r.ok);

  if (flags.json) {
    console.log(JSON.stringify({ ok, files: results }, null, 2));
  } else {
    for (const r of results) {
      const label = r.ok ? 'PASS' : 'FAIL';
      const detail = r.ok ? `run=${r.run} status=${r.status} 条数=${r.total}` : `${r.errors.length} 个错误`;
      console.log(`[${label}] ${r.file}  ${detail}`);
      if (!flags.quiet) {
        for (const e of r.errors) console.log(`  - 错误: ${e}`);
        if (r.warnings.length) console.log(`  - 警告共 ${r.warnings.length} 条:`);
        for (const w of summarizeWarnings(r.warnings)) console.log(`    · ${w}`);
      }
    }
    console.log(ok ? '\n结论: 证据已冻结，可以派写作。' : '\n结论: 证据未通过门禁，不得派写作。');
  }

  process.exit(ok ? 0 : 1);
}

main();
