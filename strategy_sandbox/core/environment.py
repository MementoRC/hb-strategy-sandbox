"""
Main sandbox environment that orchestrates all components.

The SandboxEnvironment provides the central coordination point for all sandbox
components and provides a simple API for strategy testing.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

from strategy_sandbox.balance.manager import SandboxBalanceManager
from strategy_sandbox.core.protocols import (
    BalanceProtocol,
    DataProviderProtocol,
    EventProtocol,
    MarketProtocol,
    OrderProtocol,
    PositionProtocol,
    StrategyProtocol,
)
from strategy_sandbox.data.providers import SimpleDataProvider
from strategy_sandbox.events.system import SandboxEventSystem
from strategy_sandbox.markets.exchange_simulator import ExchangeSimulator


class SandboxConfiguration:
    """Configuration for sandbox environment."""

    def __init__(
        self,
        initial_balances: dict[str, Decimal] | None = None,
        trading_pairs: list[str] | None = None,
        start_timestamp: float | None = None,
        end_timestamp: float | None = None,
        tick_interval: float = 1.0,  # seconds
        enable_derivatives: bool = False,
    ):
        """Initialize SandboxConfiguration.

        :param initial_balances: Initial balances for assets.
        :param trading_pairs: List of trading pairs to simulate.
        :param start_timestamp: Starting timestamp for the simulation.
        :param end_timestamp: Ending timestamp for the simulation.
        :param tick_interval: Interval between simulation ticks in seconds.
        :param enable_derivatives: Whether to enable derivatives trading.
        """
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
        config: SandboxConfiguration | None = None,
        data_provider: DataProviderProtocol | None = None,
    ):
        """Initialize the SandboxEnvironment.

        :param config: Configuration for the sandbox environment.
        :param data_provider: Data provider for historical market data.
        """
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
        self._strategies: list[StrategyProtocol] = []
        self._initialized = False

        # Performance tracking
        self._performance_metrics: dict[str, Any] = {}

    async def initialize(self) -> None:
        """Initialize the sandbox environment.

        :return: None
        """
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
        if hasattr(self._data_provider, "initialize") and callable(
            getattr(self._data_provider, "initialize", None)
        ):
            await self._data_provider.initialize()  # type: ignore

        self._initialized = True
        self.logger.info("Sandbox environment initialized")

    def add_strategy(self, strategy: StrategyProtocol) -> None:
        """Add a strategy to the sandbox.

        :param strategy: The strategy to add.
        """
        strategy.initialize(self)
        self._strategies.append(strategy)
        self.logger.info(f"Added strategy: {strategy.__class__.__name__}")

    def remove_strategy(self, strategy: StrategyProtocol) -> None:
        """Remove a strategy from the sandbox.

        :param strategy: The strategy to remove.
        """
        if strategy in self._strategies:
            strategy.cleanup()
            self._strategies.remove(strategy)
            self.logger.info(f"Removed strategy: {strategy.__class__.__name__}")

    async def run(
        self,
        duration: timedelta | float | None = None,
        until_timestamp: float | None = None,
    ) -> dict[str, Any]:
        """Run the sandbox simulation.

        :param duration: How long to run the simulation.
        :param until_timestamp: Run until this timestamp.
        :return: Performance metrics and results.
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

    async def step(self, timestamp: float) -> None:
        """Advance simulation by one step.

        :param timestamp: The timestamp to advance to.
        """
        self._current_timestamp = timestamp
        await self._simulation_step()

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
            if hasattr(self._data_provider, "get_order_book_snapshot"):
                order_book = await self._data_provider.get_order_book_snapshot(  # type: ignore
                    trading_pair,
                    datetime.fromtimestamp(self._current_timestamp),
                )
                if order_book:
                    await self._exchange_simulator.update_order_book(trading_pair, order_book)

    def stop(self) -> None:
        """Stop the simulation.

        :return: None
        """
        self._is_running = False
        self.logger.info("Simulation stopped")

    def reset(self) -> None:
        """Reset sandbox to initial state.

        :return: None
        """
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
        """Calculate performance metrics.

        :return: None
        """
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
        """Get market protocol instance.

        :return: The MarketProtocol instance.
        """
        return self._exchange_simulator

    @property
    def balance(self) -> BalanceProtocol:
        """Get balance protocol instance.

        :return: The BalanceProtocol instance.
        """
        return self._balance_manager

    @property
    def order(self) -> OrderProtocol:
        """Get order protocol instance.

        :return: The OrderProtocol instance.
        """
        return self._exchange_simulator

    @property
    def event(self) -> EventProtocol:
        """Get event protocol instance.

        :return: The EventProtocol instance.
        """
        return self._event_system

    @property
    def position(self) -> PositionProtocol | None:
        """Get position protocol instance.

        :return: The PositionProtocol instance, or None if derivatives are not enabled.
        """
        if self.config.enable_derivatives:
            return self._exchange_simulator
        return None

    @property
    def current_timestamp(self) -> float:
        """Get current simulation timestamp.

        :return: The current simulation timestamp as a float.
        """
        return self._current_timestamp

    @property
    def performance_metrics(self) -> dict[str, Any]:
        """Get current performance metrics.

        :return: A dictionary containing the performance metrics.
        """
        return self._performance_metrics.copy()

    @property
    def is_running(self) -> bool:
        """Check if simulation is running.

        :return: True if the simulation is running, False otherwise.
        """
        return self._is_running
