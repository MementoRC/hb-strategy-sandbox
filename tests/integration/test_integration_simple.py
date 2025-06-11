"""Simple integration tests for strategy sandbox workflow."""

from decimal import Decimal

import pytest

from strategy_sandbox.core.environment import SandboxConfiguration, SandboxEnvironment
from strategy_sandbox.core.protocols import MarketEvent, Order


class SimpleTestStrategy:
    """Simple test strategy for integration testing."""

    def __init__(self):
        self.tick_count = 0
        self.sandbox = None

    async def on_tick(self, timestamp: float) -> None:
        """Called on each simulation tick."""
        self.tick_count += 1

    def on_order_filled(self, order: Order) -> None:
        """Called when an order is filled."""
        pass

    def on_balance_updated(self, asset: str, balance: Decimal) -> None:
        """Called when balance is updated."""
        pass

    def initialize(self, sandbox) -> None:
        """Initialize strategy with sandbox."""
        self.sandbox = sandbox

    def cleanup(self) -> None:
        """Cleanup strategy resources."""
        pass


@pytest.mark.integration
class TestSimpleSandboxIntegration:
    """Test basic sandbox integration functionality."""

    @pytest.fixture
    def strategy(self):
        """Create test strategy."""
        return SimpleTestStrategy()

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return SandboxConfiguration(
            initial_balances={"USDT": Decimal("10000"), "BTC": Decimal("0")},
            trading_pairs=["BTC-USDT"],
            tick_interval=1.0,
        )

    @pytest.mark.asyncio
    async def test_environment_initialization(self, config):
        """Test basic environment initialization."""
        env = SandboxEnvironment(config=config)

        # Test initialization
        await env.initialize()
        assert env._initialized is True
        assert env.current_timestamp == config.start_timestamp

        # Test balance access through protocol
        usdt_balance = env.balance.get_balance("USDT")
        assert usdt_balance == Decimal("10000")

        btc_balance = env.balance.get_balance("BTC")
        assert btc_balance == Decimal("0")

    @pytest.mark.asyncio
    async def test_strategy_integration(self, strategy, config):
        """Test strategy integration with environment."""
        env = SandboxEnvironment(config=config)
        await env.initialize()

        # Add strategy
        env.add_strategy(strategy)
        assert len(env._strategies) == 1
        assert strategy.sandbox is env

        # Test strategy tick
        initial_tick_count = strategy.tick_count
        await env.step(config.start_timestamp + 1)
        assert strategy.tick_count == initial_tick_count + 1

    @pytest.mark.asyncio
    async def test_balance_protocol_integration(self, config):
        """Test balance protocol integration."""
        env = SandboxEnvironment(config=config)
        await env.initialize()

        balance_manager = env.balance

        # Test basic balance operations
        assert balance_manager.get_balance("USDT") == Decimal("10000")

        # Test balance update
        balance_manager.update_balance("USDT", Decimal("-1000"))
        assert balance_manager.get_balance("USDT") == Decimal("9000")

        # Test balance locking
        lock_result = balance_manager.lock_balance("USDT", Decimal("5000"))
        assert lock_result is True
        assert balance_manager.get_available_balance("USDT") == Decimal("4000")

        # Test unlock
        unlock_result = balance_manager.unlock_balance("USDT", Decimal("2000"))
        assert unlock_result is True
        assert balance_manager.get_available_balance("USDT") == Decimal("6000")

    @pytest.mark.asyncio
    async def test_event_system_integration(self, config):
        """Test event system integration."""
        env = SandboxEnvironment(config=config)
        await env.initialize()

        event_system = env.event

        # Test event emission
        test_data = {"test": "data"}
        event_system.emit_event(MarketEvent.ORDER_FILLED, test_data)

        # Test event processing (should not raise errors)
        await event_system.process_events()

        # Test subscription
        events_received = []

        def test_callback(data):
            events_received.append(data)

        sub_id = event_system.subscribe(MarketEvent.ORDER_FILLED, test_callback)
        assert isinstance(sub_id, str)

        # Emit and process event
        event_system.emit_event(MarketEvent.ORDER_FILLED, test_data)
        await event_system.process_events()

        assert len(events_received) == 1
        assert events_received[0] == test_data

        # Test unsubscribe
        unsubscribe_result = event_system.unsubscribe(sub_id)
        assert unsubscribe_result is True

    @pytest.mark.asyncio
    async def test_market_protocol_integration(self, config):
        """Test market protocol integration."""
        env = SandboxEnvironment(config=config)
        await env.initialize()

        market = env.market

        # Test trading pairs access
        trading_pairs = market.get_trading_pairs()
        assert "BTC-USDT" in trading_pairs

        # Test that we can access current timestamp (value may be 0 initially)
        timestamp = market.current_timestamp
        assert isinstance(timestamp, int | float)

    @pytest.mark.asyncio
    async def test_order_protocol_basic(self, config):
        """Test basic order protocol functionality."""
        env = SandboxEnvironment(config=config)
        await env.initialize()

        order_manager = env.order

        # Test get open orders (should be empty initially)
        open_orders = order_manager.get_open_orders()
        assert isinstance(open_orders, list)
        assert len(open_orders) == 0

        # Test get open orders for specific pair
        btc_orders = order_manager.get_open_orders("BTC-USDT")
        assert isinstance(btc_orders, list)
        assert len(btc_orders) == 0

    @pytest.mark.asyncio
    async def test_reset_functionality(self, strategy, config):
        """Test reset functionality across components."""
        env = SandboxEnvironment(config=config)
        await env.initialize()
        env.add_strategy(strategy)

        # Modify state
        env.balance.update_balance("USDT", Decimal("-1000"))
        initial_timestamp = env.current_timestamp
        await env.step(initial_timestamp + 10)

        # Verify state changed
        assert env.balance.get_balance("USDT") == Decimal("9000")
        assert env.current_timestamp > initial_timestamp
        assert strategy.tick_count > 0

        # Reset
        env.reset()

        # Verify reset
        assert env.balance.get_balance("USDT") == Decimal("10000")
        assert env.current_timestamp == config.start_timestamp
        # Note: strategy tick_count won't reset as it's not part of the environment reset

    @pytest.mark.asyncio
    async def test_simulation_step_integration(self, strategy, config):
        """Test full simulation step integration."""
        env = SandboxEnvironment(config=config)
        await env.initialize()
        env.add_strategy(strategy)

        initial_timestamp = env.current_timestamp
        initial_tick_count = strategy.tick_count

        # Execute simulation step
        await env.step(initial_timestamp + 1)

        # Verify step executed
        assert env.current_timestamp == initial_timestamp + 1
        assert strategy.tick_count == initial_tick_count + 1

    @pytest.mark.asyncio
    async def test_multiple_strategies_integration(self, config):
        """Test multiple strategies working together."""
        env = SandboxEnvironment(config=config)
        await env.initialize()

        # Create and add multiple strategies
        strategy1 = SimpleTestStrategy()
        strategy2 = SimpleTestStrategy()

        env.add_strategy(strategy1)
        env.add_strategy(strategy2)

        assert len(env._strategies) == 2
        assert strategy1.sandbox is env
        assert strategy2.sandbox is env

        # Execute step
        await env.step(config.start_timestamp + 1)

        # Both strategies should have been called
        assert strategy1.tick_count == 1
        assert strategy2.tick_count == 1

        # Remove one strategy
        env.remove_strategy(strategy1)
        assert len(env._strategies) == 1

        # Execute another step
        await env.step(config.start_timestamp + 2)

        # Only remaining strategy should have been called
        assert strategy1.tick_count == 1  # No change
        assert strategy2.tick_count == 2  # Incremented

    @pytest.mark.asyncio
    async def test_configuration_integration(self):
        """Test different configurations."""
        # Test custom configuration
        custom_config = SandboxConfiguration(
            initial_balances={"ETH": Decimal("100"), "USDT": Decimal("50000")},
            trading_pairs=["ETH-USDT", "BTC-USDT"],
            tick_interval=0.5,
        )

        env = SandboxEnvironment(config=custom_config)
        await env.initialize()

        # Verify configuration applied
        assert env.balance.get_balance("ETH") == Decimal("100")
        assert env.balance.get_balance("USDT") == Decimal("50000")

        trading_pairs = env.market.get_trading_pairs()
        assert "ETH-USDT" in trading_pairs
        assert "BTC-USDT" in trading_pairs

        assert env.config.tick_interval == 0.5

    @pytest.mark.asyncio
    async def test_performance_metrics_integration(self, strategy, config):
        """Test performance metrics calculation."""
        env = SandboxEnvironment(config=config)
        await env.initialize()
        env.add_strategy(strategy)

        # Modify balances to simulate trading
        env.balance.update_balance("USDT", Decimal("-5000"))
        env.balance.update_balance("BTC", Decimal("0.1"))

        # Advance time
        await env.step(config.start_timestamp + 100)

        # Calculate performance (simulating end of run)
        env._calculate_performance_metrics()

        metrics = env.performance_metrics
        assert "duration_seconds" in metrics
        assert "initial_balances" in metrics
        assert "final_balances" in metrics
        assert "total_pnl" in metrics

        # Verify balance tracking
        assert metrics["initial_balances"]["USDT"] == 10000.0
        assert metrics["final_balances"]["USDT"] == 5000.0
        assert metrics["final_balances"]["BTC"] == 0.1
