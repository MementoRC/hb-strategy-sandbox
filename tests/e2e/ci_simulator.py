"""CI Pipeline Simulator for end-to-end testing."""

import json
import os
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import patch

from strategy_sandbox.performance.collector import PerformanceCollector
from strategy_sandbox.performance.trend_analyzer import TrendAnalyzer
from strategy_sandbox.reporting.github_reporter import GitHubReporter
from strategy_sandbox.security.analyzer import DependencyAnalyzer
from strategy_sandbox.security.dashboard_generator import SecurityDashboardGenerator
from strategy_sandbox.security.sbom_generator import SBOMGenerator


class CISimulatorResult:
    """Result from CI pipeline simulation."""

    def __init__(self):
        self.artifacts: Dict[str, str] = {}
        self.step_summary: str = ""
        self.detected_regressions: List[str] = []
        self.detected_vulnerabilities: List[str] = []
        self.performance_data: Dict[str, Any] = {}
        self.security_data: Dict[str, Any] = {}
        self.reports: Dict[str, str] = {}
        self.success: bool = True
        self.errors: List[str] = []

    def add_artifact(self, name: str, content: str) -> None:
        """Add an artifact to the results."""
        self.artifacts[name] = content

    def add_error(self, error: str) -> None:
        """Add an error to the results."""
        self.errors.append(error)
        self.success = False


class CISimulator:
    """Simulates CI pipeline execution for testing."""

    def __init__(self, test_repo: Optional[Path] = None):
        """Initialize CI simulator."""
        self.test_repo = test_repo or Path(tempfile.mkdtemp())
        self.artifacts_dir = self.test_repo / "artifacts"
        self.artifacts_dir.mkdir(exist_ok=True)

        # Initialize components
        self.performance_collector = PerformanceCollector()
        self.trend_analyzer = TrendAnalyzer()
        self.github_reporter = GitHubReporter()
        self.dependency_analyzer = DependencyAnalyzer(str(self.test_repo))
        self.sbom_generator = SBOMGenerator(self.dependency_analyzer)
        self.security_dashboard = SecurityDashboardGenerator(self.sbom_generator, self.github_reporter)

        # Track simulation state
        self.has_performance_regression = False
        self.has_vulnerable_dependency = False
        self.github_environment = False

    def setup_github_environment(self, enable: bool = True) -> None:
        """Set up GitHub Actions environment simulation."""
        self.github_environment = enable
        if enable:
            os.environ.update(
                {
                    "GITHUB_ACTIONS": "true",
                    "CI": "true",
                    "GITHUB_WORKFLOW": "CI",
                    "GITHUB_RUN_ID": "12345",
                    "GITHUB_RUN_NUMBER": "1",
                    "GITHUB_REPOSITORY": "test/repo",
                    "GITHUB_STEP_SUMMARY": str(self.artifacts_dir / "step_summary.md"),
                }
            )

    def cleanup_github_environment(self) -> None:
        """Clean up GitHub Actions environment."""
        github_vars = [
            "GITHUB_ACTIONS",
            "CI",
            "GITHUB_WORKFLOW",
            "GITHUB_RUN_ID",
            "GITHUB_RUN_NUMBER",
            "GITHUB_REPOSITORY",
            "GITHUB_STEP_SUMMARY",
        ]
        for var in github_vars:
            os.environ.pop(var, None)

    def add_performance_regression(self, severity: str = "high") -> None:
        """Simulate performance regression."""
        self.has_performance_regression = True

        # Create benchmark results with regression
        regression_data = {
            "test_slow_function": {
                "current": 2.5,  # seconds
                "baseline": 1.0,  # seconds
                "ratio": 2.5,
                "status": "regression",
                "severity": severity,
            },
            "test_memory_intensive": {
                "current": 150.0,  # MB
                "baseline": 100.0,  # MB
                "ratio": 1.5,
                "status": "warning",
                "severity": "medium",
            },
        }

        # Save benchmark results
        benchmark_file = self.test_repo / "benchmark-results.json"
        with open(benchmark_file, "w") as f:
            json.dump(regression_data, f, indent=2)

    def add_vulnerable_dependency(self, severity: str = "high") -> None:
        """Simulate vulnerable dependency."""
        self.has_vulnerable_dependency = True

        # Create fake requirements with known vulnerable package
        requirements_file = self.test_repo / "requirements.txt"
        with open(requirements_file, "w") as f:
            f.write("requests==2.25.1\n")  # Known vulnerable version
            f.write("django==3.1.0\n")  # Another potentially vulnerable version
            f.write("pyyaml==5.3.1\n")  # Another test case

    def create_test_project_structure(self) -> None:
        """Create a realistic test project structure."""
        # Create source directories
        (self.test_repo / "src").mkdir(exist_ok=True)
        (self.test_repo / "tests").mkdir(exist_ok=True)

        # Create pyproject.toml
        pyproject_content = """
[project]
name = "test-project"
version = "1.0.0"
dependencies = [
    "requests>=2.25.0",
    "pyyaml>=5.3.0"
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
"""
        with open(self.test_repo / "pyproject.toml", "w") as f:
            f.write(pyproject_content)

    def _run_performance_monitoring(self) -> Dict[str, Any]:
        """Run performance monitoring pipeline."""
        try:
            # Create benchmark results file - use regression data if set, otherwise sample data
            benchmark_file = self.test_repo / "benchmark-results.json"
            
            if self.has_performance_regression:
                # Regression data was already created by add_performance_regression()
                pass  # File should already exist with regression data
            elif not benchmark_file.exists():
                # Create sample data only if no regression and file doesn't exist
                sample_data = {
                    "orders_placed": 100,
                    "duration_seconds": 5.2,
                    "memory_usage": "45MB",
                    "orders_per_second": 19.2,
                    "avg_order_time_ms": 52.1
                }
                with open(benchmark_file, "w") as f:
                    json.dump(sample_data, f, indent=2)

            # Collect performance metrics using the benchmark results file
            metrics = self.performance_collector.collect_metrics(benchmark_file)
            performance_data = metrics.to_dict()

            # If regression exists, load and add the regression analysis data
            if self.has_performance_regression and benchmark_file.exists():
                with open(benchmark_file) as f:
                    regression_data = json.load(f)
                
                # Add regression information to performance data
                if "test_slow_function" in regression_data:
                    performance_data["regressions_detected"] = True
                    performance_data["regression_details"] = regression_data

            return performance_data

        except Exception as e:
            return {"error": str(e), "component": "performance_monitoring"}

    def _run_security_scanning(self) -> Dict[str, Any]:
        """Run security scanning pipeline."""
        try:
            security_data = {}

            # Run dependency analysis
            if self.has_vulnerable_dependency:
                # Simulate vulnerability scan results
                vulnerabilities = [
                    {
                        "package": "requests",
                        "version": "2.25.1",
                        "vulnerability": "CVE-2023-32681",
                        "severity": "high",
                        "description": "Proxy-Connections header vulnerability",
                    },
                    {
                        "package": "pyyaml",
                        "version": "5.3.1",
                        "vulnerability": "CVE-2020-14343",
                        "severity": "medium",
                        "description": "Code execution via unsafe loading",
                    },
                ]
                security_data["vulnerabilities"] = vulnerabilities

            # Generate SBOM
            sbom_data = self.sbom_generator.generate_sbom(
                output_format="cyclonedx",
                output_type="json",
                include_dev_dependencies=False,
                include_vulnerabilities=True
            )
            security_data["sbom"] = sbom_data

            # Generate security dashboard
            dashboard_data = self.security_dashboard.generate_security_dashboard()
            security_data["dashboard"] = dashboard_data

            return security_data

        except Exception as e:
            return {"error": str(e), "component": "security_scanning"}

    def _run_trend_analysis(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run trend analysis on performance data."""
        try:
            # Simulate trend analysis
            if self.has_performance_regression:
                trend_data = {
                    "alerts": [
                        {
                            "type": "performance_regression",
                            "severity": "high",
                            "metric": "execution_time",
                            "threshold_exceeded": True,
                            "recommendation": "Investigate recent changes that may have caused performance degradation",
                        }
                    ],
                    "trends": {
                        "execution_time": {"direction": "increasing", "magnitude": 2.5},
                        "memory_usage": {"direction": "increasing", "magnitude": 1.5},
                    },
                }
            else:
                trend_data = {
                    "alerts": [],
                    "trends": {
                        "execution_time": {"direction": "stable", "magnitude": 1.0},
                        "memory_usage": {"direction": "stable", "magnitude": 1.0},
                    },
                }

            return trend_data

        except Exception as e:
            return {"error": str(e), "component": "trend_analysis"}

    def _run_reporting(
        self, performance_data: Dict[str, Any], security_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """Run reporting pipeline."""
        reports = {}

        try:
            # Generate performance report markdown
            if performance_data and "error" not in performance_data:
                perf_report_md = self.github_reporter.create_performance_summary(performance_data)
                reports["performance_report.md"] = perf_report_md

            # Generate security report markdown
            if security_data and "error" not in security_data:
                # Create pip-audit-like results from our vulnerability data
                pip_audit_data = None
                if "vulnerabilities" in security_data:
                    # Convert our vulnerability format to pip-audit format
                    dependencies = []
                    for vuln in security_data["vulnerabilities"]:
                        dependencies.append({
                            "name": vuln["package"],
                            "version": vuln["version"],
                            "vulns": [{
                                "id": vuln["vulnerability"],
                                "description": vuln["description"],
                                "severity": vuln["severity"]
                            }]
                        })
                    
                    pip_audit_data = {
                        "dependencies": dependencies
                    }
                
                sec_report_md = self.github_reporter.create_security_summary(
                    bandit_results=None,
                    pip_audit_results=pip_audit_data
                )
                reports["security_report.md"] = sec_report_md

            # Generate build status summary
            build_report = self.github_reporter.create_build_status_summary(
                build_status="success",
                test_results={"passed": 203, "failed": 0, "total": 203},
                performance_data={"coverage": {"line_rate": 85.5, "branch_rate": 78.2}, "build_time": 45.2},
                security_data={}
            )
            reports["build_status.md"] = build_report

            # Generate step summary if in GitHub environment
            if self.github_environment:
                step_summary = self._generate_step_summary(performance_data, security_data)
                reports["step_summary.md"] = step_summary

                # Write to GitHub step summary file
                summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
                if summary_file:
                    with open(summary_file, "w") as f:
                        f.write(step_summary)

            return reports

        except Exception as e:
            return {"error": str(e), "component": "reporting"}

    def _generate_step_summary(
        self, performance_data: Dict[str, Any], security_data: Dict[str, Any]
    ) -> str:
        """Generate GitHub Actions step summary."""
        summary_parts = ["# CI Pipeline Summary\n"]

        # Performance summary
        if performance_data and "error" not in performance_data:
            summary_parts.append("## 🚀 Performance Summary")
            if self.has_performance_regression:
                summary_parts.append("❌ **Performance regressions detected**")
                summary_parts.append("- test_slow_function: 2.5x slower than baseline")
                summary_parts.append("- test_memory_intensive: 1.5x more memory usage")
            else:
                summary_parts.append("✅ **No performance regressions detected**")
            summary_parts.append("")

        # Security summary
        if security_data and "error" not in security_data:
            summary_parts.append("## 🔒 Security Summary")
            vuln_count = len(security_data.get("vulnerabilities", []))
            if vuln_count > 0:
                summary_parts.append(f"⚠️ **{vuln_count} vulnerabilities detected**")
                for vuln in security_data.get("vulnerabilities", []):
                    summary_parts.append(
                        f"- {vuln['package']} ({vuln['severity']}): {vuln['vulnerability']}"
                    )
            else:
                summary_parts.append("✅ **No security vulnerabilities detected**")
            summary_parts.append("")

        # Build summary
        summary_parts.append("## 🏗️ Build Summary")
        summary_parts.append("✅ **All 203 tests passed**")
        summary_parts.append("✅ **Code coverage: 85.5%**")
        summary_parts.append("✅ **Build completed in 45.2s**")

        return "\n".join(summary_parts)

    def _collect_results(
        self,
        performance_data: Dict[str, Any],
        security_data: Dict[str, Any],
        trend_data: Dict[str, Any],
        reports: Dict[str, str],
    ) -> CISimulatorResult:
        """Collect and organize simulation results."""
        result = CISimulatorResult()

        # Add artifacts
        for name, content in reports.items():
            result.add_artifact(name, content)

        # Save artifacts to files
        for name, content in reports.items():
            artifact_file = self.artifacts_dir / name
            with open(artifact_file, "w") as f:
                f.write(content)

        # Extract performance regressions
        if self.has_performance_regression and "regression_details" in performance_data:
            for test_name, data in performance_data["regression_details"].items():
                if data.get("status") == "regression":
                    result.detected_regressions.append(f"{test_name}: {data['ratio']}x slower")

        # Extract vulnerabilities
        if self.has_vulnerable_dependency and "vulnerabilities" in security_data:
            for vuln in security_data["vulnerabilities"]:
                result.detected_vulnerabilities.append(
                    f"{vuln['package']} {vuln['version']}: {vuln['vulnerability']}"
                )

        # Set step summary
        if "step_summary.md" in reports:
            result.step_summary = reports["step_summary.md"]

        # Store raw data
        result.performance_data = performance_data
        result.security_data = security_data
        result.reports = reports

        # Check for errors
        for data in [performance_data, security_data, trend_data]:
            if isinstance(data, dict) and "error" in data:
                result.add_error(f"{data.get('component', 'unknown')}: {data['error']}")

        if isinstance(reports, dict) and "error" in reports:
            result.add_error(f"reporting: {reports['error']}")

        return result

    def run_ci_pipeline(self) -> CISimulatorResult:
        """Run complete CI pipeline simulation."""
        try:
            # Create test project structure
            self.create_test_project_structure()

            # Run performance monitoring
            performance_data = self._run_performance_monitoring()

            # Run security scanning
            security_data = self._run_security_scanning()

            # Run trend analysis
            trend_data = self._run_trend_analysis(performance_data)

            # Run reporting
            reports = self._run_reporting(performance_data, security_data)

            # Collect results
            return self._collect_results(performance_data, security_data, trend_data, reports)

        except Exception as e:
            result = CISimulatorResult()
            result.add_error(f"Pipeline execution failed: {str(e)}")
            return result

    def cleanup(self) -> None:
        """Clean up simulation artifacts."""
        import shutil

        if self.test_repo.exists():
            shutil.rmtree(self.test_repo, ignore_errors=True)

        # Clean up environment
        self.cleanup_github_environment()
