# pi-agent-switcher

A Pi extension for manually switching the primary agent role in a session from Markdown-defined agent files.

Each agent can have its own system prompt, tool set, model, and thinking level. Agent definitions are simple Markdown files with YAML frontmatter.

## Features

- **Markdown-defined agents** — define roles with `.md` files and YAML frontmatter
- **Two scopes** — user agents (`~/.pi/agent/k-priagent/`) and project agents (`.pi/k-priagent/`)
- **Project overrides user** — a project agent with the same name takes precedence
- **Separate from subagents** — this extension manages primary session roles from `k-priagent/`; `~/.pi/agent/agents/` remains available to subagent runtimes such as [@agwab/pi-subagent](https://github.com/AgwaB/pi-subagent)
- **System-prompt switching** — the agent identity is prepended; Pi's built-in context remains inside `<environment_context>`
- **Tool, model, and thinking switching** — optionally restrict tools or select a model and thinking level per agent
- **Session persistence** — the selected agent survives session branches and reloads
- **Interactive picker** — search, keyboard navigation, and number shortcuts
- **Optional French UI** — uses [pi-i18n](https://github.com/jerryfan/pi-i18n) when installed; otherwise the UI is English

## Install

```bash
pi install npm:pi-agent-switcher
```

Optional French UI:

```bash
pi install npm:pi-i18n
# Restart Pi, then run:
/lang fr
```

`pi-i18n` is not required: without it, pi-agent-switcher stays fully functional in English.

## Usage

### Commands

| Command | Description |
| --- | --- |
| `/agent <name>` | Switch to an agent |
| `/agent` | Open the interactive agent picker |
| `/agent reset` | Restore Pi's default behavior |
| `/agents` | List available agents |

### Shortcut

| Key | Action |
| --- | --- |
| `Alt+A` | Open the interactive agent picker |

### Interactive picker

- **Arrow keys** — navigate the list
- **1–9** — select an item directly
- **Enter** — confirm
- **Esc** — cancel
- **Type** — filter by name or description

## Define an agent

Create a `.md` file in either directory:

- **User**: `~/.pi/agent/k-priagent/` — available in every project
- **Project**: `.pi/k-priagent/` — available only in the current project

### Agent file format

```markdown
---
name: my-agent
description: A short description of this agent's role
tools: read,write,bash,edit
model: anthropic/claude-sonnet-4-20250514
thinking: medium
---

You are a specialist for [a specific task].

Your responsibilities:

- ...
- ...

Rules:

- ...
```

### Frontmatter fields

| Field | Required | Description |
| --- | --- | --- |
| `name` | Yes | Unique identifier used by `/agent <name>` |
| `description` | Yes | Short label shown in agent lists |
| `tools` | No | Comma-separated allowed tools, such as `read,write,bash,edit` |
| `model` | No | `provider/modelId`, such as `anthropic/claude-sonnet-4-20250514` |
| `thinking` | No | `off`, `low`, `medium`, or `high` |

The Markdown body after the frontmatter is the agent system prompt.

### Example: code reviewer

`~/.pi/agent/k-priagent/code-reviewer.md`

```markdown
---
name: code-reviewer
description: Reviews code quality and correctness
tools: read,bash
thinking: high
---

You are a senior code reviewer. Focus on:

- Correctness and edge cases
- Performance impact
- Security vulnerabilities
- Readability and maintainability

Always give actionable advice and concrete code examples.
```

### Example: frontend developer

`.pi/k-priagent/frontend.md`

```markdown
---
name: frontend
description: Frontend specialist for React and Vue
model: anthropic/claude-sonnet-4-20250514
tools: read,write,bash,edit
---

You are a frontend developer specializing in React, Vue, and modern CSS.
Prefer component-oriented designs and accessibility best practices.
```

## How it works

When an agent is active, the extension handles Pi's `before_agent_start` event:

1. **System prompt** — prepends the agent system prompt and wraps Pi's built-in context in `<environment_context>`
2. **Tools** — activates only the configured tools when the agent defines `tools`
3. **Model** — switches to the configured model when available
4. **Thinking level** — applies the configured thinking level

On session start, the extension restores the most recently active agent from session history.

## Debugging

To inspect the complete assembled system prompt after an agent switch (agent identity plus `<environment_context>`), use [pi-message-capture](https://github.com/KunCheng-He/pi-message-capture).

## License

MIT
