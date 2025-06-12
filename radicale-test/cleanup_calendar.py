#!/usr/bin/env python3
"""
Calendar Cleanup Script

This script removes test events with excessively long text content and other
test data to make the calendar more manageable for testing.

Usage:
    python cleanup_calendar.py

Features:
- Removes events with very long summaries, descriptions, or locations
- Removes duplicate test events
- Removes events created by automated tests
- Provides detailed cleanup summary
- Safe mode with confirmation prompts
"""

import logging
import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Local imports
from radicale_calendar_manager import RadicaleCalendarManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class CalendarCleaner:
    """Utility class for cleaning up calendar test data"""
    
    def __init__(self, radicale_url: str = None, username: str = None, password: str = None):
        """Initialize the calendar cleaner"""
        # Use environment variables as defaults
        radicale_url = radicale_url or os.getenv("RADICALE_URL", "http://localhost:5232")
        username = username or os.getenv("RADICALE_USERNAME", "")
        password = password or os.getenv("RADICALE_PASSWORD", "")
        
        self.calendar_manager = RadicaleCalendarManager(radicale_url, username, password)
        self.events_to_delete = []
        self.cleanup_stats = {
            'long_text': 0,
            'test_events': 0,
            'duplicates': 0,
            'total_deleted': 0
        }
    
    def connect(self):
        """Connect to the Radicale server"""
        try:
            success = self.calendar_manager.connect()
            if success:
                logger.info(f"Connected to Radicale server at {self.calendar_manager.url}")
                calendars = self.calendar_manager.calendars
                calendar_names = [cal.name for cal in calendars] if calendars else []
                logger.info(f"Found {len(calendar_names)} calendars: {calendar_names}")
                return True
            else:
                logger.error("Failed to connect to Radicale server")
                return False
        except Exception as e:
            logger.error(f"Failed to connect to Radicale server: {e}")
            return False
    
    def analyze_events(self, calendar_name: str = None) -> List[Dict[str, Any]]:
        """Analyze events and identify cleanup candidates"""
        try:
            events = self.calendar_manager.get_events(calendar_name)
            logger.info(f"Analyzing {len(events)} events for cleanup...")
            
            candidates = []
            
            for event in events:
                reasons = []
                
                # Check for very long text (over 200 characters)
                summary = event.get('summary', '')
                description = event.get('description', '')
                location = event.get('location', '')
                
                if len(summary) > 200:
                    reasons.append(f"Long summary ({len(summary)} chars)")
                
                if len(description) > 500:
                    reasons.append(f"Long description ({len(description)} chars)")
                
                if len(location) > 200:
                    reasons.append(f"Long location ({len(location)} chars)")
                
                # Check for test event patterns
                test_patterns = [
                    r'Test Event \d{4}-\d{2}-\d{2}',
                    r'Created by.*test',
                    r'LangChain.*[Tt]est',
                    r'Multi-day Test Event',
                    r'Duplicate Test Event',
                    r'Long text Test Event',
                    r'Timezone Test Event',
                    r'All-day Test Event'
                ]
                
                for pattern in test_patterns:
                    if re.search(pattern, summary, re.IGNORECASE) or re.search(pattern, description, re.IGNORECASE):
                        reasons.append("Test event pattern")
                        break
                
                # Check for events with very repetitive content (like 'x' repeated many times)
                if re.search(r'x{50,}|z{50,}|y{50,}', summary + description + location):
                    reasons.append("Repetitive filler text")
                
                if reasons:
                    candidates.append({
                        'event': event,
                        'reasons': reasons
                    })
            
            logger.info(f"Found {len(candidates)} events marked for cleanup")
            return candidates
            
        except Exception as e:
            logger.error(f"Error analyzing events: {e}")
            return []
    
    def preview_cleanup(self, candidates: List[Dict[str, Any]]):
        """Preview what will be cleaned up"""
        print("\n" + "="*80)
        print("CLEANUP PREVIEW")
        print("="*80)
        
        if not candidates:
            print("No events found that need cleanup.")
            return
        
        for i, candidate in enumerate(candidates, 1):
            event = candidate['event']
            reasons = candidate['reasons']
            
            print(f"\n{i}. Event: {event.get('summary', 'No title')[:60]}...")
            print(f"   ID: {event.get('id', 'Unknown')}")
            print(f"   Start: {event.get('start', 'Unknown')}")
            print(f"   Reasons: {', '.join(reasons)}")
            
            # Show truncated content for very long fields
            if len(event.get('summary', '')) > 60:
                print(f"   Summary length: {len(event.get('summary', ''))} chars")
            
            if len(event.get('description', '')) > 100:
                print(f"   Description length: {len(event.get('description', ''))} chars")
                
            if len(event.get('location', '')) > 60:
                print(f"   Location length: {len(event.get('location', ''))} chars")
    
    def perform_cleanup(self, candidates: List[Dict[str, Any]], calendar_name: str = None, dry_run: bool = False):
        """Perform the actual cleanup"""
        if not candidates:
            logger.info("No events to clean up.")
            return
        
        logger.info(f"{'DRY RUN: Would delete' if dry_run else 'Deleting'} {len(candidates)} events...")
        
        deleted_count = 0
        
        for candidate in candidates:
            event = candidate['event']
            event_id = event.get('id')
            
            if not event_id:
                logger.warning(f"Skipping event without ID: {event.get('summary', 'Unknown')[:50]}")
                continue
            
            try:
                if not dry_run:
                    self.calendar_manager.delete_event(calendar_name, event_id)
                
                deleted_count += 1
                
                # Update stats based on reasons
                reasons = candidate['reasons']
                if any('Long' in reason for reason in reasons):
                    self.cleanup_stats['long_text'] += 1
                if any('Test' in reason for reason in reasons):
                    self.cleanup_stats['test_events'] += 1
                if any('Duplicate' in reason for reason in reasons):
                    self.cleanup_stats['duplicates'] += 1
                
                logger.info(f"{'Would delete' if dry_run else 'Deleted'} event: {event.get('summary', 'Unknown')[:50]}...")
                
            except Exception as e:
                logger.error(f"Failed to delete event {event_id}: {e}")
        
        self.cleanup_stats['total_deleted'] = deleted_count
        
        if not dry_run:
            logger.info(f"Successfully deleted {deleted_count} events")
        else:
            logger.info(f"Dry run complete: Would delete {deleted_count} events")
    
    def print_stats(self):
        """Print cleanup statistics"""
        print("\n" + "="*50)
        print("CLEANUP STATISTICS")
        print("="*50)
        print(f"Events with long text:     {self.cleanup_stats['long_text']}")
        print(f"Test events:               {self.cleanup_stats['test_events']}")
        print(f"Duplicate events:          {self.cleanup_stats['duplicates']}")
        print(f"Total events processed:    {self.cleanup_stats['total_deleted']}")
        print("="*50)

def main():
    """Main cleanup script"""
    print("🧹 Calendar Cleanup Tool")
    print("=" * 50)
    
    # Parse command line arguments
    dry_run = "--dry-run" in sys.argv
    force = "--force" in sys.argv
    calendar_name = None
    
    # Look for calendar name argument
    for arg in sys.argv[1:]:
        if not arg.startswith('--'):
            calendar_name = arg
            break
    
    if dry_run:
        print("🔍 DRY RUN MODE: No events will actually be deleted")
    
    # Initialize cleaner
    cleaner = CalendarCleaner()
    
    if not cleaner.connect():
        print("❌ Failed to connect to Radicale server")
        print("   Make sure Radicale is running on localhost:5232")
        return 1
    
    # Analyze events
    candidates = cleaner.analyze_events(calendar_name)
    
    if not candidates:
        print("✅ No cleanup needed - calendar looks good!")
        return 0
    
    # Preview cleanup
    cleaner.preview_cleanup(candidates)
    
    # Confirm cleanup (unless forced)
    if not force and not dry_run:
        print(f"\n⚠️  This will permanently delete {len(candidates)} events.")
        confirm = input("Do you want to proceed? (y/N): ").strip().lower()
        
        if confirm not in ['y', 'yes']:
            print("Cleanup cancelled.")
            return 0
    
    # Perform cleanup
    cleaner.perform_cleanup(candidates, calendar_name, dry_run)
    
    # Show statistics
    cleaner.print_stats()
    
    if not dry_run:
        print("\n✅ Cleanup completed!")
        print("💡 Tip: You can now run queries like:")
        print("   - 'List my events for today'")
        print("   - 'What meetings do I have this week?'")
    else:
        print("\n💡 To actually perform the cleanup, run without --dry-run")
    
    return 0

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print(__doc__)
        print("\nUsage:")
        print("  python cleanup_calendar.py [options] [calendar_name]")
        print("\nOptions:")
        print("  --dry-run    Preview cleanup without deleting")
        print("  --force      Skip confirmation prompt")
        print("  --help       Show this help message")
        print("\nExamples:")
        print("  python cleanup_calendar.py --dry-run")
        print("  python cleanup_calendar.py \"Default Calendar\"")
        print("  python cleanup_calendar.py --force")
        sys.exit(0)
    
    sys.exit(main())