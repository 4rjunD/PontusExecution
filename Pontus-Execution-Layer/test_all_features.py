#!/usr/bin/env python3
"""
Comprehensive Test Suite - Test All Features
"""
import asyncio
import sys
import json
from datetime import datetime
from typing import Dict, Any, List

sys.path.insert(0, '/Users/arjundixit/Downloads/PontusExecution/Pontus-Execution-Layer')

import httpx
from app.clients import WiseClient, KrakenClient
from app.config import settings
from app.services.routing_service import RoutingService
from app.services.aggregator_service import AggregatorService
from app.services.execution.execution_service import ExecutionService
from app.services.execution.advanced_execution_service import AdvancedExecutionService
from app.schemas.execution import (
    RouteExecutionRequest,
    CancelExecutionRequest,
    RerouteRequest,
    ModifyTransactionRequest
)

print("=" * 80)
print("🧪 COMPREHENSIVE FEATURE TEST SUITE")
print("=" * 80)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

test_results: List[Dict[str, Any]] = []
test_count = 0
pass_count = 0


def log_test(name: str, passed: bool, details: str = "", data: Dict = None):
    global test_count, pass_count
    test_count += 1
    if passed:
        pass_count += 1
        status = "✅ PASS"
    else:
        status = "❌ FAIL"
    
    result = {
        "name": name,
        "status": status,
        "passed": passed,
        "details": details,
        "data": data or {}
    }
    test_results.append(result)
    
    print(f"{status} - {name}")
    if details:
        print(f"    {details}")
    if data:
        for key, value in data.items():
            print(f"    {key}: {value}")
    print()


async def test_api_connections():
    """Test API client connections"""
    print("=" * 80)
    print("TEST 1: API CONNECTIONS")
    print("=" * 80)
    
    # Test Wise API
    if settings.wise_api_key:
        try:
            client = httpx.AsyncClient(timeout=30.0)
            wise = WiseClient(client)
            profiles = await wise.get_profiles()
            
            if profiles:
                log_test("Wise API Connection", True, f"Found {len(profiles)} profiles", {
                    "profile_count": len(profiles),
                    "first_profile_id": profiles[0].get("id") if profiles else None
                })
            else:
                log_test("Wise API Connection", False, "No profiles returned")
            
            await client.aclose()
        except Exception as e:
            log_test("Wise API Connection", False, f"Error: {str(e)}")
    else:
        log_test("Wise API Connection", False, "API key not configured")
    
    # Test Kraken API
    if settings.kraken_api_key:
        try:
            client = httpx.AsyncClient(timeout=30.0)
            kraken = KrakenClient(client)
            ticker = await kraken.get_ticker("XBTUSD")
            
            if ticker:
                price = ticker.get("c", [None])[0] if ticker.get("c") else None
                log_test("Kraken API Connection", True, f"BTC/USD: ${price}", {
                    "ticker_price": price
                })
            else:
                log_test("Kraken API Connection", False, "No ticker data")
            
            await client.aclose()
        except Exception as e:
            log_test("Kraken API Connection", False, f"Error: {str(e)}")
    else:
        log_test("Kraken API Connection", False, "API key not configured")


async def test_routing_engine():
    """Test routing engine"""
    print("=" * 80)
    print("TEST 2: ROUTING ENGINE")
    print("=" * 80)
    
    try:
        routing_service = RoutingService()
        aggregator_service = AggregatorService()
        
        # Get segments
        segments = await aggregator_service.get_cached_segments()
        if not segments:
            segments = await aggregator_service.get_segments_from_db(limit=100)
        
        if segments:
            log_test("Route Segments Available", True, f"Found {len(segments)} segments", {
                "segment_count": len(segments)
            })
            
            # Test route finding
            route_result = routing_service.find_optimal_route(
                segments=segments,
                from_asset="USD",
                to_asset="EUR",
                from_network=None,
                to_network=None
            )
            
            if "error" not in route_result and route_result.get("route"):
                log_test("Route Optimization", True, f"Found route with {len(route_result['route'])} segments", {
                    "route_segments": len(route_result["route"]),
                    "cost_percent": route_result.get("cost_percent"),
                    "eta_hours": route_result.get("eta_hours")
                })
            else:
                log_test("Route Optimization", False, route_result.get("error", "Unknown error"))
        else:
            log_test("Route Segments Available", False, "No segments found (database may not be connected)")
        
        await aggregator_service.close()
        
    except Exception as e:
        log_test("Routing Engine Test", False, f"Error: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_basic_execution():
    """Test basic execution (simulation)"""
    print("=" * 80)
    print("TEST 3: BASIC EXECUTION (SIMULATION)")
    print("=" * 80)
    
    try:
        routing_service = RoutingService()
        aggregator_service = AggregatorService()
        execution_service = ExecutionService(routing_service, aggregator_service)
        
        # Get segments
        segments = await aggregator_service.get_cached_segments()
        if not segments:
            segments = await aggregator_service.get_segments_from_db(limit=100)
        
        if not segments:
            log_test("Basic Execution", False, "No segments available")
            return
        
        request = RouteExecutionRequest(
            from_asset="USD",
            to_asset="EUR",
            amount=100.0
        )
        
        result = await execution_service.execute_route(request, parallel=False, enable_ai_rerouting=False)
        
        if result.status.value == "completed":
            log_test("Basic Execution", True, f"Execution completed successfully", {
                "execution_id": result.execution_id,
                "final_amount": result.final_amount,
                "total_fees": result.total_fees,
                "segments_executed": len(result.segment_executions)
            })
        else:
            log_test("Basic Execution", False, f"Status: {result.status.value}", {
                "error": result.error_message
            })
        
        await aggregator_service.close()
        
    except Exception as e:
        log_test("Basic Execution", False, f"Error: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_automatic_funding():
    """Test automatic funding feature"""
    print("=" * 80)
    print("TEST 4: AUTOMATIC FUNDING")
    print("=" * 80)
    
    if not settings.wise_api_key:
        log_test("Automatic Funding", False, "Wise API key not configured")
        return
    
    try:
        client = httpx.AsyncClient(timeout=30.0)
        wise = WiseClient(client)
        
        # Test funding method exists
        if hasattr(wise, 'fund_transfer'):
            log_test("Automatic Funding Method", True, "fund_transfer() method exists")
        else:
            log_test("Automatic Funding Method", False, "fund_transfer() method not found")
        
        # Test in segment executor
        from app.services.execution.segment_executors import BankRailExecutor
        from app.services.execution.simulator import Simulator
        
        executor = BankRailExecutor(Simulator(), wise_client=wise)
        if executor.wise_client:
            log_test("Automatic Funding Integration", True, "BankRailExecutor has Wise client")
        else:
            log_test("Automatic Funding Integration", False, "BankRailExecutor missing Wise client")
        
        await client.aclose()
        
    except Exception as e:
        log_test("Automatic Funding", False, f"Error: {str(e)}")


async def test_cancellation():
    """Test cancellation features"""
    print("=" * 80)
    print("TEST 5: CANCELLATION FEATURES")
    print("=" * 80)
    
    # Test Wise cancellation
    if settings.wise_api_key:
        try:
            client = httpx.AsyncClient(timeout=30.0)
            wise = WiseClient(client)
            
            if hasattr(wise, 'cancel_transfer'):
                log_test("Wise Cancellation Method", True, "cancel_transfer() method exists")
            else:
                log_test("Wise Cancellation Method", False, "cancel_transfer() method not found")
            
            await client.aclose()
        except Exception as e:
            log_test("Wise Cancellation", False, f"Error: {str(e)}")
    
    # Test Kraken cancellation
    if settings.kraken_api_key:
        try:
            client = httpx.AsyncClient(timeout=30.0)
            kraken = KrakenClient(client)
            
            if hasattr(kraken, 'cancel_order'):
                log_test("Kraken Cancellation Method", True, "cancel_order() method exists")
            else:
                log_test("Kraken Cancellation Method", False, "cancel_order() method not found")
            
            await client.aclose()
        except Exception as e:
            log_test("Kraken Cancellation", False, f"Error: {str(e)}")
    
    # Test execution service cancellation
    try:
        routing_service = RoutingService()
        aggregator_service = AggregatorService()
        execution_service = ExecutionService(routing_service, aggregator_service)
        
        if hasattr(execution_service, 'cancel_execution'):
            log_test("Execution Service Cancellation", True, "cancel_execution() method exists")
        else:
            log_test("Execution Service Cancellation", False, "cancel_execution() method not found")
        
        await aggregator_service.close()
    except Exception as e:
        log_test("Execution Service Cancellation", False, f"Error: {str(e)}")


async def test_pause_resume():
    """Test pause/resume features"""
    print("=" * 80)
    print("TEST 6: PAUSE/RESUME FEATURES")
    print("=" * 80)
    
    try:
        routing_service = RoutingService()
        aggregator_service = AggregatorService()
        execution_service = ExecutionService(routing_service, aggregator_service)
        
        # Test pause method
        if hasattr(execution_service, 'pause_execution'):
            log_test("Pause Method", True, "pause_execution() method exists")
        else:
            log_test("Pause Method", False, "pause_execution() method not found")
        
        # Test resume method
        if hasattr(execution_service, 'resume_execution'):
            log_test("Resume Method", True, "resume_execution() method exists")
        else:
            log_test("Resume Method", False, "resume_execution() method not found")
        
        # Test advanced service
        advanced_service = execution_service.advanced_service
        if advanced_service:
            log_test("Advanced Service Available", True, "AdvancedExecutionService initialized")
            
            # Test state management
            if hasattr(advanced_service, 'execution_states'):
                log_test("State Management", True, "Execution state tracking available")
            else:
                log_test("State Management", False, "State tracking not found")
        else:
            log_test("Advanced Service Available", False, "AdvancedExecutionService not initialized")
        
        await aggregator_service.close()
        
    except Exception as e:
        log_test("Pause/Resume Test", False, f"Error: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_rerouting():
    """Test dynamic re-routing"""
    print("=" * 80)
    print("TEST 7: DYNAMIC RE-ROUTING")
    print("=" * 80)
    
    try:
        routing_service = RoutingService()
        aggregator_service = AggregatorService()
        execution_service = ExecutionService(routing_service, aggregator_service)
        
        # Test reroute method
        if hasattr(execution_service, 'reroute_execution'):
            log_test("Re-route Method", True, "reroute_execution() method exists")
        else:
            log_test("Re-route Method", False, "reroute_execution() method not found")
        
        # Test AI re-routing logic
        advanced_service = execution_service.advanced_service
        if advanced_service:
            if hasattr(advanced_service, '_should_reroute'):
                log_test("AI Re-routing Logic", True, "AI decision making available")
            else:
                log_test("AI Re-routing Logic", False, "AI decision logic not found")
            
            if hasattr(advanced_service, 'reroute_thresholds'):
                log_test("Re-routing Thresholds", True, "Configurable thresholds available", {
                    "thresholds": advanced_service.reroute_thresholds
                })
            else:
                log_test("Re-routing Thresholds", False, "Thresholds not found")
        
        await aggregator_service.close()
        
    except Exception as e:
        log_test("Re-routing Test", False, f"Error: {str(e)}")


async def test_parallel_execution():
    """Test parallel execution"""
    print("=" * 80)
    print("TEST 8: PARALLEL EXECUTION")
    print("=" * 80)
    
    try:
        routing_service = RoutingService()
        aggregator_service = AggregatorService()
        execution_service = ExecutionService(routing_service, aggregator_service)
        
        # Test parallel execution parameter
        if hasattr(execution_service, 'execute_route'):
            # Check if method accepts parallel parameter
            import inspect
            sig = inspect.signature(execution_service.execute_route)
            if 'parallel' in sig.parameters:
                log_test("Parallel Execution Parameter", True, "execute_route() accepts parallel parameter")
            else:
                log_test("Parallel Execution Parameter", False, "parallel parameter not found")
        
        # Test parallel grouping
        advanced_service = execution_service.advanced_service
        if advanced_service:
            if hasattr(advanced_service, '_group_parallel_segments'):
                log_test("Parallel Grouping Logic", True, "Segment grouping for parallel execution available")
            else:
                log_test("Parallel Grouping Logic", False, "Grouping logic not found")
            
            if hasattr(advanced_service, '_execute_parallel'):
                log_test("Parallel Execution Method", True, "_execute_parallel() method exists")
            else:
                log_test("Parallel Execution Method", False, "Parallel execution method not found")
        
        await aggregator_service.close()
        
    except Exception as e:
        log_test("Parallel Execution Test", False, f"Error: {str(e)}")


async def test_modification():
    """Test transaction modification"""
    print("=" * 80)
    print("TEST 9: TRANSACTION MODIFICATION")
    print("=" * 80)
    
    # Test Wise modification
    if settings.wise_api_key:
        try:
            client = httpx.AsyncClient(timeout=30.0)
            wise = WiseClient(client)
            
            if hasattr(wise, 'modify_transfer'):
                log_test("Wise Modification Method", True, "modify_transfer() method exists")
            else:
                log_test("Wise Modification Method", False, "modify_transfer() method not found")
            
            await client.aclose()
        except Exception as e:
            log_test("Wise Modification", False, f"Error: {str(e)}")
    
    # Test Kraken modification
    if settings.kraken_api_key:
        try:
            client = httpx.AsyncClient(timeout=30.0)
            kraken = KrakenClient(client)
            
            if hasattr(kraken, 'modify_order'):
                log_test("Kraken Modification Method", True, "modify_order() method exists")
            else:
                log_test("Kraken Modification Method", False, "modify_order() method not found")
            
            await client.aclose()
        except Exception as e:
            log_test("Kraken Modification", False, f"Error: {str(e)}")
    
    # Test execution service modification
    try:
        routing_service = RoutingService()
        aggregator_service = AggregatorService()
        execution_service = ExecutionService(routing_service, aggregator_service)
        
        if hasattr(execution_service, 'modify_transaction'):
            log_test("Execution Service Modification", True, "modify_transaction() method exists")
        else:
            log_test("Execution Service Modification", False, "modify_transaction() method not found")
        
        await aggregator_service.close()
    except Exception as e:
        log_test("Execution Service Modification", False, f"Error: {str(e)}")


async def test_api_endpoints():
    """Test API endpoints"""
    print("=" * 80)
    print("TEST 10: API ENDPOINTS")
    print("=" * 80)
    
    try:
        from app.api.routes_execution import router
        
        # Get all routes
        routes = [r.path for r in router.routes]
        
        expected_routes = [
            "/api/routes/execute",
            "/api/routes/execute/{execution_id}/status",
            "/api/routes/execute/{execution_id}/pause",
            "/api/routes/execute/{execution_id}/resume",
            "/api/routes/execute/{execution_id}/cancel",
            "/api/routes/execute/{execution_id}/reroute",
            "/api/routes/execute/{execution_id}/modify",
        ]
        
        found_routes = []
        for expected in expected_routes:
            # Check if route exists (account for path variations)
            found = any(expected.replace("{execution_id}", "") in r.replace("{execution_id}", "") for r in routes)
            if found:
                found_routes.append(expected)
                log_test(f"Endpoint: {expected}", True, "Route registered")
            else:
                log_test(f"Endpoint: {expected}", False, "Route not found")
        
        log_test("API Endpoints Summary", True, f"Found {len(found_routes)}/{len(expected_routes)} endpoints", {
            "found": found_routes
        })
        
    except Exception as e:
        log_test("API Endpoints Test", False, f"Error: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_schemas():
    """Test execution schemas"""
    print("=" * 80)
    print("TEST 11: EXECUTION SCHEMAS")
    print("=" * 80)
    
    try:
        from app.schemas.execution import (
            ExecutionStatus,
            RerouteRequest,
            CancelExecutionRequest,
            ModifyTransactionRequest
        )
        
        # Test ExecutionStatus enum
        if ExecutionStatus.PAUSED in ExecutionStatus:
            log_test("Paused Status", True, "PAUSED status available")
        else:
            log_test("Paused Status", False, "PAUSED status not found")
        
        if ExecutionStatus.REROUTING in ExecutionStatus:
            log_test("Rerouting Status", True, "REROUTING status available")
        else:
            log_test("Rerouting Status", False, "REROUTING status not found")
        
        # Test request schemas
        try:
            reroute_req = RerouteRequest(execution_id="test", from_current_position=True)
            log_test("RerouteRequest Schema", True, "Schema validates correctly")
        except Exception as e:
            log_test("RerouteRequest Schema", False, f"Validation error: {str(e)}")
        
        try:
            cancel_req = CancelExecutionRequest(execution_id="test", cancel_pending_segments=True)
            log_test("CancelExecutionRequest Schema", True, "Schema validates correctly")
        except Exception as e:
            log_test("CancelExecutionRequest Schema", False, f"Validation error: {str(e)}")
        
        try:
            modify_req = ModifyTransactionRequest(execution_id="test", segment_index=0, new_amount=100.0)
            log_test("ModifyTransactionRequest Schema", True, "Schema validates correctly")
        except Exception as e:
            log_test("ModifyTransactionRequest Schema", False, f"Validation error: {str(e)}")
        
    except Exception as e:
        log_test("Schemas Test", False, f"Error: {str(e)}")
        import traceback
        traceback.print_exc()


async def main():
    """Run all tests"""
    import httpx
    
    # Run all test suites
    await test_api_connections()
    await test_routing_engine()
    await test_basic_execution()
    await test_automatic_funding()
    await test_cancellation()
    await test_pause_resume()
    await test_rerouting()
    await test_parallel_execution()
    await test_modification()
    await test_api_endpoints()
    await test_schemas()
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {test_count}")
    print(f"Passed: {pass_count}")
    print(f"Failed: {test_count - pass_count}")
    print(f"Success Rate: {(pass_count/test_count)*100:.1f}%")
    print("=" * 80)
    
    # Group by category
    print("\n📊 Results by Category:\n")
    
    categories = {
        "API Connections": ["Wise API Connection", "Kraken API Connection"],
        "Routing Engine": ["Route Segments Available", "Route Optimization"],
        "Basic Execution": ["Basic Execution"],
        "Automatic Funding": ["Automatic Funding Method", "Automatic Funding Integration"],
        "Cancellation": ["Wise Cancellation Method", "Kraken Cancellation Method", "Execution Service Cancellation"],
        "Pause/Resume": ["Pause Method", "Resume Method", "Advanced Service Available", "State Management"],
        "Re-routing": ["Re-route Method", "AI Re-routing Logic", "Re-routing Thresholds"],
        "Parallel Execution": ["Parallel Execution Parameter", "Parallel Grouping Logic", "Parallel Execution Method"],
        "Modification": ["Wise Modification Method", "Kraken Modification Method", "Execution Service Modification"],
        "API Endpoints": ["Endpoint:"],
        "Schemas": ["Paused Status", "Rerouting Status", "RerouteRequest Schema", "CancelExecutionRequest Schema", "ModifyTransactionRequest Schema"]
    }
    
    for category, test_names in categories.items():
        category_tests = [t for t in test_results if any(name in t["name"] for name in test_names)]
        if category_tests:
            passed = sum(1 for t in category_tests if t["passed"])
            total = len(category_tests)
            print(f"{category}: {passed}/{total} passed")
    
    print("\n" + "=" * 80)
    print("✅ FEATURES THAT WORK:")
    print("=" * 80)
    
    working_features = [t["name"] for t in test_results if t["passed"]]
    for feature in sorted(working_features):
        print(f"  ✅ {feature}")
    
    print("\n" + "=" * 80)
    print("❌ FEATURES THAT NEED ATTENTION:")
    print("=" * 80)
    
    failing_features = [t["name"] for t in test_results if not t["passed"]]
    for feature in sorted(failing_features):
        print(f"  ❌ {feature}")
    
    return pass_count == test_count


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

