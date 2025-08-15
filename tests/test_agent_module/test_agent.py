import pytest
from unittest.mock import Mock, MagicMock, patch
from agent_module.agent import Agent
from state_module.state_handler import StateHandler
from memory_module.memory import Memory
from model_module.ArkModelNew import ArkModelLink, UserMessage, AIMessage, SystemMessage
from tool_module.tool import Tool


class TestAgent:
    """Tests for Agent class."""

    def test_init_with_all_required_components(self, mock_state_handler, mock_memory, mock_ark_model):
        """Test Agent initialization with all required components."""
        mock_initial_state = Mock()
        mock_state_handler.get_initial_state.return_value = mock_initial_state
        
        agent = Agent(
            agent_id="test_agent",
            flow=mock_state_handler,
            memory=mock_memory,
            llm=mock_ark_model
        )
        
        assert agent.agent_id == "test_agent"
        assert agent.flow == mock_state_handler
        assert agent.memory == mock_memory
        assert agent.llm == mock_ark_model
        assert agent.current_state == mock_initial_state
        assert agent.context == {}
        assert agent.tools == []
        assert agent.tool_names == []

    def test_init_with_missing_components(self):
        """Test Agent initialization with missing components."""
        with pytest.raises(TypeError):
            Agent()  # Missing all required parameters

    def test_initial_state_assignment(self, mock_state_handler, mock_memory, mock_ark_model):
        """Test that initial state is correctly assigned during initialization."""
        mock_initial_state = Mock()
        mock_initial_state.name = "initial_state"
        mock_state_handler.get_initial_state.return_value = mock_initial_state
        
        agent = Agent("test", mock_state_handler, mock_memory, mock_ark_model)
        
        mock_state_handler.get_initial_state.assert_called_once()
        assert agent.current_state == mock_initial_state

    def test_context_initialization(self, mock_state_handler, mock_memory, mock_ark_model):
        """Test that context is properly initialized as empty dict."""
        mock_state_handler.get_initial_state.return_value = Mock()
        
        agent = Agent("test", mock_state_handler, mock_memory, mock_ark_model)
        
        assert isinstance(agent.context, dict)
        assert len(agent.context) == 0

    def test_bind_tool_functionality(self, mock_state_handler, mock_memory, mock_ark_model, mock_tool):
        """Test bind_tool adds tool to tools list."""
        mock_state_handler.get_initial_state.return_value = Mock()
        agent = Agent("test", mock_state_handler, mock_memory, mock_ark_model)
        
        agent.bind_tool(mock_tool)
        
        assert mock_tool in agent.tools
        assert len(agent.tools) == 1

    def test_bind_multiple_tools(self, mock_state_handler, mock_memory, mock_ark_model):
        """Test binding multiple tools."""
        mock_state_handler.get_initial_state.return_value = Mock()
        agent = Agent("test", mock_state_handler, mock_memory, mock_ark_model)
        
        tool1 = Mock()
        tool2 = Mock()
        
        agent.bind_tool(tool1)
        agent.bind_tool(tool2)
        
        assert len(agent.tools) == 2
        assert tool1 in agent.tools
        assert tool2 in agent.tools

    @patch('agent_module.agent.Tool')
    def test_find_downloaded_tool_functionality(self, mock_tool_class, mock_state_handler, mock_memory, mock_ark_model):
        """Test find_downloaded_tool pulls tool from registry and binds it."""
        mock_state_handler.get_initial_state.return_value = Mock()
        agent = Agent("test", mock_state_handler, mock_memory, mock_ark_model)
        
        mock_tool_instance = Mock()
        mock_tool_instance.tool = "test_tool"
        mock_tool_class.pull_tool_from_registry.return_value = mock_tool_instance
        
        agent.find_downloaded_tool("test_embedding")
        
        mock_tool_class.pull_tool_from_registry.assert_called_once_with("test_embedding")
        assert mock_tool_instance in agent.tools
        assert "test_tool" in agent.tool_names

    def test_tool_names_list_management(self, mock_state_handler, mock_memory, mock_ark_model):
        """Test that tool names are properly managed."""
        mock_state_handler.get_initial_state.return_value = Mock()
        agent = Agent("test", mock_state_handler, mock_memory, mock_ark_model)
        
        assert agent.tool_names == []
        
        # Manually add a tool name to test the list
        agent.tool_names.append("test_tool")
        assert "test_tool" in agent.tool_names
        assert len(agent.tool_names) == 1

    def test_call_llm_with_context_parameter(self, mock_state_handler, mock_memory, mock_ark_model):
        """Test call_llm with context parameter."""
        mock_state_handler.get_initial_state.return_value = Mock()
        agent = Agent("test", mock_state_handler, mock_memory, mock_ark_model)
        
        mock_context = {"messages": [Mock()]}
        mock_llm_response = "Test LLM response"
        
        # Mock the LLM call
        with patch.object(agent, 'llm') as mock_llm:
            mock_chat_model = Mock()
            mock_chat_model.generate_response.return_value = mock_llm_response
            mock_llm.bind_tools.return_value = mock_chat_model
            
            result = agent.call_llm(context=mock_context)
            
            assert isinstance(result, AIMessage)
            assert result.content == mock_llm_response

    def test_call_llm_with_input_parameter_only(self, mock_state_handler, mock_memory, mock_ark_model):
        """Test call_llm with input parameter only."""
        mock_state_handler.get_initial_state.return_value = Mock()
        agent = Agent("test", mock_state_handler, mock_memory, mock_ark_model)
        
        test_input = "Test input message"
        mock_llm_response = "Test LLM response"
        
        with patch.object(agent, 'llm') as mock_llm:
            mock_chat_model = Mock()
            mock_chat_model.generate_response.return_value = mock_llm_response
            mock_llm.bind_tools.return_value = mock_chat_model
            
            result = agent.call_llm(input=test_input)
            
            assert isinstance(result, AIMessage)
            assert result.content == mock_llm_response

    def test_call_llm_with_json_schema_parameter(self, mock_state_handler, mock_memory, mock_ark_model):
        """Test call_llm with json_schema parameter."""
        mock_state_handler.get_initial_state.return_value = Mock()
        agent = Agent("test", mock_state_handler, mock_memory, mock_ark_model)
        
        test_schema = {"type": "object", "properties": {"test": {"type": "string"}}}
        mock_llm_response = "Test LLM response"
        
        with patch.object(agent, 'llm') as mock_llm:
            mock_chat_model = Mock()
            mock_chat_model.generate_response.return_value = mock_llm_response
            mock_llm.bind_tools.return_value = mock_chat_model
            
            result = agent.call_llm(input="test", json_schema=test_schema)
            
            mock_chat_model.generate_response.assert_called_once()
            args = mock_chat_model.generate_response.call_args
            assert test_schema in args[0] or test_schema in args[1].values()

    def test_call_llm_error_handling(self, mock_state_handler, mock_memory, mock_ark_model):
        """Test call_llm error handling."""
        mock_state_handler.get_initial_state.return_value = Mock()
        agent = Agent("test", mock_state_handler, mock_memory, mock_ark_model)
        
        with patch.object(agent, 'llm') as mock_llm:
            mock_llm.bind_tools.side_effect = Exception("LLM Error")
            
            with pytest.raises(Exception, match="LLM Error"):
                agent.call_llm(input="test")

    def test_step_method_with_valid_input(self, mock_state_handler, mock_memory, mock_ark_model):
        """Test step method with valid input."""
        # Create mock state that is not terminal
        mock_state = Mock()
        mock_state.is_terminal = False
        mock_state.run.return_value = Mock()  # Mock message return
        mock_state_handler.get_initial_state.return_value = mock_state
        mock_state_handler.get_next_state.return_value = mock_state
        
        agent = Agent("test", mock_state_handler, mock_memory, mock_ark_model)
        agent.context = {"messages": []}
        
        # Override current_state to control the flow
        agent.current_state = mock_state
        
        # Make state terminal after first iteration to avoid infinite loop
        def make_terminal(*args):
            mock_state.is_terminal = True
            return Mock()
        
        mock_state.run.side_effect = make_terminal
        
        agent.step("test input")
        
        mock_state.run.assert_called()

    def test_step_method_state_transition_logic(self, mock_state_handler, mock_memory, mock_ark_model):
        """Test step method state transition logic."""
        # Create two different states
        initial_state = Mock()
        initial_state.is_terminal = False
        initial_state.name = "initial"
        
        next_state = Mock()  
        next_state.is_terminal = True  # Terminal to stop the loop
        next_state.name = "next"
        
        mock_state_handler.get_initial_state.return_value = initial_state
        mock_state_handler.get_next_state.return_value = next_state
        
        agent = Agent("test", mock_state_handler, mock_memory, mock_ark_model)
        agent.context = {"messages": []}
        
        # Mock the state run method to return a message
        mock_message = Mock()
        initial_state.run.return_value = mock_message
        
        agent.step("test input")
        
        # Verify state handler was called for next state
        mock_state_handler.get_next_state.assert_called()
        
        # Verify context was updated
        assert mock_message in agent.context["messages"]

    def test_step_method_terminal_state_handling(self, mock_state_handler, mock_memory, mock_ark_model):
        """Test step method handles terminal states correctly."""
        # Create terminal state
        terminal_state = Mock()
        terminal_state.is_terminal = True
        terminal_state.name = "terminal"
        
        mock_state_handler.get_initial_state.return_value = terminal_state
        
        agent = Agent("test", mock_state_handler, mock_memory, mock_ark_model)
        agent.context = {"messages": []}
        
        agent.step("test input")
        
        # Terminal state should not call run method
        terminal_state.run.assert_not_called()
        
        # Should not call get_next_state for terminal states
        mock_state_handler.get_next_state.assert_not_called()

    def test_step_method_context_update_mechanism(self, mock_state_handler, mock_memory, mock_ark_model):
        """Test step method updates context correctly."""
        mock_state = Mock()
        mock_state.is_terminal = False
        mock_state_handler.get_initial_state.return_value = mock_state
        mock_state_handler.get_next_state.return_value = mock_state
        
        agent = Agent("test", mock_state_handler, mock_memory, mock_ark_model)
        agent.context = {"messages": []}
        
        # Create mock message to be returned by state.run()
        mock_message = Mock()
        
        # Make state terminal after first run to avoid infinite loop
        def run_and_terminate(*args):
            mock_state.is_terminal = True
            return mock_message
        
        mock_state.run.side_effect = run_and_terminate
        
        agent.step("test input")
        
        # Verify message was added to context
        assert mock_message in agent.context["messages"]
        assert len(agent.context["messages"]) == 1

    def test_step_method_no_current_state_initialization(self, mock_state_handler, mock_memory, mock_ark_model):
        """Test step method initializes current_state if None."""
        initial_state = Mock()
        initial_state.is_terminal = True  # Make it terminal to stop immediately
        mock_state_handler.get_initial_state.return_value = initial_state
        
        agent = Agent("test", mock_state_handler, mock_memory, mock_ark_model)
        agent.current_state = None  # Simulate no current state
        agent.context = {"messages": []}
        
        agent.step("test input")
        
        # Should call get_initial_state when current_state is None
        mock_state_handler.get_initial_state.assert_called()
        assert agent.current_state == initial_state

    def test_tool_registry_integration(self, mock_state_handler, mock_memory, mock_ark_model):
        """Test tool registry integration."""
        mock_state_handler.get_initial_state.return_value = Mock()
        agent = Agent("test", mock_state_handler, mock_memory, mock_ark_model)
        
        # Test that agent has access to tool registry (from module level)
        from agent_module.agent import tool_registry
        
        assert "keyA" in tool_registry
        assert "embedding_b" in tool_registry
        assert tool_registry["keyA"]["url"] == "https://localhost:4040"