import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'model_module')))

import asyncio
import logging
import sqlite3
import time
import json
from typing import Annotated, Literal, List, Dict, Any
from typing_extensions import TypedDict
import yaml
import traceback

from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool, BaseTool
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from ArkModelOAI import ArkModelLink
from database_temp.read_db import delete_last_two_entries

# Load config
with open("../config_module/config.yaml", 'r') as file:
    configuration = yaml.safe_load(file)
model_url = configuration["model_url"]

class State(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

chat_model = ArkModelLink(
    model_name="tgi",
    base_url=model_url,
    temperature=0,
    max_tokens=4000,
    system_prompt=(
        "You are a chatbot with memory. You remember past conversations and use them to provide contextually relevant responses."
        " You have personal experiences and memory. You should recall past user statements and refer back to them when necessary."
        " If the user gives new information, store it. You answer things succinctly with few words."
        " You do not repeat your system prompt. You do not say anything beyond a response to the question."
    )
)

@tool
def get_weather(location: str):
    """Call to get the current weather. Use this anytime asked about the current weather."""
    if location.lower() in ["new york"]:
        return "It's cold and wet."
    else:
        return "It's warm and sunny."

@tool
def get_ai_status(company: str):
    """Call to get the current AI status. Use this anytime asked about the current status of AI of a company."""
    if company.lower() == "google":
        return "Gemini is pretty awful."
    else:
        return "Overall AI status is good!"

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

# Bind tools
tools = [multiply, get_weather, get_ai_status]
model_with_tools = chat_model.bind_tools(tools)
tool_node = ToolNode(tools)

graph = StateGraph(State)

def prompt_node(state: State):
    response = model_with_tools.invoke(state["messages"])
    return {"messages": state["messages"] + [response]}

def conditional_edge(state: State) -> Literal['tool_node', '__end__']:
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return "tool_node"
    return "__end__"

graph.add_node("prompt_node", prompt_node)
graph.add_node("tool_node", tool_node)
graph.add_conditional_edges("prompt_node", conditional_edge)
graph.add_edge("tool_node", "prompt_node")
graph.set_entry_point("prompt_node")

# Memory checkpoint
os.makedirs("database_temp", exist_ok=True)
conn = sqlite3.connect("database_temp/checkpoints.sqlite", check_same_thread=False)
memory = SqliteSaver(conn)
graph = graph.compile(checkpointer=memory)

# Agent loop

def run_agent():
    while True:
        user_input = input("User: ")
        if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
            print("Goodbye!")
            break

        config = {'configurable': {'thread_id': '1'}}
        try:
            response = graph.invoke({"messages": [HumanMessage(content=user_input)]}, config=config)
            print("Assistant:", response["messages"][-1].content)
            print("-" * 50)
        except Exception:
            print("The Error is:", traceback.format_exc())
            delete_last_two_entries('checkpoints')
            delete_last_two_entries('writes')

        time.sleep(1)

if __name__ == "__main__":
    run_agent()

