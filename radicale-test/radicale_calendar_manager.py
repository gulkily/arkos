"""
RadicaleCalendarManager - Calendar Operations Interface for Radicale Server

This module provides a high-level interface for interacting with a Radicale CalDAV server.
It handles calendar operations like creating, reading, updating and deleting events,
as well as managing connections and calendar discovery.

Key Features:
- Calendar server connection management
- Event creation, updates and deletion
- Event querying with date range filtering
- Calendar discovery and selection
- iCalendar data parsing and formatting

Example usage:
    manager = RadicaleCalendarManager(url="http://localhost:5232",
                                    username="user",
                                    password="pass")
    manager.connect()

    # Get events for next 30 days
    events = manager.get_events("my_calendar")

    # Create new event
    event_data = {
        "summary": "Meeting",
        "start": "2023-06-01T10:00:00",
        "end": "2023-06-01T11:00:00",
        "location": "Office",
        "description": "Team sync-up"
    }
    event_id = manager.add_event("my_calendar", event_data)

    # Update event
    update_data = {"summary": "Updated Meeting"}
    manager.set_event("my_calendar", event_id, update_data)

    # Delete event
    manager.delete_event("my_calendar", event_id)

Dependencies:
    - caldav: For CalDAV protocol communication
    - logging: For operation logging
    - datetime: For date/time handling

Author: Unknown
License: Unknown
"""

import caldav
import logging
from datetime import datetime, timedelta
import re
import uuid

# Configure logging
logger = logging.getLogger("radicale-calendar-manager")

class RadicaleCalendarManager:
    """
    A class to manage calendar operations with a Radicale server using CalDAV protocol.
    Handles connections, event creation, updates, deletions and queries.
    """
    def __init__(self, url, username, password):
        """Initialize connection parameters and CalDAV client"""
        self.url = url
        self.username = username
        self.password = password
        self.client = caldav.DAVClient(url=url, username=username, password=password)
        self.principal = None
        self.calendars = []

    def connect(self):
        """
        Establish connection to Radicale server and fetch available calendars.
        Returns True if successful, False otherwise.
        """
        try:
            self.principal = self.client.principal()
            self.calendars = self.principal.calendars()
            if not self.calendars:
                logger.warning("No calendars found in Radicale")
                return False
            logger.info(f"Connected to Radicale, found {len(self.calendars)} calendars")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Radicale: {e}")
            return False

    def get_calendar(self, calendar_name=None):
        """
        Retrieve a calendar by name. If no name provided, returns the first available calendar.
        Returns None if calendar not found.
        """
        if not calendar_name:
            return self.calendars[0] if self.calendars else None

        for calendar in self.calendars:
            if calendar.name.lower() == calendar_name.lower():
                return calendar
        return None

    def get_events(self, calendar_name=None, start_date=None, end_date=None):
        """
        Fetch events from a calendar within the specified date range.

        Args:
            calendar_name (str, optional): Name of calendar to fetch events from.
                                         If None, uses the first available calendar.
            start_date (datetime, optional): Start of date range to fetch events.
                                           If None, uses current datetime.
            end_date (datetime, optional): End of date range to fetch events.
                                         If None, defaults to start_date + 30 days.

        Returns:
            list[dict]: List of event dictionaries containing:
                {
                    "id": str,          # Unique event identifier
                    "summary": str,     # Event title
                    "start": str,       # Start time in iCalendar format
                    "end": str,         # End time in iCalendar format
                    "location": str,    # Event location
                    "description": str  # Event description
                }

        Raises:
            ValueError: If calendar not found
        """
        calendar = self.get_calendar(calendar_name)
        if not calendar:
            raise ValueError("Calendar not found")

        if start_date is None:
            start_date = datetime.now()
        if end_date is None:
            end_date = start_date + timedelta(days=30)

        events = calendar.date_search(start=start_date, end=end_date)
        return [self._format_event(event) for event in events]

    def add_event(self, calendar_name, event_data):
        """
        Create a new calendar event with specified details.

        Args:
            calendar_name (str): Name of the calendar to add event to
            event_data (dict): Event details with the following structure:
                {
                    "summary": str,     # Required - Event title
                    "start": str,       # Required - ISO format datetime (e.g. "2023-06-01T10:00:00")
                    "end": str,         # Optional - ISO format datetime. Defaults to start + 1 hour
                    "location": str,    # Optional - Event location
                    "description": str  # Optional - Event description
                }

        Returns:
            str: ID of the created event, used for future updates or deletion

        Raises:
            ValueError: If calendar not found
            ValueError: If required fields are missing
            ValueError: If datetime format is invalid
        """
        calendar = self.get_calendar(calendar_name)
        if not calendar:
            raise ValueError("Calendar not found")

        # Check required fields
        if "summary" not in event_data:
            raise ValueError("Event summary is required")
        if "start" not in event_data:
            raise ValueError("Event start time is required")

        try:
            summary = event_data.get("summary")
            location = event_data.get("location", "")
            description = event_data.get("description", "")
            start_time = datetime.fromisoformat(event_data.get("start"))

            if "end" in event_data:
                end_time = datetime.fromisoformat(event_data.get("end"))
            else:
                end_time = start_time + timedelta(hours=1)
        except ValueError as e:
            raise ValueError(f"Invalid datetime format: {e}")

        # Create a unique event ID
        event_id = str(uuid.uuid4())

        # Create and save the event
        try:
            event = calendar.save_event(
                dtstart=start_time,
                dtend=end_time,
                summary=summary,
                location=location,
                description=description,
                uid=event_id
            )
            return event.id
        except Exception as e:
            logger.error(f"Failed to create event: {e}")
            raise ValueError(f"Failed to create event: {e}")

    def set_event(self, calendar_name, event_id, event_data):
        """
        Update an existing event's properties.

        Args:
            calendar_name (str): Name of the calendar containing the event
            event_id (str): Event ID (obtained from get_events() response or add_event())
            event_data (dict): Fields to update, can contain:
                {
                    "summary": str,     # Optional - New event title
                    "location": str,    # Optional - New location
                    "description": str, # Optional - New description
                    "start": str,       # Optional - New start time (ISO format)
                    "end": str,         # Optional - New end time (ISO format)
                }

        Returns:
            bool: True if update successful

        Raises:
            ValueError: If calendar not found
            ValueError: If event not found
        """
        calendar = self.get_calendar(calendar_name)
        if not calendar:
            raise ValueError("Calendar not found")

        event = self._find_event_by_id(calendar, event_id)
        if not event:
            raise ValueError(f"Event with ID {event_id} not found")

        try:
            # Get the current event data
            vcal = event.vobject_instance
            vevent = vcal.vevent

            # Update properties if provided
            if "summary" in event_data:
                vevent.summary.value = event_data["summary"]
            if "location" in event_data:
                if hasattr(vevent, 'location'):
                    vevent.location.value = event_data["location"]
                else:
                    vevent.add('location').value = event_data["location"]
            if "description" in event_data:
                if hasattr(vevent, 'description'):
                    vevent.description.value = event_data["description"]
                else:
                    vevent.add('description').value = event_data["description"]

            # Handle date changes if provided
            if "start" in event_data:
                start_time = datetime.fromisoformat(event_data["start"])
                vevent.dtstart.value = start_time

            if "end" in event_data:
                end_time = datetime.fromisoformat(event_data["end"])
                vevent.dtend.value = end_time

            # Save the updated event
            event.save()
            return True
        except Exception as e:
            logger.error(f"Failed to update event: {e}")
            raise ValueError(f"Failed to update event: {e}")

    def delete_event(self, calendar_name, event_id):
        """
        Delete an event from the calendar by its ID.

        Args:
            calendar_name (str): Name of the calendar containing the event
            event_id (str): Event ID (obtained from get_events() response or add_event())

        Returns:
            bool: True if deletion successful

        Raises:
            ValueError: If calendar not found
            ValueError: If event not found
        """
        calendar = self.get_calendar(calendar_name)
        if not calendar:
            raise ValueError("Calendar not found")

        event = self._find_event_by_id(calendar, event_id)
        if not event:
            raise ValueError(f"Event with ID {event_id} not found")

        try:
            event.delete()
            return True
        except Exception as e:
            logger.error(f"Failed to delete event: {e}")
            raise ValueError(f"Failed to delete event: {e}")

    def _find_event_by_id(self, calendar, event_id):
        """
        Helper method to find an event in a calendar by its ID.
        Returns the event object or None if not found.
        """
        try:
            events = calendar.events()
            for event in events:
                # Try to match by UID in the vobject_instance
                try:
                    vcal = event.vobject_instance
                    vevent = vcal.vevent
                    uid = getattr(vevent, 'uid', None)

                    if uid and uid.value == event_id:
                        return event
                except:
                    pass

                # Also try direct event.id match
                if event.id == event_id:
                    return event

                # Try URL-based matching as a fallback
                if event_id in str(event.url):
                    return event

            # If we can't find the event by ID, try a broader search
            # Calculate a start date that's 30 days in the past and 60 days in the future
            start_date = datetime.now() - timedelta(days=30)
            end_date = datetime.now() + timedelta(days=60)

            # Try to find events in this range and match by UID
            for event in calendar.date_search(start=start_date, end=end_date):
                try:
                    vcal = event.vobject_instance
                    vevent = vcal.vevent
                    uid = getattr(vevent, 'uid', None)

                    if uid and uid.value == event_id:
                        return event
                except:
                    pass

            return None
        except Exception as e:
            logger.error(f"Error finding event: {e}")
            return None

    def _format_event(self, event):
        """
        Helper method to format an event's data for API response.
        Extracts and returns relevant properties from iCalendar format.
        """
        try:
            vcal = event.vobject_instance
            vevent = vcal.vevent

            # Extract properties, providing defaults for missing ones
            summary = getattr(vevent, 'summary', None)
            summary = summary.value if summary else ""

            dtstart = getattr(vevent, 'dtstart', None)
            dtstart = dtstart.value.isoformat() if dtstart else ""

            dtend = getattr(vevent, 'dtend', None)
            dtend = dtend.value.isoformat() if dtend else ""

            location = getattr(vevent, 'location', None)
            location = location.value if location else ""

            description = getattr(vevent, 'description', None)
            description = description.value if description else ""

            # Extract UID from the event - this is the stable identifier
            uid = getattr(vevent, 'uid', None)
            uid = uid.value if uid else None

            # If we couldn't extract a UID, fall back to the event's ID or URL
            event_id = uid or event.id or str(event.url).split('/')[-1]

            return {
                "id": event_id,  # Use the extracted UID or fallback
                "summary": summary,
                "start": dtstart,
                "end": dtend,
                "location": location,
                "description": description
            }
        except Exception as e:
            logger.error(f"Error formatting event: {e}")
            # Return basic info if detailed extraction fails
            return {
                "id": str(event.url).split('/')[-1] if event.url else None,  # Try to get ID from URL
                "summary": "Error extracting event details",
                "start": "",
                "end": "",
                "location": "",
                "description": str(e)
            }