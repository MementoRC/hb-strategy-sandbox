"""
Hummingbot Strategy Sandbox - A testing and simulation framework for trading strategies.

This package provides a comprehensive sandbox environment for testing and developing
trading strategies without connecting to real exchanges.
"""

from strategy_sandbox.__about__ import __version__
from strategy_sandbox.core.environment import SandboxEnvironment
from strategy_sandbox.core.protocols import (
    MarketProtocol,
    BalanceProtocol,
    OrderProtocol,
    EventProtocol,
)

__all__ = [
    "__version__",
    "SandboxEnvironment",
    "MarketProtocol",
    "BalanceProtocol",
    "OrderProtocol",
    "EventProtocol",
]
