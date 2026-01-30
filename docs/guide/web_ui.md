# Base Module Web UI Overview

`base_module_web/` contains an experimental FastAPI application that wraps the same agent used by the CLI. That module is not tracked in this repository right now, so this guide only applies if you have a local prototype copy (for example, from an internal branch or working directory). Treat the details below as best-effort notes that may drift from your local version.

## Entry points (prototype only)
- `base_module_web/app.py` – FastAPI app with routes for message handling.
- `base_module_web/static/index.html` – Single-page frontend consuming the REST endpoints.
- `base_module_web/data/` – Directory where session transcripts are stored if persistence is enabled.

## FastAPI application
- Uses the same `Agent`, `Memory`, and `ArkModelLink` classes from the CLI, so the backend behavior is consistent.
- Endpoint shapes, auth middleware, and response payloads depend on the specific prototype version you are running. Confirm routes and schemas in your local `base_module_web/app.py`.

## Response model
Tool metadata is not yet captured; the `tool_events` array mentioned in planning documents remains a TODO in the prototype.

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
