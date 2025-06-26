#!/usr/bin/env python3
# get_caldav_events.py - Verify ability to fetch events from Radicale CalDAV server

import caldav
import sys
import socket
import argparse
from datetime import datetime, timedelta, date
from requests.exceptions import ConnectionError, Timeout

def parse_arguments():
    """Parse command line arguments for the script."""
    parser = argparse.ArgumentParser(description='Verify data access from a Radicale CalDAV server.')
    
    # Server connection arguments
    parser.add_argument('--url', default='http://localhost:5232',
                        help='URL of the Radicale server (default: http://localhost:5232)')
    parser.add_argument('--username', default='ilyag',
                        help='Username for authentication (default: ilyag)')
    parser.add_argument('--password', default='admin',
                        help='Password for authentication (default: admin)')
    
    # Calendar selection
    parser.add_argument('--calendar-name',
                        help='Specific calendar name to use (default: first available)')
    
    # Date range arguments
    parser.add_argument('--days', type=int, default=30,
                        help='Number of days to look ahead for events (default: 30)')
    
    return parser.parse_args()

def check_radicale_running(host="localhost", port=5232, max_retries=3):
    """Check if Radicale is running on the specified host and port."""
    for attempt in range(max_retries):
        try:
            # Try to make a simple connection to the server
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                return True
            else:
                print(f"Radicale not responding (attempt {attempt+1}/{max_retries})")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(1)
        except Exception as e:
            print(f"Error checking service: {e}")
    
    return False

def get_calendar_events(args):
    """Retrieve and display events from the calendar server."""
    try:
        # Connect to the CalDAV server
        print(f"Connecting to {args.url} with username: {args.username}")
        client = caldav.DAVClient(url=args.url, username=args.username, password=args.password)
        
        # Get principal (user)
        principal = client.principal()
        print(f"Successfully connected as: {principal}")
        
        # Get calendars
        calendars = principal.calendars()
        if not calendars:
            print("No calendars found!")
            return False
        
        print(f"Found {len(calendars)} calendar(s):")
        for idx, cal in enumerate(calendars):
            print(f"  {idx+1}. {cal.name}")
        
        # Select calendar to use
        calendar = None
        if args.calendar_name:
            for cal in calendars:
                if cal.name.lower() == args.calendar_name.lower():
                    calendar = cal
                    break
            if not calendar:
                print(f"Calendar '{args.calendar_name}' not found. Using first available calendar.")
                calendar = calendars[0]
        else:
            calendar = calendars[0]  # Use the first calendar
        
        print(f"\nUsing calendar: {calendar.name}")
        
        # Set up date range for events
        start_date = date.today()
        end_date = start_date + timedelta(days=args.days)
        
        print(f"Searching for events between {start_date} and {end_date}")
        
        # Get events within date range
        events = calendar.date_search(start=start_date, end=end_date)
        
        if not events:
            print(f"No events found in the next {args.days} days.")
            return True
        
        print(f"\nFound {len(events)} event(s):")
        for idx, event in enumerate(events):
            event_data = event.data
            ical_data = event.icalendar_component
            
            # Extract basic event information
            summary = ical_data.get('summary', 'No Title')
            start = ical_data.get('dtstart')
            end = ical_data.get('dtend')
            location = ical_data.get('location', 'No Location')
            
            start_str = start.dt.strftime('%Y-%m-%d %H:%M') if hasattr(start.dt, 'strftime') else str(start.dt)
            end_str = end.dt.strftime('%Y-%m-%d %H:%M') if hasattr(end.dt, 'strftime') else str(end.dt)
            
            print(f"\nEvent {idx+1}:")
            print(f"  Summary: {summary}")
            print(f"  Start: {start_str}")
            print(f"  End: {end_str}")
            print(f"  Location: {location}")
            print(f"  UID: {event.id}")
        
        return True
        
    except ConnectionError as e:
        print(f"Connection error: {e}")
        print("Make sure Radicale is running and accessible.")
        return False
    except caldav.lib.error.AuthorizationError:
        print("Authentication failed. Check your username and password.")
        return False
    except caldav.lib.error.NotFoundError:
        print("Calendar or resource not found.")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    # Parse command-line arguments
    args = parse_arguments()
    
    # Extract host and port from URL
    from urllib.parse import urlparse
    parsed_url = urlparse(args.url)
    host = parsed_url.hostname or "localhost"
    port = parsed_url.port or 5232
    
    # Check if Radicale is running
    if not check_radicale_running(host, port):
        print(f"Radicale service is not running at {args.url}")
        print("Please start Radicale before running this script.")
        sys.exit(1)
    
    print("✓ Radicale server is running")
    
    # Get calendar events
    if get_calendar_events(args):
        print("\n✓ Successfully retrieved calendar data")
        sys.exit(0)
    else:
        print("\n✗ Failed to retrieve calendar data")
        sys.exit(1)

if __name__ == "__main__":
    main()
