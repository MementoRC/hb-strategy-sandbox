"""
Data providers for sandbox simulation.

Simple implementations for MVP functionality.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from strategy_sandbox.core.protocols import DataProviderProtocol, OrderBook, OrderBookLevel


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
    ) -> List[Dict[str, Any]]:
        """Get historical market data (placeholder implementation)."""
        # Return empty list for now - can be extended
        return []
    
    def get_order_book_snapshot(
        self,
        trading_pair: str,
        timestamp: datetime,
    ) -> Optional[OrderBook]:
        """Get order book snapshot at timestamp (placeholder implementation)."""
        # Return None for now - can be extended with real data
        return None