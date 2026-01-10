# Base Module FastAPI UI Plan

## Goal
Deliver a lightweight, bespoke web UI for the ARK base module that showcases core agent capabilities, is easy to operate on our Ubuntu 24.04 servers, and stays fully under our control (no third-party UI dependency).

## High-Level Architecture
- **FastAPI backend (`base_module_web/app.py`)** handles session lifecycle, auth, and interaction with the existing `Agent`.
- **Static single-page frontend (`base_module_web/static/index.html`)** consumes REST endpoints for session create/send/delete.
- **Memory persistence** via CSV files in `base_module_web/data/` (one file per session, reuseable with current `Memory` implementation).
- **Auth layer** using basic auth initially; pluggable to OAuth/OpenID if required.

## Deliverables
1. **Backend hardening**
   - Health endpoint for uptime checks (`/healthz`).
   - Config-driven settings (`Settings` class reading env vars, using `pydantic-settings`).
   - Structured logging (standard library `logging` + request IDs).
   - Graceful session cleanup endpoint (delete memory artifacts).
   - Optional rate limiting (via `slowapi` or custom middleware) for multi-user safety.

2. **Frontend polish**
   - Responsive chat layout with conversation timeline and agent metadata.
   - Streaming indicator (spinner) while waiting on backend.
   - Settings drawer for toggling temperature, system prompt override (POST to new endpoint).
   - Keyboard accessibility and optimized focus management.

3. **Tooling**
   - `uvicorn` run script (`python -m base_module_web.app` or `scripts/run_web.sh`).
   - Dockerfile + `docker-compose.yml` for self-contained deployment (maps to systemd service).
   - CI job to run `ruff`/`pytest` against web package.

4. **Documentation**
   - README covering setup, env vars, and deployment.
   - Architecture diagram (PlantUML or Mermaid) describing request flow.
   - Playbook for operations (logs, restarting service, rotating basic auth credentials).

## Endpoint Design
| Method | Path | Description |
| ------ | ---- | ----------- |
| GET | `/` | Serve SPA (static).
| GET | `/healthz` | Returns status + build info.
| POST | `/sessions` | Create new session; returns `session_id` and history.
| POST | `/sessions/{id}/message` | Append user message, invoke agent, return updated history.
| DELETE | `/sessions/{id}` | End session, delete in-memory state, optionally remove persisted memory file.
| GET | `/sessions/{id}` | (Optional) Return metadata + history without sending message.
| PATCH | `/sessions/{id}/settings` | Update per-session params (temperature, system prompt). Future enhancement.

## Implementation Phases
1. **Stabilize foundation (Day 0–1)**
   - Ensure package lives under `base_module_web/` (done).
   - Add settings module, health route, consistent responses, and tidy middleware (basic auth opt-in for local dev).
   - Write smoke tests using `httpx.AsyncClient`.

2. **Frontend polish (Day 2–3)**
   - Refine styling, add loading states, display per-message timestamps.
   - Add error banners with retry guidance.
   - Implement settings drawer and call new backend endpoints.

3. **Deployment tooling (Day 3–4)**
   - Provide Dockerfile + Compose (mirrors prod patterns).
   - Draft systemd unit file template.
   - Document ops runbook.

4. **Stretch goals (Day 5+)**
   - WebSocket-based streaming (if backend gains streaming support).
   - Multi-user accounts (JWT + OAuth integration).
   - Integrated analytics/feedback collection.

## Pitch Points
- **Ownership**: zero external UI dependency; look & feel aligns with ARK branding.
- **Performance**: minimal runtime footprint (FastAPI + static assets).
- **Extendability**: can surface agent tools, memory timeline, and custom workflows quickly.
- **Security**: only exposes what we design; easier to comply with internal policies vs. upstream UI releases.

## Next Actions
1. Confirm feature priorities with stakeholders (auth level, session persistence requirements, streaming needs).
2. Implement Phase 1 changes and demo to team.
3. Iterate UI based on feedback, then package for deployment alongside OpenWebUI pilot.
