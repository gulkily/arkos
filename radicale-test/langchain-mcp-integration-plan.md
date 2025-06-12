# LangChain MCP Integration Plan

## Overview

This plan outlines the migration from direct LangChain tool integration to using LangChain's built-in MCP (Model Context Protocol) converters. This will leverage Anthropic's MCP standard and LangChain's official MCP adapters to create a more standardized and maintainable architecture.

## Current vs. Target Architecture

### Current Architecture
```
LangChain Example → LangChain Tool Adapter → RadicaleCalendarManager → Radicale Server
                   ↗
              OpenAI API
```

### Target Architecture
```
LangChain Example → LangChain MCP Adapter → MCP Server → RadicaleCalendarManager → Radicale Server
                   ↗                        ↗
              OpenAI API              WebSocket/HTTP
```

## Implementation Strategy

### Phase 1: Research & Dependencies (Week 1)

#### 1.1 Package Selection
**Primary Option**: `langchain-mcp-adapters` (Official LangChain package)
- More mature and officially supported
- Better integration with LangGraph
- Active development

**Alternative**: `langchain-mcp-tools` 
- Simpler for basic use cases
- Has built-in `convert_mcp_to_langchain_tools()` function

#### 1.2 Dependencies Update
```bash
# Add new dependencies
pip install langchain-mcp-adapters
pip install mcp  # Core MCP package if needed

# Update requirements.txt
echo "langchain-mcp-adapters>=0.1.0" >> requirements.txt
echo "mcp>=1.0.0" >> requirements.txt
```

#### 1.3 Architecture Documentation
- Document current direct integration approach
- Design new MCP-based architecture
- Identify migration points and compatibility issues

### Phase 2: MCP Server Enhancement (Week 2)

#### 2.1 Upgrade Existing MCP Bridge
**File**: `mcp_radicale_bridge.py`

**Current Issues to Address**:
1. Make it fully MCP-compliant
2. Add proper MCP protocol headers
3. Implement standard MCP error handling
4. Add tool discovery and schema endpoints

**Enhanced Implementation**:
```python
# New structure for mcp_radicale_bridge.py
from mcp.server.fastmcp import FastMCP
from mcp.types import Tool, TextContent
import asyncio

class MCPRadicaleServer:
    def __init__(self):
        self.mcp = FastMCP("RadicaleCalendar")
        self.calendar_manager = RadicaleCalendarManager(...)
        self._register_tools()
    
    def _register_tools(self):
        """Register all calendar tools with MCP server"""
        
        @self.mcp.tool()
        async def list_calendars() -> str:
            """List all available calendars"""
            try:
                calendars = self.calendar_manager.get_calendar_list()
                return json.dumps([cal.name for cal in calendars])
            except Exception as e:
                raise MCPError(f"Failed to list calendars: {e}")
        
        @self.mcp.tool()
        async def get_events(
            calendar_name: str = None,
            start_date: str = None,
            end_date: str = None
        ) -> str:
            """Get events from calendar within date range"""
            try:
                start_dt = datetime.fromisoformat(start_date) if start_date else None
                end_dt = datetime.fromisoformat(end_date) if end_date else None
                events = self.calendar_manager.get_events(calendar_name, start_dt, end_dt)
                return json.dumps(events)
            except Exception as e:
                raise MCPError(f"Failed to get events: {e}")
        
        @self.mcp.tool()
        async def create_event(
            calendar_name: str,
            summary: str,
            start: str,
            end: str = None,
            location: str = None,
            description: str = None
        ) -> str:
            """Create a new calendar event"""
            try:
                event_data = {
                    "summary": summary,
                    "start": start,
                    "end": end,
                    "location": location,
                    "description": description
                }
                event_id = self.calendar_manager.add_event(calendar_name, event_data)
                return json.dumps({"event_id": event_id, "status": "created"})
            except Exception as e:
                raise MCPError(f"Failed to create event: {e}")
        
        @self.mcp.tool()
        async def update_event(
            calendar_name: str,
            event_id: str,
            summary: str = None,
            start: str = None,
            end: str = None,
            location: str = None,
            description: str = None
        ) -> str:
            """Update an existing calendar event"""
            try:
                update_data = {k: v for k, v in locals().items() 
                             if v is not None and k not in ['calendar_name', 'event_id']}
                success = self.calendar_manager.set_event(calendar_name, event_id, update_data)
                return json.dumps({"status": "updated" if success else "failed"})
            except Exception as e:
                raise MCPError(f"Failed to update event: {e}")
        
        @self.mcp.tool()
        async def delete_event(calendar_name: str, event_id: str) -> str:
            """Delete a calendar event"""
            try:
                success = self.calendar_manager.delete_event(calendar_name, event_id)
                return json.dumps({"status": "deleted" if success else "failed"})
            except Exception as e:
                raise MCPError(f"Failed to delete event: {e}")

    async def run_server(self, transport="stdio"):
        """Run the MCP server with specified transport"""
        if transport == "stdio":
            await self.mcp.run()
        elif transport == "http":
            await self.mcp.run_http(port=8765)

# Entry point
if __name__ == "__main__":
    server = MCPRadicaleServer()
    asyncio.run(server.run_server())
```

#### 2.2 MCP Server Configuration
**New File**: `mcp_server_config.json`
```json
{
  "name": "radicale-calendar",
  "version": "1.0.0",
  "description": "MCP server for Radicale calendar operations",
  "transport": {
    "stdio": {},
    "http": {
      "port": 8765
    }
  },
  "tools": [
    {
      "name": "list_calendars",
      "description": "List all available calendars"
    },
    {
      "name": "get_events", 
      "description": "Get events from calendar within date range"
    },
    {
      "name": "create_event",
      "description": "Create a new calendar event"
    },
    {
      "name": "update_event",
      "description": "Update an existing calendar event"
    },
    {
      "name": "delete_event",
      "description": "Delete a calendar event"
    }
  ]
}
```

### Phase 3: LangChain Integration Refactor (Week 3)

#### 3.1 Replace Direct Tool Adapter
**Action**: Replace `langchain_tool_adapter.py` with MCP-based integration

**New File**: `langchain_mcp_integration.py`
```python
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_mcp_adapters.client import MCPClient
import asyncio
from typing import List
from langchain.tools import Tool

class CalendarMCPIntegration:
    def __init__(self, mcp_server_config=None):
        self.mcp_server_config = mcp_server_config or {
            "radicale-calendar": {
                "command": "python",
                "args": ["mcp_radicale_bridge.py"],
                "transport": "stdio"
            }
        }
        self.tools = None
        self.cleanup_fn = None
    
    async def initialize(self) -> List[Tool]:
        """Initialize MCP connection and load tools"""
        try:
            from langchain_mcp_tools import convert_mcp_to_langchain_tools
            
            # Initialize MCP servers and get tools
            self.tools, self.cleanup_fn = await convert_mcp_to_langchain_tools(
                self.mcp_server_config
            )
            
            return self.tools
            
        except ImportError:
            # Fallback to langchain-mcp-adapters if langchain-mcp-tools not available
            return await self._initialize_with_adapters()
    
    async def _initialize_with_adapters(self) -> List[Tool]:
        """Alternative initialization using langchain-mcp-adapters"""
        # This would use the official langchain-mcp-adapters package
        # Implementation depends on final API
        pass
    
    async def cleanup(self):
        """Clean up MCP connections"""
        if self.cleanup_fn:
            await self.cleanup_fn()

# Usage example
async def get_calendar_tools():
    integration = CalendarMCPIntegration()
    tools = await integration.initialize()
    return tools, integration
```

#### 3.2 Update LangChain Example
**File**: `langchain_example.py` (Updated)
```python
"""
Updated LangChain example using MCP integration
"""
import os
import asyncio
from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import SystemMessage

from langchain_mcp_integration import CalendarMCPIntegration

# Load environment variables
load_dotenv()

class MCPCalendarAgent:
    def __init__(self):
        self.mcp_integration = None
        self.agent_executor = None
        
    async def initialize(self):
        """Initialize the MCP-based calendar agent"""
        # Initialize MCP integration
        self.mcp_integration = CalendarMCPIntegration()
        tools = await self.mcp_integration.initialize()
        
        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=(
                "You are a helpful calendar assistant. "
                "You can help users manage their calendar events using MCP tools. "
                "Always confirm actions before executing them. "
                "If you're unsure about any parameters, ask for clarification."
            )),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Initialize the LLM
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Create the agent
        agent = create_openai_functions_agent(
            llm=llm,
            prompt=prompt,
            tools=tools
        )
        
        # Create the agent executor
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True
        )
        
    async def run_operation(self, operation: str) -> str:
        """Run a calendar operation using the MCP-based agent"""
        if not self.agent_executor:
            await self.initialize()
            
        try:
            chat_history = []
            result = await self.agent_executor.ainvoke({
                "input": operation,
                "chat_history": chat_history
            })
            return result["output"]
        except Exception as e:
            return f"Error performing operation: {str(e)}"
    
    async def cleanup(self):
        """Clean up MCP connections"""
        if self.mcp_integration:
            await self.mcp_integration.cleanup()

# Async example usage
async def main():
    agent = MCPCalendarAgent()
    
    try:
        # Example operations
        print("\nExample 1: Listing all calendars")
        result = await agent.run_operation("What calendars do I have access to?")
        print(result)
        
        print("\nExample 2: Adding an event")
        result = await agent.run_operation(
            "Add a meeting with John tomorrow at 2pm for 1 hour in my work calendar"
        )
        print(result)
        
        print("\nExample 3: Listing events")
        result = await agent.run_operation(
            "Show me all events in my work calendar for tomorrow"
        )
        print(result)
        
    finally:
        await agent.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

### Phase 4: Testing & Validation (Week 4)

#### 4.1 MCP Compliance Testing
**New File**: `test_mcp_compliance.py`
```python
import asyncio
import pytest
from langchain_mcp_integration import CalendarMCPIntegration

class TestMCPCompliance:
    """Test MCP protocol compliance and tool conversion"""
    
    @pytest.mark.asyncio
    async def test_mcp_server_startup(self):
        """Test that MCP server starts correctly"""
        integration = CalendarMCPIntegration()
        try:
            tools = await integration.initialize()
            assert len(tools) > 0
            assert any("calendar" in tool.name.lower() for tool in tools)
        finally:
            await integration.cleanup()
    
    @pytest.mark.asyncio
    async def test_tool_conversion(self):
        """Test that MCP tools are correctly converted to LangChain tools"""
        integration = CalendarMCPIntegration()
        try:
            tools = await integration.initialize()
            
            # Check that expected tools are present
            tool_names = [tool.name for tool in tools]
            expected_tools = [
                "list_calendars", "get_events", "create_event", 
                "update_event", "delete_event"
            ]
            
            for expected_tool in expected_tools:
                assert any(expected_tool in name for name in tool_names)
                
        finally:
            await integration.cleanup()
    
    @pytest.mark.asyncio
    async def test_end_to_end_integration(self):
        """Test complete LangChain to MCP to Calendar flow"""
        from langchain_example import MCPCalendarAgent
        
        agent = MCPCalendarAgent()
        try:
            result = await agent.run_operation("List my calendars")
            assert isinstance(result, str)
            assert len(result) > 0
        finally:
            await agent.cleanup()
```

#### 4.2 Performance Comparison
**New File**: `test_performance_comparison.py`
```python
import time
import asyncio
from typing import Dict, Any

async def benchmark_direct_vs_mcp():
    """Compare performance of direct vs MCP integration"""
    
    # Test direct integration (current)
    from langchain_tool_adapter import CalendarToolAdapter
    direct_adapter = CalendarToolAdapter(url="...", username="...", password="...")
    
    start_time = time.time()
    direct_result = direct_adapter.list_calendars()
    direct_time = time.time() - start_time
    
    # Test MCP integration (new)
    from langchain_mcp_integration import CalendarMCPIntegration
    mcp_integration = CalendarMCPIntegration()
    
    try:
        tools = await mcp_integration.initialize()
        start_time = time.time()
        # Execute equivalent operation through MCP
        mcp_time = time.time() - start_time
        
        print(f"Direct integration time: {direct_time:.3f}s")
        print(f"MCP integration time: {mcp_time:.3f}s")
        print(f"Performance ratio: {mcp_time/direct_time:.2f}x")
        
    finally:
        await mcp_integration.cleanup()
```

## Migration Strategy

### Backward Compatibility
1. **Keep existing `langchain_tool_adapter.py`** during transition
2. **Add feature flag** to switch between direct and MCP integration
3. **Gradual migration** of examples and tests

### Configuration Management
```python
# New config option in .env
MCP_INTEGRATION_ENABLED=true
MCP_SERVER_TRANSPORT=stdio  # or http
MCP_SERVER_PORT=8765
```

### Rollback Plan
1. Keep original files with `.legacy` suffix
2. Feature flag to disable MCP integration
3. Documentation of migration steps for easy reversal

## Benefits of MCP Integration

### Technical Benefits
1. **Standardization**: Use industry-standard MCP protocol
2. **Better Tool Discovery**: Automatic schema discovery and validation
3. **Multi-Server Support**: Easy to add additional MCP servers
4. **Official Support**: Leverage official LangChain MCP adapters

### Architectural Benefits
1. **Loose Coupling**: MCP provides clear separation between LangChain and calendar logic
2. **Scalability**: MCP servers can be distributed and load-balanced
3. **Interoperability**: MCP tools work across different AI frameworks
4. **Ecosystem Access**: Access to 2000+ existing MCP servers

### Maintenance Benefits
1. **Reduced Custom Code**: Less custom integration code to maintain
2. **Better Error Handling**: MCP provides standardized error protocols
3. **Improved Testing**: Standard MCP testing tools and practices
4. **Future-Proofing**: Aligned with industry standards

## Timeline Summary

- **Week 1**: Research, dependencies, documentation
- **Week 2**: Enhance MCP server, add MCP compliance
- **Week 3**: Refactor LangChain integration, update examples
- **Week 4**: Testing, validation, performance analysis

## Success Criteria

1. ✅ LangChain uses MCP server instead of direct tool adapter
2. ✅ All existing functionality works through MCP integration
3. ✅ Performance is comparable or better than direct integration
4. ✅ Full MCP protocol compliance
5. ✅ Comprehensive test coverage
6. ✅ Updated documentation and examples

This plan provides a structured approach to migrating to LangChain's built-in MCP converters while maintaining system reliability and adding new capabilities.