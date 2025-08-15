import pytest
from unittest.mock import Mock, patch, MagicMock
from io import StringIO
from state_module.state_user import StateUser
from model_module.ArkModelNew import UserMessage


class TestStateUser:
    """Tests for StateUser class."""

    def test_state_user_initialization(self):
        """Test StateUser initialization with valid config."""
        config = {
            "type": "user",
            "transition": {"next": "agent_state"},
            "is_terminal": False
        }
        
        state = StateUser("test_user", config)
        
        assert state.name == "test_user"
        assert state.config == config
        assert state.transition == {"next": "agent_state"}
        assert state.is_terminal == False

    @patch('builtins.input', return_value='test user input')
    def test_normal_user_input_handling(self, mock_input):
        """Test normal user input handling."""
        config = {"type": "user", "transition": {"next": "agent_state"}}
        state = StateUser("test_user", config)
        
        messages = []
        agent = Mock()
        
        result = state.run(messages, agent)
        
        assert isinstance(result, UserMessage)
        assert result.content == "test user input"
        mock_input.assert_called_once_with("User: ")

    @patch('builtins.input', return_value='exit')
    @patch('sys.exit')
    def test_exit_command_handling(self, mock_exit, mock_input):
        """Test 'exit' command handling."""
        config = {"type": "user", "transition": {"next": "agent_state"}}
        state = StateUser("test_user", config)
        
        messages = []
        agent = Mock()
        
        state.run(messages, agent)
        
        mock_exit.assert_called_once_with(0)

    @patch('builtins.input', return_value='EXIT')
    @patch('sys.exit')
    def test_exit_command_case_insensitive(self, mock_exit, mock_input):
        """Test that 'exit' command is case insensitive."""
        config = {"type": "user", "transition": {"next": "agent_state"}}
        state = StateUser("test_user", config)
        
        messages = []
        agent = Mock()
        
        state.run(messages, agent)
        
        mock_exit.assert_called_once_with(0)

    def test_check_transition_ready_always_returns_true(self):
        """Test that check_transition_ready always returns True."""
        config = {"type": "user", "transition": {"next": "agent_state"}}
        state = StateUser("test_user", config)
        
        result = state.check_transition_ready()
        
        assert result is True

    @patch('builtins.input', return_value='test message')
    def test_run_method_returns_user_message(self, mock_input):
        """Test that run method returns UserMessage instance."""
        config = {"type": "user", "transition": {"next": "agent_state"}}
        state = StateUser("test_user", config)
        
        messages = []
        agent = Mock()
        
        result = state.run(messages, agent)
        
        assert isinstance(result, UserMessage)
        assert hasattr(result, 'content')
        assert result.content == "test message"

    def test_terminal_state_behavior(self):
        """Test terminal state behavior."""
        config = {
            "type": "user",
            "transition": {},
            "is_terminal": True
        }
        
        state = StateUser("terminal_user", config)
        
        assert state.is_terminal == True
        assert state.transition == {}

    @patch('builtins.input', return_value='')
    def test_empty_input_handling(self, mock_input):
        """Test handling of empty user input."""
        config = {"type": "user", "transition": {"next": "agent_state"}}
        state = StateUser("test_user", config)
        
        messages = []
        agent = Mock()
        
        result = state.run(messages, agent)
        
        assert isinstance(result, UserMessage)
        assert result.content == ""

    @patch('builtins.input', return_value='   whitespace only   ')
    def test_whitespace_input_handling(self, mock_input):
        """Test handling of whitespace-only user input."""
        config = {"type": "user", "transition": {"next": "agent_state"}}
        state = StateUser("test_user", config)
        
        messages = []
        agent = Mock()
        
        result = state.run(messages, agent)
        
        assert isinstance(result, UserMessage)
        assert result.content == "   whitespace only   "  # Should preserve whitespace

    @patch('builtins.input', side_effect=KeyboardInterrupt())
    def test_keyboard_interrupt_handling(self, mock_input):
        """Test handling of keyboard interrupt during input."""
        config = {"type": "user", "transition": {"next": "agent_state"}}
        state = StateUser("test_user", config)
        
        messages = []
        agent = Mock()
        
        with pytest.raises(KeyboardInterrupt):
            state.run(messages, agent)

    @patch('builtins.input', side_effect=EOFError())
    def test_eof_error_handling(self, mock_input):
        """Test handling of EOF error during input."""
        config = {"type": "user", "transition": {"next": "agent_state"}}
        state = StateUser("test_user", config)
        
        messages = []
        agent = Mock()
        
        with pytest.raises(EOFError):
            state.run(messages, agent)

    @patch('builtins.input', return_value='multi\nline\ninput')
    def test_multiline_input_handling(self, mock_input):
        """Test handling of input containing newlines."""
        config = {"type": "user", "transition": {"next": "agent_state"}}
        state = StateUser("test_user", config)
        
        messages = []
        agent = Mock()
        
        result = state.run(messages, agent)
        
        assert isinstance(result, UserMessage)
        assert result.content == "multi\nline\ninput"

    @patch('builtins.input', return_value='special !@#$%^&*() characters')
    def test_special_characters_input(self, mock_input):
        """Test handling of special characters in input."""
        config = {"type": "user", "transition": {"next": "agent_state"}}
        state = StateUser("test_user", config)
        
        messages = []
        agent = Mock()
        
        result = state.run(messages, agent)
        
        assert isinstance(result, UserMessage)
        assert result.content == "special !@#$%^&*() characters"

    @patch('builtins.input', return_value='unicode тест 测试 🤖')
    def test_unicode_input_handling(self, mock_input):
        """Test handling of unicode characters in input."""
        config = {"type": "user", "transition": {"next": "agent_state"}}
        state = StateUser("test_user", config)
        
        messages = []
        agent = Mock()
        
        result = state.run(messages, agent)
        
        assert isinstance(result, UserMessage)
        assert result.content == "unicode тест 测试 🤖"

    def test_state_inheritance_from_base_state(self):
        """Test that StateUser properly inherits from base State class."""
        config = {"type": "user", "transition": {"next": "agent_state"}}
        state = StateUser("test_user", config)
        
        # Should have inherited properties
        assert hasattr(state, 'name')
        assert hasattr(state, 'config')
        assert hasattr(state, 'transition')
        assert hasattr(state, 'is_terminal')
        
        # Should have implemented required methods
        assert hasattr(state, 'run')
        assert hasattr(state, 'check_transition_ready')
        
        # Methods should be callable
        assert callable(state.run)
        assert callable(state.check_transition_ready)

    def test_messages_parameter_not_modified(self):
        """Test that the messages parameter is not modified by StateUser."""
        config = {"type": "user", "transition": {"next": "agent_state"}}
        state = StateUser("test_user", config)
        
        messages = [Mock(), Mock()]
        original_length = len(messages)
        agent = Mock()
        
        with patch('builtins.input', return_value='test'):
            state.run(messages, agent)
        
        # Messages list should not be modified by StateUser
        assert len(messages) == original_length

    def test_agent_parameter_not_used(self):
        """Test that the agent parameter is not used by StateUser."""
        config = {"type": "user", "transition": {"next": "agent_state"}}
        state = StateUser("test_user", config)
        
        messages = []
        agent = Mock()
        
        with patch('builtins.input', return_value='test'):
            result = state.run(messages, agent)
        
        # Agent should not have been called
        agent.assert_not_called()
        assert isinstance(result, UserMessage)