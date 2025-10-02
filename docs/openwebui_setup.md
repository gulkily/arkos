# OpenWebUI Setup Runbook

This runbook walks through installing and operating OpenWebUI on Ubuntu 24.04, wired into the ARK base module API. 
It complements the higher-level plan in `openwebui_deployment_plan.md` by focusing on actionable steps.

## 1. Host Preparation
1. Update packages and install Docker tooling:
   ```bash
   sudo apt update
   sudo apt install -y docker.io docker-compose-plugin
   sudo systemctl enable --now docker
   sudo usermod -aG docker $USER
   ```
   Log out/in (or run a new shell with `newgrp docker`) to pick up group membership.
2. Create a dedicated directory structure:
   ```bash
   sudo mkdir -p /srv/openwebui/{env,caddy,data}
   sudo chown -R $USER:docker /srv/openwebui
   ```
3. (Optional) Reserve DNS entry `arkui.example.com` pointing to the server.

## 2. Compose Stack
Create `/srv/openwebui/docker-compose.yml`:
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
> Pin the image digest (`ghcr.io/open-webui/open-webui@sha256:...`) when promoting to production.

## 3. Environment Variables
Create `/srv/openwebui/env/openwebui.env`:
```
OPENAI_API_BASE=http://ark-backend.internal:30000/v1
OPENAI_API_KEY=ark-placeholder-key
DEFAULT_MODEL=ark
ENABLE_LOGIN=true
DISABLE_TELEMETRY=true
```
Adjust values for your environment; `ENABLE_LOGIN` ensures the onboarding flow enforces credentials.

## 4. Reverse Proxy (Caddy)
Write `/srv/openwebui/caddy/Caddyfile`:
```
arkui.example.com {
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
- Replace hostnames with real values.
- For internal-only deployments add `tls internal` inside the site block.

## 5. Launch & Verify
```bash
cd /srv/openwebui
sudo docker compose up -d
sudo docker compose ps
```
Check logs:
```bash
sudo docker compose logs -f openwebui
```
Browse to `https://arkui.example.com` and follow onboarding to create the first admin user. Confirm you can:
- Connect to ARK backend (send prompt, receive response).
- Access the reverse-proxied `/v1/` path (for other clients).

## 6. Maintenance Tasks
- **Updates**: `sudo docker compose pull && sudo docker compose up -d` (monthly or as needed).
- **Backups**: capture `/srv/openwebui/data` (conversation history/config) on a daily schedule.
- **Monitoring**: expose Caddy metrics or tail logs into your observability stack; add synthetic checks hitting `/login` and `/v1/chat/completions`.
- **Security**: rotate admin passwords, enable SSO/OAuth inside OpenWebUI settings, restrict firewall (e.g., ufw allow 80/443 from trusted CIDRs).

## 7. Troubleshooting
| Symptom | Likely Cause | Remedy |
| ------- | ------------ | ------ |
| 502 from browser | Caddy can’t reach OpenWebUI | Check container status, confirm port mapping `127.0.0.1:4000:8080`. |
| Login loop | Cookies blocked or time skew | Ensure HTTPS, correct system time (`chrony`). |
| “Failed to reach OpenAI backend” | ARK endpoint unreachable | Validate `OPENAI_API_BASE`, ensure backend allows traffic from OpenWebUI host. |
| Large uploads fail | Default body size limits | Add `header_up` and `request_body` adjustments in Caddyfile if needed. |

## 8. Teardown
To stop temporarily: `sudo docker compose down`. To remove all data: `sudo docker compose down -v && sudo rm -rf /srv/openwebui/data` (only after confirming no records must be retained).

## 9. Next Enhancements
- Add staging stack mirroring production for OpenWebUI upgrades.
- Configure Let’s Encrypt DNS challenge if running behind restricted firewall.
- Integrate with internal identity provider (Keycloak/OAuth) via OpenWebUI admin settings.
- Automate deployment through Ansible/Terraform once process stabilizes.
