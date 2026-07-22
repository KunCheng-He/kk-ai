/**
 * Headless subagent execution via `pi --mode json -p`.
 *
 * Spawns a separate `pi` process with JSON output mode,
 * collecting messages until the process exits.
 */

import { spawn } from "node:child_process";
import { randomUUID } from "node:crypto";
import { writeFile, mkdir, unlink, rmdir } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import type { Message } from "@earendil-works/pi-ai";
import { getRunDir, writeRunArtifacts } from "./report.ts";
import type {
  AgentDefinition,
  Backend,
  SubagentResult,
  UsageStats,
} from "./types.ts";

// ─── helpers ──────────────────────────────────────────────

const EMPTY_USAGE: UsageStats = {
  input: 0,
  output: 0,
  cacheRead: 0,
  cacheWrite: 0,
  cost: 0,
  contextTokens: 0,
  turns: 0,
};

/**
 * Get the final assistant text from messages array.
 */
export function getFinalOutput(messages: Message[]): string {
  for (let i = messages.length - 1; i >= 0; i--) {
    const msg = messages[i];
    if (msg.role === "assistant") {
      for (const part of msg.content) {
        if (part.type === "text") return part.text;
      }
    }
  }
  return "";
}

/**
 * Build the full system prompt for a subagent.
 */
export function buildAgentSystemPrompt(
  agent: AgentDefinition,
  runInfo?: { workDir: string },
): string {
  const outputContract = [
    "# Output Contract",
    "Your FINAL message is the ONLY content returned to the parent agent.",
    "",
    "- If the answer is short and simple, just answer directly in your final",
    "  message. Do NOT write any report files.",
    "- If the deliverable is substantial (e.g. a research report, long",
    "  analysis, or multi-part documentation), write the complete deliverable",
    ...(runInfo
      ? [
          `  to a markdown file inside your scratch directory: ${runInfo.workDir}/`,
          `  (e.g. ${runInfo.workDir}/report.md),`,
        ]
      : ["  to a markdown file,"]),
    "  then make your final message a concise summary of it PLUS the report",
    "  file path, so the parent can read the full report only if needed.",
    "",
    "Either way: do not dump raw logs or full file contents into the final",
    "message; keep it self-contained and to the point.",
  ];

  return [
    `You are pi subagent '${agent.displayName}'.`,
    agent.description
      ? `Agent description: ${agent.description}`
      : undefined,
    "You are running as an isolated child session.",
    "Do not spawn subagents or delegate to other child agents.",
    "Do not assume parent conversation history unless provided in the task.",
    "",
    ...outputContract,
    "",
    "# Agent Definition",
    agent.systemPrompt.trim(),
  ]
    .filter((line): line is string => line !== undefined)
    .join("\n")
    .trim();
}

/**
 * Resolve the pi binary path.
 */
function getPiCommand(): string {
  // Check for PI_BIN override
  if (process.env.PI_BIN) return process.env.PI_BIN;
  return "pi";
}

// ─── execution ────────────────────────────────────────────

export interface RunOptions {
  agent: AgentDefinition;
  task: string;
  cwd?: string;
  backend?: Backend;
  signal?: AbortSignal;
  timeoutMs?: number;
  /** Stream partial results as the run progresses (for live TUI updates) */
  onUpdate?: (partial: SubagentResult) => void;
}

/**
 * Execute a single subagent via headless pi process.
 */
export async function runSubagent(options: RunOptions): Promise<SubagentResult> {
  const { agent, task, cwd = process.cwd(), signal, timeoutMs } = options;

  const runId = `run-${Date.now()}-${randomUUID().slice(0, 8)}`;
  const workDir = getRunDir(runId, agent.name);
  await mkdir(workDir, { recursive: true });

  // -ne: no extensions (subagent doesn't need them, avoids conflicts)
  // -p: print mode (single-shot prompt/response)
  const args: string[] = ["-ne", "--mode", "json", "-p", "--no-session"];

  // Model override
  if (agent.model) {
    args.push("--model", agent.model);
  }

  // Tool allowlist
  if (agent.tools && agent.tools.length > 0) {
    args.push("--tools", agent.tools.join(","));
  } else {
    // Default: read-only + bash
    args.push("--tools", "read,bash,grep,find,ls,edit,write");
  }

  // Thinking level
  if (agent.thinking) {
    args.push("--thinking", agent.thinking);
  }

  // Write system prompt to temp file and pass it
  const tmpDir = await mkdtempSafe(join(tmpdir(), "k-subagent-"));
  const promptFile = join(tmpDir, "system-prompt.md");
  const systemPrompt = buildAgentSystemPrompt(agent, { workDir });
  await writeFile(promptFile, systemPrompt, "utf-8");
  args.push("--append-system-prompt", promptFile);

  // Task as the prompt
  args.push(`Task: ${task}`);

  const result: SubagentResult = {
    runId,
    agentName: agent.name,
    agentSource: agent.source,
    task,
    backend: options.backend ?? "headless",
    exitCode: 0,
    messages: [],
    stderr: "",
    usage: { ...EMPTY_USAGE },
    model: agent.model,
    startedAt: Date.now(),
    workDir,
  };

  const emitUpdate = () => options.onUpdate?.(result);

  try {
    result.exitCode = await new Promise<number>((resolve, reject) => {
      const piCmd = getPiCommand();
      const proc = spawn(piCmd, args, {
        cwd,
        shell: false,
        stdio: ["ignore", "pipe", "pipe"],
      });

      let buffer = "";

      const processLine = (line: string) => {
        if (!line.trim()) return;
        let event: any;
        try {
          event = JSON.parse(line);
        } catch {
          return;
        }

        // Track messages
        if (
          (event.type === "message_end" || event.type === "tool_result_end") &&
          event.message
        ) {
          const msg = event.message as Message;
          result.messages.push(msg);

          if (msg.role === "assistant") {
            result.usage.turns++;
            const usage = msg.usage;
            if (usage) {
              result.usage.input += usage.input || 0;
              result.usage.output += usage.output || 0;
              result.usage.cacheRead += usage.cacheRead || 0;
              result.usage.cacheWrite += usage.cacheWrite || 0;
              result.usage.cost += usage.cost?.total || 0;
              result.usage.contextTokens = usage.totalTokens || 0;
            }
            if (!result.model && msg.model) result.model = msg.model;
            if (msg.stopReason) result.stopReason = msg.stopReason;
            if (msg.errorMessage) result.errorMessage = msg.errorMessage;
          }
          emitUpdate();
        }
      };

      proc.stdout.on("data", (data: Buffer) => {
        buffer += data.toString();
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";
        for (const line of lines) processLine(line);
      });

      proc.stderr.on("data", (data: Buffer) => {
        result.stderr += data.toString();
      });

      proc.on("close", (code) => {
        if (buffer.trim()) processLine(buffer);
        resolve(code ?? 0);
      });

      proc.on("error", (err) => {
        result.stderr += `Process error: ${err.message}\n`;
        resolve(1);
      });

      // Timeout
      let timeoutTimer: ReturnType<typeof setTimeout> | undefined;
      if (timeoutMs && timeoutMs > 0) {
        timeoutTimer = setTimeout(() => {
          proc.kill("SIGTERM");
          setTimeout(() => {
            if (!proc.killed) proc.kill("SIGKILL");
          }, 5000);
        }, timeoutMs);
      }

      // AbortSignal
      if (signal) {
        const onAbort = () => {
          proc.kill("SIGTERM");
          setTimeout(() => {
            if (!proc.killed) proc.kill("SIGKILL");
          }, 5000);
        };
        if (signal.aborted) {
          onAbort();
        } else {
          signal.addEventListener("abort", onAbort, { once: true });
        }
      }

      proc.on("close", () => {
        if (timeoutTimer) clearTimeout(timeoutTimer);
      });
    });
    result.endedAt = Date.now();

    // Persist the execution transcript (best effort). This is an internal
    // artifact: it powers the TUI drill-down (Ctrl+O / /subagents) — it is
    // NOT the deliverable report the subagent may choose to write itself.
    try {
      const { transcriptPath } = await writeRunArtifacts(result);
      result.transcriptPath = transcriptPath;
    } catch {
      // Best effort — transcriptPath stays undefined
    }
    emitUpdate();
  } finally {
    // Cleanup temp files
    try {
      await unlink(promptFile);
      await rmdir(tmpDir);
    } catch {
      // Best effort
    }
  }

  return result;
}

/**
 * Run multiple subagents in parallel with concurrency limit.
 */
export async function runParallel(
  tasks: Array<{ agent: AgentDefinition; task: string; cwd?: string }>,
  options: {
    cwd?: string;
    signal?: AbortSignal;
    concurrency?: number;
    failFast?: boolean;
    cancelSiblingsOnFailure?: boolean;
    /** Per-task streaming updates: (taskIndex, partialResult) */
    onTaskUpdate?: (index: number, partial: SubagentResult) => void;
  } = {},
): Promise<{
  results: SubagentResult[];
  skippedCount: number;
  failFastTriggered: boolean;
}> {
  const {
    cwd = process.cwd(),
    signal,
    concurrency = 4,
    failFast = false,
    cancelSiblingsOnFailure = false,
    onTaskUpdate,
  } = options;

  const limit = Math.max(1, Math.min(concurrency, tasks.length));
  const results: SubagentResult[] = new Array(tasks.length);
  let nextIndex = 0;
  let failed = false;
  let skippedCount = 0;
  let failFastTriggered = false;

  const controller = new AbortController();
  const combinedSignal = controller.signal;

  if (signal) {
    if (signal.aborted) controller.abort();
    else signal.addEventListener("abort", () => controller.abort(), { once: true });
  }

  const workers = new Array(limit).fill(null).map(async () => {
    while (true) {
      if (combinedSignal.aborted) return;

      const current = nextIndex++;
      if (current >= tasks.length) return;
      if (failed && (failFast || cancelSiblingsOnFailure)) {
        skippedCount++;
        results[current] = {
          runId: `run-skipped-${current}`,
          agentName: tasks[current].agent.name,
          agentSource: tasks[current].agent.source,
          task: tasks[current].task,
          backend: "headless",
          exitCode: -1,
          messages: [],
          stderr: "Skipped (fail-fast)",
          usage: { ...EMPTY_USAGE },
          startedAt: Date.now(),
          endedAt: Date.now(),
        };
        continue;
      }

      const result = await runSubagent({
        agent: tasks[current].agent,
        task: tasks[current].task,
        cwd: tasks[current].cwd ?? cwd,
        signal: combinedSignal,
        onUpdate: onTaskUpdate
          ? (partial) => onTaskUpdate(current, partial)
          : undefined,
      });

      results[current] = result;

      if (result.exitCode !== 0 || result.stopReason === "error") {
        if (failFast || cancelSiblingsOnFailure) {
          failed = true;
          failFastTriggered = true;
          if (cancelSiblingsOnFailure) controller.abort();
        }
      }
    }
  });

  await Promise.all(workers);

  return { results, skippedCount, failFastTriggered };
}

// ─── utils ────────────────────────────────────────────────

async function mkdtempSafe(prefix: string): Promise<string> {
  const dir = `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
  await mkdir(dir, { recursive: true });
  return dir;
}
