"""
Data providers for sandbox simulation.

Simple implementations for MVP functionality.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from strategy_sandbox.core.protocols import OrderBook


class SimpleDataProvider:
    """Simple data provider with basic functionality."""

    def __init__(self):
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize data provider."""
        self._initialized = True

    def get_historical_data(
        self,
        trading_pair: str,
        start_time: datetime,
        end_time: datetime,
    ) -> list[dict[str, Any]]:
        """Get historical market data (placeholder implementation)."""
        # Return empty list for now - can be extended
        return []

    async def get_order_book_snapshot(
        self,
        trading_pair: str,
        timestamp: datetime,
    ) -> OrderBook | None:
        """Get order book snapshot at timestamp (placeholder implementation)."""
        # Return None for now - can be extended with real data
        return None
