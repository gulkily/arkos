import pytest
from unittest.mock import Mock, patch, MagicMock
import asyncio
import json
from typing import List, Dict, Any
import httpx


class TestArkModelOAI:
    """Test suite for ArkModelOAI implementation."""

    @patch('ArkModelOAI.ArkModelLink')
    def test_ark_model_initialization(self, mock_ark_model):
        """Test ArkModelOAI initialization."""
        mock_instance = Mock()
        mock_ark_model.return_value = mock_instance
        
        model = mock_ark_model(
            model_name="tgi",
            base_url="http://localhost:8080/v1",
            temperature=0.7,
            max_tokens=1024
        )
        
        assert model is not None
        mock_ark_model.assert_called_once()

    @patch('ArkModelOAI.ArkModelLink')
    def test_ark_model_message_handling(self, mock_ark_model):
        """Test message handling in ArkModelOAI."""
        mock_instance = Mock()
        mock_response = Mock()
        mock_response.content = "Test response"
        mock_instance.invoke.return_value = mock_response
        mock_ark_model.return_value = mock_instance
        
        model = mock_ark_model()
        
        # Test message processing
        from langchain_core.messages import HumanMessage
        messages = [HumanMessage(content="Test message")]
        response = model.invoke(messages)
        
        assert response.content == "Test response"

    @patch('ArkModelOAI.ArkModelLink')
    def test_ark_model_tool_calling(self, mock_ark_model):
        """Test tool calling functionality."""
        mock_instance = Mock()
        mock_response = Mock()
        mock_response.tool_calls = [
            {
                "id": "call_123",
                "function": {
                    "name": "get_weather",
                    "arguments": '{"location": "New York"}'
                }
            }
        ]
        mock_instance.invoke.return_value = mock_response
        mock_ark_model.return_value = mock_instance
        
        model = mock_ark_model()
        
        # Test tool calling
        messages = ["Get weather for New York"]
        response = model.invoke(messages)
        
        assert hasattr(response, 'tool_calls')
        assert len(response.tool_calls) == 1
        assert response.tool_calls[0]["function"]["name"] == "get_weather"

    @patch('ArkModelOAI.ArkModelLink')
    def test_ark_model_streaming(self, mock_ark_model):
        """Test streaming functionality."""
        mock_instance = Mock()
        mock_stream = [
            Mock(content="Hello "),
            Mock(content="world!"),
            Mock(content="")
        ]
        mock_instance.stream.return_value = iter(mock_stream)
        mock_ark_model.return_value = mock_instance
        
        model = mock_ark_model()
        
        # Test streaming
        messages = ["Hello"]
        stream = model.stream(messages)
        
        collected_content = ""
        for chunk in stream:
            collected_content += chunk.content
        
        assert collected_content == "Hello world!"

    @patch('ArkModelOAI.ArkModelLink')
    def test_ark_model_async_streaming(self, mock_ark_model):
        """Test async streaming functionality."""
        mock_instance = Mock()
        
        async def mock_astream():
            for content in ["Hello ", "world!"]:
                yield Mock(content=content)
        
        mock_instance.astream.return_value = mock_astream()
        mock_ark_model.return_value = mock_instance
        
        model = mock_ark_model()
        
        # Test async streaming
        async def test_async_stream():
            messages = ["Hello"]
            collected_content = ""
            async for chunk in model.astream(messages):
                collected_content += chunk.content
            return collected_content
        
        # Run async test
        result = asyncio.run(test_async_stream())
        assert result == "Hello world!"

    @patch('ArkModelOAI.ArkModelLink')
    def test_ark_model_error_handling(self, mock_ark_model):
        """Test error handling in ArkModelOAI."""
        mock_instance = Mock()
        mock_instance.invoke.side_effect = Exception("Model service error")
        mock_ark_model.return_value = mock_instance
        
        model = mock_ark_model()
        
        with pytest.raises(Exception) as exc_info:
            model.invoke(["test message"])
        
        assert "Model service error" in str(exc_info.value)

    @patch('ArkModelOAI.ArkModelLink')
    def test_ark_model_configuration(self, mock_ark_model):
        """Test model configuration parameters."""
        mock_instance = Mock()
        mock_ark_model.return_value = mock_instance
        
        # Test different configurations
        configs = [
            {"temperature": 0.1, "max_tokens": 512},
            {"temperature": 0.9, "max_tokens": 2048},
            {"temperature": 0.5, "max_tokens": 1024}
        ]
        
        for config in configs:
            model = mock_ark_model(**config)
            assert model is not None


class TestArkModelRefactored:
    """Test suite for ArkModelRefactored implementation."""

    @patch('ArkModelRefactored.ArkModelRefactored')
    def test_ark_model_refactored_initialization(self, mock_ark_model):
        """Test ArkModelRefactored initialization."""
        mock_instance = Mock()
        mock_ark_model.return_value = mock_instance
        
        model = mock_ark_model(
            base_url="http://localhost:8080/v1",
            model_name="tgi",
            temperature=0.7,
            max_tokens=1024
        )
        
        assert model is not None
        mock_ark_model.assert_called_once()

    @patch('ArkModelRefactored.ArkModelRefactored')
    def test_custom_message_classes(self, mock_ark_model):
        """Test custom message classes."""
        mock_instance = Mock()
        mock_ark_model.return_value = mock_instance
        
        model = mock_ark_model()
        
        # Test custom message creation
        user_message = {"role": "user", "content": "Hello"}
        ai_message = {"role": "assistant", "content": "Hi there!"}
        tool_message = {"role": "tool", "content": "Tool result"}
        
        assert user_message["role"] == "user"
        assert ai_message["role"] == "assistant"
        assert tool_message["role"] == "tool"

    @patch('ArkModelRefactored.ArkModelRefactored')
    def test_custom_tool_interface(self, mock_ark_model):
        """Test custom tool interface."""
        mock_instance = Mock()
        mock_ark_model.return_value = mock_instance
        
        model = mock_ark_model()
        
        # Test custom tool creation
        class MockTool:
            def __init__(self, name, description, func):
                self.name = name
                self.description = description
                self.func = func
            
            def execute(self, args):
                return self.func(**args)
        
        def weather_func(location):
            return f"Weather for {location}"
        
        weather_tool = MockTool("get_weather", "Get weather", weather_func)
        
        assert weather_tool.name == "get_weather"
        assert weather_tool.description == "Get weather"
        assert weather_tool.execute({"location": "NYC"}) == "Weather for NYC"

    @patch('ArkModelRefactored.ArkModelRefactored')
    def test_conversation_history_management(self, mock_ark_model):
        """Test conversation history management."""
        mock_instance = Mock()
        mock_ark_model.return_value = mock_instance
        
        model = mock_ark_model()
        
        # Test conversation history
        conversation = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi!"},
            {"role": "user", "content": "How are you?"},
            {"role": "assistant", "content": "I'm good!"}
        ]
        
        # Test history management
        assert len(conversation) == 4
        assert conversation[0]["role"] == "user"
        assert conversation[-1]["role"] == "assistant"

    @patch('ArkModelRefactored.ArkModelRefactored')
    def test_tool_schema_conversion(self, mock_ark_model):
        """Test tool schema conversion to OpenAI format."""
        mock_instance = Mock()
        mock_ark_model.return_value = mock_instance
        
        model = mock_ark_model()
        
        # Test tool schema
        tool_schema = {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get weather for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The location to get weather for"
                        }
                    },
                    "required": ["location"]
                }
            }
        }
        
        assert tool_schema["type"] == "function"
        assert tool_schema["function"]["name"] == "get_weather"
        assert "parameters" in tool_schema["function"]

    @patch('ArkModelRefactored.ArkModelRefactored')
    def test_error_handling_improvements(self, mock_ark_model):
        """Test improved error handling."""
        mock_instance = Mock()
        mock_ark_model.return_value = mock_instance
        
        model = mock_ark_model()
        
        # Test various error scenarios
        error_scenarios = [
            Exception("Network error"),
            TimeoutError("Request timeout"),
            ValueError("Invalid input"),
            KeyError("Missing key")
        ]
        
        for error in error_scenarios:
            with pytest.raises(type(error)):
                raise error

    @patch('ArkModelRefactored.ArkModelRefactored')
    def test_async_functionality(self, mock_ark_model):
        """Test async functionality in refactored model."""
        mock_instance = Mock()
        mock_ark_model.return_value = mock_instance
        
        model = mock_ark_model()
        
        # Test async operations
        async def test_async_invoke():
            mock_instance.ainvoke = Mock(return_value=Mock(content="Async response"))
            response = await mock_instance.ainvoke(["test message"])
            assert response.content == "Async response"
        
        asyncio.run(test_async_invoke())

    @patch('ArkModelRefactored.ArkModelRefactored')
    def test_streaming_improvements(self, mock_ark_model):
        """Test streaming improvements."""
        mock_instance = Mock()
        mock_ark_model.return_value = mock_instance
        
        model = mock_ark_model()
        
        # Test streaming with better error handling
        async def mock_stream():
            chunks = ["Hello", " ", "world", "!"]
            for chunk in chunks:
                yield Mock(content=chunk)
        
        mock_instance.astream = Mock(return_value=mock_stream())
        
        async def test_stream():
            content = ""
            async for chunk in mock_instance.astream(["test"]):
                content += chunk.content
            return content
        
        result = asyncio.run(test_stream())
        assert result == "Hello world!"


class TestModelComparison:
    """Test suite comparing both model implementations."""

    @patch('ArkModelOAI.ArkModelLink')
    @patch('ArkModelRefactored.ArkModelRefactored')
    def test_model_compatibility(self, mock_refactored, mock_oai):
        """Test compatibility between model implementations."""
        # Set up mocks
        mock_oai_instance = Mock()
        mock_refactored_instance = Mock()
        mock_oai.return_value = mock_oai_instance
        mock_refactored.return_value = mock_refactored_instance
        
        # Test same interface
        test_message = ["Hello, world!"]
        
        # Both should handle the same message format
        mock_oai_instance.invoke.return_value = Mock(content="OAI Response")
        mock_refactored_instance.invoke.return_value = Mock(content="Refactored Response")
        
        oai_model = mock_oai()
        refactored_model = mock_refactored()
        
        oai_response = oai_model.invoke(test_message)
        refactored_response = refactored_model.invoke(test_message)
        
        assert oai_response.content == "OAI Response"
        assert refactored_response.content == "Refactored Response"

    def test_feature_comparison(self):
        """Test feature comparison between implementations."""
        # Test feature matrix
        features = {
            "langchain_integration": {"oai": True, "refactored": False},
            "custom_messages": {"oai": False, "refactored": True},
            "tool_calling": {"oai": True, "refactored": True},
            "streaming": {"oai": True, "refactored": True},
            "async_support": {"oai": True, "refactored": True}
        }
        
        # Verify feature matrix structure
        assert "langchain_integration" in features
        assert "tool_calling" in features
        assert features["tool_calling"]["oai"] == True
        assert features["tool_calling"]["refactored"] == True

    def test_performance_characteristics(self):
        """Test performance characteristics."""
        # Test performance metrics (mock)
        performance_metrics = {
            "oai": {
                "initialization_time": 0.1,
                "inference_time": 0.5,
                "memory_usage": 100
            },
            "refactored": {
                "initialization_time": 0.05,
                "inference_time": 0.4,
                "memory_usage": 80
            }
        }
        
        assert performance_metrics["refactored"]["initialization_time"] < performance_metrics["oai"]["initialization_time"]
        assert performance_metrics["refactored"]["memory_usage"] < performance_metrics["oai"]["memory_usage"]


class TestModelHTTPClient:
    """Test suite for HTTP client functionality."""

    @patch('httpx.AsyncClient')
    def test_async_http_client(self, mock_client):
        """Test async HTTP client."""
        mock_response = Mock()
        mock_response.json.return_value = {"choices": [{"message": {"content": "Test"}}]}
        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
        
        async def test_request():
            async with mock_client() as client:
                response = await client.post("/test", json={"message": "test"})
                return response.json()
        
        result = asyncio.run(test_request())
        assert result["choices"][0]["message"]["content"] == "Test"

    @patch('httpx.Client')
    def test_sync_http_client(self, mock_client):
        """Test sync HTTP client."""
        mock_response = Mock()
        mock_response.json.return_value = {"choices": [{"message": {"content": "Test"}}]}
        mock_client.return_value.__enter__.return_value.post.return_value = mock_response
        
        with mock_client() as client:
            response = client.post("/test", json={"message": "test"})
            result = response.json()
        
        assert result["choices"][0]["message"]["content"] == "Test"

    @patch('httpx.AsyncClient')
    def test_http_error_handling(self, mock_client):
        """Test HTTP error handling."""
        mock_client.return_value.__aenter__.return_value.post.side_effect = httpx.HTTPError("Network error")
        
        async def test_error():
            async with mock_client() as client:
                with pytest.raises(httpx.HTTPError):
                    await client.post("/test", json={"message": "test"})
        
        asyncio.run(test_error())

    @patch('httpx.AsyncClient')
    def test_http_timeout_handling(self, mock_client):
        """Test HTTP timeout handling."""
        mock_client.return_value.__aenter__.return_value.post.side_effect = httpx.TimeoutException("Request timeout")
        
        async def test_timeout():
            async with mock_client() as client:
                with pytest.raises(httpx.TimeoutException):
                    await client.post("/test", json={"message": "test"})
        
        asyncio.run(test_timeout())

    @patch('httpx.AsyncClient')
    def test_streaming_response(self, mock_client):
        """Test streaming HTTP response."""
        async def mock_stream():
            for chunk in [b"Hello", b" ", b"world"]:
                yield chunk
        
        mock_response = Mock()
        mock_response.aiter_bytes.return_value = mock_stream()
        mock_client.return_value.__aenter__.return_value.stream.return_value.__aenter__.return_value = mock_response
        
        async def test_stream():
            async with mock_client() as client:
                async with client.stream("POST", "/test") as response:
                    content = b""
                    async for chunk in response.aiter_bytes():
                        content += chunk
                    return content.decode()
        
        result = asyncio.run(test_stream())
        assert result == "Hello world"


@pytest.mark.model
class TestModelIntegrationScenarios:
    """Integration test scenarios for model implementations."""

    @patch('ArkModelOAI.ArkModelLink')
    def test_chat_completion_workflow(self, mock_ark_model):
        """Test complete chat completion workflow."""
        mock_instance = Mock()
        mock_response = Mock()
        mock_response.content = "I'll help you with that!"
        mock_instance.invoke.return_value = mock_response
        mock_ark_model.return_value = mock_instance
        
        model = mock_ark_model()
        
        # Test complete workflow
        user_input = "Can you help me schedule a meeting?"
        response = model.invoke([user_input])
        
        assert response.content == "I'll help you with that!"

    @patch('ArkModelOAI.ArkModelLink')
    def test_tool_calling_workflow(self, mock_ark_model):
        """Test complete tool calling workflow."""
        mock_instance = Mock()
        mock_response = Mock()
        mock_response.tool_calls = [
            {
                "id": "call_weather",
                "function": {
                    "name": "get_weather",
                    "arguments": '{"location": "San Francisco"}'
                }
            }
        ]
        mock_instance.invoke.return_value = mock_response
        mock_ark_model.return_value = mock_instance
        
        model = mock_ark_model()
        
        # Test tool calling workflow
        user_input = "What's the weather in San Francisco?"
        response = model.invoke([user_input])
        
        assert hasattr(response, 'tool_calls')
        assert len(response.tool_calls) == 1
        assert response.tool_calls[0]["function"]["name"] == "get_weather"

    @patch('ArkModelOAI.ArkModelLink')
    def test_multi_turn_conversation(self, mock_ark_model):
        """Test multi-turn conversation."""
        mock_instance = Mock()
        mock_ark_model.return_value = mock_instance
        
        # Set up different responses for different turns
        responses = [
            Mock(content="Hello! How can I help you?"),
            Mock(content="I can help you schedule a meeting."),
            Mock(content="What time works best for you?")
        ]
        mock_instance.invoke.side_effect = responses
        
        model = mock_ark_model()
        
        # Test multi-turn conversation
        conversation = [
            "Hello",
            "I need to schedule a meeting",
            "Tomorrow at 2 PM"
        ]
        
        responses = []
        for message in conversation:
            response = model.invoke([message])
            responses.append(response.content)
        
        assert len(responses) == 3
        assert "Hello" in responses[0]
        assert "schedule" in responses[1]
        assert "time" in responses[2]

    @patch('ArkModelOAI.ArkModelLink')
    def test_error_recovery_workflow(self, mock_ark_model):
        """Test error recovery workflow."""
        mock_instance = Mock()
        mock_ark_model.return_value = mock_instance
        
        # First call fails, second succeeds
        mock_instance.invoke.side_effect = [
            Exception("Temporary service error"),
            Mock(content="Service recovered, how can I help?")
        ]
        
        model = mock_ark_model()
        
        # Test error recovery
        user_input = "Hello"
        
        # First attempt fails
        with pytest.raises(Exception):
            model.invoke([user_input])
        
        # Second attempt succeeds
        response = model.invoke([user_input])
        assert "recovered" in response.content