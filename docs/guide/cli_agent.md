# CLI Agent Guide

The CLI client is the simplest way to drive ARKOS today. It sends prompts to the FastAPI service, which runs the state machine, memory stack, and model calls.

## Prerequisites
- Python 3.10+
- Dependencies from `requirements.txt`
- Docker (for the SGLang container)
- Hugging Face token with access to `Qwen/Qwen2.5-7B-Instruct`
- Postgres connection string in `DB_URL` (required by memory)
- GPU with ~16 GB VRAM recommended (adjust `model_module/run.sh` if your setup differs)

## Configuration
Settings live in `config_module/config.yaml` and support `${ENV_VAR}` substitution via `config_module/loader.py`.

1. Copy the env template:
   ```bash
   cp .env.example .env
   ```
2. Set `DB_URL` in `.env`.
3. `OPENAI_API_KEY` is optional in the current codebase: `memory_module/memory.py` sets a dummy value on import. Only set it if you update the memory configuration to use a hosted OpenAI endpoint.
4. Note: `memory.short_term_turns` and `memory.long_term_limit` exist in `config_module/config.yaml`, but the current agent code does not read them (`Agent.get_context()` uses a hard-coded `turns=5`, and `Memory.retrieve_long_memory` defaults to `mem0_limit=50`).

## Start the model server
```bash
export HF_TOKEN="hf_xxx"
bash model_module/run.sh
```
If `model_module/run.sh` still contains `export HF_TOKEN=""`, set the token there or remove the blank export. The script downloads the `lmsysorg/sglang:latest` image and exposes an OpenAI-compatible API on `http://localhost:30000/v1`.

Verify the server is healthy:
```bash
curl http://localhost:30000/v1/models
```

## Launch the API server
```bash
python base_module/app.py
```
The port comes from `config_module/config.yaml` (default `1112`). Keep this running while you use the CLI.

## Launch the CLI client
```bash
python -m base_module.main_interface
```
You will see repeated prompts of `You:`. Type your message and press Enter. The client POSTs to `/v1/chat/completions` and prints the response.

## How it works
1. `base_module/main_interface.py` sends requests to the FastAPI service using the configured `app.port`.
2. `base_module/app.py` loads `state_module/state_graph.yaml` via `StateHandler` and wires `Agent`, `Memory`, and `ArkModelLink`.
3. `Memory` persists conversation context to Postgres and Mem0 using `DB_URL`.
4. The state graph can route through:
   - `StateUser` (`state_module/state_user.py`) as a terminal placeholder to yield control back to the client.
   - `StateAI` (`state_module/state_ai.py`) for LLM calls.
   - `StateCal` and `StateSearch` (`state_module/state_calendar.py`, `state_module/state_search.py`) for MCP-based tool calls.
   - `StateTool` (`state_module/state_tool.py`) if you re-enable it in the graph.

The system prompt is configurable in `config_module/config.yaml` (`app.system_prompt`).

## Troubleshooting
| Symptom | Likely cause | Fix |
| ------- | ------------ | --- |
| `Environment variable 'DB_URL' not found` | `.env` missing or incomplete | Copy `.env.example` and set `DB_URL`. |
| CLI returns connection errors | API server not running or wrong `app.port` | Start `python base_module/app.py` and verify the port. |
| `openai.AuthenticationError` or HTTP 401 | `HF_TOKEN` missing or invalid | Set `HF_TOKEN` in `model_module/run.sh` (or export it after removing the blank export) and restart `run.sh`. |
| Tool state fails immediately | MCP server not installed or missing env vars | Install Node.js, set MCP credentials, and retry. |

## Next steps
- Consult `docs/reference/state_and_memory.md` for lower-level details about the state machine and memory stack.
- Review `docs/guide/tools.md` for MCP tool setup and examples.
- Review `docs/guide/web_ui.md` for the experimental web UI prototype.
