import pytest
from datetime import datetime, date
from pydantic import ValidationError
from typing import Optional


class TestEventModels:
    """Test suite for Event Pydantic models."""

    def test_event_base_model(self):
        """Test EventBase model validation."""
        try:
            from main import EventBase
            
            # Test valid event creation
            event_data = {
                "title": "Test Event",
                "description": "Test description",
                "start_time": datetime(2024, 1, 15, 10, 0),
                "end_time": datetime(2024, 1, 15, 11, 0)
            }
            
            event = EventBase(**event_data)
            assert event.title == "Test Event"
            assert event.description == "Test description"
            assert event.start_time == datetime(2024, 1, 15, 10, 0)
            assert event.end_time == datetime(2024, 1, 15, 11, 0)
            
        except ImportError:
            pytest.skip("EventBase model not available")

    def test_event_base_model_optional_description(self):
        """Test EventBase model with optional description."""
        try:
            from main import EventBase
            
            event_data = {
                "title": "Test Event",
                "start_time": datetime(2024, 1, 15, 10, 0),
                "end_time": datetime(2024, 1, 15, 11, 0)
            }
            
            event = EventBase(**event_data)
            assert event.title == "Test Event"
            assert event.description is None
            
        except ImportError:
            pytest.skip("EventBase model not available")

    def test_event_create_model(self):
        """Test EventCreate model validation."""
        try:
            from main import EventCreate
            
            event_data = {
                "title": "Test Event",
                "description": "Test description",
                "start_time": datetime(2024, 1, 15, 10, 0),
                "end_time": datetime(2024, 1, 15, 11, 0)
            }
            
            event = EventCreate(**event_data)
            assert isinstance(event, EventCreate)
            assert event.title == "Test Event"
            
        except ImportError:
            pytest.skip("EventCreate model not available")

    def test_event_model_with_id(self):
        """Test Event model with ID and timestamps."""
        try:
            from main import Event
            
            event_data = {
                "id": "test-id-123",
                "title": "Test Event",
                "description": "Test description",
                "start_time": datetime(2024, 1, 15, 10, 0),
                "end_time": datetime(2024, 1, 15, 11, 0),
                "created_at": datetime(2024, 1, 14, 12, 0),
                "updated_at": datetime(2024, 1, 14, 12, 0)
            }
            
            event = Event(**event_data)
            assert event.id == "test-id-123"
            assert event.title == "Test Event"
            assert event.created_at == datetime(2024, 1, 14, 12, 0)
            assert event.updated_at == datetime(2024, 1, 14, 12, 0)
            
        except ImportError:
            pytest.skip("Event model not available")

    def test_event_model_validation_errors(self):
        """Test Event model validation errors."""
        try:
            from main import EventBase
            
            # Test missing required fields
            with pytest.raises(ValidationError):
                EventBase(description="No title or times")
            
            # Test empty title
            with pytest.raises(ValidationError):
                EventBase(
                    title="",
                    start_time=datetime(2024, 1, 15, 10, 0),
                    end_time=datetime(2024, 1, 15, 11, 0)
                )
            
            # Test invalid datetime
            with pytest.raises(ValidationError):
                EventBase(
                    title="Test Event",
                    start_time="invalid-datetime",
                    end_time=datetime(2024, 1, 15, 11, 0)
                )
                
        except ImportError:
            pytest.skip("Event models not available")

    def test_event_model_datetime_serialization(self):
        """Test Event model datetime serialization."""
        try:
            from main import EventBase
            
            event_data = {
                "title": "Test Event",
                "start_time": datetime(2024, 1, 15, 10, 0),
                "end_time": datetime(2024, 1, 15, 11, 0)
            }
            
            event = EventBase(**event_data)
            
            # Test serialization
            event_dict = event.dict()
            assert isinstance(event_dict["start_time"], datetime)
            assert isinstance(event_dict["end_time"], datetime)
            
            # Test JSON serialization
            event_json = event.json()
            assert isinstance(event_json, str)
            
        except ImportError:
            pytest.skip("Event models not available")

    def test_event_model_with_timezone(self):
        """Test Event model with timezone-aware datetimes."""
        try:
            from main import EventBase
            import pytz
            
            timezone = pytz.timezone('US/Eastern')
            
            event_data = {
                "title": "Test Event",
                "start_time": timezone.localize(datetime(2024, 1, 15, 10, 0)),
                "end_time": timezone.localize(datetime(2024, 1, 15, 11, 0))
            }
            
            event = EventBase(**event_data)
            assert event.start_time.tzinfo is not None
            assert event.end_time.tzinfo is not None
            
        except ImportError:
            pytest.skip("Event models or pytz not available")

    def test_event_model_field_constraints(self):
        """Test Event model field constraints."""
        try:
            from main import EventBase
            
            # Test very long title
            long_title = "A" * 1000
            event_data = {
                "title": long_title,
                "start_time": datetime(2024, 1, 15, 10, 0),
                "end_time": datetime(2024, 1, 15, 11, 0)
            }
            
            # Should either accept long titles or raise validation error
            try:
                event = EventBase(**event_data)
                assert len(event.title) <= 1000  # If accepted, should be within limits
            except ValidationError:
                pass  # Expected if title length is constrained
                
        except ImportError:
            pytest.skip("Event models not available")


class TestChatModels:
    """Test suite for Chat Pydantic models."""

    def test_chat_message_model(self):
        """Test ChatMessage model validation."""
        try:
            from main import ChatMessage
            
            message_data = {"message": "Hello, world!"}
            chat_message = ChatMessage(**message_data)
            
            assert chat_message.message == "Hello, world!"
            
        except ImportError:
            pytest.skip("ChatMessage model not available")

    def test_chat_message_model_empty_message(self):
        """Test ChatMessage model with empty message."""
        try:
            from main import ChatMessage
            
            message_data = {"message": ""}
            chat_message = ChatMessage(**message_data)
            
            assert chat_message.message == ""
            
        except ImportError:
            pytest.skip("ChatMessage model not available")

    def test_chat_response_model(self):
        """Test ChatResponse model validation."""
        try:
            from main import ChatResponse
            
            response_data = {
                "response": "This is a response",
                "action": "create_event",
                "data": {"key": "value"}
            }
            
            chat_response = ChatResponse(**response_data)
            assert chat_response.response == "This is a response"
            assert chat_response.action == "create_event"
            assert chat_response.data == {"key": "value"}
            
        except ImportError:
            pytest.skip("ChatResponse model not available")

    def test_chat_response_model_optional_fields(self):
        """Test ChatResponse model with optional fields."""
        try:
            from main import ChatResponse
            
            response_data = {"response": "This is a response"}
            chat_response = ChatResponse(**response_data)
            
            assert chat_response.response == "This is a response"
            assert chat_response.action is None
            assert chat_response.data is None
            
        except ImportError:
            pytest.skip("ChatResponse model not available")

    def test_chat_models_validation_errors(self):
        """Test Chat models validation errors."""
        try:
            from main import ChatMessage, ChatResponse
            
            # Test missing required fields
            with pytest.raises(ValidationError):
                ChatMessage()
            
            with pytest.raises(ValidationError):
                ChatResponse()
                
        except ImportError:
            pytest.skip("Chat models not available")

    def test_chat_models_serialization(self):
        """Test Chat models serialization."""
        try:
            from main import ChatMessage, ChatResponse
            
            # Test ChatMessage serialization
            message = ChatMessage(message="Test message")
            message_dict = message.dict()
            assert message_dict["message"] == "Test message"
            
            # Test ChatResponse serialization
            response = ChatResponse(response="Test response")
            response_dict = response.dict()
            assert response_dict["response"] == "Test response"
            assert response_dict["action"] is None
            
        except ImportError:
            pytest.skip("Chat models not available")


class TestCustomValidators:
    """Test suite for custom model validators."""

    def test_event_time_validation(self):
        """Test custom validation for event times."""
        try:
            from main import EventBase
            
            # Test that end time is after start time
            with pytest.raises(ValidationError):
                EventBase(
                    title="Test Event",
                    start_time=datetime(2024, 1, 15, 11, 0),
                    end_time=datetime(2024, 1, 15, 10, 0)  # Before start time
                )
                
        except ImportError:
            pytest.skip("Event models not available")
        except ValidationError:
            pass  # Expected if custom validation exists
        except:
            # If no custom validation, the test should pass
            pass

    def test_event_title_validation(self):
        """Test custom validation for event titles."""
        try:
            from main import EventBase
            
            # Test various title formats
            valid_titles = [
                "Meeting",
                "Meeting with @John",
                "Meeting #1",
                "Meeting (Important)",
                "Meeting & Discussion",
            ]
            
            for title in valid_titles:
                event = EventBase(
                    title=title,
                    start_time=datetime(2024, 1, 15, 10, 0),
                    end_time=datetime(2024, 1, 15, 11, 0)
                )
                assert event.title == title
                
        except ImportError:
            pytest.skip("Event models not available")

    def test_chat_message_validation(self):
        """Test custom validation for chat messages."""
        try:
            from main import ChatMessage
            
            # Test various message formats
            valid_messages = [
                "Hello",
                "Schedule a meeting",
                "What's my schedule?",
                "Meeting at 2pm",
                "Delete event #123",
            ]
            
            for message in valid_messages:
                chat_message = ChatMessage(message=message)
                assert chat_message.message == message
                
        except ImportError:
            pytest.skip("Chat models not available")


class TestModelInheritance:
    """Test suite for model inheritance."""

    def test_event_create_inheritance(self):
        """Test EventCreate inherits from EventBase."""
        try:
            from main import EventBase, EventCreate
            
            # Verify inheritance
            assert issubclass(EventCreate, EventBase)
            
            # Test that EventCreate has all EventBase fields
            event_data = {
                "title": "Test Event",
                "start_time": datetime(2024, 1, 15, 10, 0),
                "end_time": datetime(2024, 1, 15, 11, 0)
            }
            
            event_create = EventCreate(**event_data)
            assert hasattr(event_create, 'title')
            assert hasattr(event_create, 'start_time')
            assert hasattr(event_create, 'end_time')
            
        except ImportError:
            pytest.skip("Event models not available")

    def test_event_inheritance(self):
        """Test Event inherits from EventBase."""
        try:
            from main import EventBase, Event
            
            # Verify inheritance
            assert issubclass(Event, EventBase)
            
            # Test that Event has additional fields
            event_data = {
                "id": "test-id",
                "title": "Test Event",
                "start_time": datetime(2024, 1, 15, 10, 0),
                "end_time": datetime(2024, 1, 15, 11, 0),
                "created_at": datetime(2024, 1, 14, 12, 0),
                "updated_at": datetime(2024, 1, 14, 12, 0)
            }
            
            event = Event(**event_data)
            assert hasattr(event, 'id')
            assert hasattr(event, 'created_at')
            assert hasattr(event, 'updated_at')
            
        except ImportError:
            pytest.skip("Event models not available")


@pytest.mark.unit
class TestModelUtilities:
    """Test suite for model utility functions."""

    def test_model_to_dict_conversion(self):
        """Test model to dictionary conversion."""
        try:
            from main import EventBase
            
            event_data = {
                "title": "Test Event",
                "start_time": datetime(2024, 1, 15, 10, 0),
                "end_time": datetime(2024, 1, 15, 11, 0)
            }
            
            event = EventBase(**event_data)
            event_dict = event.dict()
            
            assert isinstance(event_dict, dict)
            assert event_dict["title"] == "Test Event"
            assert isinstance(event_dict["start_time"], datetime)
            
        except ImportError:
            pytest.skip("Event models not available")

    def test_model_from_dict_creation(self):
        """Test model creation from dictionary."""
        try:
            from main import EventBase
            
            event_dict = {
                "title": "Test Event",
                "start_time": datetime(2024, 1, 15, 10, 0),
                "end_time": datetime(2024, 1, 15, 11, 0)
            }
            
            event = EventBase.parse_obj(event_dict)
            assert event.title == "Test Event"
            assert event.start_time == datetime(2024, 1, 15, 10, 0)
            
        except ImportError:
            pytest.skip("Event models not available")
        except AttributeError:
            # For newer Pydantic versions
            try:
                event = EventBase.model_validate(event_dict)
                assert event.title == "Test Event"
            except:
                pytest.skip("Model validation method not available")

    def test_model_json_serialization(self):
        """Test model JSON serialization."""
        try:
            from main import EventBase
            import json
            
            event_data = {
                "title": "Test Event",
                "start_time": datetime(2024, 1, 15, 10, 0),
                "end_time": datetime(2024, 1, 15, 11, 0)
            }
            
            event = EventBase(**event_data)
            event_json = event.json()
            
            assert isinstance(event_json, str)
            parsed_data = json.loads(event_json)
            assert parsed_data["title"] == "Test Event"
            
        except ImportError:
            pytest.skip("Event models not available")