# Documentation Update Checklist

Derived from repo/code vs current docs.

- [ ] `docs/guide/web_ui.md`: `base_module_web/` is not tracked in `HEAD`; either add the module or mark this guide as out-of-tree/experimental and remove the `/sessions`/`SessionPayload` claims.
- [ ] `docs/ops/base_module_web_ubuntu_hosting.md`: endpoints (`/healthz`, `/sessions`) and env vars (`ARK_BASIC_USER/PASS`, `ARK_WEB_VERSION`) don’t exist in repo; update to match real code or move this runbook to an external/prototype section.
- [ ] `docs/ops/openwebui_setup.md`: “ARK base module API” currently points to `:30000` (LLM) not `base_module` (`:1112`); decide target and update `OPENAI_API_BASE`, proxy routes, and wording.
- [ ] `docs/ops/openwebui_deployment_plan.md`: same `OPENAI_API_BASE`/reverse-proxy mismatch as above; align with intended backend.
- [ ] `docs/guide/tools.md`: `tool_module/auth_once.py` reads/writes `secrets/*` relative to CWD; update doc to `cd tool_module` before running or update paths to `tool_module/secrets/...`.
- [ ] `docs/guide/tools.md`: `state_module/state_calendar.py` currently returns a placeholder and does not call MCP by default; document that it’s stubbed and how to enable actual tool calls.
- [ ] `docs/guide/cli_agent.md`: “set `OPENAI_API_KEY` for Mem0” is inaccurate with current code (it hard-sets "sk"); clarify whether it’s required or remove.
- [ ] `docs/guide/cli_agent.md`: config mentions `memory.user_id` and “memory limits,” but `Agent.get_context()` is hard-coded (`turns=5`, mem0 default `50`); document that limits are currently not wired.
- [ ] `docs/reference/state_and_memory.md`: add that Mem0 is configured in `memory_module/memory.py` with `supabase` vector store, `vllm_base_url` and `huggingface_base_url` (`http://localhost:30000/v1` and `http://localhost:4444/v1`) and that these are not pulled from `config_module/config.yaml`.
- [ ] `docs/reference/state_and_memory.md` and `README.md`: document required Postgres schema for `conversation_context` (table name/columns) since the code assumes it exists.
- [ ] `README.md` and `docs/guide/cli_agent.md`: clarify whether the embedding service at `:4444` is required for Mem0 and how to run it (or mark as optional/stub).
- [ ] `docs/documentation_audit_plan.md`: update inventory to reflect that `base_module_web/` is untracked in this repo.
- [ ] `docs/ops/README.md`: fill the TODO items (model backend ops, backups, monitoring) or explicitly defer them with links/tickets.
