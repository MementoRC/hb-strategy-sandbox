"""Basic tests to improve CLI coverage."""


def test_performance_cli_import():
    """Test that performance CLI can be imported."""
    from strategy_sandbox.performance import cli

    assert cli is not None


def test_reporting_cli_import():
    """Test that reporting CLI can be imported."""
    from strategy_sandbox.reporting import cli

    assert cli is not None


def test_security_cli_import():
    """Test that security CLI can be imported."""
    from strategy_sandbox.security import cli

    assert cli is not None


def test_maintenance_cli_import():
    """Test that maintenance CLI can be imported."""
    from strategy_sandbox.maintenance import cli

    assert cli is not None


def test_security_models_basic():
    """Test basic security models functionality."""
    from strategy_sandbox.security.models import DependencyInfo, VulnerabilityInfo

    vuln = VulnerabilityInfo(
        id="CVE-2023-1234",
        package_name="test-package",
        package_version="1.0.0",
        severity="high",
        description="Test vulnerability",
    )

    dep = DependencyInfo(
        name="test-dep", version="1.0.0", package_manager="pip", vulnerabilities=[vuln]
    )

    assert dep.has_vulnerabilities
    assert dep.vulnerability_count_by_severity["high"] == 1


def test_security_collector_basic():
    """Test basic security collector functionality."""
    import tempfile
    from pathlib import Path

    from strategy_sandbox.security.collector import SecurityCollector

    with tempfile.TemporaryDirectory() as temp_dir:
        collector = SecurityCollector(temp_dir)
        assert collector.storage_path == Path(temp_dir)
        assert collector.baseline_path.exists()
        assert collector.history_path.exists()

        env_info = collector.collect_environment_info()
        assert "platform" in env_info
        assert "python_version" in env_info
        assert "hostname" in env_info


def test_basic_imports():
    """Test basic imports work."""
    from strategy_sandbox.core import protocols
    from strategy_sandbox.data import providers
    from strategy_sandbox.events import system

    assert protocols is not None
    assert providers is not None
    assert system is not None

    # Test some basic protocol imports
    assert hasattr(protocols, "OrderType")
    assert hasattr(protocols, "OrderSide")
    assert hasattr(protocols, "OrderStatus")


def test_package_structure():
    """Test package structure imports."""
    # Test that main package modules can be imported
    from strategy_sandbox import (
        balance,
        core,
        data,
        events,
        maintenance,
        markets,
        performance,
        reporting,
        security,
    )

    assert all(
        [balance, core, data, events, markets, performance, reporting, security, maintenance]
    )
