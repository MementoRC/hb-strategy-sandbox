"""
Performance benchmark tests for strategy sandbox.
"""

import json
import time
from datetime import timedelta
from decimal import Decimal

import pytest

from strategy_sandbox import SandboxEnvironment
from strategy_sandbox.core import SandboxConfiguration


class SimpleBenchmarkStrategy:
    """Simple strategy for benchmarking."""

    def __init__(self):
        self.sandbox = None
        self.tick_count = 0
        self.orders_placed = 0

    def initialize(self, sandbox):
        self.sandbox = sandbox

    async def on_tick(self, timestamp: float):
        self.tick_count += 1

        # Place an order every 10 ticks
        if self.tick_count % 10 == 0:
            from strategy_sandbox.core.protocols import OrderCandidate, OrderSide, OrderType

            order = OrderCandidate(
                trading_pair="BTC-USDT",
                side=OrderSide.BUY,
                order_type=OrderType.MARKET,
                amount=Decimal("0.01"),
            )

            order_id = self.sandbox.order.place_order(order)
            if order_id:
                self.orders_placed += 1

    async def on_order_filled(self, order):
        pass

    async def on_balance_updated(self, asset: str, balance: Decimal):
        pass

    def cleanup(self):
        pass


@pytest.mark.benchmark
class TestPerformanceBenchmarks:
    """Performance benchmark test cases."""

    @pytest.mark.asyncio
    async def test_simulation_throughput(self, benchmark):
        """Benchmark simulation throughput."""

        async def run_simulation():
            config = SandboxConfiguration(
                initial_balances={"USDT": Decimal("10000")},
                trading_pairs=["BTC-USDT"],
                tick_interval=0.1,  # Fast ticks for benchmark
            )

            sandbox = SandboxEnvironment(config=config)
            strategy = SimpleBenchmarkStrategy()
            sandbox.add_strategy(strategy)

            await sandbox.run(duration=timedelta(seconds=10))
            return sandbox.performance_metrics

        # Benchmark the simulation
        result = await benchmark(run_simulation)

        # Verify we got reasonable performance
        assert result["duration_seconds"] > 0
        print(f"Simulation processed {result['duration_seconds']} seconds")

    @pytest.mark.asyncio
    async def test_order_processing_speed(self):
        """Benchmark order processing speed."""
        config = SandboxConfiguration(
            initial_balances={"USDT": Decimal("100000")},
            trading_pairs=["BTC-USDT"],
        )

        sandbox = SandboxEnvironment(config=config)
        await sandbox.initialize()

        from strategy_sandbox.core.protocols import OrderCandidate, OrderSide, OrderType

        # Benchmark order placement
        num_orders = 1000
        start_time = time.time()

        orders_placed = 0
        for i in range(num_orders):
            order = OrderCandidate(
                trading_pair="BTC-USDT",
                side=OrderSide.BUY,
                order_type=OrderType.MARKET,
                amount=Decimal("0.001"),
            )

            order_id = sandbox.order.place_order(order)
            if order_id:
                orders_placed += 1

        end_time = time.time()
        duration = end_time - start_time

        # Calculate metrics
        orders_per_second = orders_placed / duration
        avg_order_time = duration / orders_placed * 1000  # ms

        print(f"Orders placed: {orders_placed}")
        print(f"Orders per second: {orders_per_second:.2f}")
        print(f"Average order time: {avg_order_time:.2f}ms")

        # Save benchmark results
        results = {
            "orders_placed": orders_placed,
            "duration_seconds": duration,
            "orders_per_second": orders_per_second,
            "avg_order_time_ms": avg_order_time,
            "avg_response_time": f"{avg_order_time:.2f}ms",
            "memory_usage": "50MB",  # Placeholder
            "throughput": f"{orders_per_second:.0f}",
            "change_response_time": "+0%",  # Placeholder for CI
            "change_memory": "+0%",
            "change_throughput": "+0%",
        }

        with open("benchmark-results.json", "w") as f:
            json.dump(results, f, indent=2)

        # Assert performance thresholds
        assert orders_per_second > 100, f"Order processing too slow: {orders_per_second} orders/sec"
        assert avg_order_time < 50, f"Average order time too high: {avg_order_time}ms"

    @pytest.mark.asyncio
    async def test_balance_operations_speed(self):
        """Benchmark balance operations."""
        config = SandboxConfiguration(
            initial_balances={"USDT": Decimal("10000")},
        )

        sandbox = SandboxEnvironment(config=config)
        await sandbox.initialize()

        # Benchmark balance operations
        num_operations = 10000
        start_time = time.time()

        for i in range(num_operations):
            # Test various balance operations
            sandbox.balance.get_balance("USDT")
            sandbox.balance.get_available_balance("USDT")

            if i % 2 == 0:
                sandbox.balance.lock_balance("USDT", Decimal("1"))
                sandbox.balance.unlock_balance("USDT", Decimal("1"))
            else:
                sandbox.balance.update_balance("USDT", Decimal("0.01"))
                sandbox.balance.update_balance("USDT", Decimal("-0.01"))

        end_time = time.time()
        duration = end_time - start_time
        operations_per_second = num_operations / duration

        print(f"Balance operations per second: {operations_per_second:.2f}")

        # Assert performance threshold
        assert operations_per_second > 1000, (
            f"Balance operations too slow: {operations_per_second} ops/sec"
        )

    @pytest.mark.asyncio
    async def test_event_system_performance(self):
        """Benchmark event system performance."""
        config = SandboxConfiguration()
        sandbox = SandboxEnvironment(config=config)
        await sandbox.initialize()

        # Set up event subscribers
        events_received = 0

        def event_handler(data):
            nonlocal events_received
            events_received += 1

        from strategy_sandbox.core.protocols import MarketEvent

        # Subscribe to events
        sub_id = sandbox.event.subscribe(MarketEvent.ORDER_CREATED, event_handler)

        # Benchmark event emission
        num_events = 5000
        start_time = time.time()

        for i in range(num_events):
            sandbox.event.emit_event(
                MarketEvent.ORDER_CREATED,
                {
                    "order_id": f"test-{i}",
                    "timestamp": time.time(),
                },
            )

        # Process all events
        await sandbox.event.process_events()

        end_time = time.time()
        duration = end_time - start_time
        events_per_second = num_events / duration

        print(f"Events per second: {events_per_second:.2f}")
        print(f"Events received: {events_received}")

        # Cleanup
        sandbox.event.unsubscribe(sub_id)

        # Assert performance threshold
        assert events_per_second > 500, f"Event system too slow: {events_per_second} events/sec"
        assert events_received == num_events, f"Event loss detected: {events_received}/{num_events}"
