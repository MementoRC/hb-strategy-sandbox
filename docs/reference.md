# API Reference

This section contains the auto-generated API reference for the `hb-strategy-sandbox` project.

::: strategy_sandbox
    options:
        members:
            - SandboxEnvironment
            - SandboxConfiguration

::: strategy_sandbox.balance
    options:
        members:
            - SandboxBalanceManager

::: strategy_sandbox.core
    options:
        members:
            - protocols

::: strategy_sandbox.data
    options:
        members:
            - SimpleDataProvider

::: strategy_sandbox.events
    options:
        members:
            - SandboxEventSystem

::: strategy_sandbox.markets
    options:
        members:
            - ExchangeSimulator

::: strategy_sandbox.maintenance
    options:
        members:
            - CIHealthMonitor
            - MaintenanceScheduler
            - MaintenanceTask

::: strategy_sandbox.performance
    options:
        members:
            - PerformanceCollector
            - PerformanceComparator
            - BenchmarkResult
            - PerformanceMetrics
            - TrendAnalyzer

::: strategy_sandbox.reporting
    options:
        members:
            - ArtifactManager
            - GitHubReporter
            - ReportGenerator
            - TemplateEngine

::: strategy_sandbox.security
    options:
        members:
            - DependencyAnalyzer
            - SBOMGenerator
            - SecurityCollector
            - SecurityDashboardGenerator
            - VulnerabilityInfo
            - DependencyInfo
            - SecurityMetrics
