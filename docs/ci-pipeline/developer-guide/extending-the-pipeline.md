# Extending the CI Pipeline

This guide provides detailed instructions for extending and customizing the HB Strategy Sandbox CI pipeline to meet specific requirements.

## Overview

The CI pipeline is designed with extensibility in mind, providing multiple extension points for:
- **Custom metrics collection**
- **Additional analysis algorithms**
- **New report formats**
- **Integration with external systems**
- **Custom security scanners**
- **Enhanced visualization**

## Extension Architecture

### Plugin System

The pipeline uses a plugin-based architecture for extensibility:

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class PipelinePlugin(ABC):
    """Base class for pipeline plugins."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version."""
        pass

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize plugin with configuration."""
        pass

    @abstractmethod
    def execute(self, context: PipelineContext) -> PluginResult:
        """Execute plugin logic."""
        pass
```

### Registration System

Plugins are registered during pipeline initialization:

```python
from strategy_sandbox.core.plugin_manager import PluginManager

# Register custom plugins
plugin_manager = PluginManager()
plugin_manager.register_plugin('custom_metrics', CustomMetricsPlugin())
plugin_manager.register_plugin('external_scanner', ExternalScannerPlugin())
```

## Extending Performance Monitoring

### Custom Metrics Collection

Create custom performance metrics collectors:

```python
from strategy_sandbox.performance.collector import BaseCollector
from strategy_sandbox.performance.models import MetricsData
import psutil
import time

class CustomSystemMetricsCollector(BaseCollector):
    """Collects custom system-level performance metrics."""

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.sample_interval = config.get('sample_interval', 1.0) if config else 1.0

    def collect(self) -> MetricsData:
        """Collect custom system metrics."""
        start_time = time.time()

        # Collect CPU metrics
        cpu_metrics = self._collect_cpu_metrics()

        # Collect memory metrics
        memory_metrics = self._collect_memory_metrics()

        # Collect I/O metrics
        io_metrics = self._collect_io_metrics()

        # Collect network metrics
        network_metrics = self._collect_network_metrics()

        collection_time = time.time() - start_time

        return MetricsData(
            timestamp=start_time,
            collection_duration=collection_time,
            metrics={
                'cpu': cpu_metrics,
                'memory': memory_metrics,
                'io': io_metrics,
                'network': network_metrics
            }
        )

    def _collect_cpu_metrics(self) -> Dict[str, float]:
        """Collect detailed CPU metrics."""
        return {
            'usage_percent': psutil.cpu_percent(interval=self.sample_interval),
            'load_average_1m': psutil.getloadavg()[0],
            'load_average_5m': psutil.getloadavg()[1],
            'load_average_15m': psutil.getloadavg()[2],
            'context_switches': psutil.cpu_stats().ctx_switches,
            'interrupts': psutil.cpu_stats().interrupts
        }

    def _collect_memory_metrics(self) -> Dict[str, float]:
        """Collect detailed memory metrics."""
        virtual_memory = psutil.virtual_memory()
        swap_memory = psutil.swap_memory()

        return {
            'virtual_total': virtual_memory.total,
            'virtual_available': virtual_memory.available,
            'virtual_used': virtual_memory.used,
            'virtual_percent': virtual_memory.percent,
            'swap_total': swap_memory.total,
            'swap_used': swap_memory.used,
            'swap_percent': swap_memory.percent
        }

    def _collect_io_metrics(self) -> Dict[str, float]:
        """Collect I/O performance metrics."""
        io_counters = psutil.disk_io_counters()
        if io_counters:
            return {
                'read_count': io_counters.read_count,
                'write_count': io_counters.write_count,
                'read_bytes': io_counters.read_bytes,
                'write_bytes': io_counters.write_bytes,
                'read_time': io_counters.read_time,
                'write_time': io_counters.write_time
            }
        return {}

    def _collect_network_metrics(self) -> Dict[str, float]:
        """Collect network performance metrics."""
        network_io = psutil.net_io_counters()
        return {
            'bytes_sent': network_io.bytes_sent,
            'bytes_recv': network_io.bytes_recv,
            'packets_sent': network_io.packets_sent,
            'packets_recv': network_io.packets_recv,
            'errors_in': network_io.errin,
            'errors_out': network_io.errout,
            'drops_in': network_io.dropin,
            'drops_out': network_io.dropout
        }
```

### Custom Analysis Algorithms

Implement custom performance analysis:

```python
from strategy_sandbox.performance.comparator import BaseAnalyzer
from strategy_sandbox.performance.models import AnalysisResult, PerformanceMetrics
import numpy as np
from scipy import stats

class StatisticalPerformanceAnalyzer(BaseAnalyzer):
    """Advanced statistical analysis of performance data."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.confidence_level = config.get('confidence_level', 0.95)
        self.outlier_threshold = config.get('outlier_threshold', 2.0)

    def analyze(self, current_metrics: PerformanceMetrics,
                historical_metrics: List[PerformanceMetrics]) -> AnalysisResult:
        """Perform advanced statistical analysis."""

        results = {}

        for metric_name in current_metrics.benchmarks:
            current_values = self._extract_metric_values(current_metrics, metric_name)
            historical_values = self._extract_historical_values(historical_metrics, metric_name)

            # Perform statistical tests
            statistical_result = self._perform_statistical_tests(current_values, historical_values)

            # Detect outliers
            outliers = self._detect_outliers(current_values, historical_values)

            # Calculate confidence intervals
            confidence_interval = self._calculate_confidence_interval(historical_values)

            # Assess normality
            normality_test = self._test_normality(historical_values)

            results[metric_name] = {
                'statistical_significance': statistical_result,
                'outliers': outliers,
                'confidence_interval': confidence_interval,
                'normality': normality_test,
                'trend_analysis': self._analyze_trend(historical_values)
            }

        return AnalysisResult(
            analysis_type='statistical',
            results=results,
            metadata={
                'confidence_level': self.confidence_level,
                'outlier_threshold': self.outlier_threshold,
                'sample_size': len(historical_metrics)
            }
        )

    def _perform_statistical_tests(self, current: List[float],
                                   historical: List[float]) -> Dict[str, Any]:
        """Perform various statistical tests."""
        if len(historical) < 3:
            return {'insufficient_data': True}

        # T-test for mean difference
        t_stat, t_p_value = stats.ttest_ind(current, historical)

        # Mann-Whitney U test (non-parametric)
        u_stat, u_p_value = stats.mannwhitneyu(current, historical, alternative='two-sided')

        # Kolmogorov-Smirnov test for distribution similarity
        ks_stat, ks_p_value = stats.ks_2samp(current, historical)

        return {
            't_test': {'statistic': t_stat, 'p_value': t_p_value},
            'mann_whitney': {'statistic': u_stat, 'p_value': u_p_value},
            'kolmogorov_smirnov': {'statistic': ks_stat, 'p_value': ks_p_value},
            'significant_change': min(t_p_value, u_p_value, ks_p_value) < (1 - self.confidence_level)
        }

    def _detect_outliers(self, current: List[float],
                         historical: List[float]) -> Dict[str, Any]:
        """Detect outliers using multiple methods."""
        all_values = historical + current

        # Z-score method
        z_scores = np.abs(stats.zscore(all_values))
        z_outliers = np.where(z_scores > self.outlier_threshold)[0].tolist()

        # IQR method
        q1, q3 = np.percentile(all_values, [25, 75])
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        iqr_outliers = [i for i, v in enumerate(all_values)
                        if v < lower_bound or v > upper_bound]

        return {
            'z_score_outliers': z_outliers,
            'iqr_outliers': iqr_outliers,
            'outlier_count': len(set(z_outliers + iqr_outliers)),
            'outlier_percentage': len(set(z_outliers + iqr_outliers)) / len(all_values) * 100
        }

    def _calculate_confidence_interval(self, values: List[float]) -> Dict[str, float]:
        """Calculate confidence interval for the mean."""
        if len(values) < 2:
            return {'insufficient_data': True}

        mean = np.mean(values)
        sem = stats.sem(values)  # Standard error of the mean
        ci = stats.t.interval(self.confidence_level, len(values)-1, loc=mean, scale=sem)

        return {
            'mean': mean,
            'lower_bound': ci[0],
            'upper_bound': ci[1],
            'margin_of_error': ci[1] - mean
        }

    def _test_normality(self, values: List[float]) -> Dict[str, Any]:
        """Test if data follows normal distribution."""
        if len(values) < 3:
            return {'insufficient_data': True}

        # Shapiro-Wilk test
        shapiro_stat, shapiro_p = stats.shapiro(values)

        # Anderson-Darling test
        anderson_result = stats.anderson(values, dist='norm')

        return {
            'shapiro_wilk': {
                'statistic': shapiro_stat,
                'p_value': shapiro_p,
                'is_normal': shapiro_p > 0.05
            },
            'anderson_darling': {
                'statistic': anderson_result.statistic,
                'critical_values': anderson_result.critical_values.tolist(),
                'significance_levels': anderson_result.significance_level.tolist()
            }
        }

    def _analyze_trend(self, values: List[float]) -> Dict[str, Any]:
        """Analyze trend in historical data."""
        if len(values) < 3:
            return {'insufficient_data': True}

        x = np.arange(len(values))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)

        # Determine trend direction
        if abs(slope) < std_err:
            trend = 'stable'
        elif slope > 0:
            trend = 'increasing'
        else:
            trend = 'decreasing'

        return {
            'slope': slope,
            'intercept': intercept,
            'correlation': r_value,
            'p_value': p_value,
            'standard_error': std_err,
            'trend': trend,
            'trend_strength': abs(r_value)
        }
```

### Custom Threshold Policies

Create dynamic threshold policies:

```python
from strategy_sandbox.performance.models import ThresholdConfig
from typing import Dict, Any, Optional
import math

class AdaptiveThresholdPolicy:
    """Adaptive threshold policy based on historical variance."""

    def __init__(self, base_config: ThresholdConfig):
        self.base_config = base_config
        self.adaptation_factor = 1.5
        self.min_history_points = 10

    def calculate_thresholds(self, metric_name: str,
                           historical_data: List[float],
                           current_environment: str) -> Dict[str, float]:
        """Calculate adaptive thresholds based on historical variance."""

        if len(historical_data) < self.min_history_points:
            # Use base thresholds if insufficient history
            return self._get_base_thresholds(metric_name, current_environment)

        # Calculate statistical properties
        mean = np.mean(historical_data)
        std = np.std(historical_data)

        # Calculate coefficient of variation
        cv = std / mean if mean != 0 else 0

        # Adapt thresholds based on variance
        adaptation_multiplier = 1 + (cv * self.adaptation_factor)

        base_thresholds = self._get_base_thresholds(metric_name, current_environment)

        return {
            'warning': base_thresholds['warning'] * adaptation_multiplier,
            'critical': base_thresholds['critical'] * adaptation_multiplier,
            'adaptation_info': {
                'coefficient_of_variation': cv,
                'adaptation_multiplier': adaptation_multiplier,
                'historical_mean': mean,
                'historical_std': std
            }
        }

    def _get_base_thresholds(self, metric_name: str, environment: str) -> Dict[str, float]:
        """Get base thresholds from configuration."""
        # Implementation would fetch from configuration
        return {
            'warning': 10.0,
            'critical': 25.0
        }
```

## Extending Security Scanning

### Custom Security Scanners

Implement custom security scanners:

```python
from strategy_sandbox.security.analyzer import BaseSecurityScanner
from strategy_sandbox.security.models import SecurityScanResult, Vulnerability
import subprocess
import json
from pathlib import Path

class CustomVulnerabilityScanner(BaseSecurityScanner):
    """Custom vulnerability scanner implementation."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.scanner_executable = config.get('scanner_path', 'custom-scanner')
        self.severity_mapping = {
            'low': 'low',
            'medium': 'medium',
            'high': 'high',
            'critical': 'critical'
        }

    def scan(self, project_path: Path) -> SecurityScanResult:
        """Perform custom security scan."""

        # Execute external scanner
        scan_results = self._execute_scanner(project_path)

        # Parse results
        vulnerabilities = self._parse_scan_results(scan_results)

        # Generate metadata
        metadata = self._generate_metadata(project_path, len(vulnerabilities))

        return SecurityScanResult(
            scanner_name=self.name,
            scanner_version=self.version,
            scan_timestamp=datetime.utcnow(),
            project_path=project_path,
            vulnerabilities=vulnerabilities,
            metadata=metadata
        )

    def _execute_scanner(self, project_path: Path) -> Dict[str, Any]:
        """Execute the external scanner tool."""
        cmd = [
            self.scanner_executable,
            '--format', 'json',
            '--project', str(project_path),
            '--output', '-'
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                check=True
            )
            return json.loads(result.stdout)
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Scanner timed out after 300 seconds")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Scanner failed: {e.stderr}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse scanner output: {e}")

    def _parse_scan_results(self, scan_data: Dict[str, Any]) -> List[Vulnerability]:
        """Parse scanner output into vulnerability objects."""
        vulnerabilities = []

        for item in scan_data.get('vulnerabilities', []):
            vulnerability = Vulnerability(
                id=item['id'],
                package_name=item['package'],
                package_version=item['version'],
                vulnerability_id=item['cve_id'],
                severity=self.severity_mapping.get(item['severity'], 'unknown'),
                score=item.get('score', 0.0),
                description=item.get('description', ''),
                references=item.get('references', []),
                fixed_in=item.get('fixed_versions', []),
                published_date=self._parse_date(item.get('published')),
                modified_date=self._parse_date(item.get('modified'))
            )
            vulnerabilities.append(vulnerability)

        return vulnerabilities

    def _generate_metadata(self, project_path: Path, vulnerability_count: int) -> Dict[str, Any]:
        """Generate scan metadata."""
        return {
            'project_files_scanned': len(list(project_path.rglob('*.py'))),
            'dependencies_analyzed': self._count_dependencies(project_path),
            'vulnerability_count': vulnerability_count,
            'scanner_config': self.config
        }
```

### Custom SBOM Formats

Implement custom SBOM formats:

```python
from strategy_sandbox.security.sbom_generator import BaseSBOMFormat
from strategy_sandbox.security.models import SBOMDocument, Component
from typing import Dict, Any, List
import json

class CustomSBOMFormat(BaseSBOMFormat):
    """Custom SBOM format implementation."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.format_name = "custom-enhanced"
        self.format_version = "1.0"

    def generate(self, components: List[Component],
                 metadata: Dict[str, Any]) -> SBOMDocument:
        """Generate SBOM in custom format."""

        document = {
            'sbom_format': self.format_name,
            'format_version': self.format_version,
            'generated_timestamp': datetime.utcnow().isoformat(),
            'metadata': self._enhance_metadata(metadata),
            'components': self._process_components(components),
            'relationships': self._build_relationships(components),
            'custom_extensions': self._add_custom_extensions(components)
        }

        return SBOMDocument(
            format=self.format_name,
            content=document,
            metadata=metadata
        )

    def _enhance_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Add custom metadata enhancements."""
        enhanced = metadata.copy()
        enhanced.update({
            'build_environment': self._get_build_environment(),
            'security_context': self._get_security_context(),
            'compliance_info': self._get_compliance_info()
        })
        return enhanced

    def _process_components(self, components: List[Component]) -> List[Dict[str, Any]]:
        """Process components with custom enhancements."""
        processed = []

        for component in components:
            processed_component = {
                'name': component.name,
                'version': component.version,
                'type': component.type,
                'licenses': component.licenses,
                'vulnerabilities': self._process_vulnerabilities(component.vulnerabilities),
                'custom_fields': {
                    'risk_score': self._calculate_risk_score(component),
                    'maintenance_status': self._assess_maintenance_status(component),
                    'usage_analysis': self._analyze_usage(component)
                }
            }
            processed.append(processed_component)

        return processed

    def _build_relationships(self, components: List[Component]) -> List[Dict[str, Any]]:
        """Build component relationship graph."""
        relationships = []

        for component in components:
            for dependency in component.dependencies:
                relationship = {
                    'source': component.name,
                    'target': dependency.name,
                    'type': 'depends_on',
                    'metadata': {
                        'version_constraint': dependency.version_constraint,
                        'optional': dependency.optional,
                        'development_only': dependency.dev_dependency
                    }
                }
                relationships.append(relationship)

        return relationships

    def _add_custom_extensions(self, components: List[Component]) -> Dict[str, Any]:
        """Add custom format extensions."""
        return {
            'security_analysis': self._generate_security_analysis(components),
            'license_analysis': self._generate_license_analysis(components),
            'supply_chain_analysis': self._generate_supply_chain_analysis(components)
        }
```

## Extending Reporting

### Custom Report Formats

Create custom report generators:

```python
from strategy_sandbox.reporting.report_generator import BaseReportGenerator
from strategy_sandbox.reporting.models import ReportData, Report
import matplotlib.pyplot as plt
import seaborn as sns
from jinja2 import Template

class InteractiveHTMLReportGenerator(BaseReportGenerator):
    """Generate interactive HTML reports with charts."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.template_path = config.get('template_path', 'templates/interactive_report.html')

    def generate(self, report_data: ReportData) -> Report:
        """Generate interactive HTML report."""

        # Generate charts
        charts = self._generate_charts(report_data)

        # Prepare template data
        template_data = {
            'metadata': report_data.metadata,
            'performance_data': report_data.performance_data,
            'security_data': report_data.security_data,
            'charts': charts,
            'interactive_elements': self._create_interactive_elements(report_data)
        }

        # Render template
        html_content = self._render_template(template_data)

        return Report(
            format='interactive_html',
            content=html_content,
            metadata={
                'generator': self.__class__.__name__,
                'charts_count': len(charts),
                'interactive_elements': len(template_data['interactive_elements'])
            }
        )

    def _generate_charts(self, report_data: ReportData) -> Dict[str, str]:
        """Generate charts as base64-encoded images."""
        charts = {}

        # Performance trend chart
        if report_data.performance_data.historical_data:
            charts['performance_trend'] = self._create_performance_trend_chart(
                report_data.performance_data.historical_data
            )

        # Security score chart
        if report_data.security_data:
            charts['security_score'] = self._create_security_score_chart(
                report_data.security_data
            )

        # Vulnerability distribution chart
        if report_data.security_data.vulnerabilities:
            charts['vulnerability_distribution'] = self._create_vulnerability_chart(
                report_data.security_data.vulnerabilities
            )

        return charts

    def _create_performance_trend_chart(self, historical_data: List[Dict]) -> str:
        """Create performance trend chart."""
        import io
        import base64

        fig, ax = plt.subplots(figsize=(12, 6))

        # Extract data for plotting
        timestamps = [item['timestamp'] for item in historical_data]
        values = [item['mean_execution_time'] for item in historical_data]

        # Create trend line
        ax.plot(timestamps, values, marker='o', linewidth=2)
        ax.set_title('Performance Trend Over Time')
        ax.set_xlabel('Time')
        ax.set_ylabel('Execution Time (seconds)')
        ax.grid(True, alpha=0.3)

        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        chart_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()

        return f"data:image/png;base64,{chart_base64}"

    def _create_interactive_elements(self, report_data: ReportData) -> List[Dict[str, Any]]:
        """Create interactive elements for the report."""
        elements = []

        # Performance metrics table with sorting
        elements.append({
            'type': 'sortable_table',
            'id': 'performance_metrics',
            'title': 'Performance Metrics',
            'data': self._prepare_performance_table_data(report_data.performance_data)
        })

        # Vulnerability details with filtering
        elements.append({
            'type': 'filterable_list',
            'id': 'vulnerabilities',
            'title': 'Security Vulnerabilities',
            'data': self._prepare_vulnerability_list_data(report_data.security_data)
        })

        # Interactive dependency graph
        elements.append({
            'type': 'dependency_graph',
            'id': 'dependency_visualization',
            'title': 'Dependency Graph',
            'data': self._prepare_dependency_graph_data(report_data.security_data)
        })

        return elements
```

### Custom Notification Systems

Implement custom notification handlers:

```python
from strategy_sandbox.reporting.notifications import BaseNotificationHandler
from strategy_sandbox.reporting.models import NotificationData
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class SlackNotificationHandler(BaseNotificationHandler):
    """Send notifications to Slack channels."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.webhook_url = config['webhook_url']
        self.channel = config.get('channel', '#ci-notifications')
        self.username = config.get('username', 'CI Pipeline Bot')

    def send_notification(self, notification_data: NotificationData) -> bool:
        """Send notification to Slack."""

        # Prepare Slack message
        message = self._prepare_slack_message(notification_data)

        try:
            response = requests.post(
                self.webhook_url,
                json=message,
                timeout=30
            )
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            self.logger.error(f"Failed to send Slack notification: {e}")
            return False

    def _prepare_slack_message(self, data: NotificationData) -> Dict[str, Any]:
        """Prepare Slack message format."""

        # Determine color based on notification type
        color_map = {
            'success': 'good',
            'warning': 'warning',
            'error': 'danger',
            'info': '#439FE0'
        }

        attachments = [{
            'color': color_map.get(data.type, '#439FE0'),
            'title': data.title,
            'text': data.message,
            'fields': self._prepare_slack_fields(data),
            'footer': 'CI Pipeline',
            'ts': int(data.timestamp.timestamp())
        }]

        return {
            'channel': self.channel,
            'username': self.username,
            'attachments': attachments
        }

    def _prepare_slack_fields(self, data: NotificationData) -> List[Dict[str, Any]]:
        """Prepare Slack message fields."""
        fields = []

        if data.metadata:
            for key, value in data.metadata.items():
                fields.append({
                    'title': key.replace('_', ' ').title(),
                    'value': str(value),
                    'short': len(str(value)) < 50
                })

        return fields

class EmailNotificationHandler(BaseNotificationHandler):
    """Send email notifications."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.smtp_server = config['smtp_server']
        self.smtp_port = config.get('smtp_port', 587)
        self.username = config['username']
        self.password = config['password']
        self.from_email = config['from_email']
        self.to_emails = config['to_emails']

    def send_notification(self, notification_data: NotificationData) -> bool:
        """Send email notification."""

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = notification_data.title
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.to_emails)

            # Create HTML content
            html_content = self._create_html_email(notification_data)
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            return True
        except Exception as e:
            self.logger.error(f"Failed to send email notification: {e}")
            return False

    def _create_html_email(self, data: NotificationData) -> str:
        """Create HTML email content."""
        template = Template("""
        <html>
        <body>
            <h2>{{ title }}</h2>
            <p>{{ message }}</p>

            {% if metadata %}
            <h3>Details:</h3>
            <table border="1" style="border-collapse: collapse;">
                {% for key, value in metadata.items() %}
                <tr>
                    <td><strong>{{ key.replace('_', ' ').title() }}</strong></td>
                    <td>{{ value }}</td>
                </tr>
                {% endfor %}
            </table>
            {% endif %}

            <p><em>Generated by CI Pipeline at {{ timestamp }}</em></p>
        </body>
        </html>
        """)

        return template.render(
            title=data.title,
            message=data.message,
            metadata=data.metadata,
            timestamp=data.timestamp
        )
```

## Integration Extensions

### External Tool Integration

Integrate with external tools and services:

```python
from strategy_sandbox.integrations.base import BaseIntegration
import requests
from typing import Optional

class JiraIntegration(BaseIntegration):
    """Integration with Jira for issue tracking."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config['base_url']
        self.username = config['username']
        self.api_token = config['api_token']
        self.project_key = config['project_key']

    def create_security_issue(self, vulnerability: Vulnerability) -> Optional[str]:
        """Create Jira issue for security vulnerability."""

        issue_data = {
            'fields': {
                'project': {'key': self.project_key},
                'summary': f"Security Vulnerability: {vulnerability.id}",
                'description': self._format_vulnerability_description(vulnerability),
                'issuetype': {'name': 'Bug'},
                'priority': {'name': self._map_severity_to_priority(vulnerability.severity)},
                'labels': ['security', 'vulnerability', vulnerability.severity]
            }
        }

        try:
            response = requests.post(
                f"{self.base_url}/rest/api/2/issue",
                json=issue_data,
                auth=(self.username, self.api_token),
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()

            issue_key = response.json()['key']
            self.logger.info(f"Created Jira issue {issue_key} for vulnerability {vulnerability.id}")
            return issue_key

        except requests.RequestException as e:
            self.logger.error(f"Failed to create Jira issue: {e}")
            return None

    def _format_vulnerability_description(self, vulnerability: Vulnerability) -> str:
        """Format vulnerability details for Jira description."""
        description = f"""
        *Vulnerability Details:*

        * Package: {vulnerability.package_name}
        * Version: {vulnerability.package_version}
        * CVE ID: {vulnerability.vulnerability_id}
        * Severity: {vulnerability.severity}
        * Score: {vulnerability.score}

        *Description:*
        {vulnerability.description}

        *Fixed In:*
        {', '.join(vulnerability.fixed_in) if vulnerability.fixed_in else 'No fix available'}

        *References:*
        {chr(10).join(f'* {ref}' for ref in vulnerability.references)}
        """
        return description

    def _map_severity_to_priority(self, severity: str) -> str:
        """Map vulnerability severity to Jira priority."""
        mapping = {
            'critical': 'Highest',
            'high': 'High',
            'medium': 'Medium',
            'low': 'Low'
        }
        return mapping.get(severity, 'Medium')

class SonarQubeIntegration(BaseIntegration):
    """Integration with SonarQube for code quality analysis."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config['base_url']
        self.token = config['token']
        self.project_key = config['project_key']

    def get_quality_gate_status(self) -> Dict[str, Any]:
        """Get SonarQube quality gate status."""

        try:
            response = requests.get(
                f"{self.base_url}/api/qualitygates/project_status",
                params={'projectKey': self.project_key},
                auth=(self.token, ''),
                timeout=30
            )
            response.raise_for_status()

            data = response.json()
            return {
                'status': data.get('projectStatus', {}).get('status'),
                'conditions': data.get('projectStatus', {}).get('conditions', []),
                'timestamp': data.get('projectStatus', {}).get('timestamp')
            }

        except requests.RequestException as e:
            self.logger.error(f"Failed to get SonarQube quality gate status: {e}")
            return {'status': 'ERROR', 'error': str(e)}

    def get_metrics(self, metrics: List[str]) -> Dict[str, Any]:
        """Get specific metrics from SonarQube."""

        try:
            response = requests.get(
                f"{self.base_url}/api/measures/component",
                params={
                    'component': self.project_key,
                    'metricKeys': ','.join(metrics)
                },
                auth=(self.token, ''),
                timeout=30
            )
            response.raise_for_status()

            data = response.json()
            measures = {}

            for measure in data.get('component', {}).get('measures', []):
                measures[measure['metric']] = measure.get('value')

            return measures

        except requests.RequestException as e:
            self.logger.error(f"Failed to get SonarQube metrics: {e}")
            return {}
```

## Configuration and Setup

### Plugin Configuration

Configure plugins in your pipeline configuration:

```yaml
# pipeline_config.yaml
pipeline:
  plugins:
    performance:
      - name: custom_system_metrics
        class: CustomSystemMetricsCollector
        config:
          sample_interval: 0.5

      - name: statistical_analyzer
        class: StatisticalPerformanceAnalyzer
        config:
          confidence_level: 0.95
          outlier_threshold: 2.0

    security:
      - name: custom_vulnerability_scanner
        class: CustomVulnerabilityScanner
        config:
          scanner_path: /usr/local/bin/custom-scanner

    reporting:
      - name: interactive_html_reports
        class: InteractiveHTMLReportGenerator
        config:
          template_path: templates/custom_report.html

    notifications:
      - name: slack
        class: SlackNotificationHandler
        config:
          webhook_url: "${SLACK_WEBHOOK_URL}"
          channel: "#ci-notifications"

      - name: email
        class: EmailNotificationHandler
        config:
          smtp_server: smtp.company.com
          username: "${EMAIL_USERNAME}"
          password: "${EMAIL_PASSWORD}"
          from_email: ci-pipeline@company.com
          to_emails:
            - team@company.com
            - security@company.com

    integrations:
      - name: jira
        class: JiraIntegration
        config:
          base_url: https://company.atlassian.net
          username: "${JIRA_USERNAME}"
          api_token: "${JIRA_API_TOKEN}"
          project_key: SECURITY
```

### Plugin Loading

Load and initialize plugins:

```python
from strategy_sandbox.core.plugin_manager import PluginManager
from strategy_sandbox.core.config import load_pipeline_config

def initialize_pipeline_with_plugins():
    """Initialize pipeline with configured plugins."""

    # Load configuration
    config = load_pipeline_config('pipeline_config.yaml')

    # Initialize plugin manager
    plugin_manager = PluginManager()

    # Load plugins
    for category, plugins in config.pipeline.plugins.items():
        for plugin_config in plugins:
            plugin_class = import_plugin_class(plugin_config.class_name)
            plugin_instance = plugin_class(plugin_config.config)
            plugin_manager.register_plugin(category, plugin_config.name, plugin_instance)

    return plugin_manager

def import_plugin_class(class_path: str):
    """Dynamically import plugin class."""
    module_path, class_name = class_path.rsplit('.', 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)
```

## Best Practices

### Plugin Development

#### Error Handling
```python
class RobustPlugin(PipelinePlugin):
    def execute(self, context: PipelineContext) -> PluginResult:
        try:
            result = self._perform_operation(context)
            return PluginResult.success(result)
        except Exception as e:
            self.logger.error(f"Plugin execution failed: {e}")
            return PluginResult.failure(str(e))
```

#### Configuration Validation
```python
from pydantic import BaseModel, validator

class PluginConfig(BaseModel):
    sample_interval: float
    threshold: float

    @validator('sample_interval')
    def validate_sample_interval(cls, v):
        if v <= 0:
            raise ValueError('Sample interval must be positive')
        return v
```

#### Resource Management
```python
import contextlib

class ResourceAwarePlugin(PipelinePlugin):
    @contextlib.contextmanager
    def managed_resources(self):
        """Properly manage plugin resources."""
        resources = self._acquire_resources()
        try:
            yield resources
        finally:
            self._release_resources(resources)
```

### Testing Extensions

#### Unit Testing
```python
import pytest
from unittest.mock import Mock, patch

class TestCustomMetricsCollector:
    def test_metrics_collection(self):
        collector = CustomSystemMetricsCollector({'sample_interval': 1.0})

        with patch('psutil.cpu_percent', return_value=50.0):
            metrics = collector.collect()

        assert metrics.metrics['cpu']['usage_percent'] == 50.0
```

#### Integration Testing
```python
class TestPluginIntegration:
    def test_plugin_pipeline_integration(self):
        plugin_manager = PluginManager()
        plugin_manager.register_plugin('test', TestPlugin())

        context = PipelineContext()
        results = plugin_manager.execute_plugins('test', context)

        assert len(results) == 1
        assert results[0].success
```

For more information on specific extension patterns, see the [API Reference](../../reference.md).
