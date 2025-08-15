import pytest
from unittest.mock import Mock, patch, MagicMock
from io import StringIO
from state_module.state_ai import StateAI
from model_module.ArkModelNew import AIMessage


class TestStateAI:
    """Tests for StateAI class."""

    def test_state_ai_initialization(self):
        """Test StateAI initialization with valid config."""
        config = {
            "type": "agent",
            "transition": {"next": "user_state"},
            "is_terminal": False
        }
        
        state = StateAI("test_ai", config)
        
        assert state.name == "test_ai"
        assert state.config == config
        assert state.transition == {"next": "user_state"}
        assert state.is_terminal == False

    def test_agent_response_generation(self):
        """Test agent response generation through call_llm."""
        config = {"type": "agent", "transition": {"next": "user_state"}}
        state = StateAI("test_ai", config)
        
        messages = [Mock()]
        agent = Mock()
        
        # Mock the agent's call_llm method
        mock_response = AIMessage(content="Test AI response")
        agent.call_llm.return_value = mock_response
        
        with patch('builtins.print'):  # Suppress print output
            result = state.run(messages, agent)
        
        agent.call_llm.assert_called_once_with(context=messages)
        assert result == mock_response

    def test_check_transition_ready_always_returns_true(self):
        """Test that check_transition_ready always returns True."""
        config = {"type": "agent", "transition": {"next": "user_state"}}
        state = StateAI("test_ai", config)
        
        result = state.check_transition_ready()
        
        assert result is True

    def test_run_method_with_mocked_agent(self):
        """Test run method with mocked agent."""
        config = {"type": "agent", "transition": {"next": "user_state"}}
        state = StateAI("test_ai", config)
        
        messages = [Mock(), Mock()]
        agent = Mock()
        
        mock_ai_message = AIMessage(content="Mocked AI response")
        agent.call_llm.return_value = mock_ai_message
        
        with patch('builtins.print'):
            result = state.run(messages, agent)
        
        assert result == mock_ai_message
        agent.call_llm.assert_called_once_with(context=messages)

    def test_run_method_returns_ai_message(self):
        """Test that run method returns AIMessage instance."""
        config = {"type": "agent", "transition": {"next": "user_state"}}
        state = StateAI("test_ai", config)
        
        messages = []
        agent = Mock()
        
        expected_response = AIMessage(content="Test response")
        agent.call_llm.return_value = expected_response
        
        with patch('builtins.print'):
            result = state.run(messages, agent)
        
        assert isinstance(result, AIMessage)
        assert result == expected_response

    @patch('builtins.print')
    def test_print_output_functionality(self, mock_print):
        """Test that AI response is printed to output."""
        config = {"type": "agent", "transition": {"next": "user_state"}}
        state = StateAI("test_ai", config)
        
        messages = []
        agent = Mock()
        
        test_content = "This should be printed"
        mock_response = AIMessage(content=test_content)
        agent.call_llm.return_value = mock_response
        
        result = state.run(messages, agent)
        
        # Verify print was called with the AI response content
        mock_print.assert_called_once_with(test_content)

    def test_agent_call_llm_with_context_parameter(self):
        """Test that agent.call_llm is called with correct context parameter."""
        config = {"type": "agent", "transition": {"next": "user_state"}}
        state = StateAI("test_ai", config)
        
        test_messages = [Mock(), Mock(), Mock()]
        agent = Mock()
        
        mock_response = AIMessage(content="Context test")
        agent.call_llm.return_value = mock_response
        
        with patch('builtins.print'):
            result = state.run(test_messages, agent)
        
        # Verify call_llm was called with the exact messages context
        agent.call_llm.assert_called_once_with(context=test_messages)

    def test_terminal_state_behavior(self):
        """Test terminal state behavior."""
        config = {
            "type": "agent",
            "transition": {},
            "is_terminal": True
        }
        
        state = StateAI("terminal_ai", config)
        
        assert state.is_terminal == True
        assert state.transition == {}

    def test_empty_messages_handling(self):
        """Test handling of empty messages list."""
        config = {"type": "agent", "transition": {"next": "user_state"}}
        state = StateAI("test_ai", config)
        
        messages = []  # Empty messages list
        agent = Mock()
        
        mock_response = AIMessage(content="Response to empty context")
        agent.call_llm.return_value = mock_response
        
        with patch('builtins.print'):
            result = state.run(messages, agent)
        
        agent.call_llm.assert_called_once_with(context=[])
        assert result == mock_response

    def test_agent_call_llm_error_handling(self):
        """Test error handling when agent.call_llm fails."""
        config = {"type": "agent", "transition": {"next": "user_state"}}
        state = StateAI("test_ai", config)
        
        messages = [Mock()]
        agent = Mock()
        
        # Make call_llm raise an exception
        agent.call_llm.side_effect = Exception("LLM call failed")
        
        with pytest.raises(Exception, match="LLM call failed"):
            state.run(messages, agent)

    def test_messages_parameter_not_modified(self):
        """Test that the messages parameter is not modified by StateAI."""
        config = {"type": "agent", "transition": {"next": "user_state"}}
        state = StateAI("test_ai", config)
        
        messages = [Mock(), Mock()]
        original_messages = messages.copy()
        original_length = len(messages)
        agent = Mock()
        
        mock_response = AIMessage(content="Test response")
        agent.call_llm.return_value = mock_response
        
        with patch('builtins.print'):
            state.run(messages, agent)
        
        # Messages list should not be modified by StateAI
        assert len(messages) == original_length
        assert messages == original_messages

    def test_print_with_none_content(self):
        """Test printing behavior when AI message has None content."""
        config = {"type": "agent", "transition": {"next": "user_state"}}
        state = StateAI("test_ai", config)
        
        messages = []
        agent = Mock()
        
        mock_response = AIMessage(content=None)
        agent.call_llm.return_value = mock_response
        
        with patch('builtins.print') as mock_print:
            result = state.run(messages, agent)
        
        mock_print.assert_called_once_with(None)
        assert result == mock_response

    def test_print_with_empty_content(self):
        """Test printing behavior when AI message has empty content."""
        config = {"type": "agent", "transition": {"next": "user_state"}}
        state = StateAI("test_ai", config)
        
        messages = []
        agent = Mock()
        
        mock_response = AIMessage(content="")
        agent.call_llm.return_value = mock_response
        
        with patch('builtins.print') as mock_print:
            result = state.run(messages, agent)
        
        mock_print.assert_called_once_with("")
        assert result == mock_response

    def test_state_inheritance_from_base_state(self):
        """Test that StateAI properly inherits from base State class."""
        config = {"type": "agent", "transition": {"next": "user_state"}}
        state = StateAI("test_ai", config)
        
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

    def test_multiple_messages_context_handling(self):
        """Test handling of multiple messages in context."""
        config = {"type": "agent", "transition": {"next": "user_state"}}
        state = StateAI("test_ai", config)
        
        messages = [Mock() for _ in range(5)]  # 5 mock messages
        agent = Mock()
        
        mock_response = AIMessage(content="Response to multiple messages")
        agent.call_llm.return_value = mock_response
        
        with patch('builtins.print'):
            result = state.run(messages, agent)
        
        # Should pass all messages to call_llm
        agent.call_llm.assert_called_once_with(context=messages)
        assert result == mock_response

    def test_agent_object_requirement(self):
        """Test that a valid agent object is required."""
        config = {"type": "agent", "transition": {"next": "user_state"}}
        state = StateAI("test_ai", config)
        
        messages = []
        
        # Test with None agent
        with pytest.raises(AttributeError):
            state.run(messages, None)
        
        # Test with agent missing call_llm method
        invalid_agent = Mock()
        del invalid_agent.call_llm
        
        with pytest.raises(AttributeError):
            state.run(messages, invalid_agent)