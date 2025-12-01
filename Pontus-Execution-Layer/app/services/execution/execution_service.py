"""
Execution Service - Orchestrates route execution
Coordinates segment executors and manages execution flow
"""
import uuid
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.schemas.route_segment import RouteSegment, SegmentType
from app.schemas.execution import (
    RouteExecutionRequest,
    RouteExecutionResponse,
    ExecutionStatus,
    SegmentExecutionResult,
    SegmentExecutionStatus
)
from app.services.execution.simulator import Simulator
from app.services.execution.segment_executors import (
    FXExecutor,
    CryptoExecutor,
    BridgeExecutor,
    RampExecutor,
    BankRailExecutor
)
from app.services.execution.advanced_execution_service import AdvancedExecutionService
from app.services.routing_service import RoutingService
from app.services.aggregator_service import AggregatorService
from app.clients import WiseClient, KrakenClient
from app.config import settings
import httpx

logger = logging.getLogger(__name__)


class ExecutionService:
    """Main execution service that orchestrates route execution"""
    
    def __init__(self, routing_service: RoutingService, aggregator_service: AggregatorService):
        self.routing_service = routing_service
        self.aggregator_service = aggregator_service
        self.simulator = Simulator()
        self.execution_mode = settings.execution_mode
        
        # Initialize API clients for real execution
        self.http_client = httpx.AsyncClient(timeout=30.0)
        self.wise_client = WiseClient(self.http_client) if settings.wise_api_key else None
        self.kraken_client = KrakenClient(self.http_client) if settings.kraken_api_key else None
        
        # Initialize executors with API clients
        self.executors = {
            SegmentType.FX: FXExecutor(self.simulator, wise_client=self.wise_client),
            SegmentType.CRYPTO: CryptoExecutor(self.simulator, kraken_client=self.kraken_client),
            SegmentType.BRIDGE: BridgeExecutor(self.simulator),
            SegmentType.ON_RAMP: RampExecutor(self.simulator),
            SegmentType.OFF_RAMP: RampExecutor(self.simulator),
            SegmentType.BANK_RAIL: BankRailExecutor(self.simulator, wise_client=self.wise_client),
        }
        
        # Initialize advanced execution service for new features
        self.advanced_service = AdvancedExecutionService(routing_service, aggregator_service)
        
        # Store active executions (in-memory for MVP)
        self.active_executions: Dict[str, Dict[str, Any]] = {}
        self.max_execution_history = 1000  # Limit memory usage
    
    async def execute_route(
        self,
        request: RouteExecutionRequest,
        parallel: bool = False,
        enable_ai_rerouting: bool = True
    ) -> RouteExecutionResponse:
        """
        Execute a complete route from source to destination
        
        Steps:
        1. Get optimal route (or use provided route_id)
        2. Execute each segment sequentially
        3. Track execution status
        4. Return execution results
        """
        execution_id = str(uuid.uuid4())
        started_at = datetime.utcnow()
        
        # Input validation
        if not request.from_asset or not request.to_asset:
            raise ValueError("from_asset and to_asset are required")
        
        if request.amount <= 0:
            raise ValueError("Amount must be greater than 0")
        
        if request.amount > 1e15:  # Sanity check for extremely large amounts
            raise ValueError("Amount exceeds maximum limit")
        
        # Use advanced service for new features
        return await self.advanced_service.execute_route(request, parallel=parallel, enable_ai_rerouting=enable_ai_rerouting)
    
    async def execute_route_legacy(
        self,
        request: RouteExecutionRequest
    ) -> RouteExecutionResponse:
        """Legacy execution method (for backward compatibility)"""
        execution_id = str(uuid.uuid4())
        started_at = datetime.utcnow()
        
        # Input validation
        if not request.from_asset or not request.to_asset:
            raise ValueError("from_asset and to_asset are required")
        
        if request.amount <= 0:
            raise ValueError("Amount must be greater than 0")
        
        if request.amount > 1e15:  # Sanity check for extremely large amounts
            raise ValueError("Amount exceeds maximum limit")
        
        try:
            # Step 1: Get route
            logger.info(f"Execution {execution_id}: Getting optimal route...")
            
            # Get route segments
            segments = await self.aggregator_service.get_cached_segments()
            if not segments:
                segments = await self.aggregator_service.get_segments_from_db(limit=1000)
            
            if not segments:
                raise ValueError("No route segments available")
            
            # Get optimal route
            route_result = self.routing_service.find_optimal_route(
                segments=segments,
                from_asset=request.from_asset,
                to_asset=request.to_asset,
                from_network=request.from_network,
                to_network=request.to_network
            )
            
            if "error" in route_result:
                raise ValueError(route_result["error"])
            
            route_segments = route_result["route"]
            if not route_segments:
                raise ValueError("No route found")
            
            logger.info(f"Execution {execution_id}: Route found with {len(route_segments)} segments")
            
            # Step 2: Execute segments sequentially
            segment_executions: List[SegmentExecutionResult] = []
            current_amount = request.amount
            wallet_address: Optional[str] = None
            
            # Store execution state
            self.active_executions[execution_id] = {
                "status": ExecutionStatus.IN_PROGRESS,
                "started_at": started_at,
                "current_segment": 0,
                "total_segments": len(route_segments),
                "segment_executions": []
            }
            
            # Cleanup old executions if too many
            if len(self.active_executions) > self.max_execution_history:
                # Remove oldest completed/failed executions
                sorted_executions = sorted(
                    self.active_executions.items(),
                    key=lambda x: x[1].get("started_at", datetime.utcnow())
                )
                for old_id, _ in sorted_executions[:len(self.active_executions) - self.max_execution_history + 100]:
                    if self.active_executions[old_id].get("status") in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED]:
                        del self.active_executions[old_id]
            
            for idx, segment_dict in enumerate(route_segments):
                logger.info(f"Execution {execution_id}: Executing segment {idx + 1}/{len(route_segments)}")
                
                # Update active execution
                self.active_executions[execution_id]["current_segment"] = idx
                
                # Convert dict to RouteSegment with validation
                try:
                    segment_type_str = segment_dict.get("segment_type")
                    if not segment_type_str:
                        raise ValueError(f"Segment {idx} missing segment_type")
                    
                    segment = RouteSegment(
                        segment_type=SegmentType(segment_type_str),
                        from_asset=segment_dict.get("from_asset", ""),
                        to_asset=segment_dict.get("to_asset", ""),
                        from_network=segment_dict.get("from_network"),
                        to_network=segment_dict.get("to_network"),
                        cost=segment_dict.get("cost", {}),
                        latency=segment_dict.get("latency", {}),
                        reliability_score=segment_dict.get("reliability_score", 1.0),
                        provider=segment_dict.get("provider")
                    )
                    
                    # Validate segment has required fields
                    if not segment.from_asset or not segment.to_asset:
                        raise ValueError(f"Segment {idx} missing from_asset or to_asset")
                        
                except (KeyError, ValueError, TypeError) as e:
                    logger.error(f"Execution {execution_id}: Invalid segment {idx}: {e}")
                    segment_result = SegmentExecutionResult(
                        segment_index=idx,
                        segment_type=segment_dict.get("segment_type", "unknown"),
                        from_asset=segment_dict.get("from_asset", ""),
                        to_asset=segment_dict.get("to_asset", ""),
                        status=SegmentExecutionStatus.FAILED,
                        input_amount=current_amount,
                        output_amount=0.0,
                        fees_paid=0.0,
                        error_message=f"Invalid segment data: {str(e)}"
                    )
                    segment_executions.append(segment_result)
                    self.active_executions[execution_id]["status"] = ExecutionStatus.FAILED
                    break
                
                # Get executor for segment type
                executor = self.executors.get(segment.segment_type)
                if not executor:
                    logger.warning(f"No executor for segment type: {segment.segment_type}")
                    segment_result = SegmentExecutionResult(
                        segment_index=idx,
                        segment_type=segment.segment_type.value,
                        from_asset=segment.from_asset,
                        to_asset=segment.to_asset,
                        status=SegmentExecutionStatus.SKIPPED,
                        input_amount=current_amount,
                        output_amount=current_amount,
                        fees_paid=0.0,
                        error_message=f"No executor for segment type: {segment.segment_type}"
                    )
                else:
                    # Execute segment
                    segment_result = await executor.execute(
                        segment=segment,
                        input_amount=current_amount,
                        wallet_address=wallet_address,
                        metadata={"segment_index": idx, "execution_id": execution_id}
                    )
                    
                    # Update wallet address if generated
                    if segment_result.simulation_data.get("wallet_address"):
                        wallet_address = segment_result.simulation_data["wallet_address"]
                
                segment_executions.append(segment_result)
                self.active_executions[execution_id]["segment_executions"] = segment_executions
                
                # Check if segment failed
                if segment_result.status == SegmentExecutionStatus.FAILED:
                    logger.error(f"Execution {execution_id}: Segment {idx + 1} failed: {segment_result.error_message}")
                    self.active_executions[execution_id]["status"] = ExecutionStatus.FAILED
                    break
                
                # Update current amount for next segment
                current_amount = segment_result.output_amount
                logger.info(f"Execution {execution_id}: Segment {idx + 1} completed. "
                           f"Amount: {segment_result.input_amount} -> {segment_result.output_amount}")
            
            # Step 3: Calculate totals
            total_fees = sum(seg.fees_paid for seg in segment_executions)
            total_time_minutes = sum(
                seg.confirmation_time_minutes or 0 
                for seg in segment_executions 
                if seg.confirmation_time_minutes
            )
            completed_at = datetime.utcnow()
            
            # Determine final status
            if any(seg.status == SegmentExecutionStatus.FAILED for seg in segment_executions):
                final_status = ExecutionStatus.FAILED
            else:
                final_status = ExecutionStatus.COMPLETED
                self.active_executions[execution_id]["status"] = ExecutionStatus.COMPLETED
            
            logger.info(f"Execution {execution_id}: Completed with status {final_status}. "
                       f"Final amount: {current_amount}")
            
            return RouteExecutionResponse(
                execution_id=execution_id,
                status=final_status,
                route=route_segments,
                total_cost_percent=route_result.get("cost_percent", 0.0),
                total_fees=total_fees,
                input_amount=request.amount,
                final_amount=current_amount,
                eta_hours=route_result.get("eta_hours", 0.0),
                reliability=route_result.get("reliability", 0.0),
                segment_executions=segment_executions,
                started_at=started_at,
                completed_at=completed_at,
                total_time_minutes=total_time_minutes
            )
            
        except Exception as e:
            logger.error(f"Execution {execution_id} failed: {e}")
            self.active_executions[execution_id]["status"] = ExecutionStatus.FAILED
            
            return RouteExecutionResponse(
                execution_id=execution_id,
                status=ExecutionStatus.FAILED,
                route=[],
                total_cost_percent=0.0,
                total_fees=0.0,
                input_amount=request.amount,
                final_amount=0.0,
                eta_hours=0.0,
                reliability=0.0,
                segment_executions=[],
                started_at=started_at,
                completed_at=datetime.utcnow(),
                error_message=str(e)
            )
    
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get status of an active execution"""
        return self.advanced_service.get_execution_status(execution_id) or self.active_executions.get(execution_id)
    
    async def pause_execution(self, execution_id: str) -> bool:
        """Pause an execution"""
        return await self.advanced_service.pause_execution(execution_id)
    
    async def resume_execution(self, execution_id: str) -> bool:
        """Resume a paused execution"""
        return await self.advanced_service.resume_execution(execution_id)
    
    async def cancel_execution(self, execution_id: str, cancel_pending: bool = True, rollback: bool = False) -> Dict[str, Any]:
        """Cancel an execution"""
        from app.schemas.execution import CancelExecutionRequest
        request = CancelExecutionRequest(
            execution_id=execution_id,
            cancel_pending_segments=cancel_pending,
            rollback_completed=rollback
        )
        return await self.advanced_service.cancel_execution(request)
    
    async def reroute_execution(self, execution_id: str, from_current: bool = True, new_route: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Dynamically re-route an execution"""
        from app.schemas.execution import RerouteRequest
        request = RerouteRequest(
            execution_id=execution_id,
            from_current_position=from_current,
            new_route=new_route
        )
        return await self.advanced_service.reroute_execution(request)
    
    async def modify_transaction(self, execution_id: str, segment_index: int, new_amount: Optional[float] = None) -> Dict[str, Any]:
        """Modify a transaction"""
        from app.schemas.execution import ModifyTransactionRequest
        request = ModifyTransactionRequest(
            execution_id=execution_id,
            segment_index=segment_index,
            new_amount=new_amount
        )
        return await self.advanced_service.modify_transaction(request)
    
    def get_wallet_balance(self, wallet_address: str, asset: str) -> float:
        """Get simulated wallet balance"""
        return self.simulator.get_balance(wallet_address, asset)
    
    def get_transaction_status(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """Get status of a simulated transaction"""
        return self.simulator.get_transaction_status(tx_hash)

