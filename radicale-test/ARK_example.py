import os
import asyncio
import logging
from typing import List, Dict, Any

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import SystemMessage
from langchain_core.tools import BaseTool
from dotenv import load_dotenv

from langchain_mcp_integration import CalendarMCPIntegration, get_calendar_tools

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from model_module.ArkModelOAI import ArkModelLink 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("langchain-mcp-example")

class MCPCalendarAgent:
    def __init__(self, model: str = "tgi", temperature: float = 0):
        load_dotenv()

        self.model = model
        self.temperature = temperature
        self.mcp_integration: CalendarMCPIntegration = None
        self.agent_executor: AgentExecutor = None
        self.tools: List[BaseTool] = []

    async def initialize(self):
        logger.info("Initializing MCP calendar agent...")
        try:
            self.tools, self.mcp_integration = await get_calendar_tools()
            logger.info(f"Loaded {len(self.tools)} MCP tools: {[tool.name for tool in self.tools]}")

            system_prompt = self._create_system_prompt()
            prompt = ChatPromptTemplate.from_messages([
                SystemMessage(content=system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])

            llm = ArkModelLink(
                model_name=self.model,
                base_url="http://localhost:8080/v1",
                temperature=self.temperature,
                max_tokens=4000
            ).bind_tools(self.tools)

            agent = create_openai_functions_agent(
                llm=llm,
                prompt=prompt,
                tools=self.tools
            )

            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                verbose=True,
                max_iterations=10,
                early_stopping_method="generate"
            )

            logger.info("MCP calendar agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize MCP calendar agent: {e}")
            raise

    def _create_system_prompt(self) -> str:
        tool_descriptions = "\n".join([
            f"- {tool.name}: {tool.description}" for tool in self.tools
        ])
        return (
            f"You are a helpful and efficient calendar assistant powered by MCP (Model Context Protocol) tools.\n\n"
            f"You can help users manage their calendar events using the following tools:\n"
            f"{tool_descriptions}\n\n"
            "Guidelines for calendar operations:\n"
            "1. Always confirm details before creating or modifying events\n"
            "2. Use clear, natural language in your responses\n"
            "3. When dates/times are ambiguous, ask for clarification\n"
            "4. Provide helpful summaries after completing operations\n"
            "5. Handle errors gracefully and suggest alternatives\n\n"
            "Date/Time Format Guidelines:\n"
            "- Accept natural language dates (e.g., \"tomorrow\", \"next Friday\")\n"
            "- Convert them to ISO format (YYYY-MM-DDTHH:MM:SS) for tool calls\n"
            "- Default to 1-hour duration if end time not specified\n"
            "- Assume current timezone unless specified\n\n"
            "Calendar Selection:\n"
            "- If no calendar is specified, list available calendars first\n"
            "- Ask user to choose if multiple calendars are available\n"
            "- Remember user preferences within the conversation\n\n"
            "Error Handling:\n"
            "- If a tool operation fails, explain what went wrong\n"
            "- Suggest corrections or alternatives\n"
            "- Never expose technical error details to users\n\n"
            "Example Interactions:\n"
            "- \"What meetings do I have tomorrow?\"\n"
            "- \"Schedule a meeting with John at 2pm\"\n"
            "- \"Cancel my 3pm meeting\"\n"
            "- \"Move my morning meeting to afternoon\""
        )

    async def run_operation(self, operation: str, chat_history: List[Dict[str, str]] = None) -> str:
        if not self.agent_executor:
            await self.initialize()
        if chat_history is None:
            chat_history = []
        try:
            logger.info(f"Processing operation: {operation}")
            result = await self.agent_executor.ainvoke({
                "input": operation,
                "chat_history": chat_history
            })
            response = result["output"]
            logger.info("Operation completed successfully")
            return response
        except Exception as e:
            error_msg = f"Error performing calendar operation: {str(e)}"
            logger.error(error_msg)
            return error_msg

    async def run_interactive_session(self):
        if not self.agent_executor:
            await self.initialize()

        print("\n🗓️  Welcome to the MCP Calendar Assistant!")
        print("Type your calendar requests in natural language.")
        print("Examples: 'What meetings do I have today?', 'Schedule a meeting with John tomorrow at 2pm'")
        print("Type 'quit', 'exit', or 'bye' to end the session.\n")

        chat_history = []

        while True:
            try:
                user_input = input("You: ").strip()
                if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                    print("👋 Goodbye! Have a great day!")
                    break
                if not user_input:
                    continue

                print("🤔 Processing your request...")
                response = await self.run_operation(user_input, chat_history)

                print(f"Assistant: {response}\n")

                chat_history.append({"role": "human", "content": user_input})
                chat_history.append({"role": "assistant", "content": response})
                if len(chat_history) > 10:
                    chat_history = chat_history[-10:]

            except KeyboardInterrupt:
                print("\n👋 Session interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                print("Please try again or type 'quit' to exit.\n")

    async def cleanup(self):
        if self.mcp_integration:
            await self.mcp_integration.cleanup()
            logger.info("MCP integration cleaned up")

    def get_integration_info(self) -> Dict[str, Any]:
        if self.mcp_integration:
            return self.mcp_integration.get_integration_info()
        return {"status": "not_initialized"}


EXAMPLE_OPERATIONS = [
    "What calendars do I have access to?",
    "List my events for today",
    "Add a meeting with John tomorrow at 2pm for 1 hour in my work calendar",
    "Show me all events in my calendar for the next 7 days",
    "Create a dentist appointment next Friday at 10am"
]

async def run_examples():
    print("🚀 Running MCP Calendar Agent Examples\n")

    agent = MCPCalendarAgent()

    try:
        await agent.initialize()
        info = agent.get_integration_info()
        print("📋 Integration Info:")
        print(f"   Method: {info.get('integration_method', 'unknown')}")
        print(f"   Tools: {info.get('tool_count', 0)} loaded")

        for i, operation in enumerate(EXAMPLE_OPERATIONS, 1):
            print(f"📝 Example {i}: {operation}")
            print("🤔 Processing...")
            try:
                result = await agent.run_operation(operation)
                print(f"✅ Result: {result}\n")
                await asyncio.sleep(1)
            except Exception as e:
                print(f"❌ Error: {e}\n")

        print("✨ All examples completed!")

    except Exception as e:
        print(f"❌ Failed to run examples: {e}")
    finally:
        await agent.cleanup()

async def main():
    print("🗓️  MCP Calendar Agent")
    print("====================")
    print("Choose a mode:")
    print("1. Run interactive session")
    print("2. Run predefined examples")
    print("3. Quick test")

    try:
        choice = input("\nEnter your choice (1, 2, or 3): ").strip()

        if choice == "1":
            agent = MCPCalendarAgent()
            try:
                await agent.run_interactive_session()
            finally:
                await agent.cleanup()

        elif choice == "2":
            await run_examples()

        elif choice == "3":
            print("\n🧪 Running quick test...")
            agent = MCPCalendarAgent()
            try:
                await agent.initialize()
                result = await agent.run_operation("List my available calendars")
                print(f"✅ Quick test result: {result}")
            finally:
                await agent.cleanup()

        else:
            print("❌ Invalid choice. Please run the script again.")

    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())

