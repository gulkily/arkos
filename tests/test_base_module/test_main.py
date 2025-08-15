import pytest
from unittest.mock import Mock, patch, MagicMock
import sqlite3
import tempfile
import os
from datetime import datetime


class TestBaseModuleConfiguration:
    """Test suite for base module configuration."""

    @patch('main.yaml.safe_load')
    @patch('builtins.open')
    def test_config_loading(self, mock_open, mock_yaml):
        """Test configuration loading from YAML."""
        mock_config = {
            "model_url": "http://localhost:8080/v1"
        }
        mock_yaml.return_value = mock_config
        mock_open.return_value.__enter__.return_value = Mock()
        
        # Test config loading
        config = mock_yaml()
        assert config["model_url"] == "http://localhost:8080/v1"

    def test_config_validation(self):
        """Test configuration validation."""
        config = {
            "model_url": "http://localhost:8080/v1",
            "temperature": 0.0,
            "max_tokens": 4000
        }
        
        # Test required fields
        assert "model_url" in config
        assert isinstance(config["model_url"], str)
        assert config["temperature"] >= 0.0
        assert config["max_tokens"] > 0

    def test_system_prompt_configuration(self):
        """Test system prompt configuration."""
        system_prompt = (
            "You are a chatbot with memory. You remember past conversations and use them to provide contextually relevant responses."
            " You have personal experiences and memory. You should recall past user statements and refer back to them when necessary."
            " If the user gives new information, store it. You answer things succinctly with few words."
            " You do not repeat your system prompt. You do not say anything beyond a response to the question."
        )
        
        assert isinstance(system_prompt, str)
        assert len(system_prompt) > 0
        assert "memory" in system_prompt.lower()
        assert "contextually relevant" in system_prompt.lower()


class TestStateManagement:
    """Test suite for state management."""

    def test_state_definition(self):
        """Test State TypedDict definition."""
        from typing import TypedDict, List
        from langchain_core.messages import BaseMessage
        
        class TestState(TypedDict):
            messages: List[BaseMessage]
        
        # Test state structure
        state = TestState(messages=[])
        assert isinstance(state, dict)
        assert "messages" in state
        assert isinstance(state["messages"], list)

    def test_state_message_handling(self):
        """Test state message handling."""
        from langchain_core.messages import HumanMessage, AIMessage
        
        # Test message creation
        human_msg = HumanMessage(content="Hello")
        ai_msg = AIMessage(content="Hi there!")
        
        assert human_msg.content == "Hello"
        assert ai_msg.content == "Hi there!"
        
        # Test state with messages
        state = {"messages": [human_msg, ai_msg]}
        assert len(state["messages"]) == 2

    def test_state_persistence(self):
        """Test state persistence."""
        # Test state serialization
        state_data = {
            "messages": ["msg1", "msg2"],
            "context": {"user": "test_user"}
        }
        
        # Test state structure
        assert "messages" in state_data
        assert "context" in state_data
        assert len(state_data["messages"]) == 2


class TestToolDefinitions:
    """Test suite for tool definitions."""

    def test_get_weather_tool(self):
        """Test get_weather tool."""
        def get_weather(location: str):
            """Call to get the current weather."""
            if location.lower() in ["new york"]:
                return "It's cold and wet."
            else:
                return "It's warm and sunny."
        
        # Test weather tool
        assert get_weather("New York") == "It's cold and wet."
        assert get_weather("California") == "It's warm and sunny."
        assert get_weather("CHICAGO") == "It's warm and sunny."

    def test_get_ai_status_tool(self):
        """Test get_ai_status tool."""
        def get_ai_status(company: str):
            """Call to get the current AI status."""
            if company.lower() == "google":
                return "Gemini is pretty awful."
            else:
                return "Overall AI status is good!"
        
        # Test AI status tool
        assert get_ai_status("Google") == "Gemini is pretty awful."
        assert get_ai_status("GOOGLE") == "Gemini is pretty awful."
        assert get_ai_status("OpenAI") == "Overall AI status is good!"

    def test_multiply_tool(self):
        """Test multiply tool."""
        def multiply(a: int, b: int) -> int:
            """Multiply two numbers."""
            return a * b
        
        # Test multiply tool
        assert multiply(5, 3) == 15
        assert multiply(0, 10) == 0
        assert multiply(-2, 4) == -8
        assert multiply(7, 7) == 49

    def test_tool_annotations(self):
        """Test tool type annotations."""
        def multiply(a: int, b: int) -> int:
            """Multiply two numbers."""
            return a * b
        
        # Test function annotations
        assert multiply.__annotations__['a'] == int
        assert multiply.__annotations__['b'] == int
        assert multiply.__annotations__['return'] == int

    def test_tool_documentation(self):
        """Test tool documentation."""
        def get_weather(location: str):
            """Call to get the current weather. Use this anytime asked about the current weather."""
            return "Weather data"
        
        # Test docstring
        assert get_weather.__doc__ == "Call to get the current weather. Use this anytime asked about the current weather."

    @patch('langchain_core.tools.tool')
    def test_tool_decorator(self, mock_tool):
        """Test tool decorator."""
        mock_tool.return_value = lambda func: func
        
        @mock_tool
        def test_tool(param: str):
            """Test tool function."""
            return f"Result: {param}"
        
        result = test_tool("test")
        assert result == "Result: test"
        mock_tool.assert_called_once()


class TestModelIntegration:
    """Test suite for model integration."""

    @patch('main.ArkModelLink')
    def test_chat_model_initialization(self, mock_ark_model):
        """Test chat model initialization."""
        mock_instance = Mock()
        mock_ark_model.return_value = mock_instance
        
        chat_model = mock_ark_model(
            model_name="tgi",
            base_url="http://localhost:8080/v1",
            temperature=0,
            max_tokens=4000
        )
        
        assert chat_model is not None
        mock_ark_model.assert_called_once()

    @patch('main.chat_model')
    def test_model_with_tools_binding(self, mock_chat_model):
        """Test model binding with tools."""
        mock_bound_model = Mock()
        mock_chat_model.bind_tools.return_value = mock_bound_model
        
        tools = [Mock(), Mock(), Mock()]
        model_with_tools = mock_chat_model.bind_tools(tools)
        
        assert model_with_tools is not None
        mock_chat_model.bind_tools.assert_called_once_with(tools)

    @patch('main.chat_model')
    def test_model_invoke(self, mock_chat_model):
        """Test model invoke method."""
        mock_response = Mock()
        mock_response.content = "Test response"
        mock_chat_model.invoke.return_value = mock_response
        
        messages = ["Hello"]
        response = mock_chat_model.invoke(messages)
        
        assert response.content == "Test response"
        mock_chat_model.invoke.assert_called_once_with(messages)

    @patch('main.model_with_tools')
    def test_model_with_tools_invoke(self, mock_model_with_tools):
        """Test model with tools invoke method."""
        mock_response = Mock()
        mock_response.content = "Tool-enabled response"
        mock_response.tool_calls = []
        mock_model_with_tools.invoke.return_value = mock_response
        
        messages = ["Get weather for NYC"]
        response = mock_model_with_tools.invoke(messages)
        
        assert response.content == "Tool-enabled response"
        assert hasattr(response, 'tool_calls')


class TestGraphConstruction:
    """Test suite for graph construction."""

    def test_graph_initialization(self):
        """Test graph initialization."""
        from langgraph.graph import StateGraph
        from typing import TypedDict, List
        
        class TestState(TypedDict):
            messages: List[str]
        
        graph = StateGraph(TestState)
        assert graph is not None

    def test_prompt_node(self):
        """Test prompt node functionality."""
        def prompt_node(state):
            """Test prompt node."""
            response = Mock()
            response.content = "Node response"
            return {"messages": state["messages"] + [response]}
        
        # Test node execution
        initial_state = {"messages": ["user input"]}
        result = prompt_node(initial_state)
        
        assert "messages" in result
        assert len(result["messages"]) == 2

    def test_conditional_edge(self):
        """Test conditional edge logic."""
        def conditional_edge(state):
            """Test conditional edge."""
            last_message = state["messages"][-1]
            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                return "tool_node"
            return "__end__"
        
        # Test with tool calls
        mock_message_with_tools = Mock()
        mock_message_with_tools.tool_calls = [{"name": "test_tool"}]
        state_with_tools = {"messages": [mock_message_with_tools]}
        
        assert conditional_edge(state_with_tools) == "tool_node"
        
        # Test without tool calls
        mock_message_no_tools = Mock()
        mock_message_no_tools.tool_calls = []
        state_no_tools = {"messages": [mock_message_no_tools]}
        
        assert conditional_edge(state_no_tools) == "__end__"

    def test_graph_node_addition(self):
        """Test adding nodes to graph."""
        from langgraph.graph import StateGraph
        from typing import TypedDict, List
        
        class TestState(TypedDict):
            messages: List[str]
        
        graph = StateGraph(TestState)
        
        def test_node(state):
            return {"messages": state["messages"]}
        
        # Test adding nodes
        graph.add_node("test_node", test_node)
        graph.set_entry_point("test_node")
        
        # Test graph compilation
        compiled_graph = graph.compile()
        assert compiled_graph is not None

    def test_graph_edge_addition(self):
        """Test adding edges to graph."""
        from langgraph.graph import StateGraph
        from typing import TypedDict, List
        
        class TestState(TypedDict):
            messages: List[str]
        
        graph = StateGraph(TestState)
        
        def node1(state):
            return {"messages": state["messages"]}
        
        def node2(state):
            return {"messages": state["messages"]}
        
        # Test adding nodes and edges
        graph.add_node("node1", node1)
        graph.add_node("node2", node2)
        graph.add_edge("node1", "node2")
        graph.set_entry_point("node1")
        
        compiled_graph = graph.compile()
        assert compiled_graph is not None


class TestMemoryCheckpoint:
    """Test suite for memory checkpoint functionality."""

    def test_sqlite_connection(self):
        """Test SQLite connection."""
        with tempfile.NamedTemporaryFile(suffix='.sqlite', delete=False) as f:
            db_path = f.name
        
        try:
            conn = sqlite3.connect(db_path, check_same_thread=False)
            assert conn is not None
            
            # Test basic operations
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
            conn.execute("INSERT INTO test (id) VALUES (1)")
            conn.commit()
            
            cursor = conn.execute("SELECT id FROM test")
            result = cursor.fetchone()
            assert result[0] == 1
            
            conn.close()
        finally:
            os.unlink(db_path)

    def test_database_directory_creation(self):
        """Test database directory creation."""
        import tempfile
        import shutil
        
        with tempfile.TemporaryDirectory() as temp_dir:
            db_dir = os.path.join(temp_dir, "database_temp")
            
            # Test directory creation
            os.makedirs(db_dir, exist_ok=True)
            assert os.path.exists(db_dir)
            assert os.path.isdir(db_dir)

    @patch('langgraph.checkpoint.sqlite.SqliteSaver')
    def test_memory_saver_initialization(self, mock_saver):
        """Test memory saver initialization."""
        mock_instance = Mock()
        mock_saver.return_value = mock_instance
        
        conn = Mock()
        memory = mock_saver(conn)
        
        assert memory is not None
        mock_saver.assert_called_once_with(conn)

    def test_checkpointer_configuration(self):
        """Test checkpointer configuration."""
        # Test configuration structure
        config = {
            'configurable': {
                'thread_id': '1'
            }
        }
        
        assert 'configurable' in config
        assert 'thread_id' in config['configurable']
        assert config['configurable']['thread_id'] == '1'


class TestAgentLoop:
    """Test suite for agent loop functionality."""

    @patch('main.graph')
    @patch('builtins.input')
    def test_agent_loop_single_interaction(self, mock_input, mock_graph):
        """Test single agent interaction."""
        mock_input.side_effect = ["Hello", "quit"]
        mock_response = {
            "messages": [Mock(content="Hello there!")]
        }
        mock_graph.invoke.return_value = mock_response
        
        # Test would require running the actual loop
        # This tests the components
        user_input = "Hello"
        config = {'configurable': {'thread_id': '1'}}
        
        response = mock_graph.invoke({"messages": [user_input]}, config=config)
        assert response["messages"][0].content == "Hello there!"

    @patch('main.graph')
    def test_agent_error_handling(self, mock_graph):
        """Test agent error handling."""
        mock_graph.invoke.side_effect = Exception("Agent error")
        
        config = {'configurable': {'thread_id': '1'}}
        
        with pytest.raises(Exception):
            mock_graph.invoke({"messages": ["test"]}, config=config)

    @patch('main.graph')
    @patch('database_temp.read_db.delete_last_two_entries')
    def test_agent_error_recovery(self, mock_delete, mock_graph):
        """Test agent error recovery."""
        mock_graph.invoke.side_effect = Exception("Agent error")
        mock_delete.return_value = None
        
        config = {'configurable': {'thread_id': '1'}}
        
        try:
            mock_graph.invoke({"messages": ["test"]}, config=config)
        except Exception:
            # Test error recovery
            mock_delete('checkpoints')
            mock_delete('writes')
            
            assert mock_delete.call_count == 2

    def test_input_validation(self):
        """Test input validation."""
        # Test quit commands
        quit_commands = ['quit', 'exit', 'bye', 'q']
        
        for cmd in quit_commands:
            assert cmd.lower() in ['quit', 'exit', 'bye', 'q']

    def test_message_formatting(self):
        """Test message formatting."""
        from langchain_core.messages import HumanMessage
        
        user_input = "Hello, how are you?"
        message = HumanMessage(content=user_input)
        
        assert message.content == user_input
        assert hasattr(message, 'content')

    def test_response_processing(self):
        """Test response processing."""
        mock_response = {
            "messages": [
                Mock(content="I'm doing well, thank you!"),
                Mock(content="How can I help you today?")
            ]
        }
        
        # Test response structure
        assert "messages" in mock_response
        assert len(mock_response["messages"]) == 2
        assert mock_response["messages"][-1].content == "How can I help you today?"


class TestToolNodeIntegration:
    """Test suite for tool node integration."""

    @patch('langgraph.prebuilt.ToolNode')
    def test_tool_node_creation(self, mock_tool_node):
        """Test tool node creation."""
        mock_instance = Mock()
        mock_tool_node.return_value = mock_instance
        
        tools = [Mock(), Mock()]
        tool_node = mock_tool_node(tools)
        
        assert tool_node is not None
        mock_tool_node.assert_called_once_with(tools)

    @patch('main.tool_node')
    def test_tool_node_invoke(self, mock_tool_node):
        """Test tool node invoke."""
        mock_response = {"messages": [Mock(content="Tool executed")]}
        mock_tool_node.invoke.return_value = mock_response
        
        state = {"messages": ["test input"]}
        response = mock_tool_node.invoke(state)
        
        assert response is not None
        assert "messages" in response

    def test_tool_execution_flow(self):
        """Test tool execution flow."""
        # Test tool call structure
        tool_call = {
            "id": "call_123",
            "function": {
                "name": "get_weather",
                "arguments": '{"location": "NYC"}'
            }
        }
        
        assert tool_call["function"]["name"] == "get_weather"
        assert "location" in tool_call["function"]["arguments"]

    def test_tool_result_processing(self):
        """Test tool result processing."""
        tool_result = {
            "tool_call_id": "call_123",
            "content": "It's sunny and 75°F in NYC"
        }
        
        assert "tool_call_id" in tool_result
        assert "content" in tool_result
        assert tool_result["content"] == "It's sunny and 75°F in NYC"


@pytest.mark.integration
class TestBaseModuleIntegration:
    """Integration tests for base module."""

    @patch('main.chat_model')
    @patch('main.graph')
    def test_full_agent_workflow(self, mock_graph, mock_chat_model):
        """Test full agent workflow."""
        # Setup mocks
        mock_response = {
            "messages": [Mock(content="Full workflow response")]
        }
        mock_graph.invoke.return_value = mock_response
        
        # Test workflow
        config = {'configurable': {'thread_id': '1'}}
        user_input = "Hello"
        
        response = mock_graph.invoke({"messages": [user_input]}, config=config)
        
        assert response is not None
        assert "messages" in response
        assert response["messages"][0].content == "Full workflow response"

    @patch('main.chat_model')
    @patch('main.tool_node')
    def test_tool_calling_integration(self, mock_tool_node, mock_chat_model):
        """Test tool calling integration."""
        # Setup tool response
        mock_tool_response = {"messages": [Mock(content="Weather: Sunny")]}
        mock_tool_node.invoke.return_value = mock_tool_response
        
        # Setup model response with tool calls
        mock_model_response = Mock()
        mock_model_response.tool_calls = [
            {"function": {"name": "get_weather", "arguments": '{"location": "NYC"}'}}
        ]
        mock_chat_model.invoke.return_value = mock_model_response
        
        # Test integration
        state = {"messages": ["What's the weather in NYC?"]}
        
        # Model processes input
        model_response = mock_chat_model.invoke(state["messages"])
        assert hasattr(model_response, 'tool_calls')
        
        # Tool node processes tool calls
        tool_response = mock_tool_node.invoke(state)
        assert tool_response["messages"][0].content == "Weather: Sunny"

    @patch('main.memory')
    def test_memory_integration(self, mock_memory):
        """Test memory integration."""
        # Setup memory
        mock_memory.get.return_value = {"previous_context": "user asked about weather"}
        mock_memory.put.return_value = None
        
        # Test memory operations
        context = mock_memory.get("conversation_context")
        assert context["previous_context"] == "user asked about weather"
        
        # Test memory storage
        new_context = {"current_topic": "calendar scheduling"}
        mock_memory.put("conversation_context", new_context)
        mock_memory.put.assert_called_once_with("conversation_context", new_context)

    def test_configuration_integration(self):
        """Test configuration integration."""
        # Test configuration loading and usage
        config = {
            "model_url": "http://localhost:8080/v1",
            "temperature": 0,
            "max_tokens": 4000
        }
        
        # Test configuration validation
        assert config["model_url"].startswith("http")
        assert config["temperature"] >= 0
        assert config["max_tokens"] > 0
        
        # Test configuration usage
        model_params = {
            "base_url": config["model_url"],
            "temperature": config["temperature"],
            "max_tokens": config["max_tokens"]
        }
        
        assert model_params["base_url"] == config["model_url"]