# OpenWebUI Plan Compatibility Review

## Scope
Evaluate whether the documented OpenWebUI deployment plan/runbook fits the current ARK repository architecture, particularly the way `base_module` and `base_module_web` reach language models via `ArkModelLink`.

## Findings
- **Shared endpoint expectations**: Both `base_module/main_interface.py` (`llm = ArkModelLink(base_url="http://localhost:30000/v1")`) and `base_module_web/app.py` (`ARK_LLM_BASE_URL` defaulting to `http://localhost:30000/v1`) depend on an OpenAI-compatible endpoint at port 30000. The deployment plan points `OPENAI_API_BASE` to `http://ark-backend.internal:30000/v1`, matching the same contract. ✅
- **Backend implementation**: `model_module/run.sh` launches `lmsysorg/sglang` as a chat-completions server on port 30000, which already satisfies OpenWebUI's expected API surface (`POST /v1/chat/completions`, optional streaming). No additional adapter layer is required. ✅
- **Authentication model**: `ArkModelLink` passes a dummy API key (`"-"`). OpenWebUI can mirror this with the placeholder key specified in `openwebui.env`; the backend currently does not enforce key validation, so no extra work is needed. ✅
- **Reverse proxy routing**: The plan's Caddyfile forwards `/v1/*` to `ark-backend.internal:30000`. This preserves the path structure, so existing clients (including `base_module_web` if pointed through the proxy) continue to function. Ensure DNS / networking allows the Caddy container to reach the SGLang host. ✅
- **Potential adjustments**:
  - If the SGLang container runs on the same host as OpenWebUI, update the proxy target to `127.0.0.1:30000` or Docker service name.
  - Confirm streaming support is enabled in SGLang if OpenWebUI users toggle streaming responses; otherwise disable streaming in OpenWebUI settings.
  - Document resource requirements (GPU pass-through) when co-hosting SGLang and OpenWebUI; avoid GPU contention by running on separate nodes or using different devices.

## Conclusion
The OpenWebUI deployment plan and setup guide align with the current ARK LLM access pattern. Deploying OpenWebUI as described will allow it to reuse the existing OpenAI-compatible endpoint that powers `base_module` and `base_module_web`. Only environment-specific wiring (network/DNS, optional streaming, GPU scheduling) needs verification during rollout.
