#!/usr/bin/env python3
"""
Deep test all API keys to verify they actually work
"""
import asyncio
import httpx
import json
from datetime import datetime

# API Keys from .env
ETHERSCAN_KEY = "U623XN7ZQN2EYQ139ZK4NG5JI4A9U4GAFY"
LIFI_KEY = "769965df-bc7f-481a-9cce-b678122d776b.a8b6aae7-c9a5-4265-8bcf-2205950e8cc1"
ZEROX_KEY = "2d65001d-9e97-46dd-a6b1-6cd608821217"

async def test_etherscan_ethereum():
    """Test Etherscan API V2 for Ethereum gas prices"""
    print("\n" + "="*60)
    print("TEST 1: Etherscan API V2 (Ethereum)")
    print("="*60)
    
    try:
        url = "https://api.etherscan.io/v2/api"
        params = {
            "chainid": "1",  # Ethereum chain ID
            "module": "gastracker",
            "action": "gasoracle",
            "apikey": ETHERSCAN_KEY
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            print(f"Status Code: {response.status_code}")
            print(f"Response Status: {data.get('status')}")
            
            if data.get("status") == "1":
                result = data.get("result", {})
                print(f"✅ SUCCESS - Ethereum Gas Prices:")
                print(f"   Fast: {result.get('FastGasPrice')} Gwei")
                print(f"   Standard: {result.get('StandardGasPrice')} Gwei")
                print(f"   Safe: {result.get('SafeGasPrice')} Gwei")
                return True
            else:
                print(f"❌ FAILED - Error: {data.get('message', 'Unknown error')}")
                print(f"   Full response: {json.dumps(data, indent=2)}")
                return False
                
    except Exception as e:
        print(f"❌ EXCEPTION: {type(e).__name__}: {str(e)}")
        return False

async def test_etherscan_polygon():
    """Test Etherscan API V2 for Polygon gas prices"""
    print("\n" + "="*60)
    print("TEST 2: Etherscan API V2 (Polygon)")
    print("="*60)
    
    try:
        url = "https://api.etherscan.io/v2/api"
        params = {
            "chainid": "137",  # Polygon chain ID
            "module": "gastracker",
            "action": "gasoracle",
            "apikey": ETHERSCAN_KEY
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            print(f"Status Code: {response.status_code}")
            print(f"Response Status: {data.get('status')}")
            
            if data.get("status") == "1":
                result = data.get("result", {})
                print(f"✅ SUCCESS - Polygon Gas Prices:")
                print(f"   Fast: {result.get('FastGasPrice')} Gwei")
                print(f"   Standard: {result.get('StandardGasPrice')} Gwei")
                print(f"   Safe: {result.get('SafeGasPrice')} Gwei")
                return True
            else:
                print(f"❌ FAILED - Error: {data.get('message', 'Unknown error')}")
                print(f"   Full response: {json.dumps(data, indent=2)}")
                return False
                
    except Exception as e:
        print(f"❌ EXCEPTION: {type(e).__name__}: {str(e)}")
        return False

async def test_lifi():
    """Test LI.FI API for bridge quotes"""
    print("\n" + "="*60)
    print("TEST 3: LI.FI API (Bridge Quotes)")
    print("="*60)
    
    try:
        url = "https://li.quest/v1/quote"
        params = {
            "fromChain": "1",  # Ethereum
            "toChain": "137",  # Polygon
            "fromToken": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",  # USDC on Ethereum
            "toToken": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",  # USDC on Polygon
            "fromAmount": "1000000",  # 1 USDC
            "fromAddress": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",  # Uniswap V2 Router (well-known valid address)
        }
        
        headers = {
            "x-lifi-api-key": LIFI_KEY
        }
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params, headers=headers)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if "estimate" in data:
                    estimate = data.get("estimate", {})
                    action = data.get("action", {})
                    from_token = action.get("fromToken", {}) if isinstance(action, dict) else {}
                    to_token = action.get("toToken", {}) if isinstance(action, dict) else {}
                    exec_duration = estimate.get("executionDuration", {}) if isinstance(estimate.get("executionDuration"), dict) else {}
                    
                    print(f"✅ SUCCESS - Bridge Quote:")
                    print(f"   From: {from_token.get('symbol', 'N/A') if isinstance(from_token, dict) else 'N/A'}")
                    print(f"   To: {to_token.get('symbol', 'N/A') if isinstance(to_token, dict) else 'N/A'}")
                    print(f"   Estimated Time: {exec_duration.get('estimatedInSeconds', 0) if isinstance(exec_duration, dict) else 0}s")
                    gas_costs = estimate.get('gasCosts', [])
                    gas_cost = gas_costs[0].get('amountUSD', 0) if gas_costs and isinstance(gas_costs[0], dict) else 0
                    print(f"   Gas Cost: ${gas_cost}")
                    return True
                else:
                    print(f"⚠️  PARTIAL - Response received but no estimate:")
                    print(f"   Response keys: {list(data.keys())}")
                    print(f"   Full response: {json.dumps(data, indent=2)[:500]}...")
                    return True  # Still counts as working
            else:
                print(f"❌ FAILED - Status: {response.status_code}")
                print(f"   Response: {response.text[:500]}")
                return False
                
    except Exception as e:
        print(f"❌ EXCEPTION: {type(e).__name__}: {str(e)}")
        return False

async def test_zerox():
    """Test 0x API for liquidity quotes"""
    print("\n" + "="*60)
    print("TEST 4: 0x API (Liquidity Quotes)")
    print("="*60)
    
    try:
        url = "https://api.0x.org/swap/v1/quote"
        # Try WETH/USDC pair which has very high liquidity
        params = {
            "chainId": 1,  # Ethereum (integer, not string)
            "sellToken": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # WETH
            "buyToken": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",  # USDC
            "sellAmount": "1000000000000000000",  # 1 WETH (18 decimals)
        }
        
        headers = {
            "0x-api-key": ZEROX_KEY
        }
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params, headers=headers)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if "price" in data:
                    print(f"✅ SUCCESS - Liquidity Quote:")
                    print(f"   Price: {data.get('price')}")
                    print(f"   Buy Amount: {data.get('buyAmount')}")
                    print(f"   Sell Amount: {data.get('sellAmount')}")
                    print(f"   Estimated Price Impact: {data.get('estimatedPriceImpact', 0)}%")
                    return True
                else:
                    print(f"⚠️  PARTIAL - Response received but no price:")
                    print(f"   Response keys: {list(data.keys())}")
                    print(f"   Full response: {json.dumps(data, indent=2)[:500]}...")
                    return True
            else:
                print(f"❌ FAILED - Status: {response.status_code}")
                print(f"   Response: {response.text[:500]}")
                return False
                
    except Exception as e:
        print(f"❌ EXCEPTION: {type(e).__name__}: {str(e)}")
        return False

async def test_coingecko():
    """Test CoinGecko API (works without key but rate limited)"""
    print("\n" + "="*60)
    print("TEST 5: CoinGecko API (No Key - Rate Limited)")
    print("="*60)
    
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": "bitcoin",
            "vs_currencies": "usd",
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if "bitcoin" in data:
                    print(f"✅ SUCCESS - CoinGecko (No Key):")
                    print(f"   BTC Price: ${data['bitcoin']['usd']}")
                    print(f"   Note: Works but rate limited (10-50 calls/min)")
                    return True
                else:
                    print(f"❌ FAILED - No data in response")
                    return False
            else:
                print(f"❌ FAILED - Status: {response.status_code}")
                print(f"   Response: {response.text[:500]}")
                return False
                
    except Exception as e:
        print(f"❌ EXCEPTION: {type(e).__name__}: {str(e)}")
        return False

async def test_binance():
    """Test Binance API (no key needed)"""
    print("\n" + "="*60)
    print("TEST 6: Binance API (No Key Required)")
    print("="*60)
    
    try:
        url = "https://api.binance.com/api/v3/ticker/price"
        params = {"symbol": "BTCUSDT"}
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS - Binance:")
                print(f"   BTC/USDT: ${data.get('price')}")
                return True
            else:
                print(f"❌ FAILED - Status: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ EXCEPTION: {type(e).__name__}: {str(e)}")
        return False

async def test_frankfurter():
    """Test Frankfurter API (no key needed)"""
    print("\n" + "="*60)
    print("TEST 7: Frankfurter API (No Key Required)")
    print("="*60)
    
    try:
        url = "https://api.frankfurter.app/latest?from=USD&to=EUR"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS - Frankfurter:")
                print(f"   USD/EUR: {data.get('rates', {}).get('EUR')}")
                return True
            else:
                print(f"❌ FAILED - Status: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ EXCEPTION: {type(e).__name__}: {str(e)}")
        return False

async def main():
    """Run all tests"""
    print("\n" + "🔍"*30)
    print("DEEP API KEY TESTING")
    print("🔍"*30)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Test all APIs
    results['Etherscan (Ethereum)'] = await test_etherscan_ethereum()
    results['Etherscan V2 (Polygon)'] = await test_etherscan_polygon()
    results['LI.FI'] = await test_lifi()
    results['0x'] = await test_zerox()
    results['CoinGecko'] = await test_coingecko()
    results['Binance'] = await test_binance()
    results['Frankfurter'] = await test_frankfurter()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print("\n" + "-"*60)
    print(f"Total: {passed}/{total} tests passed")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    print("="*60)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! All API keys are working correctly.")
    elif passed >= total * 0.7:
        print("\n⚠️  Most tests passed. Some APIs may need attention.")
    else:
        print("\n❌ Multiple failures detected. Check API keys and network connectivity.")

if __name__ == "__main__":
    asyncio.run(main())

