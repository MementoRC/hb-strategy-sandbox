"""Tests for trend analysis and alerting system."""

import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest
import yaml

from strategy_sandbox.performance.models import BenchmarkResult, PerformanceMetrics
from strategy_sandbox.performance.trend_analyzer import (
    AlertCooldown,
    AlertSeverity,
    TrendAlert,
    TrendAnalyzer,
    TrendData,
)


class TestTrendAnalyzer:
    """Test cases for TrendAnalyzer."""

    @pytest.fixture
    def temp_config_file(self):
        """Create a temporary config file for testing."""
        config_data = {
            "alert_channels": ["step_summary"],
            "alert_thresholds": {"critical": 0.25, "warning": 0.10, "improvement": 0.05},
            "alert_cooldown": 1,  # 1 hour for testing
            "trend_analysis": {
                "min_data_points": 3,
                "correlation_threshold": 0.7,
                "anomaly_std_dev_multiplier": 2.0,
                "moving_average_window": 5,
            },
            "templates": {
                "step_summary_format": "Alert: {severity} - {benchmark_name}",
            },
            "severity_icons": {"critical": "🚨", "warning": "⚠️"},
            "cooldown_storage": f"/tmp/test_cooldown_{time.time()}.json",  # Unique file per test
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config_data, f)
            return Path(f.name)

    @pytest.fixture
    def trend_analyzer(self, temp_config_file):
        """Create TrendAnalyzer instance for testing."""
        analyzer = TrendAnalyzer(alert_config_path=temp_config_file)
        # Clear any existing cooldown data for clean test state
        analyzer.cooldown_data.clear()
        return analyzer

    @pytest.fixture
    def sample_historical_metrics(self):
        """Create sample historical metrics for testing."""
        metrics = []
        base_time = datetime.now() - timedelta(days=10)  # Start 10 days ago

        # Create 10 historical data points with gradual increase
        for i in range(10):
            timestamp = base_time + timedelta(days=i)
            execution_time = 1.0 + (i * 0.05)  # Gradual increase from 1.0 to 1.45
            memory_usage = 100.0 + (i * 2.0)  # Gradual increase from 100 to 118
            throughput = 1000.0 - (i * 10.0)  # Gradual decrease from 1000 to 910

            results = [
                BenchmarkResult(
                    name="test_benchmark",
                    execution_time=execution_time,
                    memory_usage=memory_usage,
                    throughput=throughput,
                ),
                BenchmarkResult(
                    name="stable_benchmark",
                    execution_time=0.5,  # Stable performance
                    memory_usage=50.0,
                    throughput=500.0,
                ),
            ]

            metrics.append(
                PerformanceMetrics(
                    build_id=f"build-{i}",
                    timestamp=timestamp,
                    results=results,
                )
            )

        return metrics

    def test_trend_analyzer_initialization(self, temp_config_file):
        """Test TrendAnalyzer initialization."""
        analyzer = TrendAnalyzer(alert_config_path=temp_config_file)
        assert analyzer.config["alert_thresholds"]["critical"] == 0.25
        assert analyzer.config["trend_analysis"]["min_data_points"] == 3
        assert analyzer.cooldown_data == {}

    def test_trend_analyzer_default_config(self):
        """Test TrendAnalyzer with default configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            non_existent_config = Path(temp_dir) / "nonexistent.yaml"
            analyzer = TrendAnalyzer(alert_config_path=non_existent_config)
            assert "alert_channels" in analyzer.config
            assert "alert_thresholds" in analyzer.config

    def test_analyze_trends(self, trend_analyzer, sample_historical_metrics):
        """Test trend analysis functionality."""
        trends = trend_analyzer.analyze_trends(sample_historical_metrics)

        # Should have trends for test_benchmark and stable_benchmark
        assert "test_benchmark.execution_time" in trends
        assert "test_benchmark.memory_usage" in trends
        assert "test_benchmark.throughput" in trends
        assert "stable_benchmark.execution_time" in trends

        # Check test_benchmark trend (should be increasing for exec time and memory)
        exec_trend = trends["test_benchmark.execution_time"]
        assert exec_trend.trend_direction == "increasing"
        assert exec_trend.correlation > 0.7  # Strong positive correlation

        # Check stable benchmark (should be stable)
        stable_trend = trends["stable_benchmark.execution_time"]
        assert stable_trend.trend_direction == "stable"
        assert abs(stable_trend.correlation) < 0.7

    def test_analyze_trends_with_time_window(self, trend_analyzer, sample_historical_metrics):
        """Test trend analysis with time window filtering."""
        # Only analyze last 5 days
        time_window = timedelta(days=5)
        trends = trend_analyzer.analyze_trends(sample_historical_metrics, time_window)

        # Should still detect trends but with fewer data points
        assert "test_benchmark.execution_time" in trends
        exec_trend = trends["test_benchmark.execution_time"]
        assert len(exec_trend.values) <= 6  # At most 6 data points (last 5 days + current)

    def test_calculate_correlation(self, trend_analyzer):
        """Test correlation calculation."""
        # Perfect positive correlation
        x_values = [1, 2, 3, 4, 5]
        y_values = [2.0, 4.0, 6.0, 8.0, 10.0]
        correlation = trend_analyzer._calculate_correlation(x_values, y_values)
        assert abs(correlation - 1.0) < 0.01

        # Perfect negative correlation
        y_values_neg = [10.0, 8.0, 6.0, 4.0, 2.0]
        correlation_neg = trend_analyzer._calculate_correlation(x_values, y_values_neg)
        assert abs(correlation_neg - (-1.0)) < 0.01

        # No correlation
        y_values_random = [5.0, 5.0, 5.0, 5.0, 5.0]
        correlation_none = trend_analyzer._calculate_correlation(x_values, y_values_random)
        assert abs(correlation_none) < 0.01

    def test_calculate_moving_average(self, trend_analyzer):
        """Test moving average calculation."""
        values = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
        window_size = 3

        moving_avg = trend_analyzer._calculate_moving_average(values, window_size)

        # Expected: [1.0, 1.5, 2.0, 3.0, 4.0, 5.0]
        expected = [1.0, 1.5, 2.0, 3.0, 4.0, 5.0]
        for i, val in enumerate(moving_avg):
            assert abs(val - expected[i]) < 0.01

    def test_calculate_anomaly_scores(self, trend_analyzer):
        """Test anomaly score calculation."""
        # Normal distribution with one outlier
        values = [1.0, 1.1, 0.9, 1.05, 0.95, 5.0]  # 5.0 is the outlier
        anomaly_scores = trend_analyzer._calculate_anomaly_scores(values)

        # The outlier should have the highest anomaly score
        max_score_index = anomaly_scores.index(max(anomaly_scores))
        assert max_score_index == 5  # Index of the outlier

    def test_detect_anomalies(self, trend_analyzer, sample_historical_metrics):
        """Test anomaly detection."""
        # Analyze trends first
        trends = trend_analyzer.analyze_trends(sample_historical_metrics)

        # Create current metrics with anomalous values
        anomalous_results = [
            BenchmarkResult(
                name="test_benchmark",
                execution_time=3.0,  # Much higher than historical values (1.0-1.45)
                memory_usage=200.0,  # Much higher than historical values (100-118)
                throughput=500.0,  # Much lower than historical values (910-1000)
            ),
            BenchmarkResult(
                name="stable_benchmark",
                execution_time=0.5,  # Normal value
                memory_usage=50.0,
                throughput=500.0,
            ),
        ]

        current_metrics = PerformanceMetrics(
            build_id="current-build",
            timestamp=datetime.now(),
            results=anomalous_results,
        )

        alerts = trend_analyzer.detect_anomalies(current_metrics, trends)

        # Should detect anomalies in test_benchmark
        assert len(alerts) > 0
        alert_benchmarks = [alert.benchmark_name for alert in alerts]
        assert "test_benchmark" in alert_benchmarks

        # Check alert properties
        exec_time_alerts = [a for a in alerts if a.metric_name == "execution_time"]
        if exec_time_alerts:
            alert = exec_time_alerts[0]
            assert alert.severity in [AlertSeverity.CRITICAL, AlertSeverity.WARNING]
            assert alert.anomaly_score > 2.0  # Should be high anomaly score
            assert len(alert.recommendations) > 0
            assert len(alert.root_cause_indicators) > 0

    def test_determine_severity(self, trend_analyzer):
        """Test severity determination logic."""
        # Critical threshold (25%)
        severity = trend_analyzer._determine_severity(30.0, "execution_time")
        assert severity == AlertSeverity.CRITICAL

        # Warning threshold (10%)
        severity = trend_analyzer._determine_severity(15.0, "execution_time")
        assert severity == AlertSeverity.WARNING

        # Below warning threshold
        severity = trend_analyzer._determine_severity(5.0, "execution_time")
        assert severity == AlertSeverity.INFO

    def test_generate_recommendations(self, trend_analyzer):
        """Test recommendation generation."""
        trend_data = TrendData(
            metric_name="execution_time",
            benchmark_name="test_benchmark",
            trend_direction="increasing",
        )

        # Test execution time regression
        recommendations = trend_analyzer._generate_recommendations(
            "execution_time", 20.0, trend_data
        )
        assert len(recommendations) > 0
        assert any("bottlenecks" in rec.lower() for rec in recommendations)

        # Test memory usage regression
        recommendations = trend_analyzer._generate_recommendations("memory_usage", 25.0, trend_data)
        assert len(recommendations) > 0
        assert any("memory leak" in rec.lower() for rec in recommendations)

        # Test throughput regression
        recommendations = trend_analyzer._generate_recommendations("throughput", -15.0, trend_data)
        assert len(recommendations) > 0
        assert any(
            "blocking" in rec.lower() or "contention" in rec.lower() for rec in recommendations
        )

    def test_analyze_root_cause(self, trend_analyzer):
        """Test root cause analysis."""
        trend_data = TrendData(
            metric_name="execution_time",
            benchmark_name="test_benchmark",
            trend_direction="increasing",
            correlation=0.85,
            values=[1.0, 1.1, 1.2, 1.3, 1.4],
            moving_average=[1.0, 1.05, 1.1, 1.15, 1.2],
        )

        indicators = trend_analyzer._analyze_root_cause(trend_data, 2.0, 3.5)

        assert len(indicators) > 0
        assert any("3σ" in indicator for indicator in indicators)  # Extreme deviation
        assert any("increasing trend" in indicator for indicator in indicators)

    def test_cooldown_functionality(self, trend_analyzer):
        """Test alert cooldown functionality."""
        alert = TrendAlert(
            metric_name="execution_time",
            benchmark_name="test_benchmark",
            severity=AlertSeverity.WARNING,
            message="Test alert",
            current_value=1.5,
            baseline_value=1.0,
            change_percent=50.0,
            threshold_violated="test",
        )

        # Should not be in cooldown initially
        assert not trend_analyzer._is_in_cooldown(alert)

        # Update cooldown
        trend_analyzer._update_cooldown(alert)

        # Should now be in cooldown
        assert trend_analyzer._is_in_cooldown(alert)

    def test_cooldown_persistence(self, trend_analyzer, temp_config_file):
        """Test cooldown data persistence."""
        alert = TrendAlert(
            metric_name="execution_time",
            benchmark_name="test_benchmark",
            severity=AlertSeverity.WARNING,
            message="Test alert",
            current_value=1.5,
            baseline_value=1.0,
            change_percent=50.0,
            threshold_violated="test",
        )

        # Update cooldown and save
        trend_analyzer._update_cooldown(alert)
        trend_analyzer._save_cooldown_data()

        # Create new analyzer instance and check if cooldown persists
        new_analyzer = TrendAnalyzer(alert_config_path=temp_config_file)
        assert len(new_analyzer.cooldown_data) > 0

    @patch.dict("os.environ", {"GITHUB_STEP_SUMMARY": "/tmp/test_summary"})
    def test_add_step_summary(self, trend_analyzer):
        """Test step summary addition."""
        alert = TrendAlert(
            metric_name="execution_time",
            benchmark_name="test_benchmark",
            severity=AlertSeverity.WARNING,
            message="Test alert",
            current_value=1.5,
            baseline_value=1.0,
            change_percent=50.0,
            threshold_violated="test",
            trend_direction="increasing",
            trend_strength=0.8,
        )

        with patch("builtins.open", mock_open()) as mock_file:
            trend_analyzer._add_step_summary(alert)
            mock_file.assert_called_once_with("/tmp/test_summary", "a")

    def test_trigger_alerts(self, trend_analyzer):
        """Test alert triggering and summary generation."""
        alerts = [
            TrendAlert(
                metric_name="execution_time",
                benchmark_name="test_benchmark",
                severity=AlertSeverity.WARNING,
                message="Test alert",
                current_value=1.5,
                baseline_value=1.0,
                change_percent=50.0,
                threshold_violated="test",
            )
        ]

        # Mock environment variable and file operations
        with (
            patch.dict("os.environ", {"GITHUB_STEP_SUMMARY": "/tmp/test_summary"}),
            patch("builtins.open", mock_open()),
        ):
            summary = trend_analyzer.trigger_alerts(alerts)

        assert summary["alerts_processed"] == 1
        assert summary["step_summaries_added"] == 1
        assert summary["alerts_suppressed_by_cooldown"] == 0
        assert len(summary["errors"]) == 0

    def test_github_issue_creation_logic(self, trend_analyzer):
        """Test GitHub issue creation logic."""
        # Test with critical alert
        critical_alert = TrendAlert(
            metric_name="execution_time",
            benchmark_name="test_benchmark",
            severity=AlertSeverity.CRITICAL,
            message="Critical alert",
            current_value=2.0,
            baseline_value=1.0,
            change_percent=100.0,
            threshold_violated="test",
        )

        # Should create issue for critical alerts by default
        assert trend_analyzer._should_create_github_issue(critical_alert)

        # Test with warning alert
        warning_alert = TrendAlert(
            metric_name="execution_time",
            benchmark_name="test_benchmark",
            severity=AlertSeverity.WARNING,
            message="Warning alert",
            current_value=1.2,
            baseline_value=1.0,
            change_percent=20.0,
            threshold_violated="test",
        )

        # Should not create issue for warnings by default
        assert not trend_analyzer._should_create_github_issue(warning_alert)

    def test_historical_context_generation(self, trend_analyzer):
        """Test historical context generation."""
        trend_data = TrendData(
            metric_name="execution_time",
            benchmark_name="test_benchmark",
            values=[1.0, 1.1, 1.2, 1.3, 1.4],
            trend_direction="increasing",
            correlation=0.85,
        )

        context = trend_analyzer._generate_historical_context(trend_data)

        assert "Historical range:" in context
        assert "Trend: increasing" in context
        assert "Based on 5 historical measurements" in context
        assert "correlation: 0.85" in context

    def test_insufficient_data_handling(self, trend_analyzer):
        """Test handling of insufficient historical data."""
        # Create metrics with only 2 data points (below minimum of 3)
        limited_metrics = [
            PerformanceMetrics(
                build_id="build-1",
                timestamp=datetime.now() - timedelta(days=2),
                results=[BenchmarkResult(name="test", execution_time=1.0)],
            ),
            PerformanceMetrics(
                build_id="build-2",
                timestamp=datetime.now() - timedelta(days=1),
                results=[BenchmarkResult(name="test", execution_time=1.1)],
            ),
        ]

        trends = trend_analyzer.analyze_trends(limited_metrics)

        # Should not generate trends with insufficient data
        assert len(trends) == 0

    def test_edge_cases_correlation_calculation(self, trend_analyzer):
        """Test edge cases in correlation calculation."""
        # Empty lists
        correlation = trend_analyzer._calculate_correlation([], [])
        assert correlation == 0.0

        # Single data point
        correlation = trend_analyzer._calculate_correlation([1], [1.0])
        assert correlation == 0.0

        # Zero variance in y-values
        correlation = trend_analyzer._calculate_correlation([1, 2, 3], [5.0, 5.0, 5.0])
        assert correlation == 0.0

        # Zero variance in x-values (shouldn't happen in practice)
        correlation = trend_analyzer._calculate_correlation([1, 1, 1], [1.0, 2.0, 3.0])
        assert correlation == 0.0


class TestTrendData:
    """Test cases for TrendData dataclass."""

    def test_trend_data_creation(self):
        """Test TrendData creation and default values."""
        trend_data = TrendData(metric_name="execution_time", benchmark_name="test_benchmark")

        assert trend_data.metric_name == "execution_time"
        assert trend_data.benchmark_name == "test_benchmark"
        assert trend_data.values == []
        assert trend_data.timestamps == []
        assert trend_data.correlation == 0.0
        assert trend_data.trend_direction == "stable"

    def test_trend_data_with_values(self):
        """Test TrendData with provided values."""
        values = [1.0, 1.1, 1.2]
        timestamps = [datetime(2024, 1, i) for i in range(1, 4)]

        trend_data = TrendData(
            metric_name="memory_usage",
            benchmark_name="test_benchmark",
            values=values,
            timestamps=timestamps,
            correlation=0.95,
            trend_direction="increasing",
        )

        assert trend_data.values == values
        assert trend_data.timestamps == timestamps
        assert trend_data.correlation == 0.95
        assert trend_data.trend_direction == "increasing"


class TestTrendAlert:
    """Test cases for TrendAlert dataclass."""

    def test_trend_alert_creation(self):
        """Test TrendAlert creation with extended properties."""
        alert = TrendAlert(
            metric_name="execution_time",
            benchmark_name="test_benchmark",
            severity=AlertSeverity.WARNING,
            message="Performance regression detected",
            current_value=1.5,
            baseline_value=1.0,
            change_percent=50.0,
            threshold_violated="relative_threshold",
            trend_direction="increasing",
            trend_strength=0.8,
            anomaly_score=2.5,
            historical_context="Historical data shows increasing trend",
            root_cause_indicators=["Recent code changes", "System load increase"],
            recommendations=["Review recent commits", "Check system resources"],
        )

        assert alert.metric_name == "execution_time"
        assert alert.severity == AlertSeverity.WARNING
        assert alert.trend_direction == "increasing"
        assert alert.trend_strength == 0.8
        assert alert.anomaly_score == 2.5
        assert len(alert.root_cause_indicators) == 2
        assert len(alert.recommendations) == 2

    def test_trend_alert_defaults(self):
        """Test TrendAlert with default values."""
        alert = TrendAlert(
            metric_name="memory_usage",
            benchmark_name="test_benchmark",
            severity=AlertSeverity.CRITICAL,
            message="Critical memory usage increase",
            current_value=200.0,
            baseline_value=100.0,
            change_percent=100.0,
            threshold_violated="both_relative_and_absolute",
        )

        assert alert.trend_direction == "unknown"
        assert alert.trend_strength == 0.0
        assert alert.anomaly_score == 0.0
        assert alert.historical_context == ""
        assert alert.root_cause_indicators == []
        assert alert.recommendations == []


class TestAlertCooldown:
    """Test cases for AlertCooldown dataclass."""

    def test_alert_cooldown_creation(self):
        """Test AlertCooldown creation."""
        cooldown = AlertCooldown(
            benchmark_name="test_benchmark",
            metric_name="execution_time",
            last_alert_time=datetime(2024, 1, 1, 12, 0, 0),
            severity=AlertSeverity.WARNING,
        )

        assert cooldown.benchmark_name == "test_benchmark"
        assert cooldown.metric_name == "execution_time"
        assert cooldown.last_alert_time == datetime(2024, 1, 1, 12, 0, 0)
        assert cooldown.severity == AlertSeverity.WARNING
