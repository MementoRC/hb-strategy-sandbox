# Framework CLI Documentation

Comprehensive guide to the unified Framework CLI for Hummingbot development tools.

## Overview

The Framework CLI (`framework-cli`) provides a unified command-line interface to all development and quality assurance tools in the Hummingbot Development Framework. It replaces scattered command-line tools with a single, cohesive interface.

## Installation

### Automatic Installation

The CLI is installed automatically when you install the framework:

```bash
# Install the framework (includes CLI)
pip install -e ./framework

# Verify installation
framework-cli --version
framework-cli --help
```

### Entry Point

The CLI is available as `framework-cli` system-wide after installation:

```bash
# Global access
framework-cli --help

# Alternative access methods
python -m framework.cli --help
python framework/cli.py --help
```

## Global Options

All commands support these global options:

```bash
framework-cli [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS]
```

### Global Options

- `--version`: Show version and exit
- `--verbose, -v`: Enable verbose output
- `--help`: Show help message and exit

### Examples

```bash
# Verbose mode for debugging
framework-cli --verbose performance collect results.json

# Check version
framework-cli --version

# Help for any command
framework-cli performance --help
framework-cli security scan --help
```

## Performance Commands

### `framework-cli performance`

Performance monitoring and analysis tools.

#### `performance collect`

Collect performance metrics from benchmark results.

```bash
framework-cli performance collect RESULTS_FILE [OPTIONS]
```

**Arguments:**
- `RESULTS_FILE`: Path to benchmark results file (JSON format)

**Options:**
- `--storage-path PATH`: Directory for performance data storage (default: `performance_data`)
- `--store-baseline`: Store collected metrics as a baseline
- `--baseline-name NAME`: Name for the baseline (default: `default`)
- `--compare-baseline NAME`: Compare with existing baseline
- `--output FILE`: Output file for results (JSON format)

**Examples:**
```bash
# Basic collection
framework-cli performance collect benchmark_results.json

# Store as baseline
framework-cli performance collect results.json \
    --store-baseline --baseline-name production

# Collect and compare
framework-cli performance collect current.json \
    --compare-baseline production \
    --output comparison_report.json

# Custom storage location
framework-cli performance collect results.json \
    --storage-path ./perf_data \
    --store-baseline
```

#### `performance compare`

Compare performance metrics with advanced analysis.

```bash
framework-cli performance compare CURRENT_FILE [OPTIONS]
```

**Arguments:**
- `CURRENT_FILE`: Path to current benchmark results

**Options:**
- `--baseline NAME`: Baseline name to compare against (default: `default`)
- `--storage-path PATH`: Performance data directory (default: `performance_data`)
- `--mode MODE`: Comparison mode (`single` or `trend`, default: `single`)
- `--format FORMAT`: Output format (`markdown`, `json`, `github`, default: `markdown`)
- `--output FILE`: Output file for comparison results
- `--fail-on-regression`: Exit with error if regression detected
- `--threshold FLOAT`: Regression threshold (default: 0.1 = 10%)

**Examples:**
```bash
# Basic comparison
framework-cli performance compare current_results.json

# Compare with specific baseline
framework-cli performance compare current.json \
    --baseline production \
    --format github \
    --output pr_comment.md

# Trend analysis
framework-cli performance compare current.json \
    --mode trend \
    --fail-on-regression

# Custom threshold
framework-cli performance compare current.json \
    --threshold 0.05 \
    --fail-on-regression
```

## Security Commands

### `framework-cli security`

Security scanning and vulnerability assessment tools.

#### `security scan`

Perform comprehensive security scan of a project.

```bash
framework-cli security scan PROJECT_PATH [OPTIONS]
```

**Arguments:**
- `PROJECT_PATH`: Path to project root directory

**Options:**
- `--build-id ID`: Unique identifier for this scan
- `--package-managers MANAGERS`: Package managers to scan (auto-detect if not specified)
  - Choices: `pip`, `pixi`, `conda`
  - Multiple values allowed: `--package-managers pip pixi`
- `--output FILE`: Output file for scan results (JSON format)
- `--save-baseline`: Save scan results as baseline
- `--compare-baseline`: Compare with existing baseline
- `--baseline-name NAME`: Baseline name (default: `default`)
- `--storage-path PATH`: Security data storage directory (default: `security_data`)

**Examples:**
```bash
# Basic project scan
framework-cli security scan .

# Scan with specific package managers
framework-cli security scan . \
    --package-managers pip pixi \
    --output security_report.json

# Baseline workflow
framework-cli security scan . \
    --save-baseline \
    --baseline-name main-branch

# Compare with baseline
framework-cli security scan . \
    --compare-baseline \
    --baseline-name main-branch

# CI/CD scan with build ID
framework-cli security scan . \
    --build-id ${GITHUB_RUN_ID} \
    --save-baseline \
    --output ci_security_report.json
```

#### `security sbom`

Generate Software Bill of Materials (SBOM).

```bash
framework-cli security sbom PROJECT_PATH [OPTIONS]
```

**Arguments:**
- `PROJECT_PATH`: Path to project root directory

**Options:**
- `--format FORMAT`: SBOM format (default: `cyclonedx`)
  - Choices: `cyclonedx`, `spdx`
- `--output-type TYPE`: Output file type (default: `json`)
  - Choices: `json`, `xml`, `yaml`
- `--output FILE`: Output file for SBOM
- `--include-dev`: Include development dependencies
- `--include-vulns/--no-include-vulns`: Include vulnerability information (default: include)

**Examples:**
```bash
# Basic SBOM generation
framework-cli security sbom .

# CycloneDX JSON format
framework-cli security sbom . \
    --format cyclonedx \
    --output-type json \
    --output sbom.json

# SPDX XML format with dev dependencies
framework-cli security sbom . \
    --format spdx \
    --output-type xml \
    --include-dev \
    --output sbom.xml

# SBOM without vulnerability data
framework-cli security sbom . \
    --no-include-vulns \
    --output clean_sbom.json
```

## Reporting Commands

### `framework-cli reporting`

Report generation and artifact management tools.

#### `reporting generate`

Generate comprehensive reports from framework data.

```bash
framework-cli reporting generate DATA_PATH [OPTIONS]
```

**Arguments:**
- `DATA_PATH`: Path to directory containing framework data

**Options:**
- `--template TEMPLATE`: Report template to use
- `--format FORMAT`: Output format (default: `markdown`)
  - Choices: `markdown`, `html`, `json`
- `--output FILE`: Output file for the report (required)
- `--include-charts`: Include charts and visualizations

**Examples:**
```bash
# Basic report generation
framework-cli reporting generate ./framework_data \
    --output comprehensive_report.md

# HTML report with charts
framework-cli reporting generate ./data \
    --format html \
    --include-charts \
    --output report.html

# Custom template
framework-cli reporting generate ./data \
    --template custom_security_template \
    --format markdown \
    --output security_report.md

# JSON format for API consumption
framework-cli reporting generate ./data \
    --format json \
    --output report_data.json
```

## Maintenance Commands

### `framework-cli maintenance`

Maintenance and health monitoring tools.

#### `maintenance health-check`

Run comprehensive health check.

```bash
framework-cli maintenance health-check [OPTIONS]
```

**Options:**
- `--config-path PATH`: Path to maintenance configuration file
- `--output FILE`: Output file for health report (JSON format)

**Examples:**
```bash
# Basic health check
framework-cli maintenance health-check

# Save health report
framework-cli maintenance health-check \
    --output health_status.json

# Custom configuration
framework-cli maintenance health-check \
    --config-path ./maintenance_config.yaml \
    --output detailed_health.json
```

#### `maintenance schedule`

Schedule a maintenance task.

```bash
framework-cli maintenance schedule TASK_NAME [OPTIONS]
```

**Arguments:**
- `TASK_NAME`: Name of the task to schedule

**Options:**
- `--frequency FREQ`: Task execution frequency (required)
  - Choices: `hourly`, `daily`, `weekly`, `monthly`
- `--config-path PATH`: Path to maintenance configuration file

**Examples:**
```bash
# Schedule daily cleanup
framework-cli maintenance schedule cleanup \
    --frequency daily

# Schedule weekly security scan
framework-cli maintenance schedule security-scan \
    --frequency weekly \
    --config-path ./maintenance.yaml

# Schedule monthly report generation
framework-cli maintenance schedule monthly-report \
    --frequency monthly
```

## Quick Operations

### `framework-cli quick-scan`

Run comprehensive quick scan with all tools.

```bash
framework-cli quick-scan [PROJECT_PATH] [OPTIONS]
```

**Arguments:**
- `PROJECT_PATH`: Path to project directory (default: current directory)

**Options:**
- `--output DIR`: Output directory for all reports (default: `framework_reports`)

**Examples:**
```bash
# Quick scan current directory
framework-cli quick-scan

# Quick scan specific project
framework-cli quick-scan ./my-project

# Custom output directory
framework-cli quick-scan . --output ./reports
```

**What it does:**
1. Runs health check and saves to `health_report.json`
2. Performs security scan and saves to `security_report.json`
3. Creates comprehensive summary report

## Configuration Files

### Performance Configuration

```yaml
# performance_config.yaml
performance:
  storage_path: "./performance_data"
  baseline_threshold: 0.1
  trend_analysis: true
  alert_channels:
    - "github"
    - "email"
  history_limit: 50
  comparison_mode: "trend"
```

### Security Configuration

```yaml
# security_config.yaml
security:
  scan_dev_deps: true
  sbom_format: "cyclonedx"
  compliance_standards:
    - "soc2"
    - "iso27001"
  vulnerability_severity_threshold: "medium"
  baseline_comparison: true
  package_managers:
    - "pip"
    - "pixi"
```

### Maintenance Configuration

```yaml
# maintenance_config.yaml
maintenance:
  health_check_interval: "daily"
  automated_cleanup: true
  resource_monitoring: true
  tasks:
    - name: "cleanup"
      frequency: "daily"
      command: "find ./temp -type f -mtime +7 -delete"
    - name: "security-scan"
      frequency: "weekly"
      command: "framework-cli security scan ."
```

## Environment Variables

The CLI supports configuration via environment variables:

### Performance
- `FRAMEWORK_PERFORMANCE_STORAGE`: Performance data storage path
- `FRAMEWORK_PERFORMANCE_THRESHOLD`: Default regression threshold

### Security
- `FRAMEWORK_SECURITY_STORAGE`: Security data storage path
- `FRAMEWORK_SECURITY_BASELINE`: Default baseline name

### Reporting
- `FRAMEWORK_TEMPLATE_DIR`: Template directory path
- `FRAMEWORK_ARTIFACT_STORAGE`: Artifact storage path

### GitHub Integration
- `GITHUB_TOKEN`: GitHub API token for integrations
- `GITHUB_REPOSITORY`: Default repository (owner/repo format)

### Example Usage
```bash
# Set environment variables
export FRAMEWORK_PERFORMANCE_THRESHOLD=0.05
export GITHUB_TOKEN=ghp_xxxxxxxxxxxx
export GITHUB_REPOSITORY=owner/repo

# Use in commands
framework-cli performance compare current.json --fail-on-regression
framework-cli reporting generate data/ --format github
```

## Output Formats

### Performance Reports

**Markdown Format:**
```markdown
# Performance Comparison Report

## Summary
- **Baseline**: production (2024-01-15)
- **Current**: feature-branch (2024-01-16)
- **Overall Change**: +5.2% (regression)

## Detailed Results
| Metric | Baseline | Current | Change | Status |
|--------|----------|---------|--------|--------|
| Execution Time | 100ms | 105ms | +5% | ⚠️ Regression |
| Memory Usage | 50MB | 48MB | -4% | ✅ Improvement |
```

**JSON Format:**
```json
{
  "comparison_id": "comp_123",
  "timestamp": "2024-01-16T10:30:00Z",
  "baseline": {
    "name": "production",
    "timestamp": "2024-01-15T10:00:00Z"
  },
  "current": {
    "execution_time": 105.0,
    "memory_usage": 48.0
  },
  "changes": {
    "execution_time": 0.05,
    "memory_usage": -0.04
  },
  "regressions": [
    {
      "metric": "execution_time",
      "severity": "warning",
      "threshold_exceeded": true
    }
  ]
}
```

### Security Reports

**Markdown Format:**
```markdown
# Security Scan Report

## Summary
- **Scan Date**: 2024-01-16 10:30:00
- **Total Dependencies**: 45
- **Vulnerabilities Found**: 3
- **Critical**: 0, **High**: 1, **Medium**: 2

## Vulnerability Details
### High Severity
- **CVE-2024-0001**: SQL Injection in package-name v1.2.3
  - Fixed in: v1.2.4
  - CVSS Score: 8.5
```

### Health Check Reports

**JSON Format:**
```json
{
  "timestamp": "2024-01-16T10:30:00Z",
  "status": "healthy",
  "metrics": {
    "system": {
      "cpu_usage": 45.2,
      "memory_usage": 60.1,
      "disk_usage": 35.8
    },
    "ci": {
      "environment": "github-actions",
      "runner": "ubuntu-latest",
      "python_version": "3.11.5"
    },
    "dependencies": {
      "total": 45,
      "outdated": 3,
      "vulnerable": 1
    }
  }
}
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Framework Quality Checks
on: [push, pull_request]

jobs:
  framework-checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
      - name: Install framework
        run: pip install -e ./framework
        
      - name: Quick scan
        run: framework-cli quick-scan . --output reports/
        
      - name: Performance check
        if: github.event_name == 'pull_request'
        run: |
          framework-cli performance compare current_results.json \
            --baseline main \
            --format github \
            --output pr_performance.md \
            --fail-on-regression
            
      - name: Security baseline
        run: |
          framework-cli security scan . \
            --save-baseline \
            --baseline-name ${{ github.ref_name }}
            
      - name: Upload reports
        uses: actions/upload-artifact@v3
        with:
          name: framework-reports
          path: reports/
```

### GitLab CI

```yaml
framework-checks:
  image: python:3.11
  before_script:
    - pip install -e ./framework
  script:
    - framework-cli quick-scan . --output reports/
    - framework-cli security scan . --save-baseline
  artifacts:
    reports:
      junit: reports/*.xml
    paths:
      - reports/
```

### Jenkins Pipeline

```groovy
pipeline {
    agent any
    stages {
        stage('Framework Setup') {
            steps {
                sh 'pip install -e ./framework'
            }
        }
        stage('Quality Checks') {
            parallel {
                stage('Security Scan') {
                    steps {
                        sh 'framework-cli security scan . --output security.json'
                    }
                }
                stage('Performance Check') {
                    steps {
                        sh 'framework-cli performance compare results.json'
                    }
                }
                stage('Health Check') {
                    steps {
                        sh 'framework-cli maintenance health-check --output health.json'
                    }
                }
            }
        }
        stage('Report Generation') {
            steps {
                sh 'framework-cli reporting generate reports/ --output final_report.md'
                archiveArtifacts artifacts: '*.json,*.md'
            }
        }
    }
}
```

## Error Handling

### Common Error Codes

- **1**: General command failure
- **2**: File not found or permission error
- **3**: Configuration error
- **4**: Network/API error
- **5**: Performance regression detected (with `--fail-on-regression`)
- **6**: Critical security vulnerabilities found

### Error Output Format

```bash
# Error with exit code 1
$ framework-cli performance collect nonexistent.json
Error: File not found: nonexistent.json
Error code: 2

# Verbose error output
$ framework-cli --verbose security scan /invalid/path
Error: Invalid project path: /invalid/path
  Cause: Permission denied
  Solution: Check path permissions and try again
Error code: 2
```

### Debugging

```bash
# Enable verbose output for debugging
framework-cli --verbose performance collect results.json

# Check CLI installation
which framework-cli
framework-cli --version

# Validate configuration
framework-cli maintenance health-check --verbose
```

## Best Practices

### 1. Use Configuration Files

Store common options in configuration files:

```bash
# Instead of long command lines
framework-cli performance compare current.json \
    --baseline production \
    --storage-path ./perf_data \
    --threshold 0.05 \
    --fail-on-regression

# Use configuration file
framework-cli performance compare current.json --config perf_config.yaml
```

### 2. Standardize Baseline Names

Use consistent baseline naming conventions:

```bash
# Good: Descriptive names
framework-cli performance collect results.json --store-baseline --baseline-name main-branch
framework-cli performance collect results.json --store-baseline --baseline-name production-v1.2.0

# Avoid: Generic names
framework-cli performance collect results.json --store-baseline --baseline-name baseline1
```

### 3. Integrate with CI/CD Early

Set up framework checks early in development:

```bash
# Pre-commit hook
framework-cli quick-scan . --output .framework-reports/

# CI pipeline
framework-cli security scan . --fail-on-critical
framework-cli performance compare results.json --fail-on-regression
```

### 4. Regular Maintenance

Schedule regular maintenance tasks:

```bash
# Weekly security scans
framework-cli maintenance schedule security-weekly --frequency weekly

# Daily health checks
framework-cli maintenance schedule health-daily --frequency daily
```

### 5. Monitor Trends

Use trend analysis for long-term insights:

```bash
# Enable trend analysis
framework-cli performance compare current.json --mode trend --history-limit 20
```

## Troubleshooting

### CLI Not Found

```bash
# Check installation
pip show framework | grep Location

# Reinstall if necessary
pip install -e ./framework

# Verify PATH
which framework-cli
```

### Permission Errors

```bash
# Check file permissions
ls -la benchmark_results.json

# Create output directories
mkdir -p reports/
chmod 755 reports/
```

### Configuration Issues

```bash
# Validate configuration
framework-cli maintenance health-check --verbose

# Check environment variables
env | grep FRAMEWORK_
```

### Performance Issues

```bash
# Reduce verbosity
framework-cli performance collect results.json  # No --verbose

# Use smaller datasets for testing
framework-cli performance compare small_results.json

# Check disk space
df -h
```

For additional help and support, see:
- [Framework README](../README.md)
- [API Documentation](API.md)
- [GitHub Issues](https://github.com/MementoRC/hb-strategy-sandbox/issues)