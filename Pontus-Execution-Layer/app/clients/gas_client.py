import httpx
import asyncio
from typing import List
from app.clients.base_client import BaseClient
from app.schemas.route_segment import RouteSegment, SegmentType
from app.config import settings


class GasClient(BaseClient):
    """Fetches gas fees from Etherscan and Polygonscan"""
    
    async def fetch_segments(self) -> List[RouteSegment]:
        segments = []
        
        tasks = [
            self._fetch_etherscan(),
            self._fetch_polygonscan(),
            # Removed: BSC, Arbitrum, Optimism, Avalanche (keys invalid)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, RouteSegment):
                segments.append(result)
        
        return segments
    
    async def _fetch_etherscan(self) -> RouteSegment:
        """Fetch Ethereum gas prices using Etherscan API V2"""
        try:
            # Use Etherscan key, fallback to old working key if new one fails
            api_key = settings.etherscan_api_key or "U623XN7ZQN2EYQ139ZK4NG5JI4A9U4GAFY"
            # Use Etherscan API V2 with chainid=1 for Ethereum
            url = "https://api.etherscan.io/v2/api"
            params = {
                "chainid": "1",  # Ethereum chain ID
                "module": "gastracker",
                "action": "gasoracle",
                "apikey": api_key
            }
            
            response = await self.client.get(url, params=params, timeout=5.0)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "1":
                result = data.get("result", {})
                # Use standard gas price (in Gwei)
                gas_price = float(result.get("StandardGasPrice") or result.get("FastGasPrice", 20))
                
                return self.normalize_segment(
                    segment_type=SegmentType.GAS,
                    from_asset="ETH",
                    to_asset="ETH",
                    from_network="ethereum",
                    to_network="ethereum",
                    cost={
                        "fee_percent": 0.0,
                        "fixed_fee": gas_price,
                        "effective_fx_rate": None
                    },
                    latency={"min_minutes": 0, "max_minutes": 15},
                    reliability_score=0.95,
                    provider="etherscan_v2",
                    constraints={"gas_price_gwei": gas_price}
                )
        except Exception as e:
            pass
        return None
    
    async def _fetch_polygonscan(self) -> RouteSegment:
        """Fetch Polygon gas prices using Polygon RPC (more reliable than Etherscan V2)"""
        try:
            # Method 1: Try Polygon RPC (eth_gasPrice) - most reliable, no API key needed
            rpc_url = "https://polygon-rpc.com"
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_gasPrice",
                "params": [],
                "id": 1
            }
            
            response = await self.client.post(rpc_url, json=payload, timeout=5.0)
            response.raise_for_status()
            data = response.json()
            
            if "result" in data:
                # Convert hex to Gwei
                gas_price_hex = data["result"]
                gas_price_gwei = int(gas_price_hex, 16) / 1e9
                
                return self.normalize_segment(
                    segment_type=SegmentType.GAS,
                    from_asset="MATIC",
                    to_asset="MATIC",
                    from_network="polygon",
                    to_network="polygon",
                    cost={
                        "fee_percent": 0.0,
                        "fixed_fee": gas_price_gwei,
                        "effective_fx_rate": None
                    },
                    latency={"min_minutes": 0, "max_minutes": 2},
                    reliability_score=0.95,
                    provider="polygon_rpc",
                    constraints={"gas_price_gwei": gas_price_gwei}
                )
        except Exception as e:
            # Fallback: Try Polygonscan direct API if RPC fails
            try:
                api_key = settings.polygonscan_api_key or settings.etherscan_api_key or "U623XN7ZQN2EYQ139ZK4NG5JI4A9U4GAFY"
                url = "https://api.polygonscan.com/api"
                params = {
                    "module": "gastracker",
                    "action": "gasoracle",
                    "apikey": api_key
                }
                
                response = await self.client.get(url, params=params, timeout=5.0)
                response.raise_for_status()
                data = response.json()
                
                if data.get("status") == "1":
                    result = data.get("result", {})
                    gas_price = float(result.get("StandardGasPrice") or result.get("FastGasPrice", 30))
                    
                    return self.normalize_segment(
                        segment_type=SegmentType.GAS,
                        from_asset="MATIC",
                        to_asset="MATIC",
                        from_network="polygon",
                        to_network="polygon",
                        cost={
                            "fee_percent": 0.0,
                            "fixed_fee": gas_price,
                            "effective_fx_rate": None
                        },
                        latency={"min_minutes": 0, "max_minutes": 2},
                        reliability_score=0.95,
                        provider="polygonscan_api",
                        constraints={"gas_price_gwei": gas_price}
                    )
            except Exception:
                pass
        return None

