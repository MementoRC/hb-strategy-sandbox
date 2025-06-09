"""
Main sandbox environment that orchestrates all components.

The SandboxEnvironment provides the central coordination point for all sandbox
components and provides a simple API for strategy testing.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Union

from strategy_sandbox.core.protocols import (
    BalanceProtocol,
    DataProviderProtocol,
    EventProtocol,
    MarketProtocol,
    OrderProtocol,
    PositionProtocol,
    SandboxProtocol,
    StrategyProtocol,
)
from strategy_sandbox.balance.manager import SandboxBalanceManager
from strategy_sandbox.events.system import SandboxEventSystem
from strategy_sandbox.markets.exchange_simulator import ExchangeSimulator
from strategy_sandbox.data.providers import SimpleDataProvider


class SandboxConfiguration:
    """Configuration for sandbox environment."""
    
    def __init__(
        self,
        initial_balances: Optional[Dict[str, Decimal]] = None,
        trading_pairs: Optional[List[str]] = None,
        start_timestamp: Optional[float] = None,
        end_timestamp: Optional[float] = None,
        tick_interval: float = 1.0,  # seconds
        enable_derivatives: bool = False,
    ):
        self.initial_balances = initial_balances or {"USDT": Decimal("10000")}
        self.trading_pairs = trading_pairs or ["BTC-USDT", "ETH-USDT"]
        self.start_timestamp = start_timestamp or datetime.now().timestamp()
        self.end_timestamp = end_timestamp
        self.tick_interval = tick_interval
        self.enable_derivatives = enable_derivatives


class SandboxEnvironment:
    """
    Main sandbox environment for strategy testing and simulation.
    
    This class coordinates all sandbox components and provides a simple API
    for running trading strategies in a controlled environment.
    """
    
    def __init__(
        self,
        config: Optional[SandboxConfiguration] = None,
        data_provider: Optional[DataProviderProtocol] = None,
    ):
        self.config = config or SandboxConfiguration()
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self._balance_manager = SandboxBalanceManager()
        self._event_system = SandboxEventSystem()
        self._exchange_simulator = ExchangeSimulator(
            balance_manager=self._balance_manager,
            event_system=self._event_system,
        )
        self._data_provider = data_provider or SimpleDataProvider()
        
        # State
        self._current_timestamp = self.config.start_timestamp
        self._is_running = False
        self._strategies: List[StrategyProtocol] = []
        self._initialized = False
        
        # Performance tracking
        self._performance_metrics: Dict[str, Any] = {}
    
    async def initialize(self) -> None:
        """Initialize the sandbox environment."""
        if self._initialized:
            return
        
        self.logger.info("Initializing sandbox environment")
        
        # Initialize balances
        for asset, amount in self.config.initial_balances.items():
            self._balance_manager.set_balance(asset, amount)
        
        # Initialize trading pairs
        for trading_pair in self.config.trading_pairs:
            await self._exchange_simulator.add_trading_pair(trading_pair)
        
        # Initialize data provider
        if hasattr(self._data_provider, 'initialize'):
            await self._data_provider.initialize()
        
        self._initialized = True
        self.logger.info("Sandbox environment initialized")
    
    def add_strategy(self, strategy: StrategyProtocol) -> None:
        """Add a strategy to the sandbox."""
        strategy.initialize(self)
        self._strategies.append(strategy)
        self.logger.info(f"Added strategy: {strategy.__class__.__name__}")
    
    def remove_strategy(self, strategy: StrategyProtocol) -> None:
        """Remove a strategy from the sandbox."""
        if strategy in self._strategies:
            strategy.cleanup()
            self._strategies.remove(strategy)
            self.logger.info(f"Removed strategy: {strategy.__class__.__name__}")
    
    async def run(
        self,
        duration: Optional[Union[timedelta, float]] = None,
        until_timestamp: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Run the sandbox simulation.
        
        Args:
            duration: How long to run the simulation
            until_timestamp: Run until this timestamp
            
        Returns:
            Performance metrics and results
        """
        if not self._initialized:
            await self.initialize()
        
        # Determine end time
        end_time = self._current_timestamp
        if duration:
            if isinstance(duration, timedelta):
                end_time += duration.total_seconds()
            else:
                end_time += duration
        elif until_timestamp:
            end_time = until_timestamp
        elif self.config.end_timestamp:
            end_time = self.config.end_timestamp
        else:
            # Default to 24 hours
            end_time += 24 * 3600
        
        self.logger.info(f"Starting simulation from {self._current_timestamp} to {end_time}")
        self._is_running = True
        
        try:
            while self._current_timestamp < end_time and self._is_running:
                await self._simulation_step()
                self._current_timestamp += self.config.tick_interval
                
                # Small delay to prevent tight loop
                await asyncio.sleep(0.001)
        
        except Exception as e:
            self.logger.error(f"Simulation error: {e}")
            raise
        finally:
            self._is_running = False
        
        # Calculate final performance metrics
        self._calculate_performance_metrics()
        
        self.logger.info("Simulation completed")
        return self._performance_metrics
    
    async def step(self, timestamp: Optional[float] = None) -> None:
        """Advance simulation by one step."""
        if timestamp:
            self._current_timestamp = timestamp
        
        await self._simulation_step()
        
        if not timestamp:
            self._current_timestamp += self.config.tick_interval
    
    async def _simulation_step(self) -> None:
        """Execute one simulation step."""
        # Update market data
        await self._update_market_data()
        
        # Process exchange simulation
        await self._exchange_simulator.process_tick(self._current_timestamp)
        
        # Notify strategies
        for strategy in self._strategies:
            try:
                await strategy.on_tick(self._current_timestamp)
            except Exception as e:
                self.logger.error(f"Strategy {strategy.__class__.__name__} error: {e}")
        
        # Process events
        await self._event_system.process_events()
    
    async def _update_market_data(self) -> None:
        """Update market data from data provider."""
        for trading_pair in self.config.trading_pairs:
            # Get order book data if available
            if hasattr(self._data_provider, 'get_order_book_snapshot'):
                order_book = await self._data_provider.get_order_book_snapshot(
                    trading_pair,
                    datetime.fromtimestamp(self._current_timestamp),
                )
                if order_book:
                    await self._exchange_simulator.update_order_book(trading_pair, order_book)
    
    def stop(self) -> None:
        """Stop the simulation."""
        self._is_running = False
        self.logger.info("Simulation stopped")
    
    def reset(self) -> None:
        """Reset sandbox to initial state."""
        self._current_timestamp = self.config.start_timestamp
        self._is_running = False
        self._performance_metrics = {}
        
        # Reset components
        self._balance_manager.reset()
        self._exchange_simulator.reset()
        self._event_system.reset()
        
        # Reset balances
        for asset, amount in self.config.initial_balances.items():
            self._balance_manager.set_balance(asset, amount)
        
        self.logger.info("Sandbox reset to initial state")
    
    def _calculate_performance_metrics(self) -> None:
        """Calculate performance metrics."""
        # Get final balances
        final_balances = self._balance_manager.get_all_balances()
        initial_balances = self.config.initial_balances
        
        # Calculate PnL
        total_pnl = Decimal("0")
        for asset, final_amount in final_balances.items():
            initial_amount = initial_balances.get(asset, Decimal("0"))
            pnl = final_amount - initial_amount
            total_pnl += pnl  # Simplified - would need price conversion
        
        # Get order statistics
        order_stats = self._exchange_simulator.get_order_statistics()
        
        self._performance_metrics = {
            "duration_seconds": self._current_timestamp - self.config.start_timestamp,
            "initial_balances": {k: float(v) for k, v in initial_balances.items()},
            "final_balances": {k: float(v) for k, v in final_balances.items()},
            "total_pnl": float(total_pnl),
            "order_statistics": order_stats,
            "simulation_end_time": self._current_timestamp,
        }
    
    # Protocol implementations for strategies to use
    @property
    def market(self) -> MarketProtocol:
        """Get market protocol instance."""
        return self._exchange_simulator
    
    @property
    def balance(self) -> BalanceProtocol:
        """Get balance protocol instance."""
        return self._balance_manager
    
    @property
    def order(self) -> OrderProtocol:
        """Get order protocol instance."""
        return self._exchange_simulator
    
    @property
    def event(self) -> EventProtocol:
        """Get event protocol instance."""
        return self._event_system
    
    @property
    def position(self) -> Optional[PositionProtocol]:
        """Get position protocol instance."""
        if self.config.enable_derivatives:
            return self._exchange_simulator
        return None
    
    @property
    def current_timestamp(self) -> float:
        """Get current simulation timestamp."""
        return self._current_timestamp
    
    @property
    def performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return self._performance_metrics.copy()
    
    @property
    def is_running(self) -> bool:
        """Check if simulation is running."""
        return self._is_running