import os
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import caldav
import vobject

# Google Calendar API setup
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_google_credentials():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_info(json.loads(open('token.json').read()))
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return creds

def sync_calendars():
    # Set up Google Calendar API
    creds = get_google_credentials()
    google_service = build('calendar', 'v3', credentials=creds)
    
    # Set up Radicale connection
    radicale_url = "https://localhost:5232/ilyag/"
    client = caldav.DAVClient(url=radicale_url, username="ilyag", password="admin")
    principal = client.principal()
    
    # Get calendars from Radicale
    radicale_calendars = principal.calendars()
    
    # Get calendars from Google
    google_calendars = google_service.calendarList().list().execute()
    
    # Implement your synchronization logic here
    # For each calendar in both systems:
    #   1. Compare events
    #   2. Add missing events
    #   3. Update changed events
    #   4. Remove deleted events
    
    # Example: Sync events from a specific Google calendar to Radicale
    calendar_id = 'primary'  # Use 'primary' for the main calendar
    time_min = datetime.datetime.utcnow().isoformat() + 'Z'
    
    # Get events from Google
    events_result = google_service.events().list(
        calendarId=calendar_id,
        timeMin=time_min,
        maxResults=100,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    google_events = events_result.get('items', [])
    
    # Find or create corresponding calendar in Radicale
    radicale_calendar = None
    for cal in radicale_calendars:
        if cal.name == "Google Primary":  # Use a suitable naming convention
            radicale_calendar = cal
            break
    
    if not radicale_calendar:
        radicale_calendar = principal.make_calendar(name="Google Primary")
    
    # Add Google events to Radicale
    for event in google_events:
        # Create iCalendar object
        cal = vobject.iCalendar()
        vevent = cal.add('vevent')
        
        # Set basic properties
        vevent.add('summary').value = event.get('summary', 'No Title')
        vevent.add('uid').value = event['id']
        
        # Set start time
        start = event['start'].get('dateTime', event['start'].get('date'))
        vevent.add('dtstart').value = start
        
        # Set end time
        end = event['end'].get('dateTime', event['end'].get('date'))
        vevent.add('dtend').value = end
        
        # Add the event to Radicale
        radicale_calendar.add_event(cal.serialize())

if __name__ == '__main__':
    sync_calendars()
