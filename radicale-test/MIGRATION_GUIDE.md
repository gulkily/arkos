# Migration Guide: Direct LangChain to MCP Integration

## Overview

This guide walks you through migrating from the direct LangChain tool adapter (`langchain_tool_adapter.py`) to the new MCP-based integration (`langchain_mcp_integration.py`).

## 🎯 Benefits of Migration

### Technical Benefits
- **Standardization**: Uses industry-standard MCP protocol
- **Better Tool Discovery**: Automatic schema discovery and validation
- **Multi-Server Support**: Easy integration with multiple MCP servers
- **Official Support**: Leverages official LangChain MCP adapters
- **Future-Proofing**: Aligned with Anthropic/LangChain standards

### Architectural Benefits
- **Loose Coupling**: Clean separation between LangChain and calendar logic
- **Scalability**: MCP servers can be distributed and load-balanced
- **Interoperability**: MCP tools work across different AI frameworks
- **Ecosystem Access**: Access to 2000+ existing MCP servers

## 📋 Prerequisites

### Dependencies
Install the required MCP packages:

```bash
# Primary option (official LangChain package)
pip install langchain-mcp-adapters

# Alternative option
pip install langchain-mcp-tools

# Core MCP package (if needed)
pip install mcp
```

### Environment Setup
Ensure your `.env` file contains the required variables:

```env
# Radicale server configuration
RADICALE_URL=http://localhost:5232
RADICALE_USERNAME=your_username
RADICALE_PASSWORD=your_password

# LangChain configuration
OPENAI_API_KEY=your_openai_api_key
```

## 🔄 Migration Steps

### Step 1: Replace Tool Adapter Import

**Before (Direct Integration):**
```python
from langchain_tool_adapter import CalendarToolAdapter

# Initialize adapter
adapter = CalendarToolAdapter(
    url="http://localhost:5232",
    username="user",
    password="pass"
)

# Get tools
tools = adapter.get_all_tools()
```

**After (MCP Integration):**
```python
from langchain_mcp_integration import get_calendar_tools

# Get tools and integration instance
tools, integration = await get_calendar_tools()

# Clean up when done
await integration.cleanup()
```

### Step 2: Update Agent Creation

**Before:**
```python
from langchain.agents import create_openai_functions_agent
from langchain_tool_adapter import CalendarToolAdapter

# Synchronous tool creation
adapter = CalendarToolAdapter(url="...", username="...", password="...")
tools = adapter.get_all_tools()

# Create agent
agent = create_openai_functions_agent(llm, prompt, tools)
```

**After:**
```python
from langchain.agents import create_openai_functions_agent
from langchain_mcp_integration import CalendarMCPIntegration

# Async tool creation
integration = CalendarMCPIntegration()
tools = await integration.initialize()

# Create agent
agent = create_openai_functions_agent(llm, prompt, tools)

# Remember to cleanup
await integration.cleanup()
```

### Step 3: Update Example Usage

**Before (langchain_example.py):**
```python
def run_calendar_operation(operation: str) -> str:
    try:
        chat_history = []
        result = agent_executor.invoke({
            "input": operation,
            "chat_history": chat_history
        })
        return result["output"]
    except Exception as e:
        return f"Error: {str(e)}"
```

**After (langchain_example_mcp.py):**
```python
async def run_calendar_operation(operation: str) -> str:
    try:
        chat_history = []
        result = await agent_executor.ainvoke({
            "input": operation,
            "chat_history": chat_history
        })
        return result["output"]
    except Exception as e:
        return f"Error: {str(e)}"
```

### Step 4: Use New Agent Class

**New Approach:**
```python
from langchain_example_mcp import MCPCalendarAgent

async def main():
    agent = MCPCalendarAgent()
    
    try:
        # Initialize agent
        await agent.initialize()
        
        # Run operations
        result = await agent.run_operation("List my calendars")
        print(result)
        
        # Interactive session
        await agent.run_interactive_session()
        
    finally:
        await agent.cleanup()

# Run with asyncio
asyncio.run(main())
```

## 🔧 Configuration Options

### Default Configuration
The MCP integration uses sensible defaults:

```python
{
    "radicale-calendar": {
        "command": "python",
        "args": ["mcp_radicale_server.py"],
        "transport": "stdio",
        "env": {
            "RADICALE_URL": os.getenv("RADICALE_URL"),
            "RADICALE_USERNAME": os.getenv("RADICALE_USERNAME"),
            "RADICALE_PASSWORD": os.getenv("RADICALE_PASSWORD")
        }
    }
}
```

### Custom Configuration
You can provide custom MCP server configuration:

```python
custom_config = {
    "radicale-calendar": {
        "command": "python",
        "args": ["path/to/mcp_radicale_server.py", "--transport", "http"],
        "transport": "http",
        "env": {
            "RADICALE_URL": "https://my-server.com:5232",
            "RADICALE_USERNAME": "custom_user",
            "RADICALE_PASSWORD": "custom_pass"
        }
    }
}

integration = CalendarMCPIntegration(custom_config)
```

## 🧪 Testing Your Migration

### Step 1: Run Compliance Tests
```bash
# Test MCP integration
pytest test_mcp_compliance.py -v

# Test specific functionality
pytest test_mcp_compliance.py::TestMCPCompliance::test_mcp_server_startup -v
```

### Step 2: Performance Comparison
```bash
# Compare old vs new performance
python test_performance_comparison.py
```

### Step 3: Manual Testing
```bash
# Test new MCP server
python mcp_radicale_server.py

# Test new example
python langchain_example_mcp.py
```

## 🔀 Backward Compatibility

### Feature Flag Approach
You can maintain both integrations during transition:

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Feature flag for MCP integration
USE_MCP = os.getenv("USE_MCP_INTEGRATION", "true").lower() == "true"

if USE_MCP:
    from langchain_mcp_integration import get_calendar_tools
    tools, integration = await get_calendar_tools()
else:
    from langchain_tool_adapter import CalendarToolAdapter
    adapter = CalendarToolAdapter(url="...", username="...", password="...")
    tools = adapter.get_all_tools()
    integration = None
```

### Gradual Migration
1. **Week 1**: Install MCP dependencies, run tests
2. **Week 2**: Update development environment to use MCP
3. **Week 3**: Update staging environment, run performance tests
4. **Week 4**: Update production environment, monitor metrics

## ⚠️ Common Issues and Solutions

### Issue 1: Import Errors
```
ImportError: No module named 'langchain_mcp_adapters'
```

**Solution:**
```bash
pip install langchain-mcp-adapters
# OR
pip install langchain-mcp-tools
```

### Issue 2: MCP Server Not Starting
```
Error: Failed to connect to MCP server
```

**Solutions:**
1. Check Radicale server is running
2. Verify environment variables are set
3. Check file paths in configuration
4. Review server logs for errors

### Issue 3: Tool Conversion Fails
```
Error: No tools returned from MCP server
```

**Solutions:**
1. Verify MCP server is MCP-compliant
2. Check server configuration JSON
3. Test server independently with `test_mcp_client.py`
4. Fall back to manual tool creation

### Issue 4: Async/Await Issues
```
RuntimeError: cannot be called from a running event loop
```

**Solution:**
```python
# Wrong
result = asyncio.run(agent.run_operation("test"))

# Correct
result = await agent.run_operation("test")
```

## 📊 Validation Checklist

- [ ] All MCP dependencies installed
- [ ] Environment variables configured
- [ ] MCP server starts successfully
- [ ] Tools are discovered and converted
- [ ] Agent operations work correctly
- [ ] Performance is acceptable
- [ ] Error handling works as expected
- [ ] Cleanup functions are called
- [ ] Tests pass
- [ ] Documentation updated

## 🚀 Next Steps After Migration

### 1. Optimize Performance
- Implement connection pooling
- Add caching for frequently accessed data
- Optimize MCP server startup time

### 2. Enhance Functionality
- Add more calendar operations
- Implement recurring events support
- Add calendar sharing features

### 3. Extend Integration
- Connect to additional MCP servers
- Add other calendar providers
- Implement calendar synchronization

### 4. Monitor and Maintain
- Set up monitoring for MCP operations
- Implement logging and metrics
- Regular performance testing

## 📚 Additional Resources

- [LangChain MCP Adapters Documentation](https://github.com/langchain-ai/langchain-mcp-adapters)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Anthropic MCP Documentation](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
- [Project README](./README.md)
- [Architecture Analysis](./architecture-analysis.md)

## 🆘 Getting Help

If you encounter issues during migration:

1. **Check the logs**: Review MCP server and integration logs
2. **Run diagnostics**: Use the test scripts to identify issues
3. **Consult documentation**: Review the MCP and LangChain documentation
4. **File an issue**: Create an issue in the project repository

Remember: The new MCP integration provides a more robust, standardized approach to calendar operations while maintaining the same functionality you're used to.