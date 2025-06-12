# Radicale Calendar Integration - Testing Guide

This guide provides step-by-step instructions for testing the Radicale calendar integration system.

## 🚀 Quick Test Commands

### 1. **Basic Calendar Operations** (Core functionality)
```bash
python test_radicale_calendar_manager.py
```
This tests all CRUD operations, event creation, updates, deletions.

### 2. **MCP WebSocket Integration** (Enhanced client)
```bash
# Terminal 1: Start the WebSocket bridge
python mcp_radicale_bridge.py

# Terminal 2: Run the enhanced test client
python test_mcp_client.py
```
This runs 5 comprehensive tests with colored output showing create/update/delete operations.

### 3. **LangChain AI Agent** (Natural language interface)
```bash
python langchain_example_mcp.py
```
This starts an interactive AI assistant that can manage your calendar using natural language.

### 4. **MCP Compliance Tests** (Protocol validation)
```bash
pytest test_mcp_compliance.py -v
```
Runs 15 tests validating MCP protocol compliance.

### 5. **LangChain Integration Tests** (Tool conversion)
```bash
pytest test_langchain_integration.py -v
```
Runs 19 tests validating LangChain tool integration.

## 🔧 Prerequisites

### Required: Radicale Server Running
Make sure Radicale is running:
```bash
# Check if Radicale is running
curl http://localhost:5232

# If not running, start it (check radicale_howto.txt for setup)
```

### Required: Environment Variables
Ensure your `.env` file contains:
```bash
RADICALE_URL=http://localhost:5232
RADICALE_USERNAME=your_username
RADICALE_PASSWORD=your_password
OPENAI_API_KEY=your_openai_key  # For AI agent tests
```

### Required: Dependencies
```bash
pip install -r requirements.txt
```

## 🎯 Recommended Test Sequence

### Step 1: Basic Functionality Test
```bash
python test_radicale_calendar_manager.py
```
**Expected Output:** `Ran 9 tests in X.XXXs OK`

This validates core calendar operations work properly.

### Step 2: Interactive AI Agent Demo
```bash
python langchain_example_mcp.py
```
**What to try:**
- "List my calendars"
- "Add a meeting with John tomorrow at 2pm"
- "Show me events for next week"
- "Create a dentist appointment for Friday at 10am"

**Expected:** Natural language responses with calendar operations.

### Step 3: WebSocket MCP Interface Test
```bash
# Terminal 1: Start the WebSocket bridge
python mcp_radicale_bridge.py

# Terminal 2: Test the enhanced client
python test_mcp_client.py
```
**Expected Output:** 
```
🎉 All tests passed!
Results: 5/5 tests passed
```

### Step 4: Comprehensive Test Suite
```bash
pytest test_mcp_compliance.py test_langchain_integration.py -v
```
**Expected:** All 34 tests (15 MCP + 19 LangChain) should pass.

## 📋 Individual Test Files

### Core Tests
- `test_radicale_calendar_manager.py` - Core calendar operations (9 tests)
- `test_radicale_calendar_manager_edge_cases.py` - Edge cases and error conditions

### MCP Integration Tests
- `test_mcp_client.py` - WebSocket MCP bridge client (5 comprehensive tests)
- `test_mcp_compliance.py` - MCP protocol compliance (15 tests)

### LangChain Integration Tests
- `test_langchain_integration.py` - LangChain tool integration (19 tests)
- `langchain_example_mcp.py` - Interactive AI agent demo

### Event Creation Tests
- `test_new_event.py` - Basic event creation
- `test_new_event_2.py` - Advanced event creation
- `test_new_event_3.py` - Event creation with parameters

### Utility Tests
- `test_read_event.py` - Read and display events
- `test_performance_comparison.py` - Performance metrics

## 🧪 Test Categories

### ✅ Production Ready Tests
All of these should pass in a working system:

**Calendar Operations:**
- Event CRUD operations
- Date range filtering
- Multi-day and all-day events
- Special characters handling
- Timezone support

**MCP Integration:**
- WebSocket communication
- Protocol compliance
- Error handling
- Tool discovery

**LangChain Integration:**
- Tool conversion
- Agent creation
- Async operations
- Natural language processing

### 🔍 Debugging Failed Tests

**Connection Issues:**
```bash
# Check Radicale connectivity
curl -u username:password http://localhost:5232
```

**Import Issues:**
```bash
# Test basic imports
python -c "from radicale_calendar_manager import RadicaleCalendarManager; print('✓ Core import OK')"
python -c "from mcp_radicale_server import MCPRadicaleServer; print('✓ MCP import OK')"
python -c "from langchain_mcp_integration import CalendarMCPIntegration; print('✓ LangChain import OK')"
```

**Environment Issues:**
```bash
# Check environment variables
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('RADICALE_URL:', os.getenv('RADICALE_URL'))"
```

## 📊 Expected Test Results

### All Systems Working
- **Basic Tests:** 9/9 passing
- **MCP WebSocket:** 5/5 passing  
- **MCP Compliance:** 15/15 passing
- **LangChain Integration:** 19/19 passing
- **Total:** 48/48 tests passing

### Current Status
The system is **fully functional and production-ready** with:
- ✅ Core calendar operations working
- ✅ MCP WebSocket interface working  
- ✅ LangChain AI integration working
- ✅ Comprehensive error handling
- ✅ Full test coverage

## 🎯 Quick Health Check

Run this command to quickly verify everything is working:
```bash
python -c "
from radicale_calendar_manager import RadicaleCalendarManager
import os
from dotenv import load_dotenv
load_dotenv()

manager = RadicaleCalendarManager(
    url=os.getenv('RADICALE_URL', 'http://localhost:5232'),
    username=os.getenv('RADICALE_USERNAME', ''),
    password=os.getenv('RADICALE_PASSWORD', '')
)

if manager.connect():
    print('✅ System is ready for testing!')
    calendars = [cal.name for cal in manager.calendars] if manager.calendars else []
    print(f'📅 Available calendars: {calendars}')
else:
    print('❌ Connection failed - check Radicale server and credentials')
"
```

**Expected Output:**
```
✅ System is ready for testing!
📅 Available calendars: ['Default Calendar']
```

## 🆘 Getting Help

If tests fail:
1. Check prerequisites (Radicale running, environment variables set)
2. Review the debugging section above
3. Check individual test outputs for specific error messages
4. Verify all dependencies are installed: `pip install -r requirements.txt`

The testing framework provides detailed error messages and colored output to help identify issues quickly.