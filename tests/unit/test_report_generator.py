"""Tests for dynamic report generation system."""

import tempfile
from unittest.mock import patch

from strategy_sandbox.reporting import GitHubReporter
from strategy_sandbox.reporting.report_generator import (
    BuildInsight,
    CoverageData,
    PerformanceTrend,
    ReportGenerator,
)


class TestCoverageData:
    """Test cases for CoverageData dataclass."""

    def test_coverage_data_creation(self):
        """Test CoverageData creation with all fields."""
        modules = [
            {"name": "module1", "coverage": 85.5, "lines_covered": 85, "total_lines": 100},
            {"name": "module2", "coverage": 92.0, "lines_covered": 92, "total_lines": 100},
        ]

        coverage = CoverageData(
            overall_coverage=88.5,
            line_coverage=87.2,
            branch_coverage=85.0,
            function_coverage=90.1,
            modules=modules,
            trend_direction="improvement",
            trend_percentage=2.5,
        )

        assert coverage.overall_coverage == 88.5
        assert coverage.line_coverage == 87.2
        assert coverage.branch_coverage == 85.0
        assert coverage.function_coverage == 90.1
        assert len(coverage.modules) == 2
        assert coverage.trend_direction == "improvement"
        assert coverage.trend_percentage == 2.5

    def test_coverage_data_defaults(self):
        """Test CoverageData with default values."""
        coverage = CoverageData(
            overall_coverage=80.0,
            line_coverage=78.5,
            branch_coverage=75.2,
            function_coverage=82.1,
            modules=[],
        )

        assert coverage.trend_direction == "stable"
        assert coverage.trend_percentage is None


class TestPerformanceTrend:
    """Test cases for PerformanceTrend dataclass."""

    def test_performance_trend_creation(self):
        """Test PerformanceTrend creation with all fields."""
        trend = PerformanceTrend(
            metric_name="api_response_time",
            current_value=0.125,
            baseline_value=0.100,
            historical_values=[0.095, 0.102, 0.108, 0.115, 0.125],
            trend_direction="regression",
            change_percentage=25.0,
            threshold_status="warning",
        )

        assert trend.metric_name == "api_response_time"
        assert trend.current_value == 0.125
        assert trend.baseline_value == 0.100
        assert len(trend.historical_values) == 5
        assert trend.trend_direction == "regression"
        assert trend.change_percentage == 25.0
        assert trend.threshold_status == "warning"


class TestBuildInsight:
    """Test cases for BuildInsight dataclass."""

    def test_build_insight_creation(self):
        """Test BuildInsight creation with all fields."""
        insight = BuildInsight(
            insight_type="warning",
            title="Test Coverage Below Threshold",
            description="Current test coverage is below the recommended 80% threshold.",
            action_items=["Add unit tests for uncovered functions", "Implement integration tests"],
            priority="high",
        )

        assert insight.insight_type == "warning"
        assert insight.title == "Test Coverage Below Threshold"
        assert insight.priority == "high"
        assert len(insight.action_items) == 2


class TestReportGenerator:
    """Test cases for ReportGenerator class."""

    def test_initialization_with_existing_reporter(self):
        """Test ReportGenerator initialization with existing GitHubReporter."""
        with tempfile.TemporaryDirectory() as temp_dir:
            github_reporter = GitHubReporter(temp_dir)
            generator = ReportGenerator(github_reporter=github_reporter)

            assert generator.github_reporter is github_reporter
            assert generator.template_engine is github_reporter.template_engine
            assert generator.artifact_manager is github_reporter.artifact_manager

    def test_initialization_without_reporter(self):
        """Test ReportGenerator initialization creating new GitHubReporter."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = ReportGenerator(artifact_path=temp_dir)

            assert generator.github_reporter is not None
            assert generator.template_engine is not None
            assert generator.artifact_manager is not None

    def test_set_coverage_data_with_dict(self):
        """Test setting coverage data from dictionary."""
        generator = ReportGenerator()

        coverage_dict = {
            "overall_coverage": 85.5,
            "line_coverage": 84.2,
            "branch_coverage": 81.0,
            "function_coverage": 88.5,
            "modules": [{"name": "test_module", "coverage": 85.5}],
            "trend_direction": "improvement",
            "trend_percentage": 3.2,
        }

        generator.set_coverage_data(coverage_dict)

        assert generator._coverage_data is not None
        assert generator._coverage_data.overall_coverage == 85.5
        assert generator._coverage_data.trend_direction == "improvement"

    def test_set_coverage_data_with_object(self):
        """Test setting coverage data from CoverageData object."""
        generator = ReportGenerator()

        coverage_obj = CoverageData(
            overall_coverage=90.0,
            line_coverage=89.5,
            branch_coverage=87.2,
            function_coverage=92.1,
            modules=[],
        )

        generator.set_coverage_data(coverage_obj)

        assert generator._coverage_data is coverage_obj
        assert generator._coverage_data.overall_coverage == 90.0

    def test_add_performance_trend_with_dict(self):
        """Test adding performance trend from dictionary."""
        generator = ReportGenerator()

        trend_dict = {
            "metric_name": "execution_time",
            "current_value": 0.150,
            "baseline_value": 0.120,
            "historical_values": [0.115, 0.125, 0.135, 0.145, 0.150],
            "trend_direction": "regression",
            "change_percentage": 25.0,
            "threshold_status": "warning",
        }

        generator.add_performance_trend(trend_dict)

        assert len(generator._performance_trends) == 1
        assert generator._performance_trends[0].metric_name == "execution_time"
        assert generator._performance_trends[0].threshold_status == "warning"

    def test_add_performance_trend_with_object(self):
        """Test adding performance trend from PerformanceTrend object."""
        generator = ReportGenerator()

        trend_obj = PerformanceTrend(
            metric_name="memory_usage",
            current_value=75.5,
            baseline_value=70.0,
            historical_values=[68.0, 69.5, 71.2, 73.8, 75.5],
            trend_direction="regression",
            change_percentage=7.9,
            threshold_status="critical",
        )

        generator.add_performance_trend(trend_obj)

        assert len(generator._performance_trends) == 1
        assert generator._performance_trends[0] is trend_obj

    def test_add_build_insight_with_dict(self):
        """Test adding build insight from dictionary."""
        generator = ReportGenerator()

        insight_dict = {
            "insight_type": "recommendation",
            "title": "Optimize Database Queries",
            "description": "Several slow database queries detected in performance tests.",
            "action_items": ["Add database indexes", "Optimize query structure"],
            "priority": "medium",
        }

        generator.add_build_insight(insight_dict)

        assert len(generator._build_insights) == 1
        assert generator._build_insights[0].title == "Optimize Database Queries"
        assert generator._build_insights[0].priority == "medium"

    def test_add_build_insight_with_object(self):
        """Test adding build insight from BuildInsight object."""
        generator = ReportGenerator()

        insight_obj = BuildInsight(
            insight_type="warning",
            title="Security Vulnerability Found",
            description="High severity security issue detected in dependencies.",
            action_items=["Update vulnerable dependencies", "Review security policies"],
            priority="high",
        )

        generator.add_build_insight(insight_obj)

        assert len(generator._build_insights) == 1
        assert generator._build_insights[0] is insight_obj

    def test_generate_coverage_report_without_data(self):
        """Test coverage report generation without data."""
        generator = ReportGenerator()

        report = generator.generate_coverage_report()

        assert "No coverage data available" in report

    def test_generate_coverage_report_with_basic_data(self):
        """Test coverage report generation with basic coverage data."""
        generator = ReportGenerator()

        coverage_data = CoverageData(
            overall_coverage=85.5,
            line_coverage=84.2,
            branch_coverage=81.0,
            function_coverage=88.5,
            modules=[
                {"name": "module1", "coverage": 92.0, "lines_covered": 92, "total_lines": 100},
                {"name": "module2", "coverage": 78.5, "lines_covered": 78, "total_lines": 100},
            ],
        )

        generator.set_coverage_data(coverage_data)
        report = generator.generate_coverage_report()

        assert "Test Coverage Report" in report
        assert "85.5%" in report
        assert "84.2%" in report  # Line coverage
        assert "81.0%" in report  # Branch coverage
        assert "88.5%" in report  # Function coverage
        assert "module1" in report
        assert "module2" in report

    def test_generate_coverage_report_with_trends(self):
        """Test coverage report generation with trend data."""
        generator = ReportGenerator()

        coverage_data = CoverageData(
            overall_coverage=87.2,
            line_coverage=86.5,
            branch_coverage=83.8,
            function_coverage=89.1,
            modules=[],
            trend_direction="improvement",
            trend_percentage=3.5,
        )

        generator.set_coverage_data(coverage_data)
        report = generator.generate_coverage_report(include_trends=True)

        assert "Test Coverage Report" in report
        assert "87.2%" in report
        assert "Improvement" in report or "improvement" in report
        assert "+3.5%" in report

    def test_generate_performance_dashboard_without_data(self):
        """Test performance dashboard generation without data."""
        generator = ReportGenerator()

        dashboard = generator.generate_performance_dashboard()

        assert "No performance trend data available" in dashboard

    def test_generate_performance_dashboard_with_data(self):
        """Test performance dashboard generation with trend data."""
        generator = ReportGenerator()

        # Add multiple performance trends
        trends = [
            PerformanceTrend(
                metric_name="api_response_time",
                current_value=0.125,
                baseline_value=0.100,
                historical_values=[0.095, 0.102, 0.108, 0.115, 0.125],
                trend_direction="regression",
                change_percentage=25.0,
                threshold_status="warning",
            ),
            PerformanceTrend(
                metric_name="memory_usage",
                current_value=85.5,
                baseline_value=90.0,
                historical_values=[92.0, 90.5, 89.2, 87.8, 85.5],
                trend_direction="improvement",
                change_percentage=-5.0,
                threshold_status="within",
            ),
            PerformanceTrend(
                metric_name="cpu_usage",
                current_value=95.0,
                baseline_value=70.0,
                historical_values=[65.0, 68.5, 75.2, 85.8, 95.0],
                trend_direction="regression",
                change_percentage=35.7,
                threshold_status="critical",
            ),
        ]

        for trend in trends:
            generator.add_performance_trend(trend)

        dashboard = generator.generate_performance_dashboard()

        assert "Performance Trends Dashboard" in dashboard
        assert "1 Critical Performance Issues Detected" in dashboard
        assert "api_response_time" in dashboard
        assert "memory_usage" in dashboard
        assert "cpu_usage" in dashboard
        assert "Critical Performance Issues" in dashboard

    def test_generate_build_dashboard_basic(self):
        """Test build dashboard generation with basic data."""
        generator = ReportGenerator()

        test_results = {"total": 100, "passed": 95, "failed": 5, "duration": 120.5}

        dashboard = generator.generate_build_dashboard(test_results=test_results)

        assert "Build Status Dashboard" in dashboard
        assert "Overall Build Health" in dashboard
        assert "95/100 tests" in dashboard

    def test_generate_build_dashboard_with_insights(self):
        """Test build dashboard generation with build insights."""
        generator = ReportGenerator()

        # Add build insights
        insights = [
            BuildInsight(
                insight_type="warning",
                title="Test Failures Detected",
                description="Multiple test failures in core modules.",
                action_items=["Fix failing tests", "Review test coverage"],
                priority="high",
            ),
            BuildInsight(
                insight_type="recommendation",
                title="Performance Optimization",
                description="API response times are increasing.",
                action_items=["Profile API endpoints", "Optimize database queries"],
                priority="medium",
            ),
        ]

        for insight in insights:
            generator.add_build_insight(insight)

        dashboard = generator.generate_build_dashboard()

        assert "Build Status Dashboard" in dashboard
        assert "Actionable Insights" in dashboard
        assert "High Priority" in dashboard
        assert "Test Failures Detected" in dashboard
        assert "Performance Optimization" in dashboard

    def test_generate_comprehensive_report(self):
        """Test comprehensive report generation combining all data sources."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = ReportGenerator(artifact_path=temp_dir)

            # Set up test data
            coverage_data = CoverageData(
                overall_coverage=85.5,
                line_coverage=84.2,
                branch_coverage=81.0,
                function_coverage=88.5,
                modules=[],
            )
            generator.set_coverage_data(coverage_data)

            performance_trend = PerformanceTrend(
                metric_name="execution_time",
                current_value=0.125,
                baseline_value=0.100,
                historical_values=[0.095, 0.102, 0.108, 0.115, 0.125],
                trend_direction="regression",
                change_percentage=25.0,
                threshold_status="warning",
            )
            generator.add_performance_trend(performance_trend)

            test_results = {"total": 100, "passed": 98, "failed": 2, "duration": 45.2}
            performance_data = {"benchmark_results": []}
            security_data = {"bandit_results": {}, "pip_audit_results": {}}

            # Mock the GitHub reporter's add_to_summary method
            with patch.object(generator.github_reporter, "add_to_summary", return_value=True):
                results = generator.generate_comprehensive_report(
                    test_results=test_results,
                    performance_data=performance_data,
                    security_data=security_data,
                    include_artifacts=True,
                )

            assert "summary_added" in results
            assert "artifacts_created" in results
            assert "report_sections" in results
            assert results["summary_added"] is True
            assert len(results["artifacts_created"]) > 0
            assert "build_dashboard" in results["report_sections"]
            assert "coverage_report" in results["report_sections"]
            assert "performance_dashboard" in results["report_sections"]

    def test_get_coverage_emoji(self):
        """Test coverage emoji selection."""
        generator = ReportGenerator()

        assert generator._get_coverage_emoji(95.0) == "🟢"  # Excellent
        assert generator._get_coverage_emoji(85.0) == "🟡"  # Good
        assert generator._get_coverage_emoji(75.0) == "🟠"  # Fair
        assert generator._get_coverage_emoji(65.0) == "🔴"  # Poor

    def test_get_coverage_status(self):
        """Test coverage status text."""
        generator = ReportGenerator()

        assert "Excellent" in generator._get_coverage_status(95.0)
        assert "Good" in generator._get_coverage_status(85.0)
        assert "Fair" in generator._get_coverage_status(75.0)
        assert "Poor" in generator._get_coverage_status(65.0)

    def test_get_trend_icon(self):
        """Test trend direction icons."""
        generator = ReportGenerator()

        assert generator._get_trend_icon("improvement") == "📈"
        assert generator._get_trend_icon("regression") == "📉"
        assert generator._get_trend_icon("stable") == "➡️"
        assert generator._get_trend_icon("unknown") == "➡️"  # Default

    def test_get_threshold_status_icon(self):
        """Test threshold status icons."""
        generator = ReportGenerator()

        assert generator._get_threshold_status_icon("within") == "✅"
        assert generator._get_threshold_status_icon("warning") == "⚠️"
        assert generator._get_threshold_status_icon("critical") == "🚨"
        assert generator._get_threshold_status_icon("unknown") == "❓"  # Default

    def test_format_metric_value(self):
        """Test metric value formatting."""
        generator = ReportGenerator()

        # Time metrics
        assert generator._format_metric_value("execution_time", 0.125) == "0.1250s"
        assert generator._format_metric_value("api_latency", 2.5) == "2.5000s"

        # Throughput metrics
        assert generator._format_metric_value("throughput", 1500.5) == "1500 ops/sec"
        assert generator._format_metric_value("requests_per_sec", 2000.0) == "2000 ops/sec"

        # Memory metrics
        assert generator._format_metric_value("memory_usage", 75.5) == "75.5 MB"

        # CPU metrics
        assert generator._format_metric_value("cpu_usage", 85.2) == "85.2%"

        # Generic metrics
        assert generator._format_metric_value("custom_metric", 42.123) == "42.12"

        # None value
        assert generator._format_metric_value("any_metric", None) == "N/A"

    def test_generate_coverage_insights(self):
        """Test coverage insights generation."""
        generator = ReportGenerator()

        # Test coverage below threshold
        coverage_data = CoverageData(
            overall_coverage=75.0,  # Below 80%
            line_coverage=78.0,
            branch_coverage=65.0,  # Significantly lower than line coverage
            function_coverage=80.0,
            modules=[
                {"name": "module1", "coverage": 95.0},
                {"name": "module2", "coverage": 65.0},  # Poor coverage
                {"name": "module3", "coverage": 60.0},  # Poor coverage
            ],
        )

        insights = generator._generate_coverage_insights(coverage_data)

        assert len(insights) > 0

        # Check for specific insight types
        insight_titles = [insight["title"] for insight in insights]
        assert any("Coverage Below Recommended Threshold" in title for title in insight_titles)
        assert any("Branch Coverage Gap" in title for title in insight_titles)
        assert any("Low Coverage Modules" in title for title in insight_titles)

    def test_get_performance_recommendations(self):
        """Test performance recommendations generation."""
        generator = ReportGenerator()

        # Test execution time recommendations
        execution_trend = PerformanceTrend(
            metric_name="execution_time",
            current_value=0.125,
            baseline_value=0.100,
            historical_values=[],
            trend_direction="regression",
            change_percentage=25.0,
            threshold_status="critical",
        )

        recommendations = generator._get_performance_recommendations(execution_trend)

        assert len(recommendations) > 0
        assert any("bottlenecks" in rec.lower() for rec in recommendations)
        assert any("algorithm" in rec.lower() for rec in recommendations)

        # Test memory recommendations
        memory_trend = PerformanceTrend(
            metric_name="memory_usage",
            current_value=85.0,
            baseline_value=70.0,
            historical_values=[],
            trend_direction="regression",
            change_percentage=21.4,
            threshold_status="warning",
        )

        memory_recommendations = generator._get_performance_recommendations(memory_trend)

        assert len(memory_recommendations) > 0
        assert any("memory leak" in rec.lower() for rec in memory_recommendations)

    def test_calculate_overall_status(self):
        """Test overall status calculation."""
        generator = ReportGenerator()

        # Test failure status with failed tests
        test_results_failed = {"total": 100, "passed": 95, "failed": 5}
        status = generator._calculate_overall_status(test_results_failed, None, None)
        assert status == "failure"

        # Test failure status with critical performance
        generator.add_performance_trend(
            PerformanceTrend(
                metric_name="test_metric",
                current_value=100.0,
                baseline_value=50.0,
                historical_values=[],
                trend_direction="regression",
                change_percentage=100.0,
                threshold_status="critical",
            )
        )
        status = generator._calculate_overall_status(None, None, None)
        assert status == "failure"

        # Test warning status
        generator._performance_trends.clear()
        security_data = {
            "bandit_results": {"metrics": {"_totals": {"SEVERITY.HIGH": 1, "SEVERITY.MEDIUM": 2}}}
        }
        status = generator._calculate_overall_status(None, None, security_data)
        assert status == "warning"

        # Test success status
        test_results_success = {"total": 100, "passed": 100, "failed": 0}
        status = generator._calculate_overall_status(test_results_success, None, None)
        assert status == "success"

    def test_count_security_issues(self):
        """Test security issues counting."""
        generator = ReportGenerator()

        security_data = {
            "bandit_results": {
                "metrics": {
                    "_totals": {
                        "SEVERITY.HIGH": 2,
                        "SEVERITY.MEDIUM": 3,
                        "SEVERITY.LOW": 1,  # Not counted
                    }
                }
            },
            "pip_audit_results": {
                "dependencies": [
                    {"name": "package1", "vulns": [{"id": "CVE-1"}]},  # Vulnerable
                    {"name": "package2", "vulns": []},  # Not vulnerable
                    {"name": "package3", "vulns": [{"id": "CVE-2"}, {"id": "CVE-3"}]},  # Vulnerable
                ]
            },
        }

        issues_count = generator._count_security_issues(security_data)

        # 2 high + 3 medium + 2 vulnerable packages = 7 total issues
        assert issues_count == 7

    def test_format_insight(self):
        """Test insight formatting for markdown."""
        generator = ReportGenerator()

        insight = BuildInsight(
            insight_type="warning",
            title="Test Coverage Issue",
            description="Coverage has dropped below acceptable levels.",
            action_items=["Add more unit tests", "Review integration test coverage"],
            priority="high",
        )

        formatted = generator._format_insight(insight)

        assert "🔥 Test Coverage Issue" in formatted  # High priority icon
        assert "Coverage has dropped below acceptable levels." in formatted
        assert "Action Items:" in formatted
        assert "Add more unit tests" in formatted
        assert "Review integration test coverage" in formatted

    def test_generate_auto_insights(self):
        """Test automatic insights generation."""
        generator = ReportGenerator()

        # Set up data that should trigger auto insights
        test_results = {"total": 100, "passed": 90, "failed": 10}

        generator.add_performance_trend(
            PerformanceTrend(
                metric_name="critical_metric",
                current_value=100.0,
                baseline_value=50.0,
                historical_values=[],
                trend_direction="regression",
                change_percentage=100.0,
                threshold_status="critical",
            )
        )

        coverage_data = CoverageData(
            overall_coverage=75.0,  # Below 80%
            line_coverage=75.0,
            branch_coverage=75.0,
            function_coverage=75.0,
            modules=[],
        )
        generator.set_coverage_data(coverage_data)

        auto_insights = generator._generate_auto_insights(test_results, None, None)

        assert len(auto_insights) == 3  # Test failures, performance regression, coverage

        insight_titles = [insight["title"] for insight in auto_insights]
        assert any("Test Failures Detected" in title for title in insight_titles)
        assert any("Performance Regression Alert" in title for title in insight_titles)
        assert any("Coverage Improvement Needed" in title for title in insight_titles)

    def test_create_section_artifact(self):
        """Test section artifact creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = ReportGenerator(artifact_path=temp_dir)

            section_content = "# Test Report\n\nThis is a test report content."

            artifact_path = generator._create_section_artifact("test_section", section_content)

            assert artifact_path is not None
            assert artifact_path.exists()
            assert "test_section_" in artifact_path.name
            assert artifact_path.name.endswith(".md")

            # Verify content
            with open(artifact_path) as f:
                content = f.read()
            assert content == section_content

    def test_parse_coverage_data(self):
        """Test coverage data parsing from dictionary."""
        generator = ReportGenerator()

        data = {
            "overall_coverage": 88.5,
            "line_coverage": 87.2,
            "branch_coverage": 85.0,
            "function_coverage": 90.1,
            "modules": [{"name": "test_module", "coverage": 85.0}],
            "trend_direction": "improvement",
            "trend_percentage": 2.5,
        }

        coverage = generator._parse_coverage_data(data)

        assert isinstance(coverage, CoverageData)
        assert coverage.overall_coverage == 88.5
        assert coverage.trend_direction == "improvement"
        assert coverage.trend_percentage == 2.5
        assert len(coverage.modules) == 1

    def test_parse_performance_trend(self):
        """Test performance trend parsing from dictionary."""
        generator = ReportGenerator()

        data = {
            "metric_name": "api_response_time",
            "current_value": 0.125,
            "baseline_value": 0.100,
            "historical_values": [0.095, 0.102, 0.108, 0.115, 0.125],
            "trend_direction": "regression",
            "change_percentage": 25.0,
            "threshold_status": "warning",
        }

        trend = generator._parse_performance_trend(data)

        assert isinstance(trend, PerformanceTrend)
        assert trend.metric_name == "api_response_time"
        assert trend.current_value == 0.125
        assert trend.threshold_status == "warning"
        assert len(trend.historical_values) == 5
