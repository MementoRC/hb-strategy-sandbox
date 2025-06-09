"""
Unit tests for SandboxEnvironment.
"""

import pytest
from decimal import Decimal
from datetime import timedelta

from strategy_sandbox import SandboxEnvironment
from strategy_sandbox.core import SandboxConfiguration


class TestSandboxEnvironment:
    """Test cases for SandboxEnvironment."""
    
    def test_initialization(self):
        """Test basic sandbox initialization."""
        config = SandboxConfiguration(
            initial_balances={"USDT": Decimal("1000")},
            trading_pairs=["BTC-USDT"],
        )
        sandbox = SandboxEnvironment(config=config)
        
        assert sandbox.config == config
        assert not sandbox.is_running
        assert sandbox.current_timestamp == config.start_timestamp
    
    @pytest.mark.asyncio
    async def test_initialize(self):
        """Test sandbox initialization."""
        config = SandboxConfiguration(
            initial_balances={"USDT": Decimal("1000"), "BTC": Decimal("1")},
            trading_pairs=["BTC-USDT"],
        )
        sandbox = SandboxEnvironment(config=config)
        
        await sandbox.initialize()
        
        # Check balances were set
        assert sandbox.balance.get_balance("USDT") == Decimal("1000")
        assert sandbox.balance.get_balance("BTC") == Decimal("1")
        
        # Check trading pairs were added
        assert "BTC-USDT" in sandbox.market.get_trading_pairs()
    
    @pytest.mark.asyncio
    async def test_step_function(self):
        """Test single step execution."""
        sandbox = SandboxEnvironment()
        await sandbox.initialize()
        
        initial_timestamp = sandbox.current_timestamp
        await sandbox.step()
        
        # Timestamp should advance by tick_interval
        expected_timestamp = initial_timestamp + sandbox.config.tick_interval
        assert sandbox.current_timestamp == expected_timestamp
    
    @pytest.mark.asyncio
    async def test_reset_function(self):
        """Test sandbox reset functionality."""
        config = SandboxConfiguration(
            initial_balances={"USDT": Decimal("1000")},
        )
        sandbox = SandboxEnvironment(config=config)
        await sandbox.initialize()
        
        # Modify state
        sandbox.balance.update_balance("USDT", Decimal("-100"))
        await sandbox.step()
        
        # Reset
        sandbox.reset()
        
        # Check state is back to initial
        assert sandbox.current_timestamp == config.start_timestamp
        assert not sandbox.is_running
        assert sandbox.balance.get_balance("USDT") == Decimal("1000")
    
    def test_protocol_access(self):
        """Test access to protocol interfaces."""
        sandbox = SandboxEnvironment()
        
        # Should be able to access all protocols
        assert sandbox.market is not None
        assert sandbox.balance is not None
        assert sandbox.order is not None
        assert sandbox.event is not None
        # Position is optional
        assert sandbox.position is None  # Not enabled by default