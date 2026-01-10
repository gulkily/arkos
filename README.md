# ARKOS

ARKOS (Automated Resource Knowledgebase Operating System) is an experimental agent stack for managing resource knowledge with long-term memory, configurable state transitions, and tool integrations. It currently focuses on a CLI agent that talks to a locally hosted SGLang inference server.

## Repository Layout
- `.github/` – pull request guidelines and templates used for team coordination.
- `agent_module/` – the primary `Agent` implementation orchestrating flows, tools, and the language model.
- `base_module/` – CLI entry point (`main_interface.py`) that wires the agent, memory, and state handler together.
- `config_module/` – YAML configuration assets used by other components.
- `memory_module/` – CSV-backed conversation memory utilities.
- `model_module/` – the `ArkModelLink` wrapper and scripts (`run.sh`) for launching the SGLang server backend.
- `state_module/` – finite-state configuration (`state_graph.yaml`) and helpers for agent transitions.
- `tool_module/` – MCP-compatible tool interactions and supporting helpers.
- `docs/` – living documentation split into `guide/`, `reference/`, and `ops/` directories.
- `plans/` – forward-looking AI and UI planning documents relocated out of the main docs tree.
- `requirements.txt` – minimal Python dependency set (`openai`, `pyyaml`, `pydantic`, `requests`).
- `LICENSE.txt` – GNU Affero General Public License v3.0.

## Languages and Dependencies
The entire codebase is in Python, except for a few shell scripts.

### Core Dependencies
* **`openai>=1.61.0`** - OpenAI Python SDK for standardizing inference engine communication and API compatibility
* **`pyyaml>=6.0.2`** - YAML parser for configuration files (state graphs, etc.)
* **`pydantic>=2.10.6`** - Data validation and schema definition using Python type annotations
* **`requests>=2.32.3`** - HTTP library for making API requests to external services and tools

### Web Framework
* **`fastapi>=0.115.0`** - Modern, fast web framework for building the API server with automatic OpenAPI documentation
* **`uvicorn>=0.32.0`** - ASGI server for running FastAPI applications

### Database & Memory
* **`psycopg2-binary>=2.9.11`** - PostgreSQL adapter for Python (binary distribution, no compilation required). Used for storing conversation context and long-term memory
* **`mem0ai`** - Memory management library for vector-based memory storage and retrieval using Supabase

### Installation
Install all dependencies using:

```bash
pip install -r requirements.txt
```

**Note:** `psycopg2-binary` is used instead of `psycopg2` to avoid requiring PostgreSQL development libraries (`libpq-dev`) on the system. For production deployments, you may want to use `psycopg2` with proper system dependencies.

## Prerequisites
- Python 3.10 or newer with `pip` available.
- (Optional but recommended) a virtual environment for isolating dependencies.
- Access to a GPU-capable host for running an SGLang container (the default `run.sh` launches Qwen2.5-7B).
- A Hugging Face access token exported as `HF_TOKEN` before starting the inference server.

## Environment Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Deployment Environment: MIT SIPB Shared Server (ark.mit.edu)
**⚠️ IMPORTANT:** ARK OS is deployed on a **shared server** where multiple team members work simultaneously. This means:
- **Port conflicts** can occur when multiple users run the same services
- The **LLM inference server (port 30000)** is shared among all users
- You should use **unique ports** for your API server instance

### Start Inference Engine (REQUIRED FIRST!)
**⚠️ IMPORTANT:** The LLM server MUST be running before starting any ARK OS applications. Without it, you'll get connection errors.

#### Check if LLM Server is Already Running
Since this is a shared server, someone else may have already started it:

```bash
# Check if port 30000 is in use
lsof -i :30000

# Or verify it's responding
curl http://localhost:30000/v1/models
```

If you see output, the LLM server is already running - **you can skip starting it**.

## Running the Inference Server (SGLang)
1. Export your Hugging Face token: `export HF_TOKEN="hf_xxx"`.
2. From the project root run: `bash model_module/run.sh`.
3. The script pulls `lmsysorg/sglang:latest` and serves Qwen2.5 on `http://localhost:30000/v1` by default.
4. Confirm the server is reachable before starting the agent (`curl http://localhost:30000/v1/models`).

Adjust GPU selection, model path, or port inside `model_module/run.sh` to match your hardware.

### Setting .env Variables
You need to create a .env and set DB_URL before starting the application

1. **Copy example env file**:
   ```bash
   cp .env.example .env
   ```
2. **Edit .env**:
   ```bash
   # Set DB URL
   DB_URL=postgresql://postgres:your-super-secret-and-long-postgres-password@localhost:54322/postgres
   ```

## Running the CLI Agent
Once the SGLang backend is healthy:
```bash
python -m base_module.main_interface
```

You can also run both the API server and the test interface:
1. **Start the API server** (in one terminal):
   ```bash
   python base_module/app.py
   ```
   This starts the FastAPI server on port 1111, providing the `/v1/chat/completions` endpoint.

2. **Run the test interface** (in another terminal):
   ```bash
   python base_module/main_interface.py
   ```
   This provides an interactive CLI to test the agent. Type your messages and press Enter. Type `exit` or `quit` to stop.

`state_module/state_graph.yaml` controls the conversation flow. Update it before launching the agent if you need different transitions or tool entry points.

## Tooling & Extensibility Notes
- Register additional tools by extending the interfaces in `tool_module/` and wiring them into `Agent`.
- `Memory` writes each state change to CSV; clear the file between experiments if you want a fresh run.
- The `.github/PULL_REQUEST_GUIDELINES.md` file outlines expectations for future contributions and should accompany any PR raised from this branch.

## Testing Status
Automated tests are currently stubbed out (`model_module/tests_arkmodel.py`) and require updates because `ArkModelLink.make_llm_call` is synchronous. Treat them as examples rather than runnable checks until the test harness is repaired.

## Contributors + contact

| Name                  | Role           | GitHub username | Affiliation   |
| --------------------  | -------------- | --------------- | --------------|
| Nathaniel Morgan      | Project leader | nmorgan         | MIT           |
| Joshua Guo            | Frontend       | duck_master     | MIT           |
| Ilya Gulko            | Backend        | gulkily         | MIT           |
| Jack Luo              | Backend        | thejackluo      | Georgia Tech  |
| Bryce Roberts         | Backend        | BryceRoberts13  | MIT           |
| Angela Liu            | Backend        | angelaliu6      | MIT           |
| Ishaana Misra         | Backend        | ishaanam        | MIT           |
| Hudson Hilal          | Backend        | hhilal123       | MIT           |
| Calvin Baker          | Backend        | Calvinlb404     | MIT           |

## License
This project is licensed under the GNU Affero General Public License v3.0. See `LICENSE.txt` for details.
