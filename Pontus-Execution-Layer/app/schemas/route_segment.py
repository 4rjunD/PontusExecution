from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from enum import Enum
from datetime import datetime


class SegmentType(str, Enum):
    FX = "fx"
    CRYPTO = "crypto"
    GAS = "gas"
    BRIDGE = "bridge"
    ON_RAMP = "on_ramp"
    OFF_RAMP = "off_ramp"
    BANK_RAIL = "bank_rail"
    LIQUIDITY = "liquidity"


class RouteSegment(BaseModel):
    id: Optional[str] = None
    segment_type: SegmentType
    from_asset: str
    to_asset: str
    from_network: Optional[str] = None
    to_network: Optional[str] = None
    cost: Dict[str, Any] = Field(
        default_factory=lambda: {
            "fee_percent": 0.0,
            "fixed_fee": 0.0,
            "effective_fx_rate": None
        }
    )
    latency: Dict[str, int] = Field(
        default_factory=lambda: {
            "min_minutes": 0,
            "max_minutes": 0
        }
    )
    reliability_score: float = Field(default=1.0, ge=0.0, le=1.0)
    constraints: Dict[str, Any] = Field(default_factory=dict)
    provider: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class RouteSegmentCreate(RouteSegment):
    pass


class RouteSegmentResponse(RouteSegment):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

