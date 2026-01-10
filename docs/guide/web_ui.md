# Base Module Web UI Overview

`base_module_web/` contains an experimental FastAPI application that wraps the same agent used by the CLI. It is not production-ready yet, but this guide documents the current behavior so you can evaluate or extend it.

## Entry points
- `base_module_web/app.py` – FastAPI app with routes for session creation and message handling.
- `base_module_web/static/index.html` – Single-page frontend consuming the REST endpoints.
- `base_module_web/data/` – Directory where session transcripts are stored if persistence is enabled.

## FastAPI application
- Adds basic auth middleware (`_BasicAuthMiddleware`) with credentials set via `ARK_BASIC_USER` and `ARK_BASIC_PASS` (default `ark/arkos`).
- Exposes session endpoints returning `SessionPayload` objects:
  - `POST /sessions` – Create a session.
  - `POST /sessions/{id}/message` – Send a user message and receive updated history.
  - `DELETE /sessions/{id}` – Remove a session and clean up the associated memory file.
- Uses the same `Agent`, `Memory`, and `ArkModelLink` classes from the CLI, so the backend behavior is consistent.

## Response model
`SessionPayload` contains:
- `session_id`
- `messages` – list of message dicts (`role`, `content`, optional `render_type`/`payload`).
- `status` – defaults to `"ok"`.

Tool metadata is not yet captured; the `tool_events` array mentioned in planning documents remains a TODO.

## Static frontend
- Renders a basic chat transcript using vanilla JavaScript.
- Provides message input, session persistence, and minimal error handling.
- Does not yet visualize tool calls or latency.

## Deployment notes
- Run locally with `uvicorn base_module_web.app:app --reload` after setting the `ARK_` environment variables.
- The `docs/ops/base_module_web_ubuntu_hosting.md` runbook covers systemd setup and TLS via nginx.
- For now, prefer deploying OpenWebUI if you need a polished UI—see `docs/ops/openwebui_*`.

## Roadmap highlights
- Capture latency and tool events in the backend payloads.
- Build richer frontend components (sidebar, settings drawer, toasts).
- Coordinate auth and deployment story with the rest of the stack.

The documentation audit will keep this page updated as the prototype evolves.
