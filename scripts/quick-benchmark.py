#!/usr/bin/env python3
"""
Quick benchmark script for pre-commit hook.
Runs lightweight performance checks to catch major regressions early.
"""

import json
import sys
import time
from pathlib import Path
from typing import Any


def quick_import_benchmark() -> float:
    """Benchmark package import time."""
    start = time.perf_counter()
    try:
        import strategy_sandbox  # noqa: F401

        end = time.perf_counter()
        return end - start
    except ImportError as e:
        print(f"Import failed: {e}")
        return float("inf")


def quick_initialization_benchmark() -> float:
    """Benchmark basic sandbox initialization."""
    start = time.perf_counter()
    try:
        from strategy_sandbox.core.environment import SandboxConfiguration, SandboxEnvironment

        config = SandboxConfiguration()
        SandboxEnvironment(config=config)  # Test environment creation

        end = time.perf_counter()
        return end - start
    except Exception as e:
        print(f"Initialization failed: {e}")
        return float("inf")


def run_quick_benchmarks() -> dict[str, Any]:
    """Run quick benchmarks and return results."""
    results = {"timestamp": time.time(), "benchmarks": {}}

    # Import benchmark
    import_time = quick_import_benchmark()
    results["benchmarks"]["import_time"] = import_time

    # Initialization benchmark
    init_time = quick_initialization_benchmark()
    results["benchmarks"]["initialization_time"] = init_time

    return results


def check_performance_thresholds(results: dict[str, Any]) -> bool:
    """Check if results exceed performance thresholds."""
    benchmarks = results["benchmarks"]

    # Define thresholds (in seconds)
    thresholds = {
        "import_time": 1.0,  # Package import should be under 1 second
        "initialization_time": 2.0,  # Initialization should be under 2 seconds
    }

    failures = []

    for benchmark, value in benchmarks.items():
        if benchmark in thresholds:
            threshold = thresholds[benchmark]
            if value > threshold:
                failures.append(f"{benchmark}: {value:.3f}s > {threshold}s")

    if failures:
        print("Performance threshold failures:")
        for failure in failures:
            print(f"  - {failure}")
        return False

    return True


def main():
    """Main entry point."""
    print("Running quick performance check...")

    results = run_quick_benchmarks()

    # Save results for potential analysis
    results_file = Path("reports/quick-benchmark.json")
    results_file.parent.mkdir(exist_ok=True)

    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)

    # Check thresholds
    passed = check_performance_thresholds(results)

    # Print summary
    print("Quick benchmark results:")
    for name, value in results["benchmarks"].items():
        print(f"  {name}: {value:.3f}s")

    if passed:
        print("✅ Performance check passed")
        sys.exit(0)
    else:
        print("❌ Performance check failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
