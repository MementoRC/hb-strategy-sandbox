# Hummingbot Development Framework

A comprehensive development and quality assurance framework providing shared tools for Hummingbot ecosystem projects.

## Overview

The Hummingbot Development Framework is a modular collection of tools designed to enhance the development experience across the Hummingbot ecosystem. It provides standardized solutions for performance monitoring, security scanning, report generation, and system maintenance.

## Features

### 🚀 Performance Monitoring
- **Metrics Collection**: Comprehensive performance data collection and storage
- **Benchmark Comparison**: Advanced baseline comparison with trend analysis
- **Alert System**: Configurable performance regression detection
- **Historical Analysis**: Long-term performance trend monitoring

### 🔒 Security Assessment
- **Dependency Scanning**: Automated vulnerability detection in project dependencies
- **SBOM Generation**: Software Bill of Materials in CycloneDX and SPDX formats
- **Compliance Reporting**: Security compliance and audit trail generation
- **Baseline Tracking**: Security posture monitoring over time

### 📊 Report Generation
- **Multi-format Output**: Markdown, HTML, and JSON report generation
- **Template Engine**: Customizable report templates with dynamic content
- **Artifact Management**: Centralized artifact storage and organization
- **GitHub Integration**: Direct integration with GitHub for automated reporting

### 🛠️ Maintenance Tools
- **Health Monitoring**: Comprehensive system health checks and diagnostics
- **Scheduled Maintenance**: Automated maintenance task scheduling
- **CI/CD Integration**: Seamless integration with continuous integration pipelines
- **Resource Management**: System resource monitoring and optimization

## Installation

### As Part of Hummingbot Strategy Sandbox

The framework is included automatically when you install the hb-strategy-sandbox package:

```bash
pip install hb-strategy-sandbox
```

### Standalone Installation

You can also use the framework independently:

```bash
# From the project root
pip install -e ./framework
```

## Quick Start

### Command Line Interface

The framework provides a unified CLI for all tools:

```bash
# Quick scan of current project
framework-cli quick-scan .

# Performance monitoring
framework-cli performance collect benchmark_results.json
framework-cli performance compare current_results.json --baseline production

# Security scanning
framework-cli security scan . --save-baseline
framework-cli security sbom . --format cyclonedx --output sbom.json

# Health monitoring
framework-cli maintenance health-check --output health_report.json

# Report generation
framework-cli reporting generate data/ --format markdown --output report.md
```

### Programmatic Usage

```python
from framework import (
    PerformanceCollector,
    SecurityCollector, 
    ReportGenerator,
    CIHealthMonitor
)

# Performance monitoring
collector = PerformanceCollector()
metrics = collector.collect_metrics("benchmark_results.json")

# Security scanning
security = SecurityCollector() 
scan_results = security.scan_project(".")

# Report generation
reporter = ReportGenerator()
report = reporter.generate_report(metrics, format="markdown")

# Health monitoring
monitor = CIHealthMonitor()
health_status = monitor.collect_health_metrics()
```

## Architecture

### Module Structure

```
framework/
├── performance/          # Performance monitoring tools
│   ├── collector.py      # Metrics collection
│   ├── comparator.py     # Baseline comparison
│   ├── trend_analyzer.py # Trend analysis
│   └── cli.py           # CLI commands
├── security/            # Security assessment tools
│   ├── analyzer.py      # Dependency analysis
│   ├── collector.py     # Security data collection
│   ├── sbom_generator.py # SBOM generation
│   └── cli.py          # CLI commands
├── reporting/          # Report generation tools
│   ├── report_generator.py # Core reporting
│   ├── template_engine.py  # Template processing
│   ├── artifact_manager.py # Artifact management
│   └── github_reporter.py  # GitHub integration
├── maintenance/        # Maintenance and monitoring
│   ├── health_monitor.py   # Health monitoring
│   ├── scheduler.py        # Task scheduling
│   └── cli.py             # CLI commands
└── cli.py             # Unified CLI entry point
```

### Key Components

#### Performance Module
- **PerformanceCollector**: Collects and processes benchmark data
- **PerformanceComparator**: Compares metrics against baselines
- **TrendAnalyzer**: Analyzes performance trends over time
- **AlertSeverity**: Configurable alerting for performance regressions

#### Security Module
- **SecurityCollector**: Scans projects for security vulnerabilities
- **DependencyAnalyzer**: Analyzes dependency security status
- **SBOMGenerator**: Generates Software Bills of Materials
- **VulnerabilityInfo**: Structures vulnerability data

#### Reporting Module
- **ReportGenerator**: Creates comprehensive reports from framework data
- **TemplateEngine**: Processes customizable report templates
- **ArtifactManager**: Manages report artifacts and storage
- **GitHubReporter**: Integrates with GitHub for automated reporting

#### Maintenance Module
- **CIHealthMonitor**: Monitors CI/CD pipeline health
- **MaintenanceScheduler**: Schedules automated maintenance tasks

## CLI Reference

### Performance Commands

```bash
# Collect performance metrics
framework-cli performance collect results.json [options]

# Compare with baseline
framework-cli performance compare current.json --baseline production [options]
```

**Options:**
- `--storage-path`: Directory for performance data storage
- `--store-baseline`: Save metrics as new baseline
- `--baseline-name`: Name for baseline storage
- `--output`: Output file for results
- `--fail-on-regression`: Exit with error on performance regression

### Security Commands

```bash
# Security scan
framework-cli security scan PROJECT_PATH [options]

# Generate SBOM
framework-cli security sbom PROJECT_PATH [options]
```

**Options:**
- `--package-managers`: Specify package managers to scan
- `--save-baseline`: Save results as security baseline
- `--format`: SBOM format (cyclonedx, spdx)
- `--output-type`: Output file type (json, xml, yaml)
- `--include-dev`: Include development dependencies

### Reporting Commands

```bash
# Generate reports
framework-cli reporting generate DATA_PATH [options]
```

**Options:**
- `--template`: Custom report template
- `--format`: Output format (markdown, html, json)
- `--include-charts`: Include visualizations
- `--output`: Output file path

### Maintenance Commands

```bash
# Health check
framework-cli maintenance health-check [options]

# Schedule maintenance
framework-cli maintenance schedule TASK_NAME --frequency FREQ [options]
```

**Options:**
- `--config-path`: Path to maintenance configuration
- `--frequency`: Task frequency (hourly, daily, weekly, monthly)
- `--output`: Output file for health reports

## Integration Examples

### GitHub Actions Integration

```yaml
name: Framework Quality Checks
on: [push, pull_request]

jobs:
  quality-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
      - name: Install framework
        run: pip install -e ./framework
        
      - name: Run framework checks
        run: |
          framework-cli quick-scan . --output reports/
          framework-cli security scan . --save-baseline
          framework-cli maintenance health-check --output health.json
          
      - name: Upload reports
        uses: actions/upload-artifact@v3
        with:
          name: framework-reports
          path: reports/
```

### Pre-commit Integration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: framework-security-scan
        name: Framework Security Scan
        entry: framework-cli security scan .
        language: system
        pass_filenames: false
        
      - id: framework-health-check  
        name: Framework Health Check
        entry: framework-cli maintenance health-check
        language: system
        pass_filenames: false
```

### CI/CD Pipeline Integration

```bash
#!/bin/bash
# ci-quality-check.sh

set -e

echo "🔍 Running Framework Quality Checks..."

# Performance baseline comparison
if [ -f "performance_baseline.json" ]; then
    framework-cli performance compare current_results.json \
        --baseline production \
        --fail-on-regression
fi

# Security scanning
framework-cli security scan . \
    --save-baseline \
    --compare-baseline \
    --output security_report.json

# Health monitoring
framework-cli maintenance health-check \
    --output health_status.json

# Generate comprehensive report
framework-cli reporting generate . \
    --format markdown \
    --output quality_report.md \
    --include-charts

echo "✅ Framework Quality Checks Complete"
```

## Migration from Legacy Structure

### Import Path Changes

**Old import patterns (deprecated):**
```python
# Legacy imports - still work but deprecated
from strategy_sandbox.performance import PerformanceCollector
from strategy_sandbox.security import SecurityCollector
```

**New import patterns:**
```python
# New framework imports - recommended
from framework import PerformanceCollector, SecurityCollector
from framework.performance import PerformanceCollector
from framework.security import SecurityCollector
```

### CLI Migration

**Old CLI patterns:**
```bash
# Legacy CLI access (if it existed)
python -m strategy_sandbox.performance.cli
```

**New CLI patterns:**
```bash
# Unified framework CLI
framework-cli performance collect results.json
framework-cli security scan .
framework-cli quick-scan .
```

### Configuration Migration

The framework maintains backward compatibility with existing configurations while providing enhanced options:

```python
# Existing configurations continue to work
config = {
    "performance": {"baseline_threshold": 0.1},
    "security": {"scan_dev_deps": True}
}

# Enhanced framework configuration options
framework_config = {
    "performance": {
        "baseline_threshold": 0.1,
        "trend_analysis": True,
        "alert_channels": ["github", "email"]
    },
    "security": {
        "scan_dev_deps": True,
        "sbom_format": "cyclonedx",
        "compliance_standards": ["soc2", "iso27001"]
    }
}
```

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/MementoRC/hb-strategy-sandbox.git
cd hb-strategy-sandbox

# Install development dependencies
pixi install

# Install framework in development mode
pip install -e ./framework

# Run tests
pixi run test-framework
```

### Running Tests

```bash
# Unit tests
pixi run test-unit framework/

# Integration tests  
pixi run test-integration framework/

# Performance tests
pixi run test-performance framework/

# Property-based tests
pixi run test-property framework/
```

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes in the `framework/` directory
4. Add tests for new functionality
5. Run the full test suite: `pixi run test`
6. Submit a pull request

### Adding New Tools

To add a new tool module to the framework:

1. Create the module directory: `framework/newtool/`
2. Implement the core functionality
3. Add CLI integration in `framework/newtool/cli.py`
4. Update `framework/cli.py` to include new commands
5. Add exports to `framework/__init__.py`
6. Write comprehensive tests
7. Update documentation

## Troubleshooting

### Common Issues

**Import Errors:**
```bash
# Ensure framework is properly installed
pip install -e ./framework

# Check import paths
python -c "from framework import PerformanceCollector; print('OK')"
```

**CLI Not Found:**
```bash
# Verify CLI installation
which framework-cli

# Check entry points
pip show -f hb-strategy-sandbox | grep framework-cli
```

**Permission Issues:**
```bash
# Ensure proper permissions for reports directory
mkdir -p reports/
chmod 755 reports/
```

### Debug Mode

Enable verbose output for debugging:

```bash
framework-cli --verbose quick-scan .
framework-cli -v performance collect results.json
```

### Configuration Issues

Check configuration file formats:

```bash
# Validate configuration
framework-cli maintenance health-check --config-path config.yaml
```

## API Documentation

For detailed API documentation, see:
- [Performance Module API](performance/README.md)
- [Security Module API](security/README.md) 
- [Reporting Module API](reporting/README.md)
- [Maintenance Module API](maintenance/README.md)

## License

Apache 2.0 License - see [LICENSE](../LICENSE) file for details.

## Links

- [Main Project Documentation](../README.md)
- [Migration Guide](../MIGRATION_GUIDE.md)
- [Contributing Guidelines](../CONTRIBUTING.md)
- [GitHub Repository](https://github.com/MementoRC/hb-strategy-sandbox)