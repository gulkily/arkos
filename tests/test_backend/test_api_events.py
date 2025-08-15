import pytest
from datetime import datetime, date
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from httpx import AsyncClient
import json


class TestEventAPI:
    """Test suite for Event API endpoints."""

    def test_create_event_success(self, fastapi_client, sample_event_data, mock_datetime, mock_uuid):
        """Test successful event creation."""
        response = fastapi_client.post("/api/events/", json=sample_event_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == sample_event_data["title"]
        assert data["description"] == sample_event_data["description"]
        assert data["id"] == "test-uuid-123"
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_event_invalid_data(self, fastapi_client):
        """Test event creation with invalid data."""
        invalid_data = {
            "title": "",  # Empty title
            "start_time": "invalid-datetime",
            "end_time": "invalid-datetime"
        }
        response = fastapi_client.post("/api/events/", json=invalid_data)
        assert response.status_code == 422

    def test_create_event_end_before_start(self, fastapi_client):
        """Test event creation with end time before start time."""
        invalid_data = {
            "title": "Test Event",
            "start_time": "2024-01-15T15:00:00",
            "end_time": "2024-01-15T10:00:00"  # Before start time
        }
        response = fastapi_client.post("/api/events/", json=invalid_data)
        # This should be handled by business logic validation
        assert response.status_code in [400, 422]

    def test_list_events_empty(self, fastapi_client):
        """Test listing events when no events exist."""
        response = fastapi_client.get("/api/events/")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_events_with_data(self, fastapi_client, sample_events_list):
        """Test listing events with existing data."""
        # Mock the events database
        with patch('main.events_db', sample_events_list[0]):
            with patch('main.users_db', {"test_user": {"events": ["event-1", "event-2"]}}):
                response = fastapi_client.get("/api/events/")
                assert response.status_code == 200
                # Implementation depends on the actual backend logic

    def test_list_events_with_date_filter(self, fastapi_client, sample_date_range):
        """Test listing events with date range filtering."""
        params = {
            "start_date": sample_date_range["start_date"].isoformat(),
            "end_date": sample_date_range["end_date"].isoformat()
        }
        response = fastapi_client.get("/api/events/", params=params)
        assert response.status_code == 200

    def test_get_event_success(self, fastapi_client, sample_events_list):
        """Test getting a specific event."""
        event_id = "event-1"
        # Mock the events database
        with patch('main.events_db', {event_id: sample_events_list[0]}):
            response = fastapi_client.get(f"/api/events/{event_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == event_id

    def test_get_event_not_found(self, fastapi_client):
        """Test getting a non-existent event."""
        response = fastapi_client.get("/api/events/nonexistent-id")
        assert response.status_code == 404
        assert "Event not found" in response.json()["detail"]

    def test_update_event_success(self, fastapi_client, sample_events_list):
        """Test updating an existing event."""
        event_id = "event-1"
        update_data = {
            "title": "Updated Meeting",
            "description": "Updated description"
        }
        
        # Mock the events database
        with patch('main.events_db', {event_id: sample_events_list[0]}):
            response = fastapi_client.put(f"/api/events/{event_id}", json=update_data)
            assert response.status_code == 200
            data = response.json()
            assert data["title"] == update_data["title"]
            assert data["description"] == update_data["description"]

    def test_update_event_not_found(self, fastapi_client):
        """Test updating a non-existent event."""
        update_data = {"title": "Updated Meeting"}
        response = fastapi_client.put("/api/events/nonexistent-id", json=update_data)
        assert response.status_code == 404

    def test_delete_event_success(self, fastapi_client, sample_events_list):
        """Test deleting an existing event."""
        event_id = "event-1"
        
        # Mock the events database
        with patch('main.events_db', {event_id: sample_events_list[0]}):
            with patch('main.users_db', {"test_user": {"events": [event_id]}}):
                response = fastapi_client.delete(f"/api/events/{event_id}")
                assert response.status_code == 200
                assert "Event deleted" in response.json()["message"]

    def test_delete_event_not_found(self, fastapi_client):
        """Test deleting a non-existent event."""
        response = fastapi_client.delete("/api/events/nonexistent-id")
        assert response.status_code == 404

    def test_event_permissions(self, fastapi_client):
        """Test event access permissions."""
        # This would test that users can only access their own events
        # Implementation depends on the authentication system
        pass

    @pytest.mark.asyncio
    async def test_async_event_creation(self, async_fastapi_client, sample_event_data):
        """Test async event creation."""
        response = await async_fastapi_client.post("/api/events/", json=sample_event_data)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_async_event_listing(self, async_fastapi_client):
        """Test async event listing."""
        response = await async_fastapi_client.get("/api/events/")
        assert response.status_code == 200


class TestEventValidation:
    """Test suite for Event model validation."""

    def test_event_model_validation(self):
        """Test Pydantic model validation for Event."""
        # Import the models if available
        try:
            from main import Event, EventCreate
            
            # Test valid event creation
            event_data = {
                "title": "Test Event",
                "description": "Test description",
                "start_time": datetime(2024, 1, 15, 10, 0),
                "end_time": datetime(2024, 1, 15, 11, 0)
            }
            
            event = EventCreate(**event_data)
            assert event.title == "Test Event"
            assert event.description == "Test description"
            
        except ImportError:
            pytest.skip("Event models not available")

    def test_event_model_validation_errors(self):
        """Test Pydantic model validation errors."""
        try:
            from main import EventCreate
            
            # Test missing required fields
            with pytest.raises(Exception):
                EventCreate(title="", start_time="invalid")
                
        except ImportError:
            pytest.skip("Event models not available")


class TestEventIntegration:
    """Integration tests for Event workflows."""

    def test_full_event_lifecycle(self, fastapi_client, sample_event_data):
        """Test complete event lifecycle: create, read, update, delete."""
        # Create event
        response = fastapi_client.post("/api/events/", json=sample_event_data)
        assert response.status_code == 200
        event_id = response.json()["id"]
        
        # Read event
        response = fastapi_client.get(f"/api/events/{event_id}")
        assert response.status_code == 200
        
        # Update event
        update_data = {"title": "Updated Event"}
        response = fastapi_client.put(f"/api/events/{event_id}", json=update_data)
        assert response.status_code == 200
        
        # Delete event
        response = fastapi_client.delete(f"/api/events/{event_id}")
        assert response.status_code == 200
        
        # Verify deletion
        response = fastapi_client.get(f"/api/events/{event_id}")
        assert response.status_code == 404

    def test_event_filtering_and_search(self, fastapi_client):
        """Test event filtering and search functionality."""
        # Create multiple events
        events_data = [
            {
                "title": "Morning Meeting",
                "start_time": "2024-01-15T09:00:00",
                "end_time": "2024-01-15T10:00:00"
            },
            {
                "title": "Afternoon Review",
                "start_time": "2024-01-15T14:00:00",
                "end_time": "2024-01-15T15:00:00"
            },
            {
                "title": "Evening Planning",
                "start_time": "2024-01-16T18:00:00",
                "end_time": "2024-01-16T19:00:00"
            }
        ]
        
        # Create events
        for event_data in events_data:
            response = fastapi_client.post("/api/events/", json=event_data)
            assert response.status_code == 200
        
        # Test date filtering
        response = fastapi_client.get("/api/events/", params={
            "start_date": "2024-01-15",
            "end_date": "2024-01-15"
        })
        assert response.status_code == 200
        # Should return only events from 2024-01-15

    def test_concurrent_event_operations(self, fastapi_client, sample_event_data):
        """Test concurrent event operations."""
        import concurrent.futures
        
        def create_event(event_data):
            return fastapi_client.post("/api/events/", json=event_data)
        
        # Test concurrent event creation
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(create_event, sample_event_data) for _ in range(5)]
            results = [future.result() for future in futures]
            
            # All should succeed
            for result in results:
                assert result.status_code == 200


@pytest.mark.api
class TestEventAPIEdgeCases:
    """Test edge cases for Event API."""

    def test_event_with_very_long_title(self, fastapi_client):
        """Test event creation with very long title."""
        long_title = "A" * 1000
        event_data = {
            "title": long_title,
            "start_time": "2024-01-15T10:00:00",
            "end_time": "2024-01-15T11:00:00"
        }
        
        response = fastapi_client.post("/api/events/", json=event_data)
        # Should handle long titles appropriately
        assert response.status_code in [200, 422]

    def test_event_with_special_characters(self, fastapi_client):
        """Test event creation with special characters."""
        event_data = {
            "title": "Meeting with @#$%^&*()",
            "description": "Description with émojis 🎉 and ñ",
            "start_time": "2024-01-15T10:00:00",
            "end_time": "2024-01-15T11:00:00"
        }
        
        response = fastapi_client.post("/api/events/", json=event_data)
        assert response.status_code == 200

    def test_event_timezone_handling(self, fastapi_client):
        """Test event creation with different timezones."""
        event_data = {
            "title": "Timezone Test",
            "start_time": "2024-01-15T10:00:00+05:00",
            "end_time": "2024-01-15T11:00:00+05:00"
        }
        
        response = fastapi_client.post("/api/events/", json=event_data)
        assert response.status_code == 200

    def test_bulk_event_operations(self, fastapi_client):
        """Test bulk event operations performance."""
        # Create many events
        events_data = [
            {
                "title": f"Event {i}",
                "start_time": f"2024-01-{15 + i % 10}T10:00:00",
                "end_time": f"2024-01-{15 + i % 10}T11:00:00"
            }
            for i in range(50)
        ]
        
        for event_data in events_data:
            response = fastapi_client.post("/api/events/", json=event_data)
            assert response.status_code == 200
        
        # Test listing all events
        response = fastapi_client.get("/api/events/")
        assert response.status_code == 200