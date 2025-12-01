from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List, Union
from app.services.aggregator_service import AggregatorService
from app.schemas.route_segment import RouteSegmentResponse, SegmentType
from app.schemas.quotes import FXQuote, CryptoQuote, GasQuote, QuoteResponse
from datetime import datetime

router = APIRouter(prefix="/api", tags=["routes"])

# Global aggregator instance (will be initialized in main.py)
aggregator: Optional[AggregatorService] = None


def set_aggregator(agg: AggregatorService):
    """Set the aggregator service instance"""
    global aggregator
    aggregator = agg


@router.get("/health")
async def health_check():
    """
    Enhanced health check endpoint.
    Checks database, Redis, and service status.
    """
    from app.infra.database import AsyncSessionLocal
    from app.infra.redis_client import redis_client
    from app.config import settings
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "checks": {}
    }
    
    # Check database
    try:
        from sqlalchemy import text
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            await session.commit()
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check Redis
    try:
        if redis_client:
            await redis_client.ping()
            health_status["checks"]["redis"] = "healthy"
        else:
            health_status["checks"]["redis"] = "not_initialized"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["checks"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check routing service
    try:
        from app.api.routes_optimization import routing_service
        if routing_service:
            health_status["checks"]["routing_service"] = "healthy"
        else:
            health_status["checks"]["routing_service"] = "not_initialized"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["checks"]["routing_service"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Return appropriate status code
    status_code = 200 if health_status["status"] == "healthy" else 503
    
    return health_status


@router.get("/routes/segments", response_model=List[RouteSegmentResponse])
async def get_segments(
    segment_type: Optional[SegmentType] = Query(None, description="Filter by segment type"),
    from_asset: Optional[str] = Query(None, description="Filter by from asset"),
    to_asset: Optional[str] = Query(None, description="Filter by to asset"),
    use_cache: bool = Query(True, description="Use cached data if available"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results")
):
    """Get route segments with optional filters"""
    if not aggregator:
        raise HTTPException(status_code=503, detail="Aggregator service not initialized")
    
    try:
        if use_cache:
            # Try cache first
            cached = await aggregator.get_cached_segments(
                segment_type.value if segment_type else None
            )
            if cached:
                # Apply filters
                filtered = cached
                if from_asset:
                    filtered = [s for s in filtered if s.from_asset == from_asset]
                if to_asset:
                    filtered = [s for s in filtered if s.to_asset == to_asset]
                return filtered[:limit]
        
        # Fallback to database
        segments = await aggregator.get_segments_from_db(
            segment_type=segment_type.value if segment_type else None,
            from_asset=from_asset,
            to_asset=to_asset,
            limit=limit
        )
        
        return segments
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quotes/fx", response_model=QuoteResponse)
async def get_fx_quotes(
    from_currency: str = Query(..., description="From currency code"),
    to_currency: str = Query(..., description="To currency code")
):
    """Get FX quotes"""
    if not aggregator:
        raise HTTPException(status_code=503, detail="Aggregator service not initialized")
    
    try:
        segments = await aggregator.get_segments_from_db(
            segment_type=SegmentType.FX.value,
            from_asset=from_currency,
            to_asset=to_currency,
            limit=10
        )
        
        quotes = []
        for seg in segments:
            if seg.cost.get("effective_fx_rate"):
                quote = FXQuote(
                    from_currency=seg.from_asset,
                    to_currency=seg.to_asset,
                    rate=seg.cost["effective_fx_rate"],
                    provider=seg.provider or "unknown",
                    timestamp=seg.timestamp or datetime.utcnow()
                )
                quotes.append(quote)
        
        return QuoteResponse(quotes=quotes, count=len(quotes))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quotes/crypto", response_model=QuoteResponse)
async def get_crypto_quotes(
    from_asset: str = Query(..., description="From asset"),
    to_asset: str = Query(..., description="To asset"),
    from_network: Optional[str] = Query(None, description="From network"),
    to_network: Optional[str] = Query(None, description="To network")
):
    """Get crypto quotes"""
    if not aggregator:
        raise HTTPException(status_code=503, detail="Aggregator service not initialized")
    
    try:
        segments = await aggregator.get_segments_from_db(
            segment_type=SegmentType.CRYPTO.value,
            from_asset=from_asset,
            to_asset=to_asset,
            limit=10
        )
        
        # Filter by network if provided
        if from_network:
            segments = [s for s in segments if s.from_network == from_network]
        if to_network:
            segments = [s for s in segments if s.to_network == to_network]
        
        quotes = []
        for seg in segments:
            if seg.cost.get("effective_fx_rate"):
                quote = CryptoQuote(
                    from_asset=seg.from_asset,
                    to_asset=seg.to_asset,
                    from_network=seg.from_network,
                    to_network=seg.to_network,
                    rate=seg.cost["effective_fx_rate"],
                    provider=seg.provider or "unknown",
                    timestamp=seg.timestamp or datetime.utcnow()
                )
                quotes.append(quote)
        
        return QuoteResponse(quotes=quotes, count=len(quotes))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quotes/gas", response_model=QuoteResponse)
async def get_gas_quotes(
    network: str = Query(..., description="Network name")
):
    """Get gas quotes for a network"""
    if not aggregator:
        raise HTTPException(status_code=503, detail="Aggregator service not initialized")
    
    try:
        segments = await aggregator.get_segments_from_db(
            segment_type=SegmentType.GAS.value,
            limit=10
        )
        
        # Filter by network
        segments = [s for s in segments if s.from_network == network]
        
        quotes = []
        for seg in segments:
            gas_price = seg.constraints.get("gas_price_gwei") or seg.cost.get("fixed_fee", 0)
            quote = GasQuote(
                network=network,
                gas_price_gwei=gas_price,
                provider=seg.provider or "unknown",
                timestamp=seg.timestamp or datetime.utcnow()
            )
            quotes.append(quote)
        
        return QuoteResponse(quotes=quotes, count=len(quotes))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/snapshots/latest")
async def get_latest_snapshot():
    """Get the latest snapshot of all route segments"""
    if not aggregator:
        raise HTTPException(status_code=503, detail="Aggregator service not initialized")
    
    try:
        snapshot = await aggregator.get_latest_snapshot()
        return snapshot
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

