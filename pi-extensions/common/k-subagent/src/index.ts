/**
 * k-subagent — A subagent extension for pi.
 *
 * Subagent definitions live in:
 *   - Global:  ~/.pi/agent/k-subagents/
 *   - Project: .pi/k-subagents/
 *
 * Each subagent runs in a separate headless pi process with an isolated
 * context window. Subagents either answer directly (simple tasks) or write
 * a deliverable report into their scratch dir (/tmp/k-subagent/<runId>-<agent>/)
 * and return a summary plus the report path (substantial tasks). The main
 * agent decides whether it needs to read the full report.
 *
 * In the TUI, subagent calls can be expanded (Ctrl+O) to reveal the full
 * execution transcript, and the /subagents command opens an interactive
 * browser to click into any run's complete execution process.
 */

import { join } from "node:path";
import { randomUUID } from "node:crypto";
import { Type } from "typebox";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { getAgentDir, keyHint } from "@earendil-works/pi-coding-agent";
import { Container, Spacer, Text } from "@earendil-works/pi-tui";
import type { Message, Usage } from "@earendil-works/pi-ai";
import { discoverAgents, formatAgentList } from "./agents.ts";
import { runSubagent, runParallel, getFinalOutput } from "./runner.ts";
import { loadRunMessages } from "./report.ts";
import {
  buildTranscriptLines,
  formatUsageStats,
  shortenPath,
} from "./render.ts";
import { registerSubagentsCommand } from "./viewer.ts";
import type {
  AgentDefinition,
  AgentRegistry,
  AgentScope,
  RunRecord,
  SubagentResult,
  SubagentRunSummary,
  SubagentToolDetails,
  UsageStats,
} from "./types.ts";

// ─── constants ────────────────────────────────────────────

const TOOL_NAME = "subagent";
const MAX_PARALLEL_TASKS = 8;
const DEFAULT_CONCURRENCY = 4;

/** Max chars of the subagent's final output returned inline (single mode) */
const SUMMARY_CAP_SINGLE = 12_000;
/** Max chars per task returned inline (parallel mode) */
const SUMMARY_CAP_PARALLEL = 6_000;
/** How many runs the /subagents viewer remembers */
const MAX_HISTORY = 50;
/** How many recent runs keep full messages in memory */
const MAX_FULL_RESULTS = 10;

const AGENT_SCOPES = ["global", "project", "both"] as const;
const EXECUTION_MODES = ["single", "parallel"] as const;
const ON_COMPLETE_ACTIONS = ["return", "notify", "detach"] as const;

const EMPTY_USAGE: UsageStats = {
  input: 0,
  output: 0,
  cacheRead: 0,
  cacheWrite: 0,
  cost: 0,
  contextTokens: 0,
  turns: 0,
};

// ─── helpers ──────────────────────────────────────────────

function textResult(
  text: string,
  isError = false,
  details?: unknown,
  usage?: Usage,
) {
  return {
    content: [{ type: "text" as const, text }],
    details,
    isError,
    usage,
  };
}

function isFailedResult(r: {
  exitCode: number;
  stopReason?: string;
}): boolean {
  return (
    r.exitCode !== 0 || r.stopReason === "error" || r.stopReason === "aborted"
  );
}

function getResultOutput(r: SubagentResult): string {
  if (isFailedResult(r)) {
    return (
      r.errorMessage || r.stderr || getFinalOutput(r.messages) || "(no output)"
    );
  }
  return getFinalOutput(r.messages) || "(no output)";
}

function makeSummary(r: SubagentResult, cap: number): SubagentRunSummary {
  const output = getResultOutput(r);
  const running = r.endedAt === undefined;
  return {
    runId: r.runId,
    agentName: r.agentName,
    agentSource: r.agentSource,
    task: r.task,
    status: running ? "running" : isFailedResult(r) ? "failed" : "completed",
    exitCode: r.exitCode,
    stopReason: r.stopReason,
    errorMessage: r.errorMessage,
    model: r.model,
    usage: r.usage,
    summary: output.length > cap ? output.slice(0, cap) : output,
    summaryTruncated: output.length > cap,
    workDir: r.workDir,
    transcriptPath: r.transcriptPath,
    startedAt: r.startedAt,
    endedAt: r.endedAt,
  };
}

/**
 * What the main agent sees: the subagent's final message (its answer or
 * its summary + report path when it chose to write a report). We never
 * point the main agent at the internal execution transcript — except as
 * a fallback when the final message had to be truncated.
 */
function formatRunForLLM(s: SubagentRunSummary): string {
  const icon = s.status === "completed" ? "✅" : "❌";
  const duration = s.endedAt
    ? `, ${((s.endedAt - s.startedAt) / 1000).toFixed(1)}s`
    : "";
  const lines: string[] = [];
  lines.push(
    `${icon} Subagent "${s.agentName}" ${s.status}` +
      (s.status === "failed" && s.stopReason ? ` [${s.stopReason}]` : "") +
      ` — ${s.usage.turns} turns, ${s.usage.input} in / ${s.usage.output} out, $${s.usage.cost.toFixed(4)}${duration}`,
  );
  lines.push("");
  lines.push(s.summary.trim() || "(no output)");
  if (s.summaryTruncated) {
    lines.push("");
    lines.push(
      `[Output truncated.${s.transcriptPath ? ` Full final output available at: ${s.transcriptPath}` : ""}]`,
    );
  }
  return lines.join("\n");
}

/** Aggregate nested LLM usage for pi's session accounting. */
function toUsage(u: UsageStats): Usage | undefined {
  if (!u.turns && !u.input && !u.output) return undefined;
  return {
    input: u.input,
    output: u.output,
    cacheRead: u.cacheRead,
    cacheWrite: u.cacheWrite,
    totalTokens:
      u.contextTokens || u.input + u.output + u.cacheRead + u.cacheWrite,
    cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0, total: u.cost },
  };
}

function aggregateUsage(results: SubagentResult[]): UsageStats {
  const total = { ...EMPTY_USAGE };
  for (const r of results) {
    total.input += r.usage.input;
    total.output += r.usage.output;
    total.cacheRead += r.usage.cacheRead;
    total.cacheWrite += r.usage.cacheWrite;
    total.cost += r.usage.cost;
    total.turns += r.usage.turns;
  }
  return total;
}

// ─── tool parameter schema ────────────────────────────────

const TaskItemSchema = Type.Object({
  agent: Type.String({ description: "Name of the subagent to invoke" }),
  task: Type.String({ description: "Task to delegate" }),
  cwd: Type.Optional(Type.String({ description: "Working directory override" })),
});

const SubagentParams = Type.Object({
  // Single mode
  agent: Type.Optional(Type.String({ description: "Name of the subagent (single mode)" })),
  task: Type.Optional(Type.String({ description: "Task to delegate (single mode)" })),

  // Parallel mode
  tasks: Type.Optional(
    Type.Array(TaskItemSchema, {
      description: "Array of {agent, task} for parallel execution",
    }),
  ),

  // Options
  agentScope: Type.Optional(
    Type.Union(AGENT_SCOPES.map((s) => Type.Literal(s)), {
      default: "both",
      description: "Where to discover agents",
    }),
  ),
  cwd: Type.Optional(Type.String({ description: "Working directory override" })),
  concurrency: Type.Optional(
    Type.Number({
      minimum: 1,
      description: `Max parallel executions. Default: ${DEFAULT_CONCURRENCY}`,
    }),
  ),
  failFast: Type.Optional(
    Type.Boolean({
      description: "Stop scheduling after first failure",
    }),
  ),
  cancelSiblingsOnFailure: Type.Optional(
    Type.Boolean({
      description: "Abort running siblings after first failure. Implies failFast.",
    }),
  ),

  // Async
  async: Type.Optional(Type.Boolean({ description: "Run async, return immediately" })),
  onComplete: Type.Optional(
    Type.Union(ON_COMPLETE_ACTIONS.map((a) => Type.Literal(a)), {
      description: "Async completion action",
    }),
  ),

  // Lifecycle actions
  action: Type.Optional(
    Type.Union(
      [
        Type.Literal("run"),
        Type.Literal("status"),
        Type.Literal("logs"),
        Type.Literal("wait"),
        Type.Literal("interrupt"),
      ],
      {
        default: "run",
        description: "Action: run (default), status, logs, wait, or interrupt",
      },
    ),
  ),
  runId: Type.Optional(Type.String({ description: "Run ID for lifecycle actions" })),

  // Other
  timeoutMs: Type.Optional(Type.Number({ exclusiveMinimum: 0 })),
  reason: Type.Optional(Type.String({ description: "Reason for interrupt" })),
});

// ─── extension ────────────────────────────────────────────

export default function kSubagent(pi: ExtensionAPI) {
  // ── state ──────────────────────────────────────────────

  let registry: AgentRegistry = {
    agents: [],
    globalDir: join(getAgentDir(), "k-subagents"),
    projectDir: null,
  };

  /** Run history for the /subagents viewer (most recent first) */
  const runHistory: RunRecord[] = [];

  // Track running async subagents
  const running = new Map<
    string,
    {
      result: Promise<SubagentResult>;
      abort: () => void;
    }
  >();

  function recordRun(result: SubagentResult, cap: number): SubagentRunSummary {
    const summary = makeSummary(result, cap);
    const existing = runHistory.findIndex(
      (h) => h.summary.runId === result.runId,
    );
    if (existing >= 0) runHistory.splice(existing, 1);
    runHistory.unshift({ summary, result });
    // Keep full messages only for the most recent runs
    for (let i = MAX_FULL_RESULTS; i < runHistory.length; i++) {
      runHistory[i]!.result = undefined;
    }
    if (runHistory.length > MAX_HISTORY) runHistory.length = MAX_HISTORY;
    return summary;
  }

  // ── agent discovery ────────────────────────────────────

  async function refreshAgents(cwd: string) {
    registry = await discoverAgents(cwd, "both");
  }

  function findAgent(name: string): AgentDefinition | undefined {
    return registry.agents.find((a) => a.name === name);
  }

  // ── /subagents viewer command ──────────────────────────

  registerSubagentsCommand(pi, () => runHistory);

  // ── system prompt injection ────────────────────────────

  pi.on("before_agent_start", async (event, ctx) => {
    const cwd = ctx.cwd;
    await refreshAgents(cwd);

    if (registry.agents.length === 0) return;

    const agentListSection = [
      "",
      "## Available Subagents",
      "",
      "You have access to the following subagents via the `subagent` tool.",
      "Use them to delegate complex, isolated tasks. Each subagent runs in a separate",
      "process with its own context window.",
      "",
      formatAgentList(registry.agents),
      "",
      "**When to use subagents:**",
      "- Complex multi-step tasks that benefit from isolated context",
      "- Parallel independent investigations or analyses",
      "- Tasks requiring a specific model or tool configuration",
      "- When the user explicitly asks you to delegate",
      "",
      "**Usage:** Call `subagent` with `{ agent: \"name\", task: \"...\" }`.",
      "For parallel tasks, use `{ tasks: [{ agent: \"...\", task: \"...\" }, ...] }`.",
      "",
      "**Results:** Subagents either return their answer directly, or — for",
      "substantial deliverables — write a report file and return a summary plus",
      "the report path. In the latter case, read the report file (with the `read`",
      "tool) only if the summary is not enough.",
    ].join("\n");

    const currentPrompt = event.systemPrompt || ctx.getSystemPrompt?.() || "";

    return {
      systemPrompt: currentPrompt + agentListSection,
    };
  });

  // ── register tool ──────────────────────────────────────

  pi.registerTool({
    name: TOOL_NAME,
    label: "Subagent",
    description: [
      "Delegate tasks to specialized subagents with isolated context windows.",
      "Modes: single (agent + task), parallel (tasks array).",
      "Subagents run headless (separate pi process). Simple tasks return the",
      "answer directly; substantial deliverables are written to a report file",
      "by the subagent, which returns a summary plus the report path — read",
      "the report only if the summary is not enough.",
      "See system prompt for available subagents and their descriptions.",
    ].join(" "),
    promptSnippet: "Delegate a task to a specialized subagent with isolated context",
    promptGuidelines: [
      "Use subagent to delegate complex, isolated tasks to specialized agents.",
      "For parallel independent tasks, use tasks[] array instead of multiple single calls.",
      "Each subagent runs in a separate process — do not rely on shared state between them.",
      "When the subagent tool result mentions a report path, read that report file only if the returned summary lacks detail you need.",
    ],
    parameters: SubagentParams,

    async execute(_toolCallId, params, signal, onUpdate, ctx) {
      const cwd = params.cwd ?? ctx.cwd;
      const scope: AgentScope = params.agentScope ?? "both";

      // Refresh agent list
      await refreshAgents(cwd);

      // ── lifecycle actions ────────────────────────────

      const action = params.action ?? "run";
      if (action !== "run") {
        const runId = params.runId;
        if (!runId) {
          return textResult("Lifecycle actions require a runId.", true);
        }
        const tracked = running.get(runId);
        if (!tracked) {
          return textResult(`No tracked run with id: ${runId}`, true);
        }

        if (action === "status") {
          return textResult(
            `Run ${runId}: pending. Use the subagent tool to track completion.`,
          );
        }
        if (action === "logs") {
          return textResult(
            `Run ${runId}: logs not available for headless backend.`,
          );
        }
        if (action === "wait") {
          try {
            const result = await tracked.result;
            running.delete(runId);
            const summary = recordRun(result, SUMMARY_CAP_SINGLE);
            return textResult(
              formatRunForLLM(summary),
              isFailedResult(result),
              { mode: "single", runs: [summary] } satisfies SubagentToolDetails,
              toUsage(result.usage),
            );
          } catch (err) {
            return textResult(
              `Run ${runId} failed: ${err instanceof Error ? err.message : String(err)}`,
              true,
            );
          }
        }
        if (action === "interrupt") {
          tracked.abort();
          running.delete(runId);
          return textResult(`Run ${runId} interrupted.`);
        }
      }

      // ── execute ────────────────────────────────────────

      // Determine mode
      const hasTasks = (params.tasks?.length ?? 0) > 0;
      const hasSingle = Boolean(params.agent && params.task);
      const modeCount = Number(hasTasks) + Number(hasSingle);

      if (modeCount !== 1) {
        const available = registry.agents
          .map((a) => `${a.name}: ${a.description}`)
          .join(", ") || "none";
        return textResult(
          `Provide exactly one mode: (agent + task) or tasks[]. Available agents: ${available}`,
          true,
        );
      }

      const isAsync =
        params.async === true ||
        params.onComplete === "detach" ||
        params.onComplete === "notify";

      // ── single mode ───────────────────────────────────

      if (hasSingle) {
        const agent = findAgent(params.agent!);
        if (!agent) {
          const available = registry.agents.map((a) => a.name).join(", ") || "none";
          return textResult(
            `Unknown subagent: "${params.agent}". Available: ${available}`,
            true,
          );
        }

        if (isAsync) {
          // Async: launch and track
          const abortController = new AbortController();
          const runId = `subagent-${Date.now()}-${randomUUID().slice(0, 8)}`;
          const resultPromise = runSubagent({
            agent,
            task: params.task!,
            cwd: params.cwd ?? cwd,
            signal: abortController.signal,
            timeoutMs: params.timeoutMs,
          });

          running.set(runId, {
            result: resultPromise,
            abort: () => abortController.abort(),
          });

          // Record completion for the viewer, then clean up tracking
          resultPromise
            .then((r) => recordRun(r, SUMMARY_CAP_SINGLE))
            .catch(() => {})
            .finally(() => {
              if (running.get(runId)?.result === resultPromise) {
                running.delete(runId);
              }
            });

          return textResult(
            `Async subagent started: ${runId}\nAgent: ${agent.name}\nTask: ${params.task}`,
            false,
            { runId, agent: agent.name, task: params.task, mode: "single" },
          );
        }

        // Sync (with live progress streaming)
        const result = await runSubagent({
          agent,
          task: params.task!,
          cwd: params.cwd ?? cwd,
          signal,
          timeoutMs: params.timeoutMs,
          onUpdate: onUpdate
            ? (partial) => {
                onUpdate({
                  content: [
                    {
                      type: "text",
                      text:
                        getFinalOutput(partial.messages) ||
                        `(subagent "${agent.name}" running…)`,
                    },
                  ],
                  details: {
                    mode: "single",
                    runs: [makeSummary(partial, SUMMARY_CAP_SINGLE)],
                    live: [partial],
                  } satisfies SubagentToolDetails,
                });
              }
            : undefined,
        });

        const summary = recordRun(result, SUMMARY_CAP_SINGLE);
        const details: SubagentToolDetails = {
          mode: "single",
          runs: [summary],
        };

        return textResult(
          formatRunForLLM(summary),
          isFailedResult(result),
          details,
          toUsage(result.usage),
        );
      }

      // ── parallel mode ─────────────────────────────────

      if (hasTasks) {
        if (params.tasks!.length > MAX_PARALLEL_TASKS) {
          return textResult(
            `Too many tasks (${params.tasks!.length}). Max: ${MAX_PARALLEL_TASKS}`,
            true,
          );
        }

        const resolvedTasks: Array<{ agent: AgentDefinition; task: string; cwd: string }> = [];
        for (const t of params.tasks!) {
          const agent = findAgent(t.agent);
          if (!agent) {
            const available = registry.agents.map((a) => a.name).join(", ") || "none";
            return textResult(
              `Unknown subagent: "${t.agent}". Available: ${available}`,
              true,
            );
          }
          resolvedTasks.push({
            agent,
            task: t.task,
            cwd: t.cwd ?? params.cwd ?? cwd,
          });
        }

        // Live progress aggregation
        const liveResults: (SubagentResult | undefined)[] = new Array(
          resolvedTasks.length,
        );
        const emitParallelUpdate = onUpdate
          ? (index: number, partial: SubagentResult) => {
              liveResults[index] = partial;
              const present = liveResults.filter(
                (r): r is SubagentResult => Boolean(r),
              );
              const doneCount = present.filter((r) => r.endedAt).length;
              onUpdate({
                content: [
                  {
                    type: "text",
                    text: `Parallel: ${doneCount}/${resolvedTasks.length} done…`,
                  },
                ],
                details: {
                  mode: "parallel",
                  runs: present.map((r) =>
                    makeSummary(r, SUMMARY_CAP_PARALLEL),
                  ),
                  live: present,
                } satisfies SubagentToolDetails,
              });
            }
          : undefined;

        const { results, skippedCount, failFastTriggered } = await runParallel(
          resolvedTasks,
          {
            cwd,
            signal,
            concurrency: params.concurrency ?? DEFAULT_CONCURRENCY,
            failFast: params.failFast ?? false,
            cancelSiblingsOnFailure:
              params.cancelSiblingsOnFailure ?? false,
            onTaskUpdate: emitParallelUpdate,
          },
        );

        const summaries = results.map((r) =>
          recordRun(r, SUMMARY_CAP_PARALLEL),
        );
        const successCount = summaries.filter(
          (s) => s.status === "completed",
        ).length;

        const details: SubagentToolDetails = {
          mode: "parallel",
          runs: summaries,
          skippedCount,
          failFastTriggered,
        };

        const content = [
          `Parallel: ${successCount}/${results.length} succeeded${skippedCount > 0 ? `, ${skippedCount} skipped` : ""}`,
          "",
          ...summaries.map((s) => formatRunForLLM(s)),
        ].join("\n\n");

        return textResult(
          content,
          successCount < results.length,
          details,
          toUsage(aggregateUsage(results)),
        );
      }

      return textResult("Invalid parameters.", true);
    },

    // ── custom rendering ───────────────────────────────────

    renderCall(args, theme) {
      const title = theme.fg("toolTitle", theme.bold("subagent"));
      if (args.tasks && Array.isArray(args.tasks)) {
        const taskList = args.tasks as Array<{ agent: string; task: string }>;
        let text = `${title} ${theme.fg("accent", `parallel (${taskList.length})`)}`;
        for (const t of taskList.slice(0, 3)) {
          const preview =
            typeof t.task === "string" && t.task.length > 40
              ? `${t.task.slice(0, 40)}...`
              : String(t.task ?? "");
          text += `\n  ${theme.fg("accent", t.agent)} ${theme.fg("dim", preview)}`;
        }
        if (taskList.length > 3)
          text += `\n  ${theme.fg("muted", `... +${taskList.length - 3} more`)}`;
        return new Text(text, 0, 0);
      }
      const agent = (args.agent as string) || "...";
      const task = args.task as string | undefined;
      const preview = task
        ? task.length > 60
          ? `${task.slice(0, 60)}...`
          : task
        : "...";
      return new Text(
        `${title} ${theme.fg("accent", agent)}\n  ${theme.fg("dim", preview)}`,
        0,
        0,
      );
    },

    renderResult(result, { expanded, isPartial }, theme, _context) {
      const details = result.details as SubagentToolDetails | undefined;
      if (!details || !Array.isArray(details.runs) || details.runs.length === 0) {
        const content = result.content?.[0] as
          | { type: "text"; text: string }
          | undefined;
        return new Text(content?.text ?? "(no output)", 0, 0);
      }

      const resolveMessages = (run: SubagentRunSummary): Message[] | null => {
        const live = details.live?.find((r) => r.runId === run.runId);
        if (live) return live.messages;
        const rec = runHistory.find((h) => h.summary.runId === run.runId);
        if (rec?.result) return rec.result.messages;
        return loadRunMessages(run.workDir);
      };

      const runIcon = (run: SubagentRunSummary) =>
        run.status === "running"
          ? theme.fg("warning", "⏳")
          : run.status === "failed"
            ? theme.fg("error", "✗")
            : theme.fg("success", "✓");

      const runHeader = (run: SubagentRunSummary) => {
        let text = `${runIcon(run)} ${theme.fg("toolTitle", theme.bold(run.agentName))}${theme.fg("muted", ` (${run.agentSource})`)}`;
        if (run.status === "failed" && run.stopReason)
          text += ` ${theme.fg("error", `[${run.stopReason}]`)}`;
        if (run.status === "running") text += ` ${theme.fg("warning", "running…")}`;
        return text;
      };

      const renderExpandedRun = (
        container: Container,
        run: SubagentRunSummary,
        messages: Message[] | null,
      ) => {
        container.addChild(new Text(runHeader(run), 0, 0));
        if (run.status === "failed" && run.errorMessage)
          container.addChild(
            new Text(theme.fg("error", `Error: ${run.errorMessage}`), 0, 0),
          );
        container.addChild(new Spacer(1));
        container.addChild(new Text(theme.fg("muted", "─── Task ───"), 0, 0));
        container.addChild(new Text(theme.fg("dim", run.task), 0, 0));
        container.addChild(new Spacer(1));

        if (messages && messages.length > 0) {
          const lines = buildTranscriptLines(messages, theme, {
            toolResultLineLimit: 15,
            thinkingLineLimit: 8,
          });
          if (lines.length > 0) {
            container.addChild(
              new Text(theme.fg("muted", "─── Execution ───"), 0, 0),
            );
            container.addChild(new Text(lines.join("\n"), 0, 0));
          }
        } else {
          container.addChild(
            new Text(
              theme.fg("dim", "(transcript unavailable in this session)"),
              0,
              0,
            ),
          );
        }

        container.addChild(new Spacer(1));
        const usage = formatUsageStats(run.usage, run.model);
        if (usage) container.addChild(new Text(theme.fg("dim", usage), 0, 0));
        if (run.transcriptPath)
          container.addChild(
            new Text(
              theme.fg("dim", `Transcript: ${shortenPath(run.transcriptPath)}`),
              0,
              0,
            ),
          );
      };

      // ── single mode ──
      if (details.mode === "single" && details.runs.length === 1) {
        const run = details.runs[0]!;
        const messages = resolveMessages(run);

        if (expanded) {
          const container = new Container();
          renderExpandedRun(container, run, messages);
          return container;
        }

        // Collapsed: header + summary preview + report path + hint
        let text = runHeader(run);
        if (run.status === "failed" && run.errorMessage) {
          text += `\n${theme.fg("error", `Error: ${run.errorMessage}`)}`;
        } else {
          const previewSource =
            run.summary.trim() ||
            (run.status === "running" ? "(working…)" : "(no output)");
          const preview = previewSource
            .split("\n")
            .slice(0, 3)
            .join("\n");
          text += `\n${theme.fg("toolOutput", preview)}`;
        }
        const usage = formatUsageStats(run.usage, run.model);
        if (usage) text += `\n${theme.fg("dim", usage)}`;
        if (run.transcriptPath)
          text += `\n${theme.fg("dim", `📄 ${shortenPath(run.transcriptPath)}`)}`;
        if (!isPartial) {
          text += `\n${theme.fg("muted", `(${keyHint("app.tools.expand", "to expand")} · /subagents to browse)`)}`;
        }
        return new Text(text, 0, 0);
      }

      // ── parallel mode ──
      const successCount = details.runs.filter(
        (r) => r.status === "completed",
      ).length;
      const runningCount = details.runs.filter(
        (r) => r.status === "running",
      ).length;
      const icon =
        runningCount > 0
          ? theme.fg("warning", "⏳")
          : successCount === details.runs.length
            ? theme.fg("success", "✓")
            : theme.fg("warning", "◐");

      const statusLine = `${icon} ${theme.fg("toolTitle", theme.bold("parallel "))}${theme.fg("accent", `${successCount}/${details.runs.length}`)}${runningCount > 0 ? theme.fg("warning", ` (${runningCount} running)`) : ""}`;

      if (expanded) {
        const container = new Container();
        container.addChild(new Text(statusLine, 0, 0));
        if (details.skippedCount && details.skippedCount > 0)
          container.addChild(
            new Text(
              theme.fg("muted", `(${details.skippedCount} skipped)`),
              0,
              0,
            ),
          );
        for (const run of details.runs) {
          container.addChild(new Spacer(1));
          renderExpandedRun(container, run, resolveMessages(run));
        }
        return container;
      }

      let text = statusLine;
      if (details.skippedCount && details.skippedCount > 0)
        text += theme.fg("muted", ` (${details.skippedCount} skipped)`);
      for (const run of details.runs) {
        text += `\n\n${runHeader(run)}`;
        const preview = (run.summary.trim() || "(no output)")
          .split("\n")
          .slice(0, 2)
          .join("\n");
        text += `\n${theme.fg("toolOutput", preview)}`;
      }
      if (!isPartial) {
        text += `\n${theme.fg("muted", `(${keyHint("app.tools.expand", "to expand")} · /subagents to browse)`)}`;
      }
      return new Text(text, 0, 0);
    },
  });

  // ── session start: initial discovery + reset history ───

  pi.on("session_start", async (_event, ctx) => {
    runHistory.length = 0;
    await refreshAgents(ctx.cwd);
  });
}
