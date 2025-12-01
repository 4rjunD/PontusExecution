"""
Simulation Layer for Route Execution
Simulates wallets, balances, transactions, and confirmations without real accounts
"""
import asyncio
import random
import uuid
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class Simulator:
    """Simulates blockchain and banking operations"""
    
    def __init__(self):
        # Simulated wallet storage (in-memory for MVP)
        self.wallets: Dict[str, Dict[str, float]] = {}  # wallet_id -> {asset: balance}
        self.transactions: Dict[str, Dict[str, Any]] = {}  # tx_hash -> transaction data
        self.confirmations: Dict[str, int] = {}  # tx_hash -> confirmation count
        
    def generate_wallet(self, network: Optional[str] = None) -> str:
        """Generate a simulated wallet address"""
        wallet_id = f"0x{''.join(random.choices('0123456789abcdef', k=40))}"
        if wallet_id not in self.wallets:
            self.wallets[wallet_id] = {}
        logger.info(f"Generated simulated wallet: {wallet_id} for network: {network}")
        return wallet_id
    
    def get_balance(self, wallet_id: str, asset: str) -> float:
        """Get simulated balance for a wallet"""
        if wallet_id not in self.wallets:
            self.wallets[wallet_id] = {}
        return self.wallets[wallet_id].get(asset, 0.0)
    
    def set_balance(self, wallet_id: str, asset: str, amount: float):
        """Set simulated balance"""
        if wallet_id not in self.wallets:
            self.wallets[wallet_id] = {}
        self.wallets[wallet_id][asset] = amount
        logger.debug(f"Set balance: {wallet_id} {asset} = {amount}")
    
    def add_balance(self, wallet_id: str, asset: str, amount: float):
        """Add to simulated balance"""
        current = self.get_balance(wallet_id, asset)
        self.set_balance(wallet_id, asset, current + amount)
    
    def subtract_balance(self, wallet_id: str, asset: str, amount: float) -> bool:
        """Subtract from simulated balance (returns True if successful)"""
        current = self.get_balance(wallet_id, asset)
        if current >= amount:
            self.set_balance(wallet_id, asset, current - amount)
            return True
        return False
    
    def generate_transaction_hash(self) -> str:
        """Generate a simulated transaction hash"""
        return f"0x{''.join(random.choices('0123456789abcdef', k=64))}"
    
    def create_transaction(
        self,
        tx_type: str,
        from_address: Optional[str],
        to_address: Optional[str],
        asset: str,
        amount: float,
        network: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a simulated transaction"""
        tx_hash = self.generate_transaction_hash()
        self.transactions[tx_hash] = {
            "hash": tx_hash,
            "type": tx_type,
            "from_address": from_address,
            "to_address": to_address,
            "asset": asset,
            "amount": amount,
            "network": network,
            "status": "pending",
            "created_at": datetime.utcnow(),
            "confirmed_at": None,
            "confirmations": 0,
            "metadata": metadata or {}
        }
        self.confirmations[tx_hash] = 0
        logger.info(f"Created simulated transaction: {tx_hash} ({tx_type})")
        return tx_hash
    
    async def simulate_confirmation(
        self,
        tx_hash: str,
        min_blocks: int = 1,
        max_blocks: int = 3,
        block_time_seconds: float = 12.0
    ) -> Dict[str, Any]:
        """
        Simulate transaction confirmation
        Returns confirmation details
        """
        if tx_hash not in self.transactions:
            raise ValueError(f"Transaction {tx_hash} not found")
        
        tx = self.transactions[tx_hash]
        blocks_to_confirm = random.randint(min_blocks, max_blocks)
        confirmation_time = blocks_to_confirm * block_time_seconds
        
        # Simulate confirmation delay
        await asyncio.sleep(min(confirmation_time / 10, 0.5))  # Speed up simulation
        
        tx["status"] = "confirmed"
        tx["confirmed_at"] = datetime.utcnow()
        tx["confirmations"] = blocks_to_confirm
        self.confirmations[tx_hash] = blocks_to_confirm
        
        logger.info(f"Transaction {tx_hash} confirmed after {blocks_to_confirm} blocks")
        
        return {
            "transaction_hash": tx_hash,
            "confirmations": blocks_to_confirm,
            "confirmation_time_seconds": confirmation_time,
            "confirmed_at": tx["confirmed_at"]
        }
    
    async def simulate_bank_transfer(
        self,
        from_account: str,
        to_account: str,
        amount: float,
        currency: str,
        min_hours: float = 0.5,
        max_hours: float = 2.0
    ) -> Dict[str, Any]:
        """Simulate a bank transfer"""
        transfer_id = f"TRF-{uuid.uuid4().hex[:16].upper()}"
        
        # Simulate processing time
        processing_hours = random.uniform(min_hours, max_hours)
        await asyncio.sleep(min(processing_hours / 10, 1.0))  # Speed up simulation
        
        logger.info(f"Bank transfer {transfer_id} completed: {amount} {currency}")
        
        return {
            "transfer_id": transfer_id,
            "status": "completed",
            "amount": amount,
            "currency": currency,
            "processing_time_hours": processing_hours,
            "completed_at": datetime.utcnow()
        }
    
    async def simulate_fx_conversion(
        self,
        from_currency: str,
        to_currency: str,
        amount: float,
        rate: float,
        min_minutes: int = 5,
        max_minutes: int = 10
    ) -> Dict[str, Any]:
        """Simulate FX conversion"""
        conversion_id = f"FX-{uuid.uuid4().hex[:16].upper()}"
        output_amount = amount * rate
        
        # Simulate processing time
        processing_minutes = random.randint(min_minutes, max_minutes)
        await asyncio.sleep(min(processing_minutes / 60, 0.5))  # Speed up simulation
        
        logger.info(f"FX conversion {conversion_id}: {amount} {from_currency} -> {output_amount} {to_currency}")
        
        return {
            "conversion_id": conversion_id,
            "status": "completed",
            "input_amount": amount,
            "output_amount": output_amount,
            "from_currency": from_currency,
            "to_currency": to_currency,
            "rate": rate,
            "processing_time_minutes": processing_minutes,
            "completed_at": datetime.utcnow()
        }
    
    def get_transaction_status(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """Get status of a simulated transaction"""
        return self.transactions.get(tx_hash)

