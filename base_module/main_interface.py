
import json


import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from state_module.state_handler import StateHandler
from memory_module.memory import Memory
from model_module.ArkModelNew import ArkModelLink, UserMessage, AIMessage
from tool_module.tool import Tool

from agent_module.agent import Agent  # Assuming this is your agent.py's Agent class


def run_cli_agent():
    # Initialize components (customize as needed)
    flow = StateHandler(yaml_path="../state_module/state_graph.yaml")  # Adjust path
    memory = Memory(agent_id="cli-agent")
    llm = ArkModelLink(base_url="http://localhost:8080/v1")

    agent = Agent(agent_id="cli-agent", flow=flow, memory=memory, llm=llm)

    print("=== Starting CLI Agent (type 'exit' to quit) ===")

    try:
        while True:
            user_input = input("You: ")
            if user_input.strip().lower() == "exit":
                print("Exiting agent interaction.")
                break

            context = agent.step(user_input)

            # If the agent wants tool input
            if context.get("tool_input") and not context.get("tool_result_ready", True):
                tool_input = context["tool_input"]
                print(f"Agent needs tool input parameters: {list(tool_input.keys())}")
                # Turn-by-turn filling of missing parameters
                filled_params = {}
                for param in tool_input:
                    val = input(f"Provide value for '{param}': ")
                    filled_params[param] = val

                print("Sending filled tool input back to agent...")
                agent.receive_result(filled_params)
                # After receiving tool result, agent runs step again internally
                # You can print updated message/state below

            # Show the agent's message or current state info
            if "message" in agent.context:
                print(f"Agent: {agent.context['message']}")
            else:
                print(f"Agent is in state: {agent.current_state.name}")

    except KeyboardInterrupt:
        print("\nInteraction interrupted. Goodbye!")



if __name__ == "__main__":
    run_cli_agent()
