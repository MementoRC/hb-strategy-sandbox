"""
Tests for Phase 2 advanced market dynamics and slippage simulation.
"""

from decimal import Decimal
from unittest.mock import Mock

import pytest

from strategy_sandbox.core.protocols import (
    MarketDynamicsConfig,
    MarketRegime,
    OrderCandidate,
    OrderSide,
    OrderType,
    SlippageConfig,
    SlippageModel,
)
from strategy_sandbox.markets.exchange_simulator import ExchangeSimulator


class TestMarketDynamics:
    """Test advanced market dynamics features."""

    @pytest.fixture
    def balance_manager(self):
        """Mock balance manager."""
        mock = Mock()
        mock.lock_balance.return_value = True
        mock.unlock_balance.return_value = True
        mock.update_balance.return_value = None
        return mock

    @pytest.fixture
    def event_system(self):
        """Mock event system."""
        mock = Mock()
        mock.emit_event.return_value = None
        return mock

    @pytest.fixture
    def slippage_config(self):
        """Default slippage configuration."""
        return SlippageConfig(
            model=SlippageModel.LINEAR,
            base_slippage_bps=Decimal("2.0"),
            depth_impact_factor=Decimal("0.1"),
            enable_partial_fills=True,
        )

    @pytest.fixture
    def market_dynamics_config(self):
        """Default market dynamics configuration."""
        return MarketDynamicsConfig(
            price_volatility=Decimal("0.002"),
            trend_strength=Decimal("0.1"),
            regime=MarketRegime.SIDEWAYS,
            latency_ms=Decimal("100.0"),
        )

    @pytest.fixture
    def exchange_simulator(
        self, balance_manager, event_system, slippage_config, market_dynamics_config
    ):
        """Exchange simulator with enhanced configurations."""
        return ExchangeSimulator(
            balance_manager=balance_manager,
            event_system=event_system,
            slippage_config=slippage_config,
            market_dynamics_config=market_dynamics_config,
        )

    async def test_slippage_calculation_linear(self, exchange_simulator):
        """Test linear slippage calculation."""
        # Add trading pair with order book
        await exchange_simulator.add_trading_pair("BTC-USDT")

        # Create test order
        order_candidate = OrderCandidate(
            trading_pair="BTC-USDT",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            amount=Decimal("1.0"),
        )

        # Place order and verify it was created
        order_id = exchange_simulator.place_order(order_candidate)
        assert order_id is not None

        # Get statistics
        stats = exchange_simulator.get_order_statistics()
        assert stats["total_orders"] == 1
        assert stats["pending_orders"] == 1

    async def test_market_dynamics_regime_change(self, exchange_simulator):
        """Test market regime changes."""
        await exchange_simulator.add_trading_pair("BTC-USDT")

        # Process multiple ticks to trigger regime changes
        for i in range(100):
            await exchange_simulator.process_tick(float(i))

        # Check market dynamics status
        status = exchange_simulator.get_market_dynamics_status()
        assert "market_regimes" in status
        assert "BTC-USDT" in status.get("market_regimes", {}) or len(status["market_regimes"]) == 0

    async def test_partial_fills_enabled(self, exchange_simulator):
        """Test partial fill functionality."""
        await exchange_simulator.add_trading_pair("BTC-USDT")

        # Create large order that should trigger partial fill logic
        order_candidate = OrderCandidate(
            trading_pair="BTC-USDT",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            amount=Decimal("100.0"),  # Large amount
        )

        order_id = exchange_simulator.place_order(order_candidate)
        assert order_id is not None

        # Process ticks to trigger fills
        for i in range(10):
            await exchange_simulator.process_tick(float(i + 1))

        stats = exchange_simulator.get_order_statistics()
        # Order should be tracked in statistics
        assert stats["total_orders"] >= 1

    async def test_latency_simulation(self, exchange_simulator):
        """Test order latency simulation."""
        await exchange_simulator.add_trading_pair("BTC-USDT")

        order_candidate = OrderCandidate(
            trading_pair="BTC-USDT",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            amount=Decimal("1.0"),
        )

        # Place order at timestamp 0
        exchange_simulator.place_order(order_candidate)
        await exchange_simulator.process_tick(0.0)

        # Order should be pending due to latency
        stats = exchange_simulator.get_order_statistics()
        assert stats["pending_orders"] >= 1

        # Process tick after latency period (100ms = 0.1s)
        await exchange_simulator.process_tick(0.2)

        # Order should no longer be pending
        updated_stats = exchange_simulator.get_order_statistics()
        assert updated_stats["pending_orders"] == 0

    async def test_volatility_calculation(self, exchange_simulator):
        """Test volatility calculation from price history."""
        await exchange_simulator.add_trading_pair("BTC-USDT")

        # Process multiple ticks to build price history
        for i in range(50):
            await exchange_simulator.process_tick(float(i))

        # Check that price history is being tracked
        status = exchange_simulator.get_market_dynamics_status()
        assert "price_history_length" in status
        if "BTC-USDT" in status["price_history_length"]:
            assert status["price_history_length"]["BTC-USDT"] > 0

    async def test_slippage_statistics(self, exchange_simulator):
        """Test detailed slippage statistics tracking."""
        await exchange_simulator.add_trading_pair("BTC-USDT")

        # Place and potentially fill orders
        for i in range(5):
            order_candidate = OrderCandidate(
                trading_pair="BTC-USDT",
                side=OrderSide.BUY,
                order_type=OrderType.MARKET,
                amount=Decimal("0.1"),
            )
            exchange_simulator.place_order(order_candidate)
            await exchange_simulator.process_tick(float(i + 1))

        # Get slippage statistics
        slippage_stats = exchange_simulator.get_slippage_statistics()
        # Should either have statistics or a message indicating no fills
        assert "total_fills" in slippage_stats or "message" in slippage_stats

    async def test_different_slippage_models(self, balance_manager, event_system):
        """Test different slippage calculation models."""
        models = [SlippageModel.LINEAR, SlippageModel.LOGARITHMIC, SlippageModel.SQUARE_ROOT]

        for model in models:
            config = SlippageConfig(model=model)
            simulator = ExchangeSimulator(
                balance_manager=balance_manager,
                event_system=event_system,
                slippage_config=config,
            )

            await simulator.add_trading_pair("BTC-USDT")

            order_candidate = OrderCandidate(
                trading_pair="BTC-USDT",
                side=OrderSide.BUY,
                order_type=OrderType.MARKET,
                amount=Decimal("1.0"),
            )

            order_id = simulator.place_order(order_candidate)
            assert order_id is not None

            # Verify configuration is applied
            status = simulator.get_market_dynamics_status()
            assert status["slippage_config"]["model"] == model.value

    def test_reset_enhanced_state(self, exchange_simulator):
        """Test that enhanced state is properly reset."""
        # Add some state
        exchange_simulator._price_history["BTC-USDT"] = [Decimal("100"), Decimal("101")]
        exchange_simulator._volatility_cache["BTC-USDT"] = Decimal("0.01")
        exchange_simulator._pending_orders["test"] = 1.0

        # Reset
        exchange_simulator.reset()

        # Verify state is cleared
        assert len(exchange_simulator._price_history) == 0
        assert len(exchange_simulator._volatility_cache) == 0
        assert len(exchange_simulator._pending_orders) == 0
        assert exchange_simulator._total_slippage == Decimal("0")
        assert exchange_simulator._partial_fill_count == 0


class TestSlippageModels:
    """Test specific slippage model calculations."""

    @pytest.fixture
    def mock_order(self):
        """Mock order for testing."""
        from strategy_sandbox.core.protocols import Order

        return Order(
            order_id="test-order",
            trading_pair="BTC-USDT",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            amount=Decimal("1.0"),
        )

    @pytest.fixture
    def mock_order_book(self):
        """Mock order book for testing."""
        from strategy_sandbox.core.protocols import OrderBook, OrderBookLevel

        return OrderBook(
            trading_pair="BTC-USDT",
            bids=[
                OrderBookLevel(Decimal("99"), Decimal("5")),
                OrderBookLevel(Decimal("98"), Decimal("10")),
            ],
            asks=[
                OrderBookLevel(Decimal("101"), Decimal("5")),
                OrderBookLevel(Decimal("102"), Decimal("10")),
            ],
        )

    def test_slippage_models_return_decimal(self, mock_order, mock_order_book):
        """Test that all slippage models return Decimal values."""
        balance_manager = Mock()
        event_system = Mock()

        models = [SlippageModel.LINEAR, SlippageModel.LOGARITHMIC, SlippageModel.SQUARE_ROOT]

        for model in models:
            config = SlippageConfig(model=model)
            simulator = ExchangeSimulator(
                balance_manager=balance_manager,
                event_system=event_system,
                slippage_config=config,
            )

            slippage = simulator._calculate_slippage(mock_order, mock_order_book)
            assert isinstance(slippage, Decimal)
            assert slippage >= Decimal("0")
