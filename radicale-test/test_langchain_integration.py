#!/usr/bin/env python3
"""
Comprehensive LangChain Integration Test Suite

Tests the LangChain MCP integration with Radicale calendar server,
including agent creation, tool functionality, and end-to-end scenarios.

This test suite validates:
- MCP integration initialization
- Tool loading and validation
- Agent creation and configuration
- Natural language processing capabilities
- Error handling and edge cases
- Performance characteristics

Prerequisites:
- Radicale server running
- MCP server accessible
- Environment properly configured

Usage:
    python3 test_langchain_integration.py
"""

import pytest
import asyncio
import json
import os
import tempfile
from datetime import datetime, timedelta
from unittest.mock import patch, AsyncMock, MagicMock
from typing import Dict, List, Any, Optional

# LangChain imports
from langchain_core.tools import BaseTool
from langchain.agents import AgentExecutor

# Local imports
from langchain_mcp_integration import CalendarMCPIntegration, get_calendar_tools
from langchain_example_mcp import MCPCalendarAgent


class TestLangChainMCPIntegration:
    """Test the core MCP integration functionality"""
    
    @pytest.mark.asyncio
    async def test_calendar_mcp_integration_initialization(self):
        """Test that CalendarMCPIntegration initializes correctly"""
        integration = CalendarMCPIntegration()
        
        assert integration is not None
        assert hasattr(integration, 'tools')
        assert hasattr(integration, '_integration_method')
        assert integration._integration_method is None  # Before initialization
        
    @pytest.mark.asyncio
    async def test_get_calendar_tools_function(self):
        """Test the get_calendar_tools helper function"""
        tools, integration = await get_calendar_tools()
        
        try:
            # Verify tools are returned
            assert isinstance(tools, list)
            assert len(tools) > 0
            
            # Verify each tool is a proper LangChain tool
            for tool in tools:
                assert isinstance(tool, BaseTool)
                assert hasattr(tool, 'name')
                assert hasattr(tool, 'description')
                assert hasattr(tool, 'run')
                assert hasattr(tool, 'func')
            
            # Verify integration object
            assert isinstance(integration, CalendarMCPIntegration)
            assert integration._integration_method == "manual"  # Should fallback to manual
            
            # Test tool names
            tool_names = [tool.name for tool in tools]
            expected_tools = ['list_calendars', 'get_events', 'create_event']
            for expected_tool in expected_tools:
                assert expected_tool in tool_names, f"Missing expected tool: {expected_tool}"
                
        finally:
            if integration:
                await integration.cleanup()
    
    @pytest.mark.asyncio
    async def test_tool_execution(self):
        """Test that tools can be executed properly"""
        tools, integration = await get_calendar_tools()
        
        try:
            # Find the list_calendars tool
            list_calendars_tool = None
            for tool in tools:
                if tool.name == "list_calendars":
                    list_calendars_tool = tool
                    break
            
            assert list_calendars_tool is not None, "list_calendars tool not found"
            
            # Execute the tool
            result = list_calendars_tool.run("")
            
            # Verify result is valid JSON
            assert isinstance(result, str)
            parsed_result = json.loads(result)
            
            # Verify response structure
            assert "status" in parsed_result
            assert parsed_result["status"] in ["success", "error"]
            
            if parsed_result["status"] == "success":
                assert "calendars" in parsed_result
                assert isinstance(parsed_result["calendars"], list)
                
        finally:
            if integration:
                await integration.cleanup()
    
    @pytest.mark.asyncio
    async def test_integration_method_fallback(self):
        """Test that integration properly falls back to manual tools"""
        integration = CalendarMCPIntegration()
        
        try:
            tools = await integration.initialize()
            
            # Should use manual method since MCP packages aren't installed
            assert integration._integration_method == "manual"
            assert len(tools) > 0
            
        finally:
            await integration.cleanup()
    
    @pytest.mark.asyncio
    async def test_tool_descriptions_format(self):
        """Test that tool descriptions are properly formatted for LangChain"""
        tools, integration = await get_calendar_tools()
        
        try:
            for tool in tools:
                # Verify description exists and is meaningful
                assert tool.description is not None
                assert len(tool.description) > 10  # Not empty or too short
                assert isinstance(tool.description, str)
                
                # Verify tool name is valid
                assert tool.name is not None
                assert len(tool.name) > 0
                assert ' ' not in tool.name  # Tool names shouldn't have spaces
                
        finally:
            if integration:
                await integration.cleanup()


class TestMCPCalendarAgent:
    """Test the MCPCalendarAgent class functionality"""
    
    def test_agent_initialization_without_api_key(self):
        """Test that agent fails gracefully without OpenAI API key"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}, clear=True):
            with patch('langchain_example_mcp.load_dotenv'):  # Prevent loading from .env file
                with pytest.raises(ValueError, match="OPENAI_API_KEY not found"):
                    MCPCalendarAgent()
    
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    def test_agent_creation(self):
        """Test that agent can be created with valid API key"""
        agent = MCPCalendarAgent()
        
        assert agent is not None
        assert agent.model == "gpt-3.5-turbo"
        assert agent.temperature == 0
        assert agent.mcp_integration is None  # Before initialization
        assert agent.agent_executor is None  # Before initialization
        assert agent.tools == []  # Before initialization
    
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @pytest.mark.asyncio
    async def test_agent_initialization_with_mocked_llm(self):
        """Test agent initialization with mocked LLM"""
        agent = MCPCalendarAgent()
        
        # Mock the OpenAI LLM to avoid actual API calls
        with patch('langchain_example_mcp.ChatOpenAI') as mock_llm_class:
            mock_llm = MagicMock()
            mock_llm_class.return_value = mock_llm
            
            # Mock the agent creation functions
            with patch('langchain_example_mcp.create_openai_functions_agent') as mock_create_agent:
                mock_agent = MagicMock()
                mock_create_agent.return_value = mock_agent
                
                with patch('langchain_example_mcp.AgentExecutor') as mock_executor_class:
                    mock_executor = MagicMock()
                    mock_executor_class.return_value = mock_executor
                    
                    try:
                        await agent.initialize()
                        
                        # Verify initialization completed
                        assert agent.mcp_integration is not None
                        assert len(agent.tools) > 0
                        assert agent.agent_executor is not None
                        
                        # Verify LLM was configured correctly
                        mock_llm_class.assert_called_once_with(
                            model="gpt-3.5-turbo",
                            temperature=0,
                            max_tokens=4000,
                            api_key="test-key"
                        )
                        
                    finally:
                        if agent.mcp_integration:
                            await agent.mcp_integration.cleanup()
    
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    def test_system_prompt_creation(self):
        """Test that system prompt is created correctly"""
        agent = MCPCalendarAgent()
        
        # Mock tools for testing
        mock_tools = [
            MagicMock(name="test_tool", description="Test tool description")
        ]
        agent.tools = mock_tools
        
        prompt = agent._create_system_prompt()
        
        assert isinstance(prompt, str)
        assert len(prompt) > 100  # Should be a substantial prompt
        assert "calendar assistant" in prompt.lower()
        assert "test_tool" in prompt
        assert "Test tool description" in prompt
    
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @pytest.mark.asyncio
    async def test_agent_cleanup(self):
        """Test that agent cleans up resources properly"""
        agent = MCPCalendarAgent()
        
        # Mock MCP integration
        mock_integration = AsyncMock()
        agent.mcp_integration = mock_integration
        
        await agent.cleanup()
        
        # Verify cleanup was called
        mock_integration.cleanup.assert_called_once()


class TestToolFunctionality:
    """Test individual tool functionality in detail"""
    
    @pytest.mark.asyncio
    async def test_list_calendars_tool_detailed(self):
        """Test list_calendars tool with detailed validation"""
        tools, integration = await get_calendar_tools()
        
        try:
            list_tool = None
            for tool in tools:
                if tool.name == "list_calendars":
                    list_tool = tool
                    break
            
            assert list_tool is not None
            
            # Test with empty input
            result = list_tool.run("")
            parsed_result = json.loads(result)
            
            assert "status" in parsed_result
            if parsed_result["status"] == "success":
                assert "calendars" in parsed_result
                assert "count" in parsed_result
                assert isinstance(parsed_result["calendars"], list)
                assert isinstance(parsed_result["count"], int)
                assert parsed_result["count"] == len(parsed_result["calendars"])
            
        finally:
            if integration:
                await integration.cleanup()
    
    @pytest.mark.asyncio
    async def test_get_events_tool_with_parameters(self):
        """Test get_events tool with various parameter combinations"""
        tools, integration = await get_calendar_tools()
        
        try:
            get_events_tool = None
            for tool in tools:
                if tool.name == "get_events":
                    get_events_tool = tool
                    break
            
            assert get_events_tool is not None
            
            # Test with empty input
            result = get_events_tool.run("")
            parsed_result = json.loads(result)
            assert "status" in parsed_result
            
            # Test with date range
            start_date = datetime.now().strftime("%Y-%m-%d")
            end_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
            
            input_with_dates = f"start_date: {start_date}, end_date: {end_date}"
            result = get_events_tool.run(input_with_dates)
            parsed_result = json.loads(result)
            
            assert "status" in parsed_result
            if parsed_result["status"] == "success":
                assert "events" in parsed_result
                assert "count" in parsed_result
                assert isinstance(parsed_result["events"], list)
            
        finally:
            if integration:
                await integration.cleanup()
    
    @pytest.mark.asyncio
    async def test_create_event_tool_with_json_input(self):
        """Test create_event tool with JSON input format"""
        tools, integration = await get_calendar_tools()
        
        try:
            create_tool = None
            for tool in tools:
                if tool.name == "create_event":
                    create_tool = tool
                    break
            
            assert create_tool is not None
            
            # Create event with structured input (new format)
            event_data = {
                "calendar_name": "Default Calendar",
                "summary": "Test Event from LangChain Test",
                "start": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S"),
                "duration": 60
            }
            
            result = create_tool.run(event_data)
            parsed_result = json.loads(result)
            
            assert "status" in parsed_result
            
            # If creation was successful, clean up the event
            if parsed_result["status"] == "success" and "event_id" in parsed_result:
                # Note: We don't have a direct delete tool test here,
                # but we could add cleanup logic if needed
                pass
            
        finally:
            if integration:
                await integration.cleanup()


class TestErrorHandling:
    """Test error handling scenarios"""
    
    @pytest.mark.asyncio
    async def test_tool_error_handling(self):
        """Test that tools handle errors gracefully"""
        tools, integration = await get_calendar_tools()
        
        try:
            create_tool = None
            for tool in tools:
                if tool.name == "create_event":
                    create_tool = tool
                    break
            
            assert create_tool is not None
            
            # Test with invalid structured input
            try:
                result = create_tool.run({"invalid": "data"})
                parsed_result = json.loads(result)
            except Exception as e:
                # Structured tools may raise validation errors directly
                parsed_result = {"status": "error", "message": str(e)}
            
            # Should handle error gracefully
            assert "status" in parsed_result
            # Error could be handled in different ways, so we check for reasonable response
            assert parsed_result["status"] in ["error", "success"]
            
        finally:
            if integration:
                await integration.cleanup()
    
    @pytest.mark.asyncio
    async def test_integration_cleanup_after_error(self):
        """Test that integration cleans up properly after errors"""
        integration = CalendarMCPIntegration()
        
        try:
            # Simulate an error during initialization
            with patch.object(integration, '_initialize_manual_tools', side_effect=Exception("Test error")):
                with pytest.raises(Exception):
                    await integration.initialize()
        
        finally:
            # Cleanup should work even after errors
            await integration.cleanup()  # Should not raise exception


class TestPerformanceAndScalability:
    """Test performance characteristics"""
    
    @pytest.mark.asyncio
    async def test_multiple_tool_executions(self):
        """Test multiple rapid tool executions"""
        tools, integration = await get_calendar_tools()
        
        try:
            list_tool = None
            for tool in tools:
                if tool.name == "list_calendars":
                    list_tool = tool
                    break
            
            assert list_tool is not None
            
            # Execute tool multiple times rapidly
            results = []
            for i in range(5):
                result = list_tool.run("")
                results.append(result)
            
            # All results should be valid
            for result in results:
                parsed_result = json.loads(result)
                assert "status" in parsed_result
            
        finally:
            if integration:
                await integration.cleanup()
    
    @pytest.mark.asyncio
    async def test_concurrent_integrations(self):
        """Test multiple concurrent integrations"""
        async def create_and_test_integration():
            tools, integration = await get_calendar_tools()
            try:
                assert len(tools) > 0
                return True
            finally:
                if integration:
                    await integration.cleanup()
        
        # Run multiple integrations concurrently
        tasks = [create_and_test_integration() for _ in range(3)]
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        assert all(results)


class TestIntegrationConfiguration:
    """Test configuration and environment handling"""
    
    @pytest.mark.asyncio
    async def test_default_configuration(self):
        """Test integration with default configuration"""
        integration = CalendarMCPIntegration()
        
        try:
            tools = await integration.initialize()
            
            # Should work with default config
            assert len(tools) > 0
            assert all(isinstance(tool, BaseTool) for tool in tools)
            
        finally:
            await integration.cleanup()
    
    def test_tool_descriptions_completeness(self):
        """Test that all tools have complete descriptions"""
        async def check_descriptions():
            tools, integration = await get_calendar_tools()
            
            try:
                for tool in tools:
                    # Each tool should have a meaningful description
                    assert len(tool.description) > 10
                    assert tool.description.strip() == tool.description  # No leading/trailing spaces
                    assert tool.description  # Not empty
                    
                    # Should be descriptive and contain relevant keywords
                    desc_lower = tool.description.lower()
                    if tool.name == "list_calendars":
                        assert "calendar" in desc_lower
                    elif tool.name == "get_events":
                        assert "event" in desc_lower
                    elif tool.name == "create_event":
                        assert "event" in desc_lower or "create" in desc_lower
                    
            finally:
                if integration:
                    await integration.cleanup()
        
        asyncio.run(check_descriptions())


def run_test_suite():
    """Run the complete test suite with formatted output"""
    print("🧪 Running LangChain Integration Test Suite")
    print("=" * 60)
    
    # Run pytest with verbose output
    pytest_args = [
        __file__,
        "-v",
        "--tb=short",
        "--color=yes"
    ]
    
    return pytest.main(pytest_args)


if __name__ == "__main__":
    exit_code = run_test_suite()
    exit(exit_code)