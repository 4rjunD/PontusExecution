import httpx
import asyncio
from typing import List, Dict
from app.clients.base_client import BaseClient
from app.schemas.route_segment import RouteSegment, SegmentType


class BankRailClient(BaseClient):
    """Fetches bank rail estimates from Wise/Remitly calculators + hard-coded fee table"""
    
    # Hard-coded fee table for bank rails
    FEE_TABLE = {
        ("USD", "EUR"): {"fee_percent": 0.5, "fixed_fee": 2.0, "latency_min": 1, "latency_max": 3},
        ("EUR", "USD"): {"fee_percent": 0.5, "fixed_fee": 2.0, "latency_min": 1, "latency_max": 3},
        ("USD", "GBP"): {"fee_percent": 0.6, "fixed_fee": 1.5, "latency_min": 1, "latency_max": 2},
        ("GBP", "USD"): {"fee_percent": 0.6, "fixed_fee": 1.5, "latency_min": 1, "latency_max": 2},
        ("USD", "CAD"): {"fee_percent": 0.4, "fixed_fee": 1.0, "latency_min": 0, "latency_max": 1},
        ("CAD", "USD"): {"fee_percent": 0.4, "fixed_fee": 1.0, "latency_min": 0, "latency_max": 1},
        ("USD", "MXN"): {"fee_percent": 0.8, "fixed_fee": 3.0, "latency_min": 1, "latency_max": 2},
        ("MXN", "USD"): {"fee_percent": 0.8, "fixed_fee": 3.0, "latency_min": 1, "latency_max": 2},
    }
    
    async def fetch_segments(self) -> List[RouteSegment]:
        segments = []
        
        # Common bank rail routes
        routes = [
            ("USD", "EUR"), ("EUR", "USD"),
            ("USD", "GBP"), ("GBP", "USD"),
            ("USD", "CAD"), ("CAD", "USD"),
            ("USD", "MXN"), ("MXN", "USD"),
        ]
        
        tasks = []
        for from_curr, to_curr in routes:
            tasks.append(self._fetch_wise(from_curr, to_curr))
            tasks.append(self._fetch_remitly(from_curr, to_curr))
            tasks.append(self._fetch_hardcoded(from_curr, to_curr))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, RouteSegment):
                segments.append(result)
        
        return segments
    
    async def _fetch_wise(self, from_curr: str, to_curr: str) -> RouteSegment:
        """Fetch from Wise calculator - API endpoint may not be publicly available"""
        # Wise API requires authentication and is not publicly accessible
        # Return None gracefully - hard-coded fee table provides backup
        return None
    
    async def _fetch_remitly(self, from_curr: str, to_curr: str) -> RouteSegment:
        """Fetch from Remitly calculator - API endpoint may not be publicly available"""
        # Remitly API requires authentication and is not publicly accessible
        # Return None gracefully - hard-coded fee table provides backup
        return None
    
    async def _fetch_hardcoded(self, from_curr: str, to_curr: str) -> RouteSegment:
        """Use hard-coded fee table"""
        try:
            key = (from_curr, to_curr)
            if key in self.FEE_TABLE:
                fee_data = self.FEE_TABLE[key]
                
                return self.normalize_segment(
                    segment_type=SegmentType.BANK_RAIL,
                    from_asset=from_curr,
                    to_asset=to_curr,
                    from_network=None,
                    to_network=None,
                    cost={
                        "fee_percent": fee_data["fee_percent"],
                        "fixed_fee": fee_data["fixed_fee"],
                        "effective_fx_rate": None
                    },
                    latency={
                        "min_minutes": fee_data["latency_min"],
                        "max_minutes": fee_data["latency_max"]
                    },
                    reliability_score=0.85,
                    provider="hardcoded_fee_table"
                )
        except Exception as e:
            pass
        return None

