import httpx
import asyncio
from typing import List, Dict, Any
from datetime import datetime
import uuid

from app.clients import (
    FXClient, CryptoClient, GasClient, BridgeClient,
    RampClient, BankRailClient, LiquidityClient, RegulatoryClient
)
from app.schemas.route_segment import RouteSegment
from app.infra.redis_client import cache_set, cache_get
from app.infra.database import AsyncSessionLocal
from app.models.route_segment import RouteSegmentModel, SnapshotModel
from sqlalchemy import select
import json


class AggregatorService:
    """Aggregates data from all adapters, normalizes, caches, and persists"""
    
    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=30.0)
        self.clients = {
            "fx": FXClient(self.http_client),
            "crypto": CryptoClient(self.http_client),
            "gas": GasClient(self.http_client),
            "bridge": BridgeClient(self.http_client),
            "ramp": RampClient(self.http_client),
            "bank_rail": BankRailClient(self.http_client),
            "liquidity": LiquidityClient(self.http_client),
            "regulatory": RegulatoryClient(self.http_client),
        }
    
    async def fetch_all_segments(self) -> List[RouteSegment]:
        """Fetch segments from all adapters in parallel"""
        tasks = [
            self.clients["fx"].fetch_segments(),
            self.clients["crypto"].fetch_segments(),
            self.clients["gas"].fetch_segments(),
            self.clients["bridge"].fetch_segments(),
            self.clients["ramp"].fetch_segments(),
            self.clients["bank_rail"].fetch_segments(),
            self.clients["liquidity"].fetch_segments(),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_segments = []
        for result in results:
            if isinstance(result, list):
                all_segments.extend(result)
            elif isinstance(result, Exception):
                # Log error but continue
                pass
        
        # Apply regulatory constraints
        regulatory_client = self.clients["regulatory"]
        filtered_segments = []
        for segment in all_segments:
            if regulatory_client.is_allowed(segment.from_asset, segment.to_asset):
                # Add regulatory constraints to segment
                segment.constraints.update(regulatory_client.get_constraints())
                filtered_segments.append(segment)
        
        return filtered_segments
    
    async def cache_segments(self, segments: List[RouteSegment]):
        """Cache segments in Redis"""
        cache_key = "routes:segments:latest"
        segments_dict = [seg.dict() for seg in segments]
        await cache_set(cache_key, segments_dict, ttl=2)
        
        # Also cache by segment type
        by_type: Dict[str, List[Dict]] = {}
        for seg in segments_dict:
            seg_type = seg.get("segment_type")
            if seg_type not in by_type:
                by_type[seg_type] = []
            by_type[seg_type].append(seg)
        
        for seg_type, segs in by_type.items():
            await cache_set(f"routes:segments:{seg_type}", segs, ttl=2)
    
    async def persist_segments(self, segments: List[RouteSegment]):
        """Persist segments to Postgres"""
        async with AsyncSessionLocal() as session:
            try:
                # Convert to models and insert/update
                for seg in segments:
                    # Check if segment exists (by provider, type, from_asset, to_asset)
                    stmt = select(RouteSegmentModel).where(
                        RouteSegmentModel.provider == seg.provider,
                        RouteSegmentModel.segment_type == seg.segment_type.value,
                        RouteSegmentModel.from_asset == seg.from_asset,
                        RouteSegmentModel.to_asset == seg.to_asset,
                    )
                    result = await session.execute(stmt)
                    existing = result.scalar_one_or_none()
                    
                    if existing:
                        # Update existing
                        existing.cost = seg.cost
                        existing.latency = seg.latency
                        existing.reliability_score = seg.reliability_score
                        existing.constraints = seg.constraints
                        existing.timestamp = seg.timestamp
                    else:
                        # Create new
                        new_segment = RouteSegmentModel(
                            id=str(uuid.uuid4()),
                            segment_type=seg.segment_type.value,
                            from_asset=seg.from_asset,
                            to_asset=seg.to_asset,
                            from_network=seg.from_network,
                            to_network=seg.to_network,
                            cost=seg.cost,
                            latency=seg.latency,
                            reliability_score=seg.reliability_score,
                            constraints=seg.constraints,
                            provider=seg.provider,
                            timestamp=seg.timestamp,
                        )
                        session.add(new_segment)
                
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise
    
    async def persist_snapshot(self, segments: List[RouteSegment]):
        """Persist a snapshot of all segments"""
        async with AsyncSessionLocal() as session:
            try:
                # Serialize segments to JSON-compatible format
                segments_data = []
                for seg in segments:
                    seg_dict = seg.dict()
                    # Convert any datetime objects to ISO format strings
                    for key, value in seg_dict.items():
                        if isinstance(value, datetime):
                            seg_dict[key] = value.isoformat()
                    segments_data.append(seg_dict)
                
                snapshot_data = {
                    "segments": segments_data,
                    "timestamp": datetime.utcnow().isoformat(),
                    "count": len(segments)
                }
                
                snapshot = SnapshotModel(
                    id=str(uuid.uuid4()),
                    snapshot_data=snapshot_data,
                    segment_count=len(segments)
                )
                session.add(snapshot)
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise
    
    async def get_cached_segments(self, segment_type: str = None) -> List[RouteSegment]:
        """Get segments from cache"""
        if segment_type:
            cache_key = f"routes:segments:{segment_type}"
        else:
            cache_key = "routes:segments:latest"
        
        cached = await cache_get(cache_key)
        if cached:
            return [RouteSegment(**seg) for seg in cached]
        return []
    
    async def get_segments_from_db(
        self,
        segment_type: str = None,
        from_asset: str = None,
        to_asset: str = None,
        limit: int = 100
    ) -> List[RouteSegment]:
        """Get segments from database"""
        async with AsyncSessionLocal() as session:
            try:
                stmt = select(RouteSegmentModel)
                
                if segment_type:
                    stmt = stmt.where(RouteSegmentModel.segment_type == segment_type)
                if from_asset:
                    stmt = stmt.where(RouteSegmentModel.from_asset == from_asset)
                if to_asset:
                    stmt = stmt.where(RouteSegmentModel.to_asset == to_asset)
                
                stmt = stmt.order_by(RouteSegmentModel.timestamp.desc()).limit(limit)
                
                result = await session.execute(stmt)
                models = result.scalars().all()
                
                segments = []
                for model in models:
                    seg = RouteSegment(
                        id=model.id,
                        segment_type=model.segment_type,
                        from_asset=model.from_asset,
                        to_asset=model.to_asset,
                        from_network=model.from_network,
                        to_network=model.to_network,
                        cost=model.cost,
                        latency=model.latency,
                        reliability_score=model.reliability_score,
                        constraints=model.constraints,
                        provider=model.provider,
                        timestamp=model.timestamp,
                    )
                    segments.append(seg)
                
                return segments
            except Exception as e:
                return []
    
    async def get_latest_snapshot(self) -> Dict[str, Any]:
        """Get latest snapshot from database"""
        async with AsyncSessionLocal() as session:
            try:
                stmt = select(SnapshotModel).order_by(
                    SnapshotModel.created_at.desc()
                ).limit(1)
                
                result = await session.execute(stmt)
                snapshot = result.scalar_one_or_none()
                
                if snapshot:
                    return snapshot.snapshot_data
                return {}
            except Exception as e:
                return {}
    
    async def close(self):
        """Close HTTP client"""
        await self.http_client.aclose()

