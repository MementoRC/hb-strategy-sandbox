"""
Pytest configuration and fixtures for strategy sandbox tests.
"""

import pytest
from decimal import Decimal

from strategy_sandbox import SandboxEnvironment
from strategy_sandbox.core import SandboxConfiguration


@pytest.fixture
def basic_config():
    """Basic sandbox configuration for testing."""
    return SandboxConfiguration(
        initial_balances={
            "USDT": Decimal("10000"),
            "BTC": Decimal("1"),
        },
        trading_pairs=["BTC-USDT", "ETH-USDT"],
        tick_interval=1.0,
    )


@pytest.fixture
async def sandbox(basic_config):
    """Initialized sandbox environment for testing."""
    sandbox = SandboxEnvironment(config=basic_config)
    await sandbox.initialize()
    return sandbox


@pytest.fixture
def mock_strategy():
    """Mock strategy for testing."""
    
    class MockStrategy:
        def __init__(self):
            self.sandbox = None
            self.tick_count = 0
            self.initialized = False
            self.cleaned_up = False
        
        def initialize(self, sandbox):
            self.sandbox = sandbox
            self.initialized = True
        
        async def on_tick(self, timestamp: float):
            self.tick_count += 1
        
        async def on_order_filled(self, order):
            pass
        
        async def on_balance_updated(self, asset: str, balance: Decimal):
            pass
        
        def cleanup(self):
            self.cleaned_up = True
    
    return MockStrategy()