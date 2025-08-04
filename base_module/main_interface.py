
import json


import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from state_module.state_handler import StateHandler
from memory_module.memory import Memory
from model_module.ArkModelNew import ArkModelLink, UserMessage, AIMessage, SystemMessage
from tool_module.tool import Tool

from agent_module.agent import Agent  # Assuming this is your agent.py's Agent class


def run_cli_agent():
    # Initialize components (customize as needed)
    flow = StateHandler(yaml_path="../state_module/state_graph.yaml")  # Adjust path
    memory = Memory(agent_id="cli-agent")
    llm = ArkModelLink(base_url="http://localhost:30000/v1")

    agent = Agent(agent_id="cli-agent", flow=flow, memory=memory, llm=llm)
    ############## INITIALIZATION PROCEDURE
    default_message = SystemMessage(content="You are a helpful assistant names ARK who can use tools, and has memory. Greet the user accordingly")
    agent.context.setdefault("messages", []).append(default_message)

    default_response = agent.call_llm(context=agent.context["messages"])
    ################## INITIALIZATION PROCEDURE
    print("=== Starting CLI Agent (type 'exit' to quit) ===")

    print(default_response.content)

    try:
         agent.step("remove this variable")
            



    except KeyboardInterrupt:
        print("\nInteraction interrupted. Goodbye!")



if __name__ == "__main__":
    run_cli_agent()
