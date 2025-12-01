import httpx
import asyncio
from typing import List
from app.clients.base_client import BaseClient
from app.schemas.route_segment import RouteSegment, SegmentType
from app.config import settings


class RampClient(BaseClient):
    """Fetches on/off-ramp quotes from Transak and Onmeta"""
    
    async def fetch_segments(self) -> List[RouteSegment]:
        segments = []
        
        # Common ramp routes
        on_ramp_routes = [
            ("USD", "USDC", "ethereum"),
            ("USD", "USDT", "ethereum"),
            ("EUR", "USDC", "polygon"),
        ]
        
        off_ramp_routes = [
            ("USDC", "USD", "ethereum"),
            ("USDT", "USD", "ethereum"),
            ("USDC", "EUR", "polygon"),
        ]
        
        tasks = []
        for from_asset, to_asset, network in on_ramp_routes:
            tasks.append(self._fetch_transak_onramp(from_asset, to_asset, network))
            tasks.append(self._fetch_onmeta_onramp(from_asset, to_asset, network))
        
        for from_asset, to_asset, network in off_ramp_routes:
            tasks.append(self._fetch_transak_offramp(from_asset, to_asset, network))
            tasks.append(self._fetch_onmeta_offramp(from_asset, to_asset, network))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, RouteSegment):
                segments.append(result)
        
        return segments
    
    async def _fetch_transak_onramp(self, from_asset: str, to_asset: str, network: str) -> RouteSegment:
        """Fetch Transak on-ramp quote"""
        try:
            url = "https://api.transak.com/api/v2/currencies/crypto-currencies"
            params = {
                "fiatCurrency": from_asset,
                "cryptoCurrency": to_asset,
                "network": network,
            }
            
            headers = {}
            if settings.transak_api_key:
                headers["apiKey"] = settings.transak_api_key
            
            response = await self.client.get(url, params=params, headers=headers, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            
            # Extract fee information (simplified)
            fee_percent = 1.0  # Default estimate
            if "response" in data and isinstance(data["response"], list) and len(data["response"]) > 0:
                crypto_data = data["response"][0]
                fee_percent = float(crypto_data.get("fees", {}).get("transakFee", 1.0))
            
            return self.normalize_segment(
                segment_type=SegmentType.ON_RAMP,
                from_asset=from_asset,
                to_asset=to_asset,
                from_network=None,
                to_network=network,
                cost={
                    "fee_percent": fee_percent,
                    "fixed_fee": 0.0,
                    "effective_fx_rate": None
                },
                latency={"min_minutes": 5, "max_minutes": 30},
                reliability_score=0.85,
                provider="transak"
            )
        except Exception as e:
            pass
        return None
    
    async def _fetch_transak_offramp(self, from_asset: str, to_asset: str, network: str) -> RouteSegment:
        """Fetch Transak off-ramp quote"""
        try:
            url = "https://api.transak.com/api/v2/currencies/fiat-currencies"
            params = {
                "cryptoCurrency": from_asset,
                "fiatCurrency": to_asset,
                "network": network,
            }
            
            headers = {}
            if settings.transak_api_key:
                headers["apiKey"] = settings.transak_api_key
            
            response = await self.client.get(url, params=params, headers=headers, timeout=10.0)
            response.raise_for_status()
            
            return self.normalize_segment(
                segment_type=SegmentType.OFF_RAMP,
                from_asset=from_asset,
                to_asset=to_asset,
                from_network=network,
                to_network=None,
                cost={
                    "fee_percent": 1.5,  # Default estimate
                    "fixed_fee": 0.0,
                    "effective_fx_rate": None
                },
                latency={"min_minutes": 10, "max_minutes": 60},
                reliability_score=0.85,
                provider="transak"
            )
        except Exception as e:
            pass
        return None
    
    async def _fetch_onmeta_onramp(self, from_asset: str, to_asset: str, network: str) -> RouteSegment:
        """Fetch Onmeta on-ramp quote (test mode)"""
        try:
            url = "https://api.onmeta.in/v1/onramp/quote"
            params = {
                "fiatCurrency": from_asset,
                "cryptoCurrency": to_asset,
                "network": network,
                "amount": "100",
            }
            
            headers = {
                "Content-Type": "application/json",
            }
            if settings.onmeta_api_key:
                headers["x-api-key"] = settings.onmeta_api_key
            
            response = await self.client.get(url, params=params, headers=headers, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            
            fee_percent = float(data.get("fee", {}).get("percentage", 1.5))
            
            return self.normalize_segment(
                segment_type=SegmentType.ON_RAMP,
                from_asset=from_asset,
                to_asset=to_asset,
                from_network=None,
                to_network=network,
                cost={
                    "fee_percent": fee_percent,
                    "fixed_fee": 0.0,
                    "effective_fx_rate": None
                },
                latency={"min_minutes": 5, "max_minutes": 30},
                reliability_score=0.80,
                provider="onmeta"
            )
        except Exception as e:
            pass
        return None
    
    async def _fetch_onmeta_offramp(self, from_asset: str, to_asset: str, network: str) -> RouteSegment:
        """Fetch Onmeta off-ramp quote (test mode)"""
        try:
            url = "https://api.onmeta.in/v1/offramp/quote"
            params = {
                "cryptoCurrency": from_asset,
                "fiatCurrency": to_asset,
                "network": network,
                "amount": "100",
            }
            
            headers = {
                "Content-Type": "application/json",
            }
            if settings.onmeta_api_key:
                headers["x-api-key"] = settings.onmeta_api_key
            
            response = await self.client.get(url, params=params, headers=headers, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            
            fee_percent = float(data.get("fee", {}).get("percentage", 2.0))
            
            return self.normalize_segment(
                segment_type=SegmentType.OFF_RAMP,
                from_asset=from_asset,
                to_asset=to_asset,
                from_network=network,
                to_network=None,
                cost={
                    "fee_percent": fee_percent,
                    "fixed_fee": 0.0,
                    "effective_fx_rate": None
                },
                latency={"min_minutes": 15, "max_minutes": 90},
                reliability_score=0.80,
                provider="onmeta"
            )
        except Exception as e:
            pass
        return None

