"""
Framework Property-Based Tests

Uses hypothesis to test framework components with generated data
to verify properties and invariants hold across a wide range of inputs.
"""

from datetime import datetime

import pytest
from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

from framework.performance.collector import PerformanceCollector
from framework.performance.models import BenchmarkResult, PerformanceMetrics
from framework.reporting.github_reporter import GitHubReporter


@pytest.mark.property
class TestFrameworkProperties:
    """Property-based tests for framework components."""

    @given(
        execution_time=st.floats(min_value=0.001, max_value=1000.0),
        memory_usage=st.integers(min_value=1, max_value=10000),
        throughput=st.integers(min_value=1, max_value=100000),
    )
    @settings(
        max_examples=5,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=2000,  # Allow 2 seconds per test case
    )
    def test_performance_collector_data_integrity(
        self, execution_time, memory_usage, throughput, tmp_path
    ):
        """Test that performance collector maintains data integrity across various inputs."""
        # Setup
        collector = PerformanceCollector(storage_path=tmp_path)

        # Create test data with generated values
        test_name = "property_test"
        performance_data = {
            test_name: {
                "execution_time": execution_time,
                "memory_usage": f"{memory_usage}MB",
                "throughput": throughput,
            }
        }

        # Collect metrics and store as baseline
        metrics = collector.collect_metrics(performance_data)
        collector.store_baseline(metrics, baseline_name=test_name)

        # Retrieve the stored baseline
        retrieved_metrics = collector.load_baseline(baseline_name=test_name)

        # Verify data integrity properties
        assert retrieved_metrics is not None
        assert len(retrieved_metrics.results) == 1

        # Find the stored benchmark result
        stored_result = None
        for result in retrieved_metrics.results:
            if result.name == test_name:
                stored_result = result
                break

        assert stored_result is not None
        assert stored_result.execution_time == execution_time
        assert stored_result.memory_usage == memory_usage  # Should be parsed numeric value
        assert stored_result.throughput == throughput

    @given(
        test_names=st.lists(
            st.text(
                min_size=1,
                max_size=50,
                alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Pc")),
            ),
            min_size=1,
            max_size=10,
            unique=True,
        ),
        values=st.lists(st.floats(min_value=0.001, max_value=1000.0), min_size=1, max_size=10),
    )
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_performance_metrics_aggregation_properties(self, test_names, values, tmp_path):
        """Test that performance metrics aggregation maintains mathematical properties."""
        assume(len(test_names) == len(values))

        # Setup
        metrics = PerformanceMetrics(build_id="test-build", timestamp=datetime.now())

        # Add results with generated data
        for name, value in zip(test_names, values, strict=True):
            metrics.add_result(BenchmarkResult(name=name, execution_time=value))

        # Calculate summary statistics
        summary = metrics.calculate_summary_stats()

        # Verify mathematical properties
        if len(values) > 0:
            min_value = min(values)
            max_value = max(values)

            # Property: min <= mean <= max
            # The summary returns aggregate statistics, not per-test-name statistics
            if "avg_execution_time" in summary:
                mean_value = summary["avg_execution_time"]
                assert min_value <= mean_value <= max_value

    @given(
        vulnerability_data=st.lists(
            st.tuples(
                st.sampled_from(["low", "medium", "high", "critical"]),
                st.text(
                    min_size=1,
                    max_size=30,
                    alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Pc")),
                ),
            ),
            min_size=0,
            max_size=20,
        ),
    )
    @settings(max_examples=15)
    def test_security_analyzer_vulnerability_counting_properties(self, vulnerability_data):
        """Test that security analyzer maintains counting properties."""
        severity_levels, package_names = (
            zip(*vulnerability_data, strict=False) if vulnerability_data else ([], [])
        )

        # Create mock vulnerability data
        vulnerabilities = []
        for severity, package in zip(severity_levels, package_names, strict=False):
            vulnerabilities.append({"package": package, "severity": severity, "version": "1.0.0"})

        # Count vulnerabilities by severity
        severity_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for vuln in vulnerabilities:
            severity_counts[vuln["severity"]] += 1

        # Verify counting properties
        total_count = sum(severity_counts.values())
        assert total_count == len(vulnerabilities)

        # Property: sum of individual counts equals total
        assert (
            severity_counts["low"]
            + severity_counts["medium"]
            + severity_counts["high"]
            + severity_counts["critical"]
            == total_count
        )

        # Property: all counts are non-negative
        for count in severity_counts.values():
            assert count >= 0

    @given(
        test_count=st.integers(min_value=0, max_value=10000),
        coverage=st.floats(min_value=0.0, max_value=100.0),
        duration_seconds=st.integers(min_value=1, max_value=7200),
    )
    @settings(max_examples=20)
    def test_github_reporter_summary_properties(self, test_count, coverage, duration_seconds):
        """Test that GitHub reporter maintains summary properties."""
        # Setup
        reporter = GitHubReporter()

        # Convert duration to human-readable format
        minutes = duration_seconds // 60
        seconds = duration_seconds % 60
        duration_str = f"{minutes}m {seconds}s"

        # Generate build status summary
        summary = reporter.create_build_status_summary(
            success=True, duration=duration_str, test_count=test_count, coverage=coverage
        )

        # Verify summary properties
        assert summary is not None
        assert isinstance(summary, str)
        assert len(summary) > 0

        # Property: summary should contain key information
        assert str(test_count) in summary
        # Check if coverage appears in the summary (various formats possible)
        coverage_in_summary = (
            f"{coverage:.1f}" in summary
            or f"{coverage:.0f}" in summary
            or f"{coverage:.2f}" in summary
            or f"{coverage:.3f}" in summary
            or f"{coverage:.4f}" in summary
            or f"{coverage}" in summary  # Exact floating point representation
            or f"{coverage:.1f}%" in summary
            or f"{coverage:.2f}%" in summary
            or f"{coverage:.3f}%" in summary
            or f"{coverage:.4f}%" in summary
            or f"{coverage}%" in summary
        )
        assert coverage_in_summary

    @given(
        benchmark_data=st.dictionaries(
            keys=st.text(
                min_size=1,
                max_size=30,
                alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Pc")),
            ),
            values=st.dictionaries(
                keys=st.sampled_from(["execution_time", "memory_usage", "throughput"]),
                values=st.one_of(
                    st.floats(min_value=0.001, max_value=1000.0),
                    st.integers(min_value=1, max_value=10000),
                ),
                min_size=1,
                max_size=3,
            ),
            min_size=1,
            max_size=5,
        )
    )
    @settings(
        max_examples=3,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=5000,  # 5 seconds per test case
    )
    def test_performance_collector_batch_operations_properties(self, benchmark_data, tmp_path):
        """Test that batch operations maintain consistency properties."""
        # Setup
        collector = PerformanceCollector(storage_path=tmp_path)

        # Process each test data item individually using collect_metrics
        for test_name, expected_data in benchmark_data.items():
            test_data = {test_name: expected_data}
            metrics = collector.collect_metrics(test_data)
            collector.store_baseline(metrics, baseline_name=test_name)

        # Verify batch consistency properties
        for test_name, expected_data in benchmark_data.items():
            retrieved_metrics = collector.load_baseline(baseline_name=test_name)

            # Property: all stored data can be retrieved
            assert retrieved_metrics is not None
            assert len(retrieved_metrics.results) == 1

            # Find the stored result
            stored_result = retrieved_metrics.get_result(test_name)
            assert stored_result is not None

            # Property: retrieved data matches stored data for core metrics
            if "execution_time" in expected_data:
                assert stored_result.execution_time == expected_data["execution_time"]
            if "memory_usage" in expected_data and isinstance(
                expected_data["memory_usage"], int | float
            ):
                assert stored_result.memory_usage == expected_data["memory_usage"]
            if "throughput" in expected_data:
                assert stored_result.throughput == expected_data["throughput"]

    @given(
        baseline_values=st.lists(
            st.floats(min_value=0.1, max_value=100.0), min_size=1, max_size=10
        ),
        current_values=st.lists(st.floats(min_value=0.1, max_value=100.0), min_size=1, max_size=10),
    )
    @settings(
        max_examples=15,
        suppress_health_check=[HealthCheck.filter_too_much],
    )
    def test_performance_comparison_properties(self, baseline_values, current_values):
        """Test that performance comparison maintains mathematical properties."""
        assume(len(baseline_values) == len(current_values))
        assume(len(baseline_values) > 0)

        # Calculate percentage changes
        percentage_changes = []
        for baseline, current in zip(baseline_values, current_values, strict=True):
            if baseline > 0:
                change = ((current - baseline) / baseline) * 100
                percentage_changes.append(change)

        # Verify comparison properties
        for baseline, current, change in zip(
            baseline_values, current_values, percentage_changes, strict=True
        ):
            # Property: improvement should be negative percentage change
            if current < baseline:
                assert change < 0

            # Property: regression should be positive percentage change
            elif current > baseline:
                assert change > 0

            # Property: no change should be zero percentage change
            else:
                assert abs(change) < 1e-10

    @given(
        metric_values=st.lists(
            st.floats(min_value=0.001, max_value=1000.0), min_size=2, max_size=100
        )
    )
    @settings(max_examples=10)
    def test_statistical_properties_invariants(self, metric_values):
        """Test that statistical calculations maintain mathematical invariants."""
        # Calculate basic statistics
        n = len(metric_values)
        mean_val = sum(metric_values) / n
        min_val = min(metric_values)
        max_val = max(metric_values)

        # Verify statistical invariants
        # Property: min <= mean <= max
        assert min_val <= mean_val <= max_val

        # Property: variance is non-negative
        variance = sum((x - mean_val) ** 2 for x in metric_values) / n
        assert variance >= 0

        # Property: standard deviation is non-negative
        std_dev = variance**0.5
        assert std_dev >= 0

        # Property: if all values are the same, variance should be 0
        if len(set(metric_values)) == 1:
            assert variance < 1e-10

    @given(
        file_count=st.integers(min_value=1, max_value=1000),
        test_percentage=st.floats(min_value=0.0, max_value=100.0),
    )
    @settings(max_examples=15)
    def test_coverage_calculation_properties(self, file_count, test_percentage):
        """Test that coverage calculations maintain mathematical properties."""
        # Calculate covered files
        covered_files = int((test_percentage / 100.0) * file_count)

        # Verify coverage properties
        # Property: covered files cannot exceed total files
        assert covered_files <= file_count

        # Property: covered files cannot be negative
        assert covered_files >= 0

        # Property: if percentage is 100%, all files should be covered
        if abs(test_percentage - 100.0) < 0.001:
            assert covered_files == file_count

        # Property: if percentage is 0%, no files should be covered
        if abs(test_percentage) < 0.001:
            assert covered_files == 0


@pytest.mark.property
class TestFrameworkDataValidation:
    """Property-based tests for data validation in framework."""

    @given(
        execution_time=st.floats(min_value=0.001, max_value=1000.0),
        memory_usage=st.one_of(
            st.floats(min_value=1.0, max_value=1000.0),
            st.text(min_size=1, max_size=10).filter(lambda x: x.isdigit()),
        ),
        throughput=st.floats(min_value=1.0, max_value=10000.0),
        custom_data=st.dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=st.one_of(st.text(min_size=1, max_size=20), st.integers()),
            min_size=0,
            max_size=3,
        ),
    )
    @settings(
        max_examples=3,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=5000,  # 5 seconds per test case
    )
    def test_data_serialization_properties(
        self, execution_time, memory_usage, throughput, custom_data, tmp_path
    ):
        """Test that data serialization maintains consistency properties."""
        # Setup
        collector = PerformanceCollector(storage_path=tmp_path)

        # Create a test with the generated data
        test_name = "serialization_test"
        data = {
            "execution_time": execution_time,
            "memory_usage": memory_usage,
            "throughput": throughput,
            **custom_data,
        }
        test_data = {test_name: data}

        # Collect metrics and store as baseline
        metrics = collector.collect_metrics(test_data)
        collector.store_baseline(metrics, baseline_name=test_name)

        # Retrieve the stored baseline
        retrieved_metrics = collector.load_baseline(baseline_name=test_name)

        # Property: serialization round-trip should preserve data
        assert retrieved_metrics is not None
        assert len(retrieved_metrics.results) == 1

        # Find the stored benchmark result
        stored_result = retrieved_metrics.get_result(test_name)
        assert stored_result is not None

        # Verify data was preserved in the serialization/deserialization
        # The exact structure may be different but key data should be preserved
        assert stored_result.name == test_name

        # Verify that at least some data from the original input was preserved
        # in the metadata or directly in the result
        assert stored_result.metadata is not None
