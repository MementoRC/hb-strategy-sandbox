"""
Sandbox balance manager implementation.

Simplified version of the balance manager from the original sandbox for MVP.
"""

from decimal import Decimal


class SandboxBalanceManager:
    """Simple implementation of balance management for sandbox."""

    def __init__(self):
        """Initialize the SandboxBalanceManager."""
        self._balances: dict[str, Decimal] = {}
        self._locked_balances: dict[str, Decimal] = {}

    def get_balance(self, asset: str) -> Decimal:
        """Get total balance for an asset.

        :param asset: The asset symbol (e.g., "USDT").
        :return: The total balance as a Decimal.
        """
        return self._balances.get(asset, Decimal("0"))

    def get_available_balance(self, asset: str) -> Decimal:
        """Get available balance for an asset.

        :param asset: The asset symbol (e.g., "USDT").
        :return: The available balance as a Decimal.
        """
        total = self._balances.get(asset, Decimal("0"))
        locked = self._locked_balances.get(asset, Decimal("0"))
        return total - locked

    def get_all_balances(self) -> dict[str, Decimal]:
        """Get all asset balances.

        :return: A dictionary of all asset balances.
        """
        return self._balances.copy()

    def lock_balance(self, asset: str, amount: Decimal) -> bool:
        """Lock balance for trading.

        :param asset: The asset symbol.
        :param amount: The amount to lock.
        :return: True if the balance was successfully locked, False otherwise.
        """
        available = self.get_available_balance(asset)
        if available >= amount:
            self._locked_balances[asset] = self._locked_balances.get(asset, Decimal("0")) + amount
            return True
        return False

    def unlock_balance(self, asset: str, amount: Decimal) -> bool:
        """Unlock previously locked balance.

        :param asset: The asset symbol.
        :param amount: The amount to unlock.
        :return: True if the balance was successfully unlocked, False otherwise.
        """
        locked = self._locked_balances.get(asset, Decimal("0"))
        if locked >= amount:
            self._locked_balances[asset] = locked - amount
            return True
        return False

    def update_balance(self, asset: str, delta: Decimal) -> None:
        """Update balance by delta amount.

        :param asset: The asset symbol.
        :param delta: The amount to change the balance by.
        """
        current = self._balances.get(asset, Decimal("0"))
        self._balances[asset] = current + delta

    def set_balance(self, asset: str, amount: Decimal) -> None:
        """Set balance for an asset.

        :param asset: The asset symbol.
        :param amount: The amount to set the balance to.
        """
        self._balances[asset] = amount

    def reset(self) -> None:
        """Reset all balances."""
        self._balances.clear()
        self._locked_balances.clear()
