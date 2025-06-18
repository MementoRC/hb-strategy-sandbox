"""
End-to-end tests for CI pipeline functionality.

These tests validate the complete CI pipeline workflow including:
- Performance monitoring and regression detection
- Security scanning and vulnerability reporting
- GitHub Actions integration and reporting
- Artifact generation and validation
- Error handling and graceful degradation
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from tests.e2e.ci_simulator import CISimulator


@pytest.mark.e2e
class TestCIPipelineEndToEnd:
    """End-to-end tests for CI pipeline functionality."""

    @pytest.fixture
    def clean_environment(self):
        """Fixture providing completely clean environment for tests."""
        with patch.dict(os.environ, {}, clear=True):
            yield

    @pytest.fixture
    def github_environment(self):
        """Fixture simulating GitHub Actions environment."""
        github_vars = {
            "GITHUB_ACTIONS": "true",
            "CI": "true",
            "GITHUB_WORKFLOW": "CI",
            "GITHUB_RUN_ID": "12345",
            "GITHUB_RUN_NUMBER": "1",
            "GITHUB_REPOSITORY": "test/repo",
        }
        with patch.dict(os.environ, github_vars, clear=True):
            yield

    @pytest.fixture
    def test_repo(self):
        """Create temporary test repository."""
        repo_path = Path(tempfile.mkdtemp())
        yield repo_path
        # Cleanup handled by simulator

    @pytest.fixture
    def ci_simulator(self, test_repo):
        """Create CI simulator instance."""
        simulator = CISimulator(test_repo)
        yield simulator
        simulator.cleanup()

    def test_performance_monitoring_end_to_end(self, ci_simulator, clean_environment):
        """Test complete performance monitoring pipeline."""
        # Arrange: Add performance regression
        ci_simulator.add_performance_regression(severity="high")

        # Act: Run CI pipeline
        result = ci_simulator.run_ci_pipeline()

        # Assert: Verify regression detection
        assert result.success, f"Pipeline failed: {result.errors}"
        assert len(result.detected_regressions) > 0, "No performance regressions detected"
        assert any("test_slow_function" in reg for reg in result.detected_regressions)
        assert "performance_report.md" in result.artifacts

        # Verify performance report content
        perf_report = result.artifacts["performance_report.md"]
        assert "Performance" in perf_report
        assert "regression" in perf_report.lower()

    def test_security_scanning_end_to_end(self, ci_simulator, clean_environment):
        """Test complete security scanning pipeline."""
        # Arrange: Add vulnerable dependency
        ci_simulator.add_vulnerable_dependency(severity="high")

        # Act: Run CI pipeline
        result = ci_simulator.run_ci_pipeline()

        # Assert: Verify vulnerability detection
        assert result.success, f"Pipeline failed: {result.errors}"
        assert len(result.detected_vulnerabilities) > 0, "No vulnerabilities detected"
        assert any("requests" in vuln for vuln in result.detected_vulnerabilities)

        # Verify security artifacts
        assert "security_report.md" in result.artifacts

        # Verify security report content
        sec_report = result.artifacts["security_report.md"]
        assert "Security" in sec_report
        assert "vulnerability" in sec_report.lower() or "CVE" in sec_report

    def test_github_integration_end_to_end(self, ci_simulator, github_environment):
        """Test GitHub Actions integration pipeline."""
        # Arrange: Set up GitHub environment
        ci_simulator.setup_github_environment(enable=True)

        # Act: Run CI pipeline
        result = ci_simulator.run_ci_pipeline()

        # Assert: Verify GitHub integration
        assert result.success, f"Pipeline failed: {result.errors}"
        assert "step_summary.md" in result.artifacts, "GitHub step summary not generated"

        # Verify step summary content
        step_summary = result.step_summary
        assert "CI Pipeline Summary" in step_summary
        assert "Performance Summary" in step_summary
        assert "Security Summary" in step_summary
        assert "Build Summary" in step_summary

    def test_reporting_integration_end_to_end(self, ci_simulator, clean_environment):
        """Test that all reports are generated and integrated correctly."""
        # Act: Run CI pipeline without regressions or vulnerabilities
        result = ci_simulator.run_ci_pipeline()

        # Assert: Verify all core reports generated
        assert result.success, f"Pipeline failed: {result.errors}"

        expected_reports = ["performance_report.md", "security_report.md", "build_status.md"]

        for report in expected_reports:
            assert report in result.artifacts, f"Missing report: {report}"
            assert len(result.artifacts[report]) > 0, f"Empty report: {report}"

        # Verify build status report content
        build_report = result.artifacts["build_status.md"]
        assert "203 tests passed" in build_report or "Build" in build_report

    def test_multiple_issues_detection(self, ci_simulator, clean_environment):
        """Test detection of both performance and security issues."""
        # Arrange: Add both types of issues
        ci_simulator.add_performance_regression(severity="medium")
        ci_simulator.add_vulnerable_dependency(severity="high")

        # Act: Run CI pipeline
        result = ci_simulator.run_ci_pipeline()

        # Assert: Verify both issue types detected
        assert result.success, f"Pipeline failed: {result.errors}"
        assert len(result.detected_regressions) > 0, "Performance regressions not detected"
        assert len(result.detected_vulnerabilities) > 0, "Security vulnerabilities not detected"

        # Verify both report types exist
        assert "performance_report.md" in result.artifacts
        assert "security_report.md" in result.artifacts

    def test_clean_pipeline_run(self, ci_simulator, clean_environment):
        """Test pipeline run with no issues detected."""
        # Act: Run CI pipeline without adding any issues
        result = ci_simulator.run_ci_pipeline()

        # Assert: Verify clean run
        assert result.success, f"Pipeline failed: {result.errors}"
        assert len(result.detected_regressions) == 0, "False positive regressions detected"
        assert len(result.detected_vulnerabilities) == 0, "False positive vulnerabilities detected"

        # Verify reports still generated
        assert "performance_report.md" in result.artifacts
        assert "security_report.md" in result.artifacts
        assert "build_status.md" in result.artifacts

    def test_artifact_generation_validation(self, ci_simulator, clean_environment):
        """Test that all artifacts are properly generated and accessible."""
        # Arrange: Add some test data
        ci_simulator.add_performance_regression()
        ci_simulator.add_vulnerable_dependency()

        # Act: Run CI pipeline
        result = ci_simulator.run_ci_pipeline()

        # Assert: Verify artifact accessibility
        assert result.success, f"Pipeline failed: {result.errors}"

        # Check artifacts directory structure
        artifacts_dir = ci_simulator.artifacts_dir
        assert artifacts_dir.exists(), "Artifacts directory not created"

        # Verify artifact files exist
        for artifact_name in result.artifacts.keys():
            artifact_file = artifacts_dir / artifact_name
            assert artifact_file.exists(), f"Artifact file not found: {artifact_name}"

            # Verify file content matches result
            with open(artifact_file) as f:
                file_content = f.read()
            assert file_content == result.artifacts[artifact_name]

    def test_environment_isolation_consistency(self, ci_simulator):
        """Test that results are consistent across different environments."""
        # Test 1: Clean environment
        with patch.dict(os.environ, {}, clear=True):
            ci_simulator.add_performance_regression()
            result_clean = ci_simulator.run_ci_pipeline()

        # Reset simulator state but keep directory structure
        ci_simulator.has_performance_regression = False
        ci_simulator.has_vulnerable_dependency = False
        ci_simulator.github_environment = False

        # Test 2: GitHub environment
        with patch.dict(os.environ, {"GITHUB_ACTIONS": "true", "CI": "true"}, clear=True):
            ci_simulator.setup_github_environment(enable=True)
            ci_simulator.add_performance_regression()
            result_github = ci_simulator.run_ci_pipeline()

        # Assert: Core functionality should be consistent
        assert result_clean.success == result_github.success
        assert len(result_clean.detected_regressions) == len(result_github.detected_regressions)

        # GitHub environment should have additional step summary
        assert "step_summary.md" not in result_clean.artifacts
        assert "step_summary.md" in result_github.artifacts

    def test_error_handling_and_graceful_degradation(self, ci_simulator, clean_environment):
        """Test error handling and graceful degradation."""
        # Arrange: Simulate component failure by breaking test repo structure
        test_repo = ci_simulator.test_repo

        # Create invalid pyproject.toml
        invalid_config = "invalid toml content ["
        with open(test_repo / "pyproject.toml", "w") as f:
            f.write(invalid_config)

        # Act: Run pipeline (should handle errors gracefully)
        result = ci_simulator.run_ci_pipeline()

        # Assert: Pipeline should still complete with some functionality
        # Even with errors, some reports should still be generated
        assert "build_status.md" in result.artifacts  # Basic build report should work

        # Errors should be captured in result
        if not result.success:
            assert len(result.errors) > 0, "Errors occurred but not captured"

    def test_data_flow_integrity(self, ci_simulator, clean_environment):
        """Test that data flows correctly between pipeline components."""
        # Arrange: Set up test scenario
        ci_simulator.add_performance_regression(severity="high")
        ci_simulator.add_vulnerable_dependency(severity="critical")

        # Act: Run pipeline
        result = ci_simulator.run_ci_pipeline()

        # Assert: Verify data integrity throughout pipeline
        assert result.success, f"Pipeline failed: {result.errors}"

        # Verify performance data flow
        assert "regression_details" in result.performance_data
        regression_data = result.performance_data["regression_details"]
        assert "test_slow_function" in regression_data
        assert regression_data["test_slow_function"]["ratio"] > 1.0

        # Verify security data flow
        assert "vulnerabilities" in result.security_data
        vulnerabilities = result.security_data["vulnerabilities"]
        assert len(vulnerabilities) > 0
        assert all("package" in vuln for vuln in vulnerabilities)

        # Verify data consistency in reports
        perf_report = result.artifacts.get("performance_report.md", "")
        sec_report = result.artifacts.get("security_report.md", "")

        # Performance data should be reflected in performance report
        assert "regression" in perf_report.lower() or "performance" in perf_report.lower()

        # Security data should be reflected in security report
        assert "vulnerability" in sec_report.lower() or "security" in sec_report.lower()

    def test_format_compatibility_validation(self, ci_simulator, clean_environment):
        """Test different output formats and their compatibility."""
        # Arrange: Add test data
        ci_simulator.add_vulnerable_dependency()

        # Act: Run pipeline
        result = ci_simulator.run_ci_pipeline()

        # Assert: Verify format compatibility
        assert result.success, f"Pipeline failed: {result.errors}"

        # Check that artifacts contain expected formats
        artifacts = result.artifacts

        # Markdown reports should be valid markdown
        for name, content in artifacts.items():
            if name.endswith(".md"):
                assert "#" in content or "*" in content, f"Invalid markdown in {name}"

        # Verify JSON data structure in performance data
        if "benchmarks" in result.performance_data:
            # Should be valid JSON-serializable
            try:
                json.dumps(result.performance_data["benchmarks"])
            except Exception as e:
                pytest.fail(f"Performance data not JSON serializable: {e}")

        # Verify security data structure
        if "vulnerabilities" in result.security_data:
            vulnerabilities = result.security_data["vulnerabilities"]
            for vuln in vulnerabilities:
                required_fields = ["package", "version", "vulnerability", "severity"]
                for field in required_fields:
                    assert field in vuln, f"Missing required field {field} in vulnerability data"


@pytest.mark.e2e
class TestCIPipelineIntegration:
    """Test integration points between CI components."""

    @pytest.fixture
    def ci_simulator(self):
        """Create CI simulator for integration tests."""
        simulator = CISimulator()
        yield simulator
        simulator.cleanup()

    def test_performance_to_reporting_integration(self, ci_simulator):
        """Test integration between performance collection and reporting."""
        # Arrange
        ci_simulator.add_performance_regression(severity="high")

        # Act
        result = ci_simulator.run_ci_pipeline()

        # Assert: Performance data should flow to reporting
        assert result.success, f"Pipeline failed: {result.errors}"
        assert "performance_report.md" in result.artifacts

        # Verify performance data is integrated into report
        perf_report = result.artifacts["performance_report.md"]
        assert len(perf_report) > 0
        assert "performance" in perf_report.lower() or "benchmark" in perf_report.lower()

    def test_security_to_dashboard_integration(self, ci_simulator):
        """Test integration between security analysis and dashboard generation."""
        # Arrange
        ci_simulator.add_vulnerable_dependency(severity="critical")

        # Act
        result = ci_simulator.run_ci_pipeline()

        # Assert: Security data should flow to dashboard
        assert result.success, f"Pipeline failed: {result.errors}"
        assert "security_report.md" in result.artifacts

        # Verify security dashboard includes vulnerability data
        sec_report = result.artifacts["security_report.md"]
        assert len(sec_report) > 0
        assert "security" in sec_report.lower() or "vulnerability" in sec_report.lower()

    def test_trend_analysis_integration(self, ci_simulator):
        """Test integration of trend analysis with performance data."""
        # Arrange
        ci_simulator.add_performance_regression(severity="medium")

        # Act
        result = ci_simulator.run_ci_pipeline()

        # Assert: Trend analysis should process performance data
        assert result.success, f"Pipeline failed: {result.errors}"

        # Verify regression detection worked
        assert len(result.detected_regressions) > 0
        assert any("2.5x slower" in reg for reg in result.detected_regressions)

    def test_multi_component_error_handling(self, ci_simulator):
        """Test error handling across multiple components."""
        # This test verifies that if one component fails, others continue
        # The specific failure simulation would depend on implementation details

        # Act: Run pipeline (components should handle missing data gracefully)
        result = ci_simulator.run_ci_pipeline()

        # Assert: Basic pipeline should complete even with some component issues
        # At minimum, build status should be generated
        assert "build_status.md" in result.artifacts
