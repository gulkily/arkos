#!/usr/bin/env python3
"""
Enhanced MCP Client Test Suite

Tests the MCP Radicale bridge WebSocket interface with proper assertions,
error handling, and formatted output.

Prerequisites:
- Run mcp_radicale_bridge.py in a separate terminal before running this test
- Ensure Radicale server is running

Usage:
    python3 test_mcp_client.py
"""

import asyncio
import websockets
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'


class MCPTestClient:
    """Enhanced MCP WebSocket client with proper testing capabilities"""
    
    def __init__(self, uri: str = "ws://localhost:8765"):
        self.uri = uri
        self.websocket = None
        self.test_results = []
        
    async def connect(self):
        """Connect to the MCP WebSocket server"""
        try:
            self.websocket = await websockets.connect(self.uri)
            self.log_success("Connected to MCP server")
            return True
        except Exception as e:
            self.log_error(f"Failed to connect to MCP server: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from the MCP WebSocket server"""
        if self.websocket:
            await self.websocket.close()
            self.log_info("Disconnected from MCP server")
    
    def log_info(self, message: str):
        """Log info message with color"""
        print(f"{Colors.CYAN}ℹ {message}{Colors.END}")
    
    def log_success(self, message: str):
        """Log success message with color"""
        print(f"{Colors.GREEN}✓ {message}{Colors.END}")
    
    def log_error(self, message: str):
        """Log error message with color"""
        print(f"{Colors.RED}✗ {message}{Colors.END}")
    
    def log_warning(self, message: str):
        """Log warning message with color"""
        print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")
    
    def log_test_header(self, test_name: str):
        """Log test header with formatting"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}Testing: {test_name}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}")
    
    async def send_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send message and receive response with error handling"""
        try:
            message_str = json.dumps(message)
            await self.websocket.send(message_str)
            
            response_str = await asyncio.wait_for(self.websocket.recv(), timeout=10.0)
            response = json.loads(response_str)
            
            return response
        except asyncio.TimeoutError:
            self.log_error("Request timed out")
            return None
        except Exception as e:
            self.log_error(f"Error sending message: {e}")
            return None
    
    def assert_response_valid(self, response: Dict[str, Any], test_name: str) -> bool:
        """Assert that response is valid and has required fields"""
        if not response:
            self.log_error(f"{test_name}: No response received")
            return False
        
        if "status" not in response:
            self.log_error(f"{test_name}: Response missing 'status' field")
            return False
        
        self.log_success(f"{test_name}: Response received with status '{response['status']}'")
        return True
    
    def assert_success_response(self, response: Dict[str, Any], test_name: str) -> bool:
        """Assert that response indicates success"""
        if not self.assert_response_valid(response, test_name):
            return False
        
        if response["status"] != "success":
            self.log_error(f"{test_name}: Expected success, got '{response['status']}'")
            if "message" in response:
                self.log_error(f"Error message: {response['message']}")
            return False
        
        self.log_success(f"{test_name}: Operation successful")
        return True
    
    async def test_query_events(self) -> bool:
        """Test querying events from calendar"""
        self.log_test_header("Query Events")
        
        # Test with date range
        start_date = datetime.now().strftime("%Y-%m-%dT00:00:00")
        end_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%dT23:59:59")
        
        query = {
            "type": "query",
            "calendar": "Default Calendar",
            "start_date": start_date,
            "end_date": end_date
        }
        
        self.log_info(f"Querying events from {start_date} to {end_date}")
        response = await self.send_message(query)
        
        if not self.assert_success_response(response, "Query Events"):
            return False
        
        # Validate response structure
        if "events" not in response:
            self.log_error("Query Events: Response missing 'events' field")
            return False
        
        events = response["events"]
        self.log_success(f"Query Events: Found {len(events)} events")
        
        # Display summary of events
        if events:
            print(f"{Colors.WHITE}Event summaries:{Colors.END}")
            for i, event in enumerate(events[:5], 1):  # Show first 5 events
                summary = event.get("summary", "No title")
                start = event.get("start", "No start time")
                print(f"  {i}. {summary} ({start})")
            if len(events) > 5:
                print(f"  ... and {len(events) - 5} more events")
        
        return True
    
    async def test_create_event(self) -> Optional[str]:
        """Test creating a new event"""
        self.log_test_header("Create Event")
        
        # Generate unique event data
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        start_time = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S")
        end_time = (datetime.now() + timedelta(days=1, hours=1)).strftime("%Y-%m-%dT%H:%M:%S")
        
        create = {
            "type": "create",
            "calendar": "Default Calendar",
            "event": {
                "summary": f"MCP Test Event {timestamp}",
                "location": "Test Location",
                "description": "Event created by MCP test suite",
                "start": start_time,
                "end": end_time
            }
        }
        
        self.log_info(f"Creating event: '{create['event']['summary']}'")
        response = await self.send_message(create)
        
        if not self.assert_success_response(response, "Create Event"):
            return None
        
        # Validate event ID is returned
        if "event_id" not in response:
            self.log_error("Create Event: Response missing 'event_id' field")
            return None
        
        event_id = response["event_id"]
        self.log_success(f"Create Event: Event created with ID '{event_id}'")
        return event_id
    
    async def test_update_event(self, event_id: str) -> bool:
        """Test updating an existing event"""
        self.log_test_header("Update Event")
        
        update = {
            "type": "update",
            "calendar": "Default Calendar",
            "event_id": event_id,
            "event": {
                "summary": "Updated MCP Test Event",
                "description": "Event updated by MCP test suite",
                "location": "Updated Location"
            }
        }
        
        self.log_info(f"Updating event ID: {event_id}")
        response = await self.send_message(update)
        
        return self.assert_success_response(response, "Update Event")
    
    async def test_delete_event(self, event_id: str) -> bool:
        """Test deleting an event"""
        self.log_test_header("Delete Event")
        
        delete = {
            "type": "delete",
            "calendar": "Default Calendar",
            "event_id": event_id
        }
        
        self.log_info(f"Deleting event ID: {event_id}")
        response = await self.send_message(delete)
        
        return self.assert_success_response(response, "Delete Event")
    
    async def test_error_handling(self) -> bool:
        """Test error handling with invalid requests"""
        self.log_test_header("Error Handling")
        
        # Test invalid operation type
        invalid_op = {
            "type": "invalid_operation",
            "calendar": "Default Calendar"
        }
        
        self.log_info("Testing invalid operation type")
        response = await self.send_message(invalid_op)
        
        if not response or response.get("status") != "error":
            self.log_warning("Error Handling: Expected error response for invalid operation")
            return False
        
        self.log_success("Error Handling: Invalid operation properly rejected")
        
        # Test missing required fields
        incomplete = {
            "type": "create"
            # Missing calendar and event fields
        }
        
        self.log_info("Testing incomplete request")
        response = await self.send_message(incomplete)
        
        if not response or response.get("status") != "error":
            self.log_warning("Error Handling: Expected error response for incomplete request")
            return False
        
        self.log_success("Error Handling: Incomplete request properly rejected")
        return True
    
    async def run_all_tests(self) -> Dict[str, bool]:
        """Run all test cases and return results"""
        print(f"{Colors.BOLD}{Colors.WHITE}MCP Client Test Suite{Colors.END}")
        print(f"{Colors.WHITE}Testing WebSocket connection to {self.uri}{Colors.END}")
        
        results = {}
        
        # Connect to server
        if not await self.connect():
            return {"connection": False}
        
        try:
            # Test query events
            results["query_events"] = await self.test_query_events()
            
            # Test create event
            event_id = await self.test_create_event()
            results["create_event"] = event_id is not None
            
            # Test update and delete if create succeeded
            if event_id:
                results["update_event"] = await self.test_update_event(event_id)
                results["delete_event"] = await self.test_delete_event(event_id)
            else:
                results["update_event"] = False
                results["delete_event"] = False
            
            # Test error handling
            results["error_handling"] = await self.test_error_handling()
            
        finally:
            await self.disconnect()
        
        return results
    
    def print_test_summary(self, results: Dict[str, bool]):
        """Print a formatted test summary"""
        print(f"\n{Colors.BOLD}{Colors.WHITE}{'=' * 60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.WHITE}Test Summary{Colors.END}")
        print(f"{Colors.BOLD}{Colors.WHITE}{'=' * 60}{Colors.END}")
        
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result)
        
        for test_name, passed in results.items():
            status_icon = "✓" if passed else "✗"
            status_color = Colors.GREEN if passed else Colors.RED
            test_display = test_name.replace("_", " ").title()
            print(f"{status_color}{status_icon} {test_display}{Colors.END}")
        
        print(f"\n{Colors.BOLD}Results: {passed_tests}/{total_tests} tests passed{Colors.END}")
        
        if passed_tests == total_tests:
            print(f"{Colors.GREEN}{Colors.BOLD}🎉 All tests passed!{Colors.END}")
        else:
            print(f"{Colors.RED}{Colors.BOLD}❌ Some tests failed{Colors.END}")


async def main():
    """Main test runner"""
    client = MCPTestClient()
    results = await client.run_all_tests()
    client.print_test_summary(results)
    
    # Return exit code based on test results
    return 0 if all(results.values()) else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
