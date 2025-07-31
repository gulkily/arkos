from enum import Enum
from typing import Dict, Any, Optional


class AgentState(Enum):
    """Central registry of all possible agent states."""
    GREET_USER = "greet_user"
    FETCH_PRODUCT = "fetch_product"
    SUMMARIZE_RESULT = "summarize_result"
    DONE = "done"


class State:
    def __init__(self, name: str, metadata: Dict[str, Any]):
        self.name = name
        self.intent: Optional[str] = metadata.get("intent")
        self.tool: Optional[str] = metadata.get("tool", {}).get("name")
        self.tool_inputs: Optional[list] = metadata.get("tool", {}).get("inputs", [])
        self.wait_for_tool_result: bool = metadata.get("wait_for_tool_result", False)
        self.is_terminal: bool = metadata.get("is_terminal", False)
        self.response: Optional[str] = metadata.get("response")
        self.transitions: Dict[str, str] = metadata.get("transitions", {})

    def check_transition_ready(self, context: Dict[str, Any]) -> bool:
        if self.wait_for_tool_result and not context.get("tool_result_ready"):
            return False
        return True

    def run(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if self.tool:
            tool_input = {k: context.get(k) for k in self.tool_inputs}
            return {
                "intent": self.intent,
                "tool": self.tool,
                "tool_input": tool_input,
                "tool_result_ready": False
            }
        elif self.response:
            return {"message": self.response}
        return {}

