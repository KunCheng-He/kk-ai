/**
 * Per-run artifacts. Every subagent run gets a shallow scratch directory:
 *
 *   /tmp/k-subagent/<runId>-<agent>/
 *     transcript.md  — full execution transcript (internal; powers the
 *                      Ctrl+O expanded view and the /subagents browser)
 *     messages.json  — raw message array (full fidelity)
 *
 * The subagent may additionally write its own deliverables (e.g. a
 * research report.md) into the same directory — those are authored by
 * the subagent, not auto-generated, and are what the main agent is
 * pointed at when the subagent chooses to produce a report.
 */

import { readFileSync } from "node:fs";
import { mkdir, writeFile } from "node:fs/promises";
import { join } from "node:path";
import type { Message } from "@earendil-works/pi-ai";
import type { SubagentResult, UsageStats } from "./types.ts";

// ─── caps ─────────────────────────────────────────────────

/** Max chars per tool result inside transcript.md */
const TOOL_RESULT_REPORT_CAP = 20_000;
/** Max chars for serialized tool call arguments inside transcript.md */
const TOOL_ARGS_REPORT_CAP = 8_000;
/** Max chars per thinking block inside transcript.md */
const THINKING_REPORT_CAP = 8_000;

// ─── helpers ──────────────────────────────────────────────

/** Root directory for all run scratch dirs (shallow, user-visible). */
export function getRunsRoot(): string {
  return "/tmp/k-subagent";
}

/** Scratch directory for a single run. */
export function getRunDir(runId: string, agentName: string): string {
  const safeAgent = agentName.replace(/[^\w.-]+/g, "_");
  return join(getRunsRoot(), `${runId}-${safeAgent}`);
}

function truncateTail(text: string, cap: number): string {
  if (text.length <= cap) return text;
  const omitted = text.length - cap;
  return `${text.slice(0, cap)}\n\n[... ${omitted} chars omitted — see messages.json for full content]`;
}

function formatTokens(count: number): string {
  if (count < 1000) return count.toString();
  if (count < 10_000) return `${(count / 1000).toFixed(1)}k`;
  if (count < 1_000_000) return `${Math.round(count / 1000)}k`;
  return `${(count / 1_000_000).toFixed(1)}M`;
}

export function formatUsageLine(usage: UsageStats, model?: string): string {
  const parts: string[] = [];
  if (usage.turns) parts.push(`${usage.turns} turn${usage.turns > 1 ? "s" : ""}`);
  if (usage.input) parts.push(`input ${formatTokens(usage.input)}`);
  if (usage.output) parts.push(`output ${formatTokens(usage.output)}`);
  if (usage.cacheRead) parts.push(`cache-read ${formatTokens(usage.cacheRead)}`);
  if (usage.cacheWrite) parts.push(`cache-write ${formatTokens(usage.cacheWrite)}`);
  if (usage.cost) parts.push(`$${usage.cost.toFixed(4)}`);
  if (model) parts.push(`model ${model}`);
  return parts.join(", ");
}

export function formatDurationMs(startedAt: number, endedAt?: number): string {
  if (!endedAt) return "(running)";
  const ms = endedAt - startedAt;
  if (ms < 1000) return `${ms}ms`;
  if (ms < 60_000) return `${(ms / 1000).toFixed(1)}s`;
  return `${Math.floor(ms / 60_000)}m${Math.round((ms % 60_000) / 1000)}s`;
}

function messageText(content: unknown): string {
  if (typeof content === "string") return content;
  if (!Array.isArray(content)) return "";
  return content
    .filter((p: any) => p?.type === "text")
    .map((p: any) => p.text as string)
    .join("\n");
}

// ─── markdown transcript ──────────────────────────────────

export function buildMarkdownTranscript(result: SubagentResult): string {
  const lines: string[] = [];
  const status =
    result.exitCode !== 0 ||
    result.stopReason === "error" ||
    result.stopReason === "aborted"
      ? "failed"
      : "completed";

  lines.push(`# Subagent Transcript: ${result.agentName}`);
  lines.push("");
  lines.push(`- **Run ID**: ${result.runId}`);
  lines.push(`- **Agent**: ${result.agentName} (${result.agentSource})`);
  lines.push(`- **Status**: ${status}${result.stopReason ? ` (stopReason: ${result.stopReason})` : ""}`);
  lines.push(`- **Exit code**: ${result.exitCode}`);
  if (result.errorMessage) lines.push(`- **Error**: ${result.errorMessage}`);
  lines.push(`- **Started**: ${new Date(result.startedAt).toISOString()}`);
  if (result.endedAt) {
    lines.push(`- **Ended**: ${new Date(result.endedAt).toISOString()}`);
    lines.push(`- **Duration**: ${formatDurationMs(result.startedAt, result.endedAt)}`);
  }
  const usageLine = formatUsageLine(result.usage, result.model);
  if (usageLine) lines.push(`- **Usage**: ${usageLine}`);
  lines.push("");
  lines.push("---");
  lines.push("");
  lines.push("## Task");
  lines.push("");
  lines.push(result.task);
  lines.push("");
  lines.push("---");
  lines.push("");
  lines.push("## Transcript");
  lines.push("");

  let step = 0;
  for (const msg of result.messages) {
    if (msg.role === "user") {
      lines.push("### 👤 User");
      lines.push("");
      lines.push(messageText(msg.content) || "(empty)");
      lines.push("");
      continue;
    }

    if (msg.role === "toolResult") {
      const text = truncateTail(messageText(msg.content), TOOL_RESULT_REPORT_CAP);
      lines.push(
        `#### ⎿ Tool result: ${msg.toolName}${msg.isError ? " (error)" : ""}`,
      );
      lines.push("");
      lines.push("```");
      lines.push(text || "(empty)");
      lines.push("```");
      lines.push("");
      continue;
    }

    // assistant
    for (const part of msg.content) {
      if (part.type === "text") {
        lines.push("### 🤖 Assistant");
        lines.push("");
        lines.push(part.text);
        lines.push("");
      } else if (part.type === "thinking") {
        lines.push("### 💭 Thinking");
        lines.push("");
        lines.push(truncateTail(part.thinking, THINKING_REPORT_CAP));
        lines.push("");
      } else if (part.type === "toolCall") {
        step++;
        lines.push(`#### 🔧 Step ${step}: ${part.name}`);
        lines.push("");
        lines.push("```json");
        lines.push(
          truncateTail(
            JSON.stringify(part.arguments, null, 2) ?? "{}",
            TOOL_ARGS_REPORT_CAP,
          ),
        );
        lines.push("```");
        lines.push("");
      }
    }
  }

  if (result.stderr.trim()) {
    lines.push("---");
    lines.push("");
    lines.push("## Stderr");
    lines.push("");
    lines.push("```");
    lines.push(truncateTail(result.stderr.trim(), TOOL_RESULT_REPORT_CAP));
    lines.push("```");
    lines.push("");
  }

  lines.push("---");
  lines.push("");
  lines.push(
    `*Raw messages are stored in \`messages.json\` next to this report.*`,
  );
  lines.push("");

  return lines.join("\n");
}

// ─── persistence ──────────────────────────────────────────

/**
 * Write transcript.md + messages.json for a finished (or aborted) run
 * into its scratch directory. Returns the locations; throws on IO
 * failure (caller should catch).
 */
export async function writeRunArtifacts(
  result: SubagentResult,
): Promise<{ workDir: string; transcriptPath: string }> {
  const workDir = result.workDir ?? getRunDir(result.runId, result.agentName);
  await mkdir(workDir, { recursive: true });

  const transcriptPath = join(workDir, "transcript.md");
  await writeFile(transcriptPath, buildMarkdownTranscript(result), "utf-8");
  await writeFile(
    join(workDir, "messages.json"),
    JSON.stringify(result.messages, null, 2),
    "utf-8",
  );

  return { workDir, transcriptPath };
}

/**
 * Load raw messages from a run's scratch directory (for rendering
 * transcripts of runs that are no longer in memory). Returns null when
 * unavailable.
 */
export function loadRunMessages(workDir?: string): Message[] | null {
  if (!workDir) return null;
  try {
    const raw = readFileSync(join(workDir, "messages.json"), "utf-8");
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? (parsed as Message[]) : null;
  } catch {
    return null;
  }
}
