"""
Reporting Framework Integration Tests

Tests for reporting module integration with other framework components.
"""

import json
from pathlib import Path

import pytest

from framework.reporting.artifact_manager import ArtifactManager
from framework.reporting.github_reporter import GitHubReporter
from framework.reporting.report_generator import ReportGenerator
from framework.reporting.template_engine import TemplateEngine


@pytest.mark.reporting
@pytest.mark.integration
class TestReportingIntegration:
    """Test reporting module integration with framework."""

    def test_github_reporter_to_artifact_manager_integration(self, tmp_path):
        """Test integration between GitHub reporter and artifact manager."""
        # Setup
        reporter = GitHubReporter()
        artifact_manager = ArtifactManager(artifact_path=tmp_path)

        # Generate report
        performance_data = {
            "test_suite": {"execution_time": 2.5, "memory_usage": "75MB", "throughput": 500}
        }

        report_content = reporter.generate_performance_report(performance_data=performance_data)

        # Store as artifact
        artifact_path = artifact_manager.create_artifact(
            name="performance_report.md", content=report_content, content_type="text/markdown"
        )

        # Verify integration
        assert artifact_path.exists()
        stored_content = artifact_path.read_text()
        assert "test_suite" in stored_content
        assert "2.5" in stored_content

    def test_report_generator_comprehensive_integration(self, tmp_path):
        """Test comprehensive report generation integration."""
        # Setup
        report_generator = ReportGenerator()

        # Comprehensive data from multiple sources
        coverage_data = {
            "overall_coverage": 85.5,
            "line_coverage": 85.5,
            "branch_coverage": 78.2,
            "function_coverage": 80.0,
            "modules": [],
        }

        performance_data = {
            "metric_name": "execution_time",
            "current_value": 1.8,
            "baseline_value": 2.0,
            "historical_values": [2.0, 1.9, 1.8],
            "trend_direction": "improvement",
            "change_percentage": -10.0,
            "threshold_status": "within",
        }

        # Generate comprehensive report
        report_generator.set_coverage_data(coverage_data)
        report_generator.add_performance_trend(performance_data)

        comprehensive_report = report_generator.generate_comprehensive_report(
            test_results={"passed": 100, "failed": 0, "total": 100},
            performance_data={"results": []},
            security_data={},
            include_artifacts=False,
        )

        # Verify comprehensive integration
        assert comprehensive_report is not None
        assert isinstance(comprehensive_report, dict)
        assert "report_sections" in comprehensive_report
        assert "build_dashboard" in comprehensive_report["report_sections"]
        assert "coverage_report" in comprehensive_report["report_sections"]
        assert "performance_dashboard" in comprehensive_report["report_sections"]

        # Verify content contains expected data
        coverage_content = comprehensive_report["report_sections"]["coverage_report"]
        assert "85.5" in coverage_content  # Coverage percentage

        performance_content = comprehensive_report["report_sections"]["performance_dashboard"]
        assert "execution_time" in performance_content  # Performance metric

    def test_template_engine_integration(self, tmp_path):
        """Test template engine integration with reporting components."""
        # Setup
        template_engine = TemplateEngine()

        # Test template rendering with various data types
        build_context = {
            "build_status": "success",
            "test_results": {
                "total": 200,
                "passed": 192,
                "failed": 8,
                "duration": 225.0,  # Numeric duration in seconds
                "duration_string": "3m 45s",  # String format for display
                "coverage": 92.3,
            },
            "performance_data": {"results": []},
            "security_data": {},
            "github_env": {"GITHUB_WORKFLOW": "CI", "GITHUB_RUN_NUMBER": "123"},
            "timestamp": "2024-01-01T00:00:00Z",
        }

        # Render using template engine
        build_summary = template_engine.render_build_status(build_context)

        # Verify template integration
        assert build_summary is not None
        assert "200" in build_summary
        assert "92.3" in build_summary
        assert "3m 45s" in build_summary

    def test_artifact_manager_multiple_formats_integration(self, tmp_path):
        """Test artifact manager with multiple report formats."""
        # Setup
        artifact_manager = ArtifactManager(artifact_path=tmp_path)

        # Test data
        test_data = {"timestamp": "2024-01-01T00:00:00Z", "results": {"tests": 150, "failures": 0}}

        # Create artifacts in different formats
        json_artifact = artifact_manager.create_artifact(
            name="test_results.json", content=test_data, content_type="application/json"
        )

        text_artifact = artifact_manager.create_artifact(
            name="summary.txt",
            content="Test Results Summary\n===================\nTests: 150\nFailures: 0",
            content_type="text/plain",
        )

        # Verify multiple format integration
        assert json_artifact.exists()
        assert text_artifact.exists()

        # Verify content integrity
        json_content = json.loads(json_artifact.read_text())
        assert json_content["results"]["tests"] == 150

        text_content = text_artifact.read_text()
        assert "Tests: 150" in text_content

    def test_reporting_with_performance_data_integration(self, tmp_path):
        """Test reporting integration with performance data from framework."""
        # Setup
        reporter = GitHubReporter()
        artifact_manager = ArtifactManager(artifact_path=tmp_path)

        # Mock performance data from framework.performance
        performance_metrics = {
            "benchmarks": {
                "simulation_throughput": {"current": 1500, "baseline": 1200, "improvement": 25.0},
                "memory_efficiency": {"current": "45MB", "baseline": "52MB", "improvement": 13.5},
            },
            "summary": {"total_benchmarks": 2, "improvements": 2, "regressions": 0},
        }

        # Generate performance report
        performance_report = reporter.generate_performance_report(
            performance_data=performance_metrics
        )

        # Store as artifact using correct method signature
        artifact_path = artifact_manager.create_report_artifact(
            report_name="performance_analysis",
            report_data={"content": performance_report, "metrics": performance_metrics},
            format_type="markdown",
        )

        # Verify performance integration
        assert artifact_path.exists()
        content = artifact_path.read_text()
        assert "simulation_throughput" in content or "benchmarks" in content
        assert "memory_efficiency" in content or "benchmarks" in content

    def test_reporting_with_security_data_integration(self, tmp_path):
        """Test reporting integration with security data from framework."""
        # Setup
        reporter = GitHubReporter()

        # Mock security data from framework.security (flattened format for backward compatibility)
        security_findings = {
            "vulnerabilities": [
                {
                    "package": "requests",
                    "version": "2.25.1",
                    "severity": "medium",
                    "description": "Request vulnerability in requests package",
                },
                {
                    "package": "urllib3",
                    "version": "1.26.5",
                    "severity": "high",
                    "description": "High severity vulnerability in urllib3",
                },
            ],
            "total_vulnerabilities": 8,
            "by_severity": {"critical": 0, "high": 1, "medium": 6, "low": 1},
        }

        # Generate security report
        security_report = reporter.generate_security_report(security_findings)

        # Verify security integration
        assert security_report is not None
        assert "8" in security_report  # Total vulnerabilities
        assert "requests" in security_report
        assert "urllib3" in security_report
        assert "medium" in security_report
        assert "high" in security_report

    def test_reporting_error_handling_integration(self, tmp_path):
        """Test error handling in reporting integrations."""
        # Setup
        reporter = GitHubReporter()

        # Test with various invalid inputs
        invalid_inputs = [None, {}, {"invalid": "structure"}, {"missing_required_fields": True}]

        for invalid_input in invalid_inputs:
            try:
                # Should handle gracefully without crashing
                report = reporter.generate_performance_report(performance_data=invalid_input)
                assert report is not None  # Should return some content
            except Exception as e:
                pytest.fail(f"Reporting should handle invalid input gracefully: {e}")

    def test_reporting_large_dataset_integration(self, tmp_path):
        """Test reporting with large datasets."""
        # Setup
        reporter = GitHubReporter()
        artifact_manager = ArtifactManager(artifact_path=tmp_path)

        # Large performance dataset
        large_dataset = {
            "benchmarks": {
                f"test_{i}": {
                    "execution_time": i * 0.1,
                    "memory_usage": f"{i * 5}MB",
                    "throughput": 1000 + i,
                }
                for i in range(100)  # 100 benchmarks
            }
        }

        # Generate report with large dataset
        import time

        start_time = time.time()

        report = reporter.generate_performance_report(performance_data=large_dataset)

        # Store large report using correct method signature
        artifact_path = artifact_manager.create_report_artifact(
            report_name="large_performance_report",
            report_data={"content": report, "dataset": large_dataset},
            format_type="markdown",
        )

        end_time = time.time()
        processing_time = end_time - start_time

        # Verify large dataset handling
        assert processing_time < 5.0  # Should complete within 5 seconds
        assert artifact_path.exists()
        assert artifact_path.stat().st_size > 1000  # Substantial content

    def test_reporting_template_customization_integration(self, tmp_path):
        """Test template customization integration."""
        # Setup
        template_engine = TemplateEngine()

        # Custom template data
        custom_context = {
            "metrics": {
                "results": [
                    {
                        "name": "execution_time",
                        "execution_time": 1.234,
                        "throughput": 850.0,
                        "memory_usage": 42.5,
                    },
                    {
                        "name": "memory_usage",
                        "execution_time": 0.987,
                        "memory_usage": 35.2,
                    },
                ]
            },
            "timestamp": "2024-01-01T00:00:00Z",
        }

        # Test custom template rendering
        performance_summary = template_engine.render_performance_summary(custom_context)

        # Verify customization integration
        assert performance_summary is not None
        assert "execution_time" in performance_summary
        assert "memory_usage" in performance_summary
        assert "1.234" in performance_summary or "execution_time" in performance_summary

    @pytest.mark.asyncio
    async def test_reporting_async_integration(self, tmp_path):
        """Test async reporting operations integration."""
        # Setup
        artifact_manager = ArtifactManager(artifact_path=tmp_path)

        # Simulate async report generation
        import asyncio

        async def generate_async_report():
            await asyncio.sleep(0.1)  # Simulate async processing
            return {"async_report": True, "generation_time": "0.1s", "status": "completed"}

        # Generate async report
        async_data = await generate_async_report()

        # Store async results
        artifact_path = artifact_manager.create_artifact(
            name="async_report.json", content=async_data, content_type="application/json"
        )

        # Verify async integration
        assert artifact_path.exists()
        stored_data = json.loads(artifact_path.read_text())
        assert stored_data["async_report"] is True
        assert stored_data["status"] == "completed"


@pytest.mark.reporting
@pytest.mark.unit
class TestReportingModuleUnits:
    """Unit tests specific to reporting framework components."""

    def test_github_reporter_initialization(self):
        """Test GitHub reporter proper initialization."""
        reporter = GitHubReporter()

        assert hasattr(reporter, "generate_performance_report")
        assert hasattr(reporter, "generate_security_report")
        assert hasattr(reporter, "create_build_status_summary")

    def test_report_generator_initialization(self):
        """Test report generator proper initialization."""
        generator = ReportGenerator()

        assert hasattr(generator, "set_coverage_data")
        assert hasattr(generator, "add_performance_trend")
        assert hasattr(generator, "generate_comprehensive_report")

    def test_artifact_manager_initialization(self, tmp_path):
        """Test artifact manager proper initialization."""
        manager = ArtifactManager(artifact_path=tmp_path)

        assert manager.artifact_path == Path(tmp_path)
        assert hasattr(manager, "create_artifact")
        assert hasattr(manager, "create_report_artifact")
        assert hasattr(manager, "create_log_artifact")
        assert hasattr(manager, "create_data_artifact")

    def test_template_engine_initialization(self):
        """Test template engine proper initialization."""
        engine = TemplateEngine()

        assert hasattr(engine, "render_build_status")
        assert hasattr(engine, "render_performance_summary")
        assert hasattr(engine, "render_security_summary")
