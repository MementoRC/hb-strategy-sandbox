# Framework API Documentation

Comprehensive API reference for the Hummingbot Development Framework.

## Overview

The Framework API provides programmatic access to all development and quality assurance tools. This documentation covers the public APIs for each framework module.

## Core Modules

### Performance Module

#### PerformanceCollector

Collects and manages performance metrics from benchmark results.

```python
from framework.performance import PerformanceCollector

class PerformanceCollector:
    def __init__(self, storage_path: str = "performance_data"):
        """Initialize performance collector.

        Args:
            storage_path: Directory for storing performance data
        """

    def collect_metrics(self, results_file: str) -> PerformanceMetrics:
        """Collect performance metrics from benchmark results.

        Args:
            results_file: Path to benchmark results file (JSON format)

        Returns:
            PerformanceMetrics object containing collected data

        Raises:
            FileNotFoundError: If results file doesn't exist
            ValueError: If results file format is invalid
        """

    def store_baseline(self, metrics: PerformanceMetrics, name: str = "default") -> None:
        """Store metrics as baseline for future comparisons.

        Args:
            metrics: Performance metrics to store
            name: Baseline name identifier
        """

    def list_baselines(self) -> List[str]:
        """List all available baseline names.

        Returns:
            List of baseline names
        """
```

#### PerformanceComparator

Compares performance metrics against baselines with advanced analysis.

```python
from framework.performance import PerformanceComparator, ComparisonMode

class PerformanceComparator:
    def __init__(self, storage_path: str = "performance_data"):
        """Initialize performance comparator."""

    def compare_with_baseline(
        self,
        current: PerformanceMetrics,
        baseline_name: str = "default",
        mode: ComparisonMode = ComparisonMode.SINGLE
    ) -> BenchmarkResult:
        """Compare current metrics with stored baseline.

        Args:
            current: Current performance metrics
            baseline_name: Name of baseline to compare against
            mode: Comparison mode (SINGLE or TREND)

        Returns:
            BenchmarkResult with comparison analysis

        Raises:
            ValueError: If baseline doesn't exist or comparison fails
        """

    def detect_regressions(
        self,
        comparison: BenchmarkResult,
        threshold: float = 0.1
    ) -> List[PerformanceAlert]:
        """Detect performance regressions in comparison results.

        Args:
            comparison: Benchmark comparison result
            threshold: Regression threshold (0.1 = 10% regression)

        Returns:
            List of performance alerts for detected regressions
        """
```

#### TrendAnalyzer

Analyzes performance trends over multiple data points.

```python
from framework.performance import TrendAnalyzer, TrendData

class TrendAnalyzer:
    def analyze_trends(
        self,
        metrics_history: List[PerformanceMetrics],
        window_size: int = 10
    ) -> TrendData:
        """Analyze performance trends from historical data.

        Args:
            metrics_history: List of historical performance metrics
            window_size: Number of data points for trend analysis

        Returns:
            TrendData with trend analysis results
        """

    def predict_future_performance(
        self,
        trend_data: TrendData,
        periods_ahead: int = 5
    ) -> List[float]:
        """Predict future performance based on trends.

        Args:
            trend_data: Historical trend analysis
            periods_ahead: Number of future periods to predict

        Returns:
            List of predicted performance values
        """
```

### Security Module

#### SecurityCollector

Scans projects for security vulnerabilities and compliance issues.

```python
from framework.security import SecurityCollector, SecurityMetrics

class SecurityCollector:
    def __init__(self, project_path: str = "."):
        """Initialize security collector.

        Args:
            project_path: Path to project root directory
        """

    def scan_project(
        self,
        package_managers: Optional[List[str]] = None,
        include_dev_deps: bool = True
    ) -> SecurityMetrics:
        """Scan project for security vulnerabilities.

        Args:
            package_managers: List of package managers to scan (auto-detect if None)
            include_dev_deps: Include development dependencies in scan

        Returns:
            SecurityMetrics with vulnerability data

        Raises:
            RuntimeError: If scan tools are not available
        """

    def compare_with_baseline(
        self,
        current: SecurityMetrics,
        baseline_name: str = "default"
    ) -> Dict[str, Any]:
        """Compare current security metrics with baseline.

        Args:
            current: Current security metrics
            baseline_name: Baseline to compare against

        Returns:
            Dictionary with comparison results
        """
```

#### DependencyAnalyzer

Analyzes project dependencies for vulnerabilities and license issues.

```python
from framework.security import DependencyAnalyzer, DependencyInfo

class DependencyAnalyzer:
    def analyze_dependencies(self, project_path: str) -> List[DependencyInfo]:
        """Analyze project dependencies.

        Args:
            project_path: Path to project root

        Returns:
            List of dependency information objects
        """

    def check_vulnerabilities(
        self,
        dependencies: List[DependencyInfo]
    ) -> List[VulnerabilityInfo]:
        """Check dependencies for known vulnerabilities.

        Args:
            dependencies: List of dependencies to check

        Returns:
            List of vulnerability information
        """

    def analyze_licenses(
        self,
        dependencies: List[DependencyInfo]
    ) -> Dict[str, List[str]]:
        """Analyze dependency licenses.

        Args:
            dependencies: List of dependencies to analyze

        Returns:
            Dictionary mapping license types to dependency lists
        """
```

#### SBOMGenerator

Generates Software Bill of Materials in standard formats.

```python
from framework.security import SBOMGenerator

class SBOMGenerator:
    def generate_sbom(
        self,
        project_path: str,
        format: str = "cyclonedx",
        output_type: str = "json",
        include_dev: bool = False,
        include_vulns: bool = True
    ) -> Dict[str, Any]:
        """Generate Software Bill of Materials.

        Args:
            project_path: Path to project root
            format: SBOM format ("cyclonedx" or "spdx")
            output_type: Output format ("json", "xml", or "yaml")
            include_dev: Include development dependencies
            include_vulns: Include vulnerability information

        Returns:
            SBOM data structure

        Raises:
            ValueError: If format or output_type is unsupported
        """

    def save_sbom(
        self,
        sbom_data: Dict[str, Any],
        output_file: str
    ) -> None:
        """Save SBOM data to file.

        Args:
            sbom_data: SBOM data structure
            output_file: Output file path
        """
```

### Reporting Module

#### ReportGenerator

Generates comprehensive reports from framework data.

```python
from framework.reporting import ReportGenerator

class ReportGenerator:
    def __init__(self, template_engine: Optional[TemplateEngine] = None):
        """Initialize report generator.

        Args:
            template_engine: Optional custom template engine
        """

    def generate_report(
        self,
        data: Dict[str, Any],
        template: Optional[str] = None,
        format: str = "markdown",
        include_charts: bool = False
    ) -> str:
        """Generate comprehensive report.

        Args:
            data: Report data dictionary
            template: Template name or path
            format: Output format ("markdown", "html", "json")
            include_charts: Include charts and visualizations

        Returns:
            Generated report content

        Raises:
            ValueError: If format is unsupported
            TemplateError: If template processing fails
        """

    def generate_performance_report(
        self,
        metrics: PerformanceMetrics,
        comparison: Optional[BenchmarkResult] = None
    ) -> str:
        """Generate performance-specific report.

        Args:
            metrics: Performance metrics data
            comparison: Optional baseline comparison

        Returns:
            Performance report in markdown format
        """

    def generate_security_report(
        self,
        security_data: SecurityMetrics,
        include_sbom: bool = True
    ) -> str:
        """Generate security-specific report.

        Args:
            security_data: Security metrics data
            include_sbom: Include SBOM information

        Returns:
            Security report in markdown format
        """
```

#### TemplateEngine

Processes customizable report templates.

```python
from framework.reporting import TemplateEngine

class TemplateEngine:
    def __init__(self, template_dir: str = "templates"):
        """Initialize template engine.

        Args:
            template_dir: Directory containing template files
        """

    def load_template(self, template_name: str) -> str:
        """Load template by name.

        Args:
            template_name: Template file name

        Returns:
            Template content string

        Raises:
            FileNotFoundError: If template doesn't exist
        """

    def render_template(
        self,
        template: str,
        context: Dict[str, Any]
    ) -> str:
        """Render template with context data.

        Args:
            template: Template content
            context: Data context for template variables

        Returns:
            Rendered template content

        Raises:
            TemplateError: If template rendering fails
        """

    def register_filter(self, name: str, filter_func: Callable) -> None:
        """Register custom template filter.

        Args:
            name: Filter name
            filter_func: Filter function
        """
```

#### ArtifactManager

Manages report artifacts and storage.

```python
from framework.reporting import ArtifactManager

class ArtifactManager:
    def __init__(self, storage_path: str = "artifacts"):
        """Initialize artifact manager.

        Args:
            storage_path: Base directory for artifact storage
        """

    def store_artifact(
        self,
        content: str,
        artifact_name: str,
        artifact_type: str = "report",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store artifact with metadata.

        Args:
            content: Artifact content
            artifact_name: Unique artifact identifier
            artifact_type: Type of artifact ("report", "data", "chart")
            metadata: Optional metadata dictionary

        Returns:
            Artifact ID for future reference
        """

    def retrieve_artifact(self, artifact_id: str) -> Tuple[str, Dict[str, Any]]:
        """Retrieve artifact by ID.

        Args:
            artifact_id: Artifact identifier

        Returns:
            Tuple of (content, metadata)

        Raises:
            ValueError: If artifact doesn't exist
        """

    def list_artifacts(
        self,
        artifact_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List all artifacts.

        Args:
            artifact_type: Filter by artifact type

        Returns:
            List of artifact metadata dictionaries
        """
```

#### GitHubReporter

Integrates with GitHub for automated reporting.

```python
from framework.reporting import GitHubReporter

class GitHubReporter:
    def __init__(self, token: Optional[str] = None):
        """Initialize GitHub reporter.

        Args:
            token: GitHub API token (uses environment variable if None)
        """

    def post_comment(
        self,
        report: str,
        repo: str,
        pr_number: int,
        update_existing: bool = True
    ) -> None:
        """Post report as PR comment.

        Args:
            report: Report content
            repo: Repository name (owner/repo)
            pr_number: Pull request number
            update_existing: Update existing framework comment if found

        Raises:
            GitHubError: If API call fails
        """

    def create_issue(
        self,
        title: str,
        body: str,
        repo: str,
        labels: Optional[List[str]] = None
    ) -> int:
        """Create GitHub issue.

        Args:
            title: Issue title
            body: Issue body content
            repo: Repository name (owner/repo)
            labels: Optional issue labels

        Returns:
            Issue number

        Raises:
            GitHubError: If API call fails
        """

    def update_status(
        self,
        repo: str,
        sha: str,
        state: str,
        context: str = "framework/quality-check",
        description: Optional[str] = None
    ) -> None:
        """Update commit status.

        Args:
            repo: Repository name (owner/repo)
            sha: Commit SHA
            state: Status state ("pending", "success", "failure", "error")
            context: Status context
            description: Optional status description
        """
```

### Maintenance Module

#### CIHealthMonitor

Monitors CI/CD pipeline health and system resources.

```python
from framework.maintenance import CIHealthMonitor

class CIHealthMonitor:
    def __init__(self, base_dir: str = "."):
        """Initialize CI health monitor.

        Args:
            base_dir: Base directory for monitoring
        """

    def collect_health_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive health metrics.

        Returns:
            Dictionary with health metrics including:
            - System resources (CPU, memory, disk)
            - CI environment information
            - Dependency status
            - Configuration validation
        """

    def check_ci_environment(self) -> Dict[str, Any]:
        """Check CI/CD environment configuration.

        Returns:
            Dictionary with CI environment status
        """

    def validate_dependencies(self) -> List[Dict[str, Any]]:
        """Validate project dependencies.

        Returns:
            List of dependency validation results
        """

    def monitor_resources(self) -> Dict[str, float]:
        """Monitor system resource usage.

        Returns:
            Dictionary with resource usage metrics
        """
```

#### MaintenanceScheduler

Schedules and manages automated maintenance tasks.

```python
from framework.maintenance import MaintenanceScheduler

class MaintenanceScheduler:
    def __init__(self, config_path: Optional[str] = None):
        """Initialize maintenance scheduler.

        Args:
            config_path: Path to scheduler configuration file
        """

    def schedule_task(
        self,
        task_name: str,
        frequency: str,
        command: str,
        description: Optional[str] = None
    ) -> str:
        """Schedule a maintenance task.

        Args:
            task_name: Unique task identifier
            frequency: Task frequency ("hourly", "daily", "weekly", "monthly")
            command: Command to execute
            description: Optional task description

        Returns:
            Task ID for future reference
        """

    def list_tasks(self) -> List[Dict[str, Any]]:
        """List all scheduled tasks.

        Returns:
            List of task information dictionaries
        """

    def execute_task(self, task_id: str) -> Dict[str, Any]:
        """Execute a scheduled task manually.

        Args:
            task_id: Task identifier

        Returns:
            Execution result dictionary

        Raises:
            ValueError: If task doesn't exist
        """

    def remove_task(self, task_id: str) -> None:
        """Remove a scheduled task.

        Args:
            task_id: Task identifier

        Raises:
            ValueError: If task doesn't exist
        """
```

## Data Models

### PerformanceMetrics

```python
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure."""

    timestamp: str
    test_name: str
    execution_time: float
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None
    custom_metrics: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PerformanceMetrics":
        """Create from dictionary."""
```

### BenchmarkResult

```python
@dataclass
class BenchmarkResult:
    """Benchmark comparison result."""

    current_metrics: PerformanceMetrics
    baseline_metrics: PerformanceMetrics
    performance_change: float
    regressions: List[PerformanceAlert]
    improvements: List[PerformanceAlert]
    comparison_summary: str
```

### SecurityMetrics

```python
@dataclass
class SecurityMetrics:
    """Security scan metrics."""

    scan_timestamp: str
    project_path: str
    vulnerabilities: List[VulnerabilityInfo]
    dependencies: List[DependencyInfo]
    compliance_status: Dict[str, bool]
    scan_duration: float

    @property
    def vulnerability_count_by_severity(self) -> Dict[str, int]:
        """Count vulnerabilities by severity level."""

    @property
    def total_vulnerabilities(self) -> int:
        """Total number of vulnerabilities."""
```

### VulnerabilityInfo

```python
@dataclass
class VulnerabilityInfo:
    """Vulnerability information."""

    id: str
    severity: str
    title: str
    description: str
    affected_package: str
    affected_version: str
    fixed_version: Optional[str]
    cvss_score: Optional[float]
    references: List[str]
```

### DependencyInfo

```python
@dataclass
class DependencyInfo:
    """Dependency information."""

    name: str
    version: str
    license: Optional[str]
    source: str  # pip, conda, etc.
    is_dev_dependency: bool
    vulnerabilities: List[VulnerabilityInfo]

    @property
    def has_vulnerabilities(self) -> bool:
        """Check if dependency has vulnerabilities."""
```

## Error Handling

### Framework Exceptions

```python
class FrameworkError(Exception):
    """Base framework exception."""
    pass

class PerformanceError(FrameworkError):
    """Performance-related errors."""
    pass

class SecurityError(FrameworkError):
    """Security-related errors."""
    pass

class ReportingError(FrameworkError):
    """Reporting-related errors."""
    pass

class MaintenanceError(FrameworkError):
    """Maintenance-related errors."""
    pass

class TemplateError(ReportingError):
    """Template processing errors."""
    pass

class GitHubError(ReportingError):
    """GitHub API errors."""
    pass
```

## Configuration

### Framework Configuration Schema

```python
from typing import TypedDict, Optional, List

class PerformanceConfig(TypedDict, total=False):
    storage_path: str
    baseline_threshold: float
    trend_analysis: bool
    alert_channels: List[str]
    history_limit: int
    comparison_mode: str

class SecurityConfig(TypedDict, total=False):
    scan_dev_deps: bool
    sbom_format: str
    compliance_standards: List[str]
    vulnerability_severity_threshold: str
    baseline_comparison: bool

class ReportingConfig(TypedDict, total=False):
    default_format: str
    include_charts: bool
    template_engine: str
    artifact_storage: str
    template_dir: str

class MaintenanceConfig(TypedDict, total=False):
    health_check_interval: str
    automated_cleanup: bool
    resource_monitoring: bool
    config_path: str

class FrameworkConfig(TypedDict, total=False):
    performance: PerformanceConfig
    security: SecurityConfig
    reporting: ReportingConfig
    maintenance: MaintenanceConfig
```

## Usage Examples

### Complete Workflow Example

```python
from framework import (
    PerformanceCollector,
    SecurityCollector,
    ReportGenerator,
    CIHealthMonitor
)

async def run_quality_checks():
    """Run comprehensive quality checks."""

    # Performance monitoring
    perf_collector = PerformanceCollector()
    perf_metrics = perf_collector.collect_metrics("benchmark_results.json")

    # Security scanning
    security_collector = SecurityCollector()
    security_metrics = security_collector.scan_project(".")

    # Health monitoring
    health_monitor = CIHealthMonitor()
    health_data = health_monitor.collect_health_metrics()

    # Generate comprehensive report
    reporter = ReportGenerator()
    report = reporter.generate_report({
        "performance": perf_metrics,
        "security": security_metrics,
        "health": health_data
    }, format="markdown", include_charts=True)

    return report

# Run the workflow
report = await run_quality_checks()
print(report)
```

### Integration with CI/CD

```python
import sys
from framework import PerformanceComparator, SecurityCollector

def ci_quality_gate():
    """CI/CD quality gate with failure conditions."""

    success = True

    # Performance regression check
    comparator = PerformanceComparator()
    current_metrics = comparator.collect_current_metrics()
    comparison = comparator.compare_with_baseline(current_metrics)

    if comparison.regressions:
        print(f"❌ Performance regressions detected: {len(comparison.regressions)}")
        success = False

    # Security vulnerability check
    security = SecurityCollector()
    sec_metrics = security.scan_project(".")

    critical_vulns = [v for v in sec_metrics.vulnerabilities if v.severity == "critical"]
    if critical_vulns:
        print(f"❌ Critical vulnerabilities found: {len(critical_vulns)}")
        success = False

    if not success:
        sys.exit(1)

    print("✅ Quality gate passed")

if __name__ == "__main__":
    ci_quality_gate()
```

## Version Compatibility

### API Versioning

The Framework API follows semantic versioning:

- **Major version**: Breaking API changes
- **Minor version**: New features, backward compatible
- **Patch version**: Bug fixes, backward compatible

### Compatibility Matrix

| Framework Version | Python Version | Features |
|-------------------|----------------|----------|
| 1.0.x            | 3.10+          | Core functionality |
| 1.1.x            | 3.10+          | Enhanced reporting |
| 1.2.x            | 3.11+          | Advanced analytics |

### Migration Between Versions

```python
# Check current API version
from framework import __version__, __api_version__

print(f"Framework: {__version__}")
print(f"API: {__api_version__}")

# Version-specific feature detection
from framework.utils import has_feature

if has_feature("trend_analysis"):
    from framework.performance import TrendAnalyzer
    analyzer = TrendAnalyzer()
```

For detailed migration guides between API versions, see the [Migration Guide](../MIGRATION_GUIDE.md).
