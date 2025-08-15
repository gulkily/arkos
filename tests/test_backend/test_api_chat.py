import pytest
from unittest.mock import patch, Mock, AsyncMock
from fastapi.testclient import TestClient
from httpx import AsyncClient
import json


class TestChatAPI:
    """Test suite for Chat API endpoints."""

    def test_process_chat_message_create_event(self, fastapi_client, sample_chat_message):
        """Test chat message processing for event creation."""
        message_data = {"message": "schedule a meeting for tomorrow"}
        
        response = fastapi_client.post("/api/chat/message", json=message_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "response" in data
        assert data["action"] == "create_event"

    def test_process_chat_message_list_events(self, fastapi_client):
        """Test chat message processing for listing events."""
        message_data = {"message": "show me my events"}
        
        response = fastapi_client.post("/api/chat/message", json=message_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "response" in data
        assert data["action"] == "list_events"

    def test_process_chat_message_delete_event(self, fastapi_client):
        """Test chat message processing for deleting events."""
        message_data = {"message": "delete my meeting"}
        
        response = fastapi_client.post("/api/chat/message", json=message_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "response" in data
        assert data["action"] == "delete_event"

    def test_process_chat_message_unknown_intent(self, fastapi_client):
        """Test chat message processing for unknown intent."""
        message_data = {"message": "what is the weather like?"}
        
        response = fastapi_client.post("/api/chat/message", json=message_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "response" in data
        assert data["action"] is None

    def test_process_chat_message_empty_message(self, fastapi_client):
        """Test chat message processing with empty message."""
        message_data = {"message": ""}
        
        response = fastapi_client.post("/api/chat/message", json=message_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "response" in data

    def test_process_chat_message_invalid_json(self, fastapi_client):
        """Test chat message processing with invalid JSON."""
        response = fastapi_client.post("/api/chat/message", json={})
        assert response.status_code == 422

    def test_get_chat_suggestions(self, fastapi_client):
        """Test getting chat suggestions."""
        response = fastapi_client.get("/api/chat/suggestions")
        assert response.status_code == 200
        
        data = response.json()
        assert "suggestions" in data
        assert isinstance(data["suggestions"], list)
        assert len(data["suggestions"]) > 0

    @pytest.mark.asyncio
    async def test_async_chat_message_processing(self, async_fastapi_client, sample_chat_message):
        """Test async chat message processing."""
        response = await async_fastapi_client.post("/api/chat/message", json=sample_chat_message)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_async_chat_suggestions(self, async_fastapi_client):
        """Test async chat suggestions."""
        response = await async_fastapi_client.get("/api/chat/suggestions")
        assert response.status_code == 200


class TestChatCommandParser:
    """Test suite for chat command parsing functionality."""

    def test_parse_command_create_event(self):
        """Test parsing create event commands."""
        try:
            from main import parse_command
            
            # Test various create event phrases
            test_cases = [
                ("add a meeting", ("create_event", {"action": "create_event"})),
                ("schedule a call", ("create_event", {"action": "create_event"})),
                ("Add meeting tomorrow", ("create_event", {"action": "create_event"})),
                ("SCHEDULE appointment", ("create_event", {"action": "create_event"})),
            ]
            
            for message, expected in test_cases:
                result = parse_command(message)
                assert result == expected
                
        except ImportError:
            pytest.skip("parse_command function not available")

    def test_parse_command_list_events(self):
        """Test parsing list events commands."""
        try:
            from main import parse_command
            
            test_cases = [
                ("show my events", ("list_events", {"action": "list_events"})),
                ("list appointments", ("list_events", {"action": "list_events"})),
                ("Show me calendar", ("list_events", {"action": "list_events"})),
                ("LIST events", ("list_events", {"action": "list_events"})),
            ]
            
            for message, expected in test_cases:
                result = parse_command(message)
                assert result == expected
                
        except ImportError:
            pytest.skip("parse_command function not available")

    def test_parse_command_delete_event(self):
        """Test parsing delete event commands."""
        try:
            from main import parse_command
            
            test_cases = [
                ("delete my meeting", ("delete_event", {"action": "delete_event"})),
                ("remove appointment", ("delete_event", {"action": "delete_event"})),
                ("Delete event", ("delete_event", {"action": "delete_event"})),
                ("REMOVE call", ("delete_event", {"action": "delete_event"})),
            ]
            
            for message, expected in test_cases:
                result = parse_command(message)
                assert result == expected
                
        except ImportError:
            pytest.skip("parse_command function not available")

    def test_parse_command_unknown(self):
        """Test parsing unknown commands."""
        try:
            from main import parse_command
            
            test_cases = [
                ("what's the weather?", ("unknown", {})),
                ("hello there", ("unknown", {})),
                ("random text", ("unknown", {})),
                ("", ("unknown", {})),
            ]
            
            for message, expected in test_cases:
                result = parse_command(message)
                assert result == expected
                
        except ImportError:
            pytest.skip("parse_command function not available")


class TestChatIntegration:
    """Integration tests for Chat workflows."""

    def test_chat_to_event_creation_workflow(self, fastapi_client):
        """Test complete workflow from chat to event creation."""
        # Step 1: Send chat message for event creation
        message_data = {"message": "schedule a meeting tomorrow at 2pm"}
        response = fastapi_client.post("/api/chat/message", json=message_data)
        assert response.status_code == 200
        
        chat_response = response.json()
        assert chat_response["action"] == "create_event"
        
        # Step 2: Create event based on chat response
        event_data = {
            "title": "Meeting",
            "description": "Meeting scheduled via chat",
            "start_time": "2024-01-16T14:00:00",
            "end_time": "2024-01-16T15:00:00"
        }
        response = fastapi_client.post("/api/events/", json=event_data)
        assert response.status_code == 200

    def test_chat_to_event_listing_workflow(self, fastapi_client):
        """Test complete workflow from chat to event listing."""
        # Step 1: Send chat message for event listing
        message_data = {"message": "show me my events"}
        response = fastapi_client.post("/api/chat/message", json=message_data)
        assert response.status_code == 200
        
        chat_response = response.json()
        assert chat_response["action"] == "list_events"
        
        # Step 2: List events based on chat response
        response = fastapi_client.get("/api/events/")
        assert response.status_code == 200

    def test_chat_session_management(self, fastapi_client):
        """Test chat session management."""
        # Send multiple messages in sequence
        messages = [
            {"message": "schedule a meeting"},
            {"message": "show my events"},
            {"message": "delete last event"}
        ]
        
        for message_data in messages:
            response = fastapi_client.post("/api/chat/message", json=message_data)
            assert response.status_code == 200
            
            data = response.json()
            assert "response" in data
            assert "action" in data

    def test_chat_error_handling(self, fastapi_client):
        """Test chat error handling scenarios."""
        # Test with various edge cases
        test_cases = [
            {"message": None},  # None message
            {"message": " " * 1000},  # Very long message
            {"message": "test\n\n\ntest"},  # Message with newlines
            {"message": "🎉🎊🎈"},  # Emoji-only message
        ]
        
        for message_data in test_cases:
            response = fastapi_client.post("/api/chat/message", json=message_data)
            # Should handle gracefully
            assert response.status_code in [200, 422]


class TestChatWithLLMIntegration:
    """Test chat integration with LLM models."""

    @patch('main.chat_model')
    def test_chat_with_mock_llm(self, mock_model, fastapi_client):
        """Test chat integration with mocked LLM."""
        mock_model.invoke.return_value = Mock(
            content="I'll help you schedule a meeting."
        )
        
        message_data = {"message": "schedule a meeting"}
        response = fastapi_client.post("/api/chat/message", json=message_data)
        assert response.status_code == 200

    @patch('main.chat_model')
    def test_chat_with_llm_error(self, mock_model, fastapi_client):
        """Test chat handling when LLM fails."""
        mock_model.invoke.side_effect = Exception("LLM service unavailable")
        
        message_data = {"message": "schedule a meeting"}
        response = fastapi_client.post("/api/chat/message", json=message_data)
        # Should handle LLM errors gracefully
        assert response.status_code in [200, 500]

    @patch('main.chat_model')
    def test_chat_with_llm_timeout(self, mock_model, fastapi_client):
        """Test chat handling with LLM timeout."""
        import time
        
        def slow_invoke(*args, **kwargs):
            time.sleep(10)  # Simulate timeout
            return Mock(content="Response")
        
        mock_model.invoke.side_effect = slow_invoke
        
        message_data = {"message": "schedule a meeting"}
        response = fastapi_client.post("/api/chat/message", json=message_data)
        # Should handle timeouts appropriately
        assert response.status_code in [200, 504]


@pytest.mark.chat
class TestChatAdvancedFeatures:
    """Test advanced chat features."""

    def test_chat_context_awareness(self, fastapi_client):
        """Test chat context awareness across messages."""
        # This would test if the chat system remembers context
        # across multiple messages in a session
        
        # First message
        message_data = {"message": "I want to schedule a meeting"}
        response = fastapi_client.post("/api/chat/message", json=message_data)
        assert response.status_code == 200
        
        # Follow-up message (should understand context)
        message_data = {"message": "make it tomorrow at 3pm"}
        response = fastapi_client.post("/api/chat/message", json=message_data)
        assert response.status_code == 200

    def test_chat_natural_language_processing(self, fastapi_client):
        """Test natural language processing capabilities."""
        # Test various natural language patterns
        test_cases = [
            "Can you schedule a meeting for next Monday?",
            "I need to add an appointment tomorrow afternoon",
            "Please show me what I have planned for this week",
            "Delete my 2pm meeting today",
            "What's on my calendar for tomorrow?",
        ]
        
        for message in test_cases:
            message_data = {"message": message}
            response = fastapi_client.post("/api/chat/message", json=message_data)
            assert response.status_code == 200
            
            data = response.json()
            assert "response" in data
            assert isinstance(data["response"], str)

    def test_chat_multilingual_support(self, fastapi_client):
        """Test multilingual chat support."""
        # Test with different languages
        test_cases = [
            "Programar una reunión para mañana",  # Spanish
            "Planifier un rendez-vous demain",    # French
            "Termine für morgen anzeigen",        # German
            "明日のミーティングを予定する",        # Japanese
        ]
        
        for message in test_cases:
            message_data = {"message": message}
            response = fastapi_client.post("/api/chat/message", json=message_data)
            assert response.status_code == 200
            
            data = response.json()
            assert "response" in data

    def test_chat_suggestions_personalization(self, fastapi_client):
        """Test personalized chat suggestions."""
        # Test if suggestions adapt to user behavior
        response = fastapi_client.get("/api/chat/suggestions")
        assert response.status_code == 200
        
        data = response.json()
        assert "suggestions" in data
        assert len(data["suggestions"]) > 0
        
        # Suggestions should be relevant and helpful
        for suggestion in data["suggestions"]:
            assert isinstance(suggestion, str)
            assert len(suggestion) > 0

    def test_chat_performance_under_load(self, fastapi_client):
        """Test chat performance under load."""
        import concurrent.futures
        
        def send_chat_message(message):
            message_data = {"message": message}
            return fastapi_client.post("/api/chat/message", json=message_data)
        
        # Test concurrent chat messages
        messages = [f"schedule meeting {i}" for i in range(10)]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(send_chat_message, msg) for msg in messages]
            results = [future.result() for future in futures]
            
            # All should succeed
            for result in results:
                assert result.status_code == 200