"""
Segment Executors - Execute individual route segments
Each executor handles a specific segment type (FX, crypto, bridge, etc.)
"""
import asyncio
import random
import uuid
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from app.schemas.route_segment import RouteSegment, SegmentType
from app.schemas.execution import SegmentExecutionResult, SegmentExecutionStatus
from app.services.execution.simulator import Simulator
from app.clients import WiseClient, KrakenClient
from app.config import settings

logger = logging.getLogger(__name__)


class SegmentExecutor:
    """Base class for segment executors"""
    
    def __init__(self, simulator: Simulator, wise_client: Optional[WiseClient] = None, kraken_client: Optional[KrakenClient] = None):
        self.simulator = simulator
        self.wise_client = wise_client
        self.kraken_client = kraken_client
        self.execution_mode = settings.execution_mode
    
    async def execute(
        self,
        segment: RouteSegment,
        input_amount: float,
        wallet_address: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SegmentExecutionResult:
        """Execute a segment - to be implemented by subclasses"""
        raise NotImplementedError


class FXExecutor(SegmentExecutor):
    """Execute FX conversion segments"""
    
    async def execute(
        self,
        segment: RouteSegment,
        input_amount: float,
        wallet_address: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SegmentExecutionResult:
        """Execute FX conversion"""
        started_at = datetime.utcnow()
        
        try:
            # Real execution via Wise API
            if self.execution_mode == "real" and self.wise_client and segment.provider == "wise":
                try:
                    # Get profile ID (cache this in production)
                    profiles = await self.wise_client.get_profiles()
                    if not profiles:
                        raise ValueError("No Wise profiles found")
                    profile_id = profiles[0]["id"]
                    
                    # Create quote
                    quote = await self.wise_client.create_quote(
                        profile_id=profile_id,
                        source_currency=segment.from_asset,
                        target_currency=segment.to_asset,
                        source_amount=input_amount
                    )
                    
                    if not quote:
                        raise ValueError("Failed to create Wise quote")
                    
                    output_amount = quote.get("targetAmount", 0.0)
                    fees = quote.get("fee", {}).get("total", 0.0)
                    fx_rate = quote.get("rate", 1.0)
                    
                    completed_at = datetime.utcnow()
                    # Wise transfers typically take 0.5-2 hours
                    confirmation_time = 60.0  # 1 hour average
                    
                    logger.info(f"Wise FX conversion completed: {segment.from_asset} -> {segment.to_asset}, "
                               f"{input_amount} -> {output_amount}")
                    
                    return SegmentExecutionResult(
                        segment_index=metadata.get("segment_index", 0) if metadata else 0,
                        segment_type=segment.segment_type.value,
                        from_asset=segment.from_asset,
                        to_asset=segment.to_asset,
                        status=SegmentExecutionStatus.COMPLETED,
                        input_amount=input_amount,
                        output_amount=output_amount,
                        fees_paid=fees,
                        provider=segment.provider,
                        started_at=started_at,
                        completed_at=completed_at,
                        confirmation_time_minutes=confirmation_time,
                        simulation_data={
                            "quote_id": quote.get("id"),
                            "fx_rate": fx_rate,
                            "type": "wise_fx_conversion",
                            "execution_mode": "real"
                        }
                    )
                except Exception as e:
                    logger.error(f"Wise API execution failed, falling back to simulation: {e}")
                    # Fall through to simulation
            
            # Simulation mode or fallback
            # Calculate fees and output amount
            fee_percent = segment.cost.get("fee_percent", 0.0)
            fixed_fee = segment.cost.get("fixed_fee", 0.0)
            fx_rate = segment.cost.get("effective_fx_rate", 1.0)
            
            fees = (input_amount * fee_percent / 100) + fixed_fee
            amount_after_fees = input_amount - fees
            output_amount = amount_after_fees * fx_rate
            
            # Simulate FX conversion
            min_minutes = segment.latency.get("min_minutes", 5)
            max_minutes = segment.latency.get("max_minutes", 10)
            
            fx_result = await self.simulator.simulate_fx_conversion(
                from_currency=segment.from_asset,
                to_currency=segment.to_asset,
                amount=amount_after_fees,
                rate=fx_rate,
                min_minutes=min_minutes,
                max_minutes=max_minutes
            )
            
            completed_at = datetime.utcnow()
            confirmation_time = fx_result["processing_time_minutes"]
            
            logger.info(f"FX conversion completed (simulation): {segment.from_asset} -> {segment.to_asset}, "
                       f"{input_amount} -> {output_amount}")
            
            return SegmentExecutionResult(
                segment_index=metadata.get("segment_index", 0) if metadata else 0,
                segment_type=segment.segment_type.value,
                from_asset=segment.from_asset,
                to_asset=segment.to_asset,
                status=SegmentExecutionStatus.COMPLETED,
                input_amount=input_amount,
                output_amount=output_amount,
                fees_paid=fees,
                provider=segment.provider,
                started_at=started_at,
                completed_at=completed_at,
                confirmation_time_minutes=confirmation_time,
                simulation_data={
                    "conversion_id": fx_result["conversion_id"],
                    "fx_rate": fx_rate,
                    "type": "fx_conversion",
                    "execution_mode": "simulation"
                }
            )
            
        except Exception as e:
            logger.error(f"FX execution failed: {e}")
            return SegmentExecutionResult(
                segment_index=metadata.get("segment_index", 0) if metadata else 0,
                segment_type=segment.segment_type.value,
                from_asset=segment.from_asset,
                to_asset=segment.to_asset,
                status=SegmentExecutionStatus.FAILED,
                input_amount=input_amount,
                output_amount=0.0,
                fees_paid=0.0,
                provider=segment.provider,
                started_at=started_at,
                error_message=str(e)
            )


class CryptoExecutor(SegmentExecutor):
    """Execute crypto swap segments"""
    
    async def execute(
        self,
        segment: RouteSegment,
        input_amount: float,
        wallet_address: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SegmentExecutionResult:
        """Execute crypto swap"""
        started_at = datetime.utcnow()
        
        try:
            # Real execution via Kraken API
            if self.execution_mode == "real" and self.kraken_client and segment.provider == "kraken":
                try:
                    # Execute swap via Kraken
                    swap_result = await self.kraken_client.execute_crypto_swap(
                        from_asset=segment.from_asset,
                        to_asset=segment.to_asset,
                        amount=input_amount
                    )
                    
                    order_id = swap_result.get("order_id")
                    if order_id:
                        # Poll for order completion
                        max_attempts = 10
                        for attempt in range(max_attempts):
                            await asyncio.sleep(2)  # Wait 2 seconds between checks
                            order_status = await self.kraken_client.get_order_status(order_id)
                            
                            if order_status:
                                status = order_status.get("status", "pending")
                                if status == "closed":
                                    # Order completed
                                    vol_exec = float(order_status.get("vol_exec", 0))
                                    cost = float(order_status.get("cost", 0))
                                    fee = float(order_status.get("fee", 0))
                                    
                                    # Determine output amount based on order type
                                    if swap_result.get("type") == "buy":
                                        output_amount = vol_exec  # Volume executed in base currency
                                    else:
                                        output_amount = cost - fee  # Cost minus fees
                                    
                                    completed_at = datetime.utcnow()
                                    confirmation_time = 5.0  # Kraken orders typically complete in minutes
                                    
                                    logger.info(f"Kraken swap completed: {segment.from_asset} -> {segment.to_asset}, "
                                               f"{input_amount} -> {output_amount}")
                                    
                                    return SegmentExecutionResult(
                                        segment_index=metadata.get("segment_index", 0) if metadata else 0,
                                        segment_type=segment.segment_type.value,
                                        from_asset=segment.from_asset,
                                        to_asset=segment.to_asset,
                                        from_network=segment.from_network,
                                        to_network=segment.to_network,
                                        status=SegmentExecutionStatus.COMPLETED,
                                        input_amount=input_amount,
                                        output_amount=output_amount,
                                        fees_paid=fee,
                                        transaction_hash=order_id,
                                        provider=segment.provider,
                                        started_at=started_at,
                                        completed_at=completed_at,
                                        confirmation_time_minutes=confirmation_time,
                                        simulation_data={
                                            "order_id": order_id,
                                            "pair": swap_result.get("pair"),
                                            "type": "kraken_swap",
                                            "execution_mode": "real"
                                        }
                                    )
                                elif status == "canceled" or status == "expired":
                                    raise ValueError(f"Order {order_id} was {status}")
                        
                        # If we get here, order is still pending
                        raise ValueError(f"Order {order_id} did not complete within timeout")
                    else:
                        raise ValueError("No order ID returned from Kraken")
                        
                except Exception as e:
                    logger.error(f"Kraken API execution failed, falling back to simulation: {e}")
                    # Fall through to simulation
            
            # Simulation mode or fallback
            if not wallet_address:
                wallet_address = self.simulator.generate_wallet(segment.from_network)
            
            # Ensure wallet has balance
            current_balance = self.simulator.get_balance(wallet_address, segment.from_asset)
            if current_balance < input_amount:
                self.simulator.add_balance(wallet_address, segment.from_asset, input_amount - current_balance)
            
            # Calculate fees and output amount with validation
            fee_percent = max(0.0, min(100.0, segment.cost.get("fee_percent", 0.0)))
            fixed_fee = max(0.0, segment.cost.get("fixed_fee", 0.0))
            swap_rate = segment.cost.get("effective_fx_rate", 1.0)
            
            if swap_rate <= 0:
                raise ValueError(f"Invalid swap rate: {swap_rate}")
            
            if input_amount < 0:
                raise ValueError(f"Invalid input amount: {input_amount}")
            
            fees = (input_amount * fee_percent / 100) + fixed_fee
            amount_after_fees = max(0.0, input_amount - fees)
            output_amount = amount_after_fees * swap_rate
            
            # Deduct from wallet
            self.simulator.subtract_balance(wallet_address, segment.from_asset, input_amount)
            
            # Create transaction
            tx_hash = self.simulator.create_transaction(
                tx_type="swap",
                from_address=wallet_address,
                to_address=None,
                asset=segment.from_asset,
                amount=input_amount,
                network=segment.from_network,
                metadata={
                    "to_asset": segment.to_asset,
                    "output_amount": output_amount,
                    "provider": segment.provider
                }
            )
            
            # Simulate confirmation
            min_minutes = segment.latency.get("min_minutes", 2)
            max_minutes = segment.latency.get("max_minutes", 5)
            block_time = 12.0 if segment.from_network != "polygon" else 2.0
            min_blocks = max(1, int(min_minutes * 60 / block_time))
            max_blocks = max(min_blocks, int(max_minutes * 60 / block_time))
            
            confirmation = await self.simulator.simulate_confirmation(
                tx_hash,
                min_blocks=min_blocks,
                max_blocks=max_blocks,
                block_time_seconds=block_time
            )
            
            # Add output to wallet
            self.simulator.add_balance(wallet_address, segment.to_asset, output_amount)
            
            completed_at = datetime.utcnow()
            confirmation_time = confirmation["confirmation_time_seconds"] / 60.0
            
            logger.info(f"Crypto swap completed (simulation): {segment.from_asset} -> {segment.to_asset}, "
                       f"{input_amount} -> {output_amount}")
            
            return SegmentExecutionResult(
                segment_index=metadata.get("segment_index", 0) if metadata else 0,
                segment_type=segment.segment_type.value,
                from_asset=segment.from_asset,
                to_asset=segment.to_asset,
                from_network=segment.from_network,
                to_network=segment.to_network,
                status=SegmentExecutionStatus.COMPLETED,
                input_amount=input_amount,
                output_amount=output_amount,
                fees_paid=fees,
                transaction_hash=tx_hash,
                provider=segment.provider,
                started_at=started_at,
                completed_at=completed_at,
                confirmation_time_minutes=confirmation_time,
                simulation_data={
                    "wallet_address": wallet_address,
                    "blocks_confirmed": confirmation["confirmations"],
                    "type": "crypto_swap",
                    "execution_mode": "simulation"
                }
            )
            
        except Exception as e:
            logger.error(f"Crypto execution failed: {e}")
            return SegmentExecutionResult(
                segment_index=metadata.get("segment_index", 0) if metadata else 0,
                segment_type=segment.segment_type.value,
                from_asset=segment.from_asset,
                to_asset=segment.to_asset,
                from_network=segment.from_network,
                to_network=segment.to_network,
                status=SegmentExecutionStatus.FAILED,
                input_amount=input_amount,
                output_amount=0.0,
                fees_paid=0.0,
                provider=segment.provider,
                started_at=started_at,
                error_message=str(e)
            )


class BridgeExecutor(SegmentExecutor):
    """Execute bridge segments"""
    
    async def execute(
        self,
        segment: RouteSegment,
        input_amount: float,
        wallet_address: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SegmentExecutionResult:
        """Execute cross-chain bridge"""
        started_at = datetime.utcnow()
        
        try:
            if not wallet_address:
                wallet_address = self.simulator.generate_wallet(segment.from_network)
            
            # Ensure wallet has balance
            current_balance = self.simulator.get_balance(wallet_address, segment.from_asset)
            if current_balance < input_amount:
                self.simulator.add_balance(wallet_address, segment.from_asset, input_amount - current_balance)
            
            # Calculate fees and output amount with validation
            fee_percent = max(0.0, min(100.0, segment.cost.get("fee_percent", 0.0)))
            fixed_fee = max(0.0, segment.cost.get("fixed_fee", 0.0))
            
            if input_amount < 0:
                raise ValueError(f"Invalid input amount: {input_amount}")
            
            fees = (input_amount * fee_percent / 100) + fixed_fee
            output_amount = max(0.0, input_amount - fees)  # Same asset, different network, ensure non-negative
            
            # Deduct from source network wallet
            self.simulator.subtract_balance(wallet_address, segment.from_asset, input_amount)
            
            # Create transaction on source network
            tx_hash = self.simulator.create_transaction(
                tx_type="bridge",
                from_address=wallet_address,
                to_address=None,
                asset=segment.from_asset,
                amount=input_amount,
                network=segment.from_network,
                metadata={
                    "to_network": segment.to_network,
                    "to_asset": segment.to_asset,
                    "output_amount": output_amount,
                    "provider": segment.provider
                }
            )
            
            # Simulate bridge confirmation (longer than regular swaps)
            min_minutes = segment.latency.get("min_minutes", 5)
            max_minutes = segment.latency.get("max_minutes", 15)
            block_time = 12.0 if segment.from_network != "polygon" else 2.0
            min_blocks = max(1, int(min_minutes * 60 / block_time))
            max_blocks = max(min_blocks, int(max_minutes * 60 / block_time))
            
            confirmation = await self.simulator.simulate_confirmation(
                tx_hash,
                min_blocks=min_blocks,
                max_blocks=max_blocks,
                block_time_seconds=block_time
            )
            
            # Generate destination network wallet (or use same address)
            dest_wallet = wallet_address  # Same address on different network
            
            # Add to destination network wallet
            self.simulator.add_balance(dest_wallet, segment.to_asset, output_amount)
            
            completed_at = datetime.utcnow()
            confirmation_time = confirmation["confirmation_time_seconds"] / 60.0
            
            logger.info(f"Bridge completed: {segment.from_asset} {segment.from_network} -> "
                       f"{segment.to_asset} {segment.to_network}, {input_amount} -> {output_amount}")
            
            return SegmentExecutionResult(
                segment_index=metadata.get("segment_index", 0) if metadata else 0,
                segment_type=segment.segment_type.value,
                from_asset=segment.from_asset,
                to_asset=segment.to_asset,
                from_network=segment.from_network,
                to_network=segment.to_network,
                status=SegmentExecutionStatus.COMPLETED,
                input_amount=input_amount,
                output_amount=output_amount,
                fees_paid=fees,
                transaction_hash=tx_hash,
                provider=segment.provider,
                started_at=started_at,
                completed_at=completed_at,
                confirmation_time_minutes=confirmation_time,
                simulation_data={
                    "from_wallet": wallet_address,
                    "to_wallet": dest_wallet,
                    "blocks_confirmed": confirmation["confirmations"],
                    "type": "bridge"
                }
            )
            
        except Exception as e:
            logger.error(f"Bridge execution failed: {e}")
            return SegmentExecutionResult(
                segment_index=metadata.get("segment_index", 0) if metadata else 0,
                segment_type=segment.segment_type.value,
                from_asset=segment.from_asset,
                to_asset=segment.to_asset,
                from_network=segment.from_network,
                to_network=segment.to_network,
                status=SegmentExecutionStatus.FAILED,
                input_amount=input_amount,
                output_amount=0.0,
                fees_paid=0.0,
                provider=segment.provider,
                started_at=started_at,
                error_message=str(e)
            )


class RampExecutor(SegmentExecutor):
    """Execute on/off-ramp segments"""
    
    async def execute(
        self,
        segment: RouteSegment,
        input_amount: float,
        wallet_address: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SegmentExecutionResult:
        """Execute on-ramp or off-ramp"""
        started_at = datetime.utcnow()
        
        try:
            is_on_ramp = segment.segment_type.value == "on_ramp"
            
            if is_on_ramp:
                # Fiat -> Crypto
                if not wallet_address:
                    wallet_address = self.simulator.generate_wallet(segment.to_network)
                
                # Calculate fees and output amount with validation
                fee_percent = max(0.0, min(100.0, segment.cost.get("fee_percent", 0.0)))
                fixed_fee = max(0.0, segment.cost.get("fixed_fee", 0.0))
                rate = segment.cost.get("effective_fx_rate", 1.0)
                
                if rate <= 0:
                    raise ValueError(f"Invalid rate: {rate}")
                if input_amount < 0:
                    raise ValueError(f"Invalid input amount: {input_amount}")
                
                fees = (input_amount * fee_percent / 100) + fixed_fee
                amount_after_fees = max(0.0, input_amount - fees)
                output_amount = amount_after_fees * rate
                
                # Simulate processing time
                min_minutes = segment.latency.get("min_minutes", 10)
                max_minutes = segment.latency.get("max_minutes", 30)
                processing_minutes = random.uniform(min_minutes, max_minutes)
                await asyncio.sleep(min(processing_minutes / 60, 1.0))
                
                # Add crypto to wallet
                self.simulator.add_balance(wallet_address, segment.to_asset, output_amount)
                
                completed_at = datetime.utcnow()
                tx_hash = None
                confirmation_time = processing_minutes
                confirmation = None
                
                logger.info(f"On-ramp completed: {segment.from_asset} -> {segment.to_asset}, "
                           f"{input_amount} -> {output_amount}")
                
            else:
                # Off-ramp: Crypto -> Fiat
                if not wallet_address:
                    wallet_address = self.simulator.generate_wallet(segment.from_network)
                
                # Ensure wallet has balance
                current_balance = self.simulator.get_balance(wallet_address, segment.from_asset)
                if current_balance < input_amount:
                    self.simulator.add_balance(wallet_address, segment.from_asset, input_amount - current_balance)
                
                # Calculate fees and output amount with validation
                fee_percent = max(0.0, min(100.0, segment.cost.get("fee_percent", 0.0)))
                fixed_fee = max(0.0, segment.cost.get("fixed_fee", 0.0))
                rate = segment.cost.get("effective_fx_rate", 1.0)
                
                if rate <= 0:
                    raise ValueError(f"Invalid rate: {rate}")
                if input_amount < 0:
                    raise ValueError(f"Invalid input amount: {input_amount}")
                
                fees = (input_amount * fee_percent / 100) + fixed_fee
                amount_after_fees = max(0.0, input_amount - fees)
                output_amount = amount_after_fees * rate
                
                # Deduct from wallet
                self.simulator.subtract_balance(wallet_address, segment.from_asset, input_amount)
                
                # Create transaction
                tx_hash = self.simulator.create_transaction(
                    tx_type="off_ramp",
                    from_address=wallet_address,
                    to_address=None,
                    asset=segment.from_asset,
                    amount=input_amount,
                    network=segment.from_network,
                    metadata={
                        "to_asset": segment.to_asset,
                        "output_amount": output_amount,
                        "provider": segment.provider
                    }
                )
                
                # Simulate confirmation
                min_minutes = segment.latency.get("min_minutes", 5)
                max_minutes = segment.latency.get("max_minutes", 15)
                block_time = 12.0 if segment.from_network != "polygon" else 2.0
                min_blocks = max(1, int(min_minutes * 60 / block_time))
                max_blocks = max(min_blocks, int(max_minutes * 60 / block_time))
                
                confirmation = await self.simulator.simulate_confirmation(
                    tx_hash,
                    min_blocks=min_blocks,
                    max_blocks=max_blocks,
                    block_time_seconds=block_time
                )
                
                completed_at = datetime.utcnow()
                confirmation_time = confirmation["confirmation_time_seconds"] / 60.0
                
                logger.info(f"Off-ramp completed: {segment.from_asset} -> {segment.to_asset}, "
                           f"{input_amount} -> {output_amount}")
            
            return SegmentExecutionResult(
                segment_index=metadata.get("segment_index", 0) if metadata else 0,
                segment_type=segment.segment_type.value,
                from_asset=segment.from_asset,
                to_asset=segment.to_asset,
                from_network=segment.from_network,
                to_network=segment.to_network,
                status=SegmentExecutionStatus.COMPLETED,
                input_amount=input_amount,
                output_amount=output_amount,
                fees_paid=fees,
                transaction_hash=tx_hash if not is_on_ramp else None,
                provider=segment.provider,
                started_at=started_at,
                completed_at=completed_at,
                confirmation_time_minutes=confirmation_time if not is_on_ramp else processing_minutes,
                simulation_data={
                    "wallet_address": wallet_address,
                    "type": "on_ramp" if is_on_ramp else "off_ramp",
                    "blocks_confirmed": confirmation.get("confirmations") if not is_on_ramp else None
                }
            )
            
        except Exception as e:
            logger.error(f"Ramp execution failed: {e}")
            return SegmentExecutionResult(
                segment_index=metadata.get("segment_index", 0) if metadata else 0,
                segment_type=segment.segment_type.value,
                from_asset=segment.from_asset,
                to_asset=segment.to_asset,
                from_network=segment.from_network,
                to_network=segment.to_network,
                status=SegmentExecutionStatus.FAILED,
                input_amount=input_amount,
                output_amount=0.0,
                fees_paid=0.0,
                provider=segment.provider,
                started_at=started_at,
                error_message=str(e)
            )


class BankRailExecutor(SegmentExecutor):
    """Execute bank rail segments"""
    
    async def execute(
        self,
        segment: RouteSegment,
        input_amount: float,
        wallet_address: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SegmentExecutionResult:
        """Execute bank transfer"""
        started_at = datetime.utcnow()
        
        try:
            # Real execution via Wise API
            if self.execution_mode == "real" and self.wise_client and segment.provider == "wise":
                try:
                    # Get target account details from metadata or use defaults
                    target_account = metadata.get("target_account", {}) if metadata else {}
                    
                    # Get profile ID
                    profiles = await self.wise_client.get_profiles()
                    if not profiles:
                        raise ValueError("No Wise profiles found")
                    profile_id = profiles[0]["id"]
                    
                    # Execute transfer via Wise
                    transfer_result = await self.wise_client.execute_bank_transfer(
                        from_currency=segment.from_asset,
                        to_currency=segment.to_asset,
                        amount=input_amount,
                        target_account_details=target_account,
                        profile_id=profile_id
                    )
                    
                    transfer_id = transfer_result.get("transfer_id")
                    
                    # Automatically fund the transfer
                    if transfer_id:
                        funding_result = await self.wise_client.fund_transfer(transfer_id, profile_id)
                        if funding_result:
                            logger.info(f"Wise transfer {transfer_id} funded successfully")
                    
                    output_amount = transfer_result.get("target_amount", 0.0)
                    fees = transfer_result.get("fee", 0.0)
                    
                    completed_at = datetime.utcnow()
                    # Wise transfers typically take 0.5-2 hours
                    confirmation_time = 60.0  # 1 hour average
                    
                    logger.info(f"Wise bank transfer completed: {segment.from_asset} -> {segment.to_asset}, "
                               f"{input_amount} -> {output_amount}")
                    
                    return SegmentExecutionResult(
                        segment_index=metadata.get("segment_index", 0) if metadata else 0,
                        segment_type=segment.segment_type.value,
                        from_asset=segment.from_asset,
                        to_asset=segment.to_asset,
                        status=SegmentExecutionStatus.COMPLETED,
                        input_amount=input_amount,
                        output_amount=output_amount,
                        fees_paid=fees,
                        provider=segment.provider,
                        started_at=started_at,
                        completed_at=completed_at,
                        confirmation_time_minutes=confirmation_time,
                        simulation_data={
                            "transfer_id": transfer_id,
                            "quote_id": transfer_result.get("quote_id"),
                            "fx_rate": transfer_result.get("rate", 1.0),
                            "type": "wise_bank_transfer",
                            "execution_mode": "real"
                        }
                    )
                except Exception as e:
                    logger.error(f"Wise API execution failed, falling back to simulation: {e}")
                    # Fall through to simulation
            
            # Simulation mode or fallback
            # Calculate fees and output amount with validation
            fee_percent = max(0.0, min(100.0, segment.cost.get("fee_percent", 0.0)))
            fixed_fee = max(0.0, segment.cost.get("fixed_fee", 0.0))
            fx_rate = segment.cost.get("effective_fx_rate", 1.0)
            
            if fx_rate <= 0:
                raise ValueError(f"Invalid FX rate: {fx_rate}")
            if input_amount < 0:
                raise ValueError(f"Invalid input amount: {input_amount}")
            
            fees = (input_amount * fee_percent / 100) + fixed_fee
            amount_after_fees = max(0.0, input_amount - fees)
            output_amount = amount_after_fees * fx_rate
            
            # Simulate bank transfer
            min_hours = segment.latency.get("min_minutes", 30) / 60.0
            max_hours = segment.latency.get("max_minutes", 120) / 60.0
            
            transfer_result = await self.simulator.simulate_bank_transfer(
                from_account=f"ACC-{uuid.uuid4().hex[:8].upper()}",
                to_account=f"ACC-{uuid.uuid4().hex[:8].upper()}",
                amount=output_amount,
                currency=segment.to_asset,
                min_hours=min_hours,
                max_hours=max_hours
            )
            
            completed_at = datetime.utcnow()
            processing_hours = transfer_result["processing_time_hours"]
            
            logger.info(f"Bank transfer completed (simulation): {segment.from_asset} -> {segment.to_asset}, "
                       f"{input_amount} -> {output_amount}")
            
            return SegmentExecutionResult(
                segment_index=metadata.get("segment_index", 0) if metadata else 0,
                segment_type=segment.segment_type.value,
                from_asset=segment.from_asset,
                to_asset=segment.to_asset,
                status=SegmentExecutionStatus.COMPLETED,
                input_amount=input_amount,
                output_amount=output_amount,
                fees_paid=fees,
                provider=segment.provider,
                started_at=started_at,
                completed_at=completed_at,
                confirmation_time_minutes=processing_hours * 60,
                simulation_data={
                    "transfer_id": transfer_result["transfer_id"],
                    "fx_rate": fx_rate,
                    "type": "bank_transfer",
                    "execution_mode": "simulation"
                }
            )
            
        except Exception as e:
            logger.error(f"Bank rail execution failed: {e}")
            return SegmentExecutionResult(
                segment_index=metadata.get("segment_index", 0) if metadata else 0,
                segment_type=segment.segment_type.value,
                from_asset=segment.from_asset,
                to_asset=segment.to_asset,
                status=SegmentExecutionStatus.FAILED,
                input_amount=input_amount,
                output_amount=0.0,
                fees_paid=0.0,
                provider=segment.provider,
                started_at=started_at,
                error_message=str(e)
            )

