#!/usr/bin/env python3
"""
API Schema Validation Script

This script validates the OpenAPI specification and tests the API endpoints
to ensure everything works correctly together.

Usage:
    python validate_api_schema.py [--server-url http://localhost:8000]
"""

import json
import yaml
import requests
import argparse
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List

# ANSI color codes for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def log_info(message: str):
    print(f"{Colors.CYAN}ℹ {message}{Colors.END}")

def log_success(message: str):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def log_error(message: str):
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def log_warning(message: str):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

def log_header(message: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{message}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}")

class APIValidator:
    """Validates API schema and functionality"""
    
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'ARK-Calendar-API-Validator/1.0'
        })
    
    def validate_openapi_spec(self) -> bool:
        """Validate the OpenAPI specification file"""
        log_header("Validating OpenAPI Specification")
        
        try:
            with open('calendar-api-spec.yaml', 'r') as file:
                spec = yaml.safe_load(file)
            
            # Check required OpenAPI fields
            required_fields = ['openapi', 'info', 'paths']
            for field in required_fields:
                if field not in spec:
                    log_error(f"Missing required field: {field}")
                    return False
            
            log_success(f"OpenAPI version: {spec['openapi']}")
            log_success(f"API title: {spec['info']['title']}")
            log_success(f"API version: {spec['info']['version']}")
            
            # Validate paths
            paths = spec.get('paths', {})
            log_success(f"Found {len(paths)} API endpoints")
            
            # Check for required endpoints
            required_endpoints = [
                '/api/events',
                '/api/calendars',
                '/api/chat/message'
            ]
            
            for endpoint in required_endpoints:
                if endpoint in paths:
                    log_success(f"Required endpoint found: {endpoint}")
                else:
                    log_error(f"Missing required endpoint: {endpoint}")
                    return False
            
            # Validate schemas
            components = spec.get('components', {})
            schemas = components.get('schemas', {})
            log_success(f"Found {len(schemas)} schema definitions")
            
            required_schemas = ['Event', 'EventCreate', 'Calendar', 'ChatMessage']
            for schema in required_schemas:
                if schema in schemas:
                    log_success(f"Required schema found: {schema}")
                else:
                    log_error(f"Missing required schema: {schema}")
                    return False
            
            log_success("OpenAPI specification is valid")
            return True
            
        except FileNotFoundError:
            log_error("calendar-api-spec.yaml not found")
            return False
        except yaml.YAMLError as e:
            log_error(f"YAML parsing error: {e}")
            return False
        except Exception as e:
            log_error(f"Validation error: {e}")
            return False
    
    def test_health_endpoint(self) -> bool:
        """Test the health check endpoint"""
        log_header("Testing Health Endpoint")
        
        try:
            response = self.session.get(f"{self.server_url}/")
            
            if response.status_code == 200:
                data = response.json()
                log_success(f"Health check passed: {data.get('message', 'OK')}")
                log_info(f"API version: {data.get('version', 'Unknown')}")
                return True
            else:
                log_error(f"Health check failed: HTTP {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            log_error(f"Cannot connect to API server at {self.server_url}")
            log_warning("Make sure the API server is running")
            return False
        except Exception as e:
            log_error(f"Health check error: {e}")
            return False
    
    def test_calendars_endpoint(self) -> bool:
        """Test the calendars listing endpoint"""
        log_header("Testing Calendars Endpoint")
        
        try:
            response = self.session.get(f"{self.server_url}/api/calendars")
            
            if response.status_code == 200:
                data = response.json()
                calendars = data.get('calendars', [])
                count = data.get('count', 0)
                
                log_success(f"Found {count} calendars")
                for i, calendar in enumerate(calendars[:3], 1):  # Show first 3
                    name = calendar.get('name', 'Unknown')
                    log_info(f"  {i}. {name}")
                
                return True
            elif response.status_code == 503:
                log_warning("Calendar service unavailable (CalDAV server may be down)")
                return False
            else:
                log_error(f"Calendars endpoint failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            log_error(f"Calendars test error: {e}")
            return False
    
    def test_events_endpoint(self) -> bool:
        """Test the events listing endpoint"""
        log_header("Testing Events Endpoint")
        
        try:
            # Test basic event listing
            response = self.session.get(f"{self.server_url}/api/events")
            
            if response.status_code == 200:
                data = response.json()
                events = data.get('events', [])
                total_count = data.get('total_count', 0)
                
                log_success(f"Found {total_count} events")
                
                # Test with date filtering
                start_date = datetime.now().strftime("%Y-%m-%dT00:00:00Z")
                end_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%dT23:59:59Z")
                
                params = {
                    'start_date': start_date,
                    'end_date': end_date,
                    'limit': 5
                }
                
                response = self.session.get(f"{self.server_url}/api/events", params=params)
                if response.status_code == 200:
                    filtered_data = response.json()
                    filtered_events = filtered_data.get('events', [])
                    log_success(f"Date filtering works: {len(filtered_events)} events in next 7 days")
                else:
                    log_warning("Date filtering test failed")
                
                return True
            else:
                log_error(f"Events endpoint failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            log_error(f"Events test error: {e}")
            return False
    
    def test_event_creation(self) -> bool:
        """Test event creation endpoint"""
        log_header("Testing Event Creation")
        
        # Prepare test event data
        test_event = {
            "calendar_name": "Default Calendar",
            "summary": "API Validation Test Event",
            "description": "Test event created by validation script",
            "start": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT14:00:00Z"),
            "end": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT15:00:00Z"),
            "location": "Test Location"
        }
        
        try:
            response = self.session.post(
                f"{self.server_url}/api/events",
                json=test_event
            )
            
            if response.status_code == 201:
                data = response.json()
                event_id = data.get('event_id')
                log_success(f"Event created successfully: {event_id}")
                
                # Test event retrieval
                if event_id:
                    get_response = self.session.get(f"{self.server_url}/api/events/{event_id}")
                    if get_response.status_code == 200:
                        log_success("Event retrieval by ID works")
                    else:
                        log_warning("Event retrieval by ID failed")
                    
                    # Test event deletion (cleanup)
                    delete_response = self.session.delete(f"{self.server_url}/api/events/{event_id}")
                    if delete_response.status_code == 200:
                        log_success("Event deletion works (test cleanup complete)")
                    else:
                        log_warning("Event deletion failed (manual cleanup may be needed)")
                
                return True
            else:
                log_error(f"Event creation failed: HTTP {response.status_code}")
                if response.status_code == 400:
                    try:
                        error_data = response.json()
                        log_error(f"Error details: {error_data.get('message', 'Unknown error')}")
                    except:
                        pass
                return False
                
        except Exception as e:
            log_error(f"Event creation test error: {e}")
            return False
    
    def test_chat_endpoint(self) -> bool:
        """Test the chat/natural language endpoint"""
        log_header("Testing Chat Endpoint")
        
        test_messages = [
            "Schedule a meeting tomorrow at 2pm",
            "Show my events for today",
            "What's on my calendar this week?"
        ]
        
        try:
            for message in test_messages:
                chat_data = {"message": message}
                response = self.session.post(
                    f"{self.server_url}/api/chat/message",
                    json=chat_data
                )
                
                if response.status_code == 200:
                    data = response.json()
                    action = data.get('action', 'none')
                    confidence = data.get('confidence', 0)
                    log_success(f"Chat processed: '{message}' -> action: {action} (confidence: {confidence})")
                else:
                    log_warning(f"Chat failed for: '{message}' (HTTP {response.status_code})")
            
            # Test chat suggestions
            response = self.session.get(f"{self.server_url}/api/chat/suggestions")
            if response.status_code == 200:
                data = response.json()
                suggestions = data.get('suggestions', [])
                log_success(f"Chat suggestions endpoint works: {len(suggestions)} suggestions available")
            else:
                log_warning("Chat suggestions endpoint failed")
            
            return True
            
        except Exception as e:
            log_error(f"Chat test error: {e}")
            return False
    
    def test_error_handling(self) -> bool:
        """Test error handling for invalid requests"""
        log_header("Testing Error Handling")
        
        try:
            # Test invalid event creation
            invalid_event = {
                "calendar_name": "Nonexistent Calendar",
                "summary": "",  # Empty summary should fail
                "start": "invalid-date"  # Invalid date format
            }
            
            response = self.session.post(
                f"{self.server_url}/api/events",
                json=invalid_event
            )
            
            if response.status_code in [400, 404]:
                log_success("Invalid event creation properly rejected")
            else:
                log_warning(f"Invalid event creation returned unexpected status: {response.status_code}")
            
            # Test nonexistent event retrieval
            response = self.session.get(f"{self.server_url}/api/events/nonexistent-id")
            if response.status_code == 404:
                log_success("Nonexistent event properly returns 404")
            else:
                log_warning(f"Nonexistent event returned unexpected status: {response.status_code}")
            
            return True
            
        except Exception as e:
            log_error(f"Error handling test failed: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all validation tests"""
        log_header("ARK Calendar API Validation Suite")
        log_info(f"Testing server: {self.server_url}")
        
        tests = [
            ("OpenAPI Specification", self.validate_openapi_spec),
            ("Health Endpoint", self.test_health_endpoint),
            ("Calendars Endpoint", self.test_calendars_endpoint),
            ("Events Endpoint", self.test_events_endpoint),
            ("Event Creation", self.test_event_creation),
            ("Chat Endpoint", self.test_chat_endpoint),
            ("Error Handling", self.test_error_handling)
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                log_error(f"Test '{test_name}' crashed: {e}")
                results.append((test_name, False))
        
        # Summary
        log_header("Validation Summary")
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status_icon = "✓" if result else "✗"
            status_color = Colors.GREEN if result else Colors.RED
            print(f"{status_color}{status_icon} {test_name}{Colors.END}")
        
        print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.END}")
        
        if passed == total:
            log_success("🎉 All validation tests passed!")
            return True
        else:
            log_error("❌ Some validation tests failed")
            return False

def main():
    parser = argparse.ArgumentParser(description="Validate ARK Calendar API")
    parser.add_argument(
        '--server-url',
        default='http://localhost:8000',
        help='API server URL (default: http://localhost:8000)'
    )
    
    args = parser.parse_args()
    
    validator = APIValidator(args.server_url)
    success = validator.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()