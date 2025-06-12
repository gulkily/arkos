"""
LangChain MCP Integration for Radicale Calendar

This module provides integration between LangChain and MCP (Model Context Protocol)
for calendar operations. It replaces the direct tool adapter approach with a 
standardized MCP-based integration using LangChain's official MCP adapters.

Features:
- Uses LangChain MCP adapters for tool conversion
- Supports multiple MCP transport methods (stdio, HTTP)
- Automatic tool discovery and schema validation
- Async operation support
- Comprehensive error handling
- Configuration-based MCP server management

Usage:
    # Basic usage with default configuration
    integration = CalendarMCPIntegration()
    tools = await integration.initialize()
    
    # Use with LangChain agent
    agent = create_openai_functions_agent(llm, prompt, tools)
    
Dependencies:
    pip install langchain-mcp-adapters mcp
    # OR alternative:
    pip install langchain-mcp-tools
"""

import os
import json
import asyncio
import logging
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path

# LangChain imports
from langchain.tools import Tool
from langchain_core.tools import BaseTool

# Environment configuration
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger("langchain-mcp-integration")

class MCPIntegrationError(Exception):
    """Custom exception for MCP integration operations"""
    pass

class CalendarMCPIntegration:
    """
    LangChain MCP Integration for Radicale Calendar Operations.
    
    This class manages the connection between LangChain and MCP servers,
    providing automatic tool discovery and conversion from MCP tools to
    LangChain-compatible tools.
    """
    
    def __init__(self, mcp_server_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the MCP integration with server configuration.
        
        Args:
            mcp_server_config: Dictionary containing MCP server configuration.
                              If None, uses default configuration.
        """
        load_dotenv()
        
        self.mcp_server_config = mcp_server_config or self._get_default_config()
        self.tools: List[BaseTool] = []
        self.cleanup_fn: Optional[Callable] = None
        self._mcp_client = None
        self._integration_method = None
        
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get default MCP server configuration.
        
        Returns:
            Dictionary containing default server configuration
        """
        # Get the directory where this script is located
        script_dir = Path(__file__).parent
        server_script = script_dir / "mcp_radicale_server.py"
        
        return {
            "radicale-calendar": {
                "command": "python",
                "args": [str(server_script)],
                "transport": "stdio",
                "env": {
                    "RADICALE_URL": os.getenv("RADICALE_URL", "http://localhost:5232"),
                    "RADICALE_USERNAME": os.getenv("RADICALE_USERNAME", ""),
                    "RADICALE_PASSWORD": os.getenv("RADICALE_PASSWORD", "")
                }
            }
        }
    
    async def initialize(self) -> List[BaseTool]:
        """
        Initialize MCP connection and load calendar tools.
        
        Returns:
            List of LangChain-compatible tools converted from MCP server
            
        Raises:
            MCPIntegrationError: If initialization fails
        """
        logger.info("Initializing LangChain MCP integration for calendar operations")
        
        try:
            # Try primary method: langchain-mcp-tools
            tools = await self._initialize_with_mcp_tools()
            if tools:
                self._integration_method = "langchain-mcp-tools"
                self.tools = tools
                logger.info(f"Successfully initialized with langchain-mcp-tools: {len(tools)} tools loaded")
                return tools
                
        except ImportError as e:
            logger.warning(f"langchain-mcp-tools not available: {e}")
        except Exception as e:
            logger.warning(f"Failed to initialize with langchain-mcp-tools: {e}")
        
        try:
            # Fallback method: langchain-mcp-adapters
            tools = await self._initialize_with_adapters()
            if tools:
                self._integration_method = "langchain-mcp-adapters"
                self.tools = tools
                logger.info(f"Successfully initialized with langchain-mcp-adapters: {len(tools)} tools loaded")
                return tools
                
        except ImportError as e:
            logger.error(f"langchain-mcp-adapters not available: {e}")
        except Exception as e:
            logger.error(f"Failed to initialize with langchain-mcp-adapters: {e}")
        
        # If both methods fail, try manual tool creation
        try:
            tools = await self._initialize_manual_tools()
            self._integration_method = "manual"
            self.tools = tools
            logger.info(f"Successfully initialized with manual tools: {len(tools)} tools loaded")
            return tools
            
        except Exception as e:
            logger.error(f"Failed to initialize with manual tools: {e}")
            raise MCPIntegrationError(f"All MCP integration methods failed: {e}")
    
    async def _initialize_with_mcp_tools(self) -> List[BaseTool]:
        """
        Initialize using langchain-mcp-tools package.
        
        Returns:
            List of converted LangChain tools
        """
        try:
            from langchain_mcp_tools import convert_mcp_to_langchain_tools
            
            logger.info("Using langchain-mcp-tools for MCP integration")
            
            # Initialize MCP servers and get tools
            tools, cleanup_fn = await convert_mcp_to_langchain_tools(
                self.mcp_server_config
            )
            
            self.cleanup_fn = cleanup_fn
            
            # Validate tools
            if not tools:
                raise MCPIntegrationError("No tools returned from MCP server")
            
            logger.info(f"Loaded {len(tools)} tools from MCP server using langchain-mcp-tools")
            return tools
            
        except ImportError:
            raise ImportError("langchain-mcp-tools package not installed")
    
    async def _initialize_with_adapters(self) -> List[BaseTool]:
        """
        Initialize using langchain-mcp-adapters package.
        
        Returns:
            List of converted LangChain tools
        """
        try:
            from langchain_mcp_adapters.client import load_mcp_tools
            
            logger.info("Using langchain-mcp-adapters for MCP integration")
            
            # For stdio transport
            server_config = self.mcp_server_config.get("radicale-calendar", {})
            if server_config.get("transport") == "stdio":
                # Start the MCP server as a subprocess
                import subprocess
                
                cmd = [server_config["command"]] + server_config["args"]
                env = os.environ.copy()
                env.update(server_config.get("env", {}))
                
                # Start MCP server process
                self._mcp_process = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=env,
                    text=True
                )
                
                # Load tools using stdio connection
                from langchain_mcp_adapters.client import stdio_client
                
                # Create stdio connection and load tools
                async with stdio_client(self._mcp_process.stdin, self._mcp_process.stdout) as session:
                    tools = await load_mcp_tools(session)
                    
            else:
                # For HTTP transport, connect to running server
                from langchain_mcp_adapters.client import sse_client
                server_url = f"http://localhost:8765/sse"
                
                async with sse_client(server_url) as session:
                    tools = await load_mcp_tools(session)
            
            if not tools:
                raise MCPIntegrationError("No tools returned from MCP server")
            
            logger.info(f"Loaded {len(tools)} tools from MCP server using langchain-mcp-adapters")
            return tools
            
        except ImportError:
            raise ImportError("langchain-mcp-adapters package not installed")
    
    async def _initialize_manual_tools(self) -> List[BaseTool]:
        """
        Fallback: Create tools manually by communicating with MCP server.
        
        Returns:
            List of manually created LangChain tools
        """
        logger.info("Creating manual MCP tools as fallback")
        
        # Import the server class to get tool definitions
        from mcp_radicale_server import MCPRadicaleServer
        
        # Create server instance to get tool information
        server = MCPRadicaleServer()
        
        # Manually create LangChain tools that call the MCP server
        tools = []
        
        def list_calendars_sync(input_str: str = "") -> str:
            """List all available calendars"""
            try:
                if not server.calendar_manager.calendars:
                    server.calendar_manager.connect()
                calendar_names = [cal.name for cal in server.calendar_manager.calendars]
                return json.dumps({
                    "status": "success", 
                    "calendars": calendar_names,
                    "count": len(calendar_names)
                })
            except Exception as e:
                return json.dumps({"status": "error", "message": str(e)})
        
        tools.append(Tool(
            name="list_calendars",
            func=list_calendars_sync,
            description="List all available calendars in the Radicale server"
        ))
        
        def get_events_sync(input_str: str) -> str:
            """Get events from calendar with parameter parsing"""
            try:
                from datetime import datetime
                import re
                
                # Parse input parameters from string
                calendar_match = re.search(r'calendar[_\s]*name[:\s]*["\']?([^"\']+)["\']?', input_str, re.IGNORECASE)
                start_match = re.search(r'start[_\s]*date[:\s]*["\']?([^"\']+)["\']?', input_str, re.IGNORECASE)
                end_match = re.search(r'end[_\s]*date[:\s]*["\']?([^"\']+)["\']?', input_str, re.IGNORECASE)
                
                calendar_name = calendar_match.group(1) if calendar_match else None
                start_date = start_match.group(1) if start_match else None
                end_date = end_match.group(1) if end_match else None
                
                start_dt = None
                end_dt = None
                
                if start_date:
                    start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                if end_date:
                    end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                
                events = server.calendar_manager.get_events(calendar_name, start_dt, end_dt)
                
                used_calendar = calendar_name
                if not used_calendar and server.calendar_manager.calendars:
                    used_calendar = server.calendar_manager.calendars[0].name
                
                return json.dumps({
                    "status": "success",
                    "calendar": used_calendar,
                    "events": events,
                    "count": len(events)
                })
            except Exception as e:
                return json.dumps({"status": "error", "message": str(e)})
        
        tools.append(Tool(
            name="get_events",
            func=get_events_sync,
            description="Get events from a calendar within a date range. Provide parameters as text like 'calendar_name: Work, start_date: 2023-06-01'"
        ))
        
        def create_event_sync(input_str: str) -> str:
            """Create a new event with parameter parsing"""
            try:
                # Parse input parameters from string - this is a simplified parser
                import re
                import json as json_module
                
                # Try to parse as JSON first
                try:
                    params = json_module.loads(input_str)
                    calendar_name = params.get("calendar_name", "")
                    summary = params.get("summary", "")
                    start = params.get("start", "")
                    kwargs = {k: v for k, v in params.items() if k not in ["calendar_name", "summary", "start"]}
                except:
                    # Fallback to regex parsing
                    calendar_match = re.search(r'calendar[_\s]*name[:\s]*["\']?([^"\']+)["\']?', input_str, re.IGNORECASE)
                    summary_match = re.search(r'summary[:\s]*["\']?([^"\']+)["\']?', input_str, re.IGNORECASE)
                    start_match = re.search(r'start[:\s]*["\']?([^"\']+)["\']?', input_str, re.IGNORECASE)
                    
                    calendar_name = calendar_match.group(1) if calendar_match else ""
                    summary = summary_match.group(1) if summary_match else ""
                    start = start_match.group(1) if start_match else ""
                    kwargs = {}
                
                # Create the event
                event_data = {
                    "summary": summary,
                    "start": start
                }
                event_data.update(kwargs)
                
                event_id = server.calendar_manager.add_event(calendar_name, event_data)
                
                return json.dumps({
                    "status": "success",
                    "message": f"Event '{summary}' created successfully",
                    "event_id": event_id,
                    "calendar": calendar_name
                })
            except Exception as e:
                return json.dumps({"status": "error", "message": str(e)})
        
        tools.append(Tool(
            name="create_event",
            func=create_event_sync,
            description="Create a new calendar event. Provide parameters as JSON or text like '{\"calendar_name\": \"Work\", \"summary\": \"Meeting\", \"start\": \"2023-06-01T10:00:00\"}'"
        ))
        
        logger.info(f"Created {len(tools)} manual MCP tools")
        return tools
    
    async def cleanup(self):
        """
        Clean up MCP connections and resources.
        """
        logger.info("Cleaning up MCP integration resources")
        
        try:
            if self.cleanup_fn:
                await self.cleanup_fn()
                logger.info("MCP cleanup function called successfully")
                
            if hasattr(self, '_mcp_process') and self._mcp_process:
                self._mcp_process.terminate()
                self._mcp_process.wait()
                logger.info("MCP server process terminated")
                
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")
    
    def get_tool_names(self) -> List[str]:
        """
        Get names of all loaded tools.
        
        Returns:
            List of tool names
        """
        return [tool.name for tool in self.tools]
    
    def get_tool_descriptions(self) -> Dict[str, str]:
        """
        Get descriptions of all loaded tools.
        
        Returns:
            Dictionary mapping tool names to descriptions
        """
        return {tool.name: tool.description for tool in self.tools}
    
    def get_integration_info(self) -> Dict[str, Any]:
        """
        Get information about the current integration setup.
        
        Returns:
            Dictionary containing integration details
        """
        return {
            "integration_method": self._integration_method,
            "server_config": self.mcp_server_config,
            "tool_count": len(self.tools),
            "tool_names": self.get_tool_names()
        }

# Convenience function for easy usage
async def get_calendar_tools(config: Optional[Dict[str, Any]] = None) -> tuple[List[BaseTool], CalendarMCPIntegration]:
    """
    Convenience function to quickly get calendar tools and integration instance.
    
    Args:
        config: Optional MCP server configuration
        
    Returns:
        Tuple of (tools_list, integration_instance)
        
    Example:
        tools, integration = await get_calendar_tools()
        
        # Use tools with LangChain
        agent = create_openai_functions_agent(llm, prompt, tools)
        
        # Clean up when done
        await integration.cleanup()
    """
    integration = CalendarMCPIntegration(config)
    tools = await integration.initialize()
    return tools, integration

# Example usage
if __name__ == "__main__":
    async def main():
        """Example usage of the MCP integration"""
        integration = CalendarMCPIntegration()
        
        try:
            # Initialize and get tools
            tools = await integration.initialize()
            
            print(f"Loaded {len(tools)} calendar tools:")
            for tool in tools:
                print(f"  - {tool.name}: {tool.description}")
            
            # Test a tool
            if tools:
                first_tool = tools[0]
                print(f"\nTesting tool: {first_tool.name}")
                result = first_tool.run("")
                print(f"Result: {result}")
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await integration.cleanup()
    
    asyncio.run(main())