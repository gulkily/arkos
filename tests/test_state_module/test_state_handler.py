import pytest
from unittest.mock import Mock, patch, mock_open
from state_module.state_handler import StateHandler
from state_module.state_registry import STATE_REGISTRY
import yaml


class TestStateHandler:
    """Tests for StateHandler class."""

    def test_init_with_valid_yaml(self, test_yaml_config_file):
        """Test StateHandler initialization with valid YAML configuration."""
        handler = StateHandler(test_yaml_config_file)
        
        assert handler.initial_state_name == "test_user"
        assert "test_user" in handler.states
        assert "test_agent" in handler.states
        assert len(handler.states) == 2

    def test_init_with_invalid_yaml_file(self):
        """Test StateHandler initialization with non-existent YAML file."""
        with pytest.raises(FileNotFoundError):
            StateHandler("nonexistent_file.yaml")

    def test_init_with_invalid_state_type(self, invalid_yaml_config_file):
        """Test StateHandler initialization with invalid state type."""
        with pytest.raises(ValueError, match="Unknown state type: invalid_type"):
            StateHandler(invalid_yaml_config_file)

    @patch("builtins.open", mock_open(read_data="invalid: yaml: content:"))
    @patch("yaml.safe_load")
    def test_init_with_malformed_yaml(self, mock_yaml_load):
        """Test StateHandler initialization with malformed YAML."""
        mock_yaml_load.side_effect = yaml.YAMLError("Invalid YAML")
        
        with pytest.raises(yaml.YAMLError):
            StateHandler("test.yaml")

    def test_get_initial_state(self, test_yaml_config_file):
        """Test get_initial_state returns correct initial state."""
        handler = StateHandler(test_yaml_config_file)
        initial_state = handler.get_initial_state()
        
        assert initial_state.name == "test_user"
        assert initial_state == handler.states["test_user"]

    def test_get_next_state_with_simple_transition(self, test_yaml_config_file):
        """Test get_next_state with simple 'next' transition."""
        handler = StateHandler(test_yaml_config_file)
        context = {"messages": []}
        
        next_state = handler.get_next_state("test_user", context)
        
        assert next_state.name == "test_agent"
        assert next_state == handler.states["test_agent"]

    def test_get_next_state_with_invalid_state_name(self, test_yaml_config_file):
        """Test get_next_state with invalid current state name."""
        handler = StateHandler(test_yaml_config_file)
        context = {"messages": []}
        
        with pytest.raises(KeyError):
            handler.get_next_state("invalid_state", context)

    def test_get_next_state_with_no_transitions(self, tmp_path):
        """Test get_next_state with terminal state (no transitions)."""
        # Create config with terminal state
        config_data = {
            "initial": "terminal_state",
            "states": {
                "terminal_state": {
                    "type": "user",
                    "transition": {}  # No transitions
                }
            }
        }
        config_file = tmp_path / "terminal_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        handler = StateHandler(str(config_file))
        context = {"messages": []}
        
        # Should return the same state when no transitions
        next_state = handler.get_next_state("terminal_state", context)
        assert next_state.name == "terminal_state"

    def test_get_next_state_with_multiple_transitions(self, tmp_path):
        """Test get_next_state with multiple transition options."""
        # Create config with multiple transitions (fallback behavior)
        config_data = {
            "initial": "multi_state",
            "states": {
                "multi_state": {
                    "type": "user",
                    "transition": {
                        "option1": "state1",
                        "option2": "state2"
                    }
                },
                "state1": {
                    "type": "user",
                    "transition": {}
                },
                "state2": {
                    "type": "user", 
                    "transition": {}
                }
            }
        }
        config_file = tmp_path / "multi_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        handler = StateHandler(str(config_file))
        context = {"messages": []}
        
        # Should return first transition value (fallback behavior)
        next_state = handler.get_next_state("multi_state", context)
        assert next_state.name in ["state1", "state2"]

    @patch("builtins.open", mock_open())
    @patch("yaml.safe_load")
    def test_states_initialization_from_registry(self, mock_yaml_load):
        """Test that states are properly initialized from STATE_REGISTRY."""
        # Mock YAML data
        mock_yaml_load.return_value = {
            "initial": "test_state",
            "states": {
                "test_state": {
                    "type": "user",
                    "transition": {"next": "test_state"}
                }
            }
        }
        
        # Mock state class in registry
        mock_state_class = Mock()
        mock_state_instance = Mock()
        mock_state_class.return_value = mock_state_instance
        
        with patch.dict(STATE_REGISTRY, {"user": mock_state_class}):
            handler = StateHandler("test.yaml")
            
            # Verify state class was called with correct parameters
            mock_state_class.assert_called_once_with(
                "test_state", 
                {"type": "user", "transition": {"next": "test_state"}}
            )
            
            # Verify state instance was stored
            assert handler.states["test_state"] == mock_state_instance

    def test_graph_property_access(self, test_yaml_config_file):
        """Test that graph property contains loaded YAML data."""
        handler = StateHandler(test_yaml_config_file)
        
        assert "initial" in handler.graph
        assert "states" in handler.graph
        assert handler.graph["initial"] == "test_user"
        assert "test_user" in handler.graph["states"]
        assert "test_agent" in handler.graph["states"]

    def test_missing_initial_key_in_yaml(self, tmp_path):
        """Test handling of YAML without 'initial' key."""
        config_data = {
            "states": {
                "test_state": {
                    "type": "user",
                    "transition": {}
                }
            }
            # Missing 'initial' key
        }
        config_file = tmp_path / "no_initial_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        with pytest.raises(KeyError):
            StateHandler(str(config_file))

    def test_missing_states_key_in_yaml(self, tmp_path):
        """Test handling of YAML without 'states' key."""
        config_data = {
            "initial": "test_state"
            # Missing 'states' key  
        }
        config_file = tmp_path / "no_states_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        handler = StateHandler(str(config_file))
        
        # Should handle missing states gracefully (empty dict)
        assert handler.states == {}