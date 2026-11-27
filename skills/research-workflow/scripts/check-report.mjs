#!/usr/bin/env node
/**
 * check-report.mjs — 报告终审门禁
 *
 * 用法:
 *   node check-report.mjs <报告.md> [--evidence <证据文件...>] [--strict] [--json]
 *
 * 退出码: 0 通过 / 1 有错误（或 --strict 下的警告）/ 2 用法或读取错误
 *
 * 判定项见 references/gates.md「门禁 2」。零依赖，Node >= 18。
 */

import fs from 'node:fs';
import path from 'node:path';

const USAGE = `用法: node check-report.mjs <报告.md> [--evidence <证据文件...>] [--strict] [--json]

检查结构顺序、引用可追溯性、URL、日期、表格、图片与证据冻结状态。
退出码: 0 通过 / 1 不通过 / 2 用法错误`;

const ID_RE = /^[a-z][a-z0-9_]*-\d+$/;
const RANGE_RE = /^[a-z][a-z0-9_]*-\d+\s*~\s*\d+$/;
const URL_RE = /https?:\/\/[^\s)）>」]+/g;
const DATE_RE = /(\d{4}-\d{2}-\d{2}|\d{4}\/\d{2}\/\d{2}|\d{4}\s*年\s*\d{1,2}\s*月)/;
const DATE_MISSING_RE = /(not stated|未获取|未标注|不详|未知)/i;

function parseArgs(argv) {
  const flags = { strict: false, json: false, help: false };
  const evidence = [];
  let report = null;
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--strict') flags.strict = true;
    else if (a === '--json') flags.json = true;
    else if (a === '-h' || a === '--help') flags.help = true;
    else if (a === '--evidence') {
      let j = i + 1;
      while (j < argv.length && !argv[j].startsWith('--')) {
        evidence.push(...argv[j].split(',').map((s) => s.trim()).filter(Boolean));
        j += 1;
      }
      i = j - 1;
    } else if (!a.startsWith('--') && !report) report = a;
    else if (a.startsWith('--')) { /* 忽略未知参数 */ }
  }
  return { report, evidence, flags };
}

function isCitationGroup(inner) {
  const tokens = inner.split(/[、,，;；\s]+/).map((s) => s.trim()).filter(Boolean);
  return tokens.length > 0 && tokens.every((t) => ID_RE.test(t));
}

function findHeading(lines, re) {
  for (let i = 0; i < lines.length; i++) {
    const m = lines[i].match(/^##\s+(.+?)\s*$/);
    if (m && re.test(m[1])) return { index: i, title: m[1] };
  }
  return null;
}

function urlKind(raw) {
  try {
    const u = new URL(raw);
    const barePath = u.pathname === '' || u.pathname === '/';
    if (!barePath) return 'content';
    if (u.search && /[?&](q|query|search|wd|word|keyword)=/i.test(u.search)) return 'search';
    return 'homepage';
  } catch {
    return 'content';
  }
}

function check(reportPath, evidencePaths, strict) {
  const errors = [];
  const warnings = [];
  const info = {};
  let text;
  try {
    text = fs.readFileSync(reportPath, 'utf8');
  } catch (err) {
    errors.push(`无法读取报告: ${err.message}`);
    return { ok: false, errors, warnings, info };
  }

  const lines = text.split(/\r?\n/);
  const headings = [];
  lines.forEach((line, i) => {
    const m = line.match(/^##\s+(.+?)\s*$/);
    if (m) headings.push({ index: i, title: m[1] });
  });

  // 1. 结构
  const summary = findHeading(lines, /^(?:\d+[.、]\s*)?(?:结论)?摘要/);
  const limits = findHeading(lines, /^(?:\d+[.、]\s*)?(?:数据局限|数据不足)/);
  const appendix = findHeading(lines, /附录|证据索引|数据来源|参考资料/);

  if (!summary) errors.push('缺少「摘要」章节');
  if (!limits) errors.push('缺少「数据局限」章节');
  if (!appendix) errors.push('缺少「附录：证据索引」章节');
  if (appendix && !/附录/.test(appendix.title)) {
    warnings.push(`证据索引章节标题是「${appendix.title}」，新版规范为「附录：证据索引」`);
  }
  if (summary && limits && summary.index > limits.index) errors.push('章节顺序错误：「摘要」应在「数据局限」之前');
  if (limits && appendix && limits.index > appendix.index) errors.push('章节顺序错误：「数据局限」应在「附录」之前');
  info.sections = headings.map((h) => h.title);

  const bodyEnd = appendix ? appendix.index : lines.length;
  const bodyLines = lines.slice(0, bodyEnd);
  const appendixLines = appendix ? lines.slice(appendix.index) : [];

  // 2. 附录编号与分组
  const groupOf = new Map();
  const groupIds = new Map();
  const appendixIds = new Set();
  let group = '(未分组)';
  for (const line of appendixLines) {
    const h = line.match(/^###\s+(.+?)\s*$/);
    if (h) {
      group = h[1];
      if (!groupIds.has(group)) groupIds.set(group, new Set());
    }
    const bullet = line.match(/^\s*[-*]\s+(.+)$/);
    if (!bullet) continue;
    const content = bullet[1];
    const ids = [];
    let inlineBracketIds = 0;
    for (const m of content.matchAll(/`([^`]+)`/g)) {
      if (ID_RE.test(m[1].trim())) ids.push(m[1].trim());
    }
    // 兼容旧式 [id] / [id~id] 写法；标出格式差异但不直接判错
    for (const m of content.matchAll(/\[([^\]\n]+)\]/g)) {
      const inner = m[1].trim();
      const tokens = inner.split(/[、,，;；\s]+/).map((s) => s.trim()).filter(Boolean);
      if (!tokens.length) continue;
      if (tokens.some((t) => RANGE_RE.test(t))) {
        for (const t of tokens.filter((x) => RANGE_RE.test(x))) {
          errors.push(`附录使用范围写法「[${t}]」，证据必须逐条编号`);
        }
        continue;
      }
      const found = tokens.filter((t) => ID_RE.test(t));
      if (found.length) {
        ids.push(...found);
        if (!/^\s*\[/.test(content)) inlineBracketIds += found.length;
      }
    }
    if (inlineBracketIds) {
      if (!warnings.some((w) => w.startsWith('附录编号写在方括号'))) {
        warnings.push('附录编号写在方括号或行内，标准格式为行首 `id` + 日期 + URL');
      }
    }
    if (!ids.length) {
      const lead = content.match(/^([a-z][a-z0-9_]*-\d+)\b/);
      if (lead) ids.push(lead[1]);
    }
    for (const id of ids) {
      if (appendixIds.has(id) && groupOf.get(id) !== group) {
        warnings.push(`编号 ${id} 在附录出现多次（分组: ${groupOf.get(id)} / ${group}）`);
      }
      appendixIds.add(id);
      groupOf.set(id, group);
      if (!groupIds.has(group)) groupIds.set(group, new Set());
      groupIds.get(group).add(id);
    }
  }
  info.appendixIds = appendixIds.size;
  info.groups = [...groupIds.entries()].map(([g, set]) => `${g}: ${set.size}`);

  if (!appendixIds.size) errors.push('附录里没有识别到任何证据编号（格式: `平台-01`）');

  // 3. 正文引用
  const cited = new Map();
  const citationGroups = [];
  bodyLines.forEach((line, idx) => {
    for (const m of line.matchAll(/〔([^〕]+)〕/g)) {
      if (!isCitationGroup(m[1])) continue;
      citationGroups.push({ line: idx + 1, raw: m[0] });
      for (const t of m[1].split(/[、,，;；\s]+/).map((s) => s.trim()).filter(Boolean)) {
        cited.set(t, (cited.get(t) || 0) + 1);
      }
    }
    for (const m of line.matchAll(/（([^）]+)）/g)) {
      if (!isCitationGroup(m[1])) continue;
      warnings.push(`第 ${idx + 1} 行用（）标注证据，新版规范用〔〕`);
    }
    // 旧式方括号引用与范围写法：给出明确诊断，不让它们静默变成 0 条
    for (const m of line.matchAll(/\[([^\]\n]+)\](?!\()/g)) {
      const inner = m[1].trim();
      const tokens = inner.split(/[、,，;；\s]+/).map((s) => s.trim()).filter(Boolean);
      if (!tokens.length) continue;
      if (tokens.some((t) => RANGE_RE.test(t))) {
        errors.push(`第 ${idx + 1} 行使用范围写法「[${inner}]」，证据必须逐条编号、逐条引用`);
      } else if (tokens.every((t) => ID_RE.test(t))) {
        warnings.push(`第 ${idx + 1} 行用 [id] 标注证据，新版规范用〔〕`);
        for (const t of tokens) cited.set(t, (cited.get(t) || 0) + 1);
      }
    }
  });
  info.citedIds = cited.size;

  const missingInAppendix = [...cited.keys()].filter((id) => !appendixIds.has(id));
  if (missingInAppendix.length) {
    errors.push(`正文引用了附录里没有的编号: ${missingInAppendix.slice(0, 12).join(', ')}${missingInAppendix.length > 12 ? ' …' : ''}`);
  }
  const unused = [...appendixIds].filter((id) => !cited.has(id));
  if (unused.length) warnings.push(`附录有 ${unused.length} 条编号未在正文引用: ${unused.slice(0, 8).join(', ')}${unused.length > 8 ? ' …' : ''}`);

  // 4. 引用密度（段落 / 列表项 / 表格行各自为单位）
  const units = [];
  let buf = [];
  const flush = () => {
    if (buf.length) units.push({ start: buf[0].line, text: buf.map((b) => b.text).join('\n') });
    buf = [];
  };
  bodyLines.forEach((line, i) => {
    const isItem = /^\s*([-*+]|\d+\.)\s+/.test(line) || /^\s*\|/.test(line);
    if (!line.trim()) {
      flush();
      return;
    }
    if (isItem) {
      flush();
      units.push({ start: i + 1, text: line });
      return;
    }
    buf.push({ line: i + 1, text: line });
  });
  flush();
  for (const u of units) {
    if (u.text.trimStart().startsWith('>')) continue; // 引用块用于表格证据索引，不按正文密度计
    const groups = [...u.text.matchAll(/〔([^〕]+)〕/g)].filter((m) => isCitationGroup(m[1])).length;
    if (groups > 1) warnings.push(`第 ${u.start} 行有 ${groups} 组引用，规范为每段（列表项）最多 1 组`);
  }

  // 5. 附录 URL 与日期
  let communityGroup = false;
  const urlChecked = { total: 0, bare: 0 };
  const bareUrls = new Map();
  const communityBare = new Set();
  for (const line of appendixLines) {
    const h = line.match(/^###\s+(.+?)\s*$/);
    if (h) communityGroup = /社区|讨论|评价/.test(h[1]);
    if (!/^\s*[-*]\s+/.test(line)) continue;
    const urls = [...line.matchAll(URL_RE)].map((m) => m[0]);
    if (!urls.length) continue;
    urlChecked.total += urls.length;
    for (const url of urls) {
      const kind = urlKind(url);
      if (kind === 'content') continue;
      urlChecked.bare += 1;
      bareUrls.set(`${kind}|${url}`, (bareUrls.get(`${kind}|${url}`) || 0) + 1);
      if (communityGroup) communityBare.add(`${kind}|${url}`);
    }
    if (communityGroup && !DATE_RE.test(line) && !DATE_MISSING_RE.test(line)) {
      warnings.push(`社区条目缺发布时间且未写「发布时间未获取」: ${line.trim().slice(0, 60)}`);
    }
  }
  for (const key of communityBare) {
    const [kind, url] = key.split('|');
    const label = kind === 'search' ? '搜索页' : '站点首页';
    errors.push(`附录条目指向${label}，社区证据必须是具体内容页: ${url}`);
  }
  for (const [key, count] of bareUrls) {
    const [kind, url] = key.split('|');
    if (communityBare.has(key)) continue;
    const label = kind === 'search' ? '搜索页' : '站点首页';
    warnings.push(
      `附录条目指向${label}: ${url}${count > 1 ? `（${count} 次）` : ''}（官方首页可接受，但确保结论确实来自该页）`
    );
  }
  info.urls = urlChecked;

  // 6. 表格
  let tableRows = 0;
  let tableViolations = 0;
  bodyLines.forEach((line, i) => {
    if (!/^\s*\|/.test(line)) return;
    const raw = line.trim();
    if (/^\|(?:\s*:?-{2,}:?\s*\|)+\s*$/.test(raw)) return;
    const cells = raw.replace(/^\|/, '').replace(/\|$/, '').split('|').map((c) => c.trim());
    tableRows += 1;
    if (cells.length > 5) {
      tableViolations += 1;
      warnings.push(`第 ${i + 1} 行表格有 ${cells.length} 列（上限 5）`);
    }
    for (const c of cells) {
      if (c.length > 25) {
        tableViolations += 1;
        warnings.push(`第 ${i + 1} 行单元格 ${c.length} 字（上限 25）: ${c.slice(0, 30)}`);
        break;
      }
    }
  });
  info.tables = { rows: tableRows, violations: tableViolations };

  // 7. 图片
  let imageCount = 0;
  for (const line of bodyLines) {
    for (const m of line.matchAll(/!\[([^\]]*)\]\(([^)\s]+)(?:\s+"[^"]*")?\)/g)) {
      imageCount += 1;
      const alt = m[1] || '';
      const target = m[2];
      if (/占位|placeholder|todo|\.\.\./i.test(alt) || /占位|placeholder|todo/i.test(target)) {
        errors.push(`疑似占位图片: ${target}`);
        continue;
      }
      if (/^https?:\/\//i.test(target)) continue;
      const abs = path.resolve(path.dirname(reportPath), decodeURIComponent(target));
      if (!fs.existsSync(abs)) errors.push(`图片不存在: ${target}（解析为 ${abs}）`);
    }
  }
  if (imageCount > 3) warnings.push(`正文配图 ${imageCount} 张（上限 3）`);
  info.images = imageCount;

  // 8. 证据文件交叉核对
  if (evidencePaths.length) {
    const evidenceIds = new Set();
    const notFrozen = [];
    for (const f of evidencePaths) {
      let t;
      try {
        t = fs.readFileSync(f, 'utf8');
      } catch (err) {
        errors.push(`无法读取证据文件 ${f}: ${err.message}`);
        continue;
      }
      for (const m of t.matchAll(/^\s*(?:-\s*)?evidence_id\s*:\s*([a-z][a-z0-9_]*-\d+)/gm)) {
        evidenceIds.add(m[1]);
      }
      const st = t.match(/^\s*status\s*:\s*(\w+)/m);
      if (!st || st[1] !== 'complete') notFrozen.push(f);
    }
    info.evidenceIds = evidenceIds.size;
    const notInEvidence = [...appendixIds].filter((id) => !evidenceIds.has(id));
    if (notInEvidence.length) {
      errors.push(`附录有 ${notInEvidence.length} 条编号在证据文件中找不到: ${notInEvidence.slice(0, 10).join(', ')}`);
    }
    const title = (text.match(/^#\s+(.+)$/m) || [, ''])[1];
    if (notFrozen.length && !/部分完成/.test(title)) {
      errors.push(`证据文件未冻结（${notFrozen.length} 个不是 status: complete），报告标题也未标注「部分完成」`);
    }
  }

  // 9. 体量（仅供参考）
  const bodyText = bodyLines.join('\n');
  info.cjkChars = (bodyText.match(/[\u4e00-\u9fa5]/g) || []).length;

  const ok = errors.length === 0 && (!strict || warnings.length === 0);
  return { ok, errors, warnings, info };
}

function warnKind(msg) {
  if (/单元格 \d+ 字/.test(msg)) return 'cell-too-long';
  if (/表格有 \d+ 列/.test(msg)) return 'table-too-many-cols';
  if (/用 \[id\] 标注/.test(msg)) return 'legacy-bracket';
  if (/用（.*）标注/.test(msg)) return 'legacy-paren';
  if (/缺发布时间/.test(msg)) return 'missing-date';
  if (/组引用/.test(msg)) return 'citation-density';
  if (/未在正文引用/.test(msg)) return 'unused-ids';
  if (/附录条目指向/.test(msg)) return msg;
  return msg;
}

function summarizeWarnings(list) {
  const groups = new Map();
  for (const w of list) {
    const k = warnKind(w);
    if (!groups.has(k)) groups.set(k, []);
    groups.get(k).push(w);
  }
  const out = [];
  const tails = {
    'cell-too-long': '单元格超过 25 字',
    'table-too-many-cols': '表格超过 5 列',
    'legacy-bracket': '旧式 [id] 引用',
    'legacy-paren': '旧式（）引用',
    'missing-date': '社区条目缺发布时间',
    'citation-density': '段落引用过密',
    'unused-ids': '附录条目未被引用',
  };
  for (const [k, arr] of groups) {
    out.push(...arr.slice(0, 3));
    if (arr.length > 3) out.push(`（同类另有 ${arr.length - 3} 条${tails[k] ? `：${tails[k]}` : ''}）`);
  }
  return out;
}

function main() {
  const { report, evidence, flags } = parseArgs(process.argv.slice(2));
  if (flags.help) {
    console.log(USAGE);
    process.exit(0);
  }
  if (!report) {
    console.error(USAGE);
    process.exit(2);
  }

  const result = check(report, evidence, flags.strict);

  if (flags.json) {
    console.log(JSON.stringify({ report, ...result }, null, 2));
  } else {
    console.log(`[${result.ok ? 'PASS' : 'FAIL'}] ${report}`);
    console.log(`  章节: ${(result.info.sections || []).join(' / ') || '(无)'}`);
    if (result.info.appendixIds !== undefined) {
      console.log(`  附录编号: ${result.info.appendixIds} 条，正文引用: ${result.info.citedIds} 个，分组: ${(result.info.groups || []).join('；')}`);
    }
    if (result.info.urls) console.log(`  附录 URL: ${result.info.urls.total} 个，其中首页/搜索页 ${result.info.urls.bare} 个`);
    if (result.info.tables) console.log(`  表格: ${result.info.tables.rows} 行，越界 ${result.info.tables.violations} 处`);
    if (result.info.images !== undefined) console.log(`  正文配图: ${result.info.images} 张`);
    if (result.info.evidenceIds !== undefined) console.log(`  证据文件编号: ${result.info.evidenceIds} 条`);
    if (result.info.cjkChars !== undefined) console.log(`  正文汉字: ${result.info.cjkChars}（不含附录，仅供参考）`);
    for (const e of result.errors) console.log(`  - 错误: ${e}`);
    if (result.warnings.length) console.log(`  - 警告共 ${result.warnings.length} 条:`);
    for (const w of summarizeWarnings(result.warnings)) console.log(`    · ${w}`);
    console.log(
      result.ok
        ? `\n结论: 脚本门禁通过（${result.warnings.length} 条警告）。仍需人工事实抽查 5 条。`
        : `\n结论: 脚本门禁未通过（${result.errors.length} 个错误，${result.warnings.length} 条警告）。`
    );
  }

  process.exit(result.ok ? 0 : 1);
}

main();
