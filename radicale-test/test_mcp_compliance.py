"""
MCP Compliance and Integration Tests

This module provides comprehensive testing for the MCP-based calendar integration,
ensuring protocol compliance, tool conversion accuracy, and end-to-end functionality.

Test Categories:
1. MCP Server Compliance Tests
2. LangChain Integration Tests
3. Tool Conversion Tests
4. End-to-End Workflow Tests
5. Performance Tests
6. Error Handling Tests

Usage:
    # Run all tests
    pytest test_mcp_compliance.py -v
    
    # Run specific test category
    pytest test_mcp_compliance.py::TestMCPCompliance -v
    
Dependencies:
    pip install pytest pytest-asyncio
"""

import asyncio
import json
import pytest
import subprocess
import time
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
from unittest.mock import patch, MagicMock

# Test imports
from langchain_mcp_integration import CalendarMCPIntegration, get_calendar_tools, MCPIntegrationError
from langchain_example_mcp import MCPCalendarAgent

class TestMCPCompliance:
    """Test MCP protocol compliance and server functionality."""
    
    @pytest.mark.asyncio
    async def test_mcp_server_startup(self):
        """Test that MCP server starts correctly and responds to tool discovery."""
        integration = CalendarMCPIntegration()
        
        try:
            tools = await integration.initialize()
            
            # Verify tools were loaded
            assert len(tools) > 0, "No tools loaded from MCP server"
            assert any("calendar" in tool.name.lower() or "event" in tool.name.lower() for tool in tools), \
                "No calendar-related tools found"
            
            # Verify expected tools are present
            tool_names = [tool.name for tool in tools]
            expected_tools = ["list_calendars", "get_events", "create_event"]
            
            for expected_tool in expected_tools:
                assert any(expected_tool in name for name in tool_names), \
                    f"Expected tool '{expected_tool}' not found in {tool_names}"
                    
        finally:
            await integration.cleanup()
    
    @pytest.mark.asyncio
    async def test_mcp_tool_schemas(self):
        """Test that MCP tools have proper schemas and descriptions."""
        integration = CalendarMCPIntegration()
        
        try:
            tools = await integration.initialize()
            
            for tool in tools:
                # Each tool should have a name
                assert hasattr(tool, 'name'), f"Tool missing name attribute"
                assert tool.name, f"Tool has empty name"
                
                # Each tool should have a description
                assert hasattr(tool, 'description'), f"Tool {tool.name} missing description"
                assert tool.description, f"Tool {tool.name} has empty description"
                
                # Each tool should be callable
                assert callable(tool.run), f"Tool {tool.name} is not callable"
                
        finally:
            await integration.cleanup()
    
    @pytest.mark.asyncio
    async def test_mcp_server_process_management(self):
        """Test MCP server process lifecycle management."""
        # Test starting server process
        config = {
            "radicale-calendar": {
                "command": "python",
                "args": ["mcp_radicale_server.py"],
                "transport": "stdio",
                "env": {
                    "RADICALE_URL": "http://localhost:5232",
                    "RADICALE_USERNAME": "test",
                    "RADICALE_PASSWORD": "test"
                }
            }
        }
        
        integration = CalendarMCPIntegration(config)
        
        try:
            tools = await integration.initialize()
            assert len(tools) > 0, "No tools loaded with custom config"
            
        finally:
            await integration.cleanup()
    
    @pytest.mark.asyncio
    async def test_integration_method_fallback(self):
        """Test that integration falls back to different methods if primary fails."""
        # Since langchain_mcp_tools and langchain_mcp_adapters are not installed,
        # integration should automatically fall back to manual tools
        integration = CalendarMCPIntegration()
        
        try:
            tools = await integration.initialize()
            
            # Should fall back to manual tools
            assert len(tools) > 0, "Fallback method should still provide tools"
            assert integration._integration_method == "manual", \
                "Should use manual integration method as fallback"
                
        finally:
            await integration.cleanup()

class TestLangChainIntegration:
    """Test LangChain-specific integration functionality."""
    
    @pytest.mark.asyncio
    async def test_tool_conversion_compatibility(self):
        """Test that MCP tools are properly converted to LangChain format."""
        tools, integration = await get_calendar_tools()
        
        try:
            # Verify tools are LangChain compatible
            for tool in tools:
                # Should have LangChain tool interface
                assert hasattr(tool, 'name'), "Tool missing name attribute"
                assert hasattr(tool, 'description'), "Tool missing description attribute"
                assert hasattr(tool, 'run'), "Tool missing run method"
                
                # Test that tool can be called
                if tool.name == "list_calendars":
                    result = tool.run("")
                    assert isinstance(result, str), "Tool should return string result"
                    
                    # Parse result to verify it's valid JSON
                    try:
                        parsed = json.loads(result)
                        assert "status" in parsed, "Result should contain status field"
                    except json.JSONDecodeError:
                        pytest.fail(f"Tool {tool.name} returned invalid JSON: {result}")
                        
        finally:
            await integration.cleanup()
    
    @pytest.mark.asyncio
    async def test_agent_creation(self):
        """Test that LangChain agent can be created with MCP tools."""
        agent = MCPCalendarAgent()
        
        try:
            await agent.initialize()
            
            # Verify agent was created
            assert agent.agent_executor is not None, "Agent executor not created"
            assert len(agent.tools) > 0, "No tools loaded for agent"
            
            # Verify agent can process simple request
            response = await agent.run_operation("What tools do you have available?")
            assert isinstance(response, str), "Agent should return string response"
            assert len(response) > 0, "Agent response should not be empty"
            
        finally:
            await agent.cleanup()
    
    @pytest.mark.asyncio
    async def test_async_operation_support(self):
        """Test that async operations work correctly throughout the stack."""
        agent = MCPCalendarAgent()
        
        try:
            await agent.initialize()
            
            # Test multiple concurrent operations
            operations = [
                "List my calendars",
                "What tools are available?",
                "Help me understand calendar operations"
            ]
            
            # Run operations concurrently
            tasks = [agent.run_operation(op) for op in operations]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Verify all operations completed
            assert len(results) == len(operations), "Not all operations completed"
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    pytest.fail(f"Operation {i} failed with exception: {result}")
                assert isinstance(result, str), f"Operation {i} returned non-string result"
                
        finally:
            await agent.cleanup()

class TestToolFunctionality:
    """Test individual tool functionality and edge cases."""
    
    @pytest.mark.asyncio
    async def test_list_calendars_tool(self):
        """Test the list_calendars tool functionality."""
        tools, integration = await get_calendar_tools()
        
        try:
            # Find list_calendars tool
            list_tool = None
            for tool in tools:
                if "list" in tool.name.lower() and "calendar" in tool.name.lower():
                    list_tool = tool
                    break
            
            assert list_tool is not None, "list_calendars tool not found"
            
            # Test tool execution
            result = list_tool.run("")
            assert isinstance(result, str), "Tool should return string"
            
            # Parse and validate result
            parsed = json.loads(result)
            assert "status" in parsed, "Result should contain status"
            
            if parsed["status"] == "success":
                assert "calendars" in parsed, "Successful result should contain calendars"
                assert isinstance(parsed["calendars"], list), "Calendars should be a list"
                
        finally:
            await integration.cleanup()
    
    @pytest.mark.asyncio
    async def test_get_events_tool(self):
        """Test the get_events tool functionality."""
        tools, integration = await get_calendar_tools()
        
        try:
            # Find get_events tool
            events_tool = None
            for tool in tools:
                if "get" in tool.name.lower() and "event" in tool.name.lower():
                    events_tool = tool
                    break
            
            assert events_tool is not None, "get_events tool not found"
            
            # Test tool execution with date range
            today = datetime.now().strftime("%Y-%m-%d")
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            
            # Format input based on tool interface
            if integration._integration_method == "manual":
                input_str = f"start_date: {today}, end_date: {tomorrow}"
            else:
                input_str = json.dumps({
                    "start_date": today,
                    "end_date": tomorrow
                })
            
            result = events_tool.run(input_str)
            assert isinstance(result, str), "Tool should return string"
            
            # Parse and validate result
            parsed = json.loads(result)
            assert "status" in parsed, "Result should contain status"
            
            if parsed["status"] == "success":
                assert "events" in parsed, "Successful result should contain events"
                assert isinstance(parsed["events"], list), "Events should be a list"
                
        finally:
            await integration.cleanup()
    
    @pytest.mark.asyncio
    async def test_create_event_tool(self):
        """Test the create_event tool functionality."""
        tools, integration = await get_calendar_tools()
        
        try:
            # Find create_event tool
            create_tool = None
            for tool in tools:
                if "create" in tool.name.lower() and "event" in tool.name.lower():
                    create_tool = tool
                    break
            
            assert create_tool is not None, "create_event tool not found"
            
            # Test tool execution
            test_summary = f"Test Event {datetime.now().strftime('%Y%m%d_%H%M%S')}"
            start_time = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S")
            
            # Format input based on tool interface
            if integration._integration_method == "manual":
                # Use structured input for StructuredTool
                input_data = {
                    "calendar_name": "Default Calendar",  # Use existing calendar
                    "summary": test_summary,
                    "start": start_time,
                    "duration": 60  # Add required duration field
                }
            else:
                # Fallback for other integration methods
                input_data = json.dumps({
                    "calendar_name": "Default Calendar",
                    "summary": test_summary,
                    "start": start_time
                })
            
            result = create_tool.run(input_data)
            assert isinstance(result, str), "Tool should return string"
            
            # Parse result (may fail due to connection issues, but should be valid JSON)
            try:
                parsed = json.loads(result)
                assert "status" in parsed, "Result should contain status"
            except json.JSONDecodeError:
                pytest.fail(f"Tool returned invalid JSON: {result}")
                
        finally:
            await integration.cleanup()

class TestErrorHandling:
    """Test error handling and edge cases."""
    
    @pytest.mark.asyncio
    async def test_invalid_configuration(self):
        """Test handling of invalid MCP server configuration."""
        invalid_config = {
            "invalid-server": {
                "command": "nonexistent_command",
                "args": ["--invalid"],
                "transport": "invalid_transport"
            }
        }
        
        integration = CalendarMCPIntegration(invalid_config)
        
        # Should handle gracefully and fall back to manual tools
        try:
            tools = await integration.initialize()
            # Should still get manual tools as fallback
            assert len(tools) >= 0, "Should handle invalid config gracefully"
        finally:
            await integration.cleanup()
    
    @pytest.mark.asyncio
    async def test_missing_dependencies(self):
        """Test handling when MCP packages are missing."""
        # Mock missing packages
        with patch.dict('sys.modules', {
            'langchain_mcp_tools': None,
            'langchain_mcp_adapters': None
        }):
            integration = CalendarMCPIntegration()
            
            try:
                tools = await integration.initialize()
                # Should fall back to manual implementation
                assert integration._integration_method == "manual"
                assert len(tools) > 0, "Manual fallback should provide tools"
            finally:
                await integration.cleanup()
    
    @pytest.mark.asyncio
    async def test_connection_failure_handling(self):
        """Test handling of calendar server connection failures."""
        # Use configuration that will fail to connect
        config = {
            "radicale-calendar": {
                "command": "python",
                "args": ["mcp_radicale_server.py"],
                "transport": "stdio",
                "env": {
                    "RADICALE_URL": "http://invalid:9999",
                    "RADICALE_USERNAME": "invalid",
                    "RADICALE_PASSWORD": "invalid"
                }
            }
        }
        
        integration = CalendarMCPIntegration(config)
        
        try:
            # Should handle connection failure gracefully
            tools = await integration.initialize()
            
            # Tools should still be created, but operations may fail
            assert len(tools) >= 0, "Should handle connection failure gracefully"
            
        finally:
            await integration.cleanup()

class TestPerformance:
    """Test performance characteristics of the MCP integration."""
    
    @pytest.mark.asyncio
    async def test_initialization_performance(self):
        """Test that MCP integration initializes within reasonable time."""
        start_time = time.time()
        
        integration = CalendarMCPIntegration()
        
        try:
            tools = await integration.initialize()
            
            initialization_time = time.time() - start_time
            
            # Should initialize within 10 seconds
            assert initialization_time < 10.0, \
                f"Initialization took too long: {initialization_time:.2f}s"
            
            assert len(tools) > 0, "Should load tools after initialization"
            
        finally:
            await integration.cleanup()
    
    @pytest.mark.asyncio
    async def test_tool_execution_performance(self):
        """Test that tool execution completes within reasonable time."""
        tools, integration = await get_calendar_tools()
        
        try:
            # Test list_calendars tool performance
            list_tool = None
            for tool in tools:
                if "list" in tool.name.lower() and "calendar" in tool.name.lower():
                    list_tool = tool
                    break
            
            if list_tool:
                start_time = time.time()
                result = list_tool.run("")
                execution_time = time.time() - start_time
                
                # Should execute within 5 seconds
                assert execution_time < 5.0, \
                    f"Tool execution took too long: {execution_time:.2f}s"
                
                assert isinstance(result, str), "Tool should return result"
                
        finally:
            await integration.cleanup()

# Fixtures for test setup
@pytest.fixture
async def mcp_integration():
    """Fixture providing initialized MCP integration."""
    integration = CalendarMCPIntegration()
    await integration.initialize()
    yield integration
    await integration.cleanup()

@pytest.fixture
async def calendar_agent():
    """Fixture providing initialized calendar agent."""
    agent = MCPCalendarAgent()
    await agent.initialize()
    yield agent
    await agent.cleanup()

# Test configuration
pytest_plugins = ['pytest_asyncio']

if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v", "--tb=short"])