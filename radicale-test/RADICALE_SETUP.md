# Radicale Server Setup Guide

This guide provides step-by-step instructions for setting up a minimal Radicale CalDAV server for use with the LangChain MCP integration.

## Overview

Radicale is a lightweight CalDAV/CardDAV server that provides calendar and contact synchronization. For this project, we need a running Radicale server to store and manage calendar events.

## Installation Methods

### Method 1: Docker (Recommended)

The easiest way to get started is using Docker:

```bash
# Pull the official Radicale image
docker pull tomsquest/docker-radicale

# Create a data directory
mkdir -p ~/radicale-data

# Run Radicale with basic authentication
docker run -d \
  --name radicale \
  -p 5232:5232 \
  -v ~/radicale-data:/data \
  -e RADICALE_CONFIG_FILE=/data/config \
  tomsquest/docker-radicale
```

### Method 2: Python Package Installation

Install Radicale directly via pip:

```bash
# Install Radicale
pip install radicale

# Optional: Install additional authentication backends
pip install radicale[bcrypt]
```

### Method 3: System Package Manager

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install radicale
```

**macOS (Homebrew):**
```bash
brew install radicale
```

## Configuration

### Basic Configuration

Create a configuration file (`~/.config/radicale/config` or `/etc/radicale/config`):

```ini
[server]
# Bind to all interfaces
hosts = 0.0.0.0:5232

[auth]
# Use htpasswd for authentication
type = htpasswd
htpasswd_filename = /path/to/users
htpasswd_encryption = bcrypt

[storage]
# Use filesystem storage
type = multifilesystem
filesystem_folder = /path/to/collections

[web]
# Enable web interface
base_prefix = /

[logging]
# Set log level
level = info
```

### Minimal Development Configuration

For development/testing, create a simple config file:

```ini
[server]
hosts = localhost:5232

[auth]
# No authentication for development (INSECURE)
type = none

[storage]
type = multifilesystem
filesystem_folder = ~/.local/share/radicale/collections

[web]
base_prefix = /

[logging]
level = debug
```

### Creating User Accounts

If using htpasswd authentication:

```bash
# Install htpasswd (if not available)
sudo apt install apache2-utils  # Ubuntu/Debian
brew install httpie            # macOS

# Create password file
htpasswd -c /path/to/users username

# Add additional users
htpasswd /path/to/users another_user
```

## Starting Radicale

### Manual Start

```bash
# Start with default configuration
radicale

# Start with custom configuration
radicale --config /path/to/config

# Start on specific host/port
radicale --hosts localhost:5232
```

### Docker Start

```bash
# Start the container
docker start radicale

# Check logs
docker logs radicale

# Stop the container
docker stop radicale
```

### System Service (Linux)

Create a systemd service file `/etc/systemd/system/radicale.service`:

```ini
[Unit]
Description=A simple CalDAV and CardDAV server
After=network.target
Requires=network.target

[Service]
ExecStart=/usr/bin/radicale --config /etc/radicale/config
Restart=on-failure
User=radicale
Group=radicale

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable radicale
sudo systemctl start radicale
sudo systemctl status radicale
```

## Verification

### Check Server Status

```bash
# Test if server is running
curl http://localhost:5232/

# Should return basic server information
```

### Access Web Interface

Open your browser and navigate to:
```
http://localhost:5232/
```

You should see the Radicale web interface.

### Test CalDAV Connection

```bash
# Test with curl
curl -X PROPFIND http://localhost:5232/ \
  -H "Content-Type: text/xml" \
  -d '<?xml version="1.0" encoding="utf-8" ?>
<propfind xmlns="DAV:">
  <prop>
    <displayname/>
  </prop>
</propfind>'
```

## Creating Initial Calendar

### Method 1: Web Interface

1. Navigate to `http://localhost:5232/`
2. Click "Create new calendar"
3. Enter a name (e.g., "Default Calendar")
4. Save the calendar

### Method 2: CalDAV Client

```python
import caldav

# Connect to server
client = caldav.DAVClient(url="http://localhost:5232", username="user", password="pass")
principal = client.principal()

# Create calendar
calendar = principal.make_calendar(name="My Calendar")
print(f"Created calendar: {calendar.name}")
```

### Method 3: Using the Calendar Manager

```python
from radicale_calendar_manager import RadicaleCalendarManager

manager = RadicaleCalendarManager(
    url="http://localhost:5232",
    username="user",  # Leave empty if no auth
    password="pass"   # Leave empty if no auth
)

if manager.connect():
    print(f"Connected! Found {len(manager.calendars)} calendars")
    
    # If no calendars exist, you may need to create one manually
    # or use a CalDAV client to create initial calendar structure
```

## Environment Configuration

Create a `.env` file in your project directory:

```env
# Radicale Server Configuration
RADICALE_URL=http://localhost:5232
RADICALE_USERNAME=your_username
RADICALE_PASSWORD=your_password

# OpenAI Configuration (for LangChain)
OPENAI_API_KEY=your_openai_api_key_here
```

## Troubleshooting

### Common Issues

#### 1. Connection Refused
```
Error: Connection refused to localhost:5232
```
**Solution:** Ensure Radicale server is running:
```bash
# Check if process is running
ps aux | grep radicale

# Check if port is open
netstat -tlnp | grep 5232

# Restart Radicale
radicale --config /path/to/config
```

#### 2. Authentication Errors
```
Error: 401 Unauthorized
```
**Solutions:**
- Check username/password in `.env` file
- Verify htpasswd file exists and is readable
- For development, use `auth.type = none` in config

#### 3. No Calendars Found
```
Warning: No calendars found in Radicale
```
**Solutions:**
- Create a calendar via web interface
- Check storage directory permissions
- Verify filesystem_folder path in config

#### 4. Permission Denied
```
Error: Permission denied writing to collections
```
**Solution:** Fix directory permissions:
```bash
sudo chown -R radicale:radicale /path/to/collections
sudo chmod -R 755 /path/to/collections
```

### Docker Troubleshooting

```bash
# Check container status
docker ps -a

# View container logs
docker logs radicale

# Access container shell
docker exec -it radicale sh

# Restart container
docker restart radicale
```

### Debugging Steps

1. **Test basic connectivity:**
   ```bash
   curl -I http://localhost:5232/
   ```

2. **Check Radicale logs:**
   ```bash
   # For system service
   sudo journalctl -u radicale -f
   
   # For manual start
   radicale --config /path/to/config --debug
   ```

3. **Validate configuration:**
   ```bash
   radicale --verify-storage
   ```

4. **Test with the integration:**
   ```python
   from radicale_calendar_manager import RadicaleCalendarManager
   
   manager = RadicaleCalendarManager(
       url="http://localhost:5232",
       username="",  # Leave empty for no auth
       password=""
   )
   
   print("Testing connection...")
   if manager.connect():
       print(f"✅ Connected! Found {len(manager.calendars)} calendars")
   else:
       print("❌ Connection failed")
   ```

## Security Considerations

### Development Environment
- Use `auth.type = none` for quick testing
- Bind to `localhost` only
- Use default ports

### Production Environment
- Always use authentication (`htpasswd` or `ldap`)
- Use HTTPS/TLS encryption
- Restrict network access
- Regular backups of calendar data
- Consider using reverse proxy (nginx/apache)

### Example Production Config

```ini
[server]
hosts = 0.0.0.0:5232
max_connections = 20
max_content_length = 100000000
timeout = 30
ssl = True
certificate = /path/to/server.crt
key = /path/to/server.key

[auth]
type = htpasswd
htpasswd_filename = /etc/radicale/users
htpasswd_encryption = bcrypt

[storage]
type = multifilesystem
filesystem_folder = /var/lib/radicale/collections
hook = /path/to/backup/script

[web]
base_prefix = /radicale/

[logging]
level = warning
mask_passwords = True
```

## Next Steps

After setting up Radicale:

1. **Test the LangChain integration:**
   ```bash
   python langchain_example_mcp.py
   ```

2. **Create test events:**
   ```bash
   python -c "
   from radicale_calendar_manager import RadicaleCalendarManager
   manager = RadicaleCalendarManager('http://localhost:5232', '', '')
   manager.connect()
   print('Ready for calendar operations!')
   "
   ```

3. **Explore the example scripts** in the project directory

4. **Read the API documentation** for advanced usage

## Additional Resources

- [Official Radicale Documentation](https://radicale.org/documentation/)
- [CalDAV RFC 4791](https://tools.ietf.org/html/rfc4791)
- [Docker Radicale Image](https://hub.docker.com/r/tomsquest/docker-radicale/)
- [Radicale GitHub Repository](https://github.com/Kozea/Radicale)