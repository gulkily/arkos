import yaml


import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from state_module.state_registry import STATE_REGISTRY, auto_register_states

from state_module.state import State
from typing import Dict, Any


auto_register_states("state_module")


class StateHandler:
    def __init__(self, yaml_path: str):
        with open(yaml_path, "r") as f:
            self.graph = yaml.safe_load(f)

        self.states = {}
        for name, config in self.graph.get("states", {}).items():
            state_type = config.get("type")
            if state_type not in STATE_REGISTRY:
                raise ValueError(f"Unknown state type: {state_type}")
            state_class = STATE_REGISTRY[state_type]
            self.states[name] = state_class(name, config)

        self.initial_state_name = self.graph["initial"]

    def get_initial_state(self) -> State:
        return self.states[self.initial_state_name]

    def get_next_state(self, current_state_name: str, context: Dict[str, Any]) -> State:
        state = self.states[current_state_name]
        
        # Handle simple 'next' transition
        if "next" in state.transition:
            next_state_name = state.transition["next"]
            return self.states[next_state_name]
        
        # Handle conditional transitions (future enhancement)
        # For now, fall back to first available transition
        if state.transition:
            next_state_name = list(state.transition.values())[0]
            return self.states[next_state_name]
        
        # If no transitions defined, return current state (terminal state)
        return state
