# Strategy Sandbox Examples

This section provides more advanced examples of how to leverage the HB Strategy Sandbox for developing and testing complex trading strategies. These examples build upon the [Getting Started](getting-started.md) guide and demonstrate various features of the sandbox.

## Example 1: Simple Market Making Strategy

This strategy places a buy and a sell limit order around the current mid-price, adjusting them as the market moves. It demonstrates continuous order placement and reaction to market price changes.

```python
from decimal import Decimal
import logging
import asyncio

from strategy_sandbox.core.protocols import StrategyProtocol, SandboxProtocol, PriceType, OrderSide, OrderType

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleMarketMakingStrategy(StrategyProtocol):
    """A simple market making strategy that places buy and sell orders around the mid-price."""

    def __init__(self, trading_pair: str = "BTC-USDT", spread_bps: Decimal = Decimal("10"), order_amount: Decimal = Decimal("0.01")):
        self.sandbox: SandboxProtocol | None = None
        self.trading_pair = trading_pair
        self.spread_bps = spread_bps
        self.order_amount = order_amount
        self.buy_order_id: str | None = None
        self.sell_order_id: str | None = None

    def initialize(self, sandbox: SandboxProtocol) -> None:
        """Initializes the strategy with the sandbox environment."""
        self.sandbox = sandbox
        logger.info(f"SimpleMarketMakingStrategy initialized for {self.trading_pair}.")

    async def on_tick(self, timestamp: float) -> None:
        """Called on each simulation tick. Manages order placement and cancellation."""
        if not self.sandbox: return

        # Cancel existing orders if they are still open
        await self._cancel_all_orders()

        # Get current mid-price
        mid_price = self.sandbox.market.get_price(self.trading_pair, PriceType.MID)
        if mid_price == Decimal("0"): # Handle cases where order book might be empty initially
            logger.warning(f"No mid-price for {self.trading_pair} at {timestamp}. Skipping tick.")
            return

        # Calculate bid and ask prices based on spread
        bid_price = mid_price * (Decimal("1") - self.spread_bps / Decimal("10000"))
        ask_price = mid_price * (Decimal("1") + self.spread_bps / Decimal("10000"))

        # Place buy order
        self.buy_order_id = self.sandbox.order.place_order(
            order_candidate=self.sandbox.order.OrderCandidate(
                trading_pair=self.trading_pair,
                side=OrderSide.BUY,
                order_type=OrderType.LIMIT,
                amount=self.order_amount,
                price=bid_price,
            )
        )
        if self.buy_order_id: logger.info(f"Placed BUY order {self.buy_order_id} at {bid_price} for {self.order_amount}")

        # Place sell order
        self.sell_order_id = self.sandbox.order.place_order(
            order_candidate=self.sandbox.order.OrderCandidate(
                trading_pair=self.trading_pair,
                side=OrderSide.SELL,
                order_type=OrderType.LIMIT,
                amount=self.order_amount,
                price=ask_price,
            )
        )
        if self.sell_order_id: logger.info(f"Placed SELL order {self.sell_order_id} at {ask_price} for {self.order_amount}")

    async def _cancel_all_orders(self):
        """Helper to cancel all active orders placed by this strategy."""
        if not self.sandbox: return
        open_orders = self.sandbox.order.get_open_orders(self.trading_pair)
        for order in open_orders:
            if order.order_id in [self.buy_order_id, self.sell_order_id]:
                success = self.sandbox.order.cancel_order(order.order_id)
                if success: logger.info(f"Cancelled order {order.order_id}")

    def on_order_filled(self, order) -> None:
        """Called when an order is filled."""
        logger.info(f"Order Filled: {order.order_id} - {order.amount} @ {order.price}")
        # Reset order IDs so new orders can be placed
        if order.order_id == self.buy_order_id: self.buy_order_id = None
        if order.order_id == self.sell_order_id: self.sell_order_id = None

    def on_balance_updated(self, asset: str, balance: Decimal) -> None:
        """Called when a balance is updated."""
        # logger.info(f"Balance Updated: {asset} - {balance}") # Uncomment for verbose balance updates
        pass

    def cleanup(self) -> None:
        """Cleans up strategy resources."""
        logger.info("SimpleMarketMakingStrategy cleaned up.")
        # In a real scenario, ensure all orders are cancelled on cleanup


# To run this strategy, use a similar `run_simulation.py` as in the Getting Started guide:
# from strategy_sandbox.core.environment import SandboxEnvironment, SandboxConfiguration
# from simple_market_making_strategy import SimpleMarketMakingStrategy
#
# async def main():
#     config = SandboxConfiguration(
#         initial_balances={"USDT": Decimal("10000"), "BTC": Decimal("1")},
#         trading_pairs=["BTC-USDT"],
#         tick_interval=10.0, # More frequent ticks for active trading
#     )
#     env = SandboxEnvironment(config=config)
#     await env.initialize()
#
#     strategy = SimpleMarketMakingStrategy(trading_pair="BTC-USDT", spread_bps=Decimal("20"), order_amount=Decimal("0.01"))
#     env.add_strategy(strategy)
#
#     print("Starting market making simulation...")
#     performance_metrics = await env.run(duration=timedelta(minutes=30)) # Run for 30 minutes
#     print("Simulation finished.")
#
#     print("\nPerformance Metrics:")
#     for key, value in performance_metrics.items():
#         print(f"  {key}: {value}")
#
# if __name__ == "__main__":
#     asyncio.run(main())
```

## Example 2: Arbitrage Strategy (Conceptual)

This conceptual example outlines an arbitrage strategy that monitors price differences between two simulated exchanges and attempts to profit from them. This would require extending the `ExchangeSimulator` or using multiple instances of it.

```python
# This is a conceptual example and requires further development of multi-exchange simulation.

from decimal import Decimal
import logging
import asyncio

from strategy_sandbox.core.protocols import StrategyProtocol, SandboxProtocol, PriceType, OrderSide, OrderType

logger = logging.getLogger(__name__)

class ConceptualArbitrageStrategy(StrategyProtocol):
    """A conceptual arbitrage strategy across two simulated exchanges."""

    def __init__(self, trading_pair: str = "ETH-USDT", min_profit_bps: Decimal = Decimal("5")):
        self.sandbox: SandboxProtocol | None = None
        self.trading_pair = trading_pair
        self.min_profit_bps = min_profit_bps
        self.exchange_a_id = "exchange_a" # Assuming multiple exchange simulators can be registered
        self.exchange_b_id = "exchange_b"

    def initialize(self, sandbox: SandboxProtocol) -> None:
        """Initializes the strategy with the sandbox environment."""
        self.sandbox = sandbox
        logger.info(f"ConceptualArbitrageStrategy initialized for {self.trading_pair}.")

    async def on_tick(self, timestamp: float) -> None:
        """Called on each simulation tick. Checks for arbitrage opportunities."""
        if not self.sandbox: return

        # In a real multi-exchange setup, you would get prices from different exchange instances
        # For this conceptual example, we'll simulate two different price feeds.
        price_a = self.sandbox.market.get_price(self.trading_pair, PriceType.ASK) # Assume Exchange A is where we buy
        price_b = self.sandbox.market.get_price(self.trading_pair, PriceType.BID) # Assume Exchange B is where we sell

        if price_a == Decimal("0") or price_b == Decimal("0"): return

        # Calculate potential profit
        # Buy on A, Sell on B
        potential_profit_bps = ((price_b - price_a) / price_a) * Decimal("10000")

        if potential_profit_bps >= self.min_profit_bps:
            logger.info(f"Arbitrage opportunity detected at {timestamp}!")
            logger.info(f"  Buy on A at {price_a}, Sell on B at {price_b}. Profit: {potential_profit_bps:.2f} bps")

            # Execute trades (conceptual - requires multi-exchange order placement)
            # self.sandbox.order.place_order(exchange_a_id, ...)
            # self.sandbox.order.place_order(exchange_b_id, ...)

    def on_order_filled(self, order) -> None:
        """Called when an order is filled."""
        logger.info(f"Arbitrage Trade Filled: {order.order_id} - {order.amount} @ {order.price}")

    def on_balance_updated(self, asset: str, balance: Decimal) -> None:
        """Called when a balance is updated."""
        pass

    def cleanup(self) -> None:
        """Cleans up strategy resources."""
        logger.info("ConceptualArbitrageStrategy cleaned up.")
```

## Example 3: Integrating Custom Data Provider (Conceptual)

This example demonstrates how you might integrate a custom data provider to feed specific historical data or synthetic data into your simulation. This requires implementing the `DataProviderProtocol`.

```python
# This is a conceptual example and requires implementing a custom data provider.

from datetime import datetime
from decimal import Decimal
from typing import Any, List, Dict

from strategy_sandbox.core.protocols import DataProviderProtocol, OrderBook, OrderBookLevel

class CustomHistoricalDataProvider(DataProviderProtocol):
    """A conceptual data provider that serves historical data from a predefined source."""

    def __init__(self, historical_data_source: List[Dict[str, Any]]):
        self.data_source = historical_data_source
        self.current_index = 0

    async def get_historical_data(
        self,
        trading_pair: str,
        start_time: datetime,
        end_time: datetime,
    ) -> List[Dict[str, Any]]:
        """Get historical market data within a specified range."""
        # In a real implementation, you would filter self.data_source by trading_pair and time range
        return [d for d in self.data_source if start_time <= d["timestamp"] <= end_time]

    async def get_order_book_snapshot(
        self,
        trading_pair: str,
        timestamp: datetime,
    ) -> OrderBook | None:
        """Get order book snapshot at a specific timestamp."""
        # For simplicity, let's return a static order book for now
        # In a real scenario, you'd look up the order book from your historical data
        if trading_pair == "BTC-USDT":
            return OrderBook(
                trading_pair=trading_pair,
                bids=[OrderBookLevel(Decimal("29999.5"), Decimal("0.5"))],
                asks=[OrderBookLevel(Decimal("30000.5"), Decimal("0.5"))],
                timestamp=timestamp
            )
        return None

# To use this, you would pass an instance to SandboxEnvironment:
# from strategy_sandbox.core.environment import SandboxEnvironment, SandboxConfiguration
# from custom_data_provider import CustomHistoricalDataProvider
#
# async def main():
#     # Example historical data (simplified)
#     historical_data = [
#         {"timestamp": datetime(2023, 1, 1, 10, 0, 0), "trading_pair": "BTC-USDT", "price": Decimal("30000")},
#         {"timestamp": datetime(2023, 1, 1, 10, 1, 0), "trading_pair": "BTC-USDT", "price": Decimal("30001")},
#         # ... more data
#     ]
#
#     custom_provider = CustomHistoricalDataProvider(historical_data)
#
#     config = SandboxConfiguration(
#         initial_balances={"USDT": Decimal("10000")},
#         trading_pairs=["BTC-USDT"],
#         tick_interval=60.0,
#     )
#
#     env = SandboxEnvironment(config=config, data_provider=custom_provider)
#     await env.initialize()
#
#     # Run simulation with your strategy
#     # ...
#
# if __name__ == "__main__":
#     asyncio.run(main())
```

These examples provide a starting point for building more sophisticated strategies and integrating custom components within the HB Strategy Sandbox. Remember to refer to the [API Reference](reference.md) for detailed information on available methods and classes.
