"""
Advanced Execution Service with Dynamic Re-routing, Pause/Resume, and Parallel Execution
"""
import uuid
import asyncio
import logging
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
from enum import Enum

from app.schemas.route_segment import RouteSegment, SegmentType
from app.schemas.execution import (
    RouteExecutionRequest,
    RouteExecutionResponse,
    ExecutionStatus,
    SegmentExecutionResult,
    SegmentExecutionStatus,
    RerouteRequest,
    CancelExecutionRequest,
    ModifyTransactionRequest
)
from app.services.execution.simulator import Simulator
from app.services.execution.segment_executors import (
    FXExecutor,
    CryptoExecutor,
    BridgeExecutor,
    RampExecutor,
    BankRailExecutor
)
from app.services.routing_service import RoutingService
from app.services.aggregator_service import AggregatorService
from app.clients import WiseClient, KrakenClient
from app.config import settings
import httpx

logger = logging.getLogger(__name__)


class ExecutionState(Enum):
    """Execution state for pause/resume"""
    RUNNING = "running"
    PAUSED = "paused"
    CANCELLING = "cancelling"
    REROUTING = "rerouting"


class AdvancedExecutionService:
    """Advanced execution service with dynamic re-routing, pause/resume, and parallel execution"""
    
    def __init__(self, routing_service: RoutingService, aggregator_service: AggregatorService):
        self.routing_service = routing_service
        self.aggregator_service = aggregator_service
        self.simulator = Simulator()
        self.execution_mode = settings.execution_mode
        
        # Initialize API clients
        self.http_client = httpx.AsyncClient(timeout=30.0)
        self.wise_client = WiseClient(self.http_client) if settings.wise_api_key else None
        self.kraken_client = KrakenClient(self.http_client) if settings.kraken_api_key else None
        
        # Initialize executors
        self.executors = {
            SegmentType.FX: FXExecutor(self.simulator, wise_client=self.wise_client),
            SegmentType.CRYPTO: CryptoExecutor(self.simulator, kraken_client=self.kraken_client),
            SegmentType.BRIDGE: BridgeExecutor(self.simulator),
            SegmentType.ON_RAMP: RampExecutor(self.simulator),
            SegmentType.OFF_RAMP: RampExecutor(self.simulator),
            SegmentType.BANK_RAIL: BankRailExecutor(self.simulator, wise_client=self.wise_client),
        }
        
        # Enhanced state management
        self.active_executions: Dict[str, Dict[str, Any]] = {}
        self.execution_states: Dict[str, ExecutionState] = {}
        self.execution_locks: Dict[str, asyncio.Lock] = {}
        self.transaction_ids: Dict[str, Dict[int, Dict[str, str]]] = {}  # execution_id -> segment_index -> {provider: tx_id}
        self.max_execution_history = 1000
        
        # AI decision making for re-routing
        self.reroute_thresholds = {
            "cost_increase_percent": 5.0,  # Re-route if cost increases by 5%
            "latency_increase_percent": 20.0,  # Re-route if latency increases by 20%
            "reliability_decrease": 0.1,  # Re-route if reliability decreases by 0.1
        }
    
    async def execute_route(
        self,
        request: RouteExecutionRequest,
        parallel: bool = False,
        enable_ai_rerouting: bool = True
    ) -> RouteExecutionResponse:
        """
        Execute route with advanced features
        
        Args:
            request: Route execution request
            parallel: Enable parallel execution where possible
            enable_ai_rerouting: Enable AI-based dynamic re-routing
        """
        execution_id = str(uuid.uuid4())
        started_at = datetime.utcnow()
        
        # Initialize execution state
        self.active_executions[execution_id] = {
            "status": ExecutionStatus.IN_PROGRESS,
            "started_at": started_at,
            "current_segment": 0,
            "total_segments": 0,
            "segment_executions": [],
            "route": [],
            "parallel": parallel,
            "ai_rerouting": enable_ai_rerouting,
            "original_route": None,
            "current_amount": request.amount,
            "wallet_address": None
        }
        self.execution_states[execution_id] = ExecutionState.RUNNING
        self.execution_locks[execution_id] = asyncio.Lock()
        self.transaction_ids[execution_id] = {}
        
        try:
            # Get initial route
            route_result = await self._get_optimal_route(request)
            if "error" in route_result:
                raise ValueError(route_result["error"])
            
            route_segments = route_result["route"]
            self.active_executions[execution_id]["route"] = route_segments
            self.active_executions[execution_id]["total_segments"] = len(route_segments)
            self.active_executions[execution_id]["original_route"] = route_segments.copy()
            
            # Execute route
            if parallel:
                result = await self._execute_parallel(execution_id, route_segments, request)
            else:
                result = await self._execute_sequential(execution_id, route_segments, request, enable_ai_rerouting)
            
            return result
            
        except Exception as e:
            logger.error(f"Execution {execution_id} failed: {e}")
            self.active_executions[execution_id]["status"] = ExecutionStatus.FAILED
            self.execution_states[execution_id] = ExecutionState.RUNNING  # Reset state
            
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
    
    async def _get_optimal_route(self, request: RouteExecutionRequest) -> Dict[str, Any]:
        """Get optimal route"""
        segments = await self.aggregator_service.get_cached_segments()
        if not segments:
            segments = await self.aggregator_service.get_segments_from_db(limit=1000)
        
        if not segments:
            return {"error": "No route segments available"}
        
        return self.routing_service.find_optimal_route(
            segments=segments,
            from_asset=request.from_asset,
            to_asset=request.to_asset,
            from_network=request.from_network,
            to_network=request.to_network
        )
    
    async def _execute_sequential(
        self,
        execution_id: str,
        route_segments: List[Dict[str, Any]],
        request: RouteExecutionRequest,
        enable_ai_rerouting: bool
    ) -> RouteExecutionResponse:
        """Execute segments sequentially with AI re-routing"""
        segment_executions: List[SegmentExecutionResult] = []
        current_amount = request.amount
        wallet_address = None
        
        for idx, segment_dict in enumerate(route_segments):
            # Check if execution was cancelled or paused
            async with self.execution_locks[execution_id]:
                state = self.execution_states.get(execution_id)
                if state == ExecutionState.CANCELLING:
                    return await self._handle_cancellation(execution_id, segment_executions, request.amount)
                elif state == ExecutionState.PAUSED:
                    await self._wait_for_resume(execution_id)
                elif state == ExecutionState.REROUTING:
                    # Re-routing in progress, wait
                    await asyncio.sleep(0.1)
                    continue
            
            # AI-based re-routing check
            if enable_ai_rerouting and idx > 0:
                should_reroute = await self._should_reroute(execution_id, idx, current_amount, request)
                if should_reroute:
                    logger.info(f"Execution {execution_id}: AI decision to re-route at segment {idx}")
                    new_route = await self._calculate_reroute(execution_id, idx, current_amount, request)
                    if new_route:
                        route_segments = new_route
                        self.active_executions[execution_id]["route"] = route_segments
                        self.active_executions[execution_id]["total_segments"] = len(route_segments)
                        # Continue with new route
                        continue
            
            # Execute segment
            segment_result = await self._execute_segment(
                execution_id, idx, segment_dict, current_amount, wallet_address
            )
            
            segment_executions.append(segment_result)
            self.active_executions[execution_id]["segment_executions"] = segment_executions
            self.active_executions[execution_id]["current_segment"] = idx + 1
            
            # Update wallet address if generated
            if segment_result.simulation_data.get("wallet_address"):
                wallet_address = segment_result.simulation_data["wallet_address"]
            
            # Check if segment failed
            if segment_result.status == SegmentExecutionStatus.FAILED:
                logger.error(f"Execution {execution_id}: Segment {idx + 1} failed")
                self.active_executions[execution_id]["status"] = ExecutionStatus.FAILED
                break
            
            # Update current amount
            current_amount = segment_result.output_amount
            self.active_executions[execution_id]["current_amount"] = current_amount
        
        # Calculate final result
        return await self._build_response(execution_id, route_segments, segment_executions, request.amount, current_amount, request)
    
    async def _execute_parallel(
        self,
        execution_id: str,
        route_segments: List[Dict[str, Any]],
        request: RouteExecutionRequest
    ) -> RouteExecutionResponse:
        """Execute segments in parallel where possible"""
        # Group segments that can run in parallel (independent segments)
        parallel_groups = self._group_parallel_segments(route_segments)
        
        segment_executions: List[SegmentExecutionResult] = []
        current_amount = request.amount
        wallet_address = None
        
        for group_idx, group in enumerate(parallel_groups):
            # Execute group in parallel
            tasks = []
            for seg_idx, segment_dict in group:
                task = self._execute_segment(
                    execution_id, seg_idx, segment_dict, current_amount, wallet_address
                )
                tasks.append((seg_idx, task))
            
            # Wait for all segments in group to complete
            results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
            
            # Process results
            for (seg_idx, _), result in zip(tasks, results):
                if isinstance(result, Exception):
                    segment_result = SegmentExecutionResult(
                        segment_index=seg_idx,
                        segment_type="unknown",
                        from_asset="",
                        to_asset="",
                        status=SegmentExecutionStatus.FAILED,
                        input_amount=current_amount,
                        output_amount=0.0,
                        fees_paid=0.0,
                        error_message=str(result)
                    )
                else:
                    segment_result = result
                
                segment_executions.append(segment_result)
                
                # Update wallet address
                if segment_result.simulation_data.get("wallet_address"):
                    wallet_address = segment_result.simulation_data["wallet_address"]
                
                # Update amount (use max output for parallel segments)
                if segment_result.output_amount > current_amount:
                    current_amount = segment_result.output_amount
            
            self.active_executions[execution_id]["segment_executions"] = segment_executions
            self.active_executions[execution_id]["current_segment"] = group[-1][0] + 1
        
        return await self._build_response(execution_id, route_segments, segment_executions, request.amount, current_amount, request)
    
    def _group_parallel_segments(self, route_segments: List[Dict[str, Any]]) -> List[List[tuple]]:
        """Group segments that can execute in parallel"""
        groups = []
        current_group = []
        
        for idx, segment in enumerate(route_segments):
            seg_type = segment.get("segment_type")
            
            # Segments that can run in parallel (independent operations)
            if seg_type in ["fx", "crypto"] and len(current_group) < 3:
                current_group.append((idx, segment))
            else:
                if current_group:
                    groups.append(current_group)
                current_group = [(idx, segment)]
        
        if current_group:
            groups.append(current_group)
        
        return groups
    
    async def _execute_segment(
        self,
        execution_id: str,
        segment_index: int,
        segment_dict: Dict[str, Any],
        input_amount: float,
        wallet_address: Optional[str]
    ) -> SegmentExecutionResult:
        """Execute a single segment"""
        try:
            segment = RouteSegment(
                segment_type=SegmentType(segment_dict.get("segment_type", "")),
                from_asset=segment_dict.get("from_asset", ""),
                to_asset=segment_dict.get("to_asset", ""),
                from_network=segment_dict.get("from_network"),
                to_network=segment_dict.get("to_network"),
                cost=segment_dict.get("cost", {}),
                latency=segment_dict.get("latency", {}),
                reliability_score=segment_dict.get("reliability_score", 1.0),
                provider=segment_dict.get("provider")
            )
            
            executor = self.executors.get(segment.segment_type)
            if not executor:
                return SegmentExecutionResult(
                    segment_index=segment_index,
                    segment_type=segment.segment_type.value,
                    from_asset=segment.from_asset,
                    to_asset=segment.to_asset,
                    status=SegmentExecutionStatus.SKIPPED,
                    input_amount=input_amount,
                    output_amount=input_amount,
                    fees_paid=0.0,
                    error_message=f"No executor for {segment.segment_type}"
                )
            
            result = await executor.execute(
                segment=segment,
                input_amount=input_amount,
                wallet_address=wallet_address,
                metadata={"segment_index": segment_index, "execution_id": execution_id}
            )
            
            # Store transaction IDs for cancellation
            if result.transaction_hash:
                if execution_id not in self.transaction_ids:
                    self.transaction_ids[execution_id] = {}
                self.transaction_ids[execution_id][segment_index] = {
                    "provider": segment.provider or "unknown",
                    "tx_id": result.transaction_hash
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing segment {segment_index}: {e}")
            return SegmentExecutionResult(
                segment_index=segment_index,
                segment_type=segment_dict.get("segment_type", "unknown"),
                from_asset=segment_dict.get("from_asset", ""),
                to_asset=segment_dict.get("to_asset", ""),
                status=SegmentExecutionStatus.FAILED,
                input_amount=input_amount,
                output_amount=0.0,
                fees_paid=0.0,
                error_message=str(e)
            )
    
    async def _should_reroute(
        self,
        execution_id: str,
        current_segment: int,
        current_amount: float,
        request: RouteExecutionRequest
    ) -> bool:
        """AI-based decision: should we re-route?"""
        try:
            # Get current route metrics
            current_route = self.active_executions[execution_id]["route"]
            completed_segments = self.active_executions[execution_id]["segment_executions"]
            
            # Calculate current route cost/latency
            total_cost = sum(seg.fees_paid for seg in completed_segments)
            total_latency = sum(seg.confirmation_time_minutes or 0 for seg in completed_segments)
            
            # Get new optimal route from current position
            remaining_segments = current_route[current_segment:]
            if not remaining_segments:
                return False
            
            # Calculate what remaining route should cost
            remaining_cost_estimate = sum(
                seg.get("cost", {}).get("fee_percent", 0) * current_amount / 100
                for seg in remaining_segments
            )
            
            # Get alternative route
            segments = await self.aggregator_service.get_cached_segments()
            if not segments:
                return False
            
            # Find route from current asset to destination
            current_asset = remaining_segments[0].get("from_asset") if remaining_segments else request.to_asset
            alt_route = self.routing_service.find_optimal_route(
                segments=segments,
                from_asset=current_asset,
                to_asset=request.to_asset,
                from_network=remaining_segments[0].get("from_network") if remaining_segments else None,
                to_network=request.to_network
            )
            
            if "error" in alt_route:
                return False
            
            # Compare routes
            alt_cost = alt_route.get("cost_percent", 0) * current_amount / 100
            alt_latency = alt_route.get("eta_hours", 0) * 60
            
            # Decision logic
            cost_increase = ((alt_cost - remaining_cost_estimate) / remaining_cost_estimate * 100) if remaining_cost_estimate > 0 else 0
            latency_increase = ((alt_latency - total_latency) / total_latency * 100) if total_latency > 0 else 0
            
            should_reroute = (
                cost_increase < -self.reroute_thresholds["cost_increase_percent"] or  # Better cost
                latency_increase < -self.reroute_thresholds["latency_increase_percent"] or  # Better latency
                alt_route.get("reliability", 0) > 0.9  # High reliability alternative
            )
            
            return should_reroute
            
        except Exception as e:
            logger.error(f"Error in AI re-routing decision: {e}")
            return False
    
    async def _calculate_reroute(
        self,
        execution_id: str,
        current_segment: int,
        current_amount: float,
        request: RouteExecutionRequest
    ) -> Optional[List[Dict[str, Any]]]:
        """Calculate new route from current position"""
        try:
            current_route = self.active_executions[execution_id]["route"]
            remaining_segments = current_route[current_segment:]
            
            if not remaining_segments:
                return None
            
            # Get current asset
            current_asset = remaining_segments[0].get("from_asset")
            current_network = remaining_segments[0].get("from_network")
            
            # Get new route
            segments = await self.aggregator_service.get_cached_segments()
            if not segments:
                segments = await self.aggregator_service.get_segments_from_db(limit=1000)
            
            if not segments:
                return None
            
            new_route_result = self.routing_service.find_optimal_route(
                segments=segments,
                from_asset=current_asset,
                to_asset=request.to_asset,
                from_network=current_network,
                to_network=request.to_network
            )
            
            if "error" in new_route_result:
                return None
            
            # Combine completed segments with new route
            completed = self.active_executions[execution_id]["segment_executions"]
            new_route = new_route_result.get("route", [])
            
            # Update execution state
            self.execution_states[execution_id] = ExecutionState.REROUTING
            self.active_executions[execution_id]["status"] = ExecutionStatus.REROUTING
            
            # Return new route starting from current position
            return new_route
            
        except Exception as e:
            logger.error(f"Error calculating re-route: {e}")
            return None
    
    async def pause_execution(self, execution_id: str) -> bool:
        """Pause an execution"""
        if execution_id not in self.active_executions:
            return False
        
        async with self.execution_locks[execution_id]:
            self.execution_states[execution_id] = ExecutionState.PAUSED
            self.active_executions[execution_id]["status"] = ExecutionStatus.PAUSED
            logger.info(f"Execution {execution_id} paused")
        
        return True
    
    async def resume_execution(self, execution_id: str) -> bool:
        """Resume a paused execution"""
        if execution_id not in self.active_executions:
            return False
        
        async with self.execution_locks[execution_id]:
            if self.execution_states[execution_id] != ExecutionState.PAUSED:
                return False
            
            self.execution_states[execution_id] = ExecutionState.RUNNING
            self.active_executions[execution_id]["status"] = ExecutionStatus.IN_PROGRESS
            logger.info(f"Execution {execution_id} resumed")
        
        return True
    
    async def _wait_for_resume(self, execution_id: str):
        """Wait for execution to be resumed"""
        while self.execution_states.get(execution_id) == ExecutionState.PAUSED:
            await asyncio.sleep(0.5)
    
    async def cancel_execution(self, request: CancelExecutionRequest) -> Dict[str, Any]:
        """Cancel an execution"""
        execution_id = request.execution_id
        
        if execution_id not in self.active_executions:
            return {"error": "Execution not found"}
        
        async with self.execution_locks[execution_id]:
            self.execution_states[execution_id] = ExecutionState.CANCELLING
            self.active_executions[execution_id]["status"] = ExecutionStatus.CANCELLED
        
        # Cancel pending transactions
        cancelled_count = 0
        if request.cancel_pending_segments:
            tx_ids = self.transaction_ids.get(execution_id, {})
            for seg_idx, tx_info in tx_ids.items():
                try:
                    provider = tx_info.get("provider")
                    tx_id = tx_info.get("tx_id")
                    
                    if provider == "wise" and self.wise_client:
                        result = await self.wise_client.cancel_transfer(tx_id)
                        if result:
                            cancelled_count += 1
                    elif provider == "kraken" and self.kraken_client:
                        result = await self.kraken_client.cancel_order(tx_id)
                        if result:
                            cancelled_count += 1
                except Exception as e:
                    logger.error(f"Error cancelling transaction {tx_id}: {e}")
        
        return {
            "execution_id": execution_id,
            "status": "cancelled",
            "cancelled_transactions": cancelled_count
        }
    
    async def _handle_cancellation(
        self,
        execution_id: str,
        segment_executions: List[SegmentExecutionResult],
        original_amount: float
    ) -> RouteExecutionResponse:
        """Handle execution cancellation"""
        return RouteExecutionResponse(
            execution_id=execution_id,
            status=ExecutionStatus.CANCELLED,
            route=self.active_executions[execution_id].get("route", []),
            total_cost_percent=0.0,
            total_fees=sum(seg.fees_paid for seg in segment_executions),
            input_amount=original_amount,
            final_amount=segment_executions[-1].output_amount if segment_executions else original_amount,
            eta_hours=0.0,
            reliability=0.0,
            segment_executions=segment_executions,
            started_at=self.active_executions[execution_id]["started_at"],
            completed_at=datetime.utcnow()
        )
    
    async def reroute_execution(self, request: RerouteRequest) -> Dict[str, Any]:
        """Dynamically re-route an execution"""
        execution_id = request.execution_id
        
        if execution_id not in self.active_executions:
            return {"error": "Execution not found"}
        
        exec_data = self.active_executions[execution_id]
        
        if request.from_current_position:
            # Re-route from current position
            current_segment = exec_data["current_segment"]
            current_amount = exec_data["current_amount"]
            
            # Calculate new route
            new_route = await self._calculate_reroute(
                execution_id, current_segment, current_amount,
                RouteExecutionRequest(
                    from_asset=exec_data["route"][current_segment].get("from_asset") if current_segment < len(exec_data["route"]) else "",
                    to_asset=exec_data["route"][-1].get("to_asset") if exec_data["route"] else "",
                    amount=current_amount
                )
            )
            
            if new_route:
                exec_data["route"] = new_route
                exec_data["total_segments"] = len(new_route)
                self.execution_states[execution_id] = ExecutionState.RUNNING
                return {"status": "rerouted", "new_route": new_route}
        else:
            # Use provided route
            if request.new_route:
                exec_data["route"] = request.new_route
                exec_data["total_segments"] = len(request.new_route)
                self.execution_states[execution_id] = ExecutionState.RUNNING
                return {"status": "rerouted", "new_route": request.new_route}
        
        return {"error": "Failed to reroute"}
    
    async def modify_transaction(self, request: ModifyTransactionRequest) -> Dict[str, Any]:
        """Modify a transaction"""
        execution_id = request.execution_id
        
        if execution_id not in self.active_executions:
            return {"error": "Execution not found"}
        
        exec_data = self.active_executions[execution_id]
        segment_executions = exec_data["segment_executions"]
        
        if request.segment_index >= len(segment_executions):
            return {"error": "Segment index out of range"}
        
        segment_result = segment_executions[request.segment_index]
        tx_info = self.transaction_ids.get(execution_id, {}).get(request.segment_index)
        
        if not tx_info:
            return {"error": "Transaction not found"}
        
        provider = tx_info.get("provider")
        tx_id = tx_info.get("tx_id")
        
        try:
            if provider == "wise" and self.wise_client:
                result = await self.wise_client.modify_transfer(tx_id)
                if result and result.get("can_create_new"):
                    # Create new transfer with modified amount
                    # This would require the original segment data
                    return {"status": "modified", "new_transfer_required": True}
            elif provider == "kraken" and self.kraken_client:
                result = await self.kraken_client.modify_order(tx_id, new_volume=request.new_amount)
                if result and result.get("can_create_new"):
                    return {"status": "modified", "new_order_required": True}
            
            return {"error": "Modification not supported for this provider"}
        except Exception as e:
            return {"error": str(e)}
    
    async def _build_response(
        self,
        execution_id: str,
        route_segments: List[Dict[str, Any]],
        segment_executions: List[SegmentExecutionResult],
        input_amount: float,
        final_amount: float,
        request: RouteExecutionRequest
    ) -> RouteExecutionResponse:
        """Build execution response"""
        total_fees = sum(seg.fees_paid for seg in segment_executions)
        total_time = sum(seg.confirmation_time_minutes or 0 for seg in segment_executions)
        
        status = ExecutionStatus.COMPLETED
        if any(seg.status == SegmentExecutionStatus.FAILED for seg in segment_executions):
            status = ExecutionStatus.FAILED
        elif self.execution_states.get(execution_id) == ExecutionState.CANCELLING:
            status = ExecutionStatus.CANCELLED
        
        exec_data = self.active_executions[execution_id]
        
        return RouteExecutionResponse(
            execution_id=execution_id,
            status=status,
            route=route_segments,
            total_cost_percent=(total_fees / input_amount * 100) if input_amount > 0 else 0.0,
            total_fees=total_fees,
            input_amount=input_amount,
            final_amount=final_amount,
            eta_hours=total_time / 60.0,
            reliability=0.9,  # Calculate from segments
            segment_executions=segment_executions,
            started_at=exec_data["started_at"],
            completed_at=datetime.utcnow(),
            total_time_minutes=total_time
        )
    
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get execution status"""
        return self.active_executions.get(execution_id)

