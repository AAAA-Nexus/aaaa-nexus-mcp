# MCP Editor Setup

Drop-in configs for every major MCP-aware editor. Copy the JSON, replace `an_your_key_here` with your key from [atomadic.tech/pay](https://atomadic.tech/pay), restart the editor.

| Editor | Config file | Template |
|---|---|---|
| **Claude Desktop** (macOS) | `~/Library/Application Support/Claude/claude_desktop_config.json` | [examples/mcp_configs/claude_desktop.json](../examples/mcp_configs/claude_desktop.json) |
| **Claude Desktop** (Windows) | `%APPDATA%\Claude\claude_desktop_config.json` | same |
| **Claude Code** | `~/.claude/settings.json` or project `.mcp.json` | same |
| **Cursor** | `~/.cursor/mcp.json` or `.cursor/mcp.json` | [cursor.json](../examples/mcp_configs/cursor.json) |
| **VS Code** (Copilot Chat) | User or workspace `settings.json` | [vscode_settings.json](../examples/mcp_configs/vscode_settings.json) |
| **Zed** | `~/.config/zed/settings.json` | [zed.json](../examples/mcp_configs/zed.json) |
| **Windsurf** | `~/.codeium/windsurf/mcp_config.json` | [windsurf.json](../examples/mcp_configs/windsurf.json) |

## Prerequisite

```bash
pip install aaaa-nexus-mcp
```

Requires Python 3.12+. If you don't have it, `pyenv install 3.12` or use the system package manager.

## Verifying

After restart, open the MCP / tools panel in your editor. You should see 140 tools prefixed with `nexus_`. A quick smoke test in chat:

> Run `nexus_health` and show me the result.

If the tool isn't available, check:

1. `python -m aaaa_nexus_mcp` runs without error in a terminal.
2. Your editor's MCP log file (varies) for activation errors.
3. `AAAA_NEXUS_API_KEY` is set in the config `env` block (not just your shell).

## Free tier

Even without a key, these tools work:

- `nexus_health`
- `nexus_rng_quantum`
- `nexus_agent_card`
- `nexus_metrics`

Use them to verify the plugin is live, then add your key for the full 140-tool surface.
