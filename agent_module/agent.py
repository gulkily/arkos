# agent.py
from typing import Any, Dict
from state_handler import StateHandler
from ark_model_link import ArkModelLink, UserMessage, AIMessage
from tool_module.tool import Tool

class Agent:
    def __init__(self, agent_id: str, flow: StateHandler, memory: Dict[str, Any]):
        self.agent_id = agent_id
        self.flow = flow
        self.memory = memory
        self.current_state = "start"
        self.llm = ArkModelLink()
        self.tool_results = {}

    def run(self):
        """Begin execution loop."""
        while True:
            state_obj = self.flow.get_next_state(self.current_state, self.memory)
            if not state_obj:
                print("End of flow.")
                break
            result = state_obj.run(self)
            self.current_state = state_obj.name
            self.memory["last_result"] = result

    def step(self, user_input: str):
        """Single step of interaction."""
        self.memory["user_input"] = user_input
        return self.run()

    def receive_result(self, tool_result):
        """Store tool output."""
        self.tool_results[self.current_state] = tool_result
        self.memory["tool_result"] = tool_result

    def serialize(self):
        """Dump agent state."""
        return {
            "agent_id": self.agent_id,
            "current_state": self.current_state,
            "memory": self.memory,
            "tool_results": self.tool_results
        }

