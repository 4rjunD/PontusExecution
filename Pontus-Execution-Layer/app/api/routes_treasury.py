"""
Treasury Management API Endpoints
"""
from fastapi import APIRouter, Query, HTTPException, Depends, Request
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, timedelta
import uuid

from app.services.aggregator_service import AggregatorService
from app.services.routing_service import RoutingService
from app.middleware.rate_limit import limiter
from app.config import settings

router = APIRouter(prefix="/api/treasury", tags=["treasury"])

# Global service instances
aggregator_service: Optional[AggregatorService] = None
routing_service: Optional[RoutingService] = None


def set_services(agg_service: AggregatorService, route_service: RoutingService):
    """Set the service instances"""
    global aggregator_service, routing_service
    aggregator_service = agg_service
    routing_service = route_service


class BalanceSource(BaseModel):
    """Balance source information"""
    source_type: str  # "bank", "wise", "exchange", "onramp", "offramp", "wallet"
    source_id: str
    asset: str
    amount: float
    network: Optional[str] = None
    location: str
    last_updated: datetime


class UnifiedBalance(BaseModel):
    """Unified balance across all sources"""
    asset: str
    total_amount: float
    sources: List[BalanceSource]
    usd_value: float
    allocation_percentage: float


class TreasuryBalanceResponse(BaseModel):
    """Treasury balance response"""
    total_usd_value: float
    balances: List[UnifiedBalance]
    last_updated: datetime


class RebalancingRule(BaseModel):
    """Rebalancing rule"""
    id: str
    name: str
    source_asset: str
    target_asset: str
    target_percentage: float
    threshold_deviation: float
    status: str  # "active", "paused", "disabled"
    savings_estimate: float


class CashPositionRecommendation(BaseModel):
    """Cash position recommendation"""
    asset: str
    recommended_allocation: float
    current_allocation: float
    optimal_rail: str
    reasoning: str
    estimated_savings: float


class PayoutForecast(BaseModel):
    """Payout forecast"""
    date: datetime
    amount: float
    currency: str
    recipient: str
    status: str  # "scheduled", "pending", "completed"
    optimal_route: Optional[str] = None
    estimated_cost: Optional[float] = None


@router.get("/balances")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_unified_balances(request: Request):
    """
    Get unified balances across all sources (banks, Wise, exchanges, wallets).
    Returns simulated data for demo purposes.
    """
    # Simulated balance data - in production, this would aggregate from real sources
    simulated_balances = [
        {
            "asset": "USD",
            "total_amount": 125000.0,
            "sources": [
                {
                    "source_type": "wise",
                    "source_id": "wise_business_001",
                    "asset": "USD",
                    "amount": 125000.0,
                    "network": "Bank",
                    "location": "Wise Business Account",
                    "last_updated": datetime.utcnow()
                }
            ],
            "usd_value": 125000.0,
            "allocation_percentage": 68.0
        },
        {
            "asset": "EUR",
            "total_amount": 45000.0,
            "sources": [
                {
                    "source_type": "wise",
                    "source_id": "wise_business_001",
                    "asset": "EUR",
                    "amount": 45000.0,
                    "network": "Bank",
                    "location": "Wise Business Account",
                    "last_updated": datetime.utcnow()
                }
            ],
            "usd_value": 41400.0,  # ~0.92 EUR/USD
            "allocation_percentage": 22.5
        },
        {
            "asset": "USDC",
            "total_amount": 25000.0,
            "sources": [
                {
                    "source_type": "wallet",
                    "source_id": "eth_wallet_001",
                    "asset": "USDC",
                    "amount": 25000.0,
                    "network": "Ethereum",
                    "location": "Ethereum Wallet",
                    "last_updated": datetime.utcnow()
                }
            ],
            "usd_value": 25000.0,
            "allocation_percentage": 13.6
        },
        {
            "asset": "USDT",
            "total_amount": 15000.0,
            "sources": [
                {
                    "source_type": "wallet",
                    "source_id": "polygon_wallet_001",
                    "asset": "USDT",
                    "amount": 15000.0,
                    "network": "Polygon",
                    "location": "Polygon Wallet",
                    "last_updated": datetime.utcnow()
                }
            ],
            "usd_value": 15000.0,
            "allocation_percentage": 8.2
        },
        {
            "asset": "INR",
            "total_amount": 8500000.0,
            "sources": [
                {
                    "source_type": "bank",
                    "source_id": "local_bank_001",
                    "asset": "INR",
                    "amount": 8500000.0,
                    "network": "Bank",
                    "location": "Local Bank Account",
                    "last_updated": datetime.utcnow()
                }
            ],
            "usd_value": 102000.0,  # ~83.33 INR/USD
            "allocation_percentage": 55.5
        }
    ]
    
    total_usd = sum(b["usd_value"] for b in simulated_balances)
    
    return TreasuryBalanceResponse(
        total_usd_value=total_usd,
        balances=[UnifiedBalance(**b) for b in simulated_balances],
        last_updated=datetime.utcnow()
    )


@router.get("/fx-rates")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_fx_rates(request: Request):
    """Get real-time FX rates"""
    if not aggregator_service:
        raise HTTPException(status_code=503, detail="Aggregator service not initialized")
    
    try:
        # Get FX segments from aggregator
        segments = await aggregator_service.get_cached_segments(segment_type="fx")
        if not segments:
            segments = await aggregator_service.get_segments_from_db(segment_type="fx", limit=100)
        
        # Extract FX rates
        fx_rates = {}
        for seg in segments:
            pair = f"{seg.from_asset}/{seg.to_asset}"
            fx_rates[pair] = {
                "rate": seg.cost_coefficient,  # Using cost as rate approximation
                "source": seg.provider,
                "last_updated": seg.timestamp.isoformat() if hasattr(seg, 'timestamp') else datetime.utcnow().isoformat()
            }
        
        return {"rates": fx_rates, "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/gas-prices")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_gas_prices(request: Request):
    """Get real-time gas prices for different networks"""
    if not aggregator_service:
        raise HTTPException(status_code=503, detail="Aggregator service not initialized")
    
    try:
        segments = await aggregator_service.get_cached_segments(segment_type="gas")
        if not segments:
            segments = await aggregator_service.get_segments_from_db(segment_type="gas", limit=10)
        
        gas_prices = {}
        for seg in segments:
            network = seg.from_network or "unknown"
            gas_prices[network] = {
                "price_gwei": seg.cost_coefficient,
                "source": seg.provider,
                "last_updated": datetime.utcnow().isoformat()
            }
        
        return {"gas_prices": gas_prices, "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/liquidity")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_liquidity_data(request: Request):
    """Get liquidity data for different assets and networks"""
    if not aggregator_service:
        raise HTTPException(status_code=503, detail="Aggregator service not initialized")
    
    try:
        segments = await aggregator_service.get_cached_segments(segment_type="bridge")
        if not segments:
            segments = await aggregator_service.get_segments_from_db(segment_type="bridge", limit=10)
        
        liquidity = {}
        for seg in segments:
            key = f"{seg.from_asset}_{seg.from_network}_{seg.to_network}"
            liquidity[key] = {
                "asset": seg.from_asset,
                "from_network": seg.from_network,
                "to_network": seg.to_network,
                "available_liquidity": seg.reliability_score * 1000000,  # Estimate
                "source": seg.provider
            }
        
        return {"liquidity": liquidity, "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rebalancing-rules")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_rebalancing_rules(request: Request):
    """Get active rebalancing rules"""
    # Simulated rebalancing rules
    rules = [
        {
            "id": str(uuid.uuid4()),
            "name": "Bank → USDC → L2 → Off-ramp",
            "source_asset": "USD",
            "target_asset": "USDC",
            "target_percentage": 30.0,
            "threshold_deviation": 5.0,
            "status": "active",
            "savings_estimate": 120.0
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Maintain 70% USD / 30% Crypto",
            "source_asset": "USD",
            "target_asset": "USDC",
            "target_percentage": 30.0,
            "threshold_deviation": 5.0,
            "status": "active",
            "savings_estimate": 45.0
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Auto-rebalance when >5% deviation",
            "source_asset": "USD",
            "target_asset": "USDC",
            "target_percentage": 30.0,
            "threshold_deviation": 5.0,
            "status": "active",
            "savings_estimate": 30.0
        }
    ]
    
    return {"rules": [RebalancingRule(**r) for r in rules]}


@router.get("/cash-positioning")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_cash_positioning(request: Request):
    """Get cash positioning recommendations"""
    recommendations = [
        {
            "asset": "USD",
            "recommended_allocation": 70.0,
            "current_allocation": 68.0,
            "optimal_rail": "Wise Business",
            "reasoning": "Optimal for immediate liquidity and low fees",
            "estimated_savings": 45.0
        },
        {
            "asset": "USDC",
            "recommended_allocation": 30.0,
            "current_allocation": 32.0,
            "optimal_rail": "Polygon Network",
            "reasoning": "Lower gas fees and faster settlement for crypto routes",
            "estimated_savings": 30.0
        }
    ]
    
    return {"recommendations": [CashPositionRecommendation(**r) for r in recommendations]}


@router.get("/payout-forecast")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_payout_forecast(request: Request, days: int = Query(30, description="Number of days to forecast")):
    """Get payout forecast for upcoming period"""
    # Simulated payout forecasts
    forecasts = []
    base_date = datetime.utcnow()
    
    for i in range(5):
        forecast_date = base_date + timedelta(days=i*7)
        forecasts.append({
            "date": forecast_date,
            "amount": 10000.0 + (i * 5000),
            "currency": "USD",
            "recipient": f"Vendor {i+1}",
            "status": "scheduled",
            "optimal_route": f"USD → EUR via Wise (Route {i+1})",
            "estimated_cost": 35.0 + (i * 5)
        })
    
    return {"forecasts": [PayoutForecast(**f) for f in forecasts]}


@router.get("/optimal-time")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_optimal_time(
    request: Request,
    from_asset: str = Query(..., description="Source asset"),
    to_asset: str = Query(..., description="Target asset"),
    amount: float = Query(..., description="Amount to convert")
):
    """Get optimal time and route to convert or move funds"""
    if not routing_service:
        raise HTTPException(status_code=503, detail="Routing service not initialized")
    
    try:
        # Get optimal route
        result = await routing_service.find_optimal_route(
            from_asset=from_asset,
            to_asset=to_asset,
            amount=amount,
            alpha=0.4,  # Cost weight
            beta=0.3,   # Speed weight
            gamma=0.3   # Reliability weight
        )
        
        if not result or not result.get("routes"):
            return {
                "optimal_time": "Now",
                "optimal_route": "No route found",
                "estimated_cost": 0.0,
                "estimated_time": "N/A"
            }
        
        best_route = result["routes"][0]
        
        return {
            "optimal_time": "Now",  # Could be enhanced with time-based analysis
            "optimal_route": best_route.get("route_description", "N/A"),
            "estimated_cost": best_route.get("total_cost", 0.0),
            "estimated_time": f"{best_route.get('total_latency', 0):.1f} hours",
            "reliability": best_route.get("reliability_score", 0.0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/corridor-liquidity")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_corridor_liquidity(
    request: Request,
    from_currency: str = Query(..., description="Source currency"),
    to_currency: str = Query(..., description="Target currency")
):
    """Get liquidity data for a specific currency corridor"""
    if not aggregator_service:
        raise HTTPException(status_code=503, detail="Aggregator service not initialized")
    
    try:
        segments = await aggregator_service.get_cached_segments(segment_type="fx")
        if not segments:
            segments = await aggregator_service.get_segments_from_db(segment_type="fx", limit=100)
        
        # Filter by currency pair
        segments = [s for s in segments if s.from_asset.upper() == from_currency.upper() and s.to_asset.upper() == to_currency.upper()]
        
        corridor_data = {
            "corridor": f"{from_currency} → {to_currency}",
            "available_routes": len(segments),
            "best_rate": min([s.cost_coefficient for s in segments]) if segments else 0.0,
            "fastest_route": min([s.latency_coefficient for s in segments]) if segments else 0.0,
            "routes": [
                {
                    "provider": s.provider,
                    "cost": s.cost_coefficient,
                    "speed": s.latency_coefficient,
                    "reliability": s.reliability_score
                }
                for s in segments[:5]  # Top 5 routes
            ]
        }
        
        return corridor_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

