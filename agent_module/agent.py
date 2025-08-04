# agent.py

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from typing import Any, Dict

from state_module.state_handler import StateHandler
from state_module.state import State, AgentState
from model_module.ArkModelNew import ArkModelLink, UserMessage, AIMessage, SystemMessage
from tool_module.tool import Tool
from memory_module.memory import Memory


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))



multiply_tool =  {"url":  "https://localhost:4040", "parameters": None}
add_tool = {"url": "https://localhost:3030", "parameters": None}
tool_registry = {"keyA": multiply_tool, "embedding_b": add_tool}
# TODO: add tool registry, navegable by directory 

class Agent:
    def __init__(self, agent_id: str, flow: StateHandler, memory: Memory, llm: ArkModelLink):
        self.agent_id = agent_id
        self.flow = flow
        self.memory = memory
        self.llm = llm
        self.current_state = self.flow.get_initial_state()
        self.context: Dict[str, Any] = {}



        self.tools = []
        self.tool_names = []
    def bind_tool(tool):

        self.tool.append(tool) 
    
    def find_downloaded_tool(embedding):
        tool = Tool.pull_tool_from_registry(embedding)
        tool_name = tool.tool
        self.bind_tool(tool)
        self.tool_names.append(tool_name)
    
    def call_llm(self, input=None,context=None, json_schema=None):
        """
        Agent's interface with chat model 
        input: messages (list), json_schema (json)

        output: AI Message
        """

        chat_model = self.llm 
        if context:

            llm_response = chat_model.generate_response(context, json_schema)


        else:
            messages = [SystemMessage(content=input)]
            llm_response = chat_model.generate_response(messages, json_schema)


        return AIMessage(content=llm_response)

    def step(self, input: str):

        # get first state from states
        if not self.current_state:
            self.current_state = flow.get_initial_state()
    


        while not self.current_state.is_terminal:

            # asumption run will always return a valid Messsage
            updates = self.current_state.run(self.context["messages"], self)
            if updates:
                self.context["messages"].append(updates)
            
            if self.current_state.check_transition_ready(self.context["messages"]):
                self.current_state = self.flow.get_next_state(self.current_state.name, self.context)

            else:
                raise ValueError("State Loop Failed, No next State agent.py")

        return 



