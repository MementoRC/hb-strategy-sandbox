"""
Core protocols and interfaces for the strategy sandbox framework.

These protocols define the clean interfaces that sandbox components must implement,
ensuring compatibility and testability.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Optional, Protocol


class PriceType(Enum):
    """Price types for market data."""

    MID = "mid"
    BID = "bid"
    ASK = "ask"
    LAST = "last"
    MARK = "mark"


class OrderType(Enum):
    """Order types."""

    MARKET = "market"
    LIMIT = "limit"
    LIMIT_MAKER = "limit_maker"


class OrderSide(Enum):
    """Order sides."""

    BUY = "buy"
    SELL = "sell"


class OrderStatus(Enum):
    """Order status."""

    PENDING = "pending"
    OPEN = "open"
    FILLED = "filled"
    CANCELLED = "cancelled"
    FAILED = "failed"


class MarketEvent(Enum):
    """Market events."""

    ORDER_CREATED = "order_created"
    ORDER_FILLED = "order_filled"
    ORDER_CANCELLED = "order_cancelled"
    ORDER_FAILED = "order_failed"
    BALANCE_UPDATED = "balance_updated"
    PRICE_UPDATED = "price_updated"


class OrderCandidate:
    """Represents an order to be placed."""

    def __init__(
        self,
        trading_pair: str,
        side: OrderSide,
        order_type: OrderType,
        amount: Decimal,
        price: Decimal | None = None,
    ):
        self.trading_pair = trading_pair
        self.side = side
        self.order_type = order_type
        self.amount = amount
        self.price = price
        self.timestamp = datetime.now()


class Order:
    """Represents an order in the system."""

    def __init__(
        self,
        order_id: str,
        trading_pair: str,
        side: OrderSide,
        order_type: OrderType,
        amount: Decimal,
        price: Decimal | None = None,
        status: OrderStatus = OrderStatus.PENDING,
    ):
        self.order_id = order_id
        self.trading_pair = trading_pair
        self.side = side
        self.order_type = order_type
        self.amount = amount
        self.price = price
        self.status = status
        self.filled_amount = Decimal("0")
        self.created_at = datetime.now()
        self.updated_at = datetime.now()


class OrderBookLevel:
    """Represents a single level in the order book."""

    def __init__(self, price: Decimal, amount: Decimal):
        self.price = price
        self.amount = amount


class OrderBook:
    """Represents an order book snapshot."""

    def __init__(
        self,
        trading_pair: str,
        bids: list[OrderBookLevel],
        asks: list[OrderBookLevel],
        timestamp: datetime | None = None,
    ):
        self.trading_pair = trading_pair
        self.bids = sorted(bids, key=lambda x: x.price, reverse=True)  # Highest first
        self.asks = sorted(asks, key=lambda x: x.price)  # Lowest first
        self.timestamp = timestamp or datetime.now()

    @property
    def best_bid(self) -> Decimal | None:
        """Get the best bid price."""
        return self.bids[0].price if self.bids else None

    @property
    def best_ask(self) -> Decimal | None:
        """Get the best ask price."""
        return self.asks[0].price if self.asks else None

    @property
    def mid_price(self) -> Decimal | None:
        """Get the mid price."""
        if self.best_bid and self.best_ask:
            return (self.best_bid + self.best_ask) / Decimal("2")
        return None


class MarketProtocol(Protocol):
    """Protocol for market data and operations."""

    def get_price(self, trading_pair: str, price_type: PriceType) -> Decimal:
        """Get current price for a trading pair."""
        ...

    def get_order_book(self, trading_pair: str) -> OrderBook:
        """Get current order book for a trading pair."""
        ...

    def get_trading_pairs(self) -> list[str]:
        """Get list of available trading pairs."""
        ...

    @property
    def current_timestamp(self) -> float:
        """Get current market timestamp."""
        ...


class BalanceProtocol(Protocol):
    """Protocol for balance management."""

    def get_balance(self, asset: str) -> Decimal:
        """Get total balance for an asset."""
        ...

    def get_available_balance(self, asset: str) -> Decimal:
        """Get available balance for an asset."""
        ...

    def get_all_balances(self) -> dict[str, Decimal]:
        """Get all asset balances."""
        ...

    def lock_balance(self, asset: str, amount: Decimal) -> bool:
        """Lock balance for trading."""
        ...

    def unlock_balance(self, asset: str, amount: Decimal) -> bool:
        """Unlock previously locked balance."""
        ...

    def update_balance(self, asset: str, delta: Decimal) -> None:
        """Update balance by delta amount."""
        ...


class OrderProtocol(Protocol):
    """Protocol for order management."""

    def place_order(self, order_candidate: OrderCandidate) -> str:
        """Place an order and return order ID."""
        ...

    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order."""
        ...

    def get_order(self, order_id: str) -> Order | None:
        """Get order by ID."""
        ...

    def get_open_orders(self, trading_pair: str | None = None) -> list[Order]:
        """Get open orders, optionally filtered by trading pair."""
        ...


class EventProtocol(Protocol):
    """Protocol for event handling."""

    def emit_event(self, event_type: MarketEvent, data: dict[str, Any]) -> None:
        """Emit a market event."""
        ...

    def subscribe(self, event_type: MarketEvent, callback) -> str:
        """Subscribe to events and return subscription ID."""
        ...

    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from events."""
        ...


class PositionProtocol(Protocol):
    """Protocol for position management (futures/derivatives)."""

    def get_position(self, trading_pair: str) -> dict[str, Any] | None:
        """Get position for a trading pair."""
        ...

    def get_all_positions(self) -> dict[str, dict[str, Any]]:
        """Get all positions."""
        ...

    def set_leverage(self, trading_pair: str, leverage: int) -> bool:
        """Set leverage for a trading pair."""
        ...


class SandboxProtocol(Protocol):
    """Main sandbox protocol that orchestrates all components."""

    @property
    def market(self) -> MarketProtocol:
        """Get market protocol instance."""
        ...

    @property
    def balance(self) -> BalanceProtocol:
        """Get balance protocol instance."""
        ...

    @property
    def order(self) -> OrderProtocol:
        """Get order protocol instance."""
        ...

    @property
    def event(self) -> EventProtocol:
        """Get event protocol instance."""
        ...

    @property
    def position(self) -> PositionProtocol | None:
        """Get position protocol instance (for derivatives)."""
        ...

    async def step(self, timestamp: float) -> None:
        """Advance sandbox simulation to timestamp."""
        ...

    def reset(self) -> None:
        """Reset sandbox to initial state."""
        ...


class DataProviderProtocol(Protocol):
    """Protocol for providing market data to the sandbox."""

    def get_historical_data(
        self,
        trading_pair: str,
        start_time: datetime,
        end_time: datetime,
    ) -> list[dict[str, Any]]:
        """Get historical market data."""
        ...

    async def get_order_book_snapshot(
        self,
        trading_pair: str,
        timestamp: datetime,
    ) -> OrderBook | None:
        """Get order book snapshot at timestamp."""
        ...


class StrategyProtocol(Protocol):
    """Protocol for strategies that can run in the sandbox."""

    async def on_tick(self, timestamp: float) -> None:
        """Called on each simulation tick."""
        ...

    def on_order_filled(self, order: Order) -> None:
        """Called when an order is filled."""
        ...

    def on_balance_updated(self, asset: str, balance: Decimal) -> None:
        """Called when balance is updated."""
        ...

    def initialize(self, sandbox: SandboxProtocol) -> None:
        """Initialize strategy with sandbox."""
        ...

    def cleanup(self) -> None:
        """Cleanup strategy resources."""
        ...


class SlippageModel(Enum):
    """Slippage calculation models."""

    LINEAR = "linear"
    LOGARITHMIC = "logarithmic"
    SQUARE_ROOT = "square_root"
    CUSTOM = "custom"


class MarketRegime(Enum):
    """Market regime types."""

    TRENDING_UP = "trending_up"
    TRENDING_DOWN = "trending_down"
    SIDEWAYS = "sideways"
    VOLATILE = "volatile"


class SlippageConfig:
    """Configuration for slippage simulation."""

    def __init__(
        self,
        model: SlippageModel = SlippageModel.LINEAR,
        base_slippage_bps: Decimal = Decimal("1.0"),  # Base slippage in basis points
        depth_impact_factor: Decimal = Decimal("0.1"),  # How much depth affects slippage
        volatility_multiplier: Decimal = Decimal("1.0"),  # Volatility impact on slippage
        max_slippage_bps: Decimal = Decimal("50.0"),  # Maximum slippage cap
        enable_partial_fills: bool = True,
    ):
        self.model = model
        self.base_slippage_bps = base_slippage_bps
        self.depth_impact_factor = depth_impact_factor
        self.volatility_multiplier = volatility_multiplier
        self.max_slippage_bps = max_slippage_bps
        self.enable_partial_fills = enable_partial_fills


class MarketDynamicsConfig:
    """Configuration for market dynamics simulation."""

    def __init__(
        self,
        price_volatility: Decimal = Decimal("0.001"),  # Price volatility per tick
        trend_strength: Decimal = Decimal("0.0"),  # Trend strength (-1 to 1)
        regime: MarketRegime = MarketRegime.SIDEWAYS,
        regime_change_probability: Decimal = Decimal("0.001"),  # Chance of regime change per tick
        order_book_refresh_rate: int = 10,  # Ticks between order book updates
        latency_ms: Decimal = Decimal("50.0"),  # Simulated order processing latency
        enable_realistic_spreads: bool = True,
    ):
        self.price_volatility = price_volatility
        self.trend_strength = trend_strength
        self.regime = regime
        self.regime_change_probability = regime_change_probability
        self.order_book_refresh_rate = order_book_refresh_rate
        self.latency_ms = latency_ms
        self.enable_realistic_spreads = enable_realistic_spreads


class MarketDepthLevel:
    """Enhanced order book level with market depth information."""

    def __init__(
        self,
        price: Decimal,
        amount: Decimal,
        cumulative_amount: Optional[Decimal] = None,
        order_count: int = 1,
    ):
        self.price = price
        self.amount = amount
        self.cumulative_amount = cumulative_amount or amount
        self.order_count = order_count
        self.last_updated = datetime.now()


class TradeFill:
    """Represents a trade fill with slippage information."""

    def __init__(
        self,
        order_id: str,
        fill_price: Decimal,
        fill_amount: Decimal,
        slippage_bps: Decimal,
        is_partial: bool = False,
        remaining_amount: Optional[Decimal] = None,
        market_impact: Optional[Decimal] = None,
    ):
        self.order_id = order_id
        self.fill_price = fill_price
        self.fill_amount = fill_amount
        self.slippage_bps = slippage_bps
        self.is_partial = is_partial
        self.remaining_amount = remaining_amount or Decimal("0")
        self.market_impact = market_impact or Decimal("0")
        self.timestamp = datetime.now()
