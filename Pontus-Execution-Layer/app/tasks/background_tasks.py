import asyncio
from typing import Optional
from app.services.aggregator_service import AggregatorService
from app.config import settings


class BackgroundTaskManager:
    def __init__(self):
        self.aggregator: Optional[AggregatorService] = None
        self.tasks: list = []
        self.running = False
    
    async def start(self):
        """Start all background tasks"""
        if self.running:
            return
        
        self.running = True
        self.aggregator = AggregatorService()
        
        # Load regulatory constraints at startup
        await self._load_regulatory_constraints()
        
        # Start fast refresh tasks (crypto, gas, bridges) - every 2s
        fast_task = asyncio.create_task(
            self._fast_refresh_loop()
        )
        self.tasks.append(fast_task)
        
        # Start slow refresh tasks (FX, bank rails, liquidity) - every 30-60s
        slow_task = asyncio.create_task(
            self._slow_refresh_loop()
        )
        self.tasks.append(slow_task)
        
        # Start full refresh loop - creates snapshots every 60s
        full_task = asyncio.create_task(
            self._full_refresh_loop()
        )
        self.tasks.append(full_task)
    
    async def _load_regulatory_constraints(self):
        """Load regulatory constraints at startup"""
        try:
            # Constraints are loaded when RegulatoryClient is initialized
            # This is just a placeholder for any additional startup logic
            pass
        except Exception as e:
            print(f"Error loading regulatory constraints: {e}")
    
    async def _fast_refresh_loop(self):
        """Fast refresh loop for crypto, gas, bridges (every 2s)"""
        while self.running:
            try:
                # Fetch crypto, gas, and bridge segments
                crypto_segments = await self.aggregator.clients["crypto"].fetch_segments()
                gas_segments = await self.aggregator.clients["gas"].fetch_segments()
                bridge_segments = await self.aggregator.clients["bridge"].fetch_segments()
                
                all_fast_segments = crypto_segments + gas_segments + bridge_segments
                
                # Cache and persist
                if all_fast_segments:
                    await self.aggregator.cache_segments(all_fast_segments)
                    await self.aggregator.persist_segments(all_fast_segments)
                
                await asyncio.sleep(settings.crypto_gas_bridge_interval)
            except Exception as e:
                print(f"Error in fast refresh loop: {e}")
                await asyncio.sleep(settings.crypto_gas_bridge_interval)
    
    async def _slow_refresh_loop(self):
        """Slow refresh loop for FX, bank rails, liquidity (every 30-60s)"""
        while self.running:
            try:
                # Fetch FX, bank rail, and liquidity segments
                fx_segments = await self.aggregator.clients["fx"].fetch_segments()
                bank_rail_segments = await self.aggregator.clients["bank_rail"].fetch_segments()
                liquidity_segments = await self.aggregator.clients["liquidity"].fetch_segments()
                
                all_slow_segments = fx_segments + bank_rail_segments + liquidity_segments
                
                # Cache and persist
                if all_slow_segments:
                    await self.aggregator.cache_segments(all_slow_segments)
                    await self.aggregator.persist_segments(all_slow_segments)
                
                await asyncio.sleep(settings.fx_bank_liquidity_interval)
            except Exception as e:
                print(f"Error in slow refresh loop: {e}")
                await asyncio.sleep(settings.fx_bank_liquidity_interval)
    
    async def _full_refresh_loop(self):
        """Full refresh loop - fetches all segments and creates snapshot"""
        while self.running:
            try:
                # Fetch all segments
                all_segments = await self.aggregator.fetch_all_segments()
                
                # Cache all segments
                await self.aggregator.cache_segments(all_segments)
                
                # Persist segments
                await self.aggregator.persist_segments(all_segments)
                
                # Create snapshot
                await self.aggregator.persist_snapshot(all_segments)
                
                # Wait 60 seconds before next full refresh
                await asyncio.sleep(60)
            except Exception as e:
                print(f"Error in full refresh loop: {e}")
                await asyncio.sleep(60)
    
    async def stop(self):
        """Stop all background tasks"""
        self.running = False
        
        # Cancel all tasks
        for task in self.tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)
        
        # Close aggregator
        if self.aggregator:
            await self.aggregator.close()
        
        self.tasks = []


# Global task manager instance
_task_manager: Optional[BackgroundTaskManager] = None


async def start_background_tasks():
    """Start background tasks"""
    global _task_manager
    _task_manager = BackgroundTaskManager()
    await _task_manager.start()


async def stop_background_tasks():
    """Stop background tasks"""
    global _task_manager
    if _task_manager:
        await _task_manager.stop()
        _task_manager = None

