"""Test suite for the reporting CLI module."""

import json
import tempfile
import unittest.mock
from pathlib import Path

import pytest

from strategy_sandbox.reporting.cli import main


class TestReportingCLI:
    """Test cases for the reporting CLI functionality."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def sample_test_results_file(self, temp_dir):
        """Create a sample test results file."""
        results = {"summary": {"total": 100, "passed": 95, "failed": 5, "skipped": 0}}
        results_file = temp_dir / "test_results.json"
        with open(results_file, "w") as f:
            json.dump(results, f)
        return results_file

    @pytest.fixture
    def sample_performance_results_file(self, temp_dir):
        """Create a sample performance results file."""
        results = {
            "benchmarks": [{"name": "test_benchmark", "min": 0.001, "max": 0.002, "mean": 0.0015}]
        }
        results_file = temp_dir / "performance_results.json"
        with open(results_file, "w") as f:
            json.dump(results, f)
        return results_file

    @pytest.fixture
    def sample_security_results_file(self, temp_dir):
        """Create a sample security results file."""
        results = {"metrics": {"CONFIDENCE.HIGH": 0, "CONFIDENCE.MEDIUM": 1, "CONFIDENCE.LOW": 0}}
        results_file = temp_dir / "security_results.json"
        with open(results_file, "w") as f:
            json.dump(results, f)
        return results_file

    def test_main_no_args(self):
        """Test main function with no arguments shows help."""
        with unittest.mock.patch("sys.argv", ["cli.py"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0  # Help command exits with 0

    def test_main_build_status_command(self, temp_dir):
        """Test main function with build-status command."""
        artifact_path = temp_dir / "artifacts"

        with (
            unittest.mock.patch(
                "sys.argv",
                [
                    "cli.py",
                    "build-status",
                    "--status",
                    "success",
                    "--artifact-path",
                    str(artifact_path),
                ],
            ),
            unittest.mock.patch("strategy_sandbox.reporting.cli.GitHubReporter") as mock_reporter,
        ):
            mock_instance = mock_reporter.return_value

            main()

            mock_reporter.assert_called_once_with(str(artifact_path))
            mock_instance.create_build_status_summary.assert_called_once()

    def test_main_build_status_with_test_results(self, temp_dir, sample_test_results_file):
        """Test main function with build-status command and test results."""
        artifact_path = temp_dir / "artifacts"

        with (
            unittest.mock.patch(
                "sys.argv",
                [
                    "cli.py",
                    "build-status",
                    "--status",
                    "failure",
                    "--test-results",
                    str(sample_test_results_file),
                    "--artifact-path",
                    str(artifact_path),
                ],
            ),
            unittest.mock.patch("strategy_sandbox.reporting.cli.GitHubReporter") as mock_reporter,
        ):
            mock_instance = mock_reporter.return_value

            main()

            mock_instance.create_build_status_summary.assert_called_once()

    def test_main_build_status_with_all_results(
        self,
        temp_dir,
        sample_test_results_file,
        sample_performance_results_file,
        sample_security_results_file,
    ):
        """Test main function with build-status command and all result files."""
        artifact_path = temp_dir / "artifacts"

        with (
            unittest.mock.patch(
                "sys.argv",
                [
                    "cli.py",
                    "build-status",
                    "--status",
                    "warning",
                    "--test-results",
                    str(sample_test_results_file),
                    "--performance-results",
                    str(sample_performance_results_file),
                    "--security-bandit",
                    str(sample_security_results_file),
                    "--security-pip-audit",
                    str(sample_security_results_file),
                    "--artifact-path",
                    str(artifact_path),
                ],
            ),
            unittest.mock.patch("strategy_sandbox.reporting.cli.GitHubReporter") as mock_reporter,
        ):
            mock_instance = mock_reporter.return_value

            main()

            mock_instance.create_build_status_summary.assert_called_once()

    def test_main_performance_command(self, temp_dir, sample_performance_results_file):
        """Test main function with performance command."""
        artifact_path = temp_dir / "artifacts"

        with (
            unittest.mock.patch(
                "sys.argv",
                [
                    "cli.py",
                    "performance",
                    "--results",
                    str(sample_performance_results_file),
                    "--artifact-path",
                    str(artifact_path),
                ],
            ),
            unittest.mock.patch("strategy_sandbox.reporting.cli.GitHubReporter") as mock_reporter,
        ):
            mock_instance = mock_reporter.return_value

            main()

            mock_reporter.assert_called_once_with(str(artifact_path))
            mock_instance.generate_performance_report.assert_called_once()

    def test_main_performance_with_baseline(self, temp_dir, sample_performance_results_file):
        """Test main function with performance command and baseline."""
        artifact_path = temp_dir / "artifacts"
        baseline_file = temp_dir / "baseline.json"

        # Create baseline file
        with open(baseline_file, "w") as f:
            json.dump({"benchmarks": []}, f)

        with (
            unittest.mock.patch(
                "sys.argv",
                [
                    "cli.py",
                    "performance",
                    "--results",
                    str(sample_performance_results_file),
                    "--baseline",
                    str(baseline_file),
                    "--artifact-path",
                    str(artifact_path),
                ],
            ),
            unittest.mock.patch("strategy_sandbox.reporting.cli.GitHubReporter") as mock_reporter,
        ):
            mock_instance = mock_reporter.return_value

            main()

            mock_instance.generate_performance_report.assert_called_once()

    def test_main_security_command(self, temp_dir, sample_security_results_file):
        """Test main function with security command."""
        artifact_path = temp_dir / "artifacts"

        with (
            unittest.mock.patch(
                "sys.argv",
                [
                    "cli.py",
                    "security",
                    "--bandit-results",
                    str(sample_security_results_file),
                    "--artifact-path",
                    str(artifact_path),
                ],
            ),
            unittest.mock.patch("strategy_sandbox.reporting.cli.GitHubReporter") as mock_reporter,
        ):
            mock_instance = mock_reporter.return_value

            main()

            mock_reporter.assert_called_once_with(str(artifact_path))
            mock_instance.generate_security_report.assert_called_once()

    def test_main_security_with_all_files(self, temp_dir, sample_security_results_file):
        """Test main function with security command and all security files."""
        artifact_path = temp_dir / "artifacts"

        with (
            unittest.mock.patch(
                "sys.argv",
                [
                    "cli.py",
                    "security",
                    "--bandit-results",
                    str(sample_security_results_file),
                    "--pip-audit-results",
                    str(sample_security_results_file),
                    "--safety-results",
                    str(sample_security_results_file),
                    "--artifact-path",
                    str(artifact_path),
                ],
            ),
            unittest.mock.patch("strategy_sandbox.reporting.cli.GitHubReporter") as mock_reporter,
        ):
            mock_instance = mock_reporter.return_value

            main()

            mock_instance.generate_security_report.assert_called_once()

    def test_main_env_info_command(self, temp_dir):
        """Test main function with env-info command."""
        artifact_path = temp_dir / "artifacts"

        with (
            unittest.mock.patch(
                "sys.argv", ["cli.py", "env-info", "--artifact-path", str(artifact_path)]
            ),
            unittest.mock.patch("strategy_sandbox.reporting.cli.GitHubReporter") as mock_reporter,
        ):
            mock_instance = mock_reporter.return_value
            mock_instance.get_environment_info.return_value = {"test": "info"}

            main()

            mock_reporter.assert_called_once_with(str(artifact_path))
            mock_instance.get_environment_info.assert_called_once()

    def test_main_artifacts_command(self, temp_dir):
        """Test main function with artifacts command."""
        artifact_path = temp_dir / "artifacts"

        with (
            unittest.mock.patch(
                "sys.argv", ["cli.py", "artifacts", "--artifact-path", str(artifact_path)]
            ),
            unittest.mock.patch("strategy_sandbox.reporting.cli.GitHubReporter") as mock_reporter,
        ):
            main()

            mock_reporter.assert_called_once_with(str(artifact_path))

    def test_main_artifacts_with_summary(self, temp_dir):
        """Test main function with artifacts command and summary."""
        artifact_path = temp_dir / "artifacts"

        with (
            unittest.mock.patch(
                "sys.argv",
                ["cli.py", "artifacts", "--artifact-path", str(artifact_path), "--summary-only"],
            ),
            unittest.mock.patch("strategy_sandbox.reporting.cli.GitHubReporter") as mock_reporter,
        ):
            main()

            mock_reporter.assert_called_once_with(str(artifact_path))

    def test_main_file_not_found_error(self, temp_dir):
        """Test main function handles file not found errors gracefully."""
        nonexistent_file = temp_dir / "nonexistent.json"

        with unittest.mock.patch(
            "sys.argv", ["cli.py", "performance", "--results", str(nonexistent_file)]
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
            "sys.argv", ["cli.py", "performance", "--results", str(invalid_json_file)]
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    def test_main_exception_handling(self, temp_dir, sample_performance_results_file):
        """Test main function handles unexpected exceptions gracefully."""
        with (
            unittest.mock.patch(
                "sys.argv",
                ["cli.py", "performance", "--results", str(sample_performance_results_file)],
            ),
            unittest.mock.patch("strategy_sandbox.reporting.cli.GitHubReporter") as mock_reporter,
        ):
            mock_reporter.side_effect = Exception("Test exception")

            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    def test_main_invalid_command(self):
        """Test main function with invalid command."""
        with unittest.mock.patch("sys.argv", ["cli.py", "invalid-command"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code != 0
