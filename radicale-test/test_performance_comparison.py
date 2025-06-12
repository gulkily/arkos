"""
Performance Comparison: Direct vs MCP Integration

This script compares the performance characteristics between the original
direct LangChain tool adapter and the new MCP-based integration.

Metrics measured:
- Initialization time
- Tool execution time
- Memory usage
- Tool discovery time
- End-to-end operation time

Usage:
    python test_performance_comparison.py
"""

import asyncio
import time
import tracemalloc
import statistics
from typing import Dict, List, Any
from datetime import datetime
import json

# Import both integration methods
try:
    from langchain_tool_adapter import CalendarToolAdapter
    DIRECT_AVAILABLE = True
except ImportError:
    DIRECT_AVAILABLE = False
    print("⚠️  Direct tool adapter not available for comparison")

from langchain_mcp_integration import CalendarMCPIntegration
from langchain_example_mcp import MCPCalendarAgent

class PerformanceMetrics:
    """Container for performance measurement results."""
    
    def __init__(self, name: str):
        self.name = name
        self.initialization_time = 0.0
        self.tool_discovery_time = 0.0
        self.execution_times = []
        self.memory_usage = 0.0
        self.success_rate = 0.0
        self.total_operations = 0
        self.successful_operations = 0
    
    def add_execution_time(self, time_taken: float, success: bool = True):
        """Add an execution time measurement."""
        self.execution_times.append(time_taken)
        self.total_operations += 1
        if success:
            self.successful_operations += 1
        self.success_rate = self.successful_operations / self.total_operations if self.total_operations > 0 else 0
    
    def get_avg_execution_time(self) -> float:
        """Get average execution time."""
        return statistics.mean(self.execution_times) if self.execution_times else 0.0
    
    def get_min_execution_time(self) -> float:
        """Get minimum execution time."""
        return min(self.execution_times) if self.execution_times else 0.0
    
    def get_max_execution_time(self) -> float:
        """Get maximum execution time."""
        return max(self.execution_times) if self.execution_times else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "name": self.name,
            "initialization_time": self.initialization_time,
            "tool_discovery_time": self.tool_discovery_time,
            "memory_usage_mb": self.memory_usage,
            "execution_times": {
                "average": self.get_avg_execution_time(),
                "minimum": self.get_min_execution_time(),
                "maximum": self.get_max_execution_time(),
                "count": len(self.execution_times)
            },
            "success_rate": self.success_rate,
            "total_operations": self.total_operations,
            "successful_operations": self.successful_operations
        }

class PerformanceTester:
    """Performance testing framework for calendar integrations."""
    
    def __init__(self):
        self.test_operations = [
            "list_calendars",
            "get_events_today",
            "get_events_week"
        ]
        self.iterations = 5  # Number of iterations per test
    
    async def test_direct_integration(self) -> PerformanceMetrics:
        """Test performance of direct LangChain tool adapter."""
        if not DIRECT_AVAILABLE:
            return None
            
        print("🔧 Testing Direct Integration Performance...")
        metrics = PerformanceMetrics("Direct Integration")
        
        # Start memory tracking
        tracemalloc.start()
        
        try:
            # Test initialization
            start_time = time.time()
            
            adapter = CalendarToolAdapter(
                url="http://localhost:5232",
                username="test",
                password="test"
            )
            
            metrics.initialization_time = time.time() - start_time
            
            # Test tool discovery
            start_time = time.time()
            tools = adapter.get_all_tools()
            metrics.tool_discovery_time = time.time() - start_time
            
            print(f"   📋 Discovered {len(tools)} tools in {metrics.tool_discovery_time:.3f}s")
            
            # Test tool execution
            for operation in self.test_operations:
                await self._test_direct_operation(adapter, tools, operation, metrics)
            
            # Measure memory usage
            current, peak = tracemalloc.get_traced_memory()
            metrics.memory_usage = peak / 1024 / 1024  # Convert to MB
            
        except Exception as e:
            print(f"   ❌ Error testing direct integration: {e}")
        finally:
            tracemalloc.stop()
        
        return metrics
    
    async def _test_direct_operation(self, adapter, tools, operation: str, metrics: PerformanceMetrics):
        """Test a specific operation with direct integration."""
        print(f"   🧪 Testing {operation}...")
        
        for i in range(self.iterations):
            try:
                start_time = time.time()
                
                if operation == "list_calendars":
                    result = adapter.list_calendars()
                elif operation == "get_events_today":
                    from datetime import datetime
                    today = datetime.now().strftime("%Y-%m-%d")
                    result = adapter.list_events(start_date=today, end_date=today)
                elif operation == "get_events_week":
                    from datetime import datetime, timedelta
                    today = datetime.now()
                    week_later = today + timedelta(days=7)
                    result = adapter.list_events(
                        start_date=today.strftime("%Y-%m-%d"),
                        end_date=week_later.strftime("%Y-%m-%d")
                    )
                
                execution_time = time.time() - start_time
                success = result is not None
                metrics.add_execution_time(execution_time, success)
                
                if i == 0:  # Log first result
                    print(f"      ✅ {operation} completed in {execution_time:.3f}s")
                
            except Exception as e:
                execution_time = time.time() - start_time
                metrics.add_execution_time(execution_time, False)
                if i == 0:  # Log first error
                    print(f"      ❌ {operation} failed in {execution_time:.3f}s: {e}")
    
    async def test_mcp_integration(self) -> PerformanceMetrics:
        """Test performance of MCP-based integration."""
        print("🚀 Testing MCP Integration Performance...")
        metrics = PerformanceMetrics("MCP Integration")
        
        # Start memory tracking
        tracemalloc.start()
        
        try:
            # Test initialization
            start_time = time.time()
            
            integration = CalendarMCPIntegration()
            await integration.initialize()
            
            metrics.initialization_time = time.time() - start_time
            
            # Test tool discovery
            start_time = time.time()
            tools = integration.tools
            metrics.tool_discovery_time = time.time() - start_time
            
            print(f"   📋 Discovered {len(tools)} tools in {metrics.tool_discovery_time:.3f}s")
            print(f"   🔧 Integration method: {integration._integration_method}")
            
            # Test tool execution
            for operation in self.test_operations:
                await self._test_mcp_operation(integration, tools, operation, metrics)
            
            # Measure memory usage
            current, peak = tracemalloc.get_traced_memory()
            metrics.memory_usage = peak / 1024 / 1024  # Convert to MB
            
            # Cleanup
            await integration.cleanup()
            
        except Exception as e:
            print(f"   ❌ Error testing MCP integration: {e}")
        finally:
            tracemalloc.stop()
        
        return metrics
    
    async def _test_mcp_operation(self, integration, tools, operation: str, metrics: PerformanceMetrics):
        """Test a specific operation with MCP integration."""
        print(f"   🧪 Testing {operation}...")
        
        # Find appropriate tool
        tool = None
        if operation == "list_calendars":
            tool = next((t for t in tools if "list" in t.name.lower() and "calendar" in t.name.lower()), None)
        elif "get_events" in operation:
            tool = next((t for t in tools if "get" in t.name.lower() and "event" in t.name.lower()), None)
        
        if not tool:
            print(f"      ❌ No tool found for {operation}")
            return
        
        for i in range(self.iterations):
            try:
                start_time = time.time()
                
                if operation == "list_calendars":
                    result = tool.run("")
                elif operation == "get_events_today":
                    from datetime import datetime
                    today = datetime.now().strftime("%Y-%m-%d")
                    input_str = f"start_date: {today}, end_date: {today}"
                    result = tool.run(input_str)
                elif operation == "get_events_week":
                    from datetime import datetime, timedelta
                    today = datetime.now()
                    week_later = today + timedelta(days=7)
                    input_str = f"start_date: {today.strftime('%Y-%m-%d')}, end_date: {week_later.strftime('%Y-%m-%d')}"
                    result = tool.run(input_str)
                
                execution_time = time.time() - start_time
                
                # Check if result is valid JSON
                success = False
                try:
                    parsed = json.loads(result)
                    success = "status" in parsed
                except:
                    success = False
                
                metrics.add_execution_time(execution_time, success)
                
                if i == 0:  # Log first result
                    status = "✅" if success else "❌"
                    print(f"      {status} {operation} completed in {execution_time:.3f}s")
                
            except Exception as e:
                execution_time = time.time() - start_time
                metrics.add_execution_time(execution_time, False)
                if i == 0:  # Log first error
                    print(f"      ❌ {operation} failed in {execution_time:.3f}s: {e}")
    
    async def test_agent_performance(self) -> PerformanceMetrics:
        """Test performance of complete agent operations."""
        print("🤖 Testing Agent Performance...")
        metrics = PerformanceMetrics("Agent Operations")
        
        # Start memory tracking
        tracemalloc.start()
        
        try:
            # Test agent initialization
            start_time = time.time()
            
            agent = MCPCalendarAgent()
            await agent.initialize()
            
            metrics.initialization_time = time.time() - start_time
            
            # Test agent operations
            test_queries = [
                "List my available calendars",
                "What tools do you have?",
                "Help me understand calendar operations"
            ]
            
            for query in test_queries:
                print(f"   🧪 Testing query: '{query}'")
                
                for i in range(3):  # Fewer iterations for agent tests
                    try:
                        start_time = time.time()
                        
                        response = await agent.run_operation(query)
                        
                        execution_time = time.time() - start_time
                        success = isinstance(response, str) and len(response) > 0
                        metrics.add_execution_time(execution_time, success)
                        
                        if i == 0:  # Log first result
                            status = "✅" if success else "❌"
                            print(f"      {status} Query completed in {execution_time:.3f}s")
                        
                    except Exception as e:
                        execution_time = time.time() - start_time
                        metrics.add_execution_time(execution_time, False)
                        if i == 0:  # Log first error
                            print(f"      ❌ Query failed in {execution_time:.3f}s: {e}")
            
            # Measure memory usage
            current, peak = tracemalloc.get_traced_memory()
            metrics.memory_usage = peak / 1024 / 1024  # Convert to MB
            
            # Cleanup
            await agent.cleanup()
            
        except Exception as e:
            print(f"   ❌ Error testing agent performance: {e}")
        finally:
            tracemalloc.stop()
        
        return metrics
    
    def print_comparison(self, direct_metrics: PerformanceMetrics, mcp_metrics: PerformanceMetrics, agent_metrics: PerformanceMetrics):
        """Print a detailed comparison of performance metrics."""
        print("\n📊 PERFORMANCE COMPARISON RESULTS")
        print("=" * 50)
        
        if direct_metrics:
            print(f"\n🔧 Direct Integration:")
            print(f"   Initialization: {direct_metrics.initialization_time:.3f}s")
            print(f"   Tool Discovery: {direct_metrics.tool_discovery_time:.3f}s")
            print(f"   Avg Execution:  {direct_metrics.get_avg_execution_time():.3f}s")
            print(f"   Memory Usage:   {direct_metrics.memory_usage:.1f} MB")
            print(f"   Success Rate:   {direct_metrics.success_rate:.1%}")
        
        print(f"\n🚀 MCP Integration:")
        print(f"   Initialization: {mcp_metrics.initialization_time:.3f}s")
        print(f"   Tool Discovery: {mcp_metrics.tool_discovery_time:.3f}s")
        print(f"   Avg Execution:  {mcp_metrics.get_avg_execution_time():.3f}s")
        print(f"   Memory Usage:   {mcp_metrics.memory_usage:.1f} MB")
        print(f"   Success Rate:   {mcp_metrics.success_rate:.1%}")
        
        print(f"\n🤖 Agent Operations:")
        print(f"   Initialization: {agent_metrics.initialization_time:.3f}s")
        print(f"   Avg Execution:  {agent_metrics.get_avg_execution_time():.3f}s")
        print(f"   Memory Usage:   {agent_metrics.memory_usage:.1f} MB")
        print(f"   Success Rate:   {agent_metrics.success_rate:.1%}")
        
        # Performance comparison
        if direct_metrics:
            print(f"\n📈 COMPARISON RATIOS (MCP vs Direct):")
            init_ratio = mcp_metrics.initialization_time / direct_metrics.initialization_time
            exec_ratio = mcp_metrics.get_avg_execution_time() / direct_metrics.get_avg_execution_time()
            memory_ratio = mcp_metrics.memory_usage / direct_metrics.memory_usage
            
            print(f"   Initialization: {init_ratio:.2f}x")
            print(f"   Execution:      {exec_ratio:.2f}x")
            print(f"   Memory:         {memory_ratio:.2f}x")
            
            # Interpretation
            print(f"\n💡 INTERPRETATION:")
            if init_ratio < 1.0:
                print(f"   ✅ MCP initializes {1/init_ratio:.1f}x faster")
            else:
                print(f"   ⚠️  MCP initializes {init_ratio:.1f}x slower")
                
            if exec_ratio < 1.0:
                print(f"   ✅ MCP executes {1/exec_ratio:.1f}x faster")
            else:
                print(f"   ⚠️  MCP executes {exec_ratio:.1f}x slower")
                
            if memory_ratio < 1.0:
                print(f"   ✅ MCP uses {1/memory_ratio:.1f}x less memory")
            else:
                print(f"   ⚠️  MCP uses {memory_ratio:.1f}x more memory")
    
    def save_results(self, direct_metrics: PerformanceMetrics, mcp_metrics: PerformanceMetrics, agent_metrics: PerformanceMetrics):
        """Save results to JSON file."""
        results = {
            "timestamp": datetime.now().isoformat(),
            "test_parameters": {
                "iterations": self.iterations,
                "operations": self.test_operations
            },
            "results": {
                "direct_integration": direct_metrics.to_dict() if direct_metrics else None,
                "mcp_integration": mcp_metrics.to_dict(),
                "agent_operations": agent_metrics.to_dict()
            }
        }
        
        filename = f"performance_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Results saved to: {filename}")

async def main():
    """Main function to run performance comparison."""
    print("🏁 Starting Performance Comparison Test")
    print("=" * 50)
    
    tester = PerformanceTester()
    
    # Test direct integration (if available)
    direct_metrics = None
    if DIRECT_AVAILABLE:
        direct_metrics = await tester.test_direct_integration()
    
    # Test MCP integration
    mcp_metrics = await tester.test_mcp_integration()
    
    # Test agent performance
    agent_metrics = await tester.test_agent_performance()
    
    # Print comparison
    tester.print_comparison(direct_metrics, mcp_metrics, agent_metrics)
    
    # Save results
    tester.save_results(direct_metrics, mcp_metrics, agent_metrics)
    
    print("\n✅ Performance comparison completed!")

if __name__ == "__main__":
    asyncio.run(main())