# Troubleshooting Guide

Common issues and solutions for the LangChain MCP Calendar Integration.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Connection Problems](#connection-problems)
- [Authentication Errors](#authentication-errors)
- [MCP Integration Issues](#mcp-integration-issues)
- [LangChain Agent Problems](#langchain-agent-problems)
- [Calendar Operation Errors](#calendar-operation-errors)
- [Performance Issues](#performance-issues)
- [Debugging Tips](#debugging-tips)

## Installation Issues

### Python Package Problems

#### Issue: `ImportError: No module named 'langchain'`
**Symptoms:**
```
ImportError: No module named 'langchain'
ModuleNotFoundError: No module named 'langchain_openai'
```

**Solutions:**
```bash
# Verify pip is using correct Python
python -m pip --version
which python

# Install in correct environment
python -m pip install langchain langchain-openai

# If using virtual environment
source venv/bin/activate  # Linux/macOS
pip install langchain langchain-openai

# Force reinstall if corrupted
pip install --force-reinstall langchain langchain-openai
```

#### Issue: Package version conflicts
**Symptoms:**
```
ERROR: pip's dependency resolver does not currently consider all packages
ImportError: cannot import name 'X' from 'langchain'
```

**Solutions:**
```bash
# Create fresh virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate

# Install core packages first
pip install --upgrade pip
pip install langchain langchain-openai python-dotenv caldav

# Then install optional packages
pip install langchain-mcp-adapters mcp
```

#### Issue: Permission denied during installation
**Symptoms:**
```
ERROR: Could not install packages due to an EnvironmentError: [Errno 13] Permission denied
```

**Solutions:**
```bash
# Use user installation
pip install --user langchain langchain-openai

# Or use virtual environment (recommended)
python -m venv venv
source venv/bin/activate
pip install langchain langchain-openai

# On macOS/Linux, fix permissions
sudo chown -R $USER ~/.local/lib/python*
```

### Environment Configuration Issues

#### Issue: `.env` file not loaded
**Symptoms:**
```
ValueError: OPENAI_API_KEY not found in environment variables
```

**Solutions:**
```bash
# Verify .env file exists in correct location
ls -la .env
pwd

# Check .env file contents
cat .env

# Ensure no extra spaces or quotes
# Correct format:
OPENAI_API_KEY=sk-your-key-here
RADICALE_URL=http://localhost:5232

# Test loading manually
python -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('API Key loaded:', bool(os.getenv('OPENAI_API_KEY')))
"
```

#### Issue: Wrong working directory
**Symptoms:**
- `.env` file not found
- Import errors for local modules

**Solutions:**
```bash
# Check current directory
pwd
ls -la

# Ensure you're in the project directory
cd path/to/radicale-test

# Or use absolute paths in .env loading
python -c "
from dotenv import load_dotenv
load_dotenv('/absolute/path/to/.env')
"
```

## Connection Problems

### Radicale Server Issues

#### Issue: Connection refused to localhost:5232
**Symptoms:**
```
requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=5232): Max retries exceeded
```

**Diagnosis:**
```bash
# Check if Radicale is running
ps aux | grep radicale
netstat -tlnp | grep 5232
curl http://localhost:5232/
```

**Solutions:**
```bash
# Start Radicale server
radicale --hosts localhost:5232

# Or with Docker
docker run -d -p 5232:5232 tomsquest/docker-radicale

# Check if another service is using port 5232
sudo lsof -i :5232

# Use different port if needed
radicale --hosts localhost:5233
# Update RADICALE_URL in .env accordingly
```

#### Issue: Radicale server crashes or stops
**Symptoms:**
- Connection works initially then fails
- Intermittent connection errors

**Diagnosis:**
```bash
# Check Radicale logs
journalctl -u radicale -f  # If using systemd
docker logs radicale       # If using Docker

# Check system resources
df -h    # Disk space
free -h  # Memory usage
```

**Solutions:**
```bash
# Restart Radicale
sudo systemctl restart radicale

# Or for Docker
docker restart radicale

# Check configuration
radicale --verify-storage

# Increase logging level in config
[logging]
level = debug
```

### Network Configuration Issues

#### Issue: CalDAV discovery fails
**Symptoms:**
```
Warning: No calendars found in Radicale
caldav.lib.error.NotFoundError: No collections found
```

**Solutions:**
```bash
# Test basic connectivity
curl -I http://localhost:5232/

# Test PROPFIND request
curl -X PROPFIND http://localhost:5232/ \
  -H "Content-Type: text/xml" \
  -d '<?xml version="1.0"?><propfind xmlns="DAV:"><prop><displayname/></prop></propfind>'

# Create initial calendar via web interface
open http://localhost:5232/

# Or programmatically
python -c "
import caldav
client = caldav.DAVClient('http://localhost:5232')
principal = client.principal()
calendar = principal.make_calendar(name='Default Calendar')
print('Created calendar:', calendar.name)
"
```

## Authentication Errors

### Basic Authentication Issues

#### Issue: 401 Unauthorized
**Symptoms:**
```
requests.exceptions.HTTPError: 401 Client Error: Unauthorized
caldav.lib.error.AuthorizationError: Unauthorized. Status code: 401
```

**Solutions:**
```bash
# Check credentials in .env
cat .env | grep -E "(USERNAME|PASSWORD)"

# Test credentials manually
curl -u username:password http://localhost:5232/

# For no authentication (development), ensure Radicale config has:
[auth]
type = none

# Check htpasswd file if using file authentication
cat /path/to/users
htpasswd -v /path/to/users username
```

#### Issue: Password encoding problems
**Symptoms:**
- Works with some clients but not others
- Special characters in password

**Solutions:**
```bash
# URL encode special characters in password
python -c "
import urllib.parse
password = 'your-password-with-special-chars'
encoded = urllib.parse.quote(password)
print('Encoded password:', encoded)
"

# Use environment variables instead of .env for special chars
export RADICALE_PASSWORD='your-password'

# Or use base64 encoding
echo -n "username:password" | base64
```

## MCP Integration Issues

### MCP Package Problems

#### Issue: MCP packages not found
**Symptoms:**
```
ImportError: No module named 'langchain_mcp_adapters'
ImportError: No module named 'mcp'
```

**Solutions:**
```bash
# Install MCP packages
pip install langchain-mcp-adapters mcp

# Or alternative
pip install langchain-mcp-tools

# Check if packages are installed
pip list | grep mcp

# The system will fallback to manual tools if MCP packages aren't available
# This is expected behavior and not an error
```

#### Issue: MCP integration fails
**Symptoms:**
```
MCPIntegrationError: All MCP integration methods failed
```

**Diagnosis:**
```python
# Test each integration method individually
import asyncio
from langchain_mcp_integration import CalendarMCPIntegration

async def test_integration():
    integration = CalendarMCPIntegration()
    try:
        tools = await integration.initialize()
        print(f"Success: {len(tools)} tools loaded")
        print(f"Method: {integration._integration_method}")
    except Exception as e:
        print(f"Integration failed: {e}")
    finally:
        await integration.cleanup()

asyncio.run(test_integration())
```

**Solutions:**
```bash
# Ensure MCP server script is accessible
ls -la mcp_radicale_server.py
python mcp_radicale_server.py --help

# Check dependencies
pip install fastmcp anyio

# Test manual tool creation (always works)
python -c "
import asyncio
from langchain_mcp_integration import CalendarMCPIntegration
async def test():
    integration = CalendarMCPIntegration()
    tools = await integration._initialize_manual_tools()
    print(f'Manual tools: {len(tools)}')
asyncio.run(test())
"
```

### MCP Server Issues

#### Issue: MCP server won't start
**Symptoms:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'mcp_radicale_server.py'
```

**Solutions:**
```bash
# Ensure file exists and is executable
ls -la mcp_radicale_server.py
chmod +x mcp_radicale_server.py

# Test server directly
python mcp_radicale_server.py

# Check dependencies
pip install fastmcp

# Use absolute path in configuration
pwd  # Get current directory
# Update configuration with full path
```

## LangChain Agent Problems

### OpenAI API Issues

#### Issue: Invalid API key
**Symptoms:**
```
openai.error.AuthenticationError: Incorrect API key provided
```

**Solutions:**
```bash
# Verify API key format (starts with sk-)
echo $OPENAI_API_KEY

# Test API key directly
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Check OpenAI account status
# Visit: https://platform.openai.com/account/billing

# Regenerate API key if needed
# Visit: https://platform.openai.com/api-keys
```

#### Issue: Rate limiting
**Symptoms:**
```
openai.error.RateLimitError: Rate limit reached
```

**Solutions:**
```python
# Add delays between requests
import asyncio
await asyncio.sleep(1)

# Use lower tier model
agent = MCPCalendarAgent(model="gpt-3.5-turbo")

# Implement retry logic
import backoff

@backoff.on_exception(backoff.expo, openai.error.RateLimitError)
async def with_retry():
    return await agent.run_operation(query)
```

### Agent Initialization Problems

#### Issue: Agent fails to initialize
**Symptoms:**
```
Failed to initialize MCP calendar agent: ...
```

**Diagnosis:**
```python
# Test components individually
import asyncio
from langchain_example_mcp import MCPCalendarAgent

async def debug_initialization():
    agent = MCPCalendarAgent()
    
    # Test MCP integration
    try:
        from langchain_mcp_integration import get_calendar_tools
        tools, integration = await get_calendar_tools()
        print(f"✅ MCP integration: {len(tools)} tools")
        await integration.cleanup()
    except Exception as e:
        print(f"❌ MCP integration failed: {e}")
    
    # Test OpenAI connection
    try:
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(model="gpt-3.5-turbo")
        print("✅ OpenAI connection")
    except Exception as e:
        print(f"❌ OpenAI connection failed: {e}")

asyncio.run(debug_initialization())
```

## Calendar Operation Errors

### Event Creation Issues

#### Issue: Invalid date format
**Symptoms:**
```
ValueError: Invalid datetime format: ...
```

**Solutions:**
```python
# Use ISO format for dates
"2023-06-01T14:00:00"

# Or natural language (with manual tools)
"tomorrow at 2pm"
"next Friday at 10am"
"June 1st at 2:30pm"

# Test date parsing
from datetime import datetime
datetime.fromisoformat("2023-06-01T14:00:00")
```

#### Issue: Event not created
**Symptoms:**
- No error but event doesn't appear
- Success response but calendar empty

**Diagnosis:**
```python
# Check calendar immediately after creation
manager = RadicaleCalendarManager(url, username, password)
manager.connect()

event_id = manager.add_event("calendar", event_data)
print(f"Created event: {event_id}")

# Verify event exists
events = manager.get_events("calendar")
print(f"Total events: {len(events)}")
for event in events:
    if event['id'] == event_id:
        print("✅ Event found")
        break
else:
    print("❌ Event not found")
```

### Calendar Access Issues

#### Issue: Calendar not found
**Symptoms:**
```
ValueError: Calendar not found
```

**Solutions:**
```python
# List available calendars
manager = RadicaleCalendarManager(url, username, password)
if manager.connect():
    print("Available calendars:")
    for i, cal in enumerate(manager.calendars):
        print(f"  {i}: {cal.name}")
    
    # Use exact calendar name
    calendar = manager.get_calendar("exact-name-here")
    
    # Or use first available
    calendar = manager.get_calendar()
```

## Performance Issues

### Slow Operations

#### Issue: Operations take too long
**Symptoms:**
- Timeouts
- Very slow responses

**Solutions:**
```python
# Limit date ranges
from datetime import datetime, timedelta
start = datetime.now()
end = start + timedelta(days=7)  # Instead of large ranges
events = manager.get_events(calendar_name, start, end)

# Use connection pooling for multiple operations
with manager:  # If implementing context manager
    event1 = manager.add_event(...)
    event2 = manager.add_event(...)

# Optimize queries
# Instead of getting all events then filtering:
events = manager.get_events(calendar_name, specific_start, specific_end)
```

### Memory Issues

#### Issue: High memory usage
**Solutions:**
```python
# Clean up resources
await agent.cleanup()
await integration.cleanup()

# Process events in batches
def process_events_batch(events, batch_size=50):
    for i in range(0, len(events), batch_size):
        batch = events[i:i + batch_size]
        # Process batch
        yield batch
```

## Debugging Tips

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# For specific modules
logger = logging.getLogger("langchain-mcp-integration")
logger.setLevel(logging.DEBUG)
```

### Inspect Tool Responses

```python
import json

# Check tool output format
result = tool.run(input_data)
print("Raw result:", result)

try:
    parsed = json.loads(result)
    print("Parsed result:", parsed)
    if parsed.get("status") == "error":
        print("Error details:", parsed.get("message"))
except json.JSONDecodeError:
    print("Result is not JSON:", result)
```

### Test Components Individually

```python
# Test calendar manager
from radicale_calendar_manager import RadicaleCalendarManager
manager = RadicaleCalendarManager("http://localhost:5232", "", "")
print("Connection:", manager.connect())

# Test MCP integration
from langchain_mcp_integration import get_calendar_tools
tools, integration = await get_calendar_tools()
print("Tools loaded:", [t.name for t in tools])

# Test agent
from langchain_example_mcp import MCPCalendarAgent
agent = MCPCalendarAgent()
await agent.initialize()
print("Agent ready")
```

### Network Debugging

```bash
# Monitor network traffic
sudo tcpdump -i lo port 5232

# Test with curl
curl -v http://localhost:5232/

# Check DNS resolution
nslookup localhost
```

### File System Debugging

```bash
# Check file permissions
ls -la mcp_radicale_server.py
ls -la .env

# Check directory structure
find . -name "*.py" | head -10

# Check disk space
df -h

# Check Radicale storage
ls -la ~/.local/share/radicale/collections/
```

## Getting Additional Help

### Log Collection

When reporting issues, include:

```bash
# System information
python --version
pip list | grep -E "(langchain|caldav|mcp)"

# Environment check
env | grep -E "(RADICALE|OPENAI)"

# Test results
python -c "
import asyncio
from langchain_mcp_integration import get_calendar_tools

async def test():
    try:
        tools, integration = await get_calendar_tools()
        print(f'SUCCESS: {len(tools)} tools loaded')
        print(f'Method: {integration._integration_method}')
    except Exception as e:
        print(f'ERROR: {e}')
        import traceback
        traceback.print_exc()

asyncio.run(test())
"
```

### Common Log Patterns

**Success patterns:**
```
INFO:langchain-mcp-integration:Successfully initialized with manual tools: 3 tools loaded
✅ Connected to calendar server!
📅 Found 2 calendars
```

**Error patterns:**
```
ERROR:radicale-calendar-manager:Failed to connect to Radicale: Connection refused
MCPIntegrationError: All MCP integration methods failed
ValueError: OPENAI_API_KEY not found in environment variables
```

### Minimal Reproduction

When reporting bugs, create a minimal reproduction:

```python
import asyncio
import os
from dotenv import load_dotenv

async def minimal_repro():
    load_dotenv()
    
    # Test basic imports
    try:
        from radicale_calendar_manager import RadicaleCalendarManager
        print("✅ Calendar manager import")
    except Exception as e:
        print(f"❌ Calendar manager import: {e}")
        return
    
    # Test connection
    manager = RadicaleCalendarManager(
        url=os.getenv("RADICALE_URL", "http://localhost:5232"),
        username=os.getenv("RADICALE_USERNAME", ""),
        password=os.getenv("RADICALE_PASSWORD", "")
    )
    
    if manager.connect():
        print(f"✅ Connected: {len(manager.calendars)} calendars")
    else:
        print("❌ Connection failed")

if __name__ == "__main__":
    asyncio.run(minimal_repro())
```

This should help identify and resolve most common issues with the LangChain MCP Calendar Integration.