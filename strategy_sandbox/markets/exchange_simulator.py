"""
Exchange simulator for sandbox testing.

Simplified implementation for MVP functionality.
"""

import uuid
from decimal import Decimal
from typing import Any

from strategy_sandbox.core.protocols import (
    BalanceProtocol,
    EventProtocol,
    MarketEvent,
    Order,
    OrderBook,
    OrderCandidate,
    OrderSide,
    OrderStatus,
    OrderType,
    PriceType,
)


class ExchangeSimulator:
    """Simple exchange simulator for MVP."""

    def __init__(self, balance_manager: BalanceProtocol, event_system: EventProtocol):
        self._balance_manager = balance_manager
        self._event_system = event_system
        self._order_books: dict[str, OrderBook] = {}
        self._active_orders: dict[str, Order] = {}
        self._trading_pairs: list[str] = []
        self._current_timestamp = 0.0

        # Statistics tracking
        self._order_count = 0
        self._fill_count = 0
        self._total_volume = Decimal("0")

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
        """Process a simulation tick."""
        self._current_timestamp = timestamp
        await self._process_orders()

    async def _process_orders(self) -> None:
        """Process active orders for fills."""
        for order_id, order in list(self._active_orders.items()):
            if order.status == OrderStatus.OPEN:
                if await self._should_fill_order(order):
                    await self._fill_order(order)

    async def _should_fill_order(self, order: Order) -> bool:
        """Determine if an order should be filled (simplified logic)."""
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
        """Fill an order."""
        # Get fill price
        order_book = self._order_books[order.trading_pair]
        if order.order_type == OrderType.MARKET:
            fill_price = order_book.best_ask if order.side == OrderSide.BUY else order_book.best_bid
        else:
            fill_price = order.price

        if not fill_price:
            return

        # Update order
        order.status = OrderStatus.FILLED
        order.filled_amount = order.amount

        # Update balances
        base_asset, quote_asset = order.trading_pair.split("-")
        if order.side == OrderSide.BUY:
            quote_amount = order.amount * fill_price
            self._balance_manager.unlock_balance(quote_asset, quote_amount)
            self._balance_manager.update_balance(quote_asset, -quote_amount)
            self._balance_manager.update_balance(base_asset, order.amount)
        else:
            self._balance_manager.unlock_balance(base_asset, order.amount)
            self._balance_manager.update_balance(base_asset, -order.amount)
            self._balance_manager.update_balance(quote_asset, order.amount * fill_price)

        # Update statistics
        self._fill_count += 1
        self._total_volume += order.amount * fill_price

        # Emit events
        self._event_system.emit_event(
            MarketEvent.ORDER_FILLED,
            {
                "order_id": order.order_id,
                "trading_pair": order.trading_pair,
                "side": order.side.value,
                "amount": float(order.amount),
                "price": float(fill_price),
                "timestamp": self._current_timestamp,
            },
        )

        # Remove from active orders
        del self._active_orders[order.order_id]

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
        """Get order statistics."""
        return {
            "total_orders": self._order_count,
            "total_fills": self._fill_count,
            "total_volume": float(self._total_volume),
            "active_orders": len(self._active_orders),
        }

    def reset(self) -> None:
        """Reset simulator state."""
        self._active_orders.clear()
        self._order_books.clear()
        self._trading_pairs.clear()
        self._current_timestamp = 0.0
        self._order_count = 0
        self._fill_count = 0
        self._total_volume = Decimal("0")

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
