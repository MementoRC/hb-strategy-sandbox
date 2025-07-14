"""Test suite for data providers module."""

from datetime import datetime

from strategy_sandbox.data.providers import SimpleDataProvider


class TestSimpleDataProvider:
    """Test cases for SimpleDataProvider class."""

    def test_simple_data_provider_creation(self):
        """Test that SimpleDataProvider can be instantiated."""
        provider = SimpleDataProvider()
        assert provider is not None
        assert not provider._initialized

    async def test_simple_data_provider_initialization(self):
        """Test SimpleDataProvider initialization."""
        provider = SimpleDataProvider()
        await provider.initialize()
        assert provider._initialized

    def test_get_historical_data(self):
        """Test get_historical_data method."""
        provider = SimpleDataProvider()
        start_time = datetime(2023, 1, 1)
        end_time = datetime(2023, 1, 2)

        data = provider.get_historical_data("BTC-USDT", start_time, end_time)
        assert isinstance(data, list)
        assert data == []  # Current implementation returns empty list

    async def test_get_order_book_snapshot(self):
        """Test get_order_book_snapshot method."""
        provider = SimpleDataProvider()
        timestamp = datetime.now()

        snapshot = await provider.get_order_book_snapshot("BTC-USDT", timestamp)
        assert snapshot is None  # Current implementation returns None
