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

# Backward compatibility imports for framework components
try:
    # Import from new framework location
    from framework.maintenance import CIHealthMonitor, MaintenanceScheduler
    from framework.performance import (
        AlertSeverity,
        BenchmarkResult,
        ComparisonMode,
        PerformanceAlert,
        PerformanceCollector,
        PerformanceComparator,
        PerformanceMetrics,
        TrendAlert,
        TrendAnalyzer,
        TrendData,
        schema,
    )
    from framework.reporting import ArtifactManager, GitHubReporter, ReportGenerator, TemplateEngine
    from framework.security import (
        DependencyAnalyzer,
        DependencyInfo,
        SBOMGenerator,
        SecurityCollector,
        SecurityMetrics,
        VulnerabilityInfo,
    )

    # Add compatibility warning
    warnings.warn(
        "Importing framework components from strategy_sandbox is deprecated. "
        "Use 'from framework import ...' instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    # Add framework components to exports
    __all__.extend(
        [
            # Performance tools
            "PerformanceCollector",
            "PerformanceComparator",
            "PerformanceMetrics",
            "BenchmarkResult",
            "AlertSeverity",
            "ComparisonMode",
            "PerformanceAlert",
            "TrendAnalyzer",
            "TrendAlert",
            "TrendData",
            "schema",
            # Security tools
            "DependencyAnalyzer",
            "SecurityCollector",
            "SBOMGenerator",
            "DependencyInfo",
            "SecurityMetrics",
            "VulnerabilityInfo",
            # Reporting tools
            "ReportGenerator",
            "ArtifactManager",
            "TemplateEngine",
            "GitHubReporter",
            # Maintenance tools
            "CIHealthMonitor",
            "MaintenanceScheduler",
        ]
    )

except ImportError:
    # Fallback to old locations (during migration)
    pass


def __getattr__(name):
    """Dynamic import handler for backward compatibility with deprecation warnings."""
    # Framework modules backward compatibility
    framework_modules = {
        "performance": "framework.performance",
        "security": "framework.security",
        "reporting": "framework.reporting",
        "maintenance": "framework.maintenance",
    }

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

    raise AttributeError(f"module 'strategy_sandbox' has no attribute '{name}'")
