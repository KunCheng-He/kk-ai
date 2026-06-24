import * as fs from "node:fs";
import * as path from "node:path";
import { CONFIG_DIR_NAME, getAgentDir } from "@earendil-works/pi-coding-agent";

// This extension (pi-agent-switcher) manages *primary* agents — the ones a user
// switches into as the main session role. They live in `main-agents/` to avoid
// colliding with `~/.pi/agent/agents/`, which is reserved for subagent
// definitions consumed by @agwab/pi-subagent (which hardcodes that path).
//
//   user    → ~/.pi/agent/main-agents/, available in all projects
//   project → .pi/main-agents/, available only in current project
// No scope field is needed in the markdown frontmatter.
const AGENT_SUBDIR = "main-agents";

export type AgentScope = "user" | "project" | "both";

export interface AgentConfig {
  name: string;
  description: string;
  tools?: string[];
  model?: string;
  thinking?: string;
  fallbackModels?: string[];
  systemPrompt: string;
  source: "user" | "project";
  filePath: string;
}

export interface AgentDiscoveryResult {
  agents: AgentConfig[];
  projectAgentsDir: string | null;
  userAgentDir: string;
}

/**
 * Parse YAML frontmatter from markdown content.
 * Returns { frontmatter, body } where frontmatter is a simple key-value map
 * and body is the content after the frontmatter delimiter.
 */
function parseFrontmatter<T extends Record<string, string>>(
  content: string,
): { frontmatter: T; body: string } {
  const frontmatter = {} as T;
  let body = content;

  const match = content.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?/);
  if (match) {
    const yaml = match[1]!;
    body = content.slice(match[0].length);

    for (const line of yaml.split("\n")) {
      const colonIdx = line.indexOf(":");
      if (colonIdx === -1) continue;
      const key = line.slice(0, colonIdx).trim();
      let value: string = line.slice(colonIdx + 1).trim();
      // Remove surrounding quotes if present
      if (
        (value.startsWith('"') && value.endsWith('"')) ||
        (value.startsWith("'") && value.endsWith("'"))
      ) {
        value = value.slice(1, -1);
      }
      frontmatter[key as keyof T] = value as T[keyof T];
    }
  }

  return { frontmatter, body };
}

/**
 * Load agents from a directory recursively.
 */
function loadAgentsFromDir(
  dir: string,
  source: "user" | "project",
): AgentConfig[] {
  const agents: AgentConfig[] = [];
  if (!fs.existsSync(dir)) return agents;

  function walk(currentDir: string) {
    let entries: fs.Dirent[];
    try {
      entries = fs.readdirSync(currentDir, { withFileTypes: true });
    } catch {
      return;
    }

    for (const entry of entries) {
      const fullPath = path.join(currentDir, entry.name);
      if (entry.isDirectory()) {
        walk(fullPath);
        continue;
      }
      if (!entry.name.endsWith(".md")) continue;
      if (!entry.isFile() && !entry.isSymbolicLink()) continue;

      let content: string;
      try {
        content = fs.readFileSync(fullPath, "utf-8");
      } catch {
        continue;
      }

      const { frontmatter, body } = parseFrontmatter<Record<string, string>>(
        content,
      );
      if (!frontmatter.name || !frontmatter.description) continue;

      const tools = frontmatter.tools
        ?.split(",")
        .map((t: string) => t.trim())
        .filter(Boolean);
      const fallbackModels = frontmatter.fallbackModels
        ?.split(",")
        .map((m: string) => m.trim())
        .filter(Boolean);

      agents.push({
        name: frontmatter.name,
        description: frontmatter.description,
        tools: tools && tools.length > 0 ? tools : undefined,
        model: frontmatter.model || undefined,
        thinking: frontmatter.thinking || undefined,
        fallbackModels:
          fallbackModels && fallbackModels.length > 0
            ? fallbackModels
            : undefined,
        systemPrompt: body.trim(),
        source,
        filePath: fullPath,
      });
    }
  }

  walk(dir);
  return agents;
}

function isDirectory(p: string): boolean {
  try {
    return fs.statSync(p).isDirectory();
  } catch {
    return false;
  }
}

/**
 * Walk up from cwd to find the nearest .pi/main-agents directory.
 */
function findNearestProjectAgentsDir(cwd: string): string | null {
  let currentDir = cwd;
  while (true) {
    const candidate = path.join(currentDir, CONFIG_DIR_NAME, AGENT_SUBDIR);
    if (isDirectory(candidate)) return candidate;
    const parentDir = path.dirname(currentDir);
    if (parentDir === currentDir) return null;
    currentDir = parentDir;
  }
}

/**
 * Discover all available agents, respecting priority:
 * user < project (project overrides user).
 */
export function discoverAgents(
  cwd: string,
  scope: AgentScope,
): AgentDiscoveryResult {
  // Global user agents
  const userAgentDir = path.join(getAgentDir(), AGENT_SUBDIR);
  const userAgents =
    scope === "project" ? [] : loadAgentsFromDir(userAgentDir, "user");

  // Project agents
  const projectAgentsDir = findNearestProjectAgentsDir(cwd);
  const projectAgents =
    scope === "user" || !projectAgentsDir
      ? []
      : loadAgentsFromDir(projectAgentsDir, "project");

  // Priority: user < project; same name = override
  const agentMap = new Map<string, AgentConfig>();

  for (const agent of userAgents) agentMap.set(agent.name, agent);
  for (const agent of projectAgents) agentMap.set(agent.name, agent);

  return {
    agents: Array.from(agentMap.values()),
    projectAgentsDir,
    userAgentDir,
  };
}

/**
 * Resolve a specific agent by name.
 */
export function resolveAgent(
  cwd: string,
  name: string,
  discovery?: AgentDiscoveryResult,
): AgentConfig | undefined {
  const agents = discovery ?? discoverAgents(cwd, "both");
  return agents.agents.find((a) => a.name === name);
}
