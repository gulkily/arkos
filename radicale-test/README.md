# Radicale Calendar Integration - Project Summary

This directory contains a comprehensive calendar integration system that bridges Radicale CalDAV server with various interfaces including LangChain tools and MCP (Model Context Protocol) bridge. The project provides robust calendar operations with proper error handling, testing, and documentation.

## 📁 Project Structure

### Core Components

#### 1. **RadicaleCalendarManager** (`radicale_calendar_manager.py`)
- **Purpose**: High-level interface for Radicale CalDAV operations
- **Features**:
  - Calendar server connection management
  - Event CRUD operations (Create, Read, Update, Delete)
  - Date range filtering and event querying
  - Calendar discovery and selection
  - iCalendar data parsing and formatting
- **Key Methods**: `connect()`, `get_events()`, `add_event()`, `set_event()`, `delete_event()`

#### 2. **MCP Server Implementation** 
- **Primary**: `mcp_radicale_server.py` - **NEW FastMCP-based server** (🆕 **MCP COMPLIANT**)
  - Full MCP protocol compliance using FastMCP framework
  - Multiple transport support (stdio, HTTP)
  - Comprehensive async tool implementation
  - Proper error handling and schema validation
- **Legacy**: `mcp_radicale_bridge.py` - WebSocket-based bridge (deprecated)
- **Configuration**: `mcp_server_config.json` - Server metadata and tool schemas
- **Supported Operations**: List calendars, Get/Create/Update/Delete events
- **Service**: Systemd service configuration available

#### 3. **LangChain MCP Integration** (🆕 **NEW IMPLEMENTATION**)
- **Primary**: `langchain_mcp_integration.py` - MCP-based LangChain integration
- **Example**: `langchain_example_mcp.py` - Updated example using MCP
- **Legacy**: `langchain_tool_adapter.py`, `langchain_example.py` - Direct integration (deprecated)
- **Features**:
  - **MCP Protocol Compliance**: Uses official LangChain MCP adapters
  - **Multiple Integration Methods**: Supports langchain-mcp-adapters and langchain-mcp-tools
  - **Async Operations**: Full async/await support throughout
  - **Automatic Tool Discovery**: Schema validation and tool discovery
  - **Fallback Support**: Manual tool creation if MCP packages unavailable
  - **OpenAI GPT Integration**: Natural language calendar operations

### Synchronization & Integration

#### 4. **Google Calendar Sync** (`google_radicale_sync.py`)
- **Purpose**: Bidirectional synchronization between Google Calendar and Radicale
- **Features**:
  - Google Calendar API integration
  - OAuth2 authentication handling
  - Event mapping and conversion between platforms
- **Status**: Basic implementation complete, advanced features pending

### Testing Framework

#### 5. **Comprehensive Test Suite**
- **Main Tests** (`test_radicale_calendar_manager.py`): Complete test coverage for core functionality
- **Edge Case Tests** (`test_radicale_calendar_manager_edge_cases.py`): Advanced scenarios and edge cases
- **MCP Tests** (`test_mcp_client.py`): WebSocket client testing for MCP bridge
- **Event Creation Tests** (`test_new_event*.py`): Various event creation scenarios

**Test Coverage Includes**:
- Connection and authentication
- Calendar operations and selection
- Event CRUD operations with all field types
- Date filtering and range queries
- Multi-day and all-day events
- Special characters and long text handling
- Duplicate summaries and timezone handling
- Error conditions and edge cases

### Utility Scripts

#### 6. **Standalone Tools**
- **Event Reader** (`test_read_event.py`): Command-line tool to view calendar events
- **Event Creators** (`test_new_event*.py`): Scripts for creating test events with various configurations
- **Configuration Helper** (`radicale_howto.txt`): Setup and configuration instructions

## 🚀 Features

### Calendar Operations
- ✅ List available calendars
- ✅ Retrieve events with date range filtering
- ✅ Create events with full field support (summary, start, end, location, description)
- ✅ Update existing events
- ✅ Delete events
- ✅ Handle timezone-aware events
- ✅ Support for multi-day and all-day events

### Integration Capabilities
- ✅ LangChain tools for AI-powered calendar operations
- ✅ MCP bridge for WebSocket-based communication
- ✅ Google Calendar synchronization (basic)
- ✅ Environment-based configuration
- ✅ Systemd service support

### Error Handling & Validation
- ✅ Connection failure handling
- ✅ Authentication error management
- ✅ Input validation for dates, calendar names, event IDs
- ✅ Graceful handling of missing calendars/events
- ✅ Comprehensive logging throughout

## 📊 Project Status

### ✅ Completed (MVP Ready)
- Core calendar operations
- MCP bridge implementation
- LangChain integration
- Comprehensive testing framework
- Basic Google Calendar sync
- Error handling and validation
- Documentation and setup guides

### 🔄 In Progress
- Advanced Google Calendar features (recurring events, attendees)
- Performance optimizations
- Extended monitoring and logging

### 📋 Future Enhancements
- Recurring events support
- Event categories and tags
- Calendar sharing features
- Batch operations
- Advanced search capabilities
- Performance caching
- CI/CD pipeline setup

## 🛠️ Setup and Usage

### Prerequisites
```bash
# Core dependencies
pip install caldav websockets python-dotenv langchain langchain-openai

# NEW: MCP Integration dependencies
pip install langchain-mcp-adapters mcp
# OR alternative:
pip install langchain-mcp-tools

# Install all dependencies from requirements.txt
pip install -r requirements.txt
```

### Configuration
1. Set up environment variables in `.env`:
   ```
   RADICALE_URL=http://localhost:5232
   RADICALE_USERNAME=your_username
   RADICALE_PASSWORD=your_password
   OPENAI_API_KEY=your_openai_key  # For LangChain integration
   ```

2. Configure Radicale server (see `radicale_howto.txt` for details)

### Quick Start Examples

#### 🆕 NEW: MCP-based LangChain Integration (Recommended)
```python
import asyncio
from langchain_example_mcp import MCPCalendarAgent

async def main():
    agent = MCPCalendarAgent()
    try:
        await agent.initialize()
        
        # Natural language calendar operations
        result = await agent.run_operation("List my calendars")
        print(result)
        
        result = await agent.run_operation("Add a meeting with John tomorrow at 2pm")
        print(result)
        
        # Interactive session
        await agent.run_interactive_session()
        
    finally:
        await agent.cleanup()

asyncio.run(main())
```

#### Direct MCP Integration
```python
import asyncio
from langchain_mcp_integration import get_calendar_tools

async def main():
    tools, integration = await get_calendar_tools()
    try:
        print(f"Loaded {len(tools)} tools: {[t.name for t in tools]}")
        
        # Use tools with any LangChain agent
        from langchain.agents import create_openai_functions_agent
        agent = create_openai_functions_agent(llm, prompt, tools)
        
    finally:
        await integration.cleanup()

asyncio.run(main())
```

#### MCP Server Standalone Usage
```bash
# Start the new MCP server
python mcp_radicale_server.py

# Or with HTTP transport
python mcp_radicale_server.py --transport http --port 8765
```

#### Legacy Examples (Still Supported)
```python
# Direct Calendar Manager Usage
from radicale_calendar_manager import RadicaleCalendarManager

manager = RadicaleCalendarManager(url="http://localhost:5232", 
                                 username="user", password="pass")
manager.connect()
events = manager.get_events("my_calendar")

# Legacy LangChain Integration
from langchain_example import run_calendar_operation
result = run_calendar_operation("Add a meeting with John tomorrow at 2pm")

# Legacy MCP Bridge
python3 mcp_radicale_bridge.py  # WebSocket-based bridge
python3 test_mcp_client.py      # Test client
```

## 🧪 Testing

### 🆕 NEW: MCP Integration Tests
```bash
# Test MCP compliance and integration
pytest test_mcp_compliance.py -v

# Performance comparison (old vs new)
python test_performance_comparison.py

# Test new MCP example
python langchain_example_mcp.py
```

### Legacy Test Suite
```bash
# Run complete legacy test suite
python test_radicale_calendar_manager.py

# Test individual components
python3 test_mcp_client.py                    # Test legacy MCP bridge
python3 test_new_event_3.py --summary "Test" # Test event creation
python3 test_read_event.py --days 7          # View existing events
```

### Migration Testing
```bash
# Test migration from direct to MCP integration
python -c "
import asyncio
from test_performance_comparison import main
asyncio.run(main())
"
```

## 📈 Architecture

The project follows a layered architecture:

1. **CalDAV Layer**: Direct interaction with Radicale server
2. **Manager Layer**: High-level calendar operations (`RadicaleCalendarManager`)
3. **Bridge Layer**: Protocol adapters (MCP, LangChain)
4. **Integration Layer**: External service connectors (Google Calendar)
5. **Application Layer**: End-user interfaces and tools

## 🔒 Security Features

- Secure credential handling via environment variables
- Request validation and sanitization
- Session management for connections
- Error message sanitization to prevent information leakage

## 📝 Documentation

### 🆕 NEW Documentation
- **Migration Guide**: `MIGRATION_GUIDE.md` - Step-by-step migration from direct to MCP integration
- **LangChain MCP Plan**: `langchain-mcp-integration-plan.md` - Implementation plan and architecture
- **Architecture Diagram**: `architecture-diagram.md` - Visual system architecture
- **Architecture Analysis**: `architecture-analysis.md` - Issues and recommendations

### Existing Documentation
- **Setup Guide**: `radicale_howto.txt`
- **Integration Plan**: `langchain_integration_plan.md`
- **MVP Checklist**: `langchain_mvp_checklist.md`
- **Code Documentation**: Comprehensive docstrings throughout all modules

### New Configuration Files
- **Requirements**: `requirements.txt` - Updated with MCP dependencies
- **MCP Config**: `mcp_server_config.json` - MCP server metadata and schemas

## 🎯 Use Cases

This integration supports various use cases:
- AI-powered calendar assistants using LangChain
- Automated calendar synchronization between systems
- Calendar-aware applications requiring CalDAV access
- Testing and development of calendar-based features
- Enterprise calendar integration solutions

The project provides a solid foundation for building calendar-aware applications with robust error handling, comprehensive testing, and multiple integration options.