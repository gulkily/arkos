#!/usr/bin/env python3
"""
Enhanced ARK Calendar Backend API

This module provides a production-ready FastAPI backend that integrates with the Radicale
CalDAV server and implements the complete OpenAPI specification defined in calendar-api-spec.yaml.

Features:
- Full CRUD operations for calendar events
- Calendar management and discovery
- Natural language processing for chat-based operations
- CalDAV integration via RadicaleCalendarManager
- Comprehensive error handling and validation
- OpenAPI/Swagger documentation
- CORS support for frontend integration

Usage:
    python enhanced_backend_api.py
    
    Or with uvicorn:
    uvicorn enhanced_backend_api:app --host 0.0.0.0 --port 8000 --reload

Dependencies:
    pip install fastapi uvicorn python-multipart caldav python-dotenv
"""

import os
import json
import uuid
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Query, Path, Body, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv

# Local imports
from radicale_calendar_manager import RadicaleCalendarManager
from langchain_mcp_integration import CalendarMCPIntegration, get_calendar_tools

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ark-calendar-api")

# Load environment variables
load_dotenv()

# Global variables for managers
calendar_manager: Optional[RadicaleCalendarManager] = None
mcp_integration: Optional[CalendarMCPIntegration] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown tasks"""
    global calendar_manager, mcp_integration
    
    # Startup
    logger.info("Starting ARK Calendar API...")
    
    try:
        # Initialize Calendar Manager
        radicale_url = os.getenv("RADICALE_URL", "http://localhost:5232")
        radicale_username = os.getenv("RADICALE_USERNAME", "")
        radicale_password = os.getenv("RADICALE_PASSWORD", "")
        
        calendar_manager = RadicaleCalendarManager(
            url=radicale_url,
            username=radicale_username,
            password=radicale_password
        )
        
        if calendar_manager.connect():
            logger.info(f"Connected to Radicale server at {radicale_url}")
        else:
            logger.warning("Failed to connect to Radicale server")
        
        # Initialize MCP Integration for chat features
        try:
            _, mcp_integration = await get_calendar_tools()
            logger.info("MCP integration initialized for chat features")
        except Exception as e:
            logger.warning(f"MCP integration not available: {e}")
            
    except Exception as e:
        logger.error(f"Failed to initialize backend services: {e}")
        
    yield
    
    # Shutdown
    logger.info("Shutting down ARK Calendar API...")
    if mcp_integration:
        try:
            await mcp_integration.cleanup()
            logger.info("MCP integration cleaned up")
        except Exception as e:
            logger.error(f"Error during MCP cleanup: {e}")


# Create FastAPI app
app = FastAPI(
    title="ARK Calendar API",
    description="""
    Comprehensive calendar management API integrating Radicale CalDAV server with ARK backend.
    
    ## Features
    - **Event Management**: Create, read, update, and delete calendar events
    - **Calendar Operations**: Manage multiple calendars and their properties
    - **Date Range Filtering**: Query events within specific date ranges
    - **Natural Language Processing**: Chat-based event management
    - **CalDAV Integration**: Full compatibility with Radicale CalDAV server
    - **Real-time Operations**: Async support for all operations
    """,
    version="2.0.0",
    contact={
        "name": "ARK Development Team",
        "email": "dev@ark-calendar.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---

class CalendarModel(BaseModel):
    """Calendar information and metadata"""
    id: str = Field(..., description="Unique calendar identifier")
    name: str = Field(..., description="Human-readable calendar name")
    description: Optional[str] = Field(None, description="Optional calendar description")
    url: str = Field(..., description="CalDAV URL for this calendar")
    color: Optional[str] = Field("#007bff", pattern=r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$")
    timezone: str = Field("UTC", description="Default timezone for calendar events")
    permissions: Dict[str, bool] = Field(default_factory=lambda: {"read": True, "write": True, "delete": True})
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AttendeeModel(BaseModel):
    """Event attendee information"""
    email: str = Field(..., description="Attendee email address")
    name: Optional[str] = Field(None, description="Attendee display name")
    status: str = Field("needs-action", regex="^(accepted|declined|tentative|needs-action)$")


class RecurrenceModel(BaseModel):
    """Event recurrence rules"""
    frequency: str = Field(..., regex="^(daily|weekly|monthly|yearly)$")
    interval: int = Field(1, ge=1, description="Recurrence interval")
    until: Optional[datetime] = Field(None, description="Recurrence end date")
    count: Optional[int] = Field(None, ge=1, description="Number of occurrences")


class EventBase(BaseModel):
    """Base event model with common fields"""
    summary: str = Field(..., min_length=1, max_length=255, description="Event title/summary")
    description: Optional[str] = Field(None, max_length=2000, description="Detailed event description")
    start: datetime = Field(..., description="Event start time")
    end: datetime = Field(..., description="Event end time")
    location: Optional[str] = Field(None, max_length=255, description="Event location")
    attendees: List[AttendeeModel] = Field(default_factory=list)
    recurrence: Optional[RecurrenceModel] = None
    status: str = Field("confirmed", regex="^(confirmed|tentative|cancelled)$")
    visibility: str = Field("public", regex="^(public|private|confidential)$")

    @validator('end')
    def end_after_start(cls, v, values):
        if 'start' in values and v <= values['start']:
            raise ValueError('End time must be after start time')
        return v


class EventCreate(EventBase):
    """Data required to create a new calendar event"""
    calendar_name: str = Field(..., description="Name of calendar to create event in")


class EventUpdate(BaseModel):
    """Data for updating an existing event (all fields optional)"""
    summary: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    location: Optional[str] = Field(None, max_length=255)
    attendees: Optional[List[AttendeeModel]] = None
    status: Optional[str] = Field(None, regex="^(confirmed|tentative|cancelled)$")
    visibility: Optional[str] = Field(None, regex="^(public|private|confidential)$")

    @validator('end')
    def end_after_start(cls, v, values):
        if 'start' in values and v and values['start'] and v <= values['start']:
            raise ValueError('End time must be after start time')
        return v


class EventResponse(EventBase):
    """Complete calendar event with all metadata"""
    id: str = Field(..., description="Unique event identifier")
    calendar: str = Field(..., description="Calendar containing this event")
    created_at: datetime = Field(..., description="Event creation timestamp")
    updated_at: datetime = Field(..., description="Last modification timestamp")
    url: Optional[str] = Field(None, description="CalDAV URL for this specific event")


class ChatContext(BaseModel):
    """Additional context for processing chat messages"""
    user_timezone: Optional[str] = Field("UTC", description="User's timezone")
    default_calendar: Optional[str] = Field(None, description="Default calendar for operations")
    conversation_id: Optional[str] = Field(None, description="Conversation identifier")


class ChatMessage(BaseModel):
    """Natural language message for calendar operations"""
    message: str = Field(..., min_length=1, max_length=1000, description="Natural language request")
    context: Optional[ChatContext] = Field(default_factory=ChatContext)


class ChatResponse(BaseModel):
    """Response to natural language calendar request"""
    response: str = Field(..., description="Human-readable response to the user")
    action: Optional[str] = Field(None, description="Suggested action based on the message")
    data: Optional[Dict[str, Any]] = Field(None, description="Action-specific data")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Confidence score")
    suggestions: List[str] = Field(default_factory=list, description="Suggested follow-up commands")
    conversation_id: Optional[str] = None


class APIError(BaseModel):
    """Standard error response format"""
    error: str = Field(..., description="Error type identifier")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.now)
    request_id: Optional[str] = None


# --- Dependency Functions ---

def get_calendar_manager() -> RadicaleCalendarManager:
    """Get the global calendar manager instance"""
    if calendar_manager is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Calendar service unavailable"
        )
    return calendar_manager


def get_mcp_integration() -> CalendarMCPIntegration:
    """Get the global MCP integration instance"""
    if mcp_integration is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chat service unavailable"
        )
    return mcp_integration


# --- Utility Functions ---

def format_calendar_response(calendar) -> CalendarModel:
    """Convert CalDAV calendar object to API response format"""
    return CalendarModel(
        id=str(calendar.id) if hasattr(calendar, 'id') else str(uuid.uuid4()),
        name=calendar.name or "Unnamed Calendar",
        description=getattr(calendar, 'description', None),
        url=str(calendar.url) if hasattr(calendar, 'url') else "",
        color="#007bff",  # Default color
        timezone="UTC",   # Default timezone
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


def format_event_response(event_data: Dict[str, Any], calendar_name: str = "Unknown") -> EventResponse:
    """Convert event data to API response format"""
    return EventResponse(
        id=event_data.get("id", str(uuid.uuid4())),
        summary=event_data.get("summary", ""),
        description=event_data.get("description", ""),
        start=datetime.fromisoformat(event_data.get("start", "").replace('Z', '+00:00')) if event_data.get("start") else datetime.now(),
        end=datetime.fromisoformat(event_data.get("end", "").replace('Z', '+00:00')) if event_data.get("end") else datetime.now(),
        location=event_data.get("location", ""),
        calendar=calendar_name,
        attendees=[],  # Would need more complex parsing for real attendees
        status="confirmed",
        visibility="public",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        url=event_data.get("url")
    )


def handle_calendar_error(e: Exception, operation: str) -> HTTPException:
    """Convert calendar manager exceptions to HTTP exceptions"""
    error_msg = str(e)
    
    if "not found" in error_msg.lower():
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{operation} failed: {error_msg}"
        )
    elif "required" in error_msg.lower() or "invalid" in error_msg.lower():
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{operation} failed: {error_msg}"
        )
    else:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{operation} failed: {error_msg}"
        )


# --- API Routes ---

@app.get("/", tags=["health"], summary="API health check")
async def health_check():
    """Basic health check endpoint to verify API availability"""
    return {
        "message": "ARK Calendar API",
        "version": "2.0.0",
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/calendars", tags=["calendars"], response_model=Dict[str, Any])
async def list_calendars(manager: RadicaleCalendarManager = Depends(get_calendar_manager)):
    """Retrieve a list of all calendars accessible to the current user"""
    try:
        calendars = [format_calendar_response(cal) for cal in manager.calendars]
        return {
            "calendars": calendars,
            "count": len(calendars)
        }
    except Exception as e:
        raise handle_calendar_error(e, "List calendars")


@app.get("/api/calendars/{calendar_id}", tags=["calendars"], response_model=CalendarModel)
async def get_calendar(
    calendar_id: str = Path(..., description="Unique calendar identifier"),
    manager: RadicaleCalendarManager = Depends(get_calendar_manager)
):
    """Retrieve detailed information about a specific calendar"""
    try:
        calendar = manager.get_calendar(calendar_id)
        if not calendar:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Calendar '{calendar_id}' not found"
            )
        return format_calendar_response(calendar)
    except HTTPException:
        raise
    except Exception as e:
        raise handle_calendar_error(e, "Get calendar")


@app.get("/api/events", tags=["events"], response_model=Dict[str, Any])
async def list_events(
    calendar_name: Optional[str] = Query(None, description="Filter events by calendar name"),
    start_date: Optional[datetime] = Query(None, description="Start date for filtering"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of events"),
    offset: int = Query(0, ge=0, description="Number of events to skip"),
    manager: RadicaleCalendarManager = Depends(get_calendar_manager)
):
    """Retrieve events from calendars with optional filtering"""
    try:
        # Get events from manager
        events_data = manager.get_events(
            calendar_name=calendar_name,
            start_date=start_date,
            end_date=end_date
        )
        
        # Apply pagination
        total_count = len(events_data)
        paginated_events = events_data[offset:offset + limit]
        
        # Format response
        events = [format_event_response(event, calendar_name or "Unknown") for event in paginated_events]
        
        return {
            "events": events,
            "total_count": total_count,
            "calendar": calendar_name,
            "date_range": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            }
        }
    except Exception as e:
        raise handle_calendar_error(e, "List events")


@app.post("/api/events", tags=["events"], response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_event(
    event: EventCreate,
    manager: RadicaleCalendarManager = Depends(get_calendar_manager)
):
    """Create a new calendar event"""
    try:
        # Prepare event data for manager
        event_data = {
            "summary": event.summary,
            "description": event.description or "",
            "start": event.start.isoformat(),
            "end": event.end.isoformat(),
            "location": event.location or ""
        }
        
        # Create event
        event_id = manager.add_event(event.calendar_name, event_data)
        
        # Get the created event for response
        events = manager.get_events(event.calendar_name)
        created_event = None
        for evt in events:
            if evt.get("id") == event_id:
                created_event = evt
                break
        
        if not created_event:
            # Fallback response if we can't retrieve the created event
            created_event = {
                "id": event_id,
                "summary": event.summary,
                "description": event.description or "",
                "start": event.start.isoformat(),
                "end": event.end.isoformat(),
                "location": event.location or ""
            }
        
        return {
            "event": format_event_response(created_event, event.calendar_name),
            "message": "Event created successfully",
            "event_id": event_id
        }
    except Exception as e:
        raise handle_calendar_error(e, "Create event")


@app.get("/api/events/{event_id}", tags=["events"], response_model=EventResponse)
async def get_event(
    event_id: str = Path(..., description="Unique event identifier"),
    manager: RadicaleCalendarManager = Depends(get_calendar_manager)
):
    """Retrieve detailed information about a specific event"""
    try:
        # Search across all calendars for the event
        for calendar in manager.calendars:
            try:
                events = manager.get_events(calendar.name)
                for event in events:
                    if event.get("id") == event_id:
                        return format_event_response(event, calendar.name)
            except Exception:
                continue  # Skip calendars that error
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event '{event_id}' not found"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise handle_calendar_error(e, "Get event")


@app.put("/api/events/{event_id}", tags=["events"], response_model=Dict[str, Any])
async def update_event(
    event_id: str = Path(..., description="Unique event identifier"),
    event_update: EventUpdate = Body(...),
    manager: RadicaleCalendarManager = Depends(get_calendar_manager)
):
    """Update an existing calendar event"""
    try:
        # Find the event and its calendar
        target_calendar = None
        for calendar in manager.calendars:
            try:
                events = manager.get_events(calendar.name)
                for event in events:
                    if event.get("id") == event_id:
                        target_calendar = calendar.name
                        break
                if target_calendar:
                    break
            except Exception:
                continue
        
        if not target_calendar:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event '{event_id}' not found"
            )
        
        # Prepare update data (only include non-None fields)
        update_data = {}
        if event_update.summary is not None:
            update_data["summary"] = event_update.summary
        if event_update.description is not None:
            update_data["description"] = event_update.description
        if event_update.start is not None:
            update_data["start"] = event_update.start.isoformat()
        if event_update.end is not None:
            update_data["end"] = event_update.end.isoformat()
        if event_update.location is not None:
            update_data["location"] = event_update.location
        
        # Update the event
        success = manager.set_event(target_calendar, event_id, update_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update event"
            )
        
        # Get updated event for response
        events = manager.get_events(target_calendar)
        updated_event = None
        for evt in events:
            if evt.get("id") == event_id:
                updated_event = evt
                break
        
        return {
            "event": format_event_response(updated_event, target_calendar),
            "message": "Event updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise handle_calendar_error(e, "Update event")


@app.delete("/api/events/{event_id}", tags=["events"])
async def delete_event(
    event_id: str = Path(..., description="Unique event identifier"),
    manager: RadicaleCalendarManager = Depends(get_calendar_manager)
):
    """Permanently delete a calendar event"""
    try:
        # Find the event and its calendar
        target_calendar = None
        for calendar in manager.calendars:
            try:
                events = manager.get_events(calendar.name)
                for event in events:
                    if event.get("id") == event_id:
                        target_calendar = calendar.name
                        break
                if target_calendar:
                    break
            except Exception:
                continue
        
        if not target_calendar:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event '{event_id}' not found"
            )
        
        # Delete the event
        success = manager.delete_event(target_calendar, event_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete event"
            )
        
        return {
            "message": "Event deleted successfully",
            "deleted_event_id": event_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise handle_calendar_error(e, "Delete event")


@app.post("/api/chat/message", tags=["chat"], response_model=ChatResponse)
async def process_chat_message(
    message: ChatMessage,
    integration: CalendarMCPIntegration = Depends(get_mcp_integration)
):
    """Process natural language requests for calendar operations"""
    try:
        # Simple intent parsing (could be enhanced with NLP)
        msg_lower = message.message.lower()
        
        if any(word in msg_lower for word in ["add", "create", "schedule", "book"]):
            return ChatResponse(
                response="I'll help you create a new event. Could you please provide more details like the title, date, and time?",
                action="create_event",
                data={"intent": "create_event"},
                confidence=0.8,
                suggestions=["Schedule a meeting tomorrow at 2pm", "Add lunch appointment on Friday"]
            )
        elif any(word in msg_lower for word in ["show", "list", "what", "when"]):
            return ChatResponse(
                response="I'll show you your upcoming events. Would you like to see events for a specific time period?",
                action="list_events",
                data={"intent": "list_events"},
                confidence=0.9,
                suggestions=["Show today's events", "What's on my calendar this week?"]
            )
        elif any(word in msg_lower for word in ["delete", "remove", "cancel"]):
            return ChatResponse(
                response="I can help you delete an event. Which event would you like to remove?",
                action="delete_event",
                data={"intent": "delete_event"},
                confidence=0.8,
                suggestions=["Delete my 3pm meeting", "Cancel tomorrow's lunch"]
            )
        elif any(word in msg_lower for word in ["update", "change", "move", "reschedule"]):
            return ChatResponse(
                response="I can help you update an event. Which event would you like to modify and what changes do you want to make?",
                action="update_event",
                data={"intent": "update_event"},
                confidence=0.8,
                suggestions=["Move my meeting to 4pm", "Change location to conference room B"]
            )
        else:
            return ChatResponse(
                response="I can help you manage your calendar events. You can ask me to create, show, update, or delete events using natural language.",
                action="request_clarification",
                data={"intent": "unknown"},
                confidence=0.3,
                suggestions=[
                    "Schedule a meeting tomorrow at 2pm",
                    "Show my events for today",
                    "Delete my 3pm appointment"
                ]
            )
    except Exception as e:
        logger.error(f"Chat processing error: {e}")
        return ChatResponse(
            response="I'm sorry, I encountered an error processing your request. Please try again.",
            action="error",
            confidence=0.0
        )


@app.get("/api/chat/suggestions", tags=["chat"])
async def get_chat_suggestions():
    """Retrieve suggested natural language commands"""
    return {
        "suggestions": [
            {
                "text": "Schedule a meeting tomorrow at 2pm",
                "category": "create",
                "description": "Create a new calendar event"
            },
            {
                "text": "Show my events for today",
                "category": "query",
                "description": "List today's events"
            },
            {
                "text": "What's on my calendar this week?",
                "category": "query",
                "description": "View weekly calendar"
            },
            {
                "text": "Move my 3pm meeting to 4pm",
                "category": "update",
                "description": "Reschedule an existing event"
            },
            {
                "text": "Delete tomorrow's lunch appointment",
                "category": "delete",
                "description": "Remove an event from calendar"
            },
            {
                "text": "Add a reminder for my doctor appointment",
                "category": "create",
                "description": "Create a reminder event"
            }
        ],
        "categories": ["create", "query", "update", "delete", "general"]
    }


# --- Custom OpenAPI Schema ---

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="ARK Calendar API",
        version="2.0.0",
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://ark-calendar.com/logo.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# --- Exception Handlers ---

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "ValidationError",
            "message": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "timestamp": datetime.now().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "enhanced_backend_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )