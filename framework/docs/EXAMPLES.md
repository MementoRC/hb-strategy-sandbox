# Framework Usage Examples

Practical examples and tutorials for using the Hummingbot Development Framework.

## Quick Start Examples

### 1. Complete Quality Check Workflow

```python
#!/usr/bin/env python3
"""Complete framework quality check workflow."""

import asyncio
from pathlib import Path
from framework import (
    PerformanceCollector,
    PerformanceComparator,
    SecurityCollector,
    ReportGenerator,
    CIHealthMonitor
)

async def main():
    """Run comprehensive quality checks."""
    print("🔍 Starting Framework Quality Checks...")

    # 1. Performance Analysis
    print("\n📊 Performance Analysis")
    perf_collector = PerformanceCollector(storage_path="./metrics")

    # Collect current metrics (assuming you have benchmark results)
    if Path("benchmark_results.json").exists():
        current_metrics = perf_collector.collect_metrics("benchmark_results.json")
        print(f"  ✓ Collected {len(current_metrics.custom_metrics or {})} performance metrics")

        # Compare with baseline if available
        comparator = PerformanceComparator(storage_path="./metrics")
        try:
            comparison = comparator.compare_with_baseline(current_metrics)
            print(f"  ✓ Performance change: {comparison.performance_change:.1%}")
            if comparison.regressions:
                print(f"  ⚠️ Found {len(comparison.regressions)} performance regressions")
        except ValueError:
            print("  ℹ️ No baseline available for comparison")
    else:
        print("  ℹ️ No benchmark results found, skipping performance analysis")

    # 2. Security Scanning
    print("\n🔒 Security Analysis")
    security_collector = SecurityCollector(project_path=".")
    security_metrics = security_collector.scan_project()

    print(f"  ✓ Scanned {len(security_metrics.dependencies)} dependencies")
    print(f"  ✓ Found {security_metrics.total_vulnerabilities} vulnerabilities")

    # Breakdown by severity
    severity_counts = security_metrics.vulnerability_count_by_severity
    for severity, count in severity_counts.items():
        if count > 0:
            print(f"    - {severity.title()}: {count}")

    # 3. Health Monitoring
    print("\n🏥 System Health Check")
    health_monitor = CIHealthMonitor(base_dir=".")
    health_data = health_monitor.collect_health_metrics()

    status = health_data.get('status', 'unknown')
    print(f"  ✓ System status: {status}")
    print(f"  ✓ Collected {len(health_data.get('metrics', []))} health metrics")

    # 4. Report Generation
    print("\n📋 Generating Comprehensive Report")
    reporter = ReportGenerator()

    # Combine all data
    report_data = {
        "timestamp": "2024-01-16T10:30:00Z",
        "performance": current_metrics if 'current_metrics' in locals() else None,
        "security": security_metrics,
        "health": health_data,
        "summary": {
            "total_vulnerabilities": security_metrics.total_vulnerabilities,
            "critical_vulns": len([v for v in security_metrics.vulnerabilities if v.severity == "critical"]),
            "system_status": status
        }
    }

    # Generate report in multiple formats
    markdown_report = reporter.generate_report(report_data, format="markdown")

    # Save reports
    Path("reports").mkdir(exist_ok=True)
    with open("reports/quality_report.md", "w") as f:
        f.write(markdown_report)

    print(f"  ✓ Generated comprehensive report: reports/quality_report.md")

    # 5. Summary
    print("\n✅ Quality Check Complete!")
    print(f"  - Vulnerabilities: {security_metrics.total_vulnerabilities}")
    print(f"  - System Status: {status}")
    print(f"  - Reports: reports/quality_report.md")

    return {
        "success": True,
        "vulnerabilities": security_metrics.total_vulnerabilities,
        "system_status": status
    }

if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result["success"] else 1)
```

### 2. CLI Integration Examples

#### Basic CLI Workflow

```bash
#!/bin/bash
# comprehensive_check.sh - Complete quality check using CLI

set -e

echo "🔍 Framework Comprehensive Check Starting..."

# Create reports directory
mkdir -p reports/

# 1. Quick scan for overview
echo "📊 Running quick scan..."
framework-cli quick-scan . --output reports/

# 2. Detailed performance analysis (if benchmark data exists)
if [ -f "benchmark_results.json" ]; then
    echo "📈 Performance analysis..."
    framework-cli performance collect benchmark_results.json \
        --storage-path reports/performance \
        --store-baseline --baseline-name current

    # Compare with previous baseline if exists
    if [ -f "reports/performance/baselines/previous.json" ]; then
        framework-cli performance compare benchmark_results.json \
            --baseline previous \
            --format markdown \
            --output reports/performance_comparison.md
    fi
fi

# 3. Security scan with baseline
echo "🔒 Security scanning..."
framework-cli security scan . \
    --save-baseline \
    --baseline-name $(date +%Y%m%d) \
    --output reports/security_scan.json

# 4. Generate SBOM
echo "📦 Generating SBOM..."
framework-cli security sbom . \
    --format cyclonedx \
    --output-type json \
    --include-dev \
    --output reports/sbom.json

# 5. System health check
echo "🏥 Health monitoring..."
framework-cli maintenance health-check \
    --output reports/health_check.json

# 6. Comprehensive report
echo "📋 Generating final report..."
framework-cli reporting generate reports/ \
    --format markdown \
    --include-charts \
    --output reports/final_report.md

echo "✅ Framework check complete! Reports in ./reports/"
echo "📊 Summary:"
echo "  - Quick scan: reports/health_report.json, reports/security_report.json"
echo "  - Detailed reports: reports/final_report.md"
echo "  - SBOM: reports/sbom.json"
```

#### CI/CD Integration Example

```yaml
# .github/workflows/framework-quality.yml
name: Framework Quality Checks

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  framework-checks:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -e .
        pip install -e ./framework

    - name: Run tests and collect performance data
      run: |
        pytest --benchmark-json=benchmark_results.json

    - name: Framework quality checks
      run: |
        # Quick comprehensive scan
        framework-cli quick-scan . --output reports/

        # Performance baseline comparison for PRs
        if [ "${{ github.event_name }}" = "pull_request" ]; then
          framework-cli performance compare benchmark_results.json \
            --baseline main \
            --format github \
            --output pr_performance.md \
            --fail-on-regression
        fi

        # Security scan with baseline tracking
        framework-cli security scan . \
          --save-baseline \
          --baseline-name ${{ github.ref_name }} \
          --output reports/security_detailed.json

        # Generate comprehensive report
        framework-cli reporting generate reports/ \
          --format markdown \
          --output reports/framework_summary.md

    - name: Upload framework reports
      uses: actions/upload-artifact@v3
      with:
        name: framework-reports
        path: reports/

    - name: Comment PR with performance results
      if: github.event_name == 'pull_request' && hashFiles('pr_performance.md') != ''
      uses: actions/github-script@v6
      with:
        script: |
          const fs = require('fs');
          const report = fs.readFileSync('pr_performance.md', 'utf8');

          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: `## Framework Performance Report\n\n${report}`
          });
```

## Module-Specific Examples

### Performance Monitoring

#### Advanced Performance Analysis

```python
from framework.performance import (
    PerformanceCollector,
    PerformanceComparator,
    TrendAnalyzer,
    ComparisonMode
)
import json
from datetime import datetime, timedelta

# 1. Collect performance data
collector = PerformanceCollector(storage_path="./perf_data")

# Simulate collecting metrics from multiple test runs
test_results = [
    {"test_name": "api_response", "execution_time": 0.125, "memory_mb": 45.2},
    {"test_name": "db_query", "execution_time": 0.089, "memory_mb": 32.1},
    {"test_name": "file_processing", "execution_time": 1.234, "memory_mb": 78.5}
]

# Save as benchmark results
with open("current_benchmark.json", "w") as f:
    json.dump(test_results, f)

# Collect metrics
current_metrics = collector.collect_metrics("current_benchmark.json")
print(f"Collected metrics for {current_metrics.test_name}")

# 2. Store as baseline for future comparisons
collector.store_baseline(current_metrics, name="v1.0.0")
print("Stored baseline: v1.0.0")

# 3. Simulate performance comparison after optimization
optimized_results = [
    {"test_name": "api_response", "execution_time": 0.098, "memory_mb": 42.1},  # 22% faster
    {"test_name": "db_query", "execution_time": 0.095, "memory_mb": 30.8},     # 6% slower
    {"test_name": "file_processing", "execution_time": 1.156, "memory_mb": 75.2}  # 6% faster
]

with open("optimized_benchmark.json", "w") as f:
    json.dump(optimized_results, f)

optimized_metrics = collector.collect_metrics("optimized_benchmark.json")

# 4. Compare performance
comparator = PerformanceComparator(storage_path="./perf_data")
comparison = comparator.compare_with_baseline(optimized_metrics, baseline_name="v1.0.0")

print(f"\nPerformance Comparison:")
print(f"Overall change: {comparison.performance_change:.1%}")
print(f"Regressions: {len(comparison.regressions)}")
print(f"Improvements: {len(comparison.improvements)}")

# 5. Detect specific regressions
regressions = comparator.detect_regressions(comparison, threshold=0.05)  # 5% threshold
for regression in regressions:
    print(f"Regression detected: {regression}")

# 6. Trend analysis (simulate historical data)
trend_analyzer = TrendAnalyzer()

# Create sample historical metrics
historical_metrics = []
base_time = 0.125
for i in range(10):
    # Simulate gradual performance degradation
    execution_time = base_time + (i * 0.002)  # 2ms increase per iteration
    historical_metrics.append(PerformanceMetrics(
        timestamp=(datetime.now() - timedelta(days=10-i)).isoformat(),
        test_name="api_response",
        execution_time=execution_time,
        memory_usage=45.0 + (i * 0.5)
    ))

# Analyze trends
trend_data = trend_analyzer.analyze_trends(historical_metrics)
print(f"\nTrend Analysis:")
print(f"Trend direction: {trend_data.direction}")
print(f"Slope: {trend_data.slope:.4f}")

# Predict future performance
future_predictions = trend_analyzer.predict_future_performance(trend_data, periods_ahead=3)
print(f"Predicted performance (next 3 periods): {future_predictions}")
```

### Security Analysis

#### Comprehensive Security Workflow

```python
from framework.security import (
    SecurityCollector,
    DependencyAnalyzer,
    SBOMGenerator
)
import json

# 1. Project security scan
print("🔒 Starting comprehensive security analysis...")

security_collector = SecurityCollector(project_path=".")
security_metrics = security_collector.scan_project(
    package_managers=["pip", "pixi"],
    include_dev_deps=True
)

print(f"Security scan completed:")
print(f"  - Dependencies scanned: {len(security_metrics.dependencies)}")
print(f"  - Vulnerabilities found: {security_metrics.total_vulnerabilities}")

# 2. Detailed vulnerability analysis
critical_vulns = [v for v in security_metrics.vulnerabilities if v.severity == "critical"]
high_vulns = [v for v in security_metrics.vulnerabilities if v.severity == "high"]

if critical_vulns:
    print(f"\n🚨 CRITICAL VULNERABILITIES ({len(critical_vulns)}):")
    for vuln in critical_vulns:
        print(f"  - {vuln.id}: {vuln.title}")
        print(f"    Package: {vuln.affected_package} {vuln.affected_version}")
        if vuln.fixed_version:
            print(f"    Fix: Upgrade to {vuln.fixed_version}")
        print(f"    CVSS: {vuln.cvss_score}")

if high_vulns:
    print(f"\n⚠️ HIGH SEVERITY VULNERABILITIES ({len(high_vulns)}):")
    for vuln in high_vulns[:3]:  # Show first 3
        print(f"  - {vuln.id}: {vuln.title}")
        print(f"    Package: {vuln.affected_package}")

# 3. Dependency analysis
analyzer = DependencyAnalyzer()
dependencies = analyzer.analyze_dependencies(".")

print(f"\n📦 Dependency Analysis:")
print(f"  - Total dependencies: {len(dependencies)}")

# License analysis
licenses = analyzer.analyze_licenses(dependencies)
print(f"  - License types found: {len(licenses)}")
for license_type, deps in licenses.items():
    if license_type and len(deps) > 0:
        print(f"    - {license_type}: {len(deps)} packages")

# Dependencies with vulnerabilities
vulnerable_deps = [dep for dep in dependencies if dep.has_vulnerabilities]
print(f"  - Vulnerable dependencies: {len(vulnerable_deps)}")

# 4. SBOM Generation
print(f"\n📋 Generating Software Bill of Materials...")

sbom_generator = SBOMGenerator()

# Generate CycloneDX SBOM
sbom_data = sbom_generator.generate_sbom(
    project_path=".",
    format="cyclonedx",
    output_type="json",
    include_dev=True,
    include_vulns=True
)

# Save SBOM
with open("sbom.json", "w") as f:
    json.dump(sbom_data, f, indent=2)

print(f"  ✓ SBOM generated: sbom.json")
print(f"  - Components: {len(sbom_data.get('components', []))}")
print(f"  - Vulnerabilities: {len(sbom_data.get('vulnerabilities', []))}")

# 5. Security baseline comparison
print(f"\n📊 Baseline Comparison:")

# Save current scan as baseline
security_collector.store_baseline(security_metrics, name="current")
print("  ✓ Stored current scan as baseline")

# Compare with previous baseline (if exists)
try:
    comparison = security_collector.compare_with_baseline(security_metrics, "previous")
    print(f"  - New vulnerabilities: {comparison.get('new_vulnerabilities', 0)}")
    print(f"  - Resolved vulnerabilities: {comparison.get('resolved_vulnerabilities', 0)}")
    print(f"  - Dependency changes: {comparison.get('dependency_changes', 0)}")
except ValueError:
    print("  - No previous baseline found")

# 6. Generate security report
print(f"\n📝 Generating Security Report...")

security_report = f"""
# Security Analysis Report

**Scan Date**: {security_metrics.scan_timestamp}
**Project**: {security_metrics.project_path}

## Summary
- **Total Dependencies**: {len(security_metrics.dependencies)}
- **Vulnerabilities Found**: {security_metrics.total_vulnerabilities}
- **Critical**: {len(critical_vulns)}
- **High**: {len(high_vulns)}

## Vulnerability Breakdown
{chr(10).join(f'- **{severity.title()}**: {count}' for severity, count in security_metrics.vulnerability_count_by_severity.items() if count > 0)}

## Critical Actions Required
{chr(10).join(f'- **{vuln.id}**: Upgrade {vuln.affected_package} to {vuln.fixed_version or "latest"}' for vuln in critical_vulns[:5])}

## SBOM Generated
- Format: CycloneDX JSON
- Components: {len(sbom_data.get('components', []))}
- File: sbom.json
"""

with open("security_report.md", "w") as f:
    f.write(security_report)

print("  ✓ Security report saved: security_report.md")
print(f"\n✅ Security analysis complete!")
```

### Report Generation

#### Custom Report Templates

```python
from framework.reporting import (
    ReportGenerator,
    TemplateEngine,
    ArtifactManager
)
import os

# 1. Setup custom template engine
template_engine = TemplateEngine(template_dir="./custom_templates")

# Create a custom template
custom_template = """
# {{ title }}

Generated on: {{ timestamp }}

## Project Summary
- **Name**: {{ project.name }}
- **Version**: {{ project.version }}
- **Status**: {{ project.status }}

## Performance Metrics
{% if performance %}
- **Execution Time**: {{ performance.execution_time }}ms
- **Memory Usage**: {{ performance.memory_usage }}MB
- **Performance Change**: {{ performance.change }}%
{% else %}
*No performance data available*
{% endif %}

## Security Analysis
{% if security %}
- **Total Vulnerabilities**: {{ security.total_vulnerabilities }}
- **Critical Issues**: {{ security.critical_count }}
- **Dependencies Scanned**: {{ security.dependency_count }}

### Top Vulnerabilities
{% for vuln in security.top_vulnerabilities %}
- **{{ vuln.id }}**: {{ vuln.title }} ({{ vuln.severity }})
{% endfor %}
{% else %}
*No security data available*
{% endif %}

## System Health
{% if health %}
- **Status**: {{ health.status }}
- **CPU Usage**: {{ health.cpu_usage }}%
- **Memory Usage**: {{ health.memory_usage }}%
- **Disk Usage**: {{ health.disk_usage }}%
{% endif %}

## Recommendations
{% for rec in recommendations %}
- {{ rec }}
{% endfor %}

---
*Report generated by Hummingbot Development Framework*
"""

# Save template
os.makedirs("custom_templates", exist_ok=True)
with open("custom_templates/project_summary.md", "w") as f:
    f.write(custom_template)

# 2. Prepare report data
report_data = {
    "title": "Hummingbot Strategy Sandbox - Quality Report",
    "timestamp": "2024-01-16 10:30:00 UTC",
    "project": {
        "name": "hb-strategy-sandbox",
        "version": "0.2.0",
        "status": "healthy"
    },
    "performance": {
        "execution_time": 125.5,
        "memory_usage": 45.2,
        "change": -5.2  # 5.2% improvement
    },
    "security": {
        "total_vulnerabilities": 3,
        "critical_count": 0,
        "dependency_count": 45,
        "top_vulnerabilities": [
            {"id": "CVE-2024-0001", "title": "SQL Injection", "severity": "high"},
            {"id": "CVE-2024-0002", "title": "XSS Vulnerability", "severity": "medium"}
        ]
    },
    "health": {
        "status": "healthy",
        "cpu_usage": 45.2,
        "memory_usage": 60.1,
        "disk_usage": 35.8
    },
    "recommendations": [
        "Upgrade vulnerable dependencies to latest versions",
        "Consider implementing automated security scanning in CI/CD",
        "Monitor performance trends for potential regressions",
        "Schedule regular dependency updates"
    ]
}

# 3. Generate report with custom template
report_generator = ReportGenerator(template_engine=template_engine)

custom_report = report_generator.generate_report(
    data=report_data,
    template="project_summary.md",
    format="markdown"
)

print("Custom Report Generated:")
print("=" * 50)
print(custom_report)
print("=" * 50)

# 4. Artifact management
artifact_manager = ArtifactManager(storage_path="./report_artifacts")

# Store report as artifact
artifact_id = artifact_manager.store_artifact(
    content=custom_report,
    artifact_name="quality_report_v1",
    artifact_type="report",
    metadata={
        "template": "project_summary.md",
        "generation_time": "2024-01-16T10:30:00Z",
        "data_sources": ["performance", "security", "health"],
        "format": "markdown"
    }
)

print(f"Report stored as artifact: {artifact_id}")

# 5. List all artifacts
artifacts = artifact_manager.list_artifacts(artifact_type="report")
print(f"\nAvailable report artifacts:")
for artifact in artifacts:
    print(f"  - {artifact['name']}: {artifact['timestamp']}")

# 6. Generate multiple formats
print(f"\nGenerating multiple report formats...")

# HTML format
html_report = report_generator.generate_report(
    data=report_data,
    template="project_summary.md",
    format="html"
)

with open("quality_report.html", "w") as f:
    f.write(html_report)

# JSON format for API consumption
json_report = report_generator.generate_report(
    data=report_data,
    format="json"
)

with open("quality_report.json", "w") as f:
    f.write(json_report)

print("  ✓ Markdown: quality_report.md")
print("  ✓ HTML: quality_report.html")
print("  ✓ JSON: quality_report.json")
```

## Integration Patterns

### Pre-commit Hook Integration

```python
#!/usr/bin/env python3
"""Pre-commit hook using framework tools."""

import subprocess
import sys
import json
from pathlib import Path

def run_framework_checks():
    """Run framework quality checks for pre-commit."""
    print("🔍 Running Framework pre-commit checks...")

    success = True

    # 1. Quick health check
    try:
        result = subprocess.run([
            "framework-cli", "maintenance", "health-check",
            "--output", "pre-commit-health.json"
        ], capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            print("  ✓ Health check passed")
        else:
            print(f"  ❌ Health check failed: {result.stderr}")
            success = False

    except subprocess.TimeoutExpired:
        print("  ❌ Health check timed out")
        success = False

    # 2. Security scan for new vulnerabilities
    try:
        result = subprocess.run([
            "framework-cli", "security", "scan", ".",
            "--output", "pre-commit-security.json"
        ], capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            # Check for critical vulnerabilities
            with open("pre-commit-security.json", "r") as f:
                security_data = json.load(f)

            critical_vulns = [
                v for v in security_data.get("vulnerabilities", [])
                if v.get("severity") == "critical"
            ]

            if critical_vulns:
                print(f"  ❌ Critical vulnerabilities found: {len(critical_vulns)}")
                for vuln in critical_vulns[:3]:
                    print(f"    - {vuln['id']}: {vuln['title']}")
                success = False
            else:
                print("  ✓ No critical vulnerabilities found")
        else:
            print(f"  ❌ Security scan failed: {result.stderr}")
            success = False

    except subprocess.TimeoutExpired:
        print("  ❌ Security scan timed out")
        success = False
    except json.JSONDecodeError:
        print("  ❌ Security scan output format error")
        success = False

    # 3. Cleanup temporary files
    for temp_file in ["pre-commit-health.json", "pre-commit-security.json"]:
        Path(temp_file).unlink(missing_ok=True)

    if success:
        print("✅ All framework checks passed")
        return 0
    else:
        print("❌ Framework checks failed - commit blocked")
        return 1

if __name__ == "__main__":
    sys.exit(run_framework_checks())
```

### Makefile Integration

```makefile
# Makefile with framework integration

.PHONY: framework-check framework-scan framework-report framework-clean

# Framework quick check
framework-check:
	@echo "🔍 Running framework quick check..."
	framework-cli quick-scan . --output reports/
	@echo "✅ Framework check complete - see reports/"

# Comprehensive framework scan
framework-scan:
	@echo "🔍 Running comprehensive framework scan..."
	mkdir -p reports/detailed/

	# Performance analysis
	@if [ -f "benchmark_results.json" ]; then \
		framework-cli performance collect benchmark_results.json \
			--storage-path reports/detailed/performance \
			--store-baseline --baseline-name $(shell date +%Y%m%d); \
	fi

	# Security scan with SBOM
	framework-cli security scan . \
		--save-baseline --baseline-name $(shell date +%Y%m%d) \
		--output reports/detailed/security_scan.json
	framework-cli security sbom . \
		--format cyclonedx --output-type json \
		--output reports/detailed/sbom.json

	# Health monitoring
	framework-cli maintenance health-check \
		--output reports/detailed/health_check.json

	# Comprehensive report
	framework-cli reporting generate reports/detailed/ \
		--format markdown --include-charts \
		--output reports/framework_report.md

	@echo "✅ Comprehensive scan complete - see reports/"

# Generate framework reports
framework-report:
	@echo "📊 Generating framework reports..."
	mkdir -p reports/

	# Generate different format reports
	framework-cli reporting generate reports/ \
		--format markdown --output reports/summary.md
	framework-cli reporting generate reports/ \
		--format html --output reports/dashboard.html
	framework-cli reporting generate reports/ \
		--format json --output reports/data.json

	@echo "✅ Reports generated in multiple formats"

# Clean framework artifacts
framework-clean:
	@echo "🧹 Cleaning framework artifacts..."
	rm -rf reports/
	rm -rf performance_data/
	rm -rf security_data/
	rm -rf artifacts/
	rm -f *.json *.md *.html
	@echo "✅ Framework artifacts cleaned"

# CI target
ci-framework: framework-scan
	@echo "🚀 Framework CI checks complete"

	# Check for critical issues
	@if grep -q "critical" reports/detailed/security_scan.json; then \
		echo "❌ Critical security issues found"; \
		exit 1; \
	fi

	@echo "✅ All CI framework checks passed"

# Development target
dev-setup: framework-check
	@echo "🔧 Development environment check complete"
```

### Docker Integration

```dockerfile
# Dockerfile with framework integration
FROM python:3.11-slim

WORKDIR /app

# Install framework dependencies
COPY requirements.txt framework/requirements.txt ./
RUN pip install -r requirements.txt -r framework/requirements.txt

# Copy application and framework
COPY . .
RUN pip install -e . -e ./framework

# Framework health check as part of container startup
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD framework-cli maintenance health-check || exit 1

# Default command runs framework checks
CMD ["framework-cli", "quick-scan", ".", "--output", "/app/reports/"]
```

```yaml
# docker-compose.yml with framework services
version: '3.8'

services:
  app:
    build: .
    volumes:
      - ./reports:/app/reports
    environment:
      - FRAMEWORK_PERFORMANCE_STORAGE=/app/reports/performance
      - FRAMEWORK_SECURITY_STORAGE=/app/reports/security

  framework-monitor:
    build: .
    command: |
      sh -c "
        while true; do
          framework-cli maintenance health-check --output /app/reports/health.json
          framework-cli security scan /app --output /app/reports/security.json
          sleep 3600  # Run every hour
        done
      "
    volumes:
      - ./reports:/app/reports
      - .:/app:ro
    depends_on:
      - app

  framework-reports:
    build: .
    command: |
      sh -c "
        # Wait for some data to be collected
        sleep 60
        framework-cli reporting generate /app/reports \
          --format html --include-charts \
          --output /app/reports/dashboard.html
      "
    volumes:
      - ./reports:/app/reports
    depends_on:
      - framework-monitor
    ports:
      - "8080:8080"
```

These examples demonstrate the comprehensive capabilities of the Framework and show how to integrate it into various development workflows. The Framework provides both programmatic APIs and CLI tools that can be adapted to different use cases and environments.
