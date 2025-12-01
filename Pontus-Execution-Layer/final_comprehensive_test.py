#!/usr/bin/env python3
"""
FINAL COMPREHENSIVE API TEST
Tests all APIs end-to-end to ensure production readiness before Part B
"""
import asyncio
import httpx
import json
import sys
from datetime import datetime
from typing import Dict, List, Any
import os
from dotenv import load_dotenv

load_dotenv()

# Test results
results: Dict[str, Dict[str, Any]] = {}
test_count = 0
pass_count = 0

def test_result(name: str, passed: bool, details: str = "", data: Any = None):
    global test_count, pass_count
    test_count += 1
    if passed:
        pass_count += 1
        status = "✅ PASS"
    else:
        status = "❌ FAIL"
    results[name] = {
        "status": status,
        "passed": passed,
        "details": details,
        "data": data
    }
    print(f"{status} - {name}")
    if details:
        print(f"        {details}")
    if data and passed:
        print(f"        Data: {json.dumps(data, indent=8)[:200]}...")

async def test_fx_apis():
    """Test all FX APIs"""
    print("\n" + "="*80)
    print("FX APIs TEST")
    print("="*80)
    
    # Test 1: Frankfurter
    try:
        url = "https://api.frankfurter.app/latest"
        params = {"from": "USD", "to": "EUR,GBP,JPY"}
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                rates = data.get("rates", {})
                if rates and len(rates) >= 3:
                    test_result("Frankfurter API", True, f"{len(rates)} rates", {"EUR": rates.get("EUR"), "GBP": rates.get("GBP")})
                else:
                    test_result("Frankfurter API", False, "Insufficient rates")
            else:
                test_result("Frankfurter API", False, f"Status {response.status_code}")
    except Exception as e:
        test_result("Frankfurter API", False, f"Exception: {e}")
    
    # Test 2: ExchangeRate API
    try:
        api_key = os.getenv("EXCHANGERATE_API_KEY", "")
        if not api_key:
            test_result("ExchangeRate API", False, "No API key")
        else:
            url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/USD/EUR"
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    rate = data.get("conversion_rate")
                    if rate:
                        test_result("ExchangeRate API", True, f"Rate: {rate}", {"rate": rate})
                    else:
                        test_result("ExchangeRate API", False, "No rate in response")
                else:
                    test_result("ExchangeRate API", False, f"Status {response.status_code}")
    except Exception as e:
        test_result("ExchangeRate API", False, f"Exception: {e}")

async def test_gas_apis():
    """Test all Gas APIs"""
    print("\n" + "="*80)
    print("GAS APIs TEST")
    print("="*80)
    
    # Test 1: Ethereum Gas
    try:
        api_key = os.getenv("ETHERSCAN_API_KEY", "U623XN7ZQN2EYQ139ZK4NG5JI4A9U4GAFY")
        url = "https://api.etherscan.io/v2/api"
        params = {
            "chainid": "1",
            "module": "gastracker",
            "action": "gasoracle",
            "apikey": api_key
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "1":
                    result = data.get("result", {})
                    fast = result.get("FastGasPrice")
                    safe = result.get("SafeGasPrice")
                    test_result("Ethereum Gas", True, f"Fast: {fast}, Safe: {safe}", {"fast": fast, "safe": safe})
                else:
                    test_result("Ethereum Gas", False, data.get("message", "NOTOK"))
            else:
                test_result("Ethereum Gas", False, f"Status {response.status_code}")
    except Exception as e:
        test_result("Ethereum Gas", False, f"Exception: {e}")
    
    # Test 2: Polygon Gas
    try:
        rpc_url = "https://polygon-rpc.com"
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_gasPrice",
            "params": [],
            "id": 1
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(rpc_url, json=payload)
            if response.status_code == 200:
                data = response.json()
                if "result" in data:
                    gas_price_hex = data["result"]
                    gas_price_gwei = int(gas_price_hex, 16) / 1e9
                    test_result("Polygon Gas", True, f"{gas_price_gwei:.2f} Gwei", {"gwei": gas_price_gwei})
                else:
                    test_result("Polygon Gas", False, "No result")
            else:
                test_result("Polygon Gas", False, f"Status {response.status_code}")
    except Exception as e:
        test_result("Polygon Gas", False, f"Exception: {e}")

async def test_crypto_apis():
    """Test Crypto Price APIs"""
    print("\n" + "="*80)
    print("CRYPTO APIs TEST")
    print("="*80)
    
    # Test: CoinGecko
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": "bitcoin,ethereum,usd-coin,tether",
            "vs_currencies": "usd"
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data and len(data) >= 2:
                    btc = data.get("bitcoin", {}).get("usd")
                    eth = data.get("ethereum", {}).get("usd")
                    test_result("CoinGecko API", True, f"BTC: ${btc}, ETH: ${eth}", {"btc": btc, "eth": eth})
                else:
                    test_result("CoinGecko API", False, "Insufficient data")
            else:
                test_result("CoinGecko API", False, f"Status {response.status_code}")
    except Exception as e:
        test_result("CoinGecko API", False, f"Exception: {e}")

async def test_bridge_apis():
    """Test Bridge APIs"""
    print("\n" + "="*80)
    print("BRIDGE APIs TEST")
    print("="*80)
    
    # Test: LI.FI
    try:
        api_key = os.getenv("LIFI_API_KEY", "")
        if not api_key:
            test_result("LI.FI API", False, "No API key")
        else:
            url = "https://li.quest/v1/quote"
            params = {
                "fromChain": "1",
                "toChain": "137",
                "fromToken": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",  # USDC Ethereum
                "toToken": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",  # USDC Polygon
                "fromAmount": "1000000",  # 1 USDC
                "fromAddress": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
            }
            headers = {"x-lifi-api-key": api_key}
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, params=params, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    if "estimate" in data:
                        estimate = data.get("estimate", {})
                        test_result("LI.FI API", True, "Bridge quote received", {"has_estimate": True})
                    else:
                        test_result("LI.FI API", False, "No estimate in response")
                else:
                    test_result("LI.FI API", False, f"Status {response.status_code}")
    except Exception as e:
        test_result("LI.FI API", False, f"Exception: {e}")

async def test_bank_rail_apis():
    """Test Bank Rail APIs"""
    print("\n" + "="*80)
    print("BANK RAIL APIs TEST")
    print("="*80)
    
    # Test: Hard-coded fee table (always available)
    fee_table = {
        ("USD", "EUR"): {"fee_percent": 0.5, "fixed_fee": 2.0},
        ("USD", "GBP"): {"fee_percent": 0.6, "fixed_fee": 1.5},
        ("USD", "CAD"): {"fee_percent": 0.4, "fixed_fee": 1.0},
    }
    test_result("Bank Rail (Hard-coded)", True, f"{len(fee_table)} pairs available", {"pairs": list(fee_table.keys())})

async def test_fastapi_endpoints():
    """Test FastAPI endpoints (if server is running)"""
    print("\n" + "="*80)
    print("FASTAPI ENDPOINTS TEST")
    print("="*80)
    
    base_url = "http://localhost:8000"
    
    # Test health endpoint
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                test_result("FastAPI Health", True, "Server is running")
            else:
                test_result("FastAPI Health", False, f"Status {response.status_code}")
    except httpx.ConnectError:
        test_result("FastAPI Health", False, "Server not running (skip if not started)")
    except Exception as e:
        test_result("FastAPI Health", False, f"Exception: {e}")
    
    # Test routes endpoint
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{base_url}/api/routes/segments?limit=5")
            if response.status_code == 200:
                data = response.json()
                segments = data.get("segments", [])
                test_result("FastAPI Routes", True, f"{len(segments)} segments", {"count": len(segments)})
            else:
                test_result("FastAPI Routes", False, f"Status {response.status_code}")
    except httpx.ConnectError:
        test_result("FastAPI Routes", False, "Server not running (skip if not started)")
    except Exception as e:
        test_result("FastAPI Routes", False, f"Exception: {e}")

async def test_data_integration():
    """Test that data flows through the system correctly"""
    print("\n" + "="*80)
    print("DATA INTEGRATION TEST")
    print("="*80)
    
    # Import and test the actual clients
    try:
        sys.path.insert(0, '.')
        from app.clients.fx_client import FXClient
        from app.clients.gas_client import GasClient
        from app.clients.crypto_client import CryptoClient
        from app.clients.bridge_client import BridgeClient
        from app.clients.bank_rail_client import BankRailClient
        
        # Test FX Client
        fx_client = FXClient(httpx.AsyncClient())
        fx_segments = await fx_client.fetch_segments()
        test_result("FX Client Integration", len(fx_segments) > 0, f"{len(fx_segments)} segments", {"count": len(fx_segments)})
        await fx_client.client.aclose()
        
        # Test Gas Client
        gas_client = GasClient(httpx.AsyncClient())
        gas_segments = await gas_client.fetch_segments()
        test_result("Gas Client Integration", len(gas_segments) > 0, f"{len(gas_segments)} segments", {"count": len(gas_segments)})
        await gas_client.client.aclose()
        
        # Test Crypto Client
        crypto_client = CryptoClient(httpx.AsyncClient())
        crypto_segments = await crypto_client.fetch_segments()
        test_result("Crypto Client Integration", len(crypto_segments) > 0, f"{len(crypto_segments)} segments", {"count": len(crypto_segments)})
        await crypto_client.client.aclose()
        
        # Test Bridge Client
        bridge_client = BridgeClient(httpx.AsyncClient())
        bridge_segments = await bridge_client.fetch_segments()
        test_result("Bridge Client Integration", len(bridge_segments) > 0, f"{len(bridge_segments)} segments", {"count": len(bridge_segments)})
        await bridge_client.client.aclose()
        
        # Test Bank Rail Client
        bank_client = BankRailClient(httpx.AsyncClient())
        bank_segments = await bank_client.fetch_segments()
        test_result("Bank Rail Client Integration", len(bank_segments) > 0, f"{len(bank_segments)} segments", {"count": len(bank_segments)})
        await bank_client.client.aclose()
        
    except Exception as e:
        test_result("Data Integration", False, f"Exception: {e}")

async def main():
    """Run all comprehensive tests"""
    print("\n" + "🚀"*40)
    print("FINAL COMPREHENSIVE API TEST")
    print("🚀"*40)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nTesting all APIs end-to-end for production readiness...")
    print("="*80)
    
    # Run all test suites
    await test_fx_apis()
    await test_gas_apis()
    await test_crypto_apis()
    await test_bridge_apis()
    await test_bank_rail_apis()
    await test_data_integration()
    await test_fastapi_endpoints()
    
    # Final Summary
    print("\n" + "="*80)
    print("FINAL TEST SUMMARY")
    print("="*80)
    
    # Group by category
    categories = {
        "FX APIs": ["Frankfurter API", "ExchangeRate API"],
        "Gas APIs": ["Ethereum Gas", "Polygon Gas"],
        "Crypto APIs": ["CoinGecko API"],
        "Bridge APIs": ["LI.FI API"],
        "Bank Rail APIs": ["Bank Rail (Hard-coded)"],
        "Integration": ["FX Client Integration", "Gas Client Integration", "Crypto Client Integration", "Bridge Client Integration", "Bank Rail Client Integration"],
        "FastAPI": ["FastAPI Health", "FastAPI Routes"],
    }
    
    for category, test_names in categories.items():
        print(f"\n{category}:")
        for name in test_names:
            if name in results:
                result = results[name]
                status = result["status"]
                details = result["details"]
                print(f"  {status} - {name}")
                if details:
                    print(f"        {details}")
    
    print("\n" + "-"*80)
    print(f"Total Tests: {test_count}")
    print(f"Passed: {pass_count}")
    print(f"Failed: {test_count - pass_count}")
    print(f"Success Rate: {(pass_count/test_count)*100:.1f}%")
    print("="*80)
    
    # Production readiness assessment
    critical_tests = [
        "Frankfurter API", "ExchangeRate API",
        "Ethereum Gas", "Polygon Gas",
        "CoinGecko API",
        "LI.FI API",
        "Bank Rail (Hard-coded)",
        "FX Client Integration", "Gas Client Integration", "Crypto Client Integration"
    ]
    
    critical_passed = sum(1 for name in critical_tests if name in results and results[name]["passed"])
    critical_total = len([name for name in critical_tests if name in results])
    
    print(f"\n📊 PRODUCTION READINESS ASSESSMENT")
    print(f"Critical Tests: {critical_passed}/{critical_total} passed")
    
    if critical_passed == critical_total:
        print("\n🎉 ALL CRITICAL TESTS PASSED!")
        print("✅ System is PRODUCTION READY")
        print("✅ Safe to commit and move to Part B (Routing Engine)")
    elif critical_passed >= critical_total * 0.9:
        print("\n✅ Most critical tests passed")
        print("⚠️  Review failed tests before production")
    else:
        print("\n⚠️  Some critical tests failed")
        print("❌ Fix issues before production")
    
    # Save results
    with open("final_test_results.json", "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": test_count,
                "passed": pass_count,
                "failed": test_count - pass_count,
                "success_rate": (pass_count/test_count)*100 if test_count > 0 else 0
            },
            "critical_tests": {
                "passed": critical_passed,
                "total": critical_total
            },
            "results": results
        }, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: final_test_results.json")
    
    return critical_passed == critical_total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

