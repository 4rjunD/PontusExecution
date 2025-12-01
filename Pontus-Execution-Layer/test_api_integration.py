#!/usr/bin/env python3
"""
Test Wise and Kraken API Integration
Tests both simulation and real API execution modes
"""
import asyncio
import sys
from datetime import datetime
import httpx

# Add project root to path
sys.path.insert(0, '/Users/arjundixit/Downloads/PontusExecution/Pontus-Execution-Layer')

from app.clients import WiseClient, KrakenClient
from app.config import settings

# Try to import execution service (may fail if OR-Tools has issues)
try:
    from app.services.execution.execution_service import ExecutionService
    from app.services.routing_service import RoutingService
    from app.services.aggregator_service import AggregatorService
    from app.schemas.execution import RouteExecutionRequest
    EXECUTION_SERVICE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Execution service import failed (OR-Tools issue): {e}")
    print("   Will skip execution service tests, focusing on API client tests")
    EXECUTION_SERVICE_AVAILABLE = False

print("=" * 80)
print("🧪 API INTEGRATION TEST - Wise & Kraken")
print("=" * 80)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

test_results = []
test_count = 0
pass_count = 0


def log_test(name: str, passed: bool, message: str = ""):
    global test_count, pass_count
    test_count += 1
    if passed:
        pass_count += 1
        status = "✅ PASS"
    else:
        status = "❌ FAIL"
    
    result = f"{status} - {name}"
    if message:
        result += f": {message}"
    print(result)
    test_results.append((name, passed, message))


async def test_wise_client_connection():
    """Test Wise API client connection"""
    print("\n--- Wise API Client Tests ---")
    
    if not settings.wise_api_key:
        log_test("Wise API Key Configured", False, "WISE_API_KEY not set in environment")
        return
    
    log_test("Wise API Key Configured", True, f"Key: {settings.wise_api_key[:20]}...")
    
    try:
        client = httpx.AsyncClient(timeout=30.0)
        wise = WiseClient(client)
        
        # Test profile fetching
        print("  Testing profile fetch...")
        profiles = await wise.get_profiles()
        
        if profiles:
            log_test("Wise Profile Fetch", True, f"Found {len(profiles)} profile(s)")
            if profiles:
                profile = profiles[0]
                print(f"    Profile ID: {profile.get('id')}")
                print(f"    Profile Type: {profile.get('type')}")
        else:
            log_test("Wise Profile Fetch", False, "No profiles returned (check API key)")
        
        # Test account fetching (if profile exists)
        if profiles:
            print("  Testing account fetch...")
            accounts = await wise.get_accounts(profiles[0]["id"])
            log_test("Wise Account Fetch", True, f"Found {len(accounts)} account(s)")
        
        await client.aclose()
        
    except Exception as e:
        log_test("Wise API Connection", False, f"Error: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_kraken_client_connection():
    """Test Kraken API client connection"""
    print("\n--- Kraken API Client Tests ---")
    
    if not settings.kraken_api_key or not settings.kraken_private_key:
        log_test("Kraken API Keys Configured", False, "KRAKEN_API_KEY or KRAKEN_PRIVATE_KEY not set")
        return
    
    log_test("Kraken API Keys Configured", True, f"Key: {settings.kraken_api_key[:20]}...")
    
    try:
        client = httpx.AsyncClient(timeout=30.0)
        kraken = KrakenClient(client)
        
        # Test balance fetching
        print("  Testing balance fetch...")
        balance = await kraken.get_account_balance()
        
        if balance:
            log_test("Kraken Balance Fetch", True, f"Found {len(balance)} asset(s)")
            # Show first few balances
            for asset, amount in list(balance.items())[:5]:
                print(f"    {asset}: {amount}")
        else:
            log_test("Kraken Balance Fetch", False, "No balance returned (check API keys)")
        
        # Test ticker fetching (public endpoint, no auth needed)
        print("  Testing ticker fetch...")
        ticker = await kraken.get_ticker("XBTUSD")
        if ticker:
            price = ticker.get("c", [None])[0] if ticker.get("c") else None
            log_test("Kraken Ticker Fetch", True, f"BTC/USD: ${price}")
        else:
            log_test("Kraken Ticker Fetch", False, "No ticker data returned")
        
        await client.aclose()
        
    except Exception as e:
        log_test("Kraken API Connection", False, f"Error: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_execution_service_simulation():
    """Test execution service in simulation mode"""
    print("\n--- Execution Service (Simulation Mode) ---")
    
    if not EXECUTION_SERVICE_AVAILABLE:
        log_test("Execution Service Test", False, "Execution service not available (OR-Tools import issue)")
        return
    
    try:
        # Force simulation mode
        original_mode = settings.execution_mode
        settings.execution_mode = "simulation"
        
        routing_service = RoutingService()
        aggregator_service = AggregatorService()
        execution_service = ExecutionService(routing_service, aggregator_service)
        
        # Get some segments
        segments = await aggregator_service.get_cached_segments()
        if not segments:
            segments = await aggregator_service.get_segments_from_db(limit=100)
        
        if not segments:
            log_test("Execution Service Init", False, "No segments available")
            return
        
        log_test("Execution Service Init", True, f"Loaded {len(segments)} segments")
        
        # Test execution request
        request = RouteExecutionRequest(
            from_asset="USD",
            to_asset="EUR",
            amount=100.0
        )
        
        print("  Testing route execution (simulation)...")
        result = await execution_service.execute_route(request)
        
        if result.status.value == "completed":
            log_test("Route Execution (Simulation)", True, 
                    f"Final amount: {result.final_amount}, Segments: {len(result.segment_executions)}")
        else:
            log_test("Route Execution (Simulation)", False, f"Status: {result.status.value}")
        
        # Restore original mode
        settings.execution_mode = original_mode
        
        await aggregator_service.close()
        
    except Exception as e:
        log_test("Execution Service Test", False, f"Error: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_execution_mode_config():
    """Test execution mode configuration"""
    print("\n--- Execution Mode Configuration ---")
    
    current_mode = settings.execution_mode
    log_test("Execution Mode", True, f"Current mode: {current_mode}")
    
    if current_mode == "real":
        print("  ⚠️  WARNING: Real execution mode is enabled!")
        print("     This will execute actual transfers. Use with caution.")
    else:
        print("  ✅ Simulation mode is enabled (safe for testing)")


async def main():
    """Run all API integration tests"""
    print("\n" + "=" * 80)
    print("API INTEGRATION TEST SUITE")
    print("=" * 80)
    
    # Test configuration
    await test_execution_mode_config()
    
    # Test API clients
    await test_wise_client_connection()
    await test_kraken_client_connection()
    
    # Test execution service
    await test_execution_service_simulation()
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {test_count}")
    print(f"Passed: {pass_count}")
    print(f"Failed: {test_count - pass_count}")
    print(f"Success Rate: {(pass_count/test_count)*100:.1f}%")
    print("=" * 80)
    
    # Recommendations
    print("\n📋 Next Steps:")
    if pass_count == test_count:
        print("  ✅ All tests passed! Ready for production testing.")
        print("  → Test with small amounts in real mode")
        print("  → Build frontend/landing page")
        print("  → Create demo flow")
    else:
        print("  ⚠️  Some tests failed. Review errors above.")
        print("  → Check API credentials in .env file")
        print("  → Verify API keys have correct permissions")
        print("  → Test API connectivity manually")
    
    return pass_count == test_count


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

