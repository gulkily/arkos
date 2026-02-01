# Documentation Update Checklist

Derived from repo/code vs current docs.

- [x] `docs/guide/web_ui.md`: `base_module_web/` is not tracked in `HEAD`; either add the module or mark this guide as out-of-tree/experimental and remove the `/sessions`/`SessionPayload` claims.
- [x] `docs/ops/base_module_web_ubuntu_hosting.md`: endpoints (`/healthz`, `/sessions`) and env vars (`ARK_BASIC_USER/PASS`, `ARK_WEB_VERSION`) don’t exist in repo; update to match real code or move this runbook to an external/prototype section.
- [x] `docs/ops/openwebui_setup.md`: “ARK base module API” currently points to `:30000` (LLM) not `base_module` (`:1112`); decide target and update `OPENAI_API_BASE`, proxy routes, and wording.
- [x] `docs/ops/openwebui_deployment_plan.md`: same `OPENAI_API_BASE`/reverse-proxy mismatch as above; align with intended backend.
- [x] `docs/guide/tools.md`: `tool_module/auth_once.py` reads/writes `secrets/*` relative to CWD; update doc to `cd tool_module` before running or update paths to `tool_module/secrets/...`.
- [x] `docs/guide/tools.md`: `state_module/state_calendar.py` currently returns a placeholder and does not call MCP by default; document that it’s stubbed and how to enable actual tool calls.
- [x] `docs/guide/cli_agent.md`: “set `OPENAI_API_KEY` for Mem0” is inaccurate with current code (it hard-sets "sk"); clarify whether it’s required or remove.
- [x] `docs/guide/cli_agent.md`: config mentions `memory.user_id` and “memory limits,” but `Agent.get_context()` is hard-coded (`turns=5`, mem0 default `50`); document that limits are currently not wired.
- [x] `docs/reference/state_and_memory.md`: add that Mem0 is configured in `memory_module/memory.py` with `supabase` vector store, `vllm_base_url` and `huggingface_base_url` (`http://localhost:30000/v1` and `http://localhost:4444/v1`) and that these are not pulled from `config_module/config.yaml`.
- [x] `docs/reference/state_and_memory.md` and `README.md`: document required Postgres schema for `conversation_context` (table name/columns) since the code assumes it exists.
- [x] `README.md` and `docs/guide/cli_agent.md`: clarify whether the embedding service at `:4444` is required for Mem0 and how to run it (or mark as optional/stub).
- [x] `docs/documentation_audit_plan.md`: update inventory to reflect that `base_module_web/` is untracked in this repo.
- [x] `docs/ops/README.md`: fill the TODO items (model backend ops, backups, monitoring) or explicitly defer them with links/tickets.
- [x] Document Docker images used by the repo (see `docs/ops/docker_images.md`).

## New items from recent tool/auth commits
- [x] Document `mcp_servers` config in `config_module/config.yaml` (transport, stdio/HTTP fields, env vars) and update `docs/guide/tools.md` accordingly.
- [x] Document per-user MCP OAuth flow: `base_module/auth.py` endpoints (`/auth/google/login`, `/auth/google/callback`, `/auth/google/status`, `/auth/google/disconnect`) and required env vars (`GOOGLE_OAUTH_CREDENTIALS`).
- [ ] Document `tool_module/token_store.py` and the `user_oauth_tokens` Postgres table schema; note token file export to `~/.arkos/user_tokens/`.
- [ ] Document `tool_module/transports/*` (stdio + HTTP transport, OAuth PKCE flow, token cache at `~/.arkos/mcp_tokens.json`).
- [ ] Update API docs to mention `X-User-ID` header or `user_id` payload field for per-user tool auth in `/v1/chat/completions`.
- [ ] Update dependencies list in `README.md` to include `aiohttp` and `google-auth-oauthlib` (used by HTTP transport and Google OAuth).
