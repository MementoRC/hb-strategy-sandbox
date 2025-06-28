"""
Hummingbot Strategy Sandbox - A testing and simulation framework for trading strategies.

This package provides a comprehensive sandbox environment for testing and developing
trading strategies without connecting to real exchanges.
"""

import warnings
from importlib import import_module

from strategy_sandbox.__about__ import __version__
from strategy_sandbox.core.environment import SandboxEnvironment
from strategy_sandbox.core.protocols import (
    BalanceProtocol,
    EventProtocol,
    MarketProtocol,
    OrderProtocol,
)

# Base exports
__all__ = [
    "__version__",
    "SandboxEnvironment",
    "MarketProtocol",
    "BalanceProtocol",
    "OrderProtocol",
    "EventProtocol",
]

# Framework backward compatibility - handled via __getattr__ to avoid unused imports


def __getattr__(name):
    """Dynamic import handler for backward compatibility with deprecation warnings."""
    # Framework modules backward compatibility
    framework_modules = {
        "performance": "framework.performance",
        "security": "framework.security",
        "reporting": "framework.reporting",
        "maintenance": "framework.maintenance",
    }

    # Framework component backward compatibility mapping
    framework_components = {
        # Performance tools
        "PerformanceCollector": "framework.performance",
        "PerformanceComparator": "framework.performance",
        "PerformanceMetrics": "framework.performance",
        "BenchmarkResult": "framework.performance",
        "AlertSeverity": "framework.performance",
        "ComparisonMode": "framework.performance",
        "PerformanceAlert": "framework.performance",
        "TrendAnalyzer": "framework.performance",
        "TrendAlert": "framework.performance",
        "TrendData": "framework.performance",
        "schema": "framework.performance",
        # Security tools
        "DependencyAnalyzer": "framework.security",
        "SecurityCollector": "framework.security",
        "SBOMGenerator": "framework.security",
        "DependencyInfo": "framework.security",
        "SecurityMetrics": "framework.security",
        "VulnerabilityInfo": "framework.security",
        # Reporting tools
        "ReportGenerator": "framework.reporting",
        "ArtifactManager": "framework.reporting",
        "TemplateEngine": "framework.reporting",
        "GitHubReporter": "framework.reporting",
        # Maintenance tools
        "CIHealthMonitor": "framework.maintenance",
        "MaintenanceScheduler": "framework.maintenance",
    }

    # Handle framework module imports
    if name in framework_modules:
        warnings.warn(
            f"Importing {name} from strategy_sandbox is deprecated. "
            f"Use 'from framework import {name}' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        try:
            return import_module(framework_modules[name])
        except ImportError:
            # Fallback to old location if framework not available
            return import_module(f"strategy_sandbox.{name}")

    # Handle individual framework component imports
    if name in framework_components:
        warnings.warn(
            f"Importing {name} from strategy_sandbox is deprecated. "
            f"Use 'from framework import ...' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        try:
            module = import_module(framework_components[name])
            return getattr(module, name)
        except (ImportError, AttributeError):
            # Fallback to old location if framework not available
            try:
                module_name = framework_components[name].replace("framework.", "strategy_sandbox.")
                module = import_module(module_name)
                return getattr(module, name)
            except (ImportError, AttributeError):
                pass

    raise AttributeError(f"module 'strategy_sandbox' has no attribute '{name}'")
