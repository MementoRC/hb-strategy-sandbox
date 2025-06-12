"""Tests for GitHub reporting integration."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

from strategy_sandbox.reporting import GitHubReporter, TemplateEngine, ArtifactManager


class TestGitHubReporter:
    """Test cases for GitHubReporter."""

    def test_reporter_initialization_without_github(self):
        """Test reporter initialization outside GitHub Actions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            reporter = GitHubReporter(temp_dir)

            assert reporter.artifact_path == Path(temp_dir)
            assert not reporter.is_github_actions
            assert reporter.summary_path is None
            assert isinstance(reporter.template_engine, TemplateEngine)
            assert isinstance(reporter.artifact_manager, ArtifactManager)

    @patch.dict(
        os.environ,
        {
            "GITHUB_ACTIONS": "true",
            "GITHUB_STEP_SUMMARY": "/tmp/step_summary.md",
            "GITHUB_WORKFLOW": "CI",
            "GITHUB_RUN_ID": "123456",
            "GITHUB_REPOSITORY": "user/repo",
        },
    )
    def test_reporter_initialization_with_github(self):
        """Test reporter initialization in GitHub Actions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            reporter = GitHubReporter(temp_dir)

            assert reporter.is_github_actions
            assert reporter.summary_path == "/tmp/step_summary.md"
            assert "GITHUB_WORKFLOW" in reporter.github_env
            assert reporter.github_env["GITHUB_WORKFLOW"] == "CI"

    def test_collect_github_environment(self):
        """Test GitHub environment collection."""
        with patch.dict(
            os.environ,
            {
                "GITHUB_ACTIONS": "true",
                "GITHUB_WORKFLOW": "Test Workflow",
                "GITHUB_RUN_ID": "987654",
                "NON_GITHUB_VAR": "should_not_appear",
            },
        ):
            reporter = GitHubReporter()
            env = reporter._collect_github_environment()

            assert "GITHUB_ACTIONS" in env
            assert "GITHUB_WORKFLOW" in env
            assert "GITHUB_RUN_ID" in env
            assert "NON_GITHUB_VAR" not in env

    @patch("builtins.open", new_callable=mock_open)
    @patch.dict(os.environ, {"GITHUB_STEP_SUMMARY": "/tmp/summary.md"})
    def test_add_to_summary_success(self, mock_file):
        """Test successful step summary addition."""
        reporter = GitHubReporter()

        result = reporter.add_to_summary("# Test Summary\nThis is a test.")

        assert result is True
        mock_file.assert_called_once_with("/tmp/summary.md", "a", encoding="utf-8")
        mock_file().write.assert_called_once_with("# Test Summary\nThis is a test.\n")

    def test_add_to_summary_no_path(self):
        """Test step summary addition without GITHUB_STEP_SUMMARY."""
        reporter = GitHubReporter()

        result = reporter.add_to_summary("Test content")

        assert result is False

    def test_create_build_status_summary(self):
        """Test build status summary creation."""
        reporter = GitHubReporter()

        test_results = {"total": 100, "passed": 95, "failed": 5, "duration": 45.2}

        summary = reporter.create_build_status_summary(
            build_status="success", test_results=test_results
        )

        assert "Build Status Report" in summary
        assert "✅" in summary  # Success emoji
        assert "95" in summary  # Passed tests
        assert "45.2" in summary  # Duration

    def test_create_performance_summary(self):
        """Test performance summary creation."""
        reporter = GitHubReporter()

        performance_data = {
            "results": [
                {
                    "name": "test_benchmark",
                    "execution_time": 0.1,
                    "throughput": 1000.0,
                    "memory_usage": 50.0,
                }
            ],
            "summary_stats": {"avg_execution_time": 0.1, "max_execution_time": 0.15},
        }

        baseline_comparison = {
            "comparisons": [
                {
                    "name": "test_benchmark",
                    "execution_time": {
                        "current": 0.1,
                        "baseline": 0.08,
                        "change_percent": 25.0,
                        "change_direction": "regression",
                    },
                }
            ]
        }

        summary = reporter.create_performance_summary(performance_data, baseline_comparison)

        assert "Performance Benchmark Report" in summary
        assert "test_benchmark" in summary
        assert "0.1000s" in summary
        assert "25.0%" in summary  # Performance change
        assert "🔴" in summary  # Regression indicator

    def test_create_security_summary(self):
        """Test security summary creation."""
        reporter = GitHubReporter()

        bandit_results = {
            "metrics": {"_totals": {"SEVERITY.HIGH": 2, "SEVERITY.MEDIUM": 3, "SEVERITY.LOW": 1}},
            "results": [
                {
                    "issue_severity": "HIGH",
                    "issue_confidence": "HIGH",
                    "issue_text": "Use of insecure function",
                    "filename": "test.py",
                    "line_number": 42,
                }
            ],
        }

        pip_audit_results = {
            "dependencies": [
                {
                    "name": "vulnerable-package",
                    "version": "1.0.0",
                    "vulns": [
                        {
                            "id": "CVE-2023-1234",
                            "description": "Security vulnerability description",
                            "fix_versions": ["1.0.1"],
                        }
                    ],
                }
            ]
        }

        summary = reporter.create_security_summary(bandit_results, pip_audit_results)

        assert "Security Scan Report" in summary
        assert "2" in summary  # High severity count
        assert "vulnerable-package" in summary
        assert "CVE-2023-1234" in summary

    def test_create_artifact(self):
        """Test artifact creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            reporter = GitHubReporter(temp_dir)

            test_data = {"key": "value", "number": 42}

            artifact_path = reporter.create_artifact(
                "test_artifact.json", test_data, "application/json"
            )

            assert artifact_path is not None
            assert artifact_path.exists()

            # Verify content
            with open(artifact_path, "r") as f:
                loaded_data = json.load(f)

            assert loaded_data == test_data

    def test_generate_performance_report(self):
        """Test comprehensive performance report generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(os.environ, {"GITHUB_STEP_SUMMARY": f"{temp_dir}/summary.md"}):
                reporter = GitHubReporter(temp_dir)

                performance_metrics = {
                    "results": [
                        {"name": "benchmark_test", "execution_time": 0.05, "throughput": 2000.0}
                    ]
                }

                results = reporter.generate_performance_report(
                    performance_metrics=performance_metrics,
                    include_summary=True,
                    include_artifact=True,
                )

                assert "summary_added" in results
                assert "artifact_created" in results
                assert results["artifact_created"] is not None

    def test_generate_security_report_with_files(self):
        """Test security report generation with file loading."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            bandit_file = Path(temp_dir) / "bandit.json"
            bandit_data = {"metrics": {"_totals": {"SEVERITY.HIGH": 0}}, "results": []}
            with open(bandit_file, "w") as f:
                json.dump(bandit_data, f)

            pip_audit_file = Path(temp_dir) / "pip-audit.json"
            pip_audit_data = {"dependencies": []}
            with open(pip_audit_file, "w") as f:
                json.dump(pip_audit_data, f)

            # Test report generation
            with patch.dict(os.environ, {"GITHUB_STEP_SUMMARY": f"{temp_dir}/summary.md"}):
                reporter = GitHubReporter(temp_dir)

                results = reporter.generate_security_report(
                    bandit_file=str(bandit_file),
                    pip_audit_file=str(pip_audit_file),
                    include_summary=True,
                    include_artifact=True,
                )

                assert "summary_added" in results
                assert "artifact_created" in results

    def test_load_json_file_success(self):
        """Test successful JSON file loading."""
        with tempfile.TemporaryDirectory() as temp_dir:
            reporter = GitHubReporter()

            test_file = Path(temp_dir) / "test.json"
            test_data = {"test": "data"}

            with open(test_file, "w") as f:
                json.dump(test_data, f)

            loaded_data = reporter._load_json_file(str(test_file))

            assert loaded_data == test_data

    def test_load_json_file_failure(self):
        """Test JSON file loading failure."""
        reporter = GitHubReporter()

        result = reporter._load_json_file("nonexistent_file.json")

        assert result is None

    @patch.dict(os.environ, {"GITHUB_REPOSITORY": "user/test-repo", "GITHUB_RUN_ID": "987654321"})
    def test_get_workflow_url(self):
        """Test workflow URL generation."""
        reporter = GitHubReporter()

        url = reporter._get_workflow_url()

        assert url == "https://github.com/user/test-repo/actions/runs/987654321"

    def test_get_workflow_url_missing_info(self):
        """Test workflow URL with missing information."""
        reporter = GitHubReporter()

        url = reporter._get_workflow_url()

        assert url is None

    def test_get_environment_info(self):
        """Test environment information retrieval."""
        with tempfile.TemporaryDirectory() as temp_dir:
            reporter = GitHubReporter(temp_dir)

            env_info = reporter.get_environment_info()

            assert "is_github_actions" in env_info
            assert "github_env" in env_info
            assert "summary_path" in env_info
            assert "artifact_path" in env_info
            assert "workflow_url" in env_info


class TestTemplateEngine:
    """Test cases for TemplateEngine."""

    def test_template_engine_initialization(self):
        """Test template engine initialization."""
        engine = TemplateEngine()
        assert engine is not None

    def test_render_build_status_success(self):
        """Test build status rendering for success."""
        engine = TemplateEngine()

        context = {
            "build_status": "success",
            "test_results": {"total": 50, "passed": 48, "failed": 2, "duration": 30.5},
            "github_env": {
                "GITHUB_WORKFLOW": "CI Pipeline",
                "GITHUB_RUN_NUMBER": "42",
                "GITHUB_SHA": "abc123def456",
            },
            "timestamp": "2023-06-11T12:00:00",
        }

        result = engine.render_build_status(context)

        assert "✅ Build Status Report" in result
        assert "CI Pipeline" in result
        assert "48" in result  # Passed tests
        assert "2" in result  # Failed tests

    def test_render_performance_summary(self):
        """Test performance summary rendering."""
        engine = TemplateEngine()

        context = {
            "metrics": {
                "results": [
                    {
                        "name": "api_benchmark",
                        "execution_time": 0.125,
                        "throughput": 800.0,
                        "memory_usage": 75.5,
                    }
                ],
                "summary_stats": {"avg_execution_time": 0.125, "max_execution_time": 0.150},
            },
            "comparison": {
                "comparisons": [
                    {
                        "name": "api_benchmark",
                        "execution_time": {
                            "current": 0.125,
                            "baseline": 0.100,
                            "change_percent": 25.0,
                            "change_direction": "regression",
                        },
                    }
                ]
            },
            "timestamp": "2023-06-11T12:00:00",
        }

        result = engine.render_performance_summary(context)

        assert "Performance Benchmark Report" in result
        assert "api_benchmark" in result
        assert "0.1250s" in result
        assert "800 ops/sec" in result
        assert "🔴" in result  # Regression indicator

    def test_render_security_summary(self):
        """Test security summary rendering."""
        engine = TemplateEngine()

        context = {
            "bandit_results": {
                "metrics": {
                    "_totals": {"SEVERITY.HIGH": 1, "SEVERITY.MEDIUM": 2, "SEVERITY.LOW": 0}
                },
                "results": [
                    {
                        "issue_severity": "HIGH",
                        "issue_confidence": "HIGH",
                        "issue_text": "Potential security issue detected",
                        "filename": "security_test.py",
                        "line_number": 123,
                    }
                ],
            },
            "pip_audit_results": {
                "dependencies": [
                    {
                        "name": "test-package",
                        "version": "1.0.0",
                        "vulns": [
                            {
                                "id": "GHSA-test-1234",
                                "description": "Test vulnerability description",
                                "fix_versions": ["1.0.1", "1.1.0"],
                            }
                        ],
                    }
                ]
            },
            "timestamp": "2023-06-11T12:00:00",
        }

        result = engine.render_security_summary(context)

        assert "Security Scan Report" in result
        assert "🔴 High | 1" in result
        assert "test-package" in result
        assert "GHSA-test-1234" in result

    def test_get_status_info(self):
        """Test status information retrieval."""
        engine = TemplateEngine()

        success_info = engine._get_status_info("success")
        assert success_info["emoji"] == "✅"
        assert "success" in success_info["badge"]

        failure_info = engine._get_status_info("failure")
        assert failure_info["emoji"] == "❌"
        assert "failure" in failure_info["badge"]

    def test_get_performance_icon(self):
        """Test performance change icons."""
        engine = TemplateEngine()

        assert engine._get_performance_icon("improvement") == "🟢"
        assert engine._get_performance_icon("regression") == "🔴"
        assert engine._get_performance_icon("unchanged") == "⚪"

    def test_get_severity_icon(self):
        """Test security severity icons."""
        engine = TemplateEngine()

        assert engine._get_severity_icon("HIGH") == "🔴"
        assert engine._get_severity_icon("MEDIUM") == "🟡"
        assert engine._get_severity_icon("LOW") == "🟢"
        assert engine._get_severity_icon("UNKNOWN") == "⚪"


class TestArtifactManager:
    """Test cases for ArtifactManager."""

    def test_artifact_manager_initialization(self):
        """Test artifact manager initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ArtifactManager(temp_dir)

            assert manager.artifact_path == Path(temp_dir)
            assert manager.reports_path.exists()
            assert manager.logs_path.exists()
            assert manager.data_path.exists()

    def test_create_json_artifact(self):
        """Test JSON artifact creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ArtifactManager(temp_dir)

            test_data = {"key": "value", "number": 123}

            artifact_path = manager.create_artifact("test.json", test_data, "application/json")

            assert artifact_path is not None
            assert artifact_path.exists()

            # Verify content
            with open(artifact_path, "r") as f:
                loaded_data = json.load(f)

            assert loaded_data == test_data

    def test_create_text_artifact(self):
        """Test text artifact creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ArtifactManager(temp_dir)

            text_content = "This is a test file\nwith multiple lines."

            artifact_path = manager.create_artifact("test.txt", text_content, "text/plain")

            assert artifact_path is not None
            assert artifact_path.exists()

            # Verify content
            with open(artifact_path, "r") as f:
                loaded_content = f.read()

            assert loaded_content == text_content

    def test_create_report_artifact(self):
        """Test report artifact creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ArtifactManager(temp_dir)

            report_data = {"report_type": "test", "metrics": {"value": 100}}

            artifact_path = manager.create_report_artifact("test_report", report_data, "json")

            assert artifact_path is not None
            assert artifact_path.exists()
            assert "test_report_" in artifact_path.name
            assert artifact_path.name.endswith(".json")

    def test_list_artifacts(self):
        """Test artifact listing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ArtifactManager(temp_dir)

            # Create test artifacts
            manager.create_artifact("test1.json", {"data": 1}, "application/json")
            manager.create_artifact("test2.txt", "test content", "text/plain")

            # List all artifacts
            artifacts = manager.list_artifacts()

            assert len(artifacts) == 2
            assert any(a["name"] == "test1.json" for a in artifacts)
            assert any(a["name"] == "test2.txt" for a in artifacts)

    def test_get_artifact_summary(self):
        """Test artifact summary generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ArtifactManager(temp_dir)

            # Create test artifacts
            manager.create_artifact("report.json", {"data": "test"}, "application/json")
            manager.create_artifact("data.csv", "col1,col2\n1,2", "text/csv")

            summary = manager.get_artifact_summary()

            assert summary["total_count"] == 2
            assert summary["total_size"] > 0
            assert "by_type" in summary
            assert len(summary["recent_artifacts"]) <= 5
