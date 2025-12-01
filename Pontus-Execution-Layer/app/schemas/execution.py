"""
Execution Layer Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class ExecutionStatus(str, Enum):
    """Execution status enum"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REROUTING = "rerouting"


class SegmentExecutionStatus(str, Enum):
    """Segment execution status"""
    PENDING = "pending"
    EXECUTING = "executing"
    CONFIRMING = "confirming"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class SegmentExecutionResult(BaseModel):
    """Result of executing a single segment"""
    segment_index: int
    segment_type: str
    from_asset: str
    to_asset: str
    from_network: Optional[str] = None
    to_network: Optional[str] = None
    status: SegmentExecutionStatus
    input_amount: float
    output_amount: float
    fees_paid: float
    transaction_hash: Optional[str] = None
    provider: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    confirmation_time_minutes: Optional[float] = None
    error_message: Optional[str] = None
    simulation_data: Dict[str, Any] = Field(default_factory=dict)


class RouteExecutionRequest(BaseModel):
    """Request to execute a route"""
    from_asset: str
    to_asset: str
    amount: float = Field(gt=0, description="Amount to transfer in from_asset")
    from_network: Optional[str] = None
    to_network: Optional[str] = None
    route_id: Optional[str] = None  # If provided, use pre-computed route
    use_cplex: bool = False
    cost_weight: float = 1.0
    latency_weight: float = 1.0
    reliability_weight: float = 1.0
    alpha: float = 0.4
    beta: float = 0.3
    gamma: float = 0.3


class RouteExecutionResponse(BaseModel):
    """Response from route execution"""
    execution_id: str
    status: ExecutionStatus
    route: List[Dict[str, Any]]
    total_cost_percent: float
    total_fees: float
    input_amount: float
    final_amount: float
    eta_hours: float
    reliability: float
    segment_executions: List[SegmentExecutionResult]
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_time_minutes: Optional[float] = None
    error_message: Optional[str] = None


class ExecutionStatusResponse(BaseModel):
    """Status of an execution"""
    execution_id: str
    status: ExecutionStatus
    current_segment: Optional[int] = None
    total_segments: int
    progress_percent: float
    segment_executions: List[SegmentExecutionResult]
    started_at: datetime
    estimated_completion: Optional[datetime] = None
    can_cancel: bool = False
    can_pause: bool = False
    can_resume: bool = False
    can_reroute: bool = False


class RerouteRequest(BaseModel):
    """Request to reroute an execution"""
    execution_id: str
    from_current_position: bool = True  # Reroute from current position or restart
    new_route: Optional[List[Dict[str, Any]]] = None  # Optional: provide new route directly


class CancelExecutionRequest(BaseModel):
    """Request to cancel an execution"""
    execution_id: str
    cancel_pending_segments: bool = True  # Cancel pending segments
    rollback_completed: bool = False  # Attempt to rollback completed segments


class ModifyTransactionRequest(BaseModel):
    """Request to modify a transaction"""
    execution_id: str
    segment_index: int
    new_amount: Optional[float] = None
    new_route_segment: Optional[Dict[str, Any]] = None

