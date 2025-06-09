"""
Basic functionality tests to verify CI pipeline.
"""

import pytest
from decimal import Decimal

from strategy_sandbox.core.protocols import OrderCandidate, OrderSide, OrderType, PriceType


class TestBasicFunctionality:
    """Test basic package functionality."""

    def test_package_imports(self):
        """Test that package imports work correctly."""
        from strategy_sandbox import SandboxEnvironment
        from strategy_sandbox.core import SandboxConfiguration

        # Should be able to create instances
        config = SandboxConfiguration()
        sandbox = SandboxEnvironment(config=config)

        assert sandbox is not None
        assert config is not None

    def test_order_candidate_creation(self):
        """Test OrderCandidate creation."""
        order = OrderCandidate(
            trading_pair="BTC-USDT",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            amount=Decimal("1.0"),
        )

        assert order.trading_pair == "BTC-USDT"
        assert order.side == OrderSide.BUY
        assert order.order_type == OrderType.MARKET
        assert order.amount == Decimal("1.0")

    def test_enum_values(self):
        """Test enum value consistency."""
        assert OrderSide.BUY.value == "buy"
        assert OrderSide.SELL.value == "sell"
        assert OrderType.MARKET.value == "market"
        assert OrderType.LIMIT.value == "limit"
        assert PriceType.MID.value == "mid"
        assert PriceType.BID.value == "bid"
        assert PriceType.ASK.value == "ask"

    def test_decimal_arithmetic(self):
        """Test decimal arithmetic works correctly."""
        amount1 = Decimal("1.5")
        amount2 = Decimal("2.5")

        result = amount1 + amount2
        assert result == Decimal("4.0")

        result = amount1 * amount2
        assert result == Decimal("3.75")

    @pytest.mark.asyncio
    async def test_async_functionality(self):
        """Test async functionality works."""
        from strategy_sandbox import SandboxEnvironment
        from strategy_sandbox.core import SandboxConfiguration

        config = SandboxConfiguration(
            initial_balances={"USDT": Decimal("1000")},
        )
        sandbox = SandboxEnvironment(config=config)

        # Test async initialization
        await sandbox.initialize()

        # Test balance access
        balance = sandbox.balance.get_balance("USDT")
        assert balance == Decimal("1000")

        # Test async step
        initial_timestamp = sandbox.current_timestamp
        await sandbox.step()
        assert sandbox.current_timestamp > initial_timestamp
