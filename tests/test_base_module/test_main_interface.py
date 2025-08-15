import pytest
from unittest.mock import Mock, patch, MagicMock
import os
import sys
from base_module.main_interface import run_cli_agent


class TestMainInterface:
    """Tests for main_interface.py CLI agent functionality."""

    @patch('base_module.main_interface.Agent')
    @patch('base_module.main_interface.ArkModelLink')
    @patch('base_module.main_interface.Memory')
    @patch('base_module.main_interface.StateHandler')
    @patch('builtins.print')
    def test_component_initialization_with_valid_parameters(
        self, mock_print, mock_state_handler, mock_memory, mock_ark_model, mock_agent
    ):
        """Test component initialization with valid parameters."""
        # Setup mocks
        mock_state_handler_instance = Mock()
        mock_memory_instance = Mock()
        mock_ark_model_instance = Mock()
        mock_agent_instance = Mock()
        
        mock_state_handler.return_value = mock_state_handler_instance
        mock_memory.return_value = mock_memory_instance
        mock_ark_model.return_value = mock_ark_model_instance
        mock_agent.return_value = mock_agent_instance
        
        # Mock agent methods
        mock_response = Mock()
        mock_response.content = "Hello! I'm ARK, your assistant."
        mock_agent_instance.call_llm.return_value = mock_response
        mock_agent_instance.context = {"messages": []}
        mock_agent_instance.step.return_value = None
        
        run_cli_agent()
        
        # Verify component initialization
        mock_state_handler.assert_called_once_with(yaml_path="../state_module/state_graph.yaml")
        mock_memory.assert_called_once_with(agent_id="cli-agent")
        mock_ark_model.assert_called_once_with(base_url="http://localhost:30000/v1")
        mock_agent.assert_called_once_with(
            agent_id="cli-agent",
            flow=mock_state_handler_instance,
            memory=mock_memory_instance,
            llm=mock_ark_model_instance
        )

    @patch('base_module.main_interface.Agent')
    @patch('base_module.main_interface.ArkModelLink')
    @patch('base_module.main_interface.Memory')
    @patch('base_module.main_interface.StateHandler')
    @patch('builtins.print')
    def test_system_message_setup(
        self, mock_print, mock_state_handler, mock_memory, mock_ark_model, mock_agent
    ):
        """Test system message setup and default response generation."""
        # Setup mocks
        mock_agent_instance = Mock()
        mock_agent.return_value = mock_agent_instance
        mock_agent_instance.context = {"messages": []}
        
        mock_response = Mock()
        mock_response.content = "Hello! I'm ARK, your assistant."
        mock_agent_instance.call_llm.return_value = mock_response
        mock_agent_instance.step.return_value = None
        
        run_cli_agent()
        
        # Verify system message was added to context
        assert len(mock_agent_instance.context["messages"]) == 1
        system_message = mock_agent_instance.context["messages"][0]
        
        # Check that it's a SystemMessage with correct content
        assert hasattr(system_message, 'content')
        assert "helpful assistant" in system_message.content
        assert "ARK" in system_message.content
        
        # Verify LLM was called with context
        mock_agent_instance.call_llm.assert_called_once_with(context=mock_agent_instance.context["messages"])

    @patch('base_module.main_interface.Agent')
    @patch('base_module.main_interface.ArkModelLink')
    @patch('base_module.main_interface.Memory')
    @patch('base_module.main_interface.StateHandler')
    @patch('builtins.print')
    def test_default_response_generation(
        self, mock_print, mock_state_handler, mock_memory, mock_ark_model, mock_agent
    ):
        """Test default response generation and printing."""
        # Setup mocks
        mock_agent_instance = Mock()
        mock_agent.return_value = mock_agent_instance
        mock_agent_instance.context = {"messages": []}
        
        expected_response = "Hello! I'm ARK, your helpful assistant."
        mock_response = Mock()
        mock_response.content = expected_response
        mock_agent_instance.call_llm.return_value = mock_response
        mock_agent_instance.step.return_value = None
        
        run_cli_agent()
        
        # Verify response was printed
        print_calls = mock_print.call_args_list
        assert any(expected_response in str(call) for call in print_calls)

    @patch('base_module.main_interface.Agent')
    @patch('base_module.main_interface.ArkModelLink')
    @patch('base_module.main_interface.Memory')
    @patch('base_module.main_interface.StateHandler')
    @patch('builtins.print')
    def test_keyboard_interrupt_handling(
        self, mock_print, mock_state_handler, mock_memory, mock_ark_model, mock_agent
    ):
        """Test keyboard interrupt handling during agent execution."""
        # Setup mocks
        mock_agent_instance = Mock()
        mock_agent.return_value = mock_agent_instance
        mock_agent_instance.context = {"messages": []}
        
        mock_response = Mock()
        mock_response.content = "Hello!"
        mock_agent_instance.call_llm.return_value = mock_response
        
        # Make agent.step raise KeyboardInterrupt
        mock_agent_instance.step.side_effect = KeyboardInterrupt()
        
        run_cli_agent()
        
        # Verify interrupt message was printed
        print_calls = mock_print.call_args_list
        interrupt_message_printed = any("Interaction interrupted" in str(call) for call in print_calls)
        assert interrupt_message_printed

    @patch('base_module.main_interface.StateHandler')
    @patch('base_module.main_interface.Memory')
    @patch('base_module.main_interface.ArkModelLink')
    @patch('base_module.main_interface.Agent')
    @patch('builtins.print')
    def test_component_initialization_with_invalid_yaml_path(
        self, mock_print, mock_agent, mock_ark_model, mock_memory, mock_state_handler
    ):
        """Test behavior with invalid YAML path."""
        # Make StateHandler raise exception for invalid path
        mock_state_handler.side_effect = FileNotFoundError("YAML file not found")
        
        with pytest.raises(FileNotFoundError):
            run_cli_agent()

    @patch('base_module.main_interface.StateHandler')
    @patch('base_module.main_interface.Memory')
    @patch('base_module.main_interface.ArkModelLink')
    @patch('base_module.main_interface.Agent')
    @patch('builtins.print')
    def test_behavior_with_llm_connection_failures(
        self, mock_print, mock_agent, mock_ark_model, mock_memory, mock_state_handler
    ):
        """Test behavior with LLM connection failures."""
        # Setup mocks
        mock_agent_instance = Mock()
        mock_agent.return_value = mock_agent_instance
        mock_agent_instance.context = {"messages": []}
        
        # Make LLM call fail
        mock_agent_instance.call_llm.side_effect = ConnectionError("LLM connection failed")
        
        with pytest.raises(ConnectionError):
            run_cli_agent()

    @patch('base_module.main_interface.Agent')
    @patch('base_module.main_interface.ArkModelLink')
    @patch('base_module.main_interface.Memory')
    @patch('base_module.main_interface.StateHandler')
    @patch('builtins.print')
    def test_full_cli_agent_flow_integration(
        self, mock_print, mock_state_handler, mock_memory, mock_ark_model, mock_agent
    ):
        """Test full CLI agent flow with mocked components."""
        # Setup comprehensive mocks
        mock_state_handler_instance = Mock()
        mock_memory_instance = Mock()
        mock_ark_model_instance = Mock()
        mock_agent_instance = Mock()
        
        mock_state_handler.return_value = mock_state_handler_instance
        mock_memory.return_value = mock_memory_instance
        mock_ark_model.return_value = mock_ark_model_instance
        mock_agent.return_value = mock_agent_instance
        
        # Setup agent behavior
        mock_agent_instance.context = {"messages": []}
        mock_response = Mock()
        mock_response.content = "Hello! I'm ARK."
        mock_agent_instance.call_llm.return_value = mock_response
        mock_agent_instance.step.return_value = None
        
        run_cli_agent()
        
        # Verify full initialization sequence
        assert mock_state_handler.called
        assert mock_memory.called
        assert mock_ark_model.called
        assert mock_agent.called
        
        # Verify system message setup
        assert len(mock_agent_instance.context["messages"]) == 1
        
        # Verify LLM interaction
        mock_agent_instance.call_llm.assert_called_once()
        
        # Verify agent step execution
        mock_agent_instance.step.assert_called_once_with("remove this variable")
        
        # Verify startup message printed
        startup_printed = any("Starting CLI Agent" in str(call) for call in mock_print.call_args_list)
        assert startup_printed

    @patch('base_module.main_interface.Agent')
    @patch('base_module.main_interface.ArkModelLink')
    @patch('base_module.main_interface.Memory')
    @patch('base_module.main_interface.StateHandler')
    def test_component_interaction_flow(
        self, mock_state_handler, mock_memory, mock_ark_model, mock_agent
    ):
        """Test component interaction between StateHandler, Memory, and Agent."""
        # Setup mocks
        mock_state_handler_instance = Mock()
        mock_memory_instance = Mock()
        mock_ark_model_instance = Mock()
        mock_agent_instance = Mock()
        
        mock_state_handler.return_value = mock_state_handler_instance
        mock_memory.return_value = mock_memory_instance
        mock_ark_model.return_value = mock_ark_model_instance
        mock_agent.return_value = mock_agent_instance
        
        mock_agent_instance.context = {"messages": []}
        mock_response = Mock()
        mock_response.content = "Test response"
        mock_agent_instance.call_llm.return_value = mock_response
        
        with patch('builtins.print'):
            run_cli_agent()
        
        # Verify Agent was initialized with correct components
        mock_agent.assert_called_once_with(
            agent_id="cli-agent",
            flow=mock_state_handler_instance,
            memory=mock_memory_instance,
            llm=mock_ark_model_instance
        )

    @patch('base_module.main_interface.Agent')
    @patch('base_module.main_interface.ArkModelLink')
    @patch('base_module.main_interface.Memory')
    @patch('base_module.main_interface.StateHandler')
    @patch('builtins.print')
    def test_context_messages_initialization(
        self, mock_print, mock_state_handler, mock_memory, mock_ark_model, mock_agent
    ):
        """Test that context messages are properly initialized."""
        mock_agent_instance = Mock()
        mock_agent.return_value = mock_agent_instance
        
        # Start with empty context
        mock_agent_instance.context = {}
        
        mock_response = Mock()
        mock_response.content = "Hello!"
        mock_agent_instance.call_llm.return_value = mock_response
        mock_agent_instance.step.return_value = None
        
        run_cli_agent()
        
        # Verify context was initialized with messages list
        assert "messages" in mock_agent_instance.context
        assert isinstance(mock_agent_instance.context["messages"], list)
        assert len(mock_agent_instance.context["messages"]) == 1

    def test_main_guard_execution(self):
        """Test that run_cli_agent is called when script is run directly."""
        # This test verifies the if __name__ == "__main__" guard
        # We can't easily test direct execution, but we can verify the function exists
        assert callable(run_cli_agent)
        
        # Test that the function can be imported
        from base_module.main_interface import run_cli_agent as imported_function
        assert imported_function is run_cli_agent