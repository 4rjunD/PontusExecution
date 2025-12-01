import httpx
from typing import Dict, Any, List, Optional
from app.schemas.route_segment import RouteSegment, SegmentType
from datetime import datetime


class BaseClient:
    def __init__(self, client: httpx.AsyncClient):
        self.client = client
    
    async def fetch_segments(self) -> List[RouteSegment]:
        """Override in subclasses to fetch and normalize data"""
        raise NotImplementedError
    
    def normalize_segment(
        self,
        segment_type: SegmentType,
        from_asset: str,
        to_asset: str,
        cost: Dict[str, Any],
        latency: Dict[str, int],
        reliability_score: float = 1.0,
        constraints: Dict[str, Any] = None,
        provider: Optional[str] = None,
        from_network: Optional[str] = None,
        to_network: Optional[str] = None,
    ) -> RouteSegment:
        """Helper to create normalized RouteSegment"""
        return RouteSegment(
            segment_type=segment_type,
            from_asset=from_asset,
            to_asset=to_asset,
            from_network=from_network,
            to_network=to_network,
            cost=cost,
            latency=latency,
            reliability_score=reliability_score,
            constraints=constraints or {},
            provider=provider,
            timestamp=datetime.utcnow(),
        )


