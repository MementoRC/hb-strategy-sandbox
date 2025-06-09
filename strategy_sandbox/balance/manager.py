"""
Sandbox balance manager implementation.

Simplified version of the balance manager from the original sandbox for MVP.
"""

from decimal import Decimal
from typing import Dict

from strategy_sandbox.core.protocols import BalanceProtocol


class SandboxBalanceManager:
    """Simple implementation of balance management for sandbox."""
    
    def __init__(self):
        self._balances: Dict[str, Decimal] = {}
        self._locked_balances: Dict[str, Decimal] = {}
    
    def get_balance(self, asset: str) -> Decimal:
        """Get total balance for an asset."""
        return self._balances.get(asset, Decimal("0"))
    
    def get_available_balance(self, asset: str) -> Decimal:
        """Get available balance for an asset."""
        total = self._balances.get(asset, Decimal("0"))
        locked = self._locked_balances.get(asset, Decimal("0"))
        return total - locked
    
    def get_all_balances(self) -> Dict[str, Decimal]:
        """Get all asset balances."""
        return self._balances.copy()
    
    def lock_balance(self, asset: str, amount: Decimal) -> bool:
        """Lock balance for trading."""
        available = self.get_available_balance(asset)
        if available >= amount:
            self._locked_balances[asset] = self._locked_balances.get(asset, Decimal("0")) + amount
            return True
        return False
    
    def unlock_balance(self, asset: str, amount: Decimal) -> bool:
        """Unlock previously locked balance."""
        locked = self._locked_balances.get(asset, Decimal("0"))
        if locked >= amount:
            self._locked_balances[asset] = locked - amount
            return True
        return False
    
    def update_balance(self, asset: str, delta: Decimal) -> None:
        """Update balance by delta amount."""
        current = self._balances.get(asset, Decimal("0"))
        self._balances[asset] = current + delta
    
    def set_balance(self, asset: str, amount: Decimal) -> None:
        """Set balance for an asset."""
        self._balances[asset] = amount
    
    def reset(self) -> None:
        """Reset all balances."""
        self._balances.clear()
        self._locked_balances.clear()