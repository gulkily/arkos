# CLI Agent Guide

The CLI agent is the most complete way to interact with ARKOS today. This guide explains the required services, how the components fit together, and how to troubleshoot common issues.

## Prerequisites
- Python 3.10+
- Dependencies from `requirements.txt`
- Docker (for the SGLang container)
- Hugging Face token with access to `Qwen/Qwen2.5-7B-Instruct`
- GPU with ~16 GB VRAM recommended (adjust `model_module/run.sh` if your setup differs)

## Start the model server
```bash
export HF_TOKEN="hf_xxx"
bash model_module/run.sh
```
This downloads the `lmsysorg/sglang:latest` image, binds it to GPU device `1` by default, and exposes an OpenAI-compatible API on `http://localhost:30000/v1`.

Verify the server is healthy:
```bash
curl http://localhost:30000/v1/models
```

## Launch the CLI agent
```bash
python -m base_module.main_interface
```
You will see `=== Starting CLI Agent (type 'exit' to quit) ===` followed by repeated prompts of `You:`. Type your message and press Enter. The agent responds using the SGLang backend until you type `exit`.

## How it works
1. `base_module/main_interface.py` loads `state_module/state_graph.yaml` via `StateHandler`.
2. `Memory(agent_id="cli-agent")` writes each turn to `memory.csv`.
3. An `Agent` object keeps the conversation context (`context["messages"]`).
4. `Agent.step(...)` walks the state graph:
   - `StateUser` collects console input.
   - `StateAI` calls `ArkModelLink` and prints the model result.
   - `StateTool` currently returns a placeholder `SystemMessage`.

The initial system prompt is defined inline in `run_cli_agent()`; edit it to change the agent persona or available tools.

## Customization tips
- **State flow**: Edit `state_module/state_graph.yaml` to add states or re-order the loop. Register new state classes with `@register_state` in `state_module/`.
- **Model endpoint**: Pass a different `base_url` to `ArkModelLink` if the SGLang server runs on another host or port.
- **Memory file**: Provide `filename="/tmp/my_memory.csv"` when creating `Memory` to isolate sessions.
- **Tool behavior**: Implement real tool logic in `state_module/state_tool.py` and create helper functions in `tool_module/`.

## Troubleshooting
| Symptom | Likely cause | Fix |
| ------- | ------------ | --- |
| `openai.AuthenticationError` or HTTP 401 | `HF_TOKEN` missing or invalid | Re-export `HF_TOKEN` and restart `run.sh`. |
| CLI hangs after user input | SGLang container not reachable | Check `docker ps` and ensure port `30000` is exposed. |
| `memory.csv` permission denied | Repository directory not writable | Run from a writable location or change `Memory` filename. |
| Tool placeholder keeps printing | `state_tool.py` still stubbed | Replace placeholder with actual tool invocation logic. |

## Next steps
- Consult `docs/reference/state_and_memory.md` for lower-level details about the state machine and memory stack.
- Review `plans/ai/` for the roadmap toward richer tooling and web interfaces.
