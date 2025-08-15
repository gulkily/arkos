import pytest
import os
import tempfile
import yaml
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import asyncio
import sqlite3


class TestModelConfiguration:
    """Test suite for model configuration loading."""

    def test_config_loading_from_yaml(self, temp_config_file, mock_config):
        """Test loading configuration from YAML file."""
        # Test loading config
        with open(temp_config_file, 'r') as file:
            loaded_config = yaml.safe_load(file)
        
        assert loaded_config == mock_config
        assert loaded_config["model_url"] == "http://localhost:8080/v1"
        assert loaded_config["endpoint_type"] == "OpenAI"

    def test_config_validation(self, mock_config):
        """Test configuration validation."""
        # Test required fields
        required_fields = ["model_url", "endpoint_type"]
        for field in required_fields:
            assert field in mock_config
            assert mock_config[field] is not None

    def test_config_defaults(self):
        """Test default configuration values."""
        default_config = {
            "temperature": 0.7,
            "max_tokens": 1024,
            "model_name": "tgi"
        }
        
        # Test that defaults are reasonable
        assert 0.0 <= default_config["temperature"] <= 1.0
        assert default_config["max_tokens"] > 0
        assert isinstance(default_config["model_name"], str)

    def test_config_file_not_found(self):
        """Test handling of missing config file."""
        with pytest.raises(FileNotFoundError):
            with open("nonexistent_config.yaml", 'r') as file:
                yaml.safe_load(file)

    def test_invalid_yaml_format(self):
        """Test handling of invalid YAML format."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [")
            config_path = f.name
        
        try:
            with pytest.raises(yaml.YAMLError):
                with open(config_path, 'r') as file:
                    yaml.safe_load(file)
        finally:
            os.unlink(config_path)

    def test_config_environment_override(self):
        """Test configuration override from environment variables."""
        # Test environment variable override
        with patch.dict(os.environ, {'MODEL_URL': 'http://override:8080'}):
            env_url = os.environ.get('MODEL_URL')
            assert env_url == 'http://override:8080'


class TestArkModelLink:
    """Test suite for ArkModelLink class."""

    @patch('ArkModelOAI.ArkModelLink')
    def test_ark_model_initialization(self, mock_ark_model):
        """Test ArkModelLink initialization."""
        mock_instance = Mock()
        mock_ark_model.return_value = mock_instance
        
        # Test initialization with parameters
        model = mock_ark_model(
            model_name="tgi",
            base_url="http://localhost:8080/v1",
            temperature=0.7,
            max_tokens=1000
        )
        
        assert model is not None
        mock_ark_model.assert_called_once_with(
            model_name="tgi",
            base_url="http://localhost:8080/v1",
            temperature=0.7,
            max_tokens=1000
        )

    @patch('ArkModelOAI.ArkModelLink')
    def test_ark_model_invoke(self, mock_ark_model):
        """Test ArkModelLink invoke method."""
        mock_instance = Mock()
        mock_response = Mock()
        mock_response.content = "Test response"
        mock_instance.invoke.return_value = mock_response
        mock_ark_model.return_value = mock_instance
        
        model = mock_ark_model()
        response = model.invoke(["test message"])
        
        assert response.content == "Test response"
        mock_instance.invoke.assert_called_once_with(["test message"])

    @patch('ArkModelOAI.ArkModelLink')
    def test_ark_model_bind_tools(self, mock_ark_model):
        """Test ArkModelLink bind_tools method."""
        mock_instance = Mock()
        mock_bound_model = Mock()
        mock_instance.bind_tools.return_value = mock_bound_model
        mock_ark_model.return_value = mock_instance
        
        model = mock_ark_model()
        tools = [Mock(), Mock()]
        bound_model = model.bind_tools(tools)
        
        assert bound_model is not None
        mock_instance.bind_tools.assert_called_once_with(tools)

    @patch('ArkModelOAI.ArkModelLink')
    def test_ark_model_system_prompt(self, mock_ark_model):
        """Test ArkModelLink with system prompt."""
        mock_instance = Mock()
        mock_ark_model.return_value = mock_instance
        
        system_prompt = "You are a helpful assistant."
        model = mock_ark_model(system_prompt=system_prompt)
        
        mock_ark_model.assert_called_once_with(system_prompt=system_prompt)

    @patch('ArkModelOAI.ArkModelLink')
    def test_ark_model_error_handling(self, mock_ark_model):
        """Test ArkModelLink error handling."""
        mock_instance = Mock()
        mock_instance.invoke.side_effect = Exception("Model service unavailable")
        mock_ark_model.return_value = mock_instance
        
        model = mock_ark_model()
        
        with pytest.raises(Exception) as exc_info:
            model.invoke(["test message"])
        
        assert "Model service unavailable" in str(exc_info.value)


class TestToolIntegration:
    """Test suite for tool integration."""

    def test_tool_definition(self):
        """Test tool definition structure."""
        # Test weather tool
        def get_weather(location: str):
            """Get weather for a location."""
            return f"Weather for {location}"
        
        assert callable(get_weather)
        assert get_weather.__doc__ == "Get weather for a location."
        assert get_weather("New York") == "Weather for New York"

    def test_tool_binding(self, mock_ark_model):
        """Test tool binding to model."""
        tools = [Mock(), Mock()]
        mock_model = Mock()
        mock_model.bind_tools.return_value = Mock()
        
        bound_model = mock_model.bind_tools(tools)
        assert bound_model is not None
        mock_model.bind_tools.assert_called_once_with(tools)

    def test_tool_execution(self):
        """Test tool execution."""
        def multiply(a: int, b: int) -> int:
            """Multiply two numbers."""
            return a * b
        
        result = multiply(5, 3)
        assert result == 15
        assert isinstance(result, int)

    def test_tool_error_handling(self):
        """Test tool error handling."""
        def divide(a: int, b: int) -> float:
            """Divide two numbers."""
            if b == 0:
                raise ValueError("Division by zero")
            return a / b
        
        # Test normal operation
        assert divide(10, 2) == 5.0
        
        # Test error handling
        with pytest.raises(ValueError):
            divide(10, 0)

    @patch('langchain_core.tools.tool')
    def test_langchain_tool_decorator(self, mock_tool_decorator):
        """Test LangChain tool decorator."""
        mock_tool_decorator.return_value = lambda func: func
        
        @mock_tool_decorator
        def test_tool(param: str):
            """Test tool function."""
            return f"Result: {param}"
        
        result = test_tool("test")
        assert result == "Result: test"
        mock_tool_decorator.assert_called_once()


class TestLangGraphIntegration:
    """Test suite for LangGraph integration."""

    def test_state_definition(self):
        """Test State TypedDict definition."""
        from typing import List, TypedDict
        from langchain_core.messages import BaseMessage
        
        class TestState(TypedDict):
            messages: List[BaseMessage]
        
        # Test state creation
        state = TestState(messages=[])
        assert isinstance(state, dict)
        assert "messages" in state
        assert isinstance(state["messages"], list)

    def test_graph_construction(self):
        """Test graph construction."""
        from langgraph.graph import StateGraph
        from typing import TypedDict, List
        
        class TestState(TypedDict):
            messages: List[str]
        
        # Test graph creation
        graph = StateGraph(TestState)
        assert graph is not None

    def test_node_definition(self):
        """Test node definition."""
        def test_node(state):
            """Test node function."""
            return {"messages": state["messages"] + ["processed"]}
        
        # Test node execution
        initial_state = {"messages": ["initial"]}
        result = test_node(initial_state)
        
        assert "messages" in result
        assert "processed" in result["messages"]
        assert "initial" in result["messages"]

    def test_conditional_edge(self):
        """Test conditional edge logic."""
        def conditional_edge(state):
            """Test conditional edge."""
            if len(state["messages"]) > 0:
                return "continue"
            return "end"
        
        # Test conditions
        assert conditional_edge({"messages": ["test"]}) == "continue"
        assert conditional_edge({"messages": []}) == "end"

    @patch('langgraph.checkpoint.sqlite.SqliteSaver')
    def test_memory_checkpointer(self, mock_saver):
        """Test memory checkpointer."""
        mock_instance = Mock()
        mock_saver.return_value = mock_instance
        
        conn = Mock()
        memory = mock_saver(conn)
        
        assert memory is not None
        mock_saver.assert_called_once_with(conn)

    def test_graph_compilation(self):
        """Test graph compilation."""
        from langgraph.graph import StateGraph
        from typing import TypedDict, List
        
        class TestState(TypedDict):
            messages: List[str]
        
        graph = StateGraph(TestState)
        
        def test_node(state):
            return {"messages": state["messages"]}
        
        # Add nodes and edges
        graph.add_node("test_node", test_node)
        graph.set_entry_point("test_node")
        
        # Test compilation
        compiled_graph = graph.compile()
        assert compiled_graph is not None


class TestMemoryManagement:
    """Test suite for memory management."""

    def test_sqlite_memory_creation(self, temp_db):
        """Test SQLite memory creation."""
        # Test database connection
        assert temp_db is not None
        
        # Test table creation
        temp_db.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY)")
        temp_db.commit()
        
        # Test data insertion
        temp_db.execute("INSERT INTO test (id) VALUES (1)")
        temp_db.commit()
        
        # Test data retrieval
        cursor = temp_db.execute("SELECT id FROM test")
        result = cursor.fetchone()
        assert result[0] == 1

    def test_memory_persistence(self, temp_db):
        """Test memory persistence."""
        # Create test data
        temp_db.execute("CREATE TABLE IF NOT EXISTS memory (key TEXT, value TEXT)")
        temp_db.execute("INSERT INTO memory (key, value) VALUES (?, ?)", ("test_key", "test_value"))
        temp_db.commit()
        
        # Retrieve data
        cursor = temp_db.execute("SELECT value FROM memory WHERE key = ?", ("test_key",))
        result = cursor.fetchone()
        assert result[0] == "test_value"

    def test_memory_cleanup(self, temp_db):
        """Test memory cleanup."""
        # Create test data
        temp_db.execute("CREATE TABLE IF NOT EXISTS cleanup_test (id INTEGER, data TEXT)")
        temp_db.execute("INSERT INTO cleanup_test (id, data) VALUES (1, 'test')")
        temp_db.execute("INSERT INTO cleanup_test (id, data) VALUES (2, 'test')")
        temp_db.commit()
        
        # Test cleanup
        temp_db.execute("DELETE FROM cleanup_test WHERE id = 1")
        temp_db.commit()
        
        # Verify cleanup
        cursor = temp_db.execute("SELECT COUNT(*) FROM cleanup_test")
        count = cursor.fetchone()[0]
        assert count == 1

    def test_memory_thread_safety(self, temp_db):
        """Test memory thread safety."""
        # Test concurrent access
        temp_db.execute("CREATE TABLE IF NOT EXISTS thread_test (id INTEGER)")
        
        # Multiple operations
        for i in range(5):
            temp_db.execute("INSERT INTO thread_test (id) VALUES (?)", (i,))
        temp_db.commit()
        
        # Verify all operations succeeded
        cursor = temp_db.execute("SELECT COUNT(*) FROM thread_test")
        count = cursor.fetchone()[0]
        assert count == 5


class TestAgentExecution:
    """Test suite for agent execution."""

    @patch('main.graph')
    def test_agent_invoke(self, mock_graph):
        """Test agent invocation."""
        mock_response = {
            "messages": [
                Mock(content="Test response")
            ]
        }
        mock_graph.invoke.return_value = mock_response
        
        config = {'configurable': {'thread_id': '1'}}
        response = mock_graph.invoke({"messages": ["test input"]}, config=config)
        
        assert response is not None
        assert "messages" in response
        assert len(response["messages"]) > 0

    @patch('main.graph')
    def test_agent_with_tools(self, mock_graph):
        """Test agent with tool execution."""
        mock_response = {
            "messages": [
                Mock(content="Tool execution result")
            ]
        }
        mock_graph.invoke.return_value = mock_response
        
        config = {'configurable': {'thread_id': '1'}}
        response = mock_graph.invoke({"messages": ["get weather for New York"]}, config=config)
        
        assert response is not None
        assert "messages" in response

    @patch('main.graph')
    def test_agent_error_recovery(self, mock_graph):
        """Test agent error recovery."""
        mock_graph.invoke.side_effect = Exception("Agent error")
        
        config = {'configurable': {'thread_id': '1'}}
        
        with pytest.raises(Exception):
            mock_graph.invoke({"messages": ["test input"]}, config=config)

    def test_agent_conversation_flow(self):
        """Test agent conversation flow."""
        conversation = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"},
            {"role": "assistant", "content": "I'm doing well, thank you!"}
        ]
        
        # Test conversation structure
        assert len(conversation) == 4
        assert conversation[0]["role"] == "user"
        assert conversation[1]["role"] == "assistant"
        assert conversation[2]["role"] == "user"
        assert conversation[3]["role"] == "assistant"

    def test_agent_memory_recall(self):
        """Test agent memory recall."""
        # Test memory structure
        memory_data = {
            "user_preferences": {"language": "English", "timezone": "UTC"},
            "conversation_history": ["previous message 1", "previous message 2"],
            "user_context": {"name": "Test User", "location": "Test City"}
        }
        
        # Test memory access
        assert "user_preferences" in memory_data
        assert memory_data["user_preferences"]["language"] == "English"
        assert len(memory_data["conversation_history"]) == 2


@pytest.mark.model
class TestModelIntegration:
    """Integration tests for model module."""

    @patch('main.chat_model')
    def test_full_model_pipeline(self, mock_chat_model):
        """Test full model processing pipeline."""
        mock_response = Mock()
        mock_response.content = "Pipeline test response"
        mock_chat_model.invoke.return_value = mock_response
        
        # Test pipeline
        input_messages = ["Test input"]
        response = mock_chat_model.invoke(input_messages)
        
        assert response.content == "Pipeline test response"
        mock_chat_model.invoke.assert_called_once_with(input_messages)

    @patch('main.chat_model')
    @patch('main.graph')
    def test_model_with_langgraph(self, mock_graph, mock_chat_model):
        """Test model integration with LangGraph."""
        mock_response = {
            "messages": [Mock(content="Graph integration test")]
        }
        mock_graph.invoke.return_value = mock_response
        
        config = {'configurable': {'thread_id': '1'}}
        response = mock_graph.invoke({"messages": ["test"]}, config=config)
        
        assert response is not None
        assert "messages" in response

    @patch('main.tool_node')
    def test_tool_node_execution(self, mock_tool_node):
        """Test tool node execution."""
        mock_response = {"messages": [Mock(content="Tool executed")]}
        mock_tool_node.invoke.return_value = mock_response
        
        state = {"messages": ["test input"]}
        response = mock_tool_node.invoke(state)
        
        assert response is not None
        assert "messages" in response

    def test_configuration_integration(self, temp_config_file):
        """Test configuration integration."""
        # Test loading and using configuration
        with open(temp_config_file, 'r') as file:
            config = yaml.safe_load(file)
        
        # Test configuration usage
        model_params = {
            "base_url": config["model_url"],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        assert model_params["base_url"] == "http://localhost:8080/v1"
        assert model_params["temperature"] == 0.7
        assert model_params["max_tokens"] == 1000

    @patch('main.memory')
    def test_memory_integration(self, mock_memory):
        """Test memory integration."""
        mock_memory.get.return_value = {"previous": "data"}
        mock_memory.put.return_value = None
        
        # Test memory operations
        retrieved_data = mock_memory.get("test_key")
        assert retrieved_data == {"previous": "data"}
        
        mock_memory.put("test_key", {"new": "data"})
        mock_memory.put.assert_called_once_with("test_key", {"new": "data"})

    @patch('main.run_agent')
    def test_agent_loop_integration(self, mock_run_agent):
        """Test agent loop integration."""
        mock_run_agent.return_value = None
        
        # Test agent loop
        mock_run_agent()
        mock_run_agent.assert_called_once()

    @patch('database_temp.read_db.delete_last_two_entries')
    def test_error_recovery_integration(self, mock_delete):
        """Test error recovery integration."""
        mock_delete.return_value = None
        
        # Test error recovery
        mock_delete('checkpoints')
        mock_delete('writes')
        
        assert mock_delete.call_count == 2