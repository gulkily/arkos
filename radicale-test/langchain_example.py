"""
Example usage of MCP Radicale Bridge with LangChain

This script demonstrates how to:
1. Connect to the MCP Radicale Bridge server
2. Create a LangChain agent with calendar tools
3. Perform basic calendar operations
4. Handle errors and responses
"""

import os
import json
import asyncio
import websockets
from datetime import datetime
from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import SystemMessage
from langchain.tools import Tool

# Load environment variables from .env file
load_dotenv()

# MCP Server settings
MCP_HOST = "localhost"
MCP_PORT = 8765

class MCPCalendarTool:
    def __init__(self, host=MCP_HOST, port=MCP_PORT):
        self.host = host
        self.port = port
        self.ws = None

    async def connect(self):
        """Connect to the MCP server"""
        try:
            self.ws = await websockets.connect(f"ws://{self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Failed to connect to MCP server: {e}")
            return False

    async def send_request(self, request_type, **kwargs):
        """Send a request to the MCP server"""
        if not self.ws:
            if not await self.connect():
                return {"status": "error", "message": "Not connected to MCP server"}

        try:
            request = {
                "type": request_type,
                **kwargs
            }
            await self.ws.send(json.dumps(request))
            response = await self.ws.recv()
            return json.loads(response)
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def list_calendars(self):
        """List available calendars"""
        return await self.send_request("query")

    async def get_events(self, calendar=None, start_date=None, end_date=None):
        """Get events from a calendar"""
        return await self.send_request(
            "query",
            calendar=calendar,
            start_date=start_date.isoformat() if start_date else None,
            end_date=end_date.isoformat() if end_date else None
        )

    async def create_event(self, calendar, event_data):
        """Create a new event"""
        return await self.send_request(
            "create",
            calendar=calendar,
            event=event_data
        )

    async def update_event(self, calendar, event_id, event_data):
        """Update an existing event"""
        return await self.send_request(
            "update",
            calendar=calendar,
            event_id=event_id,
            event=event_data
        )

    async def delete_event(self, calendar, event_id):
        """Delete an event"""
        return await self.send_request(
            "delete",
            calendar=calendar,
            event_id=event_id
        )

# Initialize the MCP calendar tool
mcp_tool = MCPCalendarTool()

# Create LangChain tools from MCP tool methods
tools = [
    Tool(
        name="list_calendars",
        func=lambda _: asyncio.run(mcp_tool.list_calendars()),
        description="List all available calendars"
    ),
    Tool(
        name="get_events",
        func=lambda calendar, start_date=None, end_date=None: asyncio.run(
            mcp_tool.get_events(
                calendar,
                datetime.fromisoformat(start_date) if start_date else None,
                datetime.fromisoformat(end_date) if end_date else None
            )
        ),
        description="Get events from a calendar within a date range"
    ),
    Tool(
        name="create_event",
        func=lambda calendar, event_data: asyncio.run(
            mcp_tool.create_event(calendar, json.loads(event_data))
        ),
        description="Create a new calendar event"
    ),
    Tool(
        name="update_event",
        func=lambda calendar, event_id, event_data: asyncio.run(
            mcp_tool.update_event(calendar, event_id, json.loads(event_data))
        ),
        description="Update an existing calendar event"
    ),
    Tool(
        name="delete_event",
        func=lambda calendar, event_id: asyncio.run(
            mcp_tool.delete_event(calendar, event_id)
        ),
        description="Delete a calendar event"
    )
]

# Create the prompt template
prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content=(
        "You are a helpful calendar assistant. "
        "You can help users manage their calendar events. "
        "Always confirm the action before executing it. "
        "If you're unsure about any parameters, ask for clarification."
    )),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# Initialize the LLM with API key from .env
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
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True
)

def run_calendar_operation(operation: str) -> str:
    """
    Run a calendar operation using the agent
    
    Args:
        operation: The operation to perform (e.g., "List my events for today")
    
    Returns:
        The result of the operation
    """
    try:
        # Initialize empty chat history for each operation
        chat_history = []
        result = agent_executor.invoke({
            "input": operation,
            "chat_history": chat_history
        })
        return result["output"]
    except Exception as e:
        return f"Error performing operation: {str(e)}"

# Example usage
if __name__ == "__main__":
    # Example 1: List all calendars
    print("\nExample 1: Listing all calendars")
    print(run_calendar_operation("What calendars do I have access to?"))
    
    # Example 2: Add an event
    print("\nExample 2: Adding an event")
    print(run_calendar_operation(
        "Add a meeting with John tomorrow at 2pm for 1 hour in my work calendar"
    ))
    
    # Example 3: List events
    print("\nExample 3: Listing events")
    print(run_calendar_operation(
        "Show me all events in my work calendar for tomorrow"
    ))
    
    # Example 4: Update an event
    print("\nExample 4: Updating an event")
    print(run_calendar_operation(
        "Change the meeting with John to 3pm tomorrow"
    ))
    
    # Example 5: Delete an event
    print("\nExample 5: Deleting an event")
    print(run_calendar_operation(
        "Cancel the meeting with John tomorrow"
    ))

# Notes:
# 1. OpenAI API key is read from the .env file:
#    OPENAI_API_KEY=your-api-key
#
# 2. The MCP Radicale Bridge server must be running on localhost:8765
#
# 3. The agent will handle date parsing and formatting automatically
#
# 4. Error handling is included in the run_calendar_operation function
#
# 5. The agent will ask for clarification if any parameters are missing or unclear 