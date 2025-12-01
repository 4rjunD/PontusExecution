import httpx
import asyncio
from typing import List
from app.clients.base_client import BaseClient
from app.schemas.route_segment import RouteSegment, SegmentType
from app.config import settings


class CryptoClient(BaseClient):
    """Fetches crypto prices from CoinGecko and exchanges"""
    
    async def fetch_segments(self) -> List[RouteSegment]:
        segments = []
        
        # Common crypto pairs
        pairs = [
            ("BTC", "USD"), ("ETH", "USD"), ("USDC", "USD"),
            ("BTC", "ETH"), ("ETH", "BTC"),
            ("USDT", "USD"), ("DAI", "USD"),
        ]
        
        tasks = []
        for from_asset, to_asset in pairs:
            tasks.append(self._fetch_coingecko(from_asset, to_asset))
            tasks.append(self._fetch_binance(from_asset, to_asset))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, RouteSegment):
                segments.append(result)
        
        return segments
    
    async def _fetch_coingecko(self, from_asset: str, to_asset: str) -> RouteSegment:
        """Fetch from CoinGecko"""
        try:
            # Map to CoinGecko IDs
            coin_map = {
                "BTC": "bitcoin",
                "ETH": "ethereum",
                "USDC": "usd-coin",
                "USDT": "tether",
                "DAI": "dai",
            }
            
            coin_id = coin_map.get(from_asset.upper())
            if not coin_id:
                return None
            
            url = f"https://api.coingecko.com/api/v3/simple/price"
            params = {
                "ids": coin_id,
                "vs_currencies": to_asset.lower(),
            }
            
            if settings.coingecko_api_key:
                params["x_cg_demo_api_key"] = settings.coingecko_api_key
            
            response = await self.client.get(url, params=params, timeout=5.0)
            response.raise_for_status()
            data = response.json()
            
            price = data.get(coin_id, {}).get(to_asset.lower())
            if price:
                return self.normalize_segment(
                    segment_type=SegmentType.CRYPTO,
                    from_asset=from_asset,
                    to_asset=to_asset,
                    from_network=None,
                    to_network=None,
                    cost={
                        "fee_percent": 0.0,
                        "fixed_fee": 0.0,
                        "effective_fx_rate": price
                    },
                    latency={"min_minutes": 0, "max_minutes": 1},
                    reliability_score=0.95,
                    provider="coingecko"
                )
        except Exception as e:
            pass
        return None
    
    async def _fetch_binance(self, from_asset: str, to_asset: str) -> RouteSegment:
        """Fetch from Binance exchange"""
        try:
            symbol = f"{from_asset}{to_asset}"
            url = f"https://api.binance.com/api/v3/ticker/price"
            params = {"symbol": symbol}
            
            response = await self.client.get(url, params=params, timeout=5.0)
            response.raise_for_status()
            data = response.json()
            
            price = float(data.get("price", 0))
            if price > 0:
                return self.normalize_segment(
                    segment_type=SegmentType.CRYPTO,
                    from_asset=from_asset,
                    to_asset=to_asset,
                    from_network=None,
                    to_network=None,
                    cost={
                        "fee_percent": 0.1,  # Binance trading fee
                        "fixed_fee": 0.0,
                        "effective_fx_rate": price
                    },
                    latency={"min_minutes": 0, "max_minutes": 1},
                    reliability_score=0.98,
                    provider="binance"
                )
        except Exception as e:
            # Try reverse pair
            try:
                symbol = f"{to_asset}{from_asset}"
                params = {"symbol": symbol}
                response = await self.client.get(url, params=params, timeout=5.0)
                response.raise_for_status()
                data = response.json()
                price = float(data.get("price", 0))
                if price > 0:
                    return self.normalize_segment(
                        segment_type=SegmentType.CRYPTO,
                        from_asset=from_asset,
                        to_asset=to_asset,
                        from_network=None,
                        to_network=None,
                        cost={
                            "fee_percent": 0.1,
                            "fixed_fee": 0.0,
                            "effective_fx_rate": 1.0 / price
                        },
                        latency={"min_minutes": 0, "max_minutes": 1},
                        reliability_score=0.98,
                        provider="binance"
                    )
            except:
                pass
        return None

