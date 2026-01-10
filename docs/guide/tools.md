# Tool Integration Guide

Tooling is the least mature part of ARKOS. The repository contains placeholder code that shows where tool support will live. Use this guide to understand the current state and how to prototype new tools.

## Where the pieces live
- `tool_module/tool.py` – placeholder registry helpers.
- `tool_module/tool_interface.md` – conceptual spec for an MCP-style tool class.
- `state_module/state_tool.py` – state invoked when the YAML graph includes `type: tool`.
- `agent_module/agent.py` – has stub methods `bind_tool` and `find_downloaded_tool` that need implementation.

## Current execution flow
1. The state graph transitions into `use_tool`.
2. `StateTool.run` prints `TOOL RESULT PLACEHOLDER` and returns `SystemMessage(content="Result: 3*6 is 18")`.
3. The agent appends that message to the conversation context and continues to `agent_reply`.

No dynamic lookup, argument parsing, or tool execution happens yet.

## Prototyping a tool
1. Define a tool class that exposes `name`, `description`, and an async `invoke(payload)` method (adapt the spec in `tool_interface.md`).
2. Update `tool_module/tool.py` to include a registry dictionary mapping tool names to implementations.
3. Replace `StateTool.run` with logic that:
   - Examines `agent.context["messages"]` to extract the latest tool request.
   - Looks up the tool in the registry.
   - Executes the tool and returns a `SystemMessage` or `ToolMessage` with the output.
4. Optionally log the tool event via `Memory.push_state`.

Example sketch:
```python
from tool_module.tool import TOOL_REGISTRY
from model_module.ArkModelNew import ToolMessage

class StateTool(State):
    ...
    def run(self, context, agent=None):
        tool_name = agent.tool_names[-1]
        tool = TOOL_REGISTRY[tool_name]
        result = tool.invoke({"args": "todo"})
        return ToolMessage(content=json.dumps(result))
```

## Surfacing tool results
- For the CLI, printing the returned message is enough.
- For future UIs, prefer emitting structured payloads (JSON with `render_type`/`payload` fields) so the frontend can render richer widgets.

## Roadmap
- Align the registry with the MCP protocol and fetch tool schemas dynamically.
- Allow states to decide whether a tool executes synchronously or asynchronously.
- Display tool latency and arguments in the session history for auditing.

Until the tooling story is fleshed out, keep expectations modest: treat the current implementation as scaffolding and document any experiments in the `plans/ai/` directory.
