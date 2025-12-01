import httpx
import asyncio
from typing import List
from app.clients.base_client import BaseClient
from app.schemas.route_segment import RouteSegment, SegmentType
from app.config import settings


class LiquidityClient(BaseClient):
    """Fetches liquidity data from 0x and Uniswap subgraph"""
    
    async def fetch_segments(self) -> List[RouteSegment]:
        segments = []
        
        # Common liquidity pairs (prioritize high liquidity pairs)
        pairs = [
            ("WETH", "USDC", "ethereum"),  # Highest liquidity pair
            ("USDC", "USDT", "ethereum"),
            ("DAI", "USDC", "ethereum"),
            ("USDC", "USDT", "polygon"),
        ]
        
        tasks = []
        for from_asset, to_asset, network in pairs:
            # Removed: 0x API (404 errors, not working)
            tasks.append(self._fetch_uniswap_subgraph(from_asset, to_asset, network))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, RouteSegment):
                segments.append(result)
        
        return segments
    
    async def _fetch_zerox(self, from_asset: str, to_asset: str, network: str) -> RouteSegment:
        """Fetch from 0x API - tries multiple approaches"""
        try:
            chain_id = int(self._get_chain_id(network))  # Convert to integer
            url = "https://api.0x.org/swap/v1/quote"
            
            # Get token addresses
            sell_token = self._get_token_address(from_asset, network)
            buy_token = self._get_token_address(to_asset, network)
            
            # Skip if token addresses are invalid (zero address)
            if sell_token == "0x0000000000000000000000000000000000000000" or buy_token == "0x0000000000000000000000000000000000000000":
                return None
            
            # Determine sell amount based on token decimals
            if from_asset == "WETH" or from_asset == "ETH":
                sell_amount = "1000000000000000000"  # 1 WETH (18 decimals)
            else:
                sell_amount = "1000000000"  # 1000 tokens (6 decimals)
            
            headers = {}
            if settings.zerox_api_key:
                headers["0x-api-key"] = settings.zerox_api_key
                headers["0x-version"] = "v2"  # Use v2 API
            
            # Try with token addresses first
            params = {
                "chainId": chain_id,
                "sellToken": sell_token,
                "buyToken": buy_token,
                "sellAmount": sell_amount,
                "taker": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
            }
            
            response = await self.client.get(url, params=params, headers=headers, timeout=10.0)
            
            # If 404, try with token symbols instead (for native tokens like ETH)
            if response.status_code == 404:
                # Try with symbols for native tokens
                if from_asset == "ETH":
                    params["sellToken"] = "ETH"
                if to_asset == "ETH":
                    params["buyToken"] = "ETH"
                
                response = await self.client.get(url, params=params, headers=headers, timeout=10.0)
            
            # 0x API may return 404 if route doesn't exist or API key has limited access
            if response.status_code == 404:
                return None  # Route not available, skip silently
            
            response.raise_for_status()
            data = response.json()
            
            if "price" in data:
                price = float(data.get("price", 0))
                # Calculate fee from price impact
                fee_percent = float(data.get("estimatedPriceImpact", 0))
                
                return self.normalize_segment(
                    segment_type=SegmentType.LIQUIDITY,
                    from_asset=from_asset,
                    to_asset=to_asset,
                    from_network=network,
                    to_network=network,
                    cost={
                        "fee_percent": fee_percent,
                        "fixed_fee": 0.0,
                        "effective_fx_rate": price
                    },
                    latency={"min_minutes": 0, "max_minutes": 1},
                    reliability_score=0.95,
                    provider="0x"
                )
        except httpx.HTTPStatusError as e:
            # Handle HTTP errors gracefully - 404 means no route
            if e.response.status_code == 404:
                return None
            pass
        except Exception as e:
            pass
        return None
    
    async def _fetch_uniswap_subgraph(self, from_asset: str, to_asset: str, network: str) -> RouteSegment:
        """Fetch from Uniswap subgraph"""
        try:
            if network != "ethereum":
                # Uniswap subgraph mainly for Ethereum
                return None
            
            # Use the public Uniswap V3 subgraph endpoint
            subgraph_url = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3"
            
            # Query for pools instead of pairs (Uniswap V3 uses pools)
            query = """
            {
                pools(
                    first: 1,
                    where: {
                        token0_: {symbol: "%s"},
                        token1_: {symbol: "%s"}
                    },
                    orderBy: totalValueLockedUSD,
                    orderDirection: desc
                ) {
                    id
                    token0 {
                        symbol
                        id
                    }
                    token1 {
                        symbol
                        id
                    }
                    token0Price
                    token1Price
                    totalValueLockedUSD
                    feeTier
                }
            }
            """ % (from_asset, to_asset)
            
            response = await self.client.post(
                subgraph_url,
                json={"query": query},
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            
            if "data" in data and data["data"].get("pools"):
                pools = data["data"]["pools"]
                if pools and len(pools) > 0:
                    pool = pools[0]
                    price = float(pool.get("token0Price", 0))
                    tvl = float(pool.get("totalValueLockedUSD", 0))
                    liquidity_score = min(1.0, tvl / 1000000)  # Normalize
                    
                    return self.normalize_segment(
                        segment_type=SegmentType.LIQUIDITY,
                        from_asset=from_asset,
                        to_asset=to_asset,
                        from_network=network,
                        to_network=network,
                        cost={
                            "fee_percent": float(pool.get("feeTier", 3000)) / 10000,  # Convert basis points to percentage
                            "fixed_fee": 0.0,
                            "effective_fx_rate": price
                        },
                        latency={"min_minutes": 0, "max_minutes": 1},
                        reliability_score=liquidity_score,
                        provider="uniswap_subgraph",
                        constraints={"liquidity_score": liquidity_score, "tvl_usd": tvl}
                    )
        except Exception as e:
            pass
        return None
    
    def _get_chain_id(self, network: str) -> str:
        """Map network name to 0x chain identifier"""
        chain_map = {
            "ethereum": "1",
            "polygon": "137",
            "arbitrum": "42161",
            "optimism": "10",
        }
        return chain_map.get(network.lower(), "1")
    
    def _get_token_address(self, asset: str, network: str) -> str:
        """Map asset to token address"""
        if asset == "USDC":
            if network == "ethereum":
                return "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
            elif network == "polygon":
                return "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
        elif asset == "USDT":
            if network == "ethereum":
                return "0xdAC17F958D2ee523a2206206994597C13D831ec7"
            elif network == "polygon":
                return "0xc2132D05D31c914a87C6611C10748AEb04B58e8F"
        elif asset == "WETH":
            if network == "ethereum":
                return "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
            elif network == "polygon":
                return "0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619"  # WETH on Polygon
        elif asset == "DAI":
            if network == "ethereum":
                return "0x6B175474E89094C44Da98b954EedeAC495271d0F"
            elif network == "polygon":
                return "0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063"  # DAI on Polygon
        elif asset == "ETH":
            # Use WETH for ETH
            if network == "ethereum":
                return "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
        return "0x0000000000000000000000000000000000000000"

