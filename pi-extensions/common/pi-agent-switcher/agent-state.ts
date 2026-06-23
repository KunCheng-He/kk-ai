import type { AgentDiscoveryResult } from "./agents";

/**
 * Manages the current agent state in memory.
 */
export class AgentStateManager {
  private currentAgent: string | null = null;
  private lastDiscoveryResult: AgentDiscoveryResult | null = null;

  getCurrentAgent(): string | null {
    return this.currentAgent;
  }

  setAgent(name: string): void {
    this.currentAgent = name;
  }

  reset(): void {
    this.currentAgent = null;
  }

  setLastDiscovery(discovery: AgentDiscoveryResult): void {
    this.lastDiscoveryResult = discovery;
  }

  lastDiscovery(): AgentDiscoveryResult | null {
    return this.lastDiscoveryResult;
  }
}
