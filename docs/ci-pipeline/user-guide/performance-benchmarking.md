# Performance Benchmarking Guide

This guide covers how to set up, configure, and optimize performance benchmarking in the HB Strategy Sandbox CI pipeline.

## Overview

The performance benchmarking system provides:
- **Automated benchmark execution** during CI builds
- **Historical performance tracking** with trend analysis
- **Regression detection** with configurable thresholds
- **Multi-platform comparison** across different environments

## Setting Up Benchmarks

### Basic Benchmark Configuration

Add performance benchmarks to your test suite using pytest-benchmark:

```python
import pytest
from strategy_sandbox.core.environment import SandboxEnvironment

def test_simulation_throughput(benchmark):
    """Benchmark simulation execution speed."""
    env = SandboxEnvironment()
    env.initialize()

    result = benchmark(run_simulation, env, duration=10.0)

    # Assertions for correctness
    assert result is not None
    assert result.trades_executed >= 0

def run_simulation(env, duration):
    """Execute a simulation for benchmarking."""
    env.reset()
    return env.run_simulation(duration)
```

### Advanced Benchmark Setup

For more complex benchmarking scenarios:

```python
@pytest.mark.benchmark(group="memory")
def test_memory_usage(benchmark):
    """Benchmark memory consumption during operations."""

    @benchmark
    def memory_intensive_operation():
        # Setup large data structures
        data = generate_large_dataset(10000)
        processor = DataProcessor()
        return processor.analyze(data)

    result = memory_intensive_operation()
    assert len(result) > 0

@pytest.mark.benchmark(
    group="throughput",
    min_rounds=5,
    max_time=30,
    warmup=True
)
def test_order_processing_speed(benchmark):
    """Benchmark order processing throughput."""
    exchange = ExchangeSimulator()
    orders = generate_test_orders(1000)

    result = benchmark(exchange.process_orders, orders)
    assert result.success_rate > 0.95
```

## Configuration

### Performance Thresholds

Configure performance expectations in `strategy_sandbox/performance/performance_thresholds.yaml`:

```yaml
# Performance threshold configuration
thresholds:
  execution_time:
    warning: 10.0  # seconds
    critical: 15.0

  memory_usage:
    warning: 500.0  # MB
    critical: 1000.0

  throughput:
    warning: -5.0   # percentage decrease
    critical: -15.0

# Benchmark-specific thresholds
benchmark_thresholds:
  test_simulation_throughput:
    execution_time:
      warning: 5.0
      critical: 10.0

  test_order_processing_speed:
    throughput:
      warning: -2.0
      critical: -10.0

# Environment-specific settings
environments:
  linux:
    memory_multiplier: 1.0
  windows:
    memory_multiplier: 1.2  # Account for higher Windows overhead
  macos:
    memory_multiplier: 1.1
```

### Alert Configuration

Set up alerting rules in `strategy_sandbox/performance/alert_config.yaml`:

```yaml
# Alert configuration
alerts:
  enabled: true

  # Alert channels
  channels:
    github_step_summary: true
    pr_comments: true
    artifacts: true

  # Alert rules
  rules:
    regression_detection:
      enabled: true
      threshold: 10.0  # percentage
      consecutive_builds: 2

    anomaly_detection:
      enabled: true
      sensitivity: 0.95
      window_size: 10

    baseline_drift:
      enabled: true
      max_drift: 25.0  # percentage
      check_interval: 7  # days

# Notification settings
notifications:
  performance_improvement:
    enabled: true
    threshold: 5.0  # percentage

  new_baseline_required:
    enabled: true
    age_threshold: 30  # days
```

## Running Benchmarks

### Local Execution

Run benchmarks locally for development:

```bash
# Run all benchmarks
pixi run performance-benchmark

# Run specific benchmark group
pytest tests/performance/ -m "benchmark" --benchmark-group=throughput

# Generate detailed reports
pytest tests/performance/ --benchmark-json=benchmark_results.json
```

### CI Integration

The pipeline automatically runs benchmarks during CI builds:

```yaml
# .github/workflows/ci.yml
- name: Run Performance Benchmarks
  run: |
    pixi run performance-benchmark
    python -m strategy_sandbox.performance.collector \
      --benchmark-file reports/benchmark.json \
      --output reports/performance_report.json
```

## Analyzing Results

### Understanding Benchmark Metrics

#### Execution Time Metrics
- **mean**: Average execution time across all runs
- **std**: Standard deviation indicating consistency
- **min/max**: Best and worst case performance
- **ops**: Operations per second (for throughput tests)

```json
{
  "test_simulation_throughput": {
    "mean": 0.125,
    "std": 0.002,
    "min": 0.123,
    "max": 0.128,
    "ops": 8.0,
    "unit": "seconds"
  }
}
```

#### Memory Usage Metrics
- **peak_memory**: Maximum memory used during execution
- **memory_increase**: Net memory increase during test
- **gc_collections**: Garbage collection activity

```json
{
  "memory_metrics": {
    "peak_memory": 450.2,
    "memory_increase": 125.7,
    "gc_collections": 3,
    "unit": "MB"
  }
}
```

### Comparison Analysis

The system automatically compares results against:

#### Historical Baselines
- **Baseline**: Established performance reference point
- **Trend**: Direction of performance change over time
- **Regression**: Significant performance degradation

```json
{
  "comparison": {
    "baseline_comparison": {
      "change_percentage": -5.2,
      "status": "regression",
      "significance": "medium"
    },
    "trend_analysis": {
      "direction": "declining",
      "slope": -0.03,
      "confidence": 0.87
    }
  }
}
```

#### Cross-Platform Analysis
Compare performance across different environments:

```json
{
  "platform_comparison": {
    "linux": { "mean": 0.125, "relative": 1.0 },
    "windows": { "mean": 0.135, "relative": 1.08 },
    "macos": { "mean": 0.128, "relative": 1.02 }
  }
}
```

## Performance Optimization

### Identifying Bottlenecks

Use benchmark results to identify performance issues:

#### CPU-Bound Operations
```python
@pytest.mark.benchmark(group="cpu")
def test_computation_intensive(benchmark):
    """Identify CPU bottlenecks."""
    result = benchmark(heavy_computation, large_dataset)

    # Check if CPU utilization is optimal
    assert result.cpu_efficiency > 0.8
```

#### Memory-Bound Operations
```python
@pytest.mark.benchmark(group="memory")
def test_memory_efficiency(benchmark):
    """Identify memory usage patterns."""
    result = benchmark.pedantic(
        memory_intensive_function,
        setup=setup_memory_test,
        teardown=cleanup_memory_test,
        rounds=10
    )

    # Verify memory is released properly
    assert result.memory_leaked < 10  # MB
```

#### I/O-Bound Operations
```python
@pytest.mark.benchmark(group="io")
def test_file_operations(benchmark):
    """Benchmark file I/O performance."""
    with temporary_directory() as temp_dir:
        result = benchmark(
            file_processing_function,
            temp_dir,
            file_count=1000
        )

    assert result.files_per_second > 100
```

### Optimization Strategies

#### Algorithm Optimization
- Profile code to identify hot spots
- Use more efficient algorithms and data structures
- Implement caching for expensive operations

#### Memory Management
- Reduce memory allocations in tight loops
- Use object pools for frequently created objects
- Implement proper cleanup and resource management

#### Parallel Processing
- Utilize asyncio for I/O-bound operations
- Implement multiprocessing for CPU-bound tasks
- Use vectorized operations with NumPy/Pandas

## Baseline Management

### Creating Baselines

Establish performance baselines for your project:

```bash
# Generate baseline from current performance
python -m strategy_sandbox.performance.collector \
  --create-baseline \
  --benchmark-file reports/benchmark.json \
  --baseline-file performance_data/baselines/main_baseline.json
```

### Updating Baselines

Update baselines when making significant changes:

```bash
# Update baseline after major feature addition
python -m strategy_sandbox.performance.collector \
  --update-baseline \
  --reason "Added new trading strategy implementation" \
  --version "v2.1.0"
```

### Baseline Versioning

Maintain multiple baselines for different contexts:

```
performance_data/baselines/
├── main_baseline.json          # Main branch baseline
├── feature_xyz_baseline.json   # Feature branch baseline
├── release_v2.0_baseline.json  # Release-specific baseline
└── archived/
    ├── v1.0_baseline.json      # Historical baselines
    └── v1.5_baseline.json
```

## Best Practices

### Benchmark Design

#### Reproducibility
```python
# Use fixed seeds for reproducible results
import random
random.seed(42)

# Control environment variables
@pytest.mark.benchmark
def test_reproducible_benchmark(benchmark):
    # Ensure consistent test conditions
    setup_deterministic_environment()
    result = benchmark(function_under_test)
    assert result.variance < 0.05  # Low variance
```

#### Isolation
```python
# Isolate benchmarks from external factors
@pytest.fixture(autouse=True)
def benchmark_isolation():
    # Clean system state before benchmark
    gc.collect()
    clear_caches()
    yield
    # Cleanup after benchmark
    reset_global_state()
```

### Performance Testing Strategy

#### Continuous Monitoring
- Run benchmarks on every CI build
- Monitor long-term performance trends
- Set up alerts for significant regressions

#### Performance Gates
- Block deployments on critical regressions
- Require performance review for large changes
- Maintain performance SLAs

#### Regular Analysis
- Weekly performance review meetings
- Monthly baseline updates
- Quarterly performance optimization sprints

## Troubleshooting

### Common Issues

#### Inconsistent Results
```
Problem: High variance in benchmark results
Solutions:
- Increase warm-up iterations
- Run more benchmark rounds
- Check for background processes
- Use benchmark.pedantic() for precise measurements
```

#### Memory Leaks
```
Problem: Increasing memory usage over time
Solutions:
- Add explicit cleanup in teardown
- Use context managers for resources
- Monitor garbage collection activity
- Profile memory usage patterns
```

#### Platform Differences
```
Problem: Different performance on different platforms
Solutions:
- Use platform-specific thresholds
- Normalize results by platform baseline
- Focus on relative performance changes
- Document platform-specific expectations
```

### Debugging Performance Issues

#### Profiling Integration
```python
import cProfile
import pstats

@pytest.mark.benchmark
def test_with_profiling(benchmark):
    """Benchmark with profiling support."""
    profiler = cProfile.Profile()

    def profiled_function():
        profiler.enable()
        result = function_under_test()
        profiler.disable()
        return result

    result = benchmark(profiled_function)

    # Save profile data for analysis
    stats = pstats.Stats(profiler)
    stats.dump_stats('profile_data.prof')
```

#### Memory Profiling
```python
from memory_profiler import profile

@profile
def memory_profiled_function():
    """Function with line-by-line memory profiling."""
    # Implementation here
    pass
```

For more detailed troubleshooting, see the [Troubleshooting Guide](../troubleshooting.md).
