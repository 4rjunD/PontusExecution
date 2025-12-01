"""
Routing Optimization API Endpoints
"""
from fastapi import APIRouter, Query, HTTPException, Depends, Request
from typing import Optional, List
from pydantic import BaseModel

from app.services.routing_service import RoutingService
from app.services.aggregator_service import AggregatorService
from app.schemas.route_segment import RouteSegment
from app.middleware.rate_limit import limiter
from app.config import settings

router = APIRouter(prefix="/api/routes", tags=["optimization"])

# Global routing service instance
routing_service: Optional[RoutingService] = None
aggregator_service: Optional[AggregatorService] = None


def set_routing_service(service: RoutingService):
    """Set the routing service instance"""
    global routing_service
    routing_service = service


def set_aggregator_for_routing(agg: AggregatorService):
    """Set the aggregator service for routing"""
    global aggregator_service
    aggregator_service = agg


class RouteRequest(BaseModel):
    from_asset: str
    to_asset: str
    from_network: Optional[str] = None
    to_network: Optional[str] = None
    use_cplex: bool = False
    cost_weight: float = 1.0
    latency_weight: float = 1.0
    reliability_weight: float = 1.0
    alpha: float = 0.4
    beta: float = 0.3
    gamma: float = 0.3


@router.post("/optimize")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def optimize_route(request: Request, route_request: RouteRequest):
    """
    Find optimal route from source to destination.
    
    Args:
        route_request: Route request with from_asset, to_asset, and optional parameters
    """
    if not routing_service or not aggregator_service:
        raise HTTPException(
            status_code=503,
            detail="Routing service not initialized"
        )
    
    try:
        # Get all route segments
        segments = await aggregator_service.get_cached_segments()
        if not segments:
            segments = await aggregator_service.get_segments_from_db(limit=1000)
        
        if not segments:
            raise HTTPException(
                status_code=404,
                detail="No route segments available. Ensure data layer is running."
            )
        
        # Create routing service with custom weights if provided
        if (route_request.cost_weight != 1.0 or route_request.latency_weight != 1.0 or 
            route_request.reliability_weight != 1.0 or route_request.alpha != 0.4 or
            route_request.beta != 0.3 or route_request.gamma != 0.3):
            custom_service = RoutingService(
                use_cplex=route_request.use_cplex,
                cost_weight=route_request.cost_weight,
                latency_weight=route_request.latency_weight,
                reliability_weight=route_request.reliability_weight,
                alpha=route_request.alpha,
                beta=route_request.beta,
                gamma=route_request.gamma
            )
        else:
            custom_service = routing_service
        
        # Find optimal route
        result = custom_service.find_optimal_route(
            segments=segments,
            from_asset=route_request.from_asset,
            to_asset=route_request.to_asset,
            from_network=route_request.from_network,
            to_network=route_request.to_network
        )
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/optimize")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def optimize_route_get(
    request: Request,
    from_asset: str = Query(..., description="Source currency/asset"),
    to_asset: str = Query(..., description="Destination currency/asset"),
    from_network: Optional[str] = Query(None, description="Source network"),
    to_network: Optional[str] = Query(None, description="Destination network"),
    use_cplex: bool = Query(False, description="Use CPLEX solver if available"),
    top_k: int = Query(1, ge=1, le=10, description="Number of top routes to return")
):
    """
    Find optimal route(s) - GET version.
    Returns top K routes if top_k > 1, otherwise returns single optimal route.
    """
    if not routing_service or not aggregator_service:
        raise HTTPException(
            status_code=503,
            detail="Routing service not initialized"
        )
    
    try:
        # Get all route segments
        segments = await aggregator_service.get_cached_segments()
        if not segments:
            segments = await aggregator_service.get_segments_from_db(limit=1000)
        
        if not segments:
            raise HTTPException(
                status_code=404,
                detail="No route segments available. Ensure data layer is running."
            )
        
        if top_k > 1:
            # Return top K routes
            result = routing_service.find_top_routes(
                segments=segments,
                from_asset=from_asset,
                to_asset=to_asset,
                from_network=from_network,
                to_network=to_network,
                top_k=top_k
            )
        else:
            # Return single optimal route
            result = routing_service.find_optimal_route(
                segments=segments,
                from_asset=from_asset,
                to_asset=to_asset,
                from_network=from_network,
                to_network=to_network
            )
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compare")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def compare_routes(
    request: Request,
    from_asset: str = Query(..., description="Source currency/asset"),
    to_asset: str = Query(..., description="Destination currency/asset"),
    from_network: Optional[str] = Query(None, description="Source network"),
    to_network: Optional[str] = Query(None, description="Destination network"),
    top_k: int = Query(3, ge=1, le=10, description="Number of routes to compare")
):
    """
    Compare top K routes side by side.
    """
    if not routing_service or not aggregator_service:
        raise HTTPException(
            status_code=503,
            detail="Routing service not initialized"
        )
    
    try:
        segments = await aggregator_service.get_cached_segments()
        if not segments:
            segments = await aggregator_service.get_segments_from_db(limit=1000)
        
        if not segments:
            raise HTTPException(
                status_code=404,
                detail="No route segments available"
            )
        
        result = routing_service.find_top_routes(
            segments=segments,
            from_asset=from_asset,
            to_asset=to_asset,
            from_network=from_network,
            to_network=to_network,
            top_k=top_k
        )
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

