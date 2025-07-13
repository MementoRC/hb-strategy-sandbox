"""Test suite for the security collector module."""

import json
import tempfile
import unittest.mock
from datetime import datetime
from pathlib import Path

import pytest

from strategy_sandbox.security.collector import SecurityCollector
from strategy_sandbox.security.models import SecurityMetrics


class TestSecurityCollector:
    """Test cases for the SecurityCollector class."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def collector(self, temp_dir):
        """Create a SecurityCollector instance with temporary storage."""
        return SecurityCollector(temp_dir / "security_data")

    @pytest.fixture
    def sample_metrics(self):
        """Create sample security metrics."""
        return SecurityMetrics(
            project_path="/test/path",
            scan_timestamp=datetime.now(),
            build_id="test_build_123",
            dependencies={"test-package": "1.0.0"},
            vulnerabilities=[],
            package_managers=["pip"],
            environment_info={"python_version": "3.12.0"},
        )

    def test_init_default_storage_path(self):
        """Test SecurityCollector initialization with default storage path."""
        collector = SecurityCollector()
        assert collector.storage_path == Path("security_data")
        assert collector.baseline_path == Path("security_data") / "baselines"
        assert collector.history_path == Path("security_data") / "history"

    def test_init_custom_storage_path(self, temp_dir):
        """Test SecurityCollector initialization with custom storage path."""
        storage_path = temp_dir / "custom_security"
        collector = SecurityCollector(storage_path)
        assert collector.storage_path == storage_path
        assert collector.baseline_path == storage_path / "baselines"
        assert collector.history_path == storage_path / "history"

    def test_init_creates_directories(self, temp_dir):
        """Test SecurityCollector initialization creates required directories."""
        storage_path = temp_dir / "security_data"
        collector = SecurityCollector(storage_path)

        assert collector.storage_path.exists()
        assert collector.baseline_path.exists()
        assert collector.history_path.exists()

    def test_collect_environment_info(self, collector):
        """Test collect_environment_info method."""
        with unittest.mock.patch("platform.platform", return_value="Linux-5.4.0"):
            with unittest.mock.patch("platform.python_version", return_value="3.12.0"):
                with unittest.mock.patch("platform.node", return_value="test-host"):
                    env_info = collector.collect_environment_info()

                    assert env_info["platform"] == "Linux-5.4.0"
                    assert env_info["python_version"] == "3.12.0"
                    assert env_info["hostname"] == "test-host"

    def test_collect_environment_info_with_ci_vars(self, collector):
        """Test collect_environment_info method with CI environment variables."""
        ci_env = {
            "GITHUB_ACTIONS": "true",
            "GITHUB_WORKFLOW": "CI",
            "GITHUB_RUN_ID": "123456",
            "GITHUB_REPOSITORY": "user/repo",
        }

        with unittest.mock.patch("platform.platform", return_value="Linux"):
            with unittest.mock.patch("platform.python_version", return_value="3.12.0"):
                with unittest.mock.patch("platform.node", return_value="test-host"):
                    with unittest.mock.patch.dict("os.environ", ci_env):
                        env_info = collector.collect_environment_info()

                        assert env_info["GITHUB_ACTIONS"] == "true"
                        assert env_info["GITHUB_WORKFLOW"] == "CI"
                        assert env_info["GITHUB_RUN_ID"] == "123456"
                        assert env_info["GITHUB_REPOSITORY"] == "user/repo"

    def test_scan_project_security(self, collector, temp_dir):
        """Test scan_project_security method."""
        project_path = temp_dir / "test_project"
        project_path.mkdir()

        # Create a requirements.txt file
        requirements_file = project_path / "requirements.txt"
        requirements_file.write_text("requests==2.28.0\n")

        with unittest.mock.patch(
            "strategy_sandbox.security.collector.DependencyAnalyzer"
        ) as mock_analyzer_class:
            mock_analyzer = mock_analyzer_class.return_value
            mock_analyzer.scan_dependencies.return_value = {"requests": "2.28.0"}
            mock_analyzer.analyze_vulnerabilities.return_value = []

            with unittest.mock.patch.object(collector, "collect_environment_info") as mock_env:
                mock_env.return_value = {"python_version": "3.12.0"}

                metrics = collector.scan_project_security(
                    project_path=str(project_path),
                    build_id="test_build_123",
                    package_managers=["pip"],
                )

                assert isinstance(metrics, SecurityMetrics)
                assert metrics.project_path == str(project_path)
                assert metrics.build_id == "test_build_123"
                assert metrics.package_managers == ["pip"]
                mock_analyzer.scan_dependencies.assert_called_once()
                mock_analyzer.analyze_vulnerabilities.assert_called_once()

    def test_save_metrics(self, collector, sample_metrics):
        """Test save_metrics method."""
        metrics_file = collector.save_metrics(sample_metrics)

        assert metrics_file.exists()
        assert metrics_file.parent == collector.storage_path

        # Verify the file contains the correct data
        with open(metrics_file) as f:
            saved_data = json.load(f)

        assert saved_data["project_path"] == sample_metrics.project_path
        assert saved_data["build_id"] == sample_metrics.build_id

    def test_save_baseline(self, collector, sample_metrics):
        """Test save_baseline method."""
        baseline_name = "test_baseline"
        baseline_file = collector.save_baseline(sample_metrics, baseline_name)

        assert baseline_file.exists()
        assert baseline_file.parent == collector.baseline_path
        assert baseline_file.name == f"{baseline_name}.json"

        # Verify the file contains the correct data
        with open(baseline_file) as f:
            saved_data = json.load(f)

        assert saved_data["project_path"] == sample_metrics.project_path
        assert saved_data["build_id"] == sample_metrics.build_id

    def test_load_baseline(self, collector, sample_metrics):
        """Test load_baseline method."""
        baseline_name = "test_baseline"

        # First save a baseline
        collector.save_baseline(sample_metrics, baseline_name)

        # Then load it
        loaded_metrics = collector.load_baseline(baseline_name)

        assert isinstance(loaded_metrics, SecurityMetrics)
        assert loaded_metrics.project_path == sample_metrics.project_path
        assert loaded_metrics.build_id == sample_metrics.build_id

    def test_load_baseline_not_found(self, collector):
        """Test load_baseline method with non-existent baseline."""
        with pytest.raises(FileNotFoundError):
            collector.load_baseline("nonexistent_baseline")

    def test_compare_with_baseline(self, collector, sample_metrics):
        """Test compare_with_baseline method."""
        baseline_name = "test_baseline"

        # Save a baseline
        collector.save_baseline(sample_metrics, baseline_name)

        # Create slightly different current metrics
        current_metrics = SecurityMetrics(
            project_path="/test/path",
            scan_timestamp=datetime.now(),
            build_id="test_build_124",
            dependencies={"test-package": "1.1.0"},  # Different version
            vulnerabilities=[],
            package_managers=["pip"],
            environment_info={"python_version": "3.12.0"},
        )

        comparison = collector.compare_with_baseline(current_metrics, baseline_name)

        assert "baseline_info" in comparison
        assert "current_info" in comparison
        assert "comparison" in comparison

    def test_get_historical_data(self, collector, sample_metrics):
        """Test get_historical_data method."""
        # Save some metrics to create history
        collector.save_metrics(sample_metrics)

        historical_data = collector.get_historical_data(limit=10)

        assert isinstance(historical_data, list)
        assert len(historical_data) > 0
        assert all(isinstance(item, SecurityMetrics) for item in historical_data)

    def test_get_historical_data_with_baseline_filter(self, collector, sample_metrics):
        """Test get_historical_data method with baseline filter."""
        baseline_name = "test_baseline"

        # Save a baseline
        collector.save_baseline(sample_metrics, baseline_name)

        historical_data = collector.get_historical_data(baseline_name=baseline_name, limit=10)

        assert isinstance(historical_data, list)

    def test_get_historical_data_empty(self, collector):
        """Test get_historical_data method with empty history."""
        historical_data = collector.get_historical_data(limit=10)

        assert isinstance(historical_data, list)
        assert len(historical_data) == 0

    def test_scan_project_security_with_multiple_package_managers(self, collector, temp_dir):
        """Test scan_project_security method with multiple package managers."""
        project_path = temp_dir / "test_project"
        project_path.mkdir()

        # Create files for different package managers
        (project_path / "requirements.txt").write_text("requests==2.28.0\n")
        (project_path / "package.json").write_text('{"dependencies": {"lodash": "4.17.21"}}\n')

        with unittest.mock.patch(
            "strategy_sandbox.security.collector.DependencyAnalyzer"
        ) as mock_analyzer_class:
            mock_analyzer = mock_analyzer_class.return_value
            mock_analyzer.scan_dependencies.return_value = {
                "requests": "2.28.0",
                "lodash": "4.17.21",
            }
            mock_analyzer.analyze_vulnerabilities.return_value = []

            with unittest.mock.patch.object(collector, "collect_environment_info") as mock_env:
                mock_env.return_value = {"python_version": "3.12.0"}

                metrics = collector.scan_project_security(
                    project_path=str(project_path),
                    build_id="test_build_123",
                    package_managers=["pip", "npm"],
                )

                assert metrics.package_managers == ["pip", "npm"]

    def test_scan_project_security_exception_handling(self, collector, temp_dir):
        """Test scan_project_security method handles exceptions gracefully."""
        project_path = temp_dir / "test_project"
        project_path.mkdir()

        with unittest.mock.patch(
            "strategy_sandbox.security.collector.DependencyAnalyzer"
        ) as mock_analyzer_class:
            mock_analyzer_class.side_effect = Exception("Test exception")

            with pytest.raises((Exception, ValueError, RuntimeError)):
                collector.scan_project_security(
                    project_path=str(project_path),
                    build_id="test_build_123",
                    package_managers=["pip"],
                )

    def test_save_metrics_creates_directories(self, temp_dir):
        """Test save_metrics creates storage directories if they don't exist."""
        storage_path = temp_dir / "new_security_data"
        collector = SecurityCollector(storage_path)

        # Remove the directories
        import shutil

        shutil.rmtree(storage_path)

        sample_metrics = SecurityMetrics(
            project_path="/test/path",
            scan_timestamp=datetime.now(),
            build_id="test_build_123",
            dependencies={},
            vulnerabilities=[],
            package_managers=["pip"],
            environment_info={},
        )

        metrics_file = collector.save_metrics(sample_metrics)

        assert metrics_file.exists()
        assert storage_path.exists()

    def test_compare_with_baseline_calculates_differences(self, collector, sample_metrics):
        """Test compare_with_baseline calculates meaningful differences."""
        baseline_name = "test_baseline"

        # Save a baseline with specific vulnerabilities
        baseline_metrics = SecurityMetrics(
            project_path="/test/path",
            scan_timestamp=datetime.now(),
            build_id="baseline_build",
            dependencies={"package1": "1.0.0", "package2": "2.0.0"},
            vulnerabilities=[],
            package_managers=["pip"],
            environment_info={"python_version": "3.12.0"},
        )
        collector.save_baseline(baseline_metrics, baseline_name)

        # Create current metrics with different dependencies
        current_metrics = SecurityMetrics(
            project_path="/test/path",
            scan_timestamp=datetime.now(),
            build_id="current_build",
            dependencies={"package1": "1.1.0", "package3": "3.0.0"},  # Changed and new packages
            vulnerabilities=[],
            package_managers=["pip"],
            environment_info={"python_version": "3.12.0"},
        )

        comparison = collector.compare_with_baseline(current_metrics, baseline_name)

        assert "baseline_info" in comparison
        assert "current_info" in comparison
        assert "comparison" in comparison

        # Verify comparison contains dependency differences
        comparison_data = comparison["comparison"]
        assert "dependency_changes" in comparison_data or "summary" in comparison_data
