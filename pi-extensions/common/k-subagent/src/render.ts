/**
 * Shared TUI rendering helpers: turn subagent messages into styled
 * transcript lines for the expanded tool result and the /subagents viewer.
 */

import { homedir } from "node:os";
import type { Message } from "@earendil-works/pi-ai";
import type { SubagentResult, UsageStats } from "./types.ts";
import { formatDurationMs } from "./report.ts";

// Minimal theme surface we rely on (structurally compatible with pi themes)
export interface RenderTheme {
  fg(color: any, text: string): string;
  bold(text: string): string;
  italic?(text: string): string;
}

// ─── display items ────────────────────────────────────────

export type DisplayItem =
  | { type: "userText"; text: string }
  | { type: "text"; text: string }
  | { type: "thinking"; text: string }
  | { type: "toolCall"; name: string; args: Record<string, any> }
  | { type: "toolResult"; toolName: string; text: string; isError: boolean };

export function getDisplayItems(messages: Message[]): DisplayItem[] {
  const items: DisplayItem[] = [];
  for (const msg of messages) {
    if (msg.role === "user") {
      const text =
        typeof msg.content === "string"
          ? msg.content
          : msg.content
              .filter((p: any) => p?.type === "text")
              .map((p: any) => p.text as string)
              .join("\n");
      if (text.trim()) items.push({ type: "userText", text });
      continue;
    }
    if (msg.role === "toolResult") {
      const text = msg.content
        .filter((p: any) => p?.type === "text")
        .map((p: any) => p.text as string)
        .join("\n");
      items.push({
        type: "toolResult",
        toolName: msg.toolName,
        text,
        isError: Boolean(msg.isError),
      });
      continue;
    }
    // assistant
    for (const part of msg.content) {
      if (part.type === "text") {
        items.push({ type: "text", text: part.text });
      } else if (part.type === "thinking") {
        items.push({ type: "thinking", text: part.thinking });
      } else if (part.type === "toolCall") {
        items.push({
          type: "toolCall",
          name: part.name,
          args: (part.arguments ?? {}) as Record<string, any>,
        });
      }
    }
  }
  return items;
}

// ─── formatting ───────────────────────────────────────────

export function shortenPath(p: string): string {
  const home = homedir();
  return p.startsWith(home) ? `~${p.slice(home.length)}` : p;
}

export function formatTokens(count: number): string {
  if (count < 1000) return count.toString();
  if (count < 10_000) return `${(count / 1000).toFixed(1)}k`;
  if (count < 1_000_000) return `${Math.round(count / 1000)}k`;
  return `${(count / 1_000_000).toFixed(1)}M`;
}

export function formatUsageStats(usage: UsageStats, model?: string): string {
  const parts: string[] = [];
  if (usage.turns) parts.push(`${usage.turns} turn${usage.turns > 1 ? "s" : ""}`);
  if (usage.input) parts.push(`↑${formatTokens(usage.input)}`);
  if (usage.output) parts.push(`↓${formatTokens(usage.output)}`);
  if (usage.cacheRead) parts.push(`R${formatTokens(usage.cacheRead)}`);
  if (usage.cacheWrite) parts.push(`W${formatTokens(usage.cacheWrite)}`);
  if (usage.cost) parts.push(`$${usage.cost.toFixed(4)}`);
  if (usage.contextTokens && usage.contextTokens > 0) {
    parts.push(`ctx:${formatTokens(usage.contextTokens)}`);
  }
  if (model) parts.push(model);
  return parts.join(" ");
}

export function formatToolCall(
  toolName: string,
  args: Record<string, unknown>,
  fg: (color: any, text: string) => string,
): string {
  switch (toolName) {
    case "bash": {
      const command = (args.command as string) || "...";
      const preview =
        command.length > 60 ? `${command.slice(0, 60)}...` : command;
      return fg("muted", "$ ") + fg("toolOutput", preview);
    }
    case "read": {
      const rawPath = (args.file_path || args.path || "...") as string;
      const filePath = shortenPath(rawPath);
      const offset = args.offset as number | undefined;
      const limit = args.limit as number | undefined;
      let text = fg("accent", filePath);
      if (offset !== undefined || limit !== undefined) {
        const startLine = offset ?? 1;
        const endLine = limit !== undefined ? startLine + limit - 1 : "";
        text += fg("warning", `:${startLine}${endLine ? `-${endLine}` : ""}`);
      }
      return fg("muted", "read ") + text;
    }
    case "write": {
      const rawPath = (args.file_path || args.path || "...") as string;
      const content = (args.content || "") as string;
      const lines = content.split("\n").length;
      let text = fg("muted", "write ") + fg("accent", shortenPath(rawPath));
      if (lines > 1) text += fg("dim", ` (${lines} lines)`);
      return text;
    }
    case "edit": {
      const rawPath = (args.file_path || args.path || "...") as string;
      return fg("muted", "edit ") + fg("accent", shortenPath(rawPath));
    }
    case "ls": {
      const rawPath = (args.path || ".") as string;
      return fg("muted", "ls ") + fg("accent", shortenPath(rawPath));
    }
    case "find": {
      const pattern = (args.pattern || "*") as string;
      const rawPath = (args.path || ".") as string;
      return (
        fg("muted", "find ") +
        fg("accent", pattern) +
        fg("dim", ` in ${shortenPath(rawPath)}`)
      );
    }
    case "grep": {
      const pattern = (args.pattern || "") as string;
      const rawPath = (args.path || ".") as string;
      return (
        fg("muted", "grep ") +
        fg("accent", `/${pattern}/`) +
        fg("dim", ` in ${shortenPath(rawPath)}`)
      );
    }
    default: {
      const argsStr = JSON.stringify(args);
      const preview =
        argsStr.length > 50 ? `${argsStr.slice(0, 50)}...` : argsStr;
      return fg("accent", toolName) + fg("dim", ` ${preview}`);
    }
  }
}

// ─── transcript lines ─────────────────────────────────────

export interface TranscriptOptions {
  /** Max lines shown per tool result (default 12) */
  toolResultLineLimit?: number;
  /** Max lines shown per thinking block (default 6) */
  thinkingLineLimit?: number;
  /** Max lines shown per user text (default 20) */
  userTextLineLimit?: number;
}

/**
 * Convert subagent messages into styled transcript lines (ANSI-styled,
 * unwrapped — caller wraps/truncates to width).
 */
export function buildTranscriptLines(
  messages: Message[],
  theme: RenderTheme,
  opts: TranscriptOptions = {},
): string[] {
  const resultLineLimit = opts.toolResultLineLimit ?? 12;
  const thinkingLineLimit = opts.thinkingLineLimit ?? 6;
  const userLineLimit = opts.userTextLineLimit ?? 20;

  const lines: string[] = [];
  const items = getDisplayItems(messages);

  const pushCapped = (
    text: string,
    limit: number,
    style: (s: string) => string,
  ) => {
    const textLines = text.split("\n");
    const shown = textLines.slice(0, limit);
    for (const l of shown) lines.push(style(l));
    if (textLines.length > limit) {
      lines.push(
        theme.fg("dim", `  … (${textLines.length - limit} more lines)`),
      );
    }
  };

  for (const item of items) {
    if (item.type === "userText") {
      lines.push(theme.fg("muted", "─── User ───"));
      pushCapped(item.text, userLineLimit, (s) => theme.fg("dim", s));
      lines.push("");
    } else if (item.type === "thinking") {
      lines.push(theme.fg("muted", "💭 thinking:"));
      pushCapped(item.text, thinkingLineLimit, (s) => theme.fg("dim", s));
      lines.push("");
    } else if (item.type === "text") {
      for (const l of item.text.split("\n")) {
        lines.push(theme.fg("toolOutput", l));
      }
      lines.push("");
    } else if (item.type === "toolCall") {
      lines.push(
        theme.fg("muted", "→ ") +
          formatToolCall(item.name, item.args, theme.fg.bind(theme)),
      );
    } else {
      // toolResult
      const resultLines = item.text.split("\n");
      const shown = resultLines.slice(0, resultLineLimit);
      const style = item.isError
        ? (s: string) => theme.fg("error", s)
        : (s: string) => theme.fg("dim", s);
      for (let i = 0; i < shown.length; i++) {
        lines.push(`${theme.fg("muted", i === 0 ? "  ⎿ " : "    ")}${style(shown[i]!)}`);
      }
      if (resultLines.length > resultLineLimit) {
        lines.push(
          theme.fg(
            "dim",
            `    … (${resultLines.length - resultLineLimit} more lines in report)`,
          ),
        );
      }
      lines.push("");
    }
  }

  // Trim trailing blank lines
  while (lines.length > 0 && lines[lines.length - 1] === "") lines.pop();
  return lines;
}

/**
 * Header lines describing a run (agent, status, timing, usage, report path).
 */
export function buildRunHeaderLines(
  result: Pick<
    SubagentResult,
    | "agentName"
    | "agentSource"
    | "task"
    | "runId"
    | "usage"
    | "model"
    | "startedAt"
    | "endedAt"
    | "transcriptPath"
    | "stopReason"
    | "errorMessage"
  > & { failed: boolean; running?: boolean },
  theme: RenderTheme,
): string[] {
  const icon = result.running
    ? theme.fg("warning", "⏳")
    : result.failed
      ? theme.fg("error", "✗")
      : theme.fg("success", "✓");
  const lines: string[] = [];
  let header = `${icon} ${theme.fg("toolTitle", theme.bold(result.agentName))}${theme.fg("muted", ` (${result.agentSource})`)}`;
  if (result.failed && result.stopReason)
    header += ` ${theme.fg("error", `[${result.stopReason}]`)}`;
  lines.push(header);
  if (result.failed && result.errorMessage)
    lines.push(theme.fg("error", `Error: ${result.errorMessage}`));
  lines.push(theme.fg("muted", "Task: ") + theme.fg("dim", result.task));
  const usage = formatUsageStats(result.usage, result.model);
  const duration = formatDurationMs(result.startedAt, result.endedAt);
  lines.push(
    theme.fg("dim", [usage, duration].filter(Boolean).join(" · ")),
  );
  if (result.transcriptPath)
    lines.push(
      theme.fg("dim", `Transcript: ${shortenPath(result.transcriptPath)}`),
    );
  return lines;
}
