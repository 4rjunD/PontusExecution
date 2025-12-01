import httpx
import asyncio
from typing import List
from app.clients.base_client import BaseClient
from app.schemas.route_segment import RouteSegment, SegmentType
from app.config import settings


class BridgeClient(BaseClient):
    """Fetches bridge quotes from Socket and LI.FI"""
    
    async def fetch_segments(self) -> List[RouteSegment]:
        segments = []
        
        # Common bridge routes
        routes = [
            ("ethereum", "polygon", "USDC", "USDC"),
            ("ethereum", "arbitrum", "USDC", "USDC"),
            ("polygon", "ethereum", "USDC", "USDC"),
            ("ethereum", "optimism", "ETH", "ETH"),
        ]
        
        tasks = []
        for from_net, to_net, from_asset, to_asset in routes:
            tasks.append(self._fetch_socket(from_net, to_net, from_asset, to_asset))
            tasks.append(self._fetch_lifi(from_net, to_net, from_asset, to_asset))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, RouteSegment):
                segments.append(result)
        
        return segments
    
    async def _fetch_socket(self, from_net: str, to_net: str, from_asset: str, to_asset: str) -> RouteSegment:
        """Fetch from Socket API"""
        try:
            url = "https://api.socket.tech/v2/quote"
            params = {
                "fromChainId": self._get_chain_id(from_net),
                "toChainId": self._get_chain_id(to_net),
                "fromTokenAddress": self._get_token_address(from_asset, from_net),
                "toTokenAddress": self._get_token_address(to_asset, to_net),
                "fromAmount": "1000000",  # 1 USDC/USDT (6 decimals)
                "userAddress": "0x0000000000000000000000000000000000000000",
            }
            
            headers = {}
            if settings.socket_api_key:
                headers["API-KEY"] = settings.socket_api_key
            
            response = await self.client.get(url, params=params, headers=headers, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            
            if data.get("success"):
                route = data.get("result", {})
                # Extract fee information
                fee_percent = 0.0
                if "bridgeFees" in route:
                    fee_percent = float(route.get("bridgeFees", {}).get("fee", 0)) / 1000000
                
                return self.normalize_segment(
                    segment_type=SegmentType.BRIDGE,
                    from_asset=from_asset,
                    to_asset=to_asset,
                    from_network=from_net,
                    to_network=to_net,
                    cost={
                        "fee_percent": fee_percent,
                        "fixed_fee": 0.0,
                        "effective_fx_rate": None
                    },
                    latency={"min_minutes": 5, "max_minutes": 30},
                    reliability_score=0.90,
                    provider="socket"
                )
        except Exception as e:
            pass
        return None
    
    async def _fetch_lifi(self, from_net: str, to_net: str, from_asset: str, to_asset: str) -> RouteSegment:
        """Fetch from LI.FI API"""
        try:
            url = "https://li.quest/v1/quote"
            params = {
                "fromChain": self._get_chain_id(from_net),
                "toChain": self._get_chain_id(to_net),
                "fromToken": self._get_token_address(from_asset, from_net),
                "toToken": self._get_token_address(to_asset, to_net),
                "fromAmount": "1000000",
                "fromAddress": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",  # Uniswap V2 Router (well-known valid address)
            }
            
            headers = {}
            if settings.lifi_api_key:
                headers["x-lifi-api-key"] = settings.lifi_api_key
            
            response = await self.client.get(url, params=params, headers=headers, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            
            if "estimate" in data:
                estimate = data.get("estimate", {})
                fee_percent = float(estimate.get("feeCosts", [{}])[0].get("amountUSD", 0)) / 100.0 if estimate.get("feeCosts") else 0.0
                
                return self.normalize_segment(
                    segment_type=SegmentType.BRIDGE,
                    from_asset=from_asset,
                    to_asset=to_asset,
                    from_network=from_net,
                    to_network=to_net,
                    cost={
                        "fee_percent": fee_percent,
                        "fixed_fee": 0.0,
                        "effective_fx_rate": None
                    },
                    latency={"min_minutes": 5, "max_minutes": 45},
                    reliability_score=0.88,
                    provider="lifi"
                )
        except Exception as e:
            pass
        return None
    
    def _get_chain_id(self, network: str) -> str:
        """Map network name to chain ID"""
        chain_map = {
            "ethereum": "1",
            "polygon": "137",
            "arbitrum": "42161",
            "optimism": "10",
            "bsc": "56",
        }
        return chain_map.get(network.lower(), "1")
    
    def _get_token_address(self, asset: str, network: str) -> str:
        """Map asset to token address"""
        # Common token addresses (simplified)
        if asset == "USDC":
            if network == "ethereum":
                return "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
            elif network == "polygon":
                return "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
        elif asset == "USDT":
            if network == "ethereum":
                return "0xdAC17F958D2ee523a2206206994597C13D831ec7"
        elif asset == "ETH":
            return "0x0000000000000000000000000000000000000000"  # Native token
        return "0x0000000000000000000000000000000000000000"

