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
        self.is_terminal: bool = False

    def check_transition_ready(self, context: Dict[str, Any]) -> bool:

        """
        USER DEFINED STATES SHOULD OVERRRIDE THIS FUNCTION 
        """
        raise NotImplementedError
    def run(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        USER DEFINED STATES SHOULD OVERRRIDE THIS FUNCTION
        """
        raise NotImplementedError
