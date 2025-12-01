import httpx
import asyncio
from typing import List
from app.clients.base_client import BaseClient
from app.schemas.route_segment import RouteSegment, SegmentType
from app.config import settings
from datetime import datetime


class FXClient(BaseClient):
    """Fetches FX rates from multiple free APIs: Frankfurter, ExConvert, UniRateAPI, ExchangeRate API"""
    
    async def fetch_segments(self) -> List[RouteSegment]:
        segments = []
        
        # Common currency pairs to fetch
        pairs = [
            ("USD", "EUR"), ("EUR", "USD"), ("USD", "GBP"), ("GBP", "USD"),
            ("USD", "JPY"), ("JPY", "USD"), ("EUR", "GBP"), ("GBP", "EUR"),
            ("USD", "CAD"), ("CAD", "USD"), ("USD", "AUD"), ("AUD", "USD"),
            ("USD", "INR"), ("INR", "USD"), ("USD", "CNY"), ("CNY", "USD"),
        ]
        
        # Use batch fetching from Frankfurter for efficiency (can fetch multiple pairs at once)
        # Group by base currency for batch requests
        usd_targets = ["EUR", "GBP", "JPY", "CAD", "AUD", "INR", "CNY"]
        eur_targets = ["USD", "GBP"]
        
        batch_tasks = [
            self._fetch_frankfurter_batch("USD", usd_targets),
            self._fetch_frankfurter_batch("EUR", eur_targets),
        ]
        
        # Also fetch individual pairs from other sources for redundancy
        individual_tasks = []
        for from_curr, to_curr in pairs:
            individual_tasks.append(self._fetch_frankfurter(from_curr, to_curr))
            individual_tasks.append(self._fetch_exchangerate_api(from_curr, to_curr))
            individual_tasks.append(self._fetch_ratesdb(from_curr, to_curr))
        
        # Execute batch and individual requests in parallel
        batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
        individual_results = await asyncio.gather(*individual_tasks, return_exceptions=True)
        
        # Collect all segments
        for result in batch_results:
            if isinstance(result, list):
                segments.extend(result)
            elif isinstance(result, RouteSegment):
                segments.append(result)
        
        for result in individual_results:
            if isinstance(result, RouteSegment):
                segments.append(result)
        
        return segments
    
    async def _fetch_frankfurter(self, from_curr: str, to_curr: str) -> RouteSegment:
        """Fetch from Frankfurter API (free, no key required)"""
        try:
            url = f"https://api.frankfurter.app/latest?from={from_curr}&to={to_curr}"
            response = await self.client.get(url, timeout=5.0)
            response.raise_for_status()
            data = response.json()
            
            rate = data.get("rates", {}).get(to_curr)
            if rate:
                return self.normalize_segment(
                    segment_type=SegmentType.FX,
                    from_asset=from_curr,
                    to_asset=to_curr,
                    cost={
                        "fee_percent": 0.0,
                        "fixed_fee": 0.0,
                        "effective_fx_rate": rate
                    },
                    latency={"min_minutes": 0, "max_minutes": 1},
                    reliability_score=0.95,
                    provider="frankfurter"
                )
        except Exception as e:
            pass
        return None
    
    async def _fetch_exchangerate_api(self, from_curr: str, to_curr: str) -> RouteSegment:
        """Fetch from ExchangeRate API"""
        try:
            # Use API key if provided
            api_key = settings.exchangerate_api_key or "demo"
            url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{from_curr}/{to_curr}"
            response = await self.client.get(url, timeout=5.0)
            
            # Handle 403 (forbidden) gracefully
            if response.status_code == 403:
                return None
            
            response.raise_for_status()
            data = response.json()
            
            rate = data.get("conversion_rate")
            if rate:
                return self.normalize_segment(
                    segment_type=SegmentType.FX,
                    from_asset=from_curr,
                    to_asset=to_curr,
                    cost={
                        "fee_percent": 0.0,
                        "fixed_fee": 0.0,
                        "effective_fx_rate": rate
                    },
                    latency={"min_minutes": 0, "max_minutes": 1},
                    reliability_score=0.90,
                    provider="exchangerate_api"
                )
        except httpx.HTTPStatusError as e:
            # Handle HTTP errors gracefully
            if e.response.status_code in [403, 404]:
                return None
        except Exception as e:
            pass
        return None
    
    async def _fetch_frankfurter_batch(self, base_curr: str, target_currs: list) -> List[RouteSegment]:
        """Fetch multiple rates from Frankfurter in one call (more efficient)"""
        segments = []
        try:
            to_currs = ",".join(target_currs)
            url = f"https://api.frankfurter.app/latest?from={base_curr}&to={to_currs}"
            response = await self.client.get(url, timeout=5.0)
            response.raise_for_status()
            data = response.json()
            
            rates = data.get("rates", {})
            for to_curr, rate in rates.items():
                segments.append(self.normalize_segment(
                    segment_type=SegmentType.FX,
                    from_asset=base_curr,
                    to_asset=to_curr,
                    cost={
                        "fee_percent": 0.0,
                        "fixed_fee": 0.0,
                        "effective_fx_rate": rate
                    },
                    latency={"min_minutes": 0, "max_minutes": 1},
                    reliability_score=0.95,
                    provider="frankfurter"
                ))
        except Exception as e:
            pass
        return segments
    
    async def _fetch_ratesdb(self, from_curr: str, to_curr: str) -> RouteSegment:
        """Fetch from RatesDB API (free, 100 requests/minute, ECB data)"""
        try:
            url = f"https://api.ratesdb.com/v1/convert/{from_curr}/{to_curr}"
            response = await self.client.get(url, timeout=5.0)
            response.raise_for_status()
            data = response.json()
            
            rate = data.get("rate") or data.get("result")
            if rate:
                return self.normalize_segment(
                    segment_type=SegmentType.FX,
                    from_asset=from_curr,
                    to_asset=to_curr,
                    cost={
                        "fee_percent": 0.0,
                        "fixed_fee": 0.0,
                        "effective_fx_rate": float(rate)
                    },
                    latency={"min_minutes": 0, "max_minutes": 1},
                    reliability_score=0.93,
                    provider="ratesdb"
                )
        except Exception as e:
            pass
        return None
    
    async def _fetch_ecb(self, from_curr: str, to_curr: str) -> RouteSegment:
        """Fetch from ECB (European Central Bank) - EUR base only"""
        # Note: exchangerate.host now requires API key, skipping for now
        return None

