# OpenWebUI Deployment Config

These manifests mirror the production stack deployed on `ark.mit.edu`. They assume the compose project is placed on the host at `/srv/openwebui` as described in `docs/openwebui_setup.md`.

## Contents
- `docker-compose.yml` – OpenWebUI + Caddy reverse proxy
- `caddy/Caddyfile` – HTTPS termination and routing rules
- `caddy/certs/` – expected location for organization-issued TLS assets
- `env/openwebui.env.example` – sample environment file for API wiring

## Usage
1. Copy this directory to the target host (`/srv/openwebui` recommended).
2. Duplicate `env/openwebui.env.example` to `env/openwebui.env` and adjust secrets / endpoints.
3. Update `docker-compose.yml`:
   - If `ark-backend.internal` resolves via DNS, remove the `extra_hosts` entry.
   - Otherwise, replace `172.17.0.1` with the Docker bridge IP (`ip addr show docker0`).
4. Provide TLS certificates:
   - Place `ark.mit.edu.key` and `ark.mit.edu.crt` (plus chain if required) in `caddy/certs/`.
   - Edit the Caddyfile to switch between org-issued certs (`tls /certs/…`) and `tls internal` for local CA.
5. Launch the stack with `docker compose up -d`.

For detailed operational guidance (backups, troubleshooting, TLS options) refer to:
- `docs/openwebui_setup.md`
- `docs/openwebui_tls_setup.md`
