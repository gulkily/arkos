# OpenWebUI Deployment Plan (Ubuntu 24.04 LTS)

## Objective
Stand up OpenWebUI alongside the ARK stack so stakeholders get a polished interface while engineering keeps the custom pipeline intact.

## Prerequisites
- Ubuntu 24.04 server with sudo access, outbound network, and ≥16GB RAM (OpenWebUI + LLM backend).
- Docker 24.x and Docker Compose 2.x installed.
- Accessible ARK base module API (OpenAI-compatible endpoint, e.g., `http://ark-backend.internal:30000/v1`).
- TLS certificate (Let's Encrypt via Caddy/NGINX or internal CA) if external access required.

## Architecture Overview
- `openwebui` container provides UI + chat orchestration.
- Existing `ark-base` backend continues running on current port.
- Reverse proxy (Caddy recommended for TLS automation) terminates HTTPS and routes `/` to OpenWebUI, `/ark` (or `/v1`) to ARK API.
- Persistent storage volume for OpenWebUI data (`/srv/openwebui/data`).

## Deployment Steps
### 1. Prepare Host
```bash
sudo apt update && sudo apt install -y docker.io docker-compose-plugin
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
# log out/in to refresh group membership
```

### 2. Directory Layout
```
/srv/openwebui/
  docker-compose.yml
  env/
    openwebui.env
  caddy/
    Caddyfile
  data/
    (bind mount target for persistent storage)
```

### 3. Compose File (`docker-compose.yml`)
```yaml
services:
  openwebui:
    image: ghcr.io/open-webui/open-webui:main
    env_file: env/openwebui.env
    volumes:
      - ./data:/app/backend/data
    ports:
      - 127.0.0.1:4000:8080
    restart: unless-stopped

  caddy:
    image: caddy:2
    volumes:
      - ./caddy/Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy_data:/data
    ports:
      - 80:80
      - 443:443
    depends_on:
      - openwebui

volumes:
  caddy_data:
```

### 4. Environment Variables (`env/openwebui.env`)
```
OPENAI_API_BASE=http://ark-backend.internal:30000/v1
OPENAI_API_KEY=ark-placeholder-key
DEFAULT_MODEL=ark
```
(Replace hostnames and keys per environment.)

### 5. Reverse Proxy (`caddy/Caddyfile`)
```
ark.example.com {
    encode gzip

    @ark path /v1/*
    handle @ark {
        reverse_proxy ark-backend.internal:30000
    }

    handle {
        reverse_proxy 127.0.0.1:4000
    }
}
```
Use `tls internal` if operating on an internal-only network.

### 6. Launch Stack
```bash
cd /srv/openwebui
sudo docker compose up -d
sudo docker compose ps
```

### 7. Post-Deployment Checklist
- Complete OpenWebUI onboarding and set admin credentials.
- Configure auth providers (GitHub OAuth/SSO) if required.
- Wire logs into existing monitoring (e.g., ship `docker logs` to Loki/ELK).
- Document support contacts and update on-call SOPs.

## Maintenance Playbook
- Monthly container updates: `docker compose pull && docker compose up -d`.
- Nightly backup `/srv/openwebui/data` (rsync or snapshot).
- Regression test after ARK API changes (ensure `/v1/chat/completions` contract intact).
- Pin image digest to avoid upstream regressions.

## Risks & Mitigations
- **Resource contention**: provision sufficient CPU/GPU; consider dedicating inference nodes.
- **Version drift**: maintain staging deployment; pin image digests.
- **Security**: enforce TLS, require strong admin creds, restrict network access (VPN or allowlist).
- **Vendor churn**: OpenWebUI roadmap may diverge; keep custom FastAPI UI as fallback.

## Next Steps
1. Confirm hardware sizing and network placement with DevOps.
2. Pilot on staging, gather feedback.
3. Schedule production cutover with stakeholders and support.
