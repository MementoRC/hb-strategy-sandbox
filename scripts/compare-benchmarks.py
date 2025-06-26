#!/usr/bin/env python3
"""
Performance benchmark comparison script.
Based on patterns from llm-task-framework reference project.
"""

import argparse
import json
import sys
from typing import Any


def load_benchmark_data(file_path: str) -> dict[str, Any] | None:
    """Load benchmark data from JSON file."""
    try:
        with open(file_path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        return None


def extract_benchmark_metrics(data: dict[str, Any]) -> dict[str, float]:
    """Extract key metrics from benchmark data."""
    metrics = {}

    if "benchmarks" in data:
        for benchmark in data["benchmarks"]:
            name = benchmark.get("name", "unknown")

            # Extract different timing metrics
            if "stats" in benchmark:
                stats = benchmark["stats"]
                metrics[f"{name}_mean"] = stats.get("mean", 0.0)
                metrics[f"{name}_min"] = stats.get("min", 0.0)
                metrics[f"{name}_max"] = stats.get("max", 0.0)
                metrics[f"{name}_stddev"] = stats.get("stddev", 0.0)

            # pytest-benchmark format
            elif "mean" in benchmark:
                metrics[f"{name}_mean"] = benchmark.get("mean", 0.0)
                metrics[f"{name}_min"] = benchmark.get("min", 0.0)
                metrics[f"{name}_max"] = benchmark.get("max", 0.0)

    return metrics


def calculate_performance_change(baseline: float, current: float) -> tuple[float, str]:
    """Calculate percentage change and determine if it's a regression."""
    if baseline == 0:
        return 0.0, "baseline_zero"

    change_percent = ((current - baseline) / baseline) * 100

    # For timing metrics, an increase is typically bad (regression)
    if change_percent > 10:  # More than 10% slower
        status = "regressions"
    elif change_percent > 5:  # 5-10% slower
        status = "warnings"
    elif change_percent < -5:  # More than 5% faster
        status = "improvements"
    else:
        status = "stable"

    return change_percent, status


def compare_benchmarks(baseline_file: str, current_file: str) -> dict[str, Any]:
    """Compare two benchmark files and return analysis."""
    baseline_data = load_benchmark_data(baseline_file)
    current_data = load_benchmark_data(current_file)

    if not baseline_data or not current_data:
        return {"error": "Could not load benchmark data"}

    baseline_metrics = extract_benchmark_metrics(baseline_data)
    current_metrics = extract_benchmark_metrics(current_data)

    comparison: dict[str, Any] = {
        "summary": {
            "total_benchmarks": len(current_metrics),
            "regressions": 0,
            "improvements": 0,
            "warnings": 0,
            "stable": 0,
            "new": 0,
            "baseline_zero": 0,
        },
        "details": [],
    }

    for metric_name in current_metrics:
        if metric_name in baseline_metrics:
            baseline_val = baseline_metrics[metric_name]
            current_val = current_metrics[metric_name]

            change_percent, status = calculate_performance_change(baseline_val, current_val)

            comparison["details"].append(
                {
                    "metric": metric_name,
                    "baseline": baseline_val,
                    "current": current_val,
                    "change_percent": round(change_percent, 2),
                    "status": status,
                }
            )

            comparison["summary"][status] += 1
        else:
            # New benchmark
            comparison["details"].append(
                {
                    "metric": metric_name,
                    "baseline": None,
                    "current": current_metrics[metric_name],
                    "change_percent": None,
                    "status": "new",
                }
            )
            comparison["summary"]["new"] += 1

    return comparison


def generate_report(comparison: dict[str, Any], output_format: str = "markdown") -> str:
    """Generate a formatted report from comparison data."""
    if "error" in comparison:
        return f"Error: {comparison['error']}"

    summary = comparison["summary"]

    if output_format == "markdown":
        report = "# Performance Benchmark Comparison\n\n"

        # Summary section
        report += "## Summary\n\n"
        report += f"- **Total Benchmarks**: {len(comparison['details'])}\n"
        report += f"- **Regressions**: {summary['regressions']} ❌\n"
        report += f"- **Warnings**: {summary['warnings']} ⚠️\n"
        report += f"- **Improvements**: {summary['improvements']} ✅\n"
        report += f"- **Stable**: {summary['stable']} ➡️\n"
        report += f"- **New**: {summary['new']} 🆕\n\n"

        # Overall status
        if summary["regressions"] > 0:
            report += "**🚨 Status: PERFORMANCE REGRESSION DETECTED**\n\n"
        elif summary["warnings"] > 0:
            report += "**⚠️ Status: PERFORMANCE WARNINGS**\n\n"
        else:
            report += "**✅ Status: PERFORMANCE OK**\n\n"

        # Detailed results
        if comparison["details"]:
            report += "## Detailed Results\n\n"
            report += "| Benchmark | Baseline | Current | Change | Status |\n"
            report += "|-----------|----------|---------|--------|--------|\n"

            for detail in comparison["details"]:
                metric = detail["metric"]
                baseline = f"{detail['baseline']:.4f}" if detail["baseline"] is not None else "N/A"
                current = f"{detail['current']:.4f}"

                if detail["change_percent"] is not None:
                    change = f"{detail['change_percent']:+.1f}%"
                else:
                    change = "NEW"

                status_icon = {
                    "regressions": "❌",
                    "warnings": "⚠️",
                    "improvements": "✅",
                    "stable": "➡️",
                    "new": "🆕",
                    "baseline_zero": "❓",
                }.get(detail["status"], "❓")

                report += f"| {metric} | {baseline} | {current} | {change} | {status_icon} |\n"

    elif output_format == "github":
        # GitHub Actions format
        if summary["regressions"] > 0:
            report = (
                f"::error::Performance regression detected in {summary['regressions']} benchmark(s)"
            )
        elif summary["warnings"] > 0:
            report = f"::warning::Performance warnings in {summary['warnings']} benchmark(s)"
        else:
            report = f"::notice::Performance check passed - {summary['total_benchmarks']} benchmarks stable"

    else:
        # Plain text format
        report = "Performance Comparison Summary:\n"
        report += f"Total: {summary['total_benchmarks']}, "
        report += f"Regressions: {summary['regressions']}, "
        report += f"Warnings: {summary['warnings']}, "
        report += f"Improvements: {summary['improvements']}, "
        report += f"Stable: {summary['stable']}\n"

    return report


def main():
    """Main entry point for benchmark comparison."""
    parser = argparse.ArgumentParser(description="Compare performance benchmarks")
    parser.add_argument("baseline", help="Baseline benchmark file (JSON)")
    parser.add_argument("current", help="Current benchmark file (JSON)")
    parser.add_argument(
        "--format", choices=["markdown", "github", "text"], default="markdown", help="Output format"
    )
    parser.add_argument("--output", help="Output file (default: stdout)")
    parser.add_argument(
        "--fail-on-regression",
        action="store_true",
        help="Exit with non-zero code if regressions detected",
    )

    args = parser.parse_args()

    # Perform comparison
    comparison = compare_benchmarks(args.baseline, args.current)

    # Generate report
    report = generate_report(comparison, args.format)

    # Output report
    if args.output:
        with open(args.output, "w") as f:
            f.write(report)
        print(f"Report written to {args.output}")
    else:
        print(report)

    # Exit with appropriate code
    if args.fail_on_regression and "error" not in comparison:
        summary = comparison["summary"]
        if summary["regressions"] > 0:
            sys.exit(1)  # Fail on regressions
        elif summary["warnings"] > 0:
            sys.exit(2)  # Warning code for warnings


if __name__ == "__main__":
    main()
