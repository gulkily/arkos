# State and Memory Reference

This document dives into two subsystems that power the CLI agent: the YAML-driven state machine and the CSV-backed memory helper.

## State machine overview

`state_module/state_graph.yaml` determines the order of execution. The default configuration is:

```yaml
initial: ask_user

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
      next: [ask_user, use_tool]

  use_tool:
    description: "state used for tool use"
    type: tool
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
| `StateUser` | `state_module/state_user.py` | Prompts for console input. Typing `exit` sets `is_terminal = True`. |
| `StateAI` | `state_module/state_ai.py` | Calls `agent.call_llm`, prints the reply, and returns an `AIMessage`. |
| `StateTool` | `state_module/state_tool.py` | Placeholder that prints a stub result and returns a `SystemMessage`. |

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

## Memory helper

`memory_module/memory.py` captures each state transition so you can inspect sessions after the fact.

### Initialization
```python
memory = Memory(agent_id="cli-agent", filename="memory.csv")
```
- Creates the file if it does not exist and writes headers: `agent_id,state,intent,tool,scratchpad`.
- Keeps an in-memory stack (`self.state_stack`) for quick access to the latest entry.

### Recording state changes
```python
memory.push_state({
    "state": "agent_reply",
    "intent": "answer_question",
    "tool": None,
    "scratchpad": {"latency_ms": 1840}
})
```
- Validates that `state` is a string.
- Serializes dictionary scratchpads to JSON before appending to the CSV.
- Stores the original dict in `state_stack` so you can modify it later with `update_scratchpad`.

### Inspecting the stack
- `peek_state()` returns the most recent entry.
- `pop_state()` removes and returns the last entry (does not delete CSV rows).
- `update_scratchpad(updates)` merges fields into the latest scratchpad dict.

### Tips for extension
- Provide a different filename if you want per-run memory files.
- Add timestamps or additional columns by editing `_write_to_csv` and the header definition.
- Replace the CSV writer with a database or object store when you need persistence across services.

## Putting it together

During a CLI session:
1. `StateHandler` fetches `StateUser`.
2. `StateUser.run` returns a `UserMessage`; the agent appends it to `context["messages"]`.
3. `StateAI.run` calls the model and returns an `AIMessage`; the agent appends it and may call `memory.push_state`.
4. `StateTool.run` is invoked only when the transition list contains `use_tool`. Extend this to call real tools and log outputs via `Memory`.

Keep this reference handy while you work through the documentation audit—any doc updates about control flow or memory should align with these details.
