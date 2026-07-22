/**
 * k-subagent type definitions
 */

import type { Message } from "@earendil-works/pi-ai";

/** Where the subagent definition was loaded from */
export type AgentSource = "global" | "project";

/** Thinking level */
export type ThinkingLevel = "off" | "minimal" | "low" | "medium" | "high" | "xhigh";

/** Agent scope for discovery */
export type AgentScope = "global" | "project" | "both";

/** Execution backend */
export type Backend = "headless" | "tmux";

/** Execution mode */
export type ExecutionMode = "single" | "parallel";

/** Async completion action */
export type OnComplete = "return" | "notify" | "detach";

/** Async dependency classification */
export type AsyncDependency = "needed-before-final" | "background" | "unclassified";

/** Sandbox configuration */
export type SandboxInput = boolean | null | { allowedDomains?: string[] };

/** Workspace mode */
export type WorkspaceMode = "shared" | "worktree" | "auto";

/** Worktree policy */
export type WorktreePolicy = "auto" | "required" | "never";

/** Lifecycle action */
export type LifecycleAction = "run" | "status" | "logs" | "wait" | "interrupt" | "mark-background" | "reconcile";

/** Agent definition parsed from markdown file */
export interface AgentDefinition {
  name: string;
  displayName: string;
  description: string;
  source: AgentSource;
  sourcePath: string;
  /** The system prompt body (markdown after frontmatter) */
  systemPrompt: string;
  /** Optional model override (e.g. "anthropic/claude-sonnet-4-5") */
  model?: string;
  /** Optional thinking level override */
  thinking?: ThinkingLevel;
  /** Optional tool allowlist */
  tools?: string[];
  /** System prompt mode: "append" (default) or "replace" */
  systemPromptMode?: "append" | "replace";
}

/** Result from agent discovery */
export interface AgentRegistry {
  agents: AgentDefinition[];
  globalDir: string;
  projectDir: string | null;
}

/** Usage statistics from a subagent run */
export interface UsageStats {
  input: number;
  output: number;
  cacheRead: number;
  cacheWrite: number;
  cost: number;
  contextTokens: number;
  turns: number;
}

/** Run status */
export type RunStatus = "running" | "completed" | "failed";

/** Result of a single subagent invocation */
export interface SubagentResult {
  /** Unique run identifier */
  runId: string;
  agentName: string;
  agentSource: AgentSource;
  task: string;
  backend: Backend;
  exitCode: number;
  messages: Message[];
  stderr: string;
  usage: UsageStats;
  model?: string;
  stopReason?: string;
  errorMessage?: string;
  /** Epoch ms when the run started */
  startedAt: number;
  /** Epoch ms when the run finished */
  endedAt?: number;
  /** Scratch dir for this run (/tmp/k-subagent/<runId>-<agent>/); the
   *  subagent may write deliverables here, we store transcript artifacts */
  workDir?: string;
  /** Path to the auto-generated execution transcript (internal) */
  transcriptPath?: string;
}

/**
 * Lightweight per-run summary. This is what gets persisted in the tool
 * result `details` (and therefore in the session file) — full messages
 * are deliberately kept out to avoid bloating the session; they live in
 * the on-disk report instead.
 */
export interface SubagentRunSummary {
  runId: string;
  agentName: string;
  agentSource: AgentSource;
  task: string;
  status: RunStatus;
  exitCode: number;
  stopReason?: string;
  errorMessage?: string;
  model?: string;
  usage: UsageStats;
  /** Final output (possibly truncated) — the "summary" returned to the LLM */
  summary: string;
  summaryTruncated: boolean;
  workDir?: string;
  transcriptPath?: string;
  startedAt: number;
  endedAt?: number;
}

/** Tool result details */
export interface SubagentToolDetails {
  mode: ExecutionMode;
  /** Persisted summaries (safe for the session file) */
  runs: SubagentRunSummary[];
  /**
   * Full live results — only present in streaming (onUpdate) partial
   * results, never persisted. Used by renderers to show live progress.
   */
  live?: SubagentResult[];
  /** Number of skipped tasks (fail-fast) */
  skippedCount?: number;
  /** Whether fail-fast was triggered */
  failFastTriggered?: boolean;
}

/** In-memory record for the /subagents viewer */
export interface RunRecord {
  summary: SubagentRunSummary;
  /** Full result incl. messages — kept only for recent runs */
  result?: SubagentResult;
}
