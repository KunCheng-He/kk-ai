/**
 * /subagents — interactive browser for subagent runs.
 *
 * Opens an overlay listing all runs of this session; selecting one opens
 * a scrollable full-transcript view (the "click into the subagent"
 * experience), similar to opencode's subagent drill-down.
 */

import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { DynamicBorder } from "@earendil-works/pi-coding-agent";
import {
  Container,
  Key,
  SelectList,
  Spacer,
  Text,
  matchesKey,
  truncateToWidth,
  visibleWidth,
  wrapTextWithAnsi,
  type SelectItem,
} from "@earendil-works/pi-tui";
import { loadRunMessages } from "./report.ts";
import {
  buildRunHeaderLines,
  buildTranscriptLines,
  formatTokens,
  shortenPath,
  type RenderTheme,
} from "./render.ts";
import type { RunRecord, SubagentRunSummary } from "./types.ts";

// ─── helpers ──────────────────────────────────────────────

function statusIcon(run: SubagentRunSummary): string {
  if (run.status === "running") return "⏳";
  return run.status === "completed" ? "✓" : "✗";
}

function runLabel(run: SubagentRunSummary): string {
  const task =
    run.task.length > 50 ? `${run.task.slice(0, 50)}…` : run.task;
  return `${statusIcon(run)} ${run.agentName} — ${task.replace(/\n/g, " ")}`;
}

function runDescription(run: SubagentRunSummary): string {
  const time = new Date(run.startedAt).toLocaleTimeString();
  const parts = [time, run.status];
  if (run.usage.turns) parts.push(`${run.usage.turns} turns`);
  if (run.usage.output) parts.push(`↓${formatTokens(run.usage.output)}`);
  if (run.usage.cost) parts.push(`$${run.usage.cost.toFixed(4)}`);
  if (run.endedAt)
    parts.push(`${((run.endedAt - run.startedAt) / 1000).toFixed(1)}s`);
  return parts.join(" · ");
}

// ─── transcript detail view ───────────────────────────────

class TranscriptView {
  private scroll = 0;
  private bodyLines: string[];
  private headerLines: string[];
  private wrapCache: { width: number; lines: string[] } | null = null;

  constructor(
    private record: RunRecord,
    private theme: RenderTheme,
    private tui: any,
    private onBack: () => void,
    private onClose: () => void,
  ) {
    const run = record.summary;
    const result = record.result;

    const headerSource = result ?? {
      agentName: run.agentName,
      agentSource: run.agentSource,
      task: run.task,
      runId: run.runId,
      usage: run.usage,
      model: run.model,
      startedAt: run.startedAt,
      endedAt: run.endedAt,
      transcriptPath: run.transcriptPath,
      stopReason: run.stopReason,
      errorMessage: run.errorMessage,
    };

    this.headerLines = buildRunHeaderLines(
      {
        ...headerSource,
        failed: run.status === "failed",
        running: run.status === "running",
      },
      theme,
    );

    const messages =
      result?.messages ?? loadRunMessages(run.workDir) ?? null;

    if (messages && messages.length > 0) {
      this.bodyLines = buildTranscriptLines(messages, theme, {
        toolResultLineLimit: 40,
        thinkingLineLimit: 20,
        userTextLineLimit: 60,
      });
      if (run.status === "running") {
        this.bodyLines.push("");
        this.bodyLines.push(
          theme.fg("warning", "⏳ run still in progress (snapshot)"),
        );
      }
    } else if (run.status === "running") {
      this.bodyLines = [theme.fg("dim", "(run in progress — no output yet)")];
    } else {
      this.bodyLines = [
        theme.fg("dim", "(transcript unavailable — no report found on disk)"),
      ];
    }
  }

  private viewportHeight(): number {
    const rows = this.tui.terminal?.rows ?? 24;
    // border(1) + header(N) + separator(1) + bottom border(1) + help(1)
    return Math.max(4, rows - this.headerLines.length - 4);
  }

  private wrapped(width: number): string[] {
    const bodyWidth = Math.max(10, width - 2);
    if (this.wrapCache && this.wrapCache.width === bodyWidth) {
      return this.wrapCache.lines;
    }
    const lines: string[] = [];
    for (const line of this.bodyLines) {
      if (line === "") {
        lines.push("");
        continue;
      }
      lines.push(...wrapTextWithAnsi(line, bodyWidth));
    }
    this.wrapCache = { width: bodyWidth, lines };
    return lines;
  }

  handleInput(data: string): void {
    const page = this.viewportHeight();
    if (matchesKey(data, Key.escape) || matchesKey(data, Key.left)) {
      this.onBack();
      return;
    }
    if (data === "q") {
      this.onClose();
      return;
    }
    if (matchesKey(data, Key.up) || data === "k") this.scroll -= 1;
    else if (matchesKey(data, Key.down) || data === "j") this.scroll += 1;
    else if (matchesKey(data, "pageUp") || data === "u") this.scroll -= page;
    else if (matchesKey(data, "pageDown") || data === " ") this.scroll += page;
    else if (matchesKey(data, Key.home) || data === "g") this.scroll = 0;
    else if (matchesKey(data, Key.end) || data === "G")
      this.scroll = Number.MAX_SAFE_INTEGER;
  }

  render(width: number): string[] {
    const all = this.wrapped(width);
    const viewH = this.viewportHeight();
    const maxScroll = Math.max(0, all.length - viewH);
    this.scroll = Math.max(0, Math.min(this.scroll, maxScroll));

    const out: string[] = [];
    const border = (s: string) => this.theme.fg("accent", s);
    out.push(border("─".repeat(Math.max(1, width - 2))));

    for (const h of this.headerLines) {
      out.push(truncateToWidth(` ${h}`, width));
    }
    out.push(border("─".repeat(Math.max(1, width - 2))));

    const slice = all.slice(this.scroll, this.scroll + viewH);
    for (const line of slice) {
      out.push(truncateToWidth(` ${line}`, width));
    }
    // Pad to keep overlay height stable while scrolling
    for (let i = slice.length; i < viewH; i++) out.push("");

    out.push(border("─".repeat(Math.max(1, width - 2))));
    const pos = `${Math.min(this.scroll + 1, Math.max(all.length, 1))}-${Math.min(this.scroll + viewH, all.length)}/${all.length}`;
    const help = ` ↑↓/jk scroll · PgUp/PgDn · g/G top/bottom · esc back · q close  ${pos}`;
    out.push(truncateToWidth(this.theme.fg("dim", help), width));
    return out;
  }

  invalidate(): void {
    this.wrapCache = null;
  }
}

// ─── browser (list + detail) ──────────────────────────────

class SubagentBrowser {
  private mode: "list" | "detail";
  private selectList: SelectList;
  private detail: TranscriptView | null = null;
  private listContainer: Container;

  constructor(
    private records: RunRecord[],
    private theme: RenderTheme,
    private tui: any,
    private done: (value: null) => void,
    initialRunId?: string,
  ) {
    const items: SelectItem[] = records.map((r) => ({
      value: r.summary.runId,
      label: runLabel(r.summary),
      description: runDescription(r.summary),
    }));

    const termRows = tui.terminal?.rows ?? 24;
    this.selectList = new SelectList(
      items,
      Math.min(items.length, Math.max(5, termRows - 8)),
      {
      selectedPrefix: (t: string) => theme.fg("accent", t),
      selectedText: (t: string) => theme.fg("accent", t),
      description: (t: string) => theme.fg("muted", t),
      scrollInfo: (t: string) => theme.fg("dim", t),
      noMatch: (t: string) => theme.fg("warning", t),
      });
    this.selectList.onSelect = (item) => this.openDetail(item.value);
    this.selectList.onCancel = () => this.done(null);

    this.listContainer = new Container();
    this.listContainer.addChild(
      new DynamicBorder((s: string) => theme.fg("accent", s)),
    );
    this.listContainer.addChild(
      new Text(theme.fg("accent", theme.bold("Subagent runs")), 1, 0),
    );
    this.listContainer.addChild(this.selectList);
    this.listContainer.addChild(new Spacer(1));
    this.listContainer.addChild(
      new Text(
        theme.fg("dim", "↑↓ navigate · enter view transcript · esc close"),
        1,
        0,
      ),
    );
    this.listContainer.addChild(
      new DynamicBorder((s: string) => theme.fg("accent", s)),
    );

    this.mode = "list";
    if (initialRunId) {
      const found = records.find(
        (r) =>
          r.summary.runId === initialRunId ||
          r.summary.agentName === initialRunId,
      );
      if (found) this.openDetail(found.summary.runId);
    }
  }

  private openDetail(runId: string): void {
    const record = this.records.find((r) => r.summary.runId === runId);
    if (!record) return;
    this.detail = new TranscriptView(
      record,
      this.theme,
      this.tui,
      () => {
        this.mode = "list";
        this.detail = null;
        this.tui.requestRender();
      },
      () => this.done(null),
    );
    this.mode = "detail";
    this.tui.requestRender();
  }

  handleInput(data: string): void {
    if (this.mode === "list") {
      this.selectList.handleInput(data);
    } else {
      this.detail?.handleInput(data);
    }
    this.tui.requestRender();
  }

  render(width: number): string[] {
    const content =
      this.mode === "detail" && this.detail
        ? this.detail.render(width)
        : this.listContainer.render(width);
    // Fullscreen: pad to terminal height so the overlay covers the whole screen
    const target = this.tui.terminal?.rows ?? 24;
    const out = content.slice(0, target);
    while (out.length < target) out.push("");
    return out;
  }

  invalidate(): void {
    this.listContainer.invalidate();
    this.detail?.invalidate();
  }
}

// ─── command registration ─────────────────────────────────

export function registerSubagentsCommand(
  pi: ExtensionAPI,
  getRecords: () => RunRecord[],
): void {
  pi.registerCommand("subagents", {
    description:
      "Browse subagent runs and inspect full execution transcripts",
    getArgumentCompletions: (prefix) => {
      const items = getRecords()
        .slice(0, 20)
        .flatMap((r) => [
          { value: r.summary.runId, label: r.summary.runId, description: runLabel(r.summary) },
          { value: r.summary.agentName, label: r.summary.agentName },
        ]);
      const filtered = items.filter((i) => i.value.startsWith(prefix));
      return filtered.length > 0 ? filtered : null;
    },
    handler: async (args, ctx) => {
      if (ctx.mode !== "tui") {
        ctx.ui.notify(
          "/subagents is only available in interactive TUI mode",
          "warning",
        );
        return;
      }
      const records = getRecords();
      if (records.length === 0) {
        ctx.ui.notify("No subagent runs in this session yet", "info");
        return;
      }
      const query = args.trim() || undefined;
      const match = query
        ? records.find(
            (r) =>
              r.summary.runId === query || r.summary.agentName === query,
          )
        : undefined;

      await ctx.ui.custom<null>(
        (_tui, theme, _keybindings, done) =>
          new SubagentBrowser(
            records,
            theme,
            _tui,
            done,
            match?.summary.runId ?? query,
          ),
        {
          overlay: true,
          overlayOptions: {
            width: "100%",
            maxHeight: "100%",
            anchor: "top-left",
            margin: 0,
          },
        },
      );
    },
  });
}
