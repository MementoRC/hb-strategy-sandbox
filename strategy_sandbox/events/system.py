"""
Sandbox event system implementation.

Simple event system for MVP functionality.
"""

import asyncio
import uuid
from typing import Any, Callable, Dict

from strategy_sandbox.core.protocols import MarketEvent


class SandboxEventSystem:
    """Simple event system implementation."""

    def __init__(self):
        self._subscribers: Dict[MarketEvent, Dict[str, Callable]] = {}
        self._event_queue: asyncio.Queue = asyncio.Queue()

    def emit_event(self, event_type: MarketEvent, data: Dict[str, Any]) -> None:
        """Emit a market event."""
        # Add to queue for async processing
        try:
            self._event_queue.put_nowait((event_type, data))
        except asyncio.QueueFull:
            # Handle queue full scenario
            pass

    def subscribe(self, event_type: MarketEvent, callback: Callable) -> str:
        """Subscribe to events and return subscription ID."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = {}

        sub_id = str(uuid.uuid4())
        self._subscribers[event_type][sub_id] = callback
        return sub_id

    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from events."""
        for event_type, subscribers in self._subscribers.items():
            if subscription_id in subscribers:
                del subscribers[subscription_id]
                return True
        return False

    async def process_events(self) -> None:
        """Process all queued events."""
        while not self._event_queue.empty():
            try:
                event_type, data = self._event_queue.get_nowait()
                await self._dispatch_event(event_type, data)
            except asyncio.QueueEmpty:
                break

    async def _dispatch_event(self, event_type: MarketEvent, data: Dict[str, Any]) -> None:
        """Dispatch event to subscribers."""
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type].values():
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(data)
                    else:
                        callback(data)
                except Exception as e:
                    # Log error but continue processing
                    print(f"Error in event callback: {e}")

    def reset(self) -> None:
        """Reset event system."""
        self._subscribers.clear()
        # Clear queue
        while not self._event_queue.empty():
            try:
                self._event_queue.get_nowait()
            except asyncio.QueueEmpty:
                break
