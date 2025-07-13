"""Test suite for the maintenance CLI module."""

import argparse
import json
import tempfile
import unittest.mock
from pathlib import Path

import pytest

from strategy_sandbox.maintenance.cli import create_parser, main
from strategy_sandbox.maintenance.health_monitor import CIHealthMonitor
from strategy_sandbox.maintenance.scheduler import MaintenanceScheduler


class TestMaintenanceCLI:
    """Test cases for the maintenance CLI functionality."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def sample_config_file(self, temp_dir):
        """Create a sample configuration file."""
        config = {
            "maintenance": {"tasks": {"health_check": {"frequency": "hourly", "enabled": True}}}
        }
        config_file = temp_dir / "config.yaml"
        with open(config_file, "w") as f:
            json.dump(config, f)  # Using JSON for simplicity in tests
        return config_file

    def test_create_parser(self):
        """Test create_parser function returns a configured parser."""
        parser = create_parser()
        assert isinstance(parser, argparse.ArgumentParser)
        assert parser.description == "Hummingbot Strategy Sandbox - Maintenance Tools"

    def test_main_no_args(self):
        """Test main function with no arguments shows help."""
        with unittest.mock.patch("sys.argv", ["cli.py"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0  # Help command exits with 0

    def test_main_health_summary(self):
        """Test main function with health summary command."""
        with unittest.mock.patch("sys.argv", ["cli.py", "health", "--summary"]):
            with unittest.mock.patch("strategy_sandbox.maintenance.cli.CIHealthMonitor"):
                with pytest.raises(SystemExit):
                    main()

    def test_main_health_collect(self):
        """Test main function with health collect command."""
        with unittest.mock.patch("sys.argv", ["cli.py", "health", "--collect"]):
            with unittest.mock.patch("strategy_sandbox.maintenance.cli.CIHealthMonitor"):
                with pytest.raises(SystemExit):
                    main()

    def test_main_health_diagnostics(self):
        """Test main function with health diagnostics command."""
        with unittest.mock.patch("sys.argv", ["cli.py", "health", "--diagnostics"]):
            with unittest.mock.patch("strategy_sandbox.maintenance.cli.CIHealthMonitor"):
                with pytest.raises(SystemExit):
                    main()

    def test_main_tasks_list(self):
        """Test main function with tasks list command."""
        with unittest.mock.patch("sys.argv", ["cli.py", "tasks", "--list"]):
            with unittest.mock.patch("strategy_sandbox.maintenance.cli.MaintenanceScheduler"):
                with pytest.raises(SystemExit):
                    main()

    def test_main_tasks_run(self):
        """Test main function with tasks run command."""
        with unittest.mock.patch("sys.argv", ["cli.py", "tasks", "--run", "health_check"]):
            with unittest.mock.patch("strategy_sandbox.maintenance.cli.MaintenanceScheduler"):
                with pytest.raises(SystemExit):
                    main()

    def test_main_tasks_run_pending(self):
        """Test main function with tasks run-pending command."""
        with unittest.mock.patch("sys.argv", ["cli.py", "tasks", "--run-pending"]):
            with unittest.mock.patch("strategy_sandbox.maintenance.cli.MaintenanceScheduler"):
                with pytest.raises(SystemExit):
                    main()

    def test_main_maintenance_perform(self):
        """Test main function with maintenance perform command."""
        with unittest.mock.patch("sys.argv", ["cli.py", "maintenance", "--perform"]):
            with unittest.mock.patch("strategy_sandbox.maintenance.cli.MaintenanceScheduler"):
                with pytest.raises(SystemExit):
                    main()

    def test_main_maintenance_dry_run(self):
        """Test main function with maintenance dry run command."""
        with unittest.mock.patch("sys.argv", ["cli.py", "maintenance", "--perform", "--dry-run"]):
            with unittest.mock.patch("strategy_sandbox.maintenance.cli.MaintenanceScheduler"):
                with pytest.raises(SystemExit):
                    main()

    def test_main_config_show(self):
        """Test main function with config show command."""
        with unittest.mock.patch("sys.argv", ["cli.py", "config", "--show"]):
            with unittest.mock.patch("strategy_sandbox.maintenance.cli.MaintenanceScheduler"):
                with pytest.raises(SystemExit):
                    main()

    def test_main_exception_handling(self):
        """Test main function handles unexpected exceptions gracefully."""
        with unittest.mock.patch("sys.argv", ["cli.py", "health", "--summary"]):
            with unittest.mock.patch(
                "strategy_sandbox.maintenance.cli.CIHealthMonitor"
            ) as mock_monitor:
                mock_monitor.side_effect = Exception("Test exception")

                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 1

    def test_main_invalid_command(self):
        """Test main function with invalid command."""
        with unittest.mock.patch("sys.argv", ["cli.py", "invalid-command"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code != 0

    def test_main_with_custom_config(self, temp_dir, sample_config_file):
        """Test main function with custom config file."""
        with (
            unittest.mock.patch(
                "sys.argv", ["cli.py", "config", "--show", "--config", str(sample_config_file)]
            ),
            unittest.mock.patch("strategy_sandbox.maintenance.cli.MaintenanceScheduler"),
        ):
            with pytest.raises(SystemExit):
                main()

    def test_main_with_custom_project_path(self, temp_dir):
        """Test main function with custom project path."""
        with (
            unittest.mock.patch(
                "sys.argv", ["cli.py", "health", "--summary", "--project-path", str(temp_dir)]
            ),
            unittest.mock.patch("strategy_sandbox.maintenance.cli.CIHealthMonitor"),
        ):
            with pytest.raises(SystemExit):
                main()

    def test_main_with_json_output(self):
        """Test main function with JSON output format."""
        with (
            unittest.mock.patch(
                "sys.argv", ["cli.py", "health", "--summary", "--output-format", "json"]
            ),
            unittest.mock.patch("strategy_sandbox.maintenance.cli.CIHealthMonitor"),
        ):
            with pytest.raises(SystemExit):
                main()
