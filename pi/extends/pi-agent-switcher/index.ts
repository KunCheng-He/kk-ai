/**
 * pi-agent-switcher Extension
 *
 * Allows users to manually switch between agent roles in the main Pi session.
 * Each agent is defined via markdown files with YAML frontmatter, controlling
 * system prompt, tools, model, and thinking level.
 *
 * Switch via Alt+A or /agent command.
 * List agents via /agents command.
 * Reset to default via /agent reset.
 */

import type { ExtensionAPI, ExtensionContext } from "@earendil-works/pi-coding-agent";
import { DynamicBorder } from "@earendil-works/pi-coding-agent";
import { Container, Key, type SelectItem, SelectList, Text, Box } from "@earendil-works/pi-tui";
import { AgentStateManager } from "./agent-state";
import { discoverAgents, resolveAgent } from "./agents";

let stateManager: AgentStateManager;

export default function agentSwitcherExtension(pi: ExtensionAPI) {
  stateManager = new AgentStateManager();

  // ============================================================
  // Event: before_agent_start — modify system prompt & tools
  // ============================================================
  pi.on("before_agent_start", async (event, ctx) => {
    const currentAgentName = stateManager.getCurrentAgent();
    if (!currentAgentName) return;

    const agent = resolveAgent(ctx.cwd, currentAgentName, stateManager.lastDiscovery());
    if (!agent) return;

    // Always use prepend mode: agent's identity goes first (high-attention position),
    // Pi's built-in tool/guideline text is kept after as background context,
    // wrapped in a tag so the model clearly separates identity from environment.
    const systemPrompt =
      agent.systemPrompt +
      "\n\n<environment_context>\n" +
      event.systemPrompt +
      "\n</environment_context>";

    // Tool set switching
    if (agent.tools && agent.tools.length > 0) {
      pi.setActiveTools(agent.tools);
    }

    // Model switching
    if (agent.model) {
      const [provider, ...rest] = agent.model.split("/");
      const modelId = rest.join("/");
      if (provider && modelId) {
        const model = ctx.modelRegistry.find(provider, modelId);
        if (model) {
          const success = await pi.setModel(model);
          if (!success) {
            ctx.ui.notify(
              `Agent "${agent.name}": 无法切换到模型 ${agent.model}`,
              "warning",
            );
          }
        }
      }
    }

    // Thinking level switching
    if (agent.thinking) {
      pi.setThinkingLevel(agent.thinking);
    }

    return {
      systemPrompt,
    };
  });

  // ============================================================
  // Event: session_start — restore agent state & update UI
  // ============================================================
  pi.on("session_start", async (_event, ctx) => {
    // Restore agent state — find the LATEST entry (not the first)
    let latestState: { currentAgent?: string | null } | undefined;
    for (const entry of ctx.sessionManager.getBranch()) {
      if (
        entry.type === "custom" &&
        (entry as { customType?: string }).customType === "agent-switcher-state"
      ) {
        const data = (entry as { data?: { currentAgent?: string | null } }).data;
        if (data) latestState = data;
      }
    }
    if (latestState?.currentAgent) {
      stateManager.setAgent(latestState.currentAgent);
      // Restore session name display
      pi.setSessionName(`🤖 ${latestState.currentAgent}`);
    } else {
      stateManager.reset();
    }

    // Discover available agents
    const discovery = discoverAgents(ctx.cwd, "both");
    stateManager.setLastDiscovery(discovery);
  });

  // ============================================================
  // Shortcut: Alt+A — open agent switcher
  // ============================================================
  pi.registerShortcut(Key.alt("a"), {
    description: "切换主 agent 角色",
    handler: async (ctx) => {
      if (!ctx.isIdle()) return;
      await openAgentSwitcher(pi, stateManager, ctx);
    },
  });

  // ============================================================
  // Command: /agent <name> — switch or open selector
  // ============================================================
  pi.registerCommand("agent", {
    description: "切换主 agent 角色",
    getArgumentCompletions(prefix: string) {
      const discovery = discoverAgents(process.cwd(), "both");
      return discovery.agents
        .filter((a) => a.name.startsWith(prefix))
        .map((a) => ({ value: a.name, label: a.name, description: a.description }));
    },
    handler: async (args, ctx) => {
      const agentName = args.trim();
      if (!agentName) {
        await openAgentSwitcher(pi, stateManager, ctx);
        return;
      }
      if (agentName === "reset" || agentName === "default") {
        await resetToDefault(pi, stateManager, ctx);
        return;
      }
      await performSwitch(pi, stateManager, agentName, ctx);
    },
  });

  // ============================================================
  // Command: /agents — list all available agents
  // ============================================================
  pi.registerCommand("agents", {
    description: "列出所有可用 agent 角色",
    handler: async (_args, ctx) => {
      const discovery = discoverAgents(ctx.cwd, "both");
      const currentAgent = stateManager.getCurrentAgent();
      const lines = discovery.agents.map((a) => {
        const marker = a.name === currentAgent ? "→ " : "  ";
        const scopeTag = a.source === "project" ? " [项目]" : "";
        const modelTag = a.model ? ` (${a.model})` : "";
        return `${marker}${a.name}: ${a.description}${modelTag}${scopeTag}`;
      });
      ctx.ui.notify(
        `当前: ${currentAgent || "默认"}\n\n${lines.join("\n")}`,
        "info",
      );
    },
  });

}

// ============================================================
// Core: open agent selector UI
// ============================================================
async function openAgentSwitcher(
  pi: ExtensionAPI,
  stateManager: AgentStateManager,
  ctx: ExtensionContext,
): Promise<void> {
  const discovery = discoverAgents(ctx.cwd, "both");
  stateManager.setLastDiscovery(discovery);
  const currentAgent = stateManager.getCurrentAgent();

  // Separate global and project agents
  const globalAgents = discovery.agents.filter((a) => a.source !== "project");
  const projectAgents = discovery.agents.filter((a) => a.source === "project");

  const items: SelectItem[] = [];

  // Global agents
  for (const a of globalAgents) {
    items.push({
      value: a.name,
      label: a.name === currentAgent ? `✓ ${a.name}` : `  ${a.name}`,
      description: a.description + (a.model ? ` (${a.model})` : ""),
    });
  }

  // Project agents (with separator)
  if (projectAgents.length > 0) {
    items.push({
      value: "__separator__",
      label: "── 项目 Agent ──",
      description: "",
    });
    for (const a of projectAgents) {
      items.push({
        value: a.name,
        label:
          a.name === currentAgent
            ? `✓ ${a.name} [项目]`
            : `  ${a.name} [项目]`,
        description: a.description + (a.model ? ` (${a.model})` : ""),
      });
    }
  }

  // Reset option
  items.push({
    value: "__reset__",
    label: "↩ 重置为默认",
    description: "恢复 Pi 默认行为",
  });

  // Build digit-to-value mapping for quick shortcuts (keys 1-9),
  // and prepend shortcut numbers to item labels.
  const shortcutMap = new Map<number, string>();
  {
    let num = 1;
    for (const item of items) {
      if (item.value === "__separator__") continue;
      if (num > 9) break;
      shortcutMap.set(num, item.value);
      const prefix = `[${num}] `;
      item.label = prefix + item.label;
      num++;
    }
  }

  const result = await ctx.ui.custom<string | null>((tui, theme, _kb, done) => {
    const container = new Container();

    // Box wrapper with subtle background to distinguish from background
    const box = new Box(0, 0, (s: string) => theme.bg("customMessageBg", s));

    // Top border
    box.addChild(new DynamicBorder((s: string) => theme.fg("accent", s)));

    // Title
    box.addChild(
      new Text(
        theme.fg("accent", theme.bold("🤖 切换主 Agent")) +
          " " +
          theme.fg("dim", `(当前: ${currentAgent || "默认"})`),
        1,
        0,
      ),
    );

    // SelectList
    const selectList = new SelectList(items, Math.min(items.length, 12), {
      selectedPrefix: (t) => theme.fg("accent", t),
      selectedText: (t) => theme.fg("accent", t),
      description: (t) => theme.fg("muted", t),
      scrollInfo: (t) => theme.fg("dim", t),
      noMatch: (t) => theme.fg("warning", t),
    });
    selectList.onSelect = (item) => done(item.value);
    selectList.onCancel = () => done(null);
    box.addChild(selectList);

    // Help text
    box.addChild(
      new Text(
        theme.fg("dim", "↑↓ 导航 • 1-9 快捷选择 • enter 选择 • esc 取消 • 输入过滤"),
        1,
        0,
      ),
    );

    // Bottom border
    box.addChild(new DynamicBorder((s: string) => theme.fg("accent", s)));

    container.addChild(box);

    return {
      render: (w: number) => container.render(w),
      invalidate: () => container.invalidate(),
      handleInput: (data: string) => {
        // Quick shortcut: digit 1-9 directly selects the corresponding item
        if (data.length === 1 && data >= "1" && data <= "9") {
          const digit = Number(data);
          const value = shortcutMap.get(digit);
          if (value) {
            done(value);
            return;
          }
        }
        selectList.handleInput(data);
        tui.requestRender();
      },
    };
  });

  if (result === null || result === "__separator__") return;
  if (result === "__reset__") {
    await resetToDefault(pi, stateManager, ctx);
    return;
  }
  await performSwitch(pi, stateManager, result, ctx);
}

// ============================================================
// Core: perform agent switch
// ============================================================
async function performSwitch(
  pi: ExtensionAPI,
  stateManager: AgentStateManager,
  agentName: string,
  ctx: ExtensionContext,
): Promise<void> {
  const discovery =
    stateManager.lastDiscovery() ?? discoverAgents(ctx.cwd, "both");
  const agent = discovery.agents.find((a) => a.name === agentName);

  if (!agent) {
    const available = discovery.agents.map((a) => a.name).join(", ");
    ctx.ui.notify(
      `未知 agent: "${agentName}"。可用: ${available}`,
      "error",
    );
    return;
  }

  const previousAgent = stateManager.getCurrentAgent();
  stateManager.setAgent(agentName);

  // Persist state in session
  pi.appendEntry("agent-switcher-state", { currentAgent: agentName });

  // Show agent name inline after cwd on line 1 of footer
  pi.setSessionName(`🤖 ${agent.name}`);

  // Notify user
  const prevLabel = previousAgent || "默认";
  ctx.ui.notify(`Agent 切换: ${prevLabel} → ${agent.name}`, "info");
}

// ============================================================
// Core: reset to default agent
// ============================================================
async function resetToDefault(
  pi: ExtensionAPI,
  stateManager: AgentStateManager,
  ctx: ExtensionContext,
): Promise<void> {
  const previousAgent = stateManager.getCurrentAgent();
  if (!previousAgent) {
    ctx.ui.notify("当前已是默认 agent", "info");
    return;
  }

  stateManager.reset();

  // Persist reset
  pi.appendEntry("agent-switcher-state", { currentAgent: null });

  // Restore original session name (or clear if it was set by us)
  pi.setSessionName("");

  // Notify user
  ctx.ui.notify(`Agent 重置: ${previousAgent} → 默认`, "info");
}