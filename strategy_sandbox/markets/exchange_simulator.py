"""
Exchange simulator for sandbox testing.

Enhanced implementation with advanced market dynamics and slippage simulation for Phase 2.
"""

import math
import random
import uuid
from decimal import Decimal
from typing import Any

from strategy_sandbox.core.protocols import (
    BalanceProtocol,
    EventProtocol,
    MarketDynamicsConfig,
    MarketEvent,
    MarketRegime,
    Order,
    OrderBook,
    OrderCandidate,
    OrderSide,
    OrderStatus,
    OrderType,
    PriceType,
    SlippageConfig,
    SlippageModel,
    TradeFill,
)


class ExchangeSimulator:
    """Enhanced exchange simulator with advanced market dynamics and slippage simulation."""

    def __init__(
        self,
        balance_manager: BalanceProtocol,
        event_system: EventProtocol,
        slippage_config: SlippageConfig | None = None,
        market_dynamics_config: MarketDynamicsConfig | None = None,
    ):
        self._balance_manager = balance_manager
        self._event_system = event_system
        self._order_books: dict[str, OrderBook] = {}
        self._active_orders: dict[str, Order] = {}
        self._trading_pairs: list[str] = []
        self._current_timestamp = 0.0

        # Enhanced configurations for Phase 2
        self._slippage_config = slippage_config or SlippageConfig()
        self._market_dynamics_config = market_dynamics_config or MarketDynamicsConfig()

        # Market dynamics state
        self._price_history: dict[str, list[Decimal]] = {}
        self._volatility_cache: dict[str, Decimal] = {}
        self._last_order_book_update: dict[str, int] = {}
        self._pending_orders: dict[str, float] = {}  # Order ID -> processing completion time
        self._market_regimes: dict[str, MarketRegime] = {}

        # Enhanced statistics tracking
        self._order_count = 0
        self._fill_count = 0
        self._partial_fill_count = 0
        self._total_volume = Decimal("0")
        self._total_slippage = Decimal("0")
        self._trade_fills: list[TradeFill] = []

    async def add_trading_pair(self, trading_pair: str) -> None:
        """Add a trading pair to the simulator."""
        if trading_pair not in self._trading_pairs:
            self._trading_pairs.append(trading_pair)
            # Initialize with basic order book
            from strategy_sandbox.core.protocols import OrderBookLevel

            self._order_books[trading_pair] = OrderBook(
                trading_pair=trading_pair,
                bids=[OrderBookLevel(Decimal("100"), Decimal("1"))],
                asks=[OrderBookLevel(Decimal("101"), Decimal("1"))],
            )

    async def update_order_book(self, trading_pair: str, order_book: OrderBook) -> None:
        """Update order book for a trading pair."""
        self._order_books[trading_pair] = order_book

    async def process_tick(self, timestamp: float) -> None:
        """Process a simulation tick with enhanced market dynamics."""
        self._current_timestamp = timestamp

        # Update market dynamics for all trading pairs
        for trading_pair in self._trading_pairs:
            await self._update_market_dynamics(trading_pair)

        # Process pending orders (latency simulation)
        await self._process_pending_orders()

        # Process active orders for fills
        await self._process_orders()

    async def _process_pending_orders(self) -> None:
        """Process orders waiting for latency simulation."""
        completed_orders = []
        for order_id, completion_time in self._pending_orders.items():
            if self._current_timestamp >= completion_time:
                completed_orders.append(order_id)

        for order_id in completed_orders:
            del self._pending_orders[order_id]
            # Order is now ready for processing

    async def _process_orders(self) -> None:
        """Process active orders for fills."""
        for _order_id, order in list(self._active_orders.items()):
            if order.status == OrderStatus.OPEN and await self._should_fill_order(order):
                await self._fill_order(order)

    async def _should_fill_order(self, order: Order) -> bool:
        """Determine if an order should be filled with enhanced logic."""
        # Check if order is still in latency simulation
        if order.order_id in self._pending_orders:
            return False

        if order.trading_pair not in self._order_books:
            return False

        order_book = self._order_books[order.trading_pair]

        if order.order_type == OrderType.MARKET:
            return True

        if order.order_type == OrderType.LIMIT:
            if order.side == OrderSide.BUY and order_book.best_ask:
                return order.price >= order_book.best_ask
            elif order.side == OrderSide.SELL and order_book.best_bid:
                return order.price <= order_book.best_bid

        return False

    async def _fill_order(self, order: Order) -> None:
        """Fill an order with enhanced slippage and partial fill simulation."""
        order_book = self._order_books[order.trading_pair]

        # Get base fill price
        if order.order_type == OrderType.MARKET:
            base_price = order_book.best_ask if order.side == OrderSide.BUY else order_book.best_bid
        else:
            base_price = order.price

        if not base_price:
            return

        # Calculate slippage
        slippage_bps = self._calculate_slippage(order, order_book)
        fill_price = self._apply_slippage_to_price(base_price, slippage_bps, order.side)

        # Check for partial fills
        fill_amount, is_partial = self._check_partial_fill(order, order_book)

        if fill_amount <= Decimal("0"):
            return

        # Calculate market impact
        market_impact = (
            abs(fill_price - base_price) / base_price * Decimal("10000")
        )  # In basis points

        # Create trade fill record
        trade_fill = TradeFill(
            order_id=order.order_id,
            fill_price=fill_price,
            fill_amount=fill_amount,
            slippage_bps=slippage_bps,
            is_partial=is_partial,
            remaining_amount=order.amount - fill_amount if is_partial else Decimal("0"),
            market_impact=market_impact,
        )
        self._trade_fills.append(trade_fill)

        # Update order
        if is_partial:
            order.filled_amount += fill_amount
            order.amount -= fill_amount  # Reduce remaining amount
            self._partial_fill_count += 1
            if order.amount <= Decimal("0"):
                order.status = OrderStatus.FILLED
        else:
            order.status = OrderStatus.FILLED
            order.filled_amount = fill_amount

        # Update balances
        base_asset, quote_asset = order.trading_pair.split("-")
        if order.side == OrderSide.BUY:
            quote_amount = fill_amount * fill_price
            locked_amount = fill_amount * base_price  # Original locked amount
            self._balance_manager.unlock_balance(quote_asset, locked_amount)
            self._balance_manager.update_balance(quote_asset, -quote_amount)
            self._balance_manager.update_balance(base_asset, fill_amount)
        else:
            self._balance_manager.unlock_balance(base_asset, fill_amount)
            self._balance_manager.update_balance(base_asset, -fill_amount)
            self._balance_manager.update_balance(quote_asset, fill_amount * fill_price)

        # Update statistics
        self._fill_count += 1
        self._total_volume += fill_amount * fill_price
        self._total_slippage += slippage_bps

        # Emit events with enhanced data
        self._event_system.emit_event(
            MarketEvent.ORDER_FILLED,
            {
                "order_id": order.order_id,
                "trading_pair": order.trading_pair,
                "side": order.side.value,
                "amount": float(fill_amount),
                "price": float(fill_price),
                "slippage_bps": float(slippage_bps),
                "is_partial": is_partial,
                "market_impact": float(market_impact),
                "timestamp": self._current_timestamp,
            },
        )

        # Remove from active orders if fully filled
        if order.status == OrderStatus.FILLED:
            del self._active_orders[order.order_id]

    def _calculate_slippage(self, order: Order, order_book: OrderBook) -> Decimal:
        """Calculate slippage for an order based on market conditions."""
        if self._slippage_config.model == SlippageModel.LINEAR:
            return self._calculate_linear_slippage(order, order_book)
        elif self._slippage_config.model == SlippageModel.LOGARITHMIC:
            return self._calculate_logarithmic_slippage(order, order_book)
        elif self._slippage_config.model == SlippageModel.SQUARE_ROOT:
            return self._calculate_square_root_slippage(order, order_book)
        else:
            return self._slippage_config.base_slippage_bps

    def _calculate_linear_slippage(self, order: Order, order_book: OrderBook) -> Decimal:
        """Calculate linear slippage based on order size vs market depth."""
        if order.side == OrderSide.BUY:
            available_depth = sum(level.amount for level in order_book.asks[:5])  # Top 5 levels
        else:
            available_depth = sum(level.amount for level in order_book.bids[:5])  # Top 5 levels

        if available_depth == Decimal("0"):
            return self._slippage_config.max_slippage_bps

        depth_ratio = order.amount / available_depth
        depth_impact = depth_ratio * self._slippage_config.depth_impact_factor

        # Add volatility impact
        volatility = self._get_volatility(order.trading_pair)
        volatility_impact = (
            volatility * self._slippage_config.volatility_multiplier * Decimal("100")
        )

        total_slippage = self._slippage_config.base_slippage_bps + depth_impact + volatility_impact
        return min(total_slippage, self._slippage_config.max_slippage_bps)

    def _calculate_logarithmic_slippage(self, order: Order, order_book: OrderBook) -> Decimal:
        """Calculate logarithmic slippage for more realistic large order impact."""
        if order.side == OrderSide.BUY:
            available_depth = sum(level.amount for level in order_book.asks[:10])
        else:
            available_depth = sum(level.amount for level in order_book.bids[:10])

        if available_depth == Decimal("0"):
            return self._slippage_config.max_slippage_bps

        depth_ratio = order.amount / available_depth
        # Logarithmic scaling for more realistic impact
        log_impact = (
            Decimal(str(math.log(1 + float(depth_ratio))))
            * self._slippage_config.depth_impact_factor
            * Decimal("10")
        )

        volatility = self._get_volatility(order.trading_pair)
        volatility_impact = (
            volatility * self._slippage_config.volatility_multiplier * Decimal("100")
        )

        total_slippage = self._slippage_config.base_slippage_bps + log_impact + volatility_impact
        return min(total_slippage, self._slippage_config.max_slippage_bps)

    def _calculate_square_root_slippage(self, order: Order, order_book: OrderBook) -> Decimal:
        """Calculate square root slippage model."""
        if order.side == OrderSide.BUY:
            available_depth = sum(level.amount for level in order_book.asks[:10])
        else:
            available_depth = sum(level.amount for level in order_book.bids[:10])

        if available_depth == Decimal("0"):
            return self._slippage_config.max_slippage_bps

        depth_ratio = order.amount / available_depth
        sqrt_impact = (
            Decimal(str(math.sqrt(float(depth_ratio))))
            * self._slippage_config.depth_impact_factor
            * Decimal("5")
        )

        volatility = self._get_volatility(order.trading_pair)
        volatility_impact = (
            volatility * self._slippage_config.volatility_multiplier * Decimal("100")
        )

        total_slippage = self._slippage_config.base_slippage_bps + sqrt_impact + volatility_impact
        return min(total_slippage, self._slippage_config.max_slippage_bps)

    def _get_volatility(self, trading_pair: str) -> Decimal:
        """Calculate volatility for a trading pair."""
        if trading_pair not in self._price_history:
            return Decimal("0.001")  # Default volatility

        if trading_pair in self._volatility_cache:
            return self._volatility_cache[trading_pair]

        prices = self._price_history[trading_pair][-20:]  # Last 20 prices
        if len(prices) < 2:
            return Decimal("0.001")

        # Calculate standard deviation of returns
        returns = []
        for i in range(1, len(prices)):
            if prices[i - 1] != Decimal("0"):
                ret = (prices[i] - prices[i - 1]) / prices[i - 1]
                returns.append(float(ret))

        if not returns:
            return Decimal("0.001")

        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        volatility = Decimal(str(math.sqrt(variance)))

        self._volatility_cache[trading_pair] = volatility
        return volatility

    def _apply_slippage_to_price(
        self, price: Decimal, slippage_bps: Decimal, side: OrderSide
    ) -> Decimal:
        """Apply slippage to execution price."""
        slippage_factor = slippage_bps / Decimal("10000")  # Convert basis points to decimal

        if side == OrderSide.BUY:
            # Buying: slippage increases price
            return price * (Decimal("1") + slippage_factor)
        else:
            # Selling: slippage decreases price
            return price * (Decimal("1") - slippage_factor)

    def _check_partial_fill(self, order: Order, order_book: OrderBook) -> tuple[Decimal, bool]:
        """Check if order should be partially filled based on market depth."""
        if not self._slippage_config.enable_partial_fills:
            return order.amount, False

        available_levels = order_book.asks if order.side == OrderSide.BUY else order_book.bids

        available_amount = Decimal("0")
        for level in available_levels:
            if order.order_type == OrderType.LIMIT:
                if order.side == OrderSide.BUY and level.price > order.price:
                    break
                if order.side == OrderSide.SELL and level.price < order.price:
                    break

            available_amount += level.amount
            if available_amount >= order.amount:
                return order.amount, False

        # Partial fill scenario
        fill_amount = min(
            available_amount, order.amount * Decimal("0.8")
        )  # Fill up to 80% if available
        return fill_amount, fill_amount < order.amount

    async def _update_market_dynamics(self, trading_pair: str) -> None:
        """Update market dynamics including price movement and order book."""
        if trading_pair not in self._order_books:
            return

        # Update price history
        current_price = self.get_price(trading_pair, PriceType.MID)
        if trading_pair not in self._price_history:
            self._price_history[trading_pair] = []

        self._price_history[trading_pair].append(current_price)
        # Keep only last 100 prices
        if len(self._price_history[trading_pair]) > 100:
            self._price_history[trading_pair] = self._price_history[trading_pair][-100:]

        # Clear volatility cache periodically
        if len(self._price_history[trading_pair]) % 20 == 0:
            self._volatility_cache.pop(trading_pair, None)

        # Update market regime if needed
        self._update_market_regime(trading_pair)

        # Update order book if needed
        ticks_since_update = self._last_order_book_update.get(trading_pair, 0)
        if ticks_since_update >= self._market_dynamics_config.order_book_refresh_rate:
            await self._simulate_order_book_movement(trading_pair)
            self._last_order_book_update[trading_pair] = 0
        else:
            self._last_order_book_update[trading_pair] = ticks_since_update + 1

    def _update_market_regime(self, trading_pair: str) -> None:
        """Update market regime based on probability and trend analysis."""
        if random.random() < float(self._market_dynamics_config.regime_change_probability):
            # Regime change
            current_regime = self._market_regimes.get(trading_pair, MarketRegime.SIDEWAYS)
            new_regimes = [r for r in MarketRegime if r != current_regime]
            self._market_regimes[trading_pair] = random.choice(new_regimes)

    async def _simulate_order_book_movement(self, trading_pair: str) -> None:
        """Simulate realistic order book price movement."""
        if trading_pair not in self._order_books:
            return

        order_book = self._order_books[trading_pair]
        if not order_book.bids or not order_book.asks:
            return

        # Get current mid price for calculations
        current_mid = order_book.mid_price

        if not current_mid:
            return

        # Calculate price movement based on market dynamics
        regime = self._market_regimes.get(trading_pair, self._market_dynamics_config.regime)
        volatility = self._market_dynamics_config.price_volatility
        trend = self._market_dynamics_config.trend_strength

        # Generate price movement
        random_component = Decimal(str(random.gauss(0, float(volatility))))
        trend_component = trend * volatility

        # Regime-specific adjustments
        if regime == MarketRegime.TRENDING_UP:
            trend_component *= Decimal("2")
        elif regime == MarketRegime.TRENDING_DOWN:
            trend_component *= Decimal("-2")
        elif regime == MarketRegime.VOLATILE:
            random_component *= Decimal("3")

        price_change = random_component + trend_component
        new_mid = current_mid * (Decimal("1") + price_change)

        # Update order book with new prices
        spread_factor = (
            Decimal("0.001")
            if self._market_dynamics_config.enable_realistic_spreads
            else Decimal("0.0001")
        )
        new_bid = new_mid * (Decimal("1") - spread_factor)
        new_ask = new_mid * (Decimal("1") + spread_factor)

        # Create new order book levels
        from strategy_sandbox.core.protocols import OrderBookLevel

        new_order_book = OrderBook(
            trading_pair=trading_pair,
            bids=[
                OrderBookLevel(new_bid, Decimal("10")),
                OrderBookLevel(new_bid * Decimal("0.999"), Decimal("25")),
                OrderBookLevel(new_bid * Decimal("0.998"), Decimal("50")),
            ],
            asks=[
                OrderBookLevel(new_ask, Decimal("10")),
                OrderBookLevel(new_ask * Decimal("1.001"), Decimal("25")),
                OrderBookLevel(new_ask * Decimal("1.002"), Decimal("50")),
            ],
        )

        self._order_books[trading_pair] = new_order_book

    # MarketProtocol implementation
    def get_price(self, trading_pair: str, price_type: PriceType) -> Decimal:
        """Get current price for a trading pair."""
        if trading_pair not in self._order_books:
            return Decimal("0")

        order_book = self._order_books[trading_pair]
        if price_type == PriceType.BID:
            return order_book.best_bid or Decimal("0")
        elif price_type == PriceType.ASK:
            return order_book.best_ask or Decimal("0")
        elif price_type == PriceType.MID:
            return order_book.mid_price or Decimal("0")
        else:
            return order_book.mid_price or Decimal("0")

    def get_order_book(self, trading_pair: str) -> OrderBook:
        """Get current order book for a trading pair."""
        return self._order_books.get(trading_pair)

    def get_trading_pairs(self) -> list[str]:
        """Get list of available trading pairs."""
        return self._trading_pairs.copy()

    @property
    def current_timestamp(self) -> float:
        """Get current market timestamp."""
        return self._current_timestamp

    # OrderProtocol implementation
    def place_order(self, order_candidate: OrderCandidate) -> str:
        """Place an order and return order ID."""
        order_id = str(uuid.uuid4())

        # Validate and lock balances
        base_asset, quote_asset = order_candidate.trading_pair.split("-")

        if order_candidate.side == OrderSide.BUY:
            if order_candidate.order_type == OrderType.MARKET:
                # For market orders, estimate required amount
                order_book = self._order_books.get(order_candidate.trading_pair)
                price = order_book.best_ask if order_book else Decimal("100")
            else:
                price = order_candidate.price

            required_amount = order_candidate.amount * price
            if not self._balance_manager.lock_balance(quote_asset, required_amount):
                return None  # Insufficient balance
        else:
            if not self._balance_manager.lock_balance(base_asset, order_candidate.amount):
                return None  # Insufficient balance

        # Create order
        order = Order(
            order_id=order_id,
            trading_pair=order_candidate.trading_pair,
            side=order_candidate.side,
            order_type=order_candidate.order_type,
            amount=order_candidate.amount,
            price=order_candidate.price,
            status=OrderStatus.OPEN,
        )

        self._active_orders[order_id] = order
        self._order_count += 1

        # Add latency simulation
        latency_seconds = float(self._market_dynamics_config.latency_ms) / 1000.0
        completion_time = self._current_timestamp + latency_seconds
        self._pending_orders[order_id] = completion_time

        # Emit event
        self._event_system.emit_event(
            MarketEvent.ORDER_CREATED,
            {
                "order_id": order_id,
                "trading_pair": order_candidate.trading_pair,
                "side": order_candidate.side.value,
                "order_type": order_candidate.order_type.value,
                "amount": float(order_candidate.amount),
                "price": float(order_candidate.price) if order_candidate.price else None,
                "latency_ms": float(self._market_dynamics_config.latency_ms),
                "timestamp": self._current_timestamp,
            },
        )

        return order_id

    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order."""
        if order_id not in self._active_orders:
            return False

        order = self._active_orders[order_id]
        order.status = OrderStatus.CANCELLED

        # Unlock balances
        base_asset, quote_asset = order.trading_pair.split("-")
        if order.side == OrderSide.BUY:
            price = order.price or self.get_price(order.trading_pair, PriceType.ASK)
            self._balance_manager.unlock_balance(quote_asset, order.amount * price)
        else:
            self._balance_manager.unlock_balance(base_asset, order.amount)

        # Emit event
        self._event_system.emit_event(
            MarketEvent.ORDER_CANCELLED,
            {
                "order_id": order_id,
                "timestamp": self._current_timestamp,
            },
        )

        del self._active_orders[order_id]
        return True

    def get_order(self, order_id: str) -> Order | None:
        """Get order by ID."""
        return self._active_orders.get(order_id)

    def get_open_orders(self, trading_pair: str | None = None) -> list[Order]:
        """Get open orders, optionally filtered by trading pair."""
        orders = [
            order for order in self._active_orders.values() if order.status == OrderStatus.OPEN
        ]

        if trading_pair:
            orders = [order for order in orders if order.trading_pair == trading_pair]

        return orders

    def get_order_statistics(self) -> dict[str, Any]:
        """Get enhanced order statistics including slippage and market dynamics."""
        avg_slippage = (
            float(self._total_slippage / self._fill_count) if self._fill_count > 0 else 0.0
        )

        return {
            "total_orders": self._order_count,
            "total_fills": self._fill_count,
            "partial_fills": self._partial_fill_count,
            "total_volume": float(self._total_volume),
            "active_orders": len(self._active_orders),
            "pending_orders": len(self._pending_orders),
            "average_slippage_bps": avg_slippage,
            "total_slippage_bps": float(self._total_slippage),
            "trade_fills": len(self._trade_fills),
        }

    def get_slippage_statistics(self) -> dict[str, Any]:
        """Get detailed slippage statistics."""
        if not self._trade_fills:
            return {"message": "No trade fills recorded"}

        slippages = [float(fill.slippage_bps) for fill in self._trade_fills]
        market_impacts = [float(fill.market_impact) for fill in self._trade_fills]

        return {
            "total_fills": len(self._trade_fills),
            "partial_fills": sum(1 for fill in self._trade_fills if fill.is_partial),
            "average_slippage_bps": sum(slippages) / len(slippages),
            "max_slippage_bps": max(slippages),
            "min_slippage_bps": min(slippages),
            "average_market_impact_bps": sum(market_impacts) / len(market_impacts),
            "max_market_impact_bps": max(market_impacts),
        }

    def get_market_dynamics_status(self) -> dict[str, Any]:
        """Get current market dynamics status."""
        return {
            "trading_pairs": len(self._trading_pairs),
            "market_regimes": {tp: regime.value for tp, regime in self._market_regimes.items()},
            "price_history_length": {tp: len(hist) for tp, hist in self._price_history.items()},
            "volatility_cache": {tp: float(vol) for tp, vol in self._volatility_cache.items()},
            "slippage_config": {
                "model": self._slippage_config.model.value,
                "base_slippage_bps": float(self._slippage_config.base_slippage_bps),
                "enable_partial_fills": self._slippage_config.enable_partial_fills,
            },
            "market_dynamics_config": {
                "price_volatility": float(self._market_dynamics_config.price_volatility),
                "trend_strength": float(self._market_dynamics_config.trend_strength),
                "regime": self._market_dynamics_config.regime.value,
                "latency_ms": float(self._market_dynamics_config.latency_ms),
            },
        }

    def reset(self) -> None:
        """Reset simulator state including enhanced market dynamics."""
        self._active_orders.clear()
        self._order_books.clear()
        self._trading_pairs.clear()
        self._current_timestamp = 0.0

        # Reset enhanced state
        self._price_history.clear()
        self._volatility_cache.clear()
        self._last_order_book_update.clear()
        self._pending_orders.clear()
        self._market_regimes.clear()
        self._trade_fills.clear()

        # Reset statistics
        self._order_count = 0
        self._fill_count = 0
        self._partial_fill_count = 0
        self._total_volume = Decimal("0")
        self._total_slippage = Decimal("0")

    # Position management methods (for derivatives support)
    def get_position(self, trading_pair: str) -> dict[str, Any] | None:
        """Get position for a trading pair."""
        # Basic implementation - return None for spot trading
        return None

    def get_all_positions(self) -> dict[str, dict[str, Any]]:
        """Get all positions."""
        # Basic implementation - return empty dict for spot trading
        return {}

    def set_leverage(self, trading_pair: str, leverage: int) -> bool:
        """Set leverage for a trading pair."""
        # Basic implementation - not supported in spot trading
        return False
