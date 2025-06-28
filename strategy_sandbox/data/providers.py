"""
Data providers for sandbox simulation.

Simple implementations for MVP functionality.
"""

from datetime import datetime
from typing import Any

from strategy_sandbox.core.protocols import OrderBook


class SimpleDataProvider:
    """Simple data provider with basic functionality."""

    def __init__(self):
        """Initialize the SimpleDataProvider."""
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize data provider.

        :return: None
        """
        self._initialized = True

    def get_historical_data(
        self,
        trading_pair: str,
        start_time: datetime,
        end_time: datetime,
    ) -> list[dict[str, Any]]:
        """Get historical market data (placeholder implementation).

        :param trading_pair: The trading pair (e.g., "BTC-USDT").
        :param start_time: The start time for the historical data.
        :param end_time: The end time for the historical data.
        :return: A list of historical data points.
        """
        # Return empty list for now - can be extended
        return []

    async def get_order_book_snapshot(
        self,
        trading_pair: str,
        timestamp: datetime,
    ) -> OrderBook | None:
        """Get order book snapshot at timestamp (placeholder implementation).

        :param trading_pair: The trading pair (e.g., "BTC-USDT").
        :param timestamp: The timestamp for the snapshot.
        :return: An OrderBook snapshot, or None if not available.
        """
        # Return None for now - can be extended with real data
        return None
