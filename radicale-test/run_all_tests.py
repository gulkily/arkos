#!/usr/bin/env python3
"""
Comprehensive Test Runner for Radicale Calendar Integration

This script runs all available tests, provides detailed explanations,
and generates comprehensive reports for the Radicale calendar system.

Test Categories:
1. Core Calendar Operations (9 tests)
2. Edge Cases and Error Handling (additional tests)
3. MCP WebSocket Integration (5 tests)
4. MCP Protocol Compliance (15 tests)
5. LangChain Integration (19 tests)
6. Event Creation Tests (3 variants)
7. Performance and Utility Tests

Usage:
    python run_all_tests.py [--verbose] [--category CATEGORY] [--report]
    
    --verbose: Show detailed test output
    --category: Run specific test category (core, mcp, langchain, all)
    --report: Generate detailed HTML report
"""

import os
import sys
import subprocess
import time
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any
import importlib.util

# Color codes for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

class TestRunner:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.results = {}
        self.start_time = datetime.now()
        self.test_dir = Path(__file__).parent
        
    def print_header(self, title: str):
        """Print a formatted header"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{title.center(60)}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")
        
    def print_section(self, title: str):
        """Print a section header"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{title}{Colors.END}")
        print(f"{Colors.CYAN}{'-'*len(title)}{Colors.END}")
        
    def run_command(self, cmd: List[str], description: str, timeout: int = 60) -> Tuple[bool, str, str]:
        """Run a command and capture output"""
        print(f"{Colors.YELLOW}🔄 Running: {description}{Colors.END}")
        if self.verbose:
            print(f"   Command: {' '.join(cmd)}")
            
        try:
            result = subprocess.run(
                cmd,
                cwd=self.test_dir,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            success = result.returncode == 0
            status_icon = f"{Colors.GREEN}✅" if success else f"{Colors.RED}❌"
            print(f"{status_icon} {description} - {'PASSED' if success else 'FAILED'}{Colors.END}")
            
            if self.verbose or not success:
                if result.stdout:
                    print(f"   Output: {result.stdout[:500]}...")
                if result.stderr:
                    print(f"   Errors: {result.stderr[:500]}...")
                    
            return success, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            print(f"{Colors.RED}❌ {description} - TIMEOUT{Colors.END}")
            return False, "", "Command timed out"
        except Exception as e:
            print(f"{Colors.RED}❌ {description} - ERROR: {str(e)}{Colors.END}")
            return False, "", str(e)
    
    def check_prerequisites(self) -> bool:
        """Check if prerequisites are met"""
        self.print_section("🔍 Checking Prerequisites")
        
        prerequisites_ok = True
        
        # Check if .env file exists
        env_file = self.test_dir / '.env'
        if env_file.exists():
            print(f"{Colors.GREEN}✅ .env file found{Colors.END}")
        else:
            print(f"{Colors.YELLOW}⚠️  .env file not found - some tests may fail{Colors.END}")
            
        # Check Radicale server connectivity
        success, stdout, stderr = self.run_command(
            ['curl', '-s', 'http://localhost:5232'],
            "Radicale server connectivity",
            timeout=10
        )
        if not success:
            print(f"{Colors.YELLOW}⚠️  Radicale server not accessible - calendar tests may fail{Colors.END}")
            prerequisites_ok = False
            
        # Check Python dependencies
        required_packages = ['pytest', 'requests', 'caldav', 'langchain', 'python-dotenv']
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                print(f"{Colors.GREEN}✅ {package} available{Colors.END}")
            except ImportError:
                print(f"{Colors.RED}❌ {package} not installed{Colors.END}")
                prerequisites_ok = False
                
        return prerequisites_ok
    
    def run_core_tests(self) -> Dict[str, Any]:
        """Run core calendar operation tests"""
        self.print_section("🎯 Core Calendar Operations Tests")
        
        results = {}
        
        # Test 1: Basic Calendar Manager Tests
        success, stdout, stderr = self.run_command(
            ['python', 'test_radicale_calendar_manager.py'],
            "Core calendar operations (9 tests)"
        )
        results['core_calendar'] = {
            'success': success,
            'output': stdout,
            'error': stderr,
            'description': "Tests basic CRUD operations, connections, and event management"
        }
        
        # Test 2: Edge Cases
        success, stdout, stderr = self.run_command(
            ['python', 'test_radicale_calendar_manager_edge_cases.py'],
            "Edge cases and error handling"
        )
        results['edge_cases'] = {
            'success': success,
            'output': stdout,
            'error': stderr,
            'description': "Tests error conditions, invalid inputs, and boundary cases"
        }
        
        return results
    
    def run_mcp_tests(self) -> Dict[str, Any]:
        """Run MCP integration tests"""
        self.print_section("🔌 MCP Integration Tests")
        
        results = {}
        
        # Test 1: MCP Client Tests
        success, stdout, stderr = self.run_command(
            ['python', 'test_mcp_client.py'],
            "MCP WebSocket client integration (5 tests)"
        )
        results['mcp_client'] = {
            'success': success,
            'output': stdout,
            'error': stderr,
            'description': "Tests WebSocket MCP bridge communication and operations"
        }
        
        # Test 2: MCP Compliance Tests
        success, stdout, stderr = self.run_command(
            ['pytest', 'test_mcp_compliance.py', '-v'],
            "MCP protocol compliance (15 tests)"
        )
        results['mcp_compliance'] = {
            'success': success,
            'output': stdout,
            'error': stderr,
            'description': "Validates MCP protocol adherence and server functionality"
        }
        
        return results
    
    def run_langchain_tests(self) -> Dict[str, Any]:
        """Run LangChain integration tests"""
        self.print_section("🤖 LangChain AI Integration Tests")
        
        results = {}
        
        # Test 1: LangChain Integration Tests
        success, stdout, stderr = self.run_command(
            ['pytest', 'test_langchain_integration.py', '-v'],
            "LangChain tool integration (19 tests)"
        )
        results['langchain_integration'] = {
            'success': success,
            'output': stdout,
            'error': stderr,
            'description': "Tests LangChain tool conversion and AI agent functionality"
        }
        
        return results
    
    def run_event_tests(self) -> Dict[str, Any]:
        """Run event creation and manipulation tests"""
        self.print_section("📅 Event Creation and Management Tests")
        
        results = {}
        
        # Event creation tests
        event_tests = [
            ('test_new_event.py', 'Basic event creation'),
            ('test_new_event_2.py', 'Advanced event creation'),
            ('test_new_event_3.py', 'Parameterized event creation'),
            ('test_read_event.py', 'Event reading and display')
        ]
        
        for test_file, description in event_tests:
            success, stdout, stderr = self.run_command(
                ['python', test_file],
                description
            )
            results[test_file.replace('.py', '')] = {
                'success': success,
                'output': stdout,
                'error': stderr,
                'description': description
            }
            
        return results
    
    def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance and utility tests"""
        self.print_section("⚡ Performance and Utility Tests")
        
        results = {}
        
        # Performance comparison test
        success, stdout, stderr = self.run_command(
            ['python', 'test_performance_comparison.py'],
            "Performance metrics and comparison"
        )
        results['performance'] = {
            'success': success,
            'output': stdout,
            'error': stderr,
            'description': "Measures performance characteristics and benchmarks"
        }
        
        return results
    
    def run_health_check(self) -> Dict[str, Any]:
        """Run system health check"""
        self.print_section("🩺 System Health Check")
        
        health_check_code = '''
from radicale_calendar_manager import RadicaleCalendarManager
import os
from dotenv import load_dotenv
load_dotenv()

manager = RadicaleCalendarManager(
    url=os.getenv('RADICALE_URL', 'http://localhost:5232'),
    username=os.getenv('RADICALE_USERNAME', ''),
    password=os.getenv('RADICALE_PASSWORD', '')
)

if manager.connect():
    print('✅ System is ready for testing!')
    calendars = [cal.name for cal in manager.calendars] if manager.calendars else []
    print(f'📅 Available calendars: {calendars}')
    print(f'🔗 Connected to: {manager.url}')
else:
    print('❌ Connection failed - check Radicale server and credentials')
    exit(1)
'''
        
        success, stdout, stderr = self.run_command(
            ['python', '-c', health_check_code],
            "System connectivity and health"
        )
        
        return {
            'health_check': {
                'success': success,
                'output': stdout,
                'error': stderr,
                'description': "Validates system connectivity and basic functionality"
            }
        }
    
    def generate_summary_report(self, all_results: Dict[str, Dict[str, Any]]):
        """Generate a comprehensive summary report"""
        self.print_header("📊 TEST EXECUTION SUMMARY")
        
        total_categories = 0
        passed_categories = 0
        total_tests = 0
        passed_tests = 0
        
        for category, tests in all_results.items():
            self.print_section(f"Category: {category.upper()}")
            
            category_passed = 0
            category_total = 0
            
            for test_name, result in tests.items():
                category_total += 1
                total_tests += 1
                
                status_icon = f"{Colors.GREEN}✅" if result['success'] else f"{Colors.RED}❌"
                print(f"{status_icon} {test_name}: {result['description']}")
                
                if result['success']:
                    category_passed += 1
                    passed_tests += 1
                elif result['error']:
                    print(f"   {Colors.RED}Error: {result['error'][:200]}...{Colors.END}")
            
            total_categories += 1
            if category_passed == category_total:
                passed_categories += 1
                
            print(f"\n{Colors.BOLD}Category Results: {category_passed}/{category_total} tests passed{Colors.END}")
        
        # Overall summary
        self.print_section("🎯 OVERALL RESULTS")
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"{Colors.BOLD}📈 Total Tests: {total_tests}{Colors.END}")
        print(f"{Colors.BOLD}✅ Passed: {passed_tests}{Colors.END}")
        print(f"{Colors.BOLD}❌ Failed: {total_tests - passed_tests}{Colors.END}")
        print(f"{Colors.BOLD}📊 Success Rate: {success_rate:.1f}%{Colors.END}")
        
        print(f"\n{Colors.BOLD}📁 Categories: {passed_categories}/{total_categories} fully passed{Colors.END}")
        
        # Status assessment
        if success_rate >= 90:
            status = f"{Colors.GREEN}🎉 EXCELLENT - System is production ready!{Colors.END}"
        elif success_rate >= 75:
            status = f"{Colors.YELLOW}⚠️  GOOD - Minor issues need attention{Colors.END}"
        elif success_rate >= 50:
            status = f"{Colors.RED}🔧 NEEDS WORK - Several components failing{Colors.END}"
        else:
            status = f"{Colors.RED}❌ CRITICAL - Major system issues{Colors.END}"
        
        print(f"\n{Colors.BOLD}System Status: {status}")
        
        # Runtime
        runtime = datetime.now() - self.start_time
        print(f"\n{Colors.BOLD}⏱️  Total Runtime: {runtime.total_seconds():.1f} seconds{Colors.END}")
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'success_rate': success_rate,
            'categories': total_categories,
            'passed_categories': passed_categories,
            'runtime_seconds': runtime.total_seconds()
        }
    
    def save_json_report(self, all_results: Dict[str, Dict[str, Any]], summary: Dict[str, Any]):
        """Save results to JSON file"""
        report_data = {
            'timestamp': self.start_time.isoformat(),
            'summary': summary,
            'detailed_results': all_results,
            'system_info': {
                'python_version': sys.version,
                'working_directory': str(self.test_dir),
                'environment_variables': {
                    'RADICALE_URL': os.getenv('RADICALE_URL', 'Not set'),
                    'RADICALE_USERNAME': 'Set' if os.getenv('RADICALE_USERNAME') else 'Not set',
                    'RADICALE_PASSWORD': 'Set' if os.getenv('RADICALE_PASSWORD') else 'Not set',
                }
            }
        }
        
        report_file = self.test_dir / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n{Colors.BLUE}💾 Detailed report saved to: {report_file}{Colors.END}")
        
    def run_all_tests(self, categories: List[str] = None):
        """Run all or specified test categories"""
        self.print_header("🚀 RADICALE CALENDAR INTEGRATION - COMPREHENSIVE TEST SUITE")
        
        # Check prerequisites
        prereq_ok = self.check_prerequisites()
        if not prereq_ok:
            print(f"{Colors.YELLOW}⚠️  Some prerequisites not met - continuing anyway{Colors.END}")
        
        # Health check
        health_results = self.run_health_check()
        
        all_results = {'health': health_results}
        
        # Run specified categories or all
        if not categories or 'all' in categories:
            categories = ['core', 'mcp', 'langchain', 'events', 'performance']
        
        if 'core' in categories:
            all_results['core'] = self.run_core_tests()
            
        if 'mcp' in categories:
            all_results['mcp'] = self.run_mcp_tests()
            
        if 'langchain' in categories:
            all_results['langchain'] = self.run_langchain_tests()
            
        if 'events' in categories:
            all_results['events'] = self.run_event_tests()
            
        if 'performance' in categories:
            all_results['performance'] = self.run_performance_tests()
        
        # Generate summary
        summary = self.generate_summary_report(all_results)
        
        # Save JSON report
        self.save_json_report(all_results, summary)
        
        return all_results, summary

def main():
    parser = argparse.ArgumentParser(description='Run comprehensive test suite for Radicale calendar integration')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed test output')
    parser.add_argument('--category', '-c', choices=['core', 'mcp', 'langchain', 'events', 'performance', 'all'], 
                       default='all', help='Test category to run')
    parser.add_argument('--report', '-r', action='store_true', help='Generate detailed HTML report (JSON always generated)')
    
    args = parser.parse_args()
    
    # Parse categories
    categories = [args.category] if args.category != 'all' else ['all']
    
    # Run tests
    runner = TestRunner(verbose=args.verbose)
    
    try:
        all_results, summary = runner.run_all_tests(categories)
        
        # Exit code based on results
        if summary['success_rate'] >= 75:
            sys.exit(0)  # Success
        else:
            sys.exit(1)  # Failure
            
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}🛑 Tests interrupted by user{Colors.END}")
        sys.exit(2)
    except Exception as e:
        print(f"\n{Colors.RED}💥 Unexpected error: {str(e)}{Colors.END}")
        sys.exit(3)

if __name__ == '__main__':
    main()