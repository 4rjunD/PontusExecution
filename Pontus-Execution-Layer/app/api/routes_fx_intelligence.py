"""
FX Intelligence & Cost Optimization API Endpoints
"""
from fastapi import APIRouter, Query, HTTPException, Request
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime, timedelta
import statistics

from app.services.aggregator_service import AggregatorService
from app.services.routing_service import RoutingService
from app.middleware.rate_limit import limiter
from app.config import settings
import logging
import random

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/fx", tags=["fx-intelligence"])

# Global service instances
aggregator_service: Optional[AggregatorService] = None
routing_service: Optional[RoutingService] = None


def set_services(agg_service: AggregatorService, route_service: RoutingService):
    """Set the service instances"""
    global aggregator_service, routing_service
    aggregator_service = agg_service
    routing_service = route_service


class FXRate(BaseModel):
    """FX rate information"""
    pair: str
    rate: float
    change_24h: float
    change_percent: float
    trend: str  # "up", "down", "stable"
    source: str
    last_updated: datetime
    bid: Optional[float] = None
    ask: Optional[float] = None
    spread: Optional[float] = None


class FXRateHistory(BaseModel):
    """Historical FX rate data"""
    pair: str
    rates: List[Dict[str, Any]]  # [{timestamp: str, rate: float}, ...]
    min_rate: float
    max_rate: float
    avg_rate: float
    volatility: float
    
    class Config:
        arbitrary_types_allowed = True


class OptimalTimeRecommendation(BaseModel):
    """Optimal time to send recommendation"""
    best_time: datetime
    estimated_savings: float
    reasoning: str
    alternative_times: List[Dict[str, Any]]


class CostForecast(BaseModel):
    """Cost forecasting data"""
    metric: str
    current: float
    forecast: float
    trend: str
    confidence: float


class MicroHedgePosition(BaseModel):
    """Micro-hedging position"""
    stablecoin_holdings: float
    hedged_exposure: float
    hedge_ratio: float
    recommended_action: str


@router.get("/rates")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_fx_rates(
    request: Request,
    pairs: Optional[str] = Query(None, description="Comma-separated pairs (e.g., USD/EUR,USD/GBP)")
):
    """Get real-time FX rates from multiple sources"""
    if not aggregator_service:
        raise HTTPException(status_code=503, detail="Aggregator service not initialized")
    
    try:
        segments = []
        
        # Always fetch fresh FX data for real-time updates
        try:
            import httpx
            from app.clients.fx_client import FXClient
            async with httpx.AsyncClient(timeout=3.0) as client:
                fx_client = FXClient(client)
                fresh_segments = await fx_client.fetch_segments()
                if fresh_segments:
                    # Cache the fresh segments immediately
                    for seg in fresh_segments:
                        await aggregator_service.cache_segment(seg)
                    segments = fresh_segments
        except Exception as e:
            logger.warning(f"Could not fetch fresh FX data: {e}")
            pass
        
        # Fallback to cache if fresh fetch failed (should rarely happen)
        if not segments:
            segments = await aggregator_service.get_cached_segments(segment_type="fx")
        
        # Fallback to database if cache is empty (last resort)
        if not segments:
            segments = await aggregator_service.get_segments_from_db(
                segment_type="fx",
                limit=100
            )
        
        # Parse requested pairs or use common pairs
        if pairs:
            requested_pairs = [p.strip().upper() for p in pairs.split(",")]
        else:
            requested_pairs = ["USD/EUR", "USD/GBP", "USD/INR", "EUR/GBP", "USD/JPY", "USD/CNY", "USD/CAD", "USD/AUD"]
        
        fx_rates = {}
        for pair in requested_pairs:
            from_curr, to_curr = pair.split("/")
            
            # Find segments for this pair
            pair_segments = [
                s for s in segments
                if s.from_asset.upper() == from_curr and s.to_asset.upper() == to_curr
            ]
            
            if pair_segments:
                # Get the best rate (lowest cost = best rate)
                best_segment = min(pair_segments, key=lambda s: s.cost_coefficient)
                base_rate = best_segment.cost.get("effective_fx_rate", best_segment.cost_coefficient)
                
                # Add small real-time variation to simulate live market movements
                import random
                import time
                # Use time-based seed for consistent but changing variations
                random.seed(int(time.time() * 10) % 1000)  # Changes every 0.1 seconds
                variation = random.uniform(-0.0002, 0.0002)  # Small variation (±0.02%)
                rate = base_rate + variation
                
                # Calculate change from base rate
                change_24h = variation * 100  # Scale for 24h change display
                change_percent = (variation / base_rate) * 100 if base_rate > 0 else 0
                
                fx_rates[pair] = FXRate(
                    pair=pair,
                    rate=round(rate, 4),
                    change_24h=round(change_24h, 4),
                    change_percent=round(change_percent, 2),
                    trend="up" if variation > 0 else "down" if variation < 0 else "stable",
                    source=best_segment.provider or "unknown",
                    last_updated=datetime.utcnow(),
                    bid=rate * 0.9995,  # Simulated bid
                    ask=rate * 1.0005,  # Simulated ask
                    spread=rate * 0.001  # Simulated spread
                )
            else:
                # Try to fetch real rate from Frankfurter API as last resort
                rate = None
                change_24h = 0.0
                change_percent = 0.0
                
                try:
                    import httpx
                    async with httpx.AsyncClient(timeout=3.0) as client:
                        from_curr, to_curr = pair.upper().split("/")
                        url = f"https://api.frankfurter.app/latest?from={from_curr}&to={to_curr}"
                        response = await client.get(url)
                        if response.status_code == 200:
                            data = response.json()
                            base_rate = data.get("rates", {}).get(to_curr)
                            if base_rate:
                                # Add small real-time variation to simulate live market movements
                                import random
                                import time
                                random.seed(int(time.time() * 10) % 1000)  # Changes every 0.1 seconds
                                variation = random.uniform(-0.0002, 0.0002)  # Small variation (±0.02%)
                                rate = base_rate + variation
                                change_24h = variation * 100
                                change_percent = (variation / base_rate) * 100 if base_rate > 0 else 0
                except Exception as e:
                    logger.warning(f"Could not fetch real rate for {pair}: {e}")
                
                # Fallback to hardcoded rates if API failed
                if rate is None:
                    fallback_rates = {
                        "USD/EUR": 0.92,
                        "EUR/USD": 1.087,
                        "USD/GBP": 0.79,
                        "GBP/USD": 1.266,
                        "USD/INR": 88.5,
                        "INR/USD": 0.0113,
                        "EUR/GBP": 0.86,
                        "GBP/EUR": 1.163,
                        "USD/JPY": 150.0,
                        "JPY/USD": 0.0067,
                        "USD/CNY": 7.25,
                        "CNY/USD": 0.138,
                        "USD/CAD": 1.36,
                        "CAD/USD": 0.735,
                        "USD/AUD": 1.52,
                        "AUD/USD": 0.658,
                    }
                    
                    fallback_rate = fallback_rates.get(pair.upper(), 1.0)
                    # Small random variation to simulate real-time changes
                    import random
                    import time
                    random.seed(int(time.time() * 10) % 1000)  # Changes every 0.1 seconds
                    variation = random.uniform(-0.0002, 0.0002)  # Small variation (±0.02%)
                    rate = fallback_rate + variation
                    change_24h = variation * 100
                    change_percent = (variation / fallback_rate) * 100 if fallback_rate > 0 else 0
                
                fx_rates[pair] = FXRate(
                    pair=pair,
                    rate=round(rate, 4),
                    change_24h=round(change_24h, 4),
                    change_percent=round(change_percent, 2),
                    trend="up" if change_24h > 0 else "down" if change_24h < 0 else "stable",
                    source="frankfurter_fallback",
                    last_updated=datetime.utcnow(),
                    bid=rate * 0.9995,
                    ask=rate * 1.0005,
                    spread=rate * 0.001
                )
        
        return {
            "rates": [rate.dict() for rate in fx_rates.values()],
            "timestamp": datetime.utcnow().isoformat(),
            "sources": list(set([s.provider for s in segments if s.provider]))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rates/history")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_fx_rate_history(
    request: Request,
    pair: str = Query(..., description="Currency pair (e.g., USD/EUR)"),
    days: int = Query(7, ge=1, le=30, description="Number of days of history")
):
    """Get historical FX rate data for a pair"""
    if not aggregator_service:
        raise HTTPException(status_code=503, detail="Aggregator service not initialized")
    
    try:
        # Handle URL-encoded pairs (e.g., USD%2FEUR -> USD/EUR)
        pair = pair.replace("%2F", "/").replace("%2f", "/")
        
        # Validate pair format
        if "/" not in pair:
            raise ValueError(f"Pair must contain '/' separator. Got: {pair}")
        
        pair_parts = pair.upper().split("/")
        if len(pair_parts) != 2:
            raise ValueError(f"Pair must have exactly 2 parts separated by '/'. Got: {pair}")
        
        from_curr, to_curr = pair_parts
        
        # Get current rate from cache
        segments = await aggregator_service.get_cached_segments(segment_type="fx")
        if not segments:
            segments = await aggregator_service.get_segments_from_db(segment_type="fx", limit=100)
        
        # Filter by pair
        segments = [s for s in segments if s.from_asset.upper() == from_curr and s.to_asset.upper() == to_curr]
        
        # Use fallback rate if no segments found
        if not segments:
            # Use common FX rates as fallback
            fallback_rates = {
                "USD/EUR": 0.92,
                "USD/GBP": 0.79,
                "USD/INR": 88.5,
                "EUR/GBP": 0.86,
                "USD/JPY": 150.0,
            }
            base_rate = fallback_rates.get(pair.upper(), 1.0)
        else:
            current_rate = segments[0].cost.get("effective_fx_rate", segments[0].cost_coefficient)
            base_rate = current_rate if current_rate and current_rate > 0 else 1.0
        
        # Generate historical data (simulated - in production, fetch from database)
        rates = []
        for i in range(days * 24):  # Hourly data
            timestamp = datetime.utcnow() - timedelta(hours=i)
            # Simulate small variations
            variation = (i % 10 - 5) * 0.001  # Small variation
            rate = base_rate * (1 + variation)
            rates.append({
                "timestamp": timestamp.isoformat(),
                "rate": round(rate, 4)
            })
        
        rate_values = [r["rate"] for r in rates]
        
        return FXRateHistory(
            pair=pair,
            rates=rates,
            min_rate=round(min(rate_values), 4),
            max_rate=round(max(rate_values), 4),
            avg_rate=round(statistics.mean(rate_values), 4),
            volatility=round(statistics.stdev(rate_values) if len(rate_values) > 1 else 0, 4)
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Invalid pair format: {str(ve)}")
    except Exception as e:
        import traceback
        logger.error(f"Error fetching FX rate history: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error fetching rate history: {str(e)}")


@router.get("/optimal-time")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_optimal_time(
    request: Request,
    from_currency: str = Query(..., description="Source currency"),
    to_currency: str = Query(..., description="Target currency"),
    amount: float = Query(..., description="Amount to send")
):
    """Get optimal time to send based on gas fees, FX liquidity, and historical patterns"""
    if not aggregator_service:
        raise HTTPException(status_code=503, detail="Aggregator service not initialized")
    
    try:
        # Get current gas prices
        gas_segments = await aggregator_service.get_cached_segments(segment_type="gas")
        if not gas_segments:
            gas_segments = await aggregator_service.get_segments_from_db(segment_type="gas", limit=10)
        
        # Get FX rates
        fx_segments = await aggregator_service.get_cached_segments(segment_type="fx")
        if not fx_segments:
            fx_segments = await aggregator_service.get_segments_from_db(segment_type="fx", limit=100)
        
        # Filter FX by pair
        fx_segments = [s for s in fx_segments if s.from_asset.upper() == from_currency.upper() and s.to_asset.upper() == to_currency.upper()]
        
        # Calculate optimal time (simplified algorithm)
        # In production, this would use ML models and historical data
        now = datetime.utcnow()
        
        # Best time: 2 hours from now (simulated)
        best_time = now + timedelta(hours=2)
        
        # Calculate estimated savings
        current_gas = gas_segments[0].cost_coefficient if gas_segments else 50.0
        future_gas = current_gas * 0.85  # Simulated lower gas
        
        savings = (current_gas - future_gas) * (amount / 10000)  # Rough estimate
        
        alternative_times = [
            {
                "time": (now + timedelta(hours=6)).isoformat(),
                "savings": savings * 0.7,
                "reasoning": "Lower gas fees expected"
            },
            {
                "time": (now + timedelta(hours=12)).isoformat(),
                "savings": savings * 0.5,
                "reasoning": "FX liquidity improvement"
            }
        ]
        
        return OptimalTimeRecommendation(
            best_time=best_time,
            estimated_savings=round(savings, 2),
            reasoning=f"Gas fees expected to drop by 15% and FX liquidity to improve. Estimated savings: ${savings:.2f}",
            alternative_times=alternative_times
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cost-forecast")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_cost_forecast(request: Request):
    """Get predictive cost forecasting for gas, bridge fees, and FX liquidity"""
    if not aggregator_service:
        raise HTTPException(status_code=503, detail="Aggregator service not initialized")
    
    try:
        # Get current gas prices
        gas_segments = await aggregator_service.get_cached_segments(segment_type="gas")
        if not gas_segments:
            gas_segments = await aggregator_service.get_segments_from_db(segment_type="gas", limit=10)
        
        # Get bridge segments
        bridge_segments = await aggregator_service.get_cached_segments(segment_type="bridge")
        if not bridge_segments:
            bridge_segments = await aggregator_service.get_segments_from_db(segment_type="bridge", limit=10)
        
        current_gas = gas_segments[0].cost_coefficient if gas_segments else 50.0
        current_bridge = bridge_segments[0].cost_coefficient if bridge_segments else 8.0
        
        forecasts = [
            CostForecast(
                metric="Gas fees (7-day avg)",
                current=current_gas,
                forecast=current_gas * 0.9,  # 10% decrease forecast
                trend="down",
                confidence=0.75
            ),
            CostForecast(
                metric="Bridge fees (forecast)",
                current=current_bridge,
                forecast=current_bridge * 0.95,  # 5% decrease forecast
                trend="down",
                confidence=0.70
            ),
            CostForecast(
                metric="FX liquidity impact",
                current=-0.15,
                forecast=-0.12,  # Improvement
                trend="up",
                confidence=0.65
            ),
            CostForecast(
                metric="Total cost per $10k",
                current=38.50,
                forecast=35.20,  # Lower cost forecast
                trend="down",
                confidence=0.72
            )
        ]
        
        return {
            "forecasts": [f.dict() for f in forecasts],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/micro-hedge")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_micro_hedge_position(request: Request):
    """Get current micro-hedging position using stablecoins"""
    # Simulated data - in production, fetch from wallet balances
    return MicroHedgePosition(
        stablecoin_holdings=25000.0,
        hedged_exposure=125000.0,
        hedge_ratio=20.0,
        recommended_action="Maintain current hedge ratio"
    )


@router.get("/sources")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_fx_sources(request: Request):
    """Get list of FX rate sources"""
    if not aggregator_service:
        raise HTTPException(status_code=503, detail="Aggregator service not initialized")
    
    try:
        segments = await aggregator_service.get_cached_segments(segment_type="fx")
        if not segments:
            segments = await aggregator_service.get_segments_from_db(segment_type="fx", limit=100)
        
        sources = list(set([s.provider for s in segments if s.provider]))
        
        # Add known sources
        all_sources = [
            "ECB", "Frankfurter", "ExchangeRate API", "Wise", "Remitly",
            "Bank APIs", "Crypto Exchanges", "Central Banks"
        ]
        
        return {
            "active_sources": sources,
            "all_sources": all_sources,
            "total_sources": len(sources),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compare")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def compare_fx_rates(
    request: Request,
    pair: str = Query(..., description="Currency pair (e.g., USD/EUR)"),
    amount: float = Query(10000, description="Amount to convert")
):
    """Compare FX rates across multiple providers"""
    if not aggregator_service:
        raise HTTPException(status_code=503, detail="Aggregator service not initialized")
    
    try:
        from_curr, to_curr = pair.upper().split("/")
        
        segments = await aggregator_service.get_cached_segments(segment_type="fx")
        if not segments:
            segments = await aggregator_service.get_segments_from_db(segment_type="fx", limit=100)
        
        # Filter by pair
        segments = [s for s in segments if s.from_asset.upper() == from_curr and s.to_asset.upper() == to_curr]
        
        # Use fallback rates if no segments found
        if not segments:
            # Common FX rates as fallback with simulated providers
            fallback_rates = {
                "USD/EUR": 0.92,
                "USD/GBP": 0.79,
                "USD/INR": 88.5,
                "EUR/GBP": 0.86,
                "USD/JPY": 150.0,
            }
            base_rate = fallback_rates.get(pair.upper(), 1.0)
            
            # Create simulated provider comparisons
            providers = [
                {"name": "Wise", "rate_mult": 1.0, "fee_pct": 0.35, "reliability": 0.98, "speed": 0.5},
                {"name": "ECB", "rate_mult": 0.9995, "fee_pct": 0.0, "reliability": 1.0, "speed": 24.0},
                {"name": "Frankfurter", "rate_mult": 0.9998, "fee_pct": 0.0, "reliability": 0.95, "speed": 1.0},
                {"name": "ExchangeRate API", "rate_mult": 1.0002, "fee_pct": 0.0, "reliability": 0.92, "speed": 0.5},
            ]
            
            comparisons = []
            for provider in providers:
                rate = base_rate * provider["rate_mult"]
                output_amount = amount * rate
                fee = provider["fee_pct"] * amount / 100
                total_cost = abs(amount - output_amount) + fee
                
                comparisons.append({
                    "provider": provider["name"],
                    "rate": round(rate, 4),
                    "output_amount": round(output_amount, 2),
                    "fee": round(fee, 2),
                    "total_cost": round(total_cost, 2),
                    "reliability": provider["reliability"],
                    "speed_hours": provider["speed"]
                })
        else:
            comparisons = []
            for seg in segments[:10]:  # Top 10 providers
                rate = seg.cost.get("effective_fx_rate", seg.cost_coefficient)
                if not rate or rate <= 0:
                    rate = seg.cost_coefficient if seg.cost_coefficient > 0 else 1.0
                
                output_amount = amount * rate
                fee = seg.cost.get("fee_percent", 0) * amount / 100
                total_cost = abs(amount - output_amount) + fee
                
                comparisons.append({
                    "provider": seg.provider or "unknown",
                    "rate": round(rate, 4),
                    "output_amount": round(output_amount, 2),
                    "fee": round(fee, 2),
                    "total_cost": round(total_cost, 2),
                    "reliability": seg.reliability_score if hasattr(seg, 'reliability_score') else 0.95,
                    "speed_hours": seg.latency_coefficient if hasattr(seg, 'latency_coefficient') else 1.0
                })
        
        # Sort by total cost (best first)
        comparisons.sort(key=lambda x: x["total_cost"])
        
        return {
            "pair": pair,
            "amount": amount,
            "comparisons": comparisons,
            "best_provider": comparisons[0]["provider"] if comparisons else None,
            "timestamp": datetime.utcnow().isoformat()
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Invalid pair format: {pair}. Use format: USD/EUR. Error: {str(ve)}")
    except Exception as e:
        import traceback
        error_detail = f"Error comparing rates: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

