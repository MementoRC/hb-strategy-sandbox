"""
Simple strategy example demonstrating sandbox usage.

This example shows how to create a basic buy-low-sell-high strategy
and test it in the sandbox environment.
"""

import asyncio
from datetime import timedelta
from decimal import Decimal

from strategy_sandbox import SandboxEnvironment
from strategy_sandbox.core import (
    OrderCandidate,
    OrderSide,
    OrderType,
    PriceType,
    SandboxConfiguration,
)


class SimpleBuyLowSellHighStrategy:
    """A simple strategy that buys low and sells high."""

    def __init__(self, trading_pair: str = "BTC-USDT", spread_threshold: Decimal = Decimal("0.01")):
        self.trading_pair = trading_pair
        self.spread_threshold = spread_threshold
        self.sandbox = None
        self.position_size = Decimal("0")
        self.last_price = None

    def initialize(self, sandbox):
        """Initialize strategy with sandbox."""
        self.sandbox = sandbox
        print(f"Strategy initialized for {self.trading_pair}")

    async def on_tick(self, timestamp: float):
        """Called on each simulation tick."""
        if not self.sandbox:
            return

        # Get current price
        current_price = self.sandbox.market.get_price(self.trading_pair, PriceType.MID)
        if current_price == Decimal("0"):
            return

        # Check if we should buy or sell
        if self.last_price:
            price_change = (current_price - self.last_price) / self.last_price

            # Buy if price dropped by threshold and we don't have position
            if price_change <= -self.spread_threshold and self.position_size == Decimal("0"):
                await self._place_buy_order(current_price)

            # Sell if price increased by threshold and we have position
            elif price_change >= self.spread_threshold and self.position_size > Decimal("0"):
                await self._place_sell_order(current_price)

        self.last_price = current_price

    async def _place_buy_order(self, price: Decimal):
        """Place a buy order."""
        if not self.sandbox:
            return

        # Calculate amount to buy based on available balance
        quote_asset = self.trading_pair.split("-")[1]
        available_balance = self.sandbox.balance.get_available_balance(quote_asset)

        if available_balance > Decimal("100"):  # Keep some buffer
            amount = Decimal("0.1")  # Buy 0.1 BTC
            order_candidate = OrderCandidate(
                trading_pair=self.trading_pair,
                side=OrderSide.BUY,
                order_type=OrderType.MARKET,
                amount=amount,
            )

            order_id = self.sandbox.order.place_order(order_candidate)
            if order_id:
                self.position_size += amount
                print(f"Placed buy order: {amount} at ~{price}")

    async def _place_sell_order(self, price: Decimal):
        """Place a sell order."""
        if not self.sandbox:
            return

        if self.position_size > Decimal("0"):
            order_candidate = OrderCandidate(
                trading_pair=self.trading_pair,
                side=OrderSide.SELL,
                order_type=OrderType.MARKET,
                amount=self.position_size,
            )

            order_id = self.sandbox.order.place_order(order_candidate)
            if order_id:
                print(f"Placed sell order: {self.position_size} at ~{price}")
                self.position_size = Decimal("0")

    async def on_order_filled(self, order):
        """Called when an order is filled."""
        print(f"Order filled: {order.order_id}")

    async def on_balance_updated(self, asset: str, balance: Decimal):
        """Called when balance is updated."""
        pass

    def cleanup(self):
        """Cleanup strategy resources."""
        print("Strategy cleaned up")


async def main():
    """Run the simple strategy example."""
    print("Starting sandbox strategy example...")

    # Create sandbox configuration
    config = SandboxConfiguration(
        initial_balances={
            "USDT": Decimal("10000"),
            "BTC": Decimal("0"),
        },
        trading_pairs=["BTC-USDT"],
        tick_interval=1.0,  # 1 second per tick
    )

    # Create sandbox environment
    sandbox = SandboxEnvironment(config=config)

    # Create and add strategy
    strategy = SimpleBuyLowSellHighStrategy()
    sandbox.add_strategy(strategy)

    # Run simulation for 1 hour (3600 ticks)
    print("Running simulation...")
    results = await sandbox.run(duration=timedelta(hours=1))

    # Print results
    print("\nSimulation Results:")
    print(f"Duration: {results['duration_seconds']} seconds")
    print(f"Initial balances: {results['initial_balances']}")
    print(f"Final balances: {results['final_balances']}")
    print(f"Total PnL: {results['total_pnl']}")
    print(f"Order statistics: {results['order_statistics']}")


if __name__ == "__main__":
    asyncio.run(main())
