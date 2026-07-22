/**
 * Subagent discovery and parsing.
 *
 * Reads agent definitions from:
 *   - Global:  ~/.pi/agent/k-subagents/
 *   - Project: .pi/k-subagents/
 *
 * Each subagent is a markdown file with YAML frontmatter:
 *
 * ```markdown
 * ---
 * name: my-agent
 * description: Does X and Y
 * model: anthropic/claude-sonnet-4-5
 * tools: read,bash,grep
 * ---
 *
 * System prompt body here...
 * ```
 *
 * - `name` (required): unique agent identifier
 * - `description` (required): what the agent does, shown to LLM
 * - `model` (optional): model override (provider/model format)
 * - `tools` (optional): comma-separated tool allowlist
 * - `thinking` (optional): thinking level override
 * - `systemPromptMode` (optional): "append" (default) or "replace"
 *
 * Nested directories create dotted names: `coding/review.md` → `coding.review`
 */

import { readdir, readFile, lstat, realpath } from "node:fs/promises";
import { homedir } from "node:os";
import {
  basename,
  dirname,
  isAbsolute,
  join,
  relative,
  resolve,
  sep,
} from "node:path";
import type {
  AgentDefinition,
  AgentRegistry,
  AgentScope,
  AgentSource,
  ThinkingLevel,
} from "./types.ts";

// ─── helpers ──────────────────────────────────────────────

function isInsideOrEqual(parent: string, child: string): boolean {
  const rel = relative(parent, child);
  return rel === "" || (!rel.startsWith("..") && !isAbsolute(rel));
}

function optionalString(value: unknown): string | undefined {
  return typeof value === "string" && value.trim().length > 0
    ? value.trim()
    : undefined;
}

const THINKING_LEVELS: readonly string[] = [
  "off", "minimal", "low", "medium", "high", "xhigh",
];

function thinkingValue(value: unknown): ThinkingLevel | undefined {
  return typeof value === "string" && THINKING_LEVELS.includes(value)
    ? (value as ThinkingLevel)
    : undefined;
}

function toolsValue(value: unknown): string[] | undefined {
  const raw = Array.isArray(value)
    ? value
    : typeof value === "string"
      ? value.split(",")
      : [];
  const tools = raw
    .map((t) => (typeof t === "string" ? t.trim() : ""))
    .filter(Boolean);
  return tools.length > 0 ? tools : undefined;
}

function toDottedName(p: string): string {
  return p.split(sep).join(".");
}

// ─── YAML frontmatter parsing ─────────────────────────────

function stripQuotes(value: string): string {
  const trimmed = value.trim();
  if (
    (trimmed.startsWith('"') && trimmed.endsWith('"')) ||
    (trimmed.startsWith("'") && trimmed.endsWith("'"))
  ) {
    return trimmed.slice(1, -1);
  }
  return trimmed;
}

function parseScalar(value: string): unknown {
  const stripped = stripQuotes(value.trim());
  if (stripped === "true") return true;
  if (stripped === "false") return false;
  const numeric = Number(stripped);
  if (
    stripped.length > 0 &&
    Number.isFinite(numeric) &&
    /^-?\d+(?:\.\d+)?$/.test(stripped)
  )
    return numeric;
  return stripped;
}

function parseSimpleYaml(yaml: string): Record<string, unknown> {
  const result: Record<string, unknown> = {};
  let currentListKey: string | undefined;

  for (const rawLine of yaml.split(/\r?\n/)) {
    const line = rawLine.trim();
    if (line.length === 0 || line.startsWith("#")) continue;

    const listItem = rawLine.match(/^\s+-\s*(.*)$/);
    if (listItem) {
      if (!currentListKey || !Array.isArray(result[currentListKey])) continue;
      (result[currentListKey] as string[]).push(
        stripQuotes(listItem[1]!.trim()),
      );
      continue;
    }

    if (/^\s/.test(rawLine)) continue;

    const match = line.match(/^([A-Za-z0-9_-]+):\s*(.*)$/);
    if (!match) continue;

    const key = match[1]!;
    const rawValue = match[2] ?? "";
    if (rawValue.trim() === "") {
      result[key] = [];
      currentListKey = key;
      continue;
    }
    currentListKey = undefined;
    result[key] = parseScalar(rawValue);
  }
  return result;
}

function splitFrontmatter(markdown: string): {
  frontmatter: Record<string, unknown>;
  body: string;
} {
  if (!markdown.startsWith("---"))
    return { frontmatter: {}, body: markdown };
  const lines = markdown.split(/\r?\n/);
  if (lines[0]?.trim() !== "---")
    return { frontmatter: {}, body: markdown };
  const end = lines.findIndex(
    (line, index) => index > 0 && line.trim() === "---",
  );
  if (end === -1) return { frontmatter: {}, body: markdown };
  return {
    frontmatter: parseSimpleYaml(lines.slice(1, end).join("\n")),
    body: lines
      .slice(end + 1)
      .join("\n")
      .trim(),
  };
}

// ─── discovery ────────────────────────────────────────────

async function findProjectAgentsDir(
  cwd: string,
): Promise<string | null> {
  let current = resolve(cwd);
  while (true) {
    const candidate = join(current, ".pi", "k-subagents");
    try {
      const info = await lstat(candidate);
      if (info.isDirectory() || info.isSymbolicLink()) return candidate;
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code !== "ENOENT") throw error;
    }

    // Stop at git root
    try {
      const gitDir = join(current, ".git");
      const gitInfo = await lstat(gitDir);
      if (gitInfo.isDirectory() || gitInfo.isFile() || gitInfo.isSymbolicLink())
        return null;
    } catch {
      // no .git
    }

    const parent = dirname(current);
    if (parent === current) return null;
    current = parent;
  }
}

async function listMarkdownFiles(
  root: string,
): Promise<string[]> {
  try {
    const entries = await readdir(root, { withFileTypes: true });
    const nested = await Promise.all(
      entries.map(async (entry) => {
        const fullPath = join(root, entry.name);
        if (entry.isDirectory())
          return await listMarkdownFiles(fullPath);
        if (
          (entry.isFile() || entry.isSymbolicLink()) &&
          entry.name.endsWith(".md")
        )
          return [fullPath];
        return [];
      }),
    );
    return nested.flat();
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === "ENOENT") return [];
    throw error;
  }
}

async function parseAgentFile(
  filePath: string,
  root: string,
  source: AgentSource,
): Promise<AgentDefinition> {
  const realFile = await realpath(filePath);
  const realRoot = await realpath(root);

  if (!isInsideOrEqual(realRoot, realFile))
    throw new Error(`Agent symlink escapes root: ${filePath}`);

  const markdown = await readFile(realFile, "utf8");
  const { frontmatter, body } = splitFrontmatter(markdown);

  const fileName = basename(filePath, ".md");
  const relName = toDottedName(relative(root, filePath).replace(/\.md$/, ""));
  const name = optionalString(frontmatter.name) ?? fileName;
  const displayName = relName || name;

  const description = optionalString(frontmatter.description) ?? "";

  if (!description) {
    // Warn but don't reject — the agent just won't be very useful
  }

  return {
    name,
    displayName,
    description,
    source,
    sourcePath: filePath,
    systemPrompt: body,
    model: optionalString(frontmatter.model),
    thinking: thinkingValue(frontmatter.thinking),
    tools: toolsValue(frontmatter.tools),
    systemPromptMode: optionalString(frontmatter.systemPromptMode) as
      | "append"
      | "replace"
      | undefined,
  };
}

// ─── public API ───────────────────────────────────────────

/**
 * Discover all subagent definitions from global and project directories.
 */
export async function discoverAgents(
  cwd: string,
  scope: AgentScope = "both",
): Promise<AgentRegistry> {
  const globalDir = join(homedir(), ".pi", "agent", "k-subagents");
  const projectDir =
    scope !== "global" ? await findProjectAgentsDir(cwd) : null;

  const agents: AgentDefinition[] = [];
  const seenNames = new Set<string>();

  const loadFrom = async (
    dir: string,
    source: AgentSource,
  ) => {
    const files = await listMarkdownFiles(dir);
    for (const file of files) {
      try {
        const agent = await parseAgentFile(file, dir, source);
        // First registration wins (global before project)
        if (!seenNames.has(agent.name)) {
          seenNames.add(agent.name);
          agents.push(agent);
        }
      } catch (err) {
        console.error(
          `[k-subagent] Failed to load agent from ${file}:`,
          err instanceof Error ? err.message : String(err),
        );
      }
    }
  };

  if (scope !== "project") await loadFrom(globalDir, "global");
  if (projectDir) await loadFrom(projectDir, "project");

  agents.sort((a, b) => a.displayName.localeCompare(b.displayName));

  return { agents, globalDir, projectDir };
}

/**
 * Format agent list for display in system prompt.
 */
export function formatAgentList(agents: AgentDefinition[]): string {
  if (agents.length === 0) return "No subagents available.";

  return agents
    .map((a) => {
      const modelInfo = a.model ? ` [model: ${a.model}]` : "";
      const toolInfo =
        a.tools && a.tools.length > 0
          ? ` [tools: ${a.tools.join(", ")}]`
          : "";
      return `- **${a.name}** (${a.source}): ${a.description}${modelInfo}${toolInfo}`;
    })
    .join("\n");
}
