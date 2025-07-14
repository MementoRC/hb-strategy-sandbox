"""Test suite for the performance CLI module."""

import json
import tempfile
import unittest.mock
from pathlib import Path

import pytest

from strategy_sandbox.performance.cli import main


class TestPerformanceCLI:
    """Test cases for the performance CLI functionality."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def sample_results_file(self, temp_dir):
        """Create a sample benchmark results file."""
        results = {
            "benchmarks": [
                {
                    "name": "test_benchmark",
                    "min": 0.001,
                    "max": 0.002,
                    "mean": 0.0015,
                    "stddev": 0.0001,
                    "rounds": 10,
                    "median": 0.0015,
                    "stats": {"ops": 666.67},
                }
            ]
        }
        results_file = temp_dir / "results.json"
        with open(results_file, "w") as f:
            json.dump(results, f)
        return results_file

    def test_main_no_args(self):
        """Test main function with no arguments shows help."""
        with unittest.mock.patch("sys.argv", ["cli.py"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0  # Help command exits with 0

    def test_main_collect_command(self, temp_dir, sample_results_file):
        """Test main function with collect command."""
        storage_path = temp_dir / "performance_data"

        with (
            unittest.mock.patch(
                "sys.argv",
                [
                    "cli.py",
                    "collect",
                    "--results",
                    str(sample_results_file),
                    "--storage-path",
                    str(storage_path),
                ],
            ),
            unittest.mock.patch(
                "strategy_sandbox.performance.cli.PerformanceCollector"
            ) as mock_collector,
        ):
            mock_instance = mock_collector.return_value
            mock_instance.collect_benchmark_data.return_value = {"test": "data"}

            main()

            mock_collector.assert_called_once_with(str(storage_path))
            mock_instance.collect_benchmark_data.assert_called_once()

    def test_main_collect_with_baseline(self, temp_dir, sample_results_file):
        """Test main function with collect command storing baseline."""
        storage_path = temp_dir / "performance_data"

        with (
            unittest.mock.patch(
                "sys.argv",
                [
                    "cli.py",
                    "collect",
                    "--results",
                    str(sample_results_file),
                    "--storage-path",
                    str(storage_path),
                    "--store-baseline",
                    "--baseline-name",
                    "test_baseline",
                ],
            ),
            unittest.mock.patch(
                "strategy_sandbox.performance.cli.PerformanceCollector"
            ) as mock_collector,
        ):
            mock_instance = mock_collector.return_value
            mock_instance.collect_benchmark_data.return_value = {"test": "data"}

            main()

            mock_instance.collect_benchmark_data.assert_called_once()
            mock_instance.store_baseline.assert_called_once_with({"test": "data"}, "test_baseline")

    def test_main_collect_with_comparison(self, temp_dir, sample_results_file):
        """Test main function with collect command and baseline comparison."""
        storage_path = temp_dir / "performance_data"

        with (
            unittest.mock.patch(
                "sys.argv",
                [
                    "cli.py",
                    "collect",
                    "--results",
                    str(sample_results_file),
                    "--storage-path",
                    str(storage_path),
                    "--compare-baseline",
                    "test_baseline",
                ],
            ),
            unittest.mock.patch(
                "strategy_sandbox.performance.cli.PerformanceCollector"
            ) as mock_collector,
        ):
            mock_instance = mock_collector.return_value
            mock_instance.collect_benchmark_data.return_value = {"test": "data"}
            mock_instance.compare_with_baseline.return_value = {"comparison": "result"}

            main()

            mock_instance.collect_benchmark_data.assert_called_once()
            mock_instance.compare_with_baseline.assert_called_once_with(
                {"test": "data"}, "test_baseline"
            )

    def test_main_collect_with_output(self, temp_dir, sample_results_file):
        """Test main function with collect command and output file."""
        storage_path = temp_dir / "performance_data"
        output_file = temp_dir / "output.json"

        with (
            unittest.mock.patch(
                "sys.argv",
                [
                    "cli.py",
                    "collect",
                    "--results",
                    str(sample_results_file),
                    "--storage-path",
                    str(storage_path),
                    "--output",
                    str(output_file),
                ],
            ),
            unittest.mock.patch(
                "strategy_sandbox.performance.cli.PerformanceCollector"
            ) as mock_collector,
        ):
            mock_instance = mock_collector.return_value
            mock_instance.collect_benchmark_data.return_value = {"test": "data"}

            with unittest.mock.patch("builtins.open", unittest.mock.mock_open()) as mock_file:
                main()

                mock_file.assert_called_once_with(str(output_file), "w")

    def test_main_compare_command(self, temp_dir):
        """Test main function with compare command."""
        results1 = temp_dir / "results1.json"
        results2 = temp_dir / "results2.json"

        # Create sample files
        for results_file in [results1, results2]:
            with open(results_file, "w") as f:
                json.dump({"benchmarks": []}, f)

        with (
            unittest.mock.patch(
                "sys.argv",
                ["cli.py", "compare", "--current", str(results1), "--baseline", str(results2)],
            ),
            unittest.mock.patch(
                "strategy_sandbox.performance.cli.PerformanceComparator"
            ) as mock_comparator,
        ):
            mock_instance = mock_comparator.return_value
            mock_instance.compare.return_value = {"comparison": "result"}

            main()

            mock_comparator.assert_called_once()
            mock_instance.compare.assert_called_once()

    def test_main_compare_with_mode(self, temp_dir):
        """Test main function with compare command and specific mode."""
        results1 = temp_dir / "results1.json"
        results2 = temp_dir / "results2.json"

        # Create sample files
        for results_file in [results1, results2]:
            with open(results_file, "w") as f:
                json.dump({"benchmarks": []}, f)

        with (
            unittest.mock.patch(
                "sys.argv",
                [
                    "cli.py",
                    "compare",
                    "--current",
                    str(results1),
                    "--baseline",
                    str(results2),
                    "--mode",
                    "statistical",
                ],
            ),
            unittest.mock.patch(
                "strategy_sandbox.performance.cli.PerformanceComparator"
            ) as mock_comparator,
        ):
            mock_instance = mock_comparator.return_value
            mock_instance.compare.return_value = {"comparison": "result"}

            main()

            mock_comparator.assert_called_once()

    def test_main_baseline_command(self, temp_dir, sample_results_file):
        """Test main function with baseline command."""
        storage_path = temp_dir / "performance_data"

        with (
            unittest.mock.patch(
                "sys.argv",
                [
                    "cli.py",
                    "baseline",
                    "--results",
                    str(sample_results_file),
                    "--storage-path",
                    str(storage_path),
                    "--name",
                    "test_baseline",
                ],
            ),
            unittest.mock.patch(
                "strategy_sandbox.performance.cli.PerformanceCollector"
            ) as mock_collector,
        ):
            mock_instance = mock_collector.return_value
            mock_instance.collect_benchmark_data.return_value = {"test": "data"}

            main()

            mock_instance.store_baseline.assert_called_once_with({"test": "data"}, "test_baseline")

    def test_main_history_command(self, temp_dir):
        """Test main function with history command."""
        storage_path = temp_dir / "performance_data"

        with (
            unittest.mock.patch(
                "sys.argv", ["cli.py", "history", "--storage-path", str(storage_path)]
            ),
            unittest.mock.patch(
                "strategy_sandbox.performance.cli.PerformanceCollector"
            ) as mock_collector,
        ):
            mock_instance = mock_collector.return_value
            mock_instance.get_historical_data.return_value = []

            main()

            mock_instance.get_historical_data.assert_called_once()

    def test_main_history_with_baseline_filter(self, temp_dir):
        """Test main function with history command and baseline filter."""
        storage_path = temp_dir / "performance_data"

        with (
            unittest.mock.patch(
                "sys.argv",
                [
                    "cli.py",
                    "history",
                    "--storage-path",
                    str(storage_path),
                    "--baseline-name",
                    "test_baseline",
                ],
            ),
            unittest.mock.patch(
                "strategy_sandbox.performance.cli.PerformanceCollector"
            ) as mock_collector,
        ):
            mock_instance = mock_collector.return_value
            mock_instance.get_historical_data.return_value = []

            main()

            mock_instance.get_historical_data.assert_called_once_with("test_baseline")

    def test_main_file_not_found_error(self, temp_dir):
        """Test main function handles file not found errors gracefully."""
        nonexistent_file = temp_dir / "nonexistent.json"

        with unittest.mock.patch(
            "sys.argv", ["cli.py", "collect", "--results", str(nonexistent_file)]
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
            "sys.argv", ["cli.py", "collect", "--results", str(invalid_json_file)]
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    def test_main_exception_handling(self, temp_dir, sample_results_file):
        """Test main function handles unexpected exceptions gracefully."""
        with (
            unittest.mock.patch(
                "sys.argv", ["cli.py", "collect", "--results", str(sample_results_file)]
            ),
            unittest.mock.patch(
                "strategy_sandbox.performance.cli.PerformanceCollector"
            ) as mock_collector,
        ):
            mock_collector.side_effect = Exception("Test exception")

            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1
