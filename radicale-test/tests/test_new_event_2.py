# creates a new event on local radicale server
# if there is no default calendar, creates a default calendar first

import caldav
import sys
import subprocess
import time
import socket
import os
from datetime import datetime, timedelta
import requests
from requests.exceptions import ConnectionError, Timeout

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

def add_calendar_event(url, username, password):
    """Add a new event to the calendar."""
    try:
        # Connect to the CalDAV server
        client = caldav.DAVClient(url=url, username=username, password=password)
        
        # Get principal (user)
        principal = client.principal()
        
        # Get calendars
        calendars = principal.calendars()
        if not calendars:
            print("No calendars found! Creating a new one...")
            # Create a default calendar
            calendar = principal.make_calendar(name="Default Calendar")
        else:
            calendar = calendars[0]  # Use the first calendar
        
        print(f"Using calendar: {calendar.name}")
        
        # Event details
        event_summary = "Team Meeting"
        event_location = "Conference Room"
        event_description = "Weekly team sync-up"
        
        # Event start and end times
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
        return False

def main():
    # Configuration
    url = "http://localhost:5232"  # Default Radicale URL
    username = "ilyag"  # Empty for default Radicale installation without auth
    password = "admin"  # Empty for default Radicale installation without auth
    
    # Check if Radicale is running
    if not check_radicale_running():
        print("Radicale service is not running.")
        
        # Try to start it
        if not start_radicale():
            print("Could not start Radicale automatically.")
            print("\nPlease try one of these options:")
            print("1. Run in a separate terminal: radicale --storage-filesystem-folder ~/radicale/collections")
            print("2. Or with sudo: sudo radicale")
            print("3. Create a configuration file with: mkdir -p ~/.config/radicale && echo '[storage]\\nfilesystem_folder = ~/radicale/collections' > ~/.config/radicale/config")
            sys.exit(1)
    
    # Add the calendar event
    if add_calendar_event(url, username, password):
        print("Operation completed successfully.")
    else:
        print("Failed to add calendar event.")
        sys.exit(1)

if __name__ == "__main__":
    main()
