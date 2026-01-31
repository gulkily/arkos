# Docker Images Reference

This document lists Docker images referenced by the repo and explains what each one does. It separates currently used images from deprecated or proposal-only images.

## Active images (current workflow)

### `lmsysorg/sglang:latest`
- **Used by**: `model_module/run.sh`
- **Purpose**: Runs the SGLang OpenAI-compatible inference server.
- **Notes**:
  - Exposes the API on `http://localhost:30000/v1` by default.
  - Requires a GPU and a Hugging Face token for gated models (`HF_TOKEN`).
  - Mounts `~/.cache/huggingface` into the container to cache model weights.

### `ghcr.io/open-webui/open-webui:main`
- **Used by**: `docs/ops/openwebui_setup.md`, `docs/ops/openwebui_deployment_plan.md`
- **Purpose**: Provides the OpenWebUI web interface and chat orchestration.
- **Notes**:
  - Typically run behind a reverse proxy.
  - Connects to the ARKOS API via `OPENAI_API_BASE` (pointing at `base_module`).

### `caddy:2`
- **Used by**: `docs/ops/openwebui_setup.md`, `docs/ops/openwebui_deployment_plan.md`, `docs/ops/openwebui_tls_setup.md`
- **Purpose**: TLS-enabled reverse proxy for OpenWebUI and the ARKOS API.
- **Notes**:
  - Terminate TLS and proxy `/v1/*` to the ARKOS API.
  - Keep certificates in a persistent volume.

## Deprecated images (legacy scripts)

### `ghcr.io/huggingface/text-generation-inference:latest`
- **Used by**: `model_module/depricated/hf_tgi.sh` (legacy)
- **Purpose**: Old TGI-based LLM serving workflow.
- **Notes**: Deprecated; prefer SGLang in `model_module/run.sh`.

### `ghcr.io/huggingface/text-generation-inference:2.0`
- **Used by**: `model_module/depricated/hftgi_2.sh` (legacy)
- **Purpose**: Older TGI serving script.
- **Notes**: Deprecated; prefer SGLang in `model_module/run.sh`.

## Proposal-only images (not wired in code)

### `ghcr.io/github/github-mcp-server`
- **Used by**: `mcp_integration_proposal.md` examples
- **Purpose**: Example MCP server image for GitHub integration.
- **Notes**: Proposal only; not configured in current code paths.
