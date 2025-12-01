"""
Route Execution API Endpoints
"""
from fastapi import APIRouter, Query, HTTPException, Depends, Request
from typing import Optional
from pydantic import BaseModel

from app.services.execution.execution_service import ExecutionService
from app.schemas.execution import (
    RouteExecutionRequest,
    RouteExecutionResponse,
    ExecutionStatusResponse,
    RerouteRequest,
    CancelExecutionRequest,
    ModifyTransactionRequest
)
from app.middleware.rate_limit import limiter
from app.config import settings

router = APIRouter(prefix="/api/routes", tags=["execution"])

# Global execution service instance
execution_service: Optional[ExecutionService] = None


def set_execution_service(service: ExecutionService):
    """Set the execution service instance"""
    global execution_service
    execution_service = service


class ExecuteRouteRequest(BaseModel):
    """Request to execute a route"""
    from_asset: str
    to_asset: str
    amount: float
    from_network: Optional[str] = None
    to_network: Optional[str] = None
    use_cplex: bool = False
    cost_weight: float = 1.0
    latency_weight: float = 1.0
    reliability_weight: float = 1.0
    alpha: float = 0.4
    beta: float = 0.3
    gamma: float = 0.3
    parallel: bool = False  # Enable parallel execution
    enable_ai_rerouting: bool = True  # Enable AI-based dynamic re-routing


@router.post("/execute")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def execute_route(request: Request, execute_request: ExecuteRouteRequest):
    """
    Execute a route from source to destination.
    
    This endpoint:
    1. Finds the optimal route
    2. Executes each segment sequentially (simulated)
    3. Returns execution results with transaction details
    
    **Note:** This is a simulation - no real transactions are executed.
    """
    if not execution_service:
        raise HTTPException(
            status_code=503,
            detail="Execution service not initialized"
        )
    
    try:
        # Input validation
        if not execute_request.from_asset or not execute_request.to_asset:
            raise HTTPException(
                status_code=400,
                detail="from_asset and to_asset are required"
            )
        
        if execute_request.amount <= 0:
            raise HTTPException(
                status_code=400,
                detail="Amount must be greater than 0"
            )
        
        # Convert to RouteExecutionRequest
        route_request = RouteExecutionRequest(
            from_asset=execute_request.from_asset.strip().upper(),
            to_asset=execute_request.to_asset.strip().upper(),
            amount=execute_request.amount,
            from_network=execute_request.from_network.strip().lower() if execute_request.from_network else None,
            to_network=execute_request.to_network.strip().lower() if execute_request.to_network else None,
            use_cplex=execute_request.use_cplex,
            cost_weight=max(0.0, execute_request.cost_weight),
            latency_weight=max(0.0, execute_request.latency_weight),
            reliability_weight=max(0.0, execute_request.reliability_weight),
            alpha=max(0.0, min(1.0, execute_request.alpha)),
            beta=max(0.0, min(1.0, execute_request.beta)),
            gamma=max(0.0, min(1.0, execute_request.gamma))
        )
        
        # Execute route with advanced features
        result = await execution_service.execute_route(
            route_request,
            parallel=execute_request.parallel,
            enable_ai_rerouting=execute_request.enable_ai_rerouting
        )
        
        return result
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Execution error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during execution")


@router.get("/execute")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def execute_route_get(
    request: Request,
    from_asset: str = Query(..., description="Source currency/asset"),
    to_asset: str = Query(..., description="Destination currency/asset"),
    amount: float = Query(..., gt=0, description="Amount to transfer"),
    from_network: Optional[str] = Query(None, description="Source network"),
    to_network: Optional[str] = Query(None, description="Destination network"),
    use_cplex: bool = Query(False, description="Use CPLEX solver if available")
):
    """
    Execute a route - GET version.
    
    **Note:** This is a simulation - no real transactions are executed.
    """
    if not execution_service:
        raise HTTPException(
            status_code=503,
            detail="Execution service not initialized"
        )
    
    try:
        route_request = RouteExecutionRequest(
            from_asset=from_asset,
            to_asset=to_asset,
            amount=amount,
            from_network=from_network,
            to_network=to_network,
            use_cplex=use_cplex
        )
        
        result = await execution_service.execute_route(route_request)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/execute/{execution_id}/status")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_execution_status(
    request: Request,
    execution_id: str
):
    """
    Get status of an execution.
    
    Returns current status, progress, and segment execution details.
    """
    if not execution_service:
        raise HTTPException(
            status_code=503,
            detail="Execution service not initialized"
        )
    
    try:
        status = execution_service.get_execution_status(execution_id)
        
        if not status:
            raise HTTPException(
                status_code=404,
                detail=f"Execution {execution_id} not found"
            )
        
        # Calculate progress
        total_segments = status.get("total_segments", 0)
        current_segment = status.get("current_segment", 0)
        progress = (current_segment / total_segments * 100) if total_segments > 0 else 0
        
        return {
            "execution_id": execution_id,
            "status": status.get("status", "unknown").value if hasattr(status.get("status"), "value") else status.get("status"),
            "current_segment": current_segment,
            "total_segments": total_segments,
            "progress_percent": round(progress, 2),
            "segment_executions": [
                seg.dict() if hasattr(seg, "dict") else seg
                for seg in status.get("segment_executions", [])
            ],
            "started_at": status.get("started_at")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/wallet/{wallet_address}/balance")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_wallet_balance(
    request: Request,
    wallet_address: str,
    asset: str = Query(..., description="Asset to check balance for")
):
    """
    Get simulated wallet balance.
    
    **Note:** This is a simulation - returns simulated balances only.
    """
    if not execution_service:
        raise HTTPException(
            status_code=503,
            detail="Execution service not initialized"
        )
    
    try:
        balance = execution_service.get_wallet_balance(wallet_address, asset)
        
        return {
            "wallet_address": wallet_address,
            "asset": asset,
            "balance": balance
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transaction/{tx_hash}/status")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_transaction_status(
    request: Request,
    tx_hash: str
):
    """
    Get status of a simulated transaction.
    
    **Note:** This is a simulation - returns simulated transaction data only.
    """
    if not execution_service:
        raise HTTPException(
            status_code=503,
            detail="Execution service not initialized"
        )
    
    try:
        tx_status = execution_service.get_transaction_status(tx_hash)
        
        if not tx_status:
            raise HTTPException(
                status_code=404,
                detail=f"Transaction {tx_hash} not found"
            )
        
        return tx_status
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute/{execution_id}/pause")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def pause_execution(
    request: Request,
    execution_id: str
):
    """Pause an in-progress execution"""
    if not execution_service:
        raise HTTPException(status_code=503, detail="Execution service not initialized")
    
    try:
        result = await execution_service.pause_execution(execution_id)
        if result:
            return {"status": "paused", "execution_id": execution_id}
        else:
            raise HTTPException(status_code=404, detail="Execution not found or cannot be paused")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute/{execution_id}/resume")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def resume_execution(
    request: Request,
    execution_id: str
):
    """Resume a paused execution"""
    if not execution_service:
        raise HTTPException(status_code=503, detail="Execution service not initialized")
    
    try:
        result = await execution_service.resume_execution(execution_id)
        if result:
            return {"status": "resumed", "execution_id": execution_id}
        else:
            raise HTTPException(status_code=404, detail="Execution not found or cannot be resumed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute/{execution_id}/cancel")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def cancel_execution(
    request: Request,
    execution_id: str,
    cancel_pending: bool = True,
    rollback: bool = False
):
    """Cancel an execution"""
    if not execution_service:
        raise HTTPException(status_code=503, detail="Execution service not initialized")
    
    try:
        result = await execution_service.cancel_execution(execution_id, cancel_pending, rollback)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute/{execution_id}/reroute")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def reroute_execution(
    request: Request,
    execution_id: str,
    reroute_request: RerouteRequest
):
    """Dynamically re-route an execution"""
    if not execution_service:
        raise HTTPException(status_code=503, detail="Execution service not initialized")
    
    try:
        result = await execution_service.reroute_execution(
            execution_id,
            reroute_request.from_current_position,
            reroute_request.new_route
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute/{execution_id}/modify")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def modify_transaction(
    request: Request,
    execution_id: str,
    modify_request: ModifyTransactionRequest
):
    """Modify a transaction in an execution"""
    if not execution_service:
        raise HTTPException(status_code=503, detail="Execution service not initialized")
    
    try:
        result = await execution_service.modify_transaction(
            execution_id,
            modify_request.segment_index,
            modify_request.new_amount
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

