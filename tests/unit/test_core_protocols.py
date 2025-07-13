"""Test suite for core protocols module."""

from decimal import Decimal

from strategy_sandbox.core.protocols import (
    Order,
    OrderBook,
    OrderBookLevel,
    OrderCandidate,
    OrderSide,
    OrderStatus,
    OrderType,
)


class TestOrderCandidate:
    """Test cases for OrderCandidate."""

    def test_order_candidate_creation(self):
        """Test basic order candidate creation."""
        order = OrderCandidate(
            symbol="BTCUSD",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("1.0"),
        )
        assert order.symbol == "BTCUSD"
        assert order.side == OrderSide.BUY
        assert order.order_type == OrderType.MARKET
        assert order.quantity == Decimal("1.0")
        assert order.price is None
        assert order.status == OrderStatus.PENDING

    def test_order_candidate_with_price(self):
        """Test order candidate with price."""
        order = OrderCandidate(
            symbol="ETHUSD",
            side=OrderSide.SELL,
            order_type=OrderType.LIMIT,
            quantity=Decimal("2.0"),
            price=Decimal("3000.0"),
        )
        assert order.price == Decimal("3000.0")
        assert order.order_type == OrderType.LIMIT


class TestOrderBookLevel:
    """Test cases for OrderBookLevel."""

    def test_order_book_level_creation(self):
        """Test basic order book level creation."""
        level = OrderBookLevel(price=Decimal("50000.0"), amount=Decimal("1.5"))
        assert level.price == Decimal("50000.0")
        assert level.amount == Decimal("1.5")


class TestOrderBook:
    """Test cases for OrderBook."""

    def test_order_book_creation(self):
        """Test basic order book creation."""
        bids = [OrderBookLevel(Decimal("50000.0"), Decimal("1.0"))]
        asks = [OrderBookLevel(Decimal("50100.0"), Decimal("1.0"))]

        book = OrderBook(bids=bids, asks=asks)
        assert len(book.bids) == 1
        assert len(book.asks) == 1
        assert book.best_bid() == Decimal("50000.0")
        assert book.best_ask() == Decimal("50100.0")
        assert book.mid_price() == Decimal("50050.0")


class TestOrder:
    """Test cases for Order."""

    def test_order_creation(self):
        """Test basic order creation."""
        order = Order(
            order_id="12345",
            trading_pair="BTCUSD",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            amount=Decimal("1.0"),
            price=Decimal("50000.0"),
            status=OrderStatus.OPEN,
        )
        assert order.order_id == "12345"
        assert order.trading_pair == "BTCUSD"
        assert order.side == OrderSide.BUY
        assert order.order_type == OrderType.LIMIT
        assert order.amount == Decimal("1.0")
        assert order.price == Decimal("50000.0")
        assert order.status == OrderStatus.OPEN


class TestEnums:
    """Test cases for protocol enums."""

    def test_order_type_enum(self):
        """Test OrderType enum values."""
        assert OrderType.MARKET == "market"
        assert OrderType.LIMIT == "limit"
        assert OrderType.STOP == "stop"
        assert OrderType.STOP_LIMIT == "stop_limit"

    def test_order_side_enum(self):
        """Test OrderSide enum values."""
        assert OrderSide.BUY == "buy"
        assert OrderSide.SELL == "sell"

    def test_order_status_enum(self):
        """Test OrderStatus enum values."""
        assert OrderStatus.PENDING == "pending"
        assert OrderStatus.OPEN == "open"
        assert OrderStatus.FILLED == "filled"
        assert OrderStatus.CANCELLED == "cancelled"
        assert OrderStatus.REJECTED == "rejected"
