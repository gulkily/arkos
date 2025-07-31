import yaml


import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from state_module.state import State, AgentState
from typing import Dict, Any


class StateHandler:
    def __init__(self, yaml_path: str):
        with open(yaml_path, "r") as f:
            self.graph = yaml.safe_load(f)

        self.states: Dict[str, State] = {
            name: State(name, config)
            for name, config in self.graph.get("states", {}).items()
        }
        self.initial_state_name: str = self.graph.get("initial")

    def get_initial_state(self) -> State:
        return self.states[self.initial_state_name]

    def get_next_state(self, current_state_name: str, context: Dict[str, Any]) -> State:
        state = self.states[current_state_name]
        for condition, next_state in state.transitions.items():
            if context.get(condition):
                return self.states[next_state]
        return state  # No transition matched; remain in current

