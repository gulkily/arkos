# create a test event on local radicale instance
# a default calendar needs to already exist for this script to work

import caldav
from datetime import datetime, timedelta

# Connection details for your Radicale server
url = "http://localhost:5232"  # Default Radicale URL - adjust if needed
username = "ilyag"     # Your Radicale username
password = "admin"     # Your Radicale password

# Connect to the CalDAV server
client = caldav.DAVClient(url=url, username=username, password=password)

# Get principal (user)
principal = client.principal()

# Get default calendar or a specific calendar by name
# Option 1: Get default calendar
calendars = principal.calendars()
if not calendars:
    print("No calendars found!")
    exit(1)
calendar = calendars[0]  # Use the first calendar

# Option 2: Find a specific calendar by name
# calendar = None
# for cal in principal.calendars():
#     if cal.name == "your_calendar_name":
#         calendar = cal
#         break
# if not calendar:
#     print("Calendar not found!")
#     exit(1)

# Event details
event_summary = "Team Meeting"
event_location = "Conference Room"
event_description = "Weekly team sync-up"

# Event start and end times (adjust as needed)
start_time = datetime.now() + timedelta(days=1)  # Tomorrow
end_time = start_time + timedelta(hours=1)       # 1 hour duration

# Create the event
event = calendar.save_event(
    dtstart=start_time,
    dtend=end_time,
    summary=event_summary,
    location=event_location,
    description=event_description
)

print(f"Event '{event_summary}' created successfully!")
print(f"Event UID: {event.id}")
