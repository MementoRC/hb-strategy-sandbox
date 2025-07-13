"""Test suite for events system module."""

import asyncio

import pytest

from strategy_sandbox.core.protocols import MarketEvent
from strategy_sandbox.events.system import SandboxEventSystem


class TestSandboxEventSystem:
    """Test cases for SandboxEventSystem class."""

    def test_event_system_creation(self):
        """Test basic event system creation."""
        event_system = SandboxEventSystem()
        assert event_system is not None
        assert event_system._subscribers == {}

    def test_subscribe_unsubscribe(self):
        """Test subscribing and unsubscribing from events."""
        event_system = SandboxEventSystem()

        def handler(data):
            pass

        # Test subscribe
        sub_id = event_system.subscribe(MarketEvent.ORDER_CREATED, handler)
        assert isinstance(sub_id, str)
        assert MarketEvent.ORDER_CREATED in event_system._subscribers
        assert sub_id in event_system._subscribers[MarketEvent.ORDER_CREATED]

        # Test unsubscribe
        result = event_system.unsubscribe(sub_id)
        assert result is True
        assert sub_id not in event_system._subscribers[MarketEvent.ORDER_CREATED]

    def test_emit_event(self):
        """Test emitting events."""
        event_system = SandboxEventSystem()

        # Test that event is added to queue
        event_system.emit_event(MarketEvent.ORDER_CREATED, {"test": "data"})
        assert not event_system._event_queue.empty()

    async def test_process_events(self):
        """Test processing events."""
        event_system = SandboxEventSystem()
        received_data = []

        def handler(data):
            received_data.append(data)

        # Subscribe to event
        event_system.subscribe(MarketEvent.ORDER_CREATED, handler)

        # Emit event
        test_data = {"symbol": "BTCUSD", "quantity": "1.0"}
        event_system.emit_event(MarketEvent.ORDER_CREATED, test_data)

        # Process events
        await event_system.process_events()

        # Verify handler was called
        assert len(received_data) == 1
        assert received_data[0]["symbol"] == "BTCUSD"
        assert received_data[0]["quantity"] == "1.0"

    def test_reset(self):
        """Test resetting the event system."""
        event_system = SandboxEventSystem()

        # Add subscriber and emit event
        def handler(data):
            pass

        event_system.subscribe(MarketEvent.ORDER_CREATED, handler)
        event_system.emit_event(MarketEvent.ORDER_CREATED, {"test": "data"})

        # Reset
        event_system.reset()

        # Verify everything is cleared
        assert event_system._subscribers == {}
        assert event_system._event_queue.empty()
