# Tool Integration Guide

ARKOS uses the Model Context Protocol (MCP) to connect to external tools. The current implementation supports stdio and HTTP transports and loads MCP server definitions from `config_module/config.yaml`.

## Requirements
- Node.js with `npx` (used to launch MCP servers)
- Any tool-specific credentials (see `.env.example`)

## Where the pieces live
- `tool_module/tool_call.py` – MCP client + manager (`MCPClient`, `MCPToolManager`).
- `tool_module/auth_once.py` – helper to create Google Calendar OAuth tokens.
- `tool_module/test_tool_call.py` – pytest-based MCP smoke tests.
- `state_module/state_calendar.py` – placeholder calendar state wired for the Google Calendar MCP server (returns stub output by default).
- `state_module/state_search.py` – state that calls the Brave Search MCP server.
- `state_module/state_tool.py` – placeholder state for custom tool logic.

## Current execution flow
1. MCP servers are defined under `mcp_servers` in `config_module/config.yaml`.
2. `base_module/app.py` constructs `MCPToolManager` from that config and initializes servers on startup.
3. `MCPToolManager.initialize_servers()` starts each server and builds a tool registry.
4. States call `MCPToolManager.call_tool(...)` and return a `ToolMessage` to the agent.

## MCP server configuration
`config_module/config.yaml` controls tool connectivity via the `mcp_servers` map. Each entry can use a `transport` of `stdio` or `http`:

```yaml
mcp_servers:
  brave-search:
    transport: stdio
    command: npx
    args: ["-y", "@brave/brave-search-mcp-server", "--transport", "stdio"]
    env:
      BRAVE_API_KEY: "${BRAVE_API_KEY}"

  google-calendar:
    transport: stdio
    command: npx
    args: ["-y", "@cocal/google-calendar-mcp"]
    env:
      GOOGLE_OAUTH_CREDENTIALS: "${GOOGLE_OAUTH_CREDENTIALS}"

  filesystem:
    transport: stdio
    command: npx
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
```

For HTTP servers, set `transport: http` and provide `url` plus optional `auth` settings (see `tool_module/transports/http.py` for OAuth/bearer options). Environment variables in the YAML (e.g., `${BRAVE_API_KEY}`) are resolved by `config_module/loader.py` using `.env`.

## Transports
ARKOS ships two MCP transport implementations in `tool_module/transports/`:
- **stdio** (`stdio.py`): launches a subprocess and speaks JSON-RPC over stdin/stdout.
- **http** (`http.py`): uses Streamable HTTP with optional OAuth 2.1 (PKCE) or bearer token auth.

When OAuth is enabled for HTTP transport, the client caches tokens in:
`~/.arkos/mcp_tokens.json`.

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
4. Enable real calendar calls in `state_module/state_calendar.py` by replacing the placeholder output with the actual MCP call (uncomment the `calendar_retrieval()` invocation and return its result as a `ToolMessage`). Keep the method async and ensure the env vars above point to real files.

### Per-user OAuth (base_module)
The API server exposes OAuth endpoints for Google Calendar in `base_module/auth.py`:
1. Ensure `GOOGLE_OAUTH_CREDENTIALS` points to a Google OAuth client JSON file (set it in `.env` or the shell).
2. Start the API server (`python base_module/app.py`).
3. Initiate auth in a browser:
   - `GET /auth/google/login?user_id=<your-user-id>`
4. The callback endpoint (`/auth/google/callback`) stores tokens for that user.
5. Check connection status:
   - `GET /auth/google/status?user_id=<your-user-id>`
6. Disconnect a user:
   - `DELETE /auth/google/disconnect?user_id=<your-user-id>`

Tokens are stored in Postgres via the per-user token store; see `tool_module/token_store.py`.

### Token storage (user_oauth_tokens)
`tool_module/token_store.py` stores per-user OAuth tokens in Postgres and exports token files for MCP subprocesses.

Expected table schema:
```sql
CREATE TABLE IF NOT EXISTS user_oauth_tokens (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    service VARCHAR(255) NOT NULL,
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    expires_at TIMESTAMP,
    token_data JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, service)
);
```

When a tool call requires per-user auth, the token store writes a service-specific token file into:
`~/.arkos/user_tokens/` (used by MCP subprocesses).

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
- Expand HTTP transport examples and document OAuth token caching behavior.
- Add structured tool call payloads for richer UI rendering.
- Centralize tool auth flows and secrets management.
