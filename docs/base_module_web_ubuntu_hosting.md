# Base Module Web UI – Ubuntu Hosting Guide

## Overview
Deploy the bespoke FastAPI UI (`base_module_web`) on Ubuntu 24.04, ensure it runs under systemd, and front it with a TLS-enabled reverse proxy so teammates can access it securely.

## 1. Prepare Server
1. **Create service account and directories**
   ```bash
   sudo adduser --system --group arkweb
   sudo mkdir -p /opt/arkos
   sudo chown arkweb:arkweb /opt/arkos
   ```
2. **Install Python tooling**
   ```bash
   sudo apt update
   sudo apt install -y python3-venv
   ```
3. **Clone/sync project** into `/opt/arkos` (git, rsync, or scp) and make sure `base_module_web/data/` is writable by `arkweb`.

## 2. Virtual Environment & Dependencies
```bash
sudo -u arkweb python3 -m venv /opt/arkos/.venv
sudo -u arkweb /opt/arkos/.venv/bin/pip install --upgrade pip
sudo -u arkweb /opt/arkos/.venv/bin/pip install -r /opt/arkos/requirements.txt uvicorn
```

## 3. Environment Configuration
Set values in `/etc/ark-base-web.env` (readable by `arkweb`):
```
ARK_BASIC_USER=ark
ARK_BASIC_PASS=arkos
ARK_LLM_BASE_URL=http://127.0.0.1:30000/v1
ARK_WEB_VERSION=0.2.0
```
You can extend this file as new settings land in `base_module_web/app.py`.

## 4. systemd Service
Create `/etc/systemd/system/ark-base-web.service`:
```
[Unit]
Description=ARK Base Module Web UI
After=network.target

[Service]
User=arkweb
Group=arkweb
EnvironmentFile=/etc/ark-base-web.env
WorkingDirectory=/opt/arkos
ExecStart=/opt/arkos/.venv/bin/uvicorn base_module_web.app:app \
  --host 127.0.0.1 --port 8100 --proxy-headers --forwarded-allow-ips="*"
Restart=on-failure
RuntimeDirectory=ark-base-web
RuntimeDirectoryMode=0750

[Install]
WantedBy=multi-user.target
```
Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now ark-base-web
```
Check status:
```bash
sudo systemctl status ark-base-web
journalctl -u ark-base-web -f
```

## 5. Reverse Proxy (nginx example)
1. Install nginx: `sudo apt install -y nginx`.
2. Create `/etc/nginx/sites-available/ark-base-web`:
```
server {
    listen 80;
    listen 443 ssl http2;
    server_name ark.example.com;

    # TLS config here (certbot or internal CA)

    location /healthz {
        proxy_pass http://127.0.0.1:8100/healthz;
    }

    location / {
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        auth_basic "Restricted";
        auth_basic_user_file /etc/nginx/.htpasswd; # optional if middleware handles auth
        proxy_pass http://127.0.0.1:8100/;
    }
}
```
3. Enable site: `sudo ln -s /etc/nginx/sites-available/ark-base-web /etc/nginx/sites-enabled/`.
4. Reload nginx: `sudo nginx -t && sudo systemctl reload nginx`.
5. If using Let’s Encrypt: `sudo certbot --nginx -d ark.example.com`.

## 6. Monitoring & Maintenance
- **Health checks**: `curl -fsS http://127.0.0.1:8100/healthz` (hook into uptime robot/Zabbix).
- **Logs**: `journalctl -u ark-base-web`. Pipe into centralized logging if available.
- **Backups**: archive `/opt/arkos/base_module_web/data/` since it contains session memories.
- **Updates**: pull repo, reinstall dependencies, and restart service (`sudo systemctl restart ark-base-web`).
- **Security**: rotate creds in `/etc/ark-base-web.env`, scope firewall to trusted networks, and keep nginx/TLS up-to-date.

## 7. Troubleshooting Tips
- 502/504 errors: check `nginx` logs (`/var/log/nginx/error.log`) and service logs.
- Permission denied on memory files: verify directory ownership (`sudo chown arkweb:arkweb base_module_web/data`).
- Proxy auth conflicts: disable middleware auth by setting empty `ARK_BASIC_USER/PASS` or remove nginx `auth_basic`.
- LLM unavailable: `/sessions` payload shows `status="error"`; confirm `ARK_LLM_BASE_URL` and backend availability.
