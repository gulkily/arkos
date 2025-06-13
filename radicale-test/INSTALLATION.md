# Installation Guide

Complete installation guide for the LangChain MCP Calendar Integration.

## System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Linux, macOS, or Windows
- **Memory**: 512MB RAM minimum (2GB recommended)
- **Storage**: 100MB for dependencies, additional space for calendar data

## Pre-Installation Checklist

- [ ] Python 3.8+ installed and accessible via `python` or `python3`
- [ ] `pip` package manager available
- [ ] Internet connection for downloading packages
- [ ] OpenAI API key (for LangChain functionality)
- [ ] Access to a CalDAV server (or ability to run Radicale locally)

## Installation Steps

### Step 1: Clone or Download Files

If you have git access:
```bash
git clone <repository-url>
cd <repository-directory>/radicale-test
```

Or download these essential files:
- `langchain_example_mcp.py`
- `langchain_mcp_integration.py`
- `mcp_radicale_server.py`
- `radicale_calendar_manager.py`

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv langchain-mcp-env

# Activate virtual environment
# On Linux/macOS:
source langchain-mcp-env/bin/activate

# On Windows:
langchain-mcp-env\Scripts\activate
```

### Step 3: Install Core Dependencies

```bash
# Core required packages
pip install langchain langchain-openai python-dotenv caldav

# Verify installation
python -c "import langchain, caldav; print('Core dependencies installed successfully')"
```

### Step 4: Install MCP Dependencies (Optional but Recommended)

The integration supports multiple MCP packages with automatic fallback:

**Option A: LangChain MCP Adapters (Recommended)**
```bash
pip install langchain-mcp-adapters mcp
```

**Option B: LangChain MCP Tools (Alternative)**
```bash
pip install langchain-mcp-tools
```

**Note:** If neither MCP package is installed, the system will automatically fall back to manual tool creation.

### Step 5: Install Additional Dependencies

For full functionality:

```bash
# For development and testing
pip install pytest pytest-asyncio

# For enhanced date parsing (optional)
pip install python-dateutil

# For logging enhancements (optional)
pip install colorlog
```

### Step 6: Verify Installation

Create a test script to verify all components:

```python
# test_installation.py
import sys

def test_imports():
    try:
        import langchain
        print("✅ LangChain installed")
        
        import langchain_openai
        print("✅ LangChain OpenAI installed")
        
        import caldav
        print("✅ CalDAV library installed")
        
        import dotenv
        print("✅ Python-dotenv installed")
        
        # Test optional MCP packages
        try:
            import mcp
            print("✅ MCP package installed")
        except ImportError:
            print("⚠️  MCP package not installed (will use fallback)")
            
        try:
            import langchain_mcp_adapters
            print("✅ LangChain MCP Adapters installed")
        except ImportError:
            try:
                import langchain_mcp_tools
                print("✅ LangChain MCP Tools installed")
            except ImportError:
                print("⚠️  No MCP adapters installed (will use manual tools)")
        
        print("\n🎉 All core dependencies are installed!")
        return True
        
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

if __name__ == "__main__":
    if test_imports():
        print("\nYou can proceed with the setup!")
    else:
        print("\nPlease install missing dependencies and try again.")
        sys.exit(1)
```

Run the test:
```bash
python test_installation.py
```

## Environment Configuration

### Step 1: Create Environment File

Create a `.env` file in the project directory:

```bash
# Create .env file
touch .env
```

### Step 2: Configure Environment Variables

Add the following to your `.env` file:

```env
# OpenAI Configuration (Required for LangChain)
OPENAI_API_KEY=your_openai_api_key_here

# Radicale Server Configuration
RADICALE_URL=http://localhost:5232
RADICALE_USERNAME=your_username
RADICALE_PASSWORD=your_password

# Optional: Logging Configuration
LOG_LEVEL=INFO

# Optional: MCP Configuration
MCP_TRANSPORT=stdio
MCP_PORT=8765
```

### Step 3: Obtain OpenAI API Key

1. Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key and add it to your `.env` file

**Important:** Never commit your `.env` file to version control.

## Radicale Server Setup

You need a running CalDAV server. See [RADICALE_SETUP.md](RADICALE_SETUP.md) for detailed instructions.

### Quick Radicale Setup (Docker)

```bash
# Run Radicale server with Docker
docker run -d \
  --name radicale \
  -p 5232:5232 \
  tomsquest/docker-radicale

# Verify server is running
curl http://localhost:5232/
```

### Quick Radicale Setup (Python)

```bash
# Install Radicale
pip install radicale

# Start server (no authentication for testing)
radicale --config /dev/stdin << EOF
[server]
hosts = localhost:5232

[auth]
type = none

[storage]
type = multifilesystem
filesystem_folder = ~/.local/share/radicale/collections
EOF
```

## Verification and Testing

### Step 1: Test Calendar Connection

```python
# test_connection.py
from radicale_calendar_manager import RadicaleCalendarManager
import os
from dotenv import load_dotenv

load_dotenv()

def test_calendar_connection():
    manager = RadicaleCalendarManager(
        url=os.getenv("RADICALE_URL", "http://localhost:5232"),
        username=os.getenv("RADICALE_USERNAME", ""),
        password=os.getenv("RADICALE_PASSWORD", "")
    )
    
    if manager.connect():
        print(f"✅ Connected to calendar server!")
        print(f"📅 Found {len(manager.calendars)} calendars")
        for cal in manager.calendars:
            print(f"   - {cal.name}")
        return True
    else:
        print("❌ Failed to connect to calendar server")
        return False

if __name__ == "__main__":
    test_calendar_connection()
```

Run the test:
```bash
python test_connection.py
```

### Step 2: Test MCP Integration

```python
# test_mcp.py
import asyncio
from langchain_mcp_integration import get_calendar_tools

async def test_mcp_integration():
    try:
        tools, integration = await get_calendar_tools()
        print(f"✅ MCP integration working!")
        print(f"🔧 Loaded {len(tools)} tools:")
        for tool in tools:
            print(f"   - {tool.name}: {tool.description}")
        
        await integration.cleanup()
        return True
        
    except Exception as e:
        print(f"❌ MCP integration failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_mcp_integration())
```

Run the test:
```bash
python test_mcp.py
```

### Step 3: Test LangChain Integration

```python
# test_langchain.py
import asyncio
import os
from langchain_example_mcp import MCPCalendarAgent

async def test_langchain_integration():
    try:
        agent = MCPCalendarAgent()
        await agent.initialize()
        
        result = await agent.run_operation("List my available calendars")
        print("✅ LangChain integration working!")
        print(f"📋 Result: {result}")
        
        await agent.cleanup()
        return True
        
    except Exception as e:
        print(f"❌ LangChain integration failed: {e}")
        return False

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Set OPENAI_API_KEY in .env file to test LangChain integration")
    else:
        asyncio.run(test_langchain_integration())
```

Run the test:
```bash
python test_langchain.py
```

## Troubleshooting Installation Issues

### Common Python Issues

**Issue: `python` command not found**
```bash
# Try python3 instead
python3 -m pip install langchain

# Or create an alias
alias python=python3
```

**Issue: Permission denied installing packages**
```bash
# Use user installation
pip install --user langchain langchain-openai

# Or use virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/macOS
pip install langchain langchain-openai
```

**Issue: Old pip version**
```bash
# Update pip
python -m pip install --upgrade pip
```

### Common Package Issues

**Issue: `ImportError: No module named 'langchain'`**
```bash
# Verify pip installed to correct Python
python -m pip list | grep langchain

# If not found, reinstall
pip install --force-reinstall langchain
```

**Issue: Conflicting package versions**
```bash
# Create fresh virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### CalDAV Connection Issues

**Issue: Connection refused to Radicale**
```bash
# Check if Radicale is running
ps aux | grep radicale
netstat -tlnp | grep 5232

# Start Radicale if not running
radicale --hosts localhost:5232
```

**Issue: Authentication errors**
- Check username/password in `.env` file
- For testing, use no authentication in Radicale config
- Verify `.env` file is in the correct directory

### OpenAI API Issues

**Issue: Invalid API key**
- Verify API key is correct and active
- Check for extra spaces or newlines
- Ensure billing is set up in OpenAI account

**Issue: Rate limiting**
- Start with fewer requests
- Add delays between operations
- Consider upgrading OpenAI plan

## Alternative Installation Methods

### Using requirements.txt

Create a `requirements.txt` file:

```txt
# Core dependencies
langchain>=0.1.0
langchain-openai>=0.1.0
python-dotenv>=1.0.0
caldav>=1.3.0

# MCP integration (optional)
langchain-mcp-adapters>=0.1.0
mcp>=1.0.0

# Development dependencies
pytest>=7.0.0
pytest-asyncio>=0.21.0
```

Install all at once:
```bash
pip install -r requirements.txt
```

### Using conda

```bash
# Create conda environment
conda create -n langchain-mcp python=3.10

# Activate environment
conda activate langchain-mcp

# Install packages
conda install -c conda-forge python-dotenv
pip install langchain langchain-openai caldav langchain-mcp-adapters mcp
```

### Using Poetry

```bash
# Initialize project
poetry init

# Add dependencies
poetry add langchain langchain-openai python-dotenv caldav
poetry add --group dev pytest pytest-asyncio

# Install
poetry install

# Activate shell
poetry shell
```

## Post-Installation Steps

1. **Run the example:**
   ```bash
   python langchain_example_mcp.py
   ```

2. **Read additional documentation:**
   - [RADICALE_SETUP.md](RADICALE_SETUP.md) - Detailed Radicale setup
   - [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - API reference
   - [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues

3. **Explore natural language examples:**
   - "What meetings do I have today?"
   - "Schedule a meeting with John tomorrow at 2pm"
   - "Show me all events next week"

4. **Customize for your needs:**
   - Modify the system prompt in `langchain_example_mcp.py`
   - Add custom tools in `langchain_mcp_integration.py`
   - Extend calendar operations in `radicale_calendar_manager.py`

## Getting Help

If you encounter issues during installation:

1. Check the [TROUBLESHOOTING.md](TROUBLESHOOTING.md) guide
2. Verify all prerequisites are met
3. Test each component individually
4. Check the logs for detailed error messages
5. Ensure environment variables are set correctly

## Success Criteria

After completing installation, you should be able to:

- ✅ Import all required Python packages
- ✅ Connect to your CalDAV server
- ✅ Load MCP tools successfully
- ✅ Run the LangChain example
- ✅ Perform calendar operations via natural language

Once these criteria are met, you're ready to use the LangChain MCP Calendar Integration!