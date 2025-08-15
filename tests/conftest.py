import pytest
import asyncio
import tempfile
import os
import sqlite3
import yaml
from datetime import datetime, date
from typing import Dict, Any
from unittest.mock import Mock, MagicMock, patch
import sys

# Optional imports for FastAPI testing - only import if available
try:
    from fastapi.testclient import TestClient
    from httpx import AsyncClient
    FASTAPI_AVAILABLE = True
except ImportError:
    TestClient = None
    AsyncClient = None
    FASTAPI_AVAILABLE = False

# Add project modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'model_module'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'base_module'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'calendar_module'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'state_module'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agent_module'))

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def temp_db():
    """Create a temporary SQLite database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.sqlite', delete=False) as f:
        db_path = f.name
    
    conn = sqlite3.connect(db_path)
    yield conn
    conn.close()
    os.unlink(db_path)

@pytest.fixture
def sample_event_data():
    """Sample event data for testing."""
    return {
        "title": "Test Meeting",
        "description": "A test meeting for unit tests",
        "start_time": datetime(2024, 1, 15, 10, 0),
        "end_time": datetime(2024, 1, 15, 11, 0)
    }

@pytest.fixture
def sample_events_list():
    """Sample list of events for testing."""
    return [
        {
            "id": "event-1",
            "title": "Morning Meeting",
            "description": "Daily standup",
            "start_time": datetime(2024, 1, 15, 9, 0),
            "end_time": datetime(2024, 1, 15, 9, 30),
            "created_at": datetime(2024, 1, 14, 12, 0),
            "updated_at": datetime(2024, 1, 14, 12, 0)
        },
        {
            "id": "event-2",
            "title": "Afternoon Review",
            "description": "Code review session",
            "start_time": datetime(2024, 1, 15, 14, 0),
            "end_time": datetime(2024, 1, 15, 15, 0),
            "created_at": datetime(2024, 1, 14, 12, 0),
            "updated_at": datetime(2024, 1, 14, 12, 0)
        }
    ]

@pytest.fixture
def sample_chat_message():
    """Sample chat message for testing."""
    return {
        "message": "Schedule a meeting for tomorrow at 2pm"
    }

@pytest.fixture
def sample_chat_response():
    """Sample chat response for testing."""
    return {
        "response": "I'll help you schedule a meeting for tomorrow at 2pm.",
        "action": "create_event",
        "data": {"action": "create_event"}
    }

@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    return {
        "model_path": "/fake/path/to/model.gguf",
        "base_prompt": "Test base prompt",
        "endpoint_type": "OpenAI",
        "model_url": "http://localhost:8080/v1"
    }

@pytest.fixture
def temp_config_file(mock_config):
    """Create a temporary config file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(mock_config, f)
        config_path = f.name
    
    yield config_path
    os.unlink(config_path)

@pytest.fixture
def mock_fastapi_app():
    """Create a mock FastAPI app for testing."""
    if not FASTAPI_AVAILABLE:
        pytest.skip("FastAPI not available")
    
    # Import here to avoid circular imports
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'depricated', 'backend'))
    try:
        from main import app
        return app
    except ImportError:
        # If the deprecated backend main.py doesn't exist, create a minimal FastAPI app
        from fastapi import FastAPI
        app = FastAPI()
        
        @app.get("/")
        async def root():
            return {"message": "Test API"}
        
        return app

@pytest.fixture
def fastapi_client(mock_fastapi_app):
    """Create a FastAPI test client."""
    if not FASTAPI_AVAILABLE:
        pytest.skip("FastAPI not available")
    
    with TestClient(mock_fastapi_app) as client:
        yield client

@pytest.fixture
async def async_fastapi_client(mock_fastapi_app):
    """Create an async FastAPI test client."""
    if not FASTAPI_AVAILABLE:
        pytest.skip("FastAPI not available")
    
    async with AsyncClient(app=mock_fastapi_app, base_url="http://test") as client:
        yield client

@pytest.fixture
def mock_user():
    """Mock user data for testing."""
    return {
        "id": "test_user",
        "username": "testuser",
        "email": "test@example.com",
        "events": []
    }

@pytest.fixture
def mock_events_db():
    """Mock events database for testing."""
    return {}

@pytest.fixture
def mock_users_db(mock_user):
    """Mock users database for testing."""
    return {
        "test_user": mock_user
    }

@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing."""
    return {
        "choices": [
            {
                "message": {
                    "content": "This is a test response from the LLM.",
                    "role": "assistant"
                },
                "finish_reason": "stop"
            }
        ]
    }

@pytest.fixture
def mock_llm_stream_response():
    """Mock LLM streaming response for testing."""
    return [
        {"choices": [{"delta": {"content": "This "}}]},
        {"choices": [{"delta": {"content": "is "}}]},
        {"choices": [{"delta": {"content": "a "}}]},
        {"choices": [{"delta": {"content": "test"}}]},
        {"choices": [{"delta": {"content": "."}}]},
        {"choices": [{"finish_reason": "stop"}]}
    ]

@pytest.fixture
def mock_tool_call_response():
    """Mock LLM response with tool calls for testing."""
    return {
        "choices": [
            {
                "message": {
                    "content": None,
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": "call_123",
                            "type": "function",
                            "function": {
                                "name": "get_weather",
                                "arguments": '{"location": "New York"}'
                            }
                        }
                    ]
                },
                "finish_reason": "tool_calls"
            }
        ]
    }

@pytest.fixture
def mock_weather_tool_result():
    """Mock weather tool execution result."""
    return "It's cold and wet."

@pytest.fixture
def mock_http_client():
    """Mock HTTP client for testing external API calls."""
    mock_client = Mock()
    mock_client.post = Mock()
    mock_client.get = Mock()
    return mock_client

@pytest.fixture
def mock_ark_model():
    """Mock ArkModelLink for testing."""
    mock_model = Mock()
    mock_model.invoke = Mock()
    mock_model.bind_tools = Mock(return_value=mock_model)
    return mock_model

@pytest.fixture
def mock_langgraph_state():
    """Mock LangGraph state for testing."""
    return {
        "messages": []
    }

@pytest.fixture
def mock_memory_saver():
    """Mock memory saver for testing."""
    mock_saver = Mock()
    mock_saver.get = Mock()
    mock_saver.put = Mock()
    return mock_saver

@pytest.fixture
def mock_calendar_manager():
    """Mock calendar manager for testing."""
    mock_manager = Mock()
    mock_manager.create_event = Mock()
    mock_manager.list_events = Mock()
    mock_manager.get_event = Mock()
    mock_manager.update_event = Mock()
    mock_manager.delete_event = Mock()
    return mock_manager

@pytest.fixture
def mock_mcp_client():
    """Mock MCP client for testing."""
    mock_client = Mock()
    mock_client.connect = Mock()
    mock_client.disconnect = Mock()
    mock_client.call_tool = Mock()
    mock_client.list_tools = Mock()
    return mock_client

@pytest.fixture
def mock_radicale_server():
    """Mock Radicale server for testing."""
    mock_server = Mock()
    mock_server.create_calendar = Mock()
    mock_server.create_event = Mock()
    mock_server.list_events = Mock()
    mock_server.update_event = Mock()
    mock_server.delete_event = Mock()
    return mock_server

@pytest.fixture
def cleanup_test_files():
    """Clean up test files after testing."""
    test_files = []
    
    def add_file(filepath):
        test_files.append(filepath)
    
    yield add_file
    
    # Cleanup
    for filepath in test_files:
        try:
            if os.path.exists(filepath):
                os.unlink(filepath)
        except:
            pass

@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Set up test environment variables."""
    monkeypatch.setenv("TESTING", "true")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    
    # Mock external dependencies
    with patch('openai.OpenAI') as mock_openai:
        mock_openai.return_value.chat.completions.create.return_value = Mock()
        yield

@pytest.fixture
def sample_date_range():
    """Sample date range for testing."""
    return {
        "start_date": date(2024, 1, 15),
        "end_date": date(2024, 1, 17)
    }

@pytest.fixture
def mock_datetime():
    """Mock datetime for consistent testing."""
    with patch('datetime.datetime') as mock_dt:
        mock_dt.now.return_value = datetime(2024, 1, 15, 12, 0, 0)
        mock_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
        yield mock_dt

@pytest.fixture
def mock_uuid():
    """Mock UUID for consistent testing."""
    with patch('uuid.uuid4') as mock_uuid:
        mock_uuid.return_value.hex = "test-uuid-123"
        mock_uuid.return_value.__str__ = lambda self: "test-uuid-123"
        yield mock_uuid

# Module-specific fixtures for new test implementation

@pytest.fixture
def mock_yaml_config():
    """Valid YAML configuration for testing."""
    return {
        "initial": "test_user",
        "states": {
            "test_user": {
                "type": "user",
                "transition": {"next": "test_agent"}
            },
            "test_agent": {
                "type": "agent", 
                "transition": {"next": "test_user"}
            }
        }
    }

@pytest.fixture
def mock_invalid_yaml_config():
    """Invalid YAML configuration for error testing."""
    return {
        "initial": "nonexistent_state",
        "states": {
            "test_state": {
                "type": "invalid_type",
                "transition": {"next": "another_nonexistent"}
            }
        }
    }

@pytest.fixture
def test_yaml_config_file(tmp_path):
    """Create temporary YAML config file for testing."""
    config_data = {
        "initial": "test_user",
        "states": {
            "test_user": {
                "type": "user",
                "transition": {"next": "test_agent"}
            },
            "test_agent": {
                "type": "agent",
                "transition": {"next": "test_user"}
            }
        }
    }
    config_file = tmp_path / "test_config.yaml"
    with open(config_file, 'w') as f:
        yaml.dump(config_data, f)
    return str(config_file)

@pytest.fixture
def invalid_yaml_config_file(tmp_path):
    """Create temporary invalid YAML config file for testing."""
    config_data = {
        "initial": "nonexistent_state",
        "states": {
            "test_state": {
                "type": "invalid_type",
                "transition": {"next": "another_nonexistent"}
            }
        }
    }
    config_file = tmp_path / "invalid_config.yaml"
    with open(config_file, 'w') as f:
        yaml.dump(config_data, f)
    return str(config_file)

@pytest.fixture
def mock_state_handler():
    """Mock StateHandler instance."""
    mock_handler = Mock()
    mock_handler.get_initial_state = Mock()
    mock_handler.get_next_state = Mock()
    mock_handler.states = {}
    return mock_handler

@pytest.fixture
def mock_memory():
    """Mock Memory instance."""
    mock_mem = Mock()
    mock_mem.get = Mock()
    mock_mem.set = Mock()
    return mock_mem

@pytest.fixture
def mock_agent():
    """Mock Agent instance."""
    mock_agent = Mock()
    mock_agent.step = Mock()
    mock_agent.bind_tool = Mock()
    mock_agent.call_llm = Mock()
    return mock_agent

@pytest.fixture
def mock_tool():
    """Mock Tool instance."""
    mock_tool = Mock()
    mock_tool.tool = "test_tool"
    mock_tool.name = "test_tool"
    return mock_tool

@pytest.fixture
def mock_user_message():
    """Mock UserMessage instance."""
    mock_msg = Mock()
    mock_msg.content = "Test user input"
    mock_msg.role = "user"
    return mock_msg

@pytest.fixture
def mock_ai_message():
    """Mock AIMessage instance."""
    mock_msg = Mock()
    mock_msg.content = "Test AI response"
    mock_msg.role = "assistant"
    return mock_msg

@pytest.fixture
def mock_system_message():
    """Mock SystemMessage instance."""
    mock_msg = Mock()
    mock_msg.content = "Test system message"
    mock_msg.role = "system"
    return mock_msg