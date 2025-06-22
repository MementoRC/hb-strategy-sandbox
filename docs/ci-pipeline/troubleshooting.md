# Troubleshooting Guide

This guide provides solutions for common issues encountered when using the HB Strategy Sandbox CI pipeline.

## Common Issues

### Performance Monitoring Issues

#### Issue: Benchmark Results Not Found

**Symptoms:**
- Error: "Benchmark file not found"
- Missing performance reports
- Empty performance data

**Solutions:**

1. **Verify benchmark file path:**
   ```bash
   # Check if benchmark file exists
   ls -la reports/benchmark.json

   # Verify pytest-benchmark is generating output
   pytest tests/performance/ --benchmark-json=reports/benchmark.json
   ```

2. **Check pytest-benchmark configuration:**
   ```python
   # In pyproject.toml
   [tool.pytest.ini_options]
   markers = [
       "benchmark: marks tests as performance benchmarks"
   ]
   ```

3. **Ensure benchmark tests are properly marked:**
   ```python
   import pytest

   @pytest.mark.benchmark
   def test_performance(benchmark):
       result = benchmark(function_to_test)
       assert result is not None
   ```

#### Issue: Performance Baselines Missing

**Symptoms:**
- Warning: "No baseline found for comparison"
- Comparison reports show no baseline data
- Trend analysis unavailable

**Solutions:**

1. **Create initial baseline:**
   ```bash
   python -m strategy_sandbox.performance.collector \
     --create-baseline \
     --benchmark-file reports/benchmark.json \
     --baseline-file performance_data/baselines/main_baseline.json
   ```

2. **Verify baseline directory structure:**
   ```
   performance_data/
   ├── baselines/
   │   ├── main_baseline.json
   │   └── feature_baseline.json
   └── history/
       └── performance_history.json
   ```

3. **Check baseline file format:**
   ```bash
   # Validate baseline JSON
   python -c "import json; print(json.load(open('performance_data/baselines/main_baseline.json')))"
   ```

#### Issue: Inconsistent Performance Results

**Symptoms:**
- High variance in benchmark results
- Flaky performance tests
- Unreliable trend analysis

**Solutions:**

1. **Increase benchmark iterations:**
   ```python
   @pytest.mark.benchmark(
       min_rounds=10,
       max_time=30,
       warmup=True
   )
   def test_stable_performance(benchmark):
       # Test implementation
       pass
   ```

2. **Use system isolation:**
   ```bash
   # Run with higher priority
   nice -n -10 pytest tests/performance/

   # Disable CPU frequency scaling
   sudo cpupower frequency-set --governor performance
   ```

3. **Control test environment:**
   ```python
   @pytest.fixture(autouse=True)
   def performance_isolation():
       # Disable garbage collection during benchmarks
       import gc
       gc.disable()
       yield
       gc.enable()
   ```

### Security Scanning Issues

#### Issue: Vulnerability Database Access

**Symptoms:**
- Error: "Failed to fetch vulnerability data"
- Timeout errors during security scans
- Empty security reports

**Solutions:**

1. **Check network connectivity:**
   ```bash
   # Test OSV database access
   curl -I https://osv.dev/api/v1/vulns

   # Test GitHub Advisory access
   curl -I https://api.github.com/advisories
   ```

2. **Configure proxy settings:**
   ```bash
   export HTTPS_PROXY=http://proxy.company.com:8080
   export HTTP_PROXY=http://proxy.company.com:8080
   ```

3. **Use offline vulnerability database:**
   ```python
   # Download vulnerability database locally
   python -m strategy_sandbox.security.analyzer \
     --offline-db /path/to/local/vuln_db \
     --project-path .
   ```

#### Issue: SBOM Generation Failures

**Symptoms:**
- Error: "Unable to generate SBOM"
- Incomplete dependency information
- Format validation errors

**Solutions:**

1. **Verify package manager detection:**
   ```bash
   # Check detected package managers
   python -c "
   from strategy_sandbox.security.analyzer import DependencyAnalyzer
   analyzer = DependencyAnalyzer('.')
   print(analyzer.detect_package_managers())
   "
   ```

2. **Ensure dependency files are present:**
   ```bash
   # Check for dependency files
   ls -la pyproject.toml pixi.lock requirements.txt setup.py
   ```

3. **Validate SBOM format:**
   ```bash
   # Use external validator
   cyclonedx-cli validate --input-file sbom.json
   ```

#### Issue: False Positive Vulnerabilities

**Symptoms:**
- Vulnerabilities reported for unused code paths
- Development-only vulnerabilities in production scans
- Known safe usage patterns flagged

**Solutions:**

1. **Configure vulnerability exceptions:**
   ```yaml
   # In vulnerability_policy.yaml
   exceptions:
     - id: "CVE-2023-12345"
       package: "example-package"
       reason: "Not exploitable in our usage"
       expires: "2024-06-01"
   ```

2. **Exclude development dependencies:**
   ```python
   sbom_generator.generate_sbom(
       format_type="cyclonedx",
       include_dev_dependencies=False
   )
   ```

3. **Use severity filtering:**
   ```bash
   python -m strategy_sandbox.security.analyzer \
     --min-severity medium \
     --exclude-dev-deps
   ```

### GitHub Integration Issues

#### Issue: Step Summary Not Appearing

**Symptoms:**
- GitHub step summary is empty
- Reports not showing in workflow output
- Missing performance/security summaries

**Solutions:**

1. **Verify GitHub environment variables:**
   ```bash
   echo $GITHUB_STEP_SUMMARY
   echo $GITHUB_WORKSPACE
   echo $GITHUB_ACTIONS
   ```

2. **Check permissions:**
   ```yaml
   # In GitHub workflow
   permissions:
     contents: read
     actions: write
     pull-requests: write
   ```

3. **Debug step summary writing:**
   ```python
   # Add debug logging
   import os
   import logging

   logger = logging.getLogger(__name__)
   summary_path = os.getenv('GITHUB_STEP_SUMMARY')
   logger.info(f"Step summary path: {summary_path}")
   ```

#### Issue: Artifact Upload Failures

**Symptoms:**
- Error: "Failed to upload artifact"
- Missing report files in workflow artifacts
- Artifact size limits exceeded

**Solutions:**

1. **Check artifact size:**
   ```bash
   # Check report file sizes
   du -h reports/

   # Compress large reports
   gzip reports/*.json
   ```

2. **Use artifact name patterns:**
   ```yaml
   - name: Upload Reports
     uses: actions/upload-artifact@v4
     with:
       name: ci-reports-${{ github.run_id }}
       path: reports/
   ```

3. **Implement incremental uploads:**
   ```bash
   # Upload only essential reports
   tar -czf essential-reports.tar.gz \
     reports/security_summary.json \
     reports/performance_summary.json
   ```

### Configuration Issues

#### Issue: Invalid Configuration Files

**Symptoms:**
- Error: "Configuration validation failed"
- Unexpected behavior from threshold settings
- YAML parsing errors

**Solutions:**

1. **Validate YAML syntax:**
   ```bash
   # Check YAML syntax
   python -c "import yaml; yaml.safe_load(open('config.yaml'))"

   # Use yamllint for detailed validation
   yamllint strategy_sandbox/performance/alert_config.yaml
   ```

2. **Check configuration schema:**
   ```python
   from strategy_sandbox.performance.models import ThresholdConfig

   # Validate configuration
   config = ThresholdConfig.from_file("config.yaml")
   print(config.validate())
   ```

3. **Use configuration templates:**
   ```bash
   # Copy from template
   cp strategy_sandbox/performance/performance_thresholds.yaml.template \
      strategy_sandbox/performance/performance_thresholds.yaml
   ```

#### Issue: Environment Variable Missing

**Symptoms:**
- Error: "Required environment variable not set"
- Authentication failures
- Missing GitHub context

**Solutions:**

1. **Set required environment variables:**
   ```bash
   # For GitHub integration
   export GITHUB_TOKEN=${{ secrets.GITHUB_TOKEN }}
   export GITHUB_REPOSITORY=${{ github.repository }}
   export GITHUB_RUN_ID=${{ github.run_id }}
   ```

2. **Use environment file:**
   ```bash
   # Create .env file
   cat > .env << EOF
   GITHUB_TOKEN=your_token_here
   PERFORMANCE_BASELINE_PATH=performance_data/baselines
   SECURITY_DB_PATH=security_data/vuln_db
   EOF
   ```

3. **Validate environment setup:**
   ```python
   # Check environment
   import os
   required_vars = ['GITHUB_TOKEN', 'GITHUB_REPOSITORY']
   missing = [var for var in required_vars if not os.getenv(var)]
   if missing:
       print(f"Missing environment variables: {missing}")
   ```

### Pixi Environment Issues

#### Issue: Environment Resolution Failures

**Symptoms:**
- Error: "Failed to resolve environment"
- Dependency conflicts in pixi environment
- Commands fail with import errors

**Solutions:**

1. **Clear pixi cache:**
   ```bash
   # Clear environment cache
   pixi clean cache

   # Recreate environment
   pixi install --force-reinstall
   ```

2. **Check environment configuration:**
   ```bash
   # Verify environment setup
   pixi info

   # Check specific environment
   pixi list -e default
   ```

3. **Debug dependency conflicts:**
   ```bash
   # Show dependency tree
   pixi tree

   # Check for conflicts
   pixi check
   ```

#### Issue: Missing Dependencies

**Symptoms:**
- ImportError during test execution
- Commands not found in environment
- Version conflicts

**Solutions:**

1. **Install missing dependencies:**
   ```bash
   # Add missing package
   pixi add package-name

   # Install from specific channel
   pixi add conda-forge::package-name
   ```

2. **Check dependency sources:**
   ```toml
   # In pyproject.toml
   [tool.pixi.dependencies]
   package-name = ">=1.0.0"

   [tool.pixi.pypi-dependencies]
   pypi-package = ">=2.0.0"
   ```

3. **Use environment-specific dependencies:**
   ```toml
   [tool.pixi.feature.dev.dependencies]
   dev-only-package = "*"
   ```

### CI/CD Pipeline Issues

#### Issue: Timeout Errors

**Symptoms:**
- Workflow timeouts during test execution
- Long-running security scans
- Performance benchmarks taking too long

**Solutions:**

1. **Optimize test execution:**
   ```bash
   # Run tests in parallel
   pytest -n auto tests/

   # Use faster test selection
   pytest -m "not slow" tests/
   ```

2. **Increase timeout limits:**
   ```yaml
   # In GitHub workflow
   - name: Run Tests
     run: pytest tests/
     timeout-minutes: 30
   ```

3. **Implement test sharding:**
   ```bash
   # Split tests across multiple jobs
   pytest --collect-only --quiet | split -l 100 - test_chunk_
   ```

#### Issue: Resource Limits

**Symptoms:**
- Out of memory errors
- Disk space exhaustion
- CPU resource constraints

**Solutions:**

1. **Monitor resource usage:**
   ```bash
   # Check memory usage during tests
   pytest tests/ --memray

   # Monitor disk space
   df -h
   ```

2. **Optimize resource usage:**
   ```python
   # Use memory-efficient data structures
   import sys

   # Clean up after tests
   @pytest.fixture(autouse=True)
   def cleanup():
       yield
       # Cleanup resources
       gc.collect()
   ```

3. **Use resource limits:**
   ```yaml
   # In GitHub workflow
   jobs:
     test:
       runs-on: ubuntu-latest-4-cores
   ```

## Debugging Techniques

### Verbose Logging

Enable detailed logging for debugging:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Component Isolation

Test individual components:

```python
# Test performance collector independently
from strategy_sandbox.performance.collector import PerformanceCollector

collector = PerformanceCollector()
result = collector.collect_system_info()
print(result)
```

### Environment Validation

Validate the complete environment:

```bash
# Run environment checks
python -m strategy_sandbox.diagnostics.environment_check

# Verify all dependencies
python -m strategy_sandbox.diagnostics.dependency_check
```

## Getting Help

### Log Analysis

When reporting issues, include:

1. **Complete error messages and stack traces**
2. **Environment information** (OS, Python version, package versions)
3. **Configuration files** (with sensitive data removed)
4. **Steps to reproduce** the issue

### Diagnostic Information

Collect diagnostic information:

```bash
# Generate diagnostic report
python -m strategy_sandbox.diagnostics.generate_report \
  --output diagnostic_report.json

# Include system information
python -m strategy_sandbox.diagnostics.system_info \
  --verbose
```

### Support Channels

- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: Check the latest documentation for updates
- **Community**: Join community discussions for peer support

For urgent issues or security vulnerabilities, follow the security reporting process outlined in the project's security policy.
