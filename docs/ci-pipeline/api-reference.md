# API Reference

This document provides comprehensive API reference documentation for the HB Strategy Sandbox CI pipeline components.

## Overview

The CI pipeline exposes several APIs and interfaces for integration and extension. This reference covers the main components and their programmatic interfaces.

## Core Modules

### Performance Module

#### `strategy_sandbox.performance.collector`

##### `PerformanceCollector`

Main class for collecting performance metrics from various sources.

```python
class PerformanceCollector:
    """Collects performance metrics from benchmark results and system information."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the collector with optional configuration."""
        
    def collect_system_info(self) -> Dict[str, Any]:
        """Collect system and environment information.
        
        Returns:
            Dictionary containing system metrics including:
            - CPU information and usage
            - Memory statistics
            - Disk usage and I/O metrics
            - Network interface information
            - Python environment details
        """
        
    def process_benchmark_results(self, benchmark_file: Path) -> BenchmarkData:
        """Process pytest-benchmark JSON output.
        
        Args:
            benchmark_file: Path to pytest-benchmark JSON results file
            
        Returns:
            Structured benchmark data with processed metrics
        """
        
    def store_baseline(self, metrics: PerformanceMetrics, tag: str = "main"):
        """Store performance baseline for future comparisons.
        
        Args:
            metrics: Performance metrics to store as baseline
            tag: Baseline identifier (default: "main")
        """
        
    def load_baseline(self, tag: str = "main") -> Optional[PerformanceMetrics]:
        """Load stored performance baseline.
        
        Args:
            tag: Baseline identifier to load
            
        Returns:
            Performance metrics if baseline exists, None otherwise
        """
```

##### `PerformanceMetrics`

Data class for performance metrics.

```python
@dataclass
class PerformanceMetrics:
    """Container for performance metrics and metadata."""
    
    timestamp: datetime
    environment: SystemInfo
    benchmarks: List[BenchmarkResult]
    system_metrics: SystemMetrics
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary format."""
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PerformanceMetrics':
        """Create metrics from dictionary data."""
```

#### `strategy_sandbox.performance.comparator`

##### `PerformanceComparator`

Analyzes performance changes and detects regressions.

```python
class PerformanceComparator:
    """Compares performance metrics and detects regressions."""
    
    def __init__(self, config: ThresholdConfig):
        """Initialize with threshold configuration."""
        
    def compare_benchmarks(
        self, 
        current: PerformanceMetrics, 
        baseline: PerformanceMetrics
    ) -> ComparisonReport:
        """Compare current metrics against baseline.
        
        Args:
            current: Current performance metrics
            baseline: Baseline metrics for comparison
            
        Returns:
            Detailed comparison report with regression analysis
        """
        
    def detect_regressions(
        self, 
        comparison: ComparisonReport,
        thresholds: Optional[ThresholdConfig] = None
    ) -> List[PerformanceAlert]:
        """Detect performance regressions based on thresholds.
        
        Args:
            comparison: Comparison report to analyze
            thresholds: Optional custom thresholds
            
        Returns:
            List of performance alerts for detected regressions
        """
```

### Security Module

#### `strategy_sandbox.security.analyzer`

##### `DependencyAnalyzer`

Scans project dependencies for security vulnerabilities.

```python
class DependencyAnalyzer:
    """Analyzes project dependencies for security vulnerabilities."""
    
    def __init__(self, project_path: Path):
        """Initialize analyzer for project at given path."""
        
    def scan_dependencies(self) -> SecurityScanResult:
        """Scan all project dependencies for vulnerabilities.
        
        Returns:
            Complete security scan results with vulnerability data
        """
        
    def detect_package_managers(self) -> List[PackageManager]:
        """Detect active package managers in project.
        
        Returns:
            List of detected package managers (pip, pixi, conda, etc.)
        """
        
    def generate_dependency_tree(self) -> DependencyTree:
        """Generate complete dependency tree.
        
        Returns:
            Hierarchical dependency tree with relationships
        """
```

#### `strategy_sandbox.security.sbom_generator`

##### `SBOMGenerator`

Generates Software Bill of Materials in various formats.

```python
class SBOMGenerator:
    """Generates Software Bill of Materials in multiple formats."""
    
    def __init__(self, analyzer: DependencyAnalyzer):
        """Initialize with dependency analyzer."""
        
    def generate_sbom(
        self, 
        format_type: str, 
        include_vulnerabilities: bool = True,
        include_dev_dependencies: bool = False
    ) -> SBOMDocument:
        """Generate SBOM in specified format.
        
        Args:
            format_type: SBOM format ('cyclonedx', 'spdx', 'custom')
            include_vulnerabilities: Include vulnerability data
            include_dev_dependencies: Include development dependencies
            
        Returns:
            Complete SBOM document
        """
        
    def generate_vulnerability_report(self) -> VulnerabilityReport:
        """Generate detailed vulnerability report.
        
        Returns:
            Structured vulnerability report with remediation suggestions
        """
```

### Reporting Module

#### `strategy_sandbox.reporting.github_reporter`

##### `GitHubReporter`

Integrates with GitHub Actions for rich reporting.

```python
class GitHubReporter:
    """Handles GitHub Actions integration and reporting."""
    
    def __init__(self):
        """Initialize with GitHub environment detection."""
        
    def add_to_summary(self, content: str, title: Optional[str] = None):
        """Add content to GitHub step summary.
        
        Args:
            content: Markdown content to add
            title: Optional section title
        """
        
    def create_artifact(self, name: str, content: Union[str, dict]):
        """Create GitHub Actions artifact.
        
        Args:
            name: Artifact name
            content: Artifact content (string or dictionary)
        """
        
    def generate_performance_report(
        self, 
        metrics: PerformanceMetrics, 
        comparison: Optional[ComparisonReport] = None
    ) -> str:
        """Generate performance report for GitHub.
        
        Args:
            metrics: Performance metrics data
            comparison: Optional comparison against baseline
            
        Returns:
            Formatted markdown report
        """
```

## Data Models

### Core Data Types

#### `BenchmarkResult`

```python
@dataclass
class BenchmarkResult:
    """Individual benchmark result data."""
    
    name: str                    # Benchmark test name
    mean: float                  # Mean execution time
    std: float                   # Standard deviation
    min: float                   # Minimum execution time
    max: float                   # Maximum execution time
    unit: str                    # Time unit (e.g., 'seconds')
    ops: Optional[float] = None  # Operations per second
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
```

#### `SecurityScanResult`

```python
@dataclass
class SecurityScanResult:
    """Security scan results container."""
    
    scanner_name: str
    scanner_version: str
    scan_timestamp: datetime
    project_path: Path
    vulnerabilities: List[Vulnerability]
    metadata: Dict[str, Any]
    
    def get_vulnerabilities_by_severity(self, severity: str) -> List[Vulnerability]:
        """Filter vulnerabilities by severity level."""
        
    def calculate_risk_score(self) -> float:
        """Calculate overall security risk score."""
```

#### `Vulnerability`

```python
@dataclass
class Vulnerability:
    """Security vulnerability information."""
    
    id: str                              # Vulnerability ID (CVE, GHSA, etc.)
    package_name: str                    # Affected package name
    package_version: str                 # Affected package version
    severity: str                        # Severity level
    score: float                         # CVSS score
    description: str                     # Vulnerability description
    references: List[str]                # Reference URLs
    fixed_in: List[str]                  # Fixed in versions
    published_date: Optional[datetime]   # Publication date
    modified_date: Optional[datetime]    # Last modification date
```

## Configuration Schemas

### Performance Configuration

```yaml
# Performance threshold configuration
thresholds:
  execution_time:
    warning: 10.0      # Warning threshold (percentage)
    critical: 25.0     # Critical threshold (percentage)
    
  memory_usage:
    warning: 15.0
    critical: 30.0
    
  throughput:
    warning: -10.0     # Negative for decreases
    critical: -25.0

# Benchmark-specific overrides
benchmark_thresholds:
  test_simulation_throughput:
    execution_time:
      warning: 5.0
      critical: 15.0
```

### Security Configuration

```yaml
# Security policy configuration
vulnerability_policy:
  blocking:
    critical: 0        # Block any critical vulnerabilities
    high: 2            # Block if more than 2 high severity
    medium: 10         # Block if more than 10 medium severity
    
  grace_period:
    critical: 0        # Fix immediately
    high: 7            # 7 days to fix
    medium: 30         # 30 days to fix
    low: 90            # 90 days to fix
```

## CLI Interfaces

### Performance CLI

```bash
# Collect performance metrics
python -m strategy_sandbox.performance.collector \
    --benchmark-file reports/benchmark.json \
    --output reports/performance_report.json

# Compare with baseline
python -m strategy_sandbox.performance.comparator \
    --current reports/performance_report.json \
    --baseline performance_data/baselines/main_baseline.json \
    --output reports/comparison_report.json
```

### Security CLI

```bash
# Run security scan
python -m strategy_sandbox.security.analyzer \
    --project-path . \
    --output reports/security_scan.json

# Generate SBOM
python -m strategy_sandbox.security.sbom_generator \
    --format cyclonedx \
    --output reports/sbom.json \
    --include-vulnerabilities
```

### Reporting CLI

```bash
# Generate GitHub report
python -m strategy_sandbox.reporting.github_reporter \
    --performance-data reports/performance_report.json \
    --security-data reports/security_scan.json \
    --output-format github

# Generate comprehensive report
python -m strategy_sandbox.reporting.report_generator \
    --all-data reports/ \
    --template comprehensive \
    --output reports/complete_report.html
```

## Error Handling

### Exception Types

#### `PerformanceError`

Base exception for performance monitoring errors.

```python
class PerformanceError(Exception):
    """Base exception for performance monitoring errors."""
    pass

class BenchmarkParsingError(PerformanceError):
    """Error parsing benchmark results."""
    pass

class ThresholdValidationError(PerformanceError):
    """Error validating performance thresholds."""
    pass
```

#### `SecurityError`

Base exception for security scanning errors.

```python
class SecurityError(Exception):
    """Base exception for security scanning errors."""
    pass

class VulnerabilityDatabaseError(SecurityError):
    """Error accessing vulnerability database."""
    pass

class SBOMGenerationError(SecurityError):
    """Error generating SBOM document."""
    pass
```

## Extension Points

### Custom Collectors

Implement the `BaseCollector` interface:

```python
from strategy_sandbox.performance.collector import BaseCollector

class CustomMetricsCollector(BaseCollector):
    """Custom metrics collector implementation."""
    
    def collect(self) -> Dict[str, Any]:
        """Collect custom metrics."""
        return {
            "custom_metric": self._collect_custom_metric(),
            "timestamp": datetime.utcnow().isoformat()
        }
```

### Custom Analyzers

Implement the `BaseAnalyzer` interface:

```python
from strategy_sandbox.performance.comparator import BaseAnalyzer

class CustomPerformanceAnalyzer(BaseAnalyzer):
    """Custom performance analysis implementation."""
    
    def analyze(self, data: PerformanceMetrics) -> AnalysisResult:
        """Implement custom analysis logic."""
        # Custom analysis implementation
        pass
```

### Custom Report Formats

Implement the `BaseReportFormat` interface:

```python
from strategy_sandbox.reporting.report_generator import BaseReportFormat

class CustomReportFormat(BaseReportFormat):
    """Custom report format implementation."""
    
    def generate(self, data: ReportData) -> str:
        """Generate custom format report."""
        # Custom format implementation
        pass
```

## Integration Examples

### GitHub Actions Integration

```yaml
- name: Run Performance Analysis
  run: |
    python -m strategy_sandbox.performance.collector \
      --benchmark-file reports/benchmark.json \
      --output performance_report.json
    
    python -m strategy_sandbox.reporting.github_reporter \
      --performance-data performance_report.json
```

### Custom Workflow Integration

```python
from strategy_sandbox.performance.collector import PerformanceCollector
from strategy_sandbox.reporting.github_reporter import GitHubReporter

# Initialize components
collector = PerformanceCollector()
reporter = GitHubReporter()

# Collect metrics
metrics = collector.collect_system_info()
benchmark_data = collector.process_benchmark_results(Path("benchmark.json"))

# Generate report
report = reporter.generate_performance_report(metrics, benchmark_data)
reporter.add_to_summary(report, "Performance Analysis")
```

For more detailed implementation examples, see the [Developer Guide](developer-guide/architecture.md).