# OpenWebUI TLS Setup & Troubleshooting

This guide captures the TLS fixes discussed for running OpenWebUI behind Caddy when automatic Let’s Encrypt issuance fails.

## 1. Diagnose TLS Failures
- Check Caddy logs: `sudo docker compose logs caddy`.
- Errors like `acme:error:rejectedIdentifier` mean the CA refuses the domain (e.g., sample domains or restricted hostnames).
- Confirm DNS A/AAAA records point to the server and ports 80/443 are reachable.
- Ensure the Caddyfile site label matches the real hostname (`ark.mit.edu`, not `arkui.example.com`).

## 2. Using an Organization-Issued Certificate
1. **Generate CSR & key**
   ```bash
   openssl req -new -newkey rsa:4096 -nodes \
     -keyout ark.mit.edu.key \
     -out ark.mit.edu.csr \
     -subj "/CN=ark.mit.edu"
   ```
2. **Request certificate**
   - Submit `ark.mit.edu.csr` to your org’s CA portal (MIT IS&T for `mit.edu`).
   - Download the issued leaf cert and any intermediate chain.
3. **Place certs on host**
   ```bash
   sudo mkdir -p /srv/openwebui/caddy/certs
   sudo mv ark.mit.edu.key ark.mit.edu.crt /srv/openwebui/caddy/certs/
   sudo chmod 600 /srv/openwebui/caddy/certs/ark.mit.edu.key
   ```
   - If a separate chain file is provided, concatenate: `cat ark.mit.edu.crt chain.pem > fullchain.pem`.
4. **Mount into Caddy** (`/srv/openwebui/docker-compose.yml`)
   ```yaml
   services:
     caddy:
       volumes:
         - ./caddy/Caddyfile:/etc/caddy/Caddyfile:ro
         - ./caddy/certs:/certs:ro
   ```
5. **Reference in Caddyfile** (`/srv/openwebui/caddy/Caddyfile`)
   ```
   ark.mit.edu {
       tls /certs/ark.mit.edu.crt /certs/ark.mit.edu.key
       encode gzip
       # reverse_proxy blocks...
   }
   ```
6. **Reload Caddy**
   ```bash
   sudo docker compose exec caddy caddy reload
   # If reload fails due to new volume, restart:
   sudo docker compose up -d caddy
   ```
7. **Verify**
   ```bash
   curl -vk https://ark.mit.edu
   ```
   Check that the certificate chain matches the issued cert.

## 3. Internal-Only Self-Signed Option
Use this path when the hostname cannot receive a publicly trusted certificate but you still need HTTPS inside a trusted network.

1. **Update the Caddyfile**
   ```
   ark.mit.edu {
       tls internal
       encode gzip
       # reverse_proxy blocks…
   }
   ```
   - Remove any previous `tls` line to avoid conflicts.
   - `tls internal` tells Caddy to issue and manage a cert signed by its built-in local CA.

2. **Reload Caddy**
   ```bash
   sudo docker compose exec caddy caddy reload
   ```
   - On reload, Caddy will create a new local CA (if not already present) and generate a cert for `ark.mit.edu` in `/data/caddy/pki` inside the container.

3. **Export the local CA certificate**
   ```bash
   sudo docker cp caddy:/data/caddy/pki/authorities/local/root.crt ./caddy-root.crt
   ```
   - Keep this file safe; any client that trusts it will accept certificates issued by your Caddy instance.

4. **Trust the CA on clients**
   - **Linux (system-wide)**: copy `caddy-root.crt` into `/usr/local/share/ca-certificates/`, then run `sudo update-ca-certificates`.
   - **macOS**: open Keychain Access → System → Certificates → import `caddy-root.crt`, set it to “Always Trust”.
   - **Windows**: run `certmgr.msc`, import into “Trusted Root Certification Authorities”.
   - Browsers with their own stores (Firefox): Preferences → Privacy & Security → Certificates → View Certificates → Authorities → Import.

5. **Verify**
   ```bash
   curl -vk https://ark.mit.edu --cacert caddy-root.crt
   ```
   - After the CA is trusted locally, browsers should load the page without warnings.

6. **Cleanup when switching to official certs**
   - Remove possession of the root CA file from shared locations.
   - Update the Caddyfile to remove `tls internal` and add the real `tls /certs/...` directive (see section 2).
   - Reload Caddy and verify that clients now see the organization-issued certificate chain. Clients will continue to trust the internal CA, but it will no longer be used.

## 4. Common Pitfalls
- Forgetting to update the Caddyfile hostname after using the sample domain.
- Missing DNS or firewall changes preventing Let’s Encrypt HTTP-01 challenge.
- Not mounting the cert directory into the container (Caddy cannot read host files).
- Incorrect file permissions (Caddy needs read access; keep the private key 600).
- Browser still caching the failed certificate; force-refresh or clear the TLS state after fixes.

## 5. Quick Validation Commands
- `sudo docker compose logs caddy` – watch for TLS-related messages.
- `curl -vk https://ark.mit.edu` – check the live certificate chain.
- `openssl s_client -connect ark.mit.edu:443 -servername ark.mit.edu` – deep dive into presented certificates.

With the above steps, Caddy will serve OpenWebUI over HTTPS using either organization-issued certificates or trusted internal ones when ACME automation is not available.
