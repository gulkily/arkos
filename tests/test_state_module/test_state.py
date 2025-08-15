import pytest
from unittest.mock import Mock, patch
from state_module.state import State, AgentState


class TestState:
    """Tests for State base class."""

    def test_state_initialization_with_valid_config(self):
        """Test State initialization with valid configuration."""
        config = {
            "type": "test_state",
            "transition": {"next": "other_state"},
            "is_terminal": False
        }
        
        state = State("test_state", config)
        
        assert state.name == "test_state"
        assert state.config == config
        assert state.transition == {"next": "other_state"}
        assert state.is_terminal == False

    def test_state_initialization_with_missing_transition_config(self):
        """Test State initialization with missing transition configuration."""
        config = {
            "type": "test_state",
            "is_terminal": False
        }
        
        state = State("test_state", config)
        
        assert state.name == "test_state"
        assert state.config == config
        assert state.transition == {}  # Should default to empty dict
        assert state.is_terminal == False

    def test_state_initialization_with_missing_is_terminal(self):
        """Test State initialization with missing is_terminal property."""
        config = {
            "type": "test_state",
            "transition": {"next": "other_state"}
        }
        
        state = State("test_state", config)
        
        assert state.name == "test_state"
        assert state.config == config
        assert state.transition == {"next": "other_state"}
        assert state.is_terminal == False  # Should default to False

    def test_state_initialization_with_terminal_flag(self):
        """Test State initialization with terminal flag set to True."""
        config = {
            "type": "test_state",
            "transition": {},
            "is_terminal": True
        }
        
        state = State("test_state", config)
        
        assert state.name == "test_state"
        assert state.is_terminal == True
        assert state.transition == {}

    def test_not_implemented_error_for_run_method(self):
        """Test that base State class run method raises NotImplementedError."""
        config = {"type": "test_state"}
        state = State("test_state", config)
        
        with pytest.raises(NotImplementedError):
            state.run([], Mock())

    def test_not_implemented_error_for_check_transition_ready_method(self):
        """Test that base State class check_transition_ready method raises NotImplementedError."""
        config = {"type": "test_state"}
        state = State("test_state", config)
        
        with pytest.raises(NotImplementedError):
            state.check_transition_ready()

    def test_state_config_access(self):
        """Test that state configuration is accessible."""
        config = {
            "type": "test_state",
            "custom_property": "test_value",
            "nested": {"key": "value"}
        }
        
        state = State("test_state", config)
        
        assert state.config["custom_property"] == "test_value"
        assert state.config["nested"]["key"] == "value"
        assert state.config["type"] == "test_state"

    def test_transition_property_access(self):
        """Test that transition property is correctly extracted from config."""
        config = {
            "type": "test_state",
            "transition": {
                "success": "success_state",
                "failure": "failure_state",
                "default": "default_state"
            }
        }
        
        state = State("test_state", config)
        
        assert "success" in state.transition
        assert "failure" in state.transition
        assert "default" in state.transition
        assert state.transition["success"] == "success_state"
        assert state.transition["failure"] == "failure_state"
        assert state.transition["default"] == "default_state"

    def test_state_name_immutability(self):
        """Test that state name is properly set and accessible."""
        config = {"type": "test_state"}
        state = State("immutable_name", config)
        
        assert state.name == "immutable_name"
        
        # Name should be read-only (though Python doesn't enforce this strictly)
        # This is more of a documentation test
        original_name = state.name
        state.name = "changed_name"  # This will work in Python
        assert state.name == "changed_name"  # But we document that it shouldn't be changed


class TestAgentState:
    """Tests for AgentState enum."""

    def test_agent_state_enum_values(self):
        """Test that AgentState enum has expected values."""
        # Check that the enum exists and has expected values
        assert hasattr(AgentState, 'PROCESSING')
        assert hasattr(AgentState, 'WAITING_FOR_INPUT')
        assert hasattr(AgentState, 'GENERATING_RESPONSE')
        assert hasattr(AgentState, 'COMPLETE')

    def test_agent_state_enum_value_types(self):
        """Test that AgentState enum values are of correct type."""
        # Enum values should be string-like or have specific values
        assert isinstance(AgentState.PROCESSING.value, (str, int))
        assert isinstance(AgentState.WAITING_FOR_INPUT.value, (str, int))
        assert isinstance(AgentState.GENERATING_RESPONSE.value, (str, int))
        assert isinstance(AgentState.COMPLETE.value, (str, int))

    def test_agent_state_enum_uniqueness(self):
        """Test that AgentState enum values are unique."""
        values = [
            AgentState.PROCESSING.value,
            AgentState.WAITING_FOR_INPUT.value,
            AgentState.GENERATING_RESPONSE.value,
            AgentState.COMPLETE.value
        ]
        
        assert len(values) == len(set(values)), "AgentState enum values should be unique"

    def test_agent_state_enum_iteration(self):
        """Test that AgentState enum can be iterated."""
        states = list(AgentState)
        
        assert len(states) >= 4  # At least the 4 states we expect
        assert AgentState.PROCESSING in states
        assert AgentState.WAITING_FOR_INPUT in states
        assert AgentState.GENERATING_RESPONSE in states
        assert AgentState.COMPLETE in states

    def test_agent_state_enum_comparison(self):
        """Test that AgentState enum values can be compared."""
        state1 = AgentState.PROCESSING
        state2 = AgentState.PROCESSING
        state3 = AgentState.WAITING_FOR_INPUT
        
        assert state1 == state2
        assert state1 != state3
        assert state2 != state3