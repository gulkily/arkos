# agent.py

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from typing import Any, Dict

from state_module.state_handler import StateHandler
from state_module.state import State, AgentState
from model_module.ArkModelNew import ArkModelLink, UserMessage, AIMessage
from tool_module.tool import Tool, pull_tool_from_registry
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
        tool = pull_tool_from_registry(embedding)
        tool_name = tool.tool
        self.bind_tool(tool)
        self.tool_names.append(tool_name)
            

    def step(self, user_input: str):
        self.context["user_input"] = user_input
        history = [UserMessage(content=user_input)]

        #  Use LLM to infer intent if not already in a tool or final state
        if not self.current_state.tool and not self.current_state.is_terminal:
            intent_response = self.llm.make_llm_call(
                messages=history + [AIMessage(content="What tool does the user want to use?")],
                json_schema={
                    "type": "json_schema",
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "intent": 
                            
                                {"type": "string",
                                "enum": self.tool_names
                                 }
                        },
                        "required": ["intent"]
                    }
                }
            )
            self.context["intent"] = intent_response["schema_result"]["content"]["intent"] 

        #  If a tool is defined, fill inputs with schema
        if self.current_state.tool:
            schema = {
                "type": "json_schema",
                "json_schema": {
                    "type": "object",
                    "properties": {
                        k: {"type": "string"} for k in self.current_state.tool_inputs
                    },
                    "required": self.current_state.tool_inputs
                }
            }
            fill_response = self.llm.make_llm_call(history, json_schema=schema)
            self.context["tool_input"] = fill_response["schema_result"]["content"]
            self.context["tool_result_ready"] = False
            return self.context  # Ready to call external tool

        #  Run state logic (static or tool)
        result = self.current_state.run(self.context)
        self.context.update(result or {})

        #  Use LLM for response if no static response provided
        if not self.current_state.response and not self.current_state.tool and not self.current_state.is_terminal:
            llm_resp = self.llm.make_llm_call(history, json_schema=None)
            self.context["message"] = llm_resp["message"]["content"]

        self.memory.push_state({
            "state": self.current_state.name,
            "intent": self.context.get("intent"),
            "tool": self.current_state.tool,
            "scratchpad": self.context.get("tool_input")
        })

        #  Advance state
        self.current_state = self.flow.get_next_state(self.current_state.name, self.context)

    def receive_result(self, result: Dict[str, Any]):
        self.context["tool_result"] = result
        self.context["tool_result_ready"] = True
        self.step(user_input="")  # Continue with same flow

    def serialize(self):
        return {
            "agent_id": self.agent_id,
            "current_state": self.current_state.name,
            "context": self.context,
            "memory": self.memory.serialize() if hasattr(self.memory, "serialize") else {}
        }

