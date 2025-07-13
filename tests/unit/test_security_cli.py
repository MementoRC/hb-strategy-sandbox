"""Test suite for the security CLI module."""

import argparse
import json
import tempfile
import unittest.mock
from pathlib import Path

import pytest

from strategy_sandbox.security.cli import (
    list_command,
    main,
    report_command,
    sbom_command,
    scan_command,
)
from strategy_sandbox.security.collector import SecurityCollector
from strategy_sandbox.security.sbom_generator import SBOMGenerator


class TestSecurityCLI:
    """Test cases for the security CLI functionality."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def sample_args(self, temp_dir):
        """Create sample command line arguments."""
        args = argparse.Namespace()
        args.project_path = str(temp_dir)
        args.storage_path = str(temp_dir / "security_data")
        args.build_id = "test_build_123"
        args.package_managers = ["pip"]
        args.save_baseline = False
        args.baseline_name = "default"
        return args

    def test_main_no_args(self):
        """Test main function with no arguments shows help."""
        with unittest.mock.patch("sys.argv", ["cli.py"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0  # Help command exits with 0

    def test_main_scan_command(self, temp_dir):
        """Test main function with scan command."""
        with (
            unittest.mock.patch(
                "sys.argv",
                [
                    "cli.py",
                    "scan",
                    "--project-path",
                    str(temp_dir),
                    "--storage-path",
                    str(temp_dir / "security_data"),
                    "--build-id",
                    "test_build",
                ],
            ),
            unittest.mock.patch("strategy_sandbox.security.cli.scan_command") as mock_scan,
        ):
            main()
            mock_scan.assert_called_once()

    def test_main_report_command(self, temp_dir):
        """Test main function with report command."""
        with (
            unittest.mock.patch(
                "sys.argv",
                [
                    "cli.py",
                    "report",
                    "--project-path",
                    str(temp_dir),
                    "--storage-path",
                    str(temp_dir / "security_data"),
                ],
            ),
            unittest.mock.patch("strategy_sandbox.security.cli.report_command") as mock_report,
        ):
            main()
            mock_report.assert_called_once()

    def test_main_list_command(self, temp_dir):
        """Test main function with list command."""
        with (
            unittest.mock.patch(
                "sys.argv", ["cli.py", "list", "--storage-path", str(temp_dir / "security_data")]
            ),
            unittest.mock.patch("strategy_sandbox.security.cli.list_command") as mock_list,
        ):
            main()
            mock_list.assert_called_once()

    def test_main_sbom_command(self, temp_dir):
        """Test main function with sbom command."""
        with (
            unittest.mock.patch(
                "sys.argv",
                [
                    "cli.py",
                    "sbom",
                    "--project-path",
                    str(temp_dir),
                    "--output",
                    str(temp_dir / "sbom.json"),
                ],
            ),
            unittest.mock.patch("strategy_sandbox.security.cli.sbom_command") as mock_sbom,
        ):
            main()
            mock_sbom.assert_called_once()

    def test_scan_command_basic(self, sample_args):
        """Test scan_command function with basic arguments."""
        mock_metrics = unittest.mock.MagicMock()
        mock_metrics.calculate_summary_stats.return_value = {
            "total_dependencies": 10,
            "vulnerable_dependencies": 2,
            "total_vulnerabilities": 3,
            "vulnerability_rate": 20.0,
            "vulnerabilities_by_severity": {"high": 1, "medium": 2},
        }

        with unittest.mock.patch(
            "strategy_sandbox.security.cli.SecurityCollector"
        ) as mock_collector_class:
            mock_collector = mock_collector_class.return_value
            mock_collector.scan_project_security.return_value = mock_metrics
            mock_collector.save_metrics.return_value = "/path/to/metrics.json"

            scan_command(sample_args)

            mock_collector_class.assert_called_once_with(sample_args.storage_path)
            mock_collector.scan_project_security.assert_called_once_with(
                project_path=sample_args.project_path,
                build_id=sample_args.build_id,
                package_managers=sample_args.package_managers,
            )
            mock_collector.save_metrics.assert_called_once_with(mock_metrics)

    def test_scan_command_with_baseline(self, sample_args):
        """Test scan_command function with baseline saving."""
        sample_args.save_baseline = True
        sample_args.baseline_name = "test_baseline"

        mock_metrics = unittest.mock.MagicMock()
        mock_metrics.calculate_summary_stats.return_value = {
            "total_dependencies": 10,
            "vulnerable_dependencies": 0,
            "total_vulnerabilities": 0,
            "vulnerability_rate": 0.0,
        }

        with unittest.mock.patch(
            "strategy_sandbox.security.cli.SecurityCollector"
        ) as mock_collector_class:
            mock_collector = mock_collector_class.return_value
            mock_collector.scan_project_security.return_value = mock_metrics
            mock_collector.save_metrics.return_value = "/path/to/metrics.json"
            mock_collector.save_baseline.return_value = "/path/to/baseline.json"

            scan_command(sample_args)

            mock_collector.save_baseline.assert_called_once_with(mock_metrics, "test_baseline")

    def test_scan_command_exception_handling(self, sample_args):
        """Test scan_command function handles exceptions gracefully."""
        with unittest.mock.patch(
            "strategy_sandbox.security.cli.SecurityCollector"
        ) as mock_collector_class:
            mock_collector_class.side_effect = Exception("Test exception")

            with pytest.raises(Exception):
                scan_command(sample_args)

    def test_report_command_basic(self, temp_dir):
        """Test report_command function with basic arguments."""
        args = argparse.Namespace()
        args.project_path = str(temp_dir)
        args.storage_path = str(temp_dir / "security_data")

        with unittest.mock.patch(
            "strategy_sandbox.security.cli.SecurityCollector"
        ) as mock_collector_class:
            report_command(args)

            mock_collector_class.assert_called_once_with(args.storage_path)

    def test_list_command_basic(self, temp_dir):
        """Test list_command function with basic arguments."""
        args = argparse.Namespace()
        args.storage_path = str(temp_dir / "security_data")

        with unittest.mock.patch(
            "strategy_sandbox.security.cli.SecurityCollector"
        ) as mock_collector_class:
            mock_collector = mock_collector_class.return_value
            mock_collector.get_historical_data.return_value = []

            list_command(args)

            mock_collector.get_historical_data.assert_called_once()

    def test_sbom_command_basic(self, temp_dir):
        """Test sbom_command function with basic arguments."""
        output_file = temp_dir / "sbom.json"

        args = argparse.Namespace()
        args.project_path = str(temp_dir)
        args.output = str(output_file)
        args.format = "json"
        args.include_dev = False

        with unittest.mock.patch("strategy_sandbox.security.cli.SBOMGenerator") as mock_sbom_class:
            mock_sbom = mock_sbom_class.return_value
            mock_sbom.generate_sbom.return_value = {"sbom": "data"}

            sbom_command(args)

            mock_sbom_class.assert_called_once_with(str(temp_dir))
            mock_sbom.generate_sbom.assert_called_once()

    def test_sbom_command_with_dev_dependencies(self, temp_dir):
        """Test sbom_command function with development dependencies."""
        output_file = temp_dir / "sbom.json"

        args = argparse.Namespace()
        args.project_path = str(temp_dir)
        args.output = str(output_file)
        args.format = "json"
        args.include_dev = True

        with unittest.mock.patch("strategy_sandbox.security.cli.SBOMGenerator") as mock_sbom_class:
            mock_sbom = mock_sbom_class.return_value
            mock_sbom.generate_sbom.return_value = {"sbom": "data"}

            sbom_command(args)

            mock_sbom.generate_sbom.assert_called_once()

    def test_main_file_not_found_error(self, temp_dir):
        """Test main function handles file not found errors gracefully."""
        nonexistent_file = temp_dir / "nonexistent.json"

        with unittest.mock.patch(
            "sys.argv", ["cli.py", "baseline", "--results", str(nonexistent_file), "--name", "test"]
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    def test_main_invalid_json_error(self, temp_dir):
        """Test main function handles invalid JSON files gracefully."""
        invalid_json_file = temp_dir / "invalid.json"
        with open(invalid_json_file, "w") as f:
            f.write("invalid json content")

        with unittest.mock.patch(
            "sys.argv",
            ["cli.py", "baseline", "--results", str(invalid_json_file), "--name", "test"],
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    def test_main_exception_handling(self, temp_dir):
        """Test main function handles unexpected exceptions gracefully."""
        with (
            unittest.mock.patch("sys.argv", ["cli.py", "scan", "--project-path", str(temp_dir)]),
            unittest.mock.patch("strategy_sandbox.security.cli.scan_command") as mock_scan,
        ):
            mock_scan.side_effect = Exception("Test exception")

            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    def test_main_invalid_command(self):
        """Test main function with invalid command."""
        with unittest.mock.patch("sys.argv", ["cli.py", "invalid-command"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code != 0
