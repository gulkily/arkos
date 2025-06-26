# add test event(s) to local radicale instance
# takes command-line arguments

import caldav
import sys
import subprocess
import time
import socket
import os
import argparse
from datetime import datetime, timedelta, date
import requests
from requests.exceptions import ConnectionError, Timeout

def parse_arguments():
    """Parse command line arguments for the script."""
    parser = argparse.ArgumentParser(description='Add an event to a Radicale CalDAV server.')
    
    # Server connection arguments
    parser.add_argument('--url', default='http://localhost:5232',
                        help='URL of the Radicale server (default: http://localhost:5232)')
    parser.add_argument('--username', default='ilyag',
                        help='Username for authentication (default: empty)')
    parser.add_argument('--password', default='admin',
                        help='Password for authentication (default: empty)')
    
    # Event details arguments
    parser.add_argument('--summary', default='Meeting',
                        help='Event summary/title (default: "Meeting")')
    parser.add_argument('--location', default='',
                        help='Event location (default: empty)')
    parser.add_argument('--description', default='',
                        help='Event description (default: empty)')
    
    # Date and time arguments
    parser.add_argument('--date', 
                        help='Event date in YYYY-MM-DD format (default: tomorrow)')
    parser.add_argument('--start-time', default='10:00',
                        help='Event start time in HH:MM format (default: 10:00)')
    parser.add_argument('--duration', type=int, default=60,
                        help='Event duration in minutes (default: 60)')
    
    # Calendar selection
    parser.add_argument('--calendar-name',
                        help='Specific calendar name to use (default: first available)')
    
    # Auto-start option
    parser.add_argument('--no-autostart', action='store_true',
                        help='Do not attempt to start Radicale if not running')

    return parser.parse_args()

def create_radicale_config():
    """Create a basic Radicale configuration file in the user's home directory."""
    config_dir = os.path.expanduser("~/.config/radicale")
    collections_dir = os.path.expanduser("~/radicale/collections")
    
    # Create directories if they don't exist
    os.makedirs(config_dir, exist_ok=True)
    os.makedirs(collections_dir, exist_ok=True)
    
    # Create config file
    config_path = os.path.join(config_dir, "config")
    with open(config_path, "w") as f:
        f.write(f"""[storage]
filesystem_folder = {collections_dir}

[server]
hosts = localhost:5232
""")
    
    return config_path

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
                time.sleep(1)
        except Exception as e:
            print(f"Error checking service: {e}")
    
    return False

def start_radicale():
    """Try to start the Radicale service with user permissions."""
    try:
        # Create config file with user-owned storage location
        config_path = create_radicale_config()
        print(f"Created configuration file at {config_path}")
        
        # Start Radicale in the background
        print("Attempting to start Radicale with user permissions...")
        process = subprocess.Popen(["radicale"], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE)
        
        # Wait a moment for the service to start
        time.sleep(2)
        
        # Check if it's running now
        if check_radicale_running():
            print("Radicale service started successfully!")
            return True
        else:
            # Check for any error message
            stderr = process.stderr.read().decode('utf-8')
            if stderr:
                print(f"Error starting Radicale: {stderr}")
            else:
                print("Failed to start Radicale service.")
            return False
    except subprocess.CalledProcessError as e:
        print(f"Error starting Radicale: {e}")
        return False
    except FileNotFoundError:
        print("Radicale command not found. Make sure it's installed and in your PATH.")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def add_calendar_event(args):
    """Add a new event to the calendar with the provided arguments."""
    try:
        # Connect to the CalDAV server
        client = caldav.DAVClient(url=args.url, username=args.username, password=args.password)
        
        # Get principal (user)
        principal = client.principal()
        
        # Get calendars
        calendars = principal.calendars()
        if not calendars:
            print("No calendars found! Creating a new one...")
            # Create a default calendar
            calendar = principal.make_calendar(name="Default Calendar")
        else:
            # Try to find the requested calendar if specified
            calendar = None
            if args.calendar_name:
                for cal in calendars:
                    if cal.name.lower() == args.calendar_name.lower():
                        calendar = cal
                        break
                if not calendar:
                    print(f"Calendar '{args.calendar_name}' not found. Available calendars:")
                    for idx, cal in enumerate(calendars):
                        print(f"  {idx+1}. {cal.name}")
                    print(f"Creating new calendar '{args.calendar_name}'...")
                    calendar = principal.make_calendar(name=args.calendar_name)
            else:
                calendar = calendars[0]  # Use the first calendar
        
        print(f"Using calendar: {calendar.name}")
        
        # Parse date and time
        if args.date:
            event_date = date.fromisoformat(args.date)
        else:
            event_date = date.today() + timedelta(days=1)  # Tomorrow
            
        # Parse time components
        hour, minute = map(int, args.start_time.split(':'))
        
        # Create start and end times
        start_time = datetime.combine(event_date, datetime.min.time().replace(hour=hour, minute=minute))
        end_time = start_time + timedelta(minutes=args.duration)
        
        # Create the event
        event = calendar.save_event(
            dtstart=start_time,
            dtend=end_time,
            summary=args.summary,
            location=args.location,
            description=args.description
        )
        
        print(f"Event '{args.summary}' created successfully!")
        print(f"Event UID: {event.id}")
        print(f"Date: {start_time.strftime('%Y-%m-%d')}")
        print(f"Time: {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}")
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
    except ValueError as e:
        print(f"Invalid date/time format: {e}")
        print("Please use YYYY-MM-DD for date and HH:MM for time.")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
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
        
        # Try to start it if autostart is enabled
        if not args.no_autostart:
            if not start_radicale():
                print("Could not start Radicale automatically.")
                print("\nPlease try one of these options:")
                print("1. Run in a separate terminal: radicale --storage-filesystem-folder ~/radicale/collections")
                print("2. Or with sudo: sudo radicale")
                print("3. Create a configuration file with: mkdir -p ~/.config/radicale && echo '[storage]\\nfilesystem_folder = ~/radicale/collections' > ~/.config/radicale/config")
                print("\nOr run this script with --no-autostart to skip the autostart attempt.")
                sys.exit(1)
        else:
            print("Autostart is disabled. Please start Radicale manually.")
            sys.exit(1)
    
    # Add the calendar event
    if add_calendar_event(args):
        print("Operation completed successfully.")
    else:
        print("Failed to add calendar event.")
        sys.exit(1)

if __name__ == "__main__":
    main()
