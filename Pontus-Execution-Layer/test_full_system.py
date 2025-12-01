#!/usr/bin/env python3
"""
Full System Test - Test everything end-to-end
"""
import asyncio
import sys
from datetime import datetime

sys.path.insert(0, '/Users/arjundixit/Downloads/PontusExecution/Pontus-Execution-Layer')

from app.services.routing_service import RoutingService
from app.services.aggregator_service import AggregatorService
from app.services.execution.execution_service import ExecutionService
from app.schemas.execution import RouteExecutionRequest

print("=" * 80)
print("🧪 FULL SYSTEM TEST")
print("=" * 80)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

test_count = 0
pass_count = 0


def log_test(name: str, passed: bool, details: str = ""):
    global test_count, pass_count
    test_count += 1
    if passed:
        pass_count += 1
        status = "✅ PASS"
    else:
        status = "❌ FAIL"
    
    print(f"{status} - {name}")
    if details:
        print(f"    {details}")
    print()


async def test_full_flow():
    """Test complete flow from route calculation to execution"""
    
    print("=" * 80)
    print("TEST: Complete System Flow")
    print("=" * 80)
    
    try:
        # Initialize services
        routing_service = RoutingService()
        aggregator_service = AggregatorService()
        execution_service = ExecutionService(routing_service, aggregator_service)
        
        # Step 1: Fetch segments
        print("\n1. Fetching route segments...")
        segments = await aggregator_service.get_cached_segments()
        if not segments:
            # Try to fetch fresh data
            segments = await aggregator_service.fetch_all_segments()
            if segments:
                await aggregator_service.cache_segments(segments)
                await aggregator_service.persist_segments(segments)
        
        if segments:
            log_test("Route Segments Available", True, f"Found {len(segments)} segments")
        else:
            log_test("Route Segments Available", False, "No segments found - database may not be connected")
            print("\n⚠️  To fix: Run setup_database.py or ensure databases are running")
            return
        
        # Step 2: Calculate route
        print("\n2. Calculating optimal route...")
        route_result = routing_service.find_optimal_route(
            segments=segments,
            from_asset="USD",
            to_asset="EUR",
            from_network=None,
            to_network=None
        )
        
        if "error" not in route_result and route_result.get("route"):
            log_test("Route Calculation", True, f"Route found with {len(route_result['route'])} segments", {
                "cost_percent": route_result.get("cost_percent"),
                "eta_hours": route_result.get("eta_hours"),
                "reliability": route_result.get("reliability")
            })
        else:
            log_test("Route Calculation", False, route_result.get("error", "Unknown error"))
            return
        
        # Step 3: Execute route (simulation)
        print("\n3. Executing route (simulation mode)...")
        request = RouteExecutionRequest(
            from_asset="USD",
            to_asset="EUR",
            amount=100.0
        )
        
        result = await execution_service.execute_route(request, parallel=False, enable_ai_rerouting=False)
        
        if result.status.value == "completed":
            log_test("Route Execution", True, f"Execution completed", {
                "execution_id": result.execution_id,
                "final_amount": result.final_amount,
                "total_fees": result.total_fees,
                "segments_executed": len(result.segment_executions)
            })
        else:
            log_test("Route Execution", False, f"Status: {result.status.value}")
        
        # Step 4: Test advanced features
        print("\n4. Testing advanced features...")
        
        # Test pause
        if hasattr(execution_service, 'pause_execution'):
            pause_result = await execution_service.pause_execution(result.execution_id)
            log_test("Pause Feature", pause_result, "Pause method works" if pause_result else "Pause failed")
        
        # Test resume
        if hasattr(execution_service, 'resume_execution'):
            resume_result = await execution_service.resume_execution(result.execution_id)
            log_test("Resume Feature", resume_result, "Resume method works" if resume_result else "Resume failed")
        
        # Test cancellation
        if hasattr(execution_service, 'cancel_execution'):
            cancel_result = await execution_service.cancel_execution(result.execution_id, cancel_pending=False)
            log_test("Cancellation Feature", "status" in cancel_result, "Cancellation method works")
        
        await aggregator_service.close()
        
        print("\n" + "=" * 80)
        print("✅ FULL SYSTEM TEST COMPLETE")
        print("=" * 80)
        
    except Exception as e:
        log_test("Full System Test", False, f"Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_full_flow())

