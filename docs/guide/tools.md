# Tool Integration Guide

ARKOS uses the Model Context Protocol (MCP) to connect to external tools. The current implementation focuses on launching MCP servers locally and routing tool calls over JSON-RPC 2.0 via stdio.

## Requirements
- Node.js with `npx` (used to launch MCP servers)
- Any tool-specific credentials (see `.env.example`)

## Where the pieces live
- `tool_module/tool_call.py` – MCP client + manager (`MCPClient`, `MCPToolManager`).
- `tool_module/auth_once.py` – helper to create Google Calendar OAuth tokens.
- `tool_module/test_tool_call.py` – pytest-based MCP smoke tests.
- `state_module/state_calendar.py` – placeholder calendar state wired for the Google Calendar MCP server.
- `state_module/state_search.py` – state that calls the Brave Search MCP server.
- `state_module/state_tool.py` – placeholder state for custom tool logic.

## Current execution flow
1. A state (calendar/search/tool) constructs a server config dictionary with `command`, `args`, and optional `env`.
2. `MCPToolManager.initialize_servers()` starts each MCP server and builds a tool registry.
3. The state calls `MCPToolManager.call_tool(...)` and returns a `ToolMessage` to the agent.

## Quickstart: filesystem MCP server
```python
from tool_module.tool_call import MCPToolManager

config = {
    "filesystem": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
    }
}

manager = MCPToolManager(config)
await manager.initialize_servers()
result = await manager.call_tool("list_directory", {"path": "/tmp"})
await manager.shutdown()
```

## Credentials and secrets
- `.env.example` lists variables for tool integrations.
- The secrets directory (`tool_module/secrets/`) is gitignored.

### Google Calendar MCP
1. Place your OAuth client file at `tool_module/secrets/gcp-oauth.keys.json`.
2. Run the auth helper from the module directory (it uses relative `secrets/` paths):
   ```bash
   cd tool_module
   python auth_once.py
   ```
   This generates `tool_module/secrets/google_tokens.json`.
3. Update `state_module/state_calendar.py` or your MCP config to pass:
   - `GOOGLE_OAUTH_CREDENTIALS` (path to OAuth client JSON)
   - `GOOGLE_CALENDAR_MCP_TOKEN_PATH` (path to generated token JSON)

### Brave Search MCP
Set `BRAVE_API_KEY` in `.env` or in the MCP server config passed to `MCPToolManager`.

## Wiring tools into the state graph
`state_module/state_graph.yaml` controls when tool states execute. The default graph includes `cal_tool` and `search_tool` (types `calendar` and `search`). To add your own tool state:
1. Create a new state class under `state_module/` and decorate it with `@register_state`.
2. Add a node in `state_graph.yaml` with `type` matching the class.
3. Return a `ToolMessage` (or `SystemMessage`) with the tool results.

## Testing tools
`pytest tool_module/test_tool_call.py` exercises the MCP client and sample tool servers. These tests require Node.js and, for Google Calendar or Brave Search, the corresponding credentials. Treat them as optional smoke tests until CI coverage is formalized.

## Roadmap
- Move MCP server configuration into `config_module/config.yaml`.
- Add structured tool call payloads for richer UI rendering.
- Centralize tool auth flows and secrets management.
