#!/usr/bin/env python3
"""
Deep comprehensive test with updated API keys
"""
import asyncio
import httpx
import json
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Load API keys from .env
ETHERSCAN_KEY = os.getenv("ETHERSCAN_API_KEY", "")
EXCHANGERATE_KEY = os.getenv("EXCHANGERATE_API_KEY", "")
LIFI_KEY = os.getenv("LIFI_API_KEY", "")
ZEROX_KEY = os.getenv("ZEROX_API_KEY", "")
BSCSCAN_KEY = os.getenv("BSCSCAN_API_KEY", "")
ARBISCAN_KEY = os.getenv("ARBISCAN_API_KEY", "")
OPTIMISM_KEY = os.getenv("OPTIMISM_API_KEY", "")
SNOWSCAN_KEY = os.getenv("SNOWSCAN_API_KEY", "")

results = {}

async def test_exchangerate():
    """Test ExchangeRate API with new key"""
    print("\n" + "="*70)
    print("EXCHANGERATE API TEST")
    print("="*70)
    
    try:
        url = f"https://v6.exchangerate-api.com/v6/{EXCHANGERATE_KEY}/pair/USD/EUR"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                rate = data.get("conversion_rate")
                if rate:
                    print(f"✅ SUCCESS - USD/EUR: {rate}")
                    results["exchangerate"] = {"status": "✅ WORKING", "rate": rate}
                else:
                    print(f"❌ FAILED - No rate in response")
                    results["exchangerate"] = {"status": "❌ FAILED", "error": "no_rate"}
            else:
                print(f"❌ FAILED - Status: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                results["exchangerate"] = {"status": "❌ FAILED", "error": response.status_code}
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        results["exchangerate"] = {"status": "❌ FAILED", "error": str(e)}

async def test_all_gas_apis():
    """Test all gas price APIs"""
    print("\n" + "="*70)
    print("GAS PRICE APIs TEST (All Chains)")
    print("="*70)
    
    chains = [
        ("1", "Ethereum", ETHERSCAN_KEY),
        ("137", "Polygon", ETHERSCAN_KEY),
        ("56", "BSC", BSCSCAN_KEY),
        ("42161", "Arbitrum", ARBISCAN_KEY),
        ("10", "Optimism", OPTIMISM_KEY),
        ("43114", "Avalanche", SNOWSCAN_KEY),
    ]
    
    for chain_id, name, key in chains:
        if not key:
            print(f"\n[{name}] - ⚠️  No API key")
            results[f"gas_{name.lower()}"] = {"status": "⚠️ NO KEY"}
            continue
            
        print(f"\n[{name}] (Chain ID: {chain_id})")
        try:
            url = "https://api.etherscan.io/v2/api"
            params = {
                "chainid": chain_id,
                "module": "gastracker",
                "action": "gasoracle",
                "apikey": key
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "1":
                        result = data.get("result", {})
                        fast = result.get("FastGasPrice")
                        safe = result.get("SafeGasPrice")
                        print(f"   ✅ SUCCESS")
                        print(f"   Fast: {fast} Gwei")
                        print(f"   Safe: {safe} Gwei")
                        results[f"gas_{name.lower()}"] = {
                            "status": "✅ WORKING",
                            "fast": fast,
                            "safe": safe
                        }
                    else:
                        print(f"   ❌ FAILED - {data.get('message')}")
                        results[f"gas_{name.lower()}"] = {"status": "❌ FAILED", "error": data.get('message')}
                else:
                    print(f"   ❌ FAILED - Status: {response.status_code}")
                    results[f"gas_{name.lower()}"] = {"status": "❌ FAILED", "error": response.status_code}
        except Exception as e:
            print(f"   ❌ EXCEPTION: {e}")
            results[f"gas_{name.lower()}"] = {"status": "❌ FAILED", "error": str(e)}

async def test_zerox_v2():
    """Test 0x API with v2 header"""
    print("\n" + "="*70)
    print("0x API TEST (with v2 header)")
    print("="*70)
    
    try:
        url = "https://api.0x.org/swap/v1/quote"
        params = {
            "chainId": 1,
            "sellToken": "WETH",
            "buyToken": "USDC",
            "sellAmount": "1000000000000000000",  # 1 WETH
        }
        headers = {
            "0x-api-key": ZEROX_KEY,
            "0x-version": "v2"
        }
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params, headers=headers)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if "price" in data:
                    print(f"✅ SUCCESS")
                    print(f"   Price: {data.get('price')}")
                    print(f"   Buy Amount: {data.get('buyAmount')}")
                    results["zerox"] = {"status": "✅ WORKING", "price": data.get('price')}
                else:
                    print(f"⚠️  PARTIAL - No price in response")
                    results["zerox"] = {"status": "⚠️ PARTIAL"}
            elif response.status_code == 404:
                print(f"❌ FAILED - 404 No Route")
                results["zerox"] = {"status": "❌ FAILED", "error": "404_no_route"}
            else:
                print(f"❌ FAILED - Status: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                results["zerox"] = {"status": "❌ FAILED", "error": response.status_code}
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        results["zerox"] = {"status": "❌ FAILED", "error": str(e)}

async def test_lifi():
    """Test LI.FI API"""
    print("\n" + "="*70)
    print("LI.FI API TEST")
    print("="*70)
    
    try:
        url = "https://li.quest/v1/quote"
        params = {
            "fromChain": "1",
            "toChain": "137",
            "fromToken": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            "toToken": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
            "fromAmount": "1000000",
            "fromAddress": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
        }
        headers = {"x-lifi-api-key": LIFI_KEY}
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params, headers=headers)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if "estimate" in data:
                    print(f"✅ SUCCESS - Bridge quote received")
                    results["lifi"] = {"status": "✅ WORKING"}
                else:
                    print(f"⚠️  PARTIAL - Response received")
                    results["lifi"] = {"status": "⚠️ PARTIAL"}
            else:
                print(f"❌ FAILED - Status: {response.status_code}")
                results["lifi"] = {"status": "❌ FAILED", "error": response.status_code}
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        results["lifi"] = {"status": "❌ FAILED", "error": str(e)}

async def main():
    """Run all tests"""
    print("\n" + "🔍"*35)
    print("DEEP TEST WITH UPDATED API KEYS")
    print("🔍"*35)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    await test_exchangerate()
    await test_all_gas_apis()
    await test_zerox_v2()
    await test_lifi()
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    working = sum(1 for r in results.values() if r.get("status") == "✅ WORKING")
    total = len(results)
    
    for name, result in sorted(results.items()):
        status = result.get("status", "UNKNOWN")
        print(f"{status} - {name}")
    
    print("\n" + "-"*70)
    print(f"Total: {working}/{total} APIs working")
    print(f"Success Rate: {(working/total)*100:.1f}%")
    print("="*70)
    
    # Save results
    with open("deep_test_updated_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Results saved to: deep_test_updated_results.json")

if __name__ == "__main__":
    asyncio.run(main())

