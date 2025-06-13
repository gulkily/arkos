# API Documentation

Complete API reference for the LangChain MCP Calendar Integration.

## Table of Contents

- [Core Classes](#core-classes)
- [MCP Integration](#mcp-integration)
- [Calendar Manager](#calendar-manager)
- [LangChain Tools](#langchain-tools)
- [Usage Examples](#usage-examples)
- [Error Handling](#error-handling)
- [Configuration](#configuration)

## Core Classes

### MCPCalendarAgent

The main class for LangChain integration with MCP calendar tools.

```python
class MCPCalendarAgent:
    def __init__(self, model: str = "gpt-3.5-turbo", temperature: float = 0)
```

#### Parameters
- `model` (str): OpenAI model to use. Default: "gpt-3.5-turbo"
- `temperature` (float): LLM temperature setting. Default: 0

#### Methods

##### `async initialize()`
Initialize the MCP integration and create the LangChain agent.

```python
agent = MCPCalendarAgent()
await agent.initialize()
```

**Returns:** None
**Raises:** 
- `ValueError`: If OPENAI_API_KEY not found
- `MCPIntegrationError`: If MCP initialization fails

##### `async run_operation(operation: str, chat_history: List[Dict] = None) -> str`
Execute a calendar operation using natural language.

```python
result = await agent.run_operation("List my calendars")
result = await agent.run_operation(
    "Schedule a meeting with John tomorrow at 2pm", 
    chat_history=previous_messages
)
```

**Parameters:**
- `operation` (str): Natural language description of the operation
- `chat_history` (List[Dict], optional): Previous conversation context

**Returns:** String response from the agent
**Raises:** Exception on operation failure

##### `async run_interactive_session()`
Start an interactive chat session with the calendar agent.

```python
await agent.run_interactive_session()
```

**Returns:** None (runs until user exits)

##### `async cleanup()`
Clean up MCP integration resources.

```python
await agent.cleanup()
```

**Returns:** None

##### `get_integration_info() -> Dict[str, Any]`
Get information about the current MCP integration.

```python
info = agent.get_integration_info()
print(f"Method: {info['integration_method']}")
print(f"Tools: {info['tool_count']}")
```

**Returns:** Dictionary with integration details

## MCP Integration

### CalendarMCPIntegration

Core class managing MCP server connections and tool conversion.

```python
class CalendarMCPIntegration:
    def __init__(self, mcp_server_config: Optional[Dict[str, Any]] = None)
```

#### Parameters
- `mcp_server_config` (Dict, optional): Custom MCP server configuration

#### Methods

##### `async initialize() -> List[BaseTool]`
Initialize MCP connection and load calendar tools.

```python
integration = CalendarMCPIntegration()
tools = await integration.initialize()
```

**Returns:** List of LangChain-compatible tools
**Raises:** `MCPIntegrationError` on failure

**Integration Methods (automatic fallback):**
1. `langchain-mcp-tools` (primary)
2. `langchain-mcp-adapters` (fallback)
3. Manual tool creation (ultimate fallback)

##### `async cleanup()`
Clean up MCP connections and resources.

```python
await integration.cleanup()
```

##### `get_tool_names() -> List[str]`
Get names of all loaded tools.

```python
tool_names = integration.get_tool_names()
# Returns: ['list_calendars', 'get_events', 'create_event']
```

##### `get_tool_descriptions() -> Dict[str, str]`
Get descriptions of all loaded tools.

```python
descriptions = integration.get_tool_descriptions()
```

##### `get_integration_info() -> Dict[str, Any]`
Get integration status and configuration details.

```python
info = integration.get_integration_info()
```

### Convenience Function

##### `async get_calendar_tools(config: Optional[Dict] = None) -> Tuple[List[BaseTool], CalendarMCPIntegration]`
Quick function to get calendar tools and integration instance.

```python
tools, integration = await get_calendar_tools()
try:
    # Use tools with LangChain
    agent = create_openai_functions_agent(llm, prompt, tools)
finally:
    await integration.cleanup()
```

## Calendar Manager

### RadicaleCalendarManager

Low-level calendar operations interface for Radicale CalDAV server.

```python
class RadicaleCalendarManager:
    def __init__(self, url: str, username: str, password: str)
```

#### Parameters
- `url` (str): Radicale server URL (e.g., "http://localhost:5232")
- `username` (str): CalDAV username (empty string for no auth)
- `password` (str): CalDAV password (empty string for no auth)

#### Methods

##### `connect() -> bool`
Establish connection to Radicale server.

```python
manager = RadicaleCalendarManager("http://localhost:5232", "", "")
if manager.connect():
    print(f"Connected! Found {len(manager.calendars)} calendars")
```

**Returns:** True if successful, False otherwise

##### `get_calendar(calendar_name: Optional[str] = None)`
Retrieve a calendar by name.

```python
calendar = manager.get_calendar("My Calendar")
default_calendar = manager.get_calendar()  # First available
```

**Parameters:**
- `calendar_name` (str, optional): Calendar name. If None, returns first calendar.

**Returns:** Calendar object or None if not found

##### `get_events(calendar_name: Optional[str] = None, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Dict]`
Fetch events from a calendar within date range.

```python
from datetime import datetime, timedelta

# Get events for next 7 days
start = datetime.now()
end = start + timedelta(days=7)
events = manager.get_events("My Calendar", start, end)

# Get all upcoming events (30 days default)
events = manager.get_events("My Calendar")
```

**Parameters:**
- `calendar_name` (str, optional): Calendar name
- `start_date` (datetime, optional): Start of date range
- `end_date` (datetime, optional): End of date range

**Returns:** List of event dictionaries:
```python
{
    "id": "unique-event-id",
    "summary": "Event Title",
    "start": "2023-06-01T10:00:00",
    "end": "2023-06-01T11:00:00",
    "location": "Office",
    "description": "Event description"
}
```

##### `add_event(calendar_name: str, event_data: Dict) -> str`
Create a new calendar event.

```python
event_data = {
    "summary": "Team Meeting",
    "start": "2023-06-01T10:00:00",
    "end": "2023-06-01T11:00:00",
    "location": "Conference Room",
    "description": "Weekly team sync"
}
event_id = manager.add_event("Work Calendar", event_data)
```

**Parameters:**
- `calendar_name` (str): Target calendar name
- `event_data` (Dict): Event details

**Required fields in event_data:**
- `summary` (str): Event title
- `start` (str): Start time in ISO format

**Optional fields:**
- `end` (str): End time (defaults to start + 1 hour)
- `location` (str): Event location
- `description` (str): Event description

**Returns:** Event ID string
**Raises:** `ValueError` for missing required fields or invalid data

##### `set_event(calendar_name: str, event_id: str, event_data: Dict) -> bool`
Update an existing event.

```python
update_data = {
    "summary": "Updated Meeting Title",
    "location": "New Location"
}
success = manager.set_event("Work Calendar", event_id, update_data)
```

**Parameters:**
- `calendar_name` (str): Calendar containing the event
- `event_id` (str): Event ID to update
- `event_data` (Dict): Fields to update

**Returns:** True if successful
**Raises:** `ValueError` if calendar or event not found

##### `delete_event(calendar_name: str, event_id: str) -> bool`
Delete an event from calendar.

```python
success = manager.delete_event("Work Calendar", event_id)
```

**Parameters:**
- `calendar_name` (str): Calendar containing the event
- `event_id` (str): Event ID to delete

**Returns:** True if successful
**Raises:** `ValueError` if calendar or event not found

## LangChain Tools

The MCP integration provides these LangChain tools:

### list_calendars
Lists all available calendars.

**Input:** Empty string or no parameters
**Output:** JSON string with calendar list

```python
result = list_calendars_tool.run("")
# Returns: {"status": "success", "calendars": ["Work", "Personal"], "count": 2}
```

### get_events  
Retrieves events from a calendar with optional date filtering.

**Input:** Parameter string or structured input
**Output:** JSON string with events

```python
# Natural language input
result = get_events_tool.run("calendar_name: Work, start_date: 2023-06-01")
result = get_events_tool.run("today")
result = get_events_tool.run("next 7 days")

# Returns: {"status": "success", "calendar": "Work", "events": [...], "count": 5}
```

### create_event
Creates a new calendar event with natural language date/time support.

**Input:** Structured parameters (StructuredTool)
**Output:** JSON string with creation result

```python
from pydantic import BaseModel

class CreateEventInput(BaseModel):
    calendar_name: str
    summary: str
    start: str  # Natural language: "tomorrow at 2pm"
    duration: int = 60  # Minutes

result = create_event_tool.run({
    "calendar_name": "Work Calendar",
    "summary": "Team Meeting",
    "start": "tomorrow at 2pm",
    "duration": 90
})
# Returns: {"status": "success", "event_id": "...", "message": "Event created"}
```

## Usage Examples

### Basic Agent Usage

```python
import asyncio
from langchain_example_mcp import MCPCalendarAgent

async def main():
    agent = MCPCalendarAgent()
    try:
        await agent.initialize()
        
        # List calendars
        result = await agent.run_operation("What calendars do I have?")
        print(result)
        
        # Create event
        result = await agent.run_operation(
            "Schedule a dentist appointment next Friday at 10am"
        )
        print(result)
        
        # Get events
        result = await agent.run_operation("What meetings do I have tomorrow?")
        print(result)
        
    finally:
        await agent.cleanup()

asyncio.run(main())
```

### Custom LangChain Integration

```python
import asyncio
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_mcp_integration import get_calendar_tools

async def custom_integration():
    # Get calendar tools
    tools, integration = await get_calendar_tools()
    
    try:
        # Create custom prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a calendar assistant. Be concise and helpful."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create LLM and agent
        llm = ChatOpenAI(model="gpt-4", temperature=0)
        agent = create_openai_functions_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        
        # Use the agent
        result = await agent_executor.ainvoke({
            "input": "Create a meeting for tomorrow at 3pm about project planning"
        })
        
        print(result["output"])
        
    finally:
        await integration.cleanup()

asyncio.run(custom_integration())
```

### Direct Calendar Manager Usage

```python
from radicale_calendar_manager import RadicaleCalendarManager
from datetime import datetime, timedelta

# Initialize manager
manager = RadicaleCalendarManager(
    url="http://localhost:5232",
    username="",
    password=""
)

# Connect and use
if manager.connect():
    # Create event
    event_data = {
        "summary": "Team Meeting",
        "start": "2023-06-01T14:00:00",
        "end": "2023-06-01T15:00:00",
        "location": "Conference Room A"
    }
    event_id = manager.add_event("Work Calendar", event_data)
    
    # Get events for next week
    start = datetime.now()
    end = start + timedelta(days=7)
    events = manager.get_events("Work Calendar", start, end)
    
    # Update event
    manager.set_event("Work Calendar", event_id, {
        "summary": "Updated Meeting Title"
    })
    
    # Delete event
    manager.delete_event("Work Calendar", event_id)
```

## Error Handling

### Common Exceptions

#### MCPIntegrationError
Raised when MCP integration fails to initialize.

```python
from langchain_mcp_integration import MCPIntegrationError

try:
    integration = CalendarMCPIntegration()
    tools = await integration.initialize()
except MCPIntegrationError as e:
    print(f"MCP integration failed: {e}")
    # Handle fallback or exit
```

#### ValueError
Raised for invalid input parameters or missing required data.

```python
try:
    event_id = manager.add_event("Work", {"summary": ""})  # Empty summary
except ValueError as e:
    print(f"Invalid event data: {e}")
```

#### ConnectionError
Network-related connection failures.

```python
try:
    success = manager.connect()
    if not success:
        raise ConnectionError("Failed to connect to CalDAV server")
except ConnectionError as e:
    print(f"Connection failed: {e}")
    # Check server status, credentials, etc.
```

### Error Response Format

Tools return structured error responses:

```python
{
    "status": "error",
    "message": "Descriptive error message",
    "error_type": "validation_error",  # Optional
    "details": {...}  # Optional additional context
}
```

### Robust Error Handling Pattern

```python
async def robust_calendar_operation():
    agent = None
    try:
        agent = MCPCalendarAgent()
        await agent.initialize()
        
        result = await agent.run_operation("List my calendars")
        
        # Parse result if needed
        import json
        if result.startswith("{"):
            parsed = json.loads(result)
            if parsed.get("status") == "error":
                print(f"Operation failed: {parsed['message']}")
                return
        
        print(f"Success: {result}")
        
    except ValueError as e:
        print(f"Configuration error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if agent:
            await agent.cleanup()
```

## Configuration

### Environment Variables

```env
# Required
OPENAI_API_KEY=sk-...

# CalDAV Server
RADICALE_URL=http://localhost:5232
RADICALE_USERNAME=user
RADICALE_PASSWORD=pass

# Optional
LOG_LEVEL=INFO
MCP_TRANSPORT=stdio
MCP_PORT=8765
```

### MCP Server Configuration

```python
mcp_config = {
    "radicale-calendar": {
        "command": "python",
        "args": ["mcp_radicale_server.py"],
        "transport": "stdio",
        "env": {
            "RADICALE_URL": "http://localhost:5232",
            "RADICALE_USERNAME": "",
            "RADICALE_PASSWORD": ""
        }
    }
}

integration = CalendarMCPIntegration(mcp_config)
```

### Custom Agent Configuration

```python
# Custom model and temperature
agent = MCPCalendarAgent(
    model="gpt-4",
    temperature=0.1
)

# Custom prompt modifications
agent._create_system_prompt = lambda: "Custom prompt here..."
```

## Best Practices

### Resource Management
Always use async context managers or try/finally blocks:

```python
async def good_practice():
    tools, integration = await get_calendar_tools()
    try:
        # Use tools
        pass
    finally:
        await integration.cleanup()
```

### Natural Language Processing
Use clear, specific language for better results:

```python
# Good
"Schedule a team meeting next Tuesday at 2pm for 1 hour"

# Less optimal  
"set up meeting next week sometime"
```

### Error Handling
Check tool responses for errors:

```python
result = tool.run(input_data)
parsed = json.loads(result)
if parsed.get("status") == "error":
    handle_error(parsed["message"])
```

### Performance
- Use connection pooling for multiple operations
- Cache calendar lists when possible
- Limit date ranges for large calendars
- Clean up resources promptly

This API documentation provides comprehensive coverage of all available classes, methods, and usage patterns for the LangChain MCP Calendar Integration.