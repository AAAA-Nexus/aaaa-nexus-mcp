# MCP Editor Configs

Drop-in configs for every major MCP-aware editor. Replace `an_your_key_here` with your key from [atomadic.tech/pay](https://atomadic.tech/pay).

| Editor | File to edit | Config |
| --- | --- | --- |
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) / `%APPDATA%\Claude\claude_desktop_config.json` (Windows) | [claude_desktop.json](claude_desktop.json) |
| Claude Code | `~/.claude/settings.json` or project `.mcp.json` | [claude_desktop.json](claude_desktop.json) |
| Cursor | `~/.cursor/mcp.json` or project `.cursor/mcp.json` | [cursor.json](cursor.json) |
| VS Code (GitHub Copilot Chat) | User or workspace `settings.json` | [vscode_settings.json](vscode_settings.json) |
| Zed | `~/.config/zed/settings.json` | [zed.json](zed.json) |
| Windsurf | `~/.codeium/windsurf/mcp_config.json` | [windsurf.json](windsurf.json) |

After saving, restart the editor. The 135 `nexus_*` tools are now available in chat.
