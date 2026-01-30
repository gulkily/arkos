# State and Memory Reference

This document covers the YAML-driven state machine and the Postgres + Mem0 memory stack used by ARKOS.

## State machine overview

`state_module/state_graph.yaml` determines the order of execution. The current default configuration is:

```yaml
initial: agent_reply

states:
  ask_user:
    description: "state used for input from user"
    type: user
    transition:
      next: [agent_reply]

  agent_reply:
    description: "state used for your reasoning"
    type: agent
    transition:
      next: [agent_reply, ask_user]

  cal_tool:
    description: "state used for querying users calendar"
    type: calendar
    transition:
      next: [agent_reply]

  search_tool:
    description: "state used for searching the internet"
    type: search
    transition:
      next: [agent_reply]
```

### StateHandler
- Loads the YAML document and instantiates state classes based on `type`.
- Exposes `get_initial_state()`, `get_state(name)`, and `get_transitions(current_state, context)`.
- Uses `state_registry.py` to discover state classes decorated with `@register_state`.

### Built-in states
| State | File | Behavior |
| ----- | ---- | -------- |
| `StateUser` | `state_module/state_user.py` | Terminal placeholder used to yield control back to the client; user input is collected outside the state graph. |
| `StateAI` | `state_module/state_ai.py` | Calls `agent.call_llm` and returns an `AIMessage`. |
| `StateCal` | `state_module/state_calendar.py` | Placeholder calendar flow that can call the Google Calendar MCP server. |
| `StateSearch` | `state_module/state_search.py` | MCP-powered search flow using the Brave Search server. |
| `StateTool` | `state_module/state_tool.py` | Placeholder for custom tool routing (not enabled by default). |

### Custom states
1. Create a new class in `state_module/` and decorate it with `@register_state`.
2. Implement `check_transition_ready` and `run`.
3. Add the state to `state_graph.yaml` with the matching `type` and transitions.

Example:
```python
@register_state
class StateLogging(State):
    type = "logging"

    def __init__(self, name, config):
        super().__init__(name, config)
        self.path = config.get("path", "logs.txt")

    def check_transition_ready(self, context):
        return True

    def run(self, context, agent=None):
        with open(self.path, "a") as fh:
            fh.write(context[-1].content + "\n")
        return None
```

## Memory stack

`memory_module/memory.py` persists conversation context in Postgres and uses Mem0 for vector-based retrieval.

### Configuration
- `DB_URL` must be set in `.env` or the shell environment.
- Mem0 expects `OPENAI_API_KEY` to be present; a placeholder value is acceptable if you are using a local LLM.
- The Mem0 configuration lives in `memory_module/memory.py` (not `config_module/config.yaml`):
  - Vector store provider: `supabase` (collection `memories`).
  - LLM provider: `vllm` with `vllm_base_url` at `http://localhost:30000/v1`.
  - Embedder provider: `huggingface` with `huggingface_base_url` at `http://localhost:4444/v1`.

### Initialization
```python
from memory_module.memory import Memory

memory = Memory(user_id="ark-agent", session_id=None, db_url=os.environ["DB_URL"])
```
- Creates a new session ID when `session_id` is `None`.
- Uses `Mem0Memory.from_config` for vector storage.

### Recording messages
`Memory.add_memory(message)`:
- Infers the role (`system`, `user`, `assistant`, `tool`).
- Stores the message in Mem0 for long-term retrieval.
- Writes the serialized message into the `conversation_context` table in Postgres.

### Required Postgres schema
The code assumes a `conversation_context` table with an auto-incrementing `id` column for ordering:
```sql
CREATE TABLE conversation_context (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,
    message TEXT NOT NULL
);
```

### Retrieving context
- `retrieve_short_memory(turns)` returns the latest messages from Postgres.
- `retrieve_long_memory(context, mem0_limit)` uses Mem0 similarity search to retrieve related memories.

### Tips for extension
- Update the Mem0 config to use a different vector store or embedding endpoint.
- Add timestamps or metadata to the Postgres table if you need richer analytics.
- Keep the state graph and memory usage in sync; tool states should log outputs consistently.

## Putting it together

During a request:
1. The agent runs the current state (`agent_reply`, `cal_tool`, `search_tool`, etc.).
2. The state returns an `AIMessage` or `ToolMessage` that the agent stores in memory.
3. The agent uses `StateHandler.get_transitions` plus `choose_transition` to pick the next state.
4. The loop ends when the next state is terminal, and the API/CLI returns the last AI message.

Keep this reference handy while you update the docs and state graphs to match the latest tool or memory work.
