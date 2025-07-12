"""Security dashboard generator for comprehensive vulnerability and dependency reporting."""

from datetime import datetime
from typing import Any

from ..reporting.github_reporter import GitHubReporter
from .sbom_generator import SBOMGenerator


class SecurityDashboardGenerator:
    """Generates comprehensive security dashboards combining SBOM and vulnerability data."""

    def __init__(
        self,
        sbom_generator: SBOMGenerator | None = None,
        github_reporter: GitHubReporter | None = None,
    ):
        """Initialize the security dashboard generator.

        Args:
            sbom_generator: SBOMGenerator instance for SBOM and vulnerability data.
            github_reporter: GitHubReporter instance for step summary integration.
        """
        # Provide defaults for backward compatibility with tests
        if sbom_generator is None:
            sbom_generator = SBOMGenerator()
        if github_reporter is None:
            github_reporter = GitHubReporter()

        self.sbom_generator = sbom_generator
        self.github_reporter = github_reporter

    def generate_security_dashboard(
        self, security_findings: dict | None = None
    ) -> dict[str, Any] | str:
        """Generate comprehensive security dashboard.

        Args:
            security_findings: Optional security findings data for backward compatibility.

        Returns:
            Dictionary containing dashboard data and generation results,
            or HTML string if security_findings provided (for backward compatibility).
        """
        # Handle backward compatibility - use provided data if available
        if security_findings is not None:
            # Generate HTML string with vulnerability details for test compatibility
            vulnerabilities = security_findings.get("vulnerabilities", [])
            html_content = "<html><body><h1>Security Dashboard</h1>"
            html_content += f"<p>Total vulnerabilities: {len(vulnerabilities)}</p>"

            # Add scan summary if available
            if "scan_summary" in security_findings:
                scan_summary = security_findings["scan_summary"]
                html_content += f"<p>Total packages: {scan_summary.get('total_packages', 0)}</p>"
                html_content += (
                    f"<p>Vulnerable packages: {scan_summary.get('vulnerable_packages', 0)}</p>"
                )
                html_content += f"<p>Scan date: {scan_summary.get('scan_date', 'unknown')}</p>"

            for vuln in vulnerabilities:
                html_content += f"<div>Package: {vuln.get('package', 'unknown')}, "
                html_content += f"Severity: {vuln.get('severity', 'unknown')}, "
                html_content += f"Version: {vuln.get('version', 'unknown')}"
                if "cvss" in vuln:
                    html_content += f", CVSS: {vuln['cvss']}"
                html_content += "</div>"

            # Add remediation information if available
            if "remediation" in security_findings:
                remediation = security_findings["remediation"]
                html_content += "<h2>Remediation</h2>"
                html_content += f"<p>upgradeable: {remediation.get('upgradeable', 0)}</p>"
                html_content += f"<p>patchable: {remediation.get('patchable', 0)}</p>"
                html_content += f"<p>no_fix: {remediation.get('no_fix', 0)}</p>"

            html_content += f"<p>Total: {security_findings.get('total_vulnerabilities', len(vulnerabilities))}</p>"
            html_content += "</body></html>"

            # Return HTML string directly for backward compatibility
            return html_content

        # Original implementation for when no data is provided
        # Generate SBOM and vulnerability data
        sbom_data = self.sbom_generator.generate_sbom()
        vulnerability_data = self.sbom_generator.generate_vulnerability_report()

        # Calculate security metrics
        security_score = self._calculate_security_score(vulnerability_data)
        dependency_health = self._analyze_dependency_health(sbom_data)
        recommendations = self._generate_recommendations(vulnerability_data)

        # Create dashboard content
        dashboard_data = {
            "security_score": security_score,
            "vulnerability_summary": self._summarize_vulnerabilities(vulnerability_data),
            "dependency_health": dependency_health,
            "recommendations": recommendations,
            "generated_at": datetime.now().isoformat(),
        }

        # Format dashboard for GitHub step summary
        dashboard_content = self._format_dashboard(dashboard_data)

        # Add to GitHub step summary
        summary_added = self.github_reporter.add_to_summary(dashboard_content)

        # Create detailed artifact
        artifact_path = self.github_reporter.create_detailed_report_artifact(
            "security_dashboard", dashboard_data
        )

        return {
            "dashboard_data": dashboard_data,
            "summary_added": summary_added,
            "artifact_created": artifact_path,
            "dashboard_content": dashboard_content,
        }

    def _calculate_security_score(self, vulnerability_data: dict[str, Any]) -> dict[str, Any]:
        """Calculate overall security score based on vulnerabilities.

        Args:
            vulnerability_data: Vulnerability report data.

        Returns:
            Security score information including score, trend, and breakdown.
        """
        severity_breakdown = vulnerability_data["summary"]["severity_breakdown"]
        total_vulnerabilities = vulnerability_data["summary"]["total_vulnerabilities"]

        # Calculate weighted score (100 = perfect, 0 = critical issues)
        # Weight vulnerabilities by severity: critical=40, high=20, medium=10, low=5
        severity_weights = {"critical": 40, "high": 20, "medium": 10, "low": 5}

        penalty_score = 0
        for severity, count in severity_breakdown.items():
            if severity in severity_weights:
                penalty_score += count * severity_weights[severity]

        # Calculate base score out of 100
        base_score = max(0, 100 - penalty_score)

        # Additional factors
        vulnerable_deps = vulnerability_data["summary"]["vulnerable_dependencies"]
        total_deps = vulnerability_data["summary"]["total_dependencies"]

        # Adjust for proportion of vulnerable dependencies
        if total_deps > 0:
            vuln_ratio = vulnerable_deps / total_deps
            vulnerability_factor = max(0.5, 1 - vuln_ratio)  # Don't go below 50% of base score
            final_score = int(base_score * vulnerability_factor)
        else:
            final_score = base_score

        # Determine score category
        if final_score >= 90:
            score_category = "excellent"
            score_trend = "🟢"
        elif final_score >= 70:
            score_category = "good"
            score_trend = "🟡"
        elif final_score >= 50:
            score_category = "fair"
            score_trend = "🟠"
        else:
            score_category = "poor"
            score_trend = "🔴"

        return {
            "score": final_score,
            "category": score_category,
            "trend": score_trend,
            "total_vulnerabilities": total_vulnerabilities,
            "severity_breakdown": severity_breakdown,
            "vulnerable_dependencies": vulnerable_deps,
            "total_dependencies": total_deps,
        }

    def _analyze_dependency_health(self, sbom_data: dict[str, Any]) -> dict[str, Any]:
        """Analyze dependency health based on SBOM data.

        Args:
            sbom_data: SBOM data structure.

        Returns:
            Dependency health analysis.
        """
        components = sbom_data.get("components", [])
        total_components = len(components)

        # Analyze license compliance
        licensed_components = len([c for c in components if c.get("licenses")])
        license_compliance = (
            (licensed_components / total_components * 100) if total_components > 0 else 100
        )

        # Analyze vulnerability exposure
        vulnerable_components = 0
        if "vulnerabilities" in sbom_data:
            affected_refs = set()
            for vuln in sbom_data["vulnerabilities"]:
                for affect in vuln.get("affects", []):
                    affected_refs.add(affect.get("ref"))
            vulnerable_components = len(affected_refs)

        vulnerability_exposure = (
            (vulnerable_components / total_components * 100) if total_components > 0 else 0
        )

        # Calculate overall health score
        health_score = int((license_compliance * 0.3) + ((100 - vulnerability_exposure) * 0.7))

        return {
            "health_score": health_score,
            "total_components": total_components,
            "licensed_components": licensed_components,
            "license_compliance_percent": round(license_compliance, 1),
            "vulnerable_components": vulnerable_components,
            "vulnerability_exposure_percent": round(vulnerability_exposure, 1),
            "health_category": self._get_health_category(health_score),
        }

    def _get_health_category(self, score: int) -> str:
        """Get health category based on score.

        Args:
            score: Health score (0-100).

        Returns:
            Health category string.
        """
        if score >= 90:
            return "excellent"
        elif score >= 70:
            return "good"
        elif score >= 50:
            return "fair"
        else:
            return "poor"

    def _generate_recommendations(self, vulnerability_data: dict[str, Any]) -> list[str]:
        """Generate actionable security recommendations.

        Args:
            vulnerability_data: Vulnerability report data.

        Returns:
            List of actionable recommendations.
        """
        recommendations = []
        severity_breakdown = vulnerability_data["summary"]["severity_breakdown"]

        # Critical vulnerabilities
        if severity_breakdown.get("critical", 0) > 0:
            recommendations.append(
                f"🚨 **URGENT**: Address {severity_breakdown['critical']} critical vulnerabilities immediately"
            )

        # High severity vulnerabilities
        if severity_breakdown.get("high", 0) > 0:
            recommendations.append(
                f"⚠️ **HIGH PRIORITY**: Resolve {severity_breakdown['high']} high-severity vulnerabilities"
            )

        # Medium severity vulnerabilities
        if severity_breakdown.get("medium", 0) > 0:
            recommendations.append(
                f"⚡ **MEDIUM PRIORITY**: Plan fixes for {severity_breakdown['medium']} medium-severity vulnerabilities"
            )

        # Specific package recommendations from vulnerability data
        existing_recommendations = vulnerability_data.get("recommendations", [])
        for rec in existing_recommendations[:5]:  # Limit to top 5 specific recommendations
            if rec not in recommendations:
                recommendations.append(f"📦 {rec}")

        # General security recommendations
        if vulnerability_data["summary"]["total_vulnerabilities"] > 0:
            recommendations.append(
                "🔄 **Enable automated security updates** for dependencies where possible"
            )
            recommendations.append("📊 **Set up regular security scans** in your CI/CD pipeline")

        if len(recommendations) == 0:
            recommendations.append(
                "✅ **Excellent security posture!** Continue monitoring for new vulnerabilities"
            )

        return recommendations

    def _summarize_vulnerabilities(
        self, vulnerability_data: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Create vulnerability summary for dashboard table.

        Args:
            vulnerability_data: Vulnerability report data.

        Returns:
            List of vulnerability summary entries for table display.
        """
        severity_breakdown = vulnerability_data["summary"]["severity_breakdown"]

        summary = []
        for severity in ["critical", "high", "medium", "low"]:
            count = severity_breakdown.get(severity, 0)

            # Count how many have fixes available
            fixed_available = 0
            for package in vulnerability_data.get("vulnerable_packages", []):
                for vuln in package.get("vulnerabilities", []):
                    if vuln.get("severity", "").lower() == severity and vuln.get("fix_versions"):
                        fixed_available += 1

            summary.append(
                {
                    "severity": severity.capitalize(),
                    "count": count,
                    "fixed_available": fixed_available,
                    "emoji": self._get_severity_emoji(severity),
                }
            )

        return summary

    def _get_severity_emoji(self, severity: str) -> str:
        """Get emoji for severity level.

        Args:
            severity: Severity level string.

        Returns:
            Appropriate emoji for severity.
        """
        severity_emojis = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢",
        }
        return severity_emojis.get(severity.lower(), "⚪")

    def _format_dashboard(self, dashboard_data: dict[str, Any]) -> str:
        """Format dashboard data as markdown for GitHub step summary.

        Args:
            dashboard_data: Dashboard data to format.

        Returns:
            Formatted markdown dashboard content.
        """
        security_score = dashboard_data["security_score"]
        dependency_health = dashboard_data["dependency_health"]
        vulnerability_summary = dashboard_data["vulnerability_summary"]
        recommendations = dashboard_data["recommendations"]

        # Build markdown dashboard
        dashboard = f"""## 🛡️ Security Dashboard

### Security Score: {security_score["score"]}/100 {security_score["trend"]} ({security_score["category"]})

**Overview**: {security_score["total_vulnerabilities"]} vulnerabilities found across {security_score["vulnerable_dependencies"]}/{security_score["total_dependencies"]} dependencies

### 📊 Vulnerability Summary

| Severity | Count | Fixed Available | Status |
|----------|-------|----------------|--------|"""

        for vuln in vulnerability_summary:
            dashboard += f"\n| {vuln['emoji']} {vuln['severity']} | {vuln['count']} | {vuln['fixed_available']} | {'✅' if vuln['count'] == 0 else '❌'} |"

        dashboard += f"""

### 🏥 Dependency Health: {dependency_health["health_score"]}/100 ({dependency_health["health_category"]})

- **Total Components**: {dependency_health["total_components"]}
- **License Compliance**: {dependency_health["license_compliance_percent"]}% ({dependency_health["licensed_components"]}/{dependency_health["total_components"]})
- **Vulnerability Exposure**: {dependency_health["vulnerability_exposure_percent"]}% ({dependency_health["vulnerable_components"]} vulnerable)

### 🎯 Top Security Recommendations

"""

        for i, rec in enumerate(recommendations[:8], 1):  # Limit to top 8 recommendations
            dashboard += f"{i}. {rec}\n"

        dashboard += f"""
### 📈 Security Metrics

- **Security Score**: {security_score["score"]}/100
- **Health Score**: {dependency_health["health_score"]}/100
- **Total Vulnerabilities**: {security_score["total_vulnerabilities"]}
- **Vulnerable Dependencies**: {security_score["vulnerable_dependencies"]}/{security_score["total_dependencies"]}

---
*Dashboard generated at {dashboard_data["generated_at"]} by Security Dashboard Generator*
"""

        return dashboard

    def generate_security_trend_data(
        self, historical_data: list[dict[str, Any]] | None = None
    ) -> dict[str, Any]:
        """Generate security trend analysis over time.

        Args:
            historical_data: List of historical security dashboard data.

        Returns:
            Security trend analysis.
        """
        if not historical_data:
            historical_data = []

        # Get current data
        dashboard_result = self.generate_security_dashboard()
        current_data = (
            dashboard_result["dashboard_data"] if isinstance(dashboard_result, dict) else {}
        )

        trend_data: dict[str, Any] = {
            "current_score": current_data.get("security_score", {}).get("score", 0),
            "current_vulnerabilities": current_data.get("security_score", {}).get(
                "total_vulnerabilities", 0
            ),
            "historical_scores": [],
            "historical_vulnerabilities": [],
            "trend_analysis": {},
        }

        # Process historical data
        for data_point in historical_data[-10:]:  # Last 10 data points
            if isinstance(data_point, dict) and "security_score" in data_point:
                security_score = data_point["security_score"]
                if isinstance(security_score, dict):
                    trend_data["historical_scores"].append(
                        {
                            "score": security_score.get("score", 0),
                            "timestamp": data_point.get("generated_at", ""),
                        }
                    )
                    trend_data["historical_vulnerabilities"].append(
                        {
                            "count": security_score.get("total_vulnerabilities", 0),
                            "timestamp": data_point.get("generated_at", ""),
                        }
                    )

        # Calculate trends
        if len(trend_data["historical_scores"]) >= 2:
            recent_scores = [point["score"] for point in trend_data["historical_scores"][-3:]]
            score_trend = (
                "improving"
                if recent_scores[-1] > recent_scores[0]
                else "declining"
                if recent_scores[-1] < recent_scores[0]
                else "stable"
            )

            recent_vulns = [
                point["count"] for point in trend_data["historical_vulnerabilities"][-3:]
            ]
            vuln_trend = (
                "decreasing"
                if recent_vulns[-1] < recent_vulns[0]
                else "increasing"
                if recent_vulns[-1] > recent_vulns[0]
                else "stable"
            )

            trend_data["trend_analysis"] = {
                "score_trend": score_trend,
                "vulnerability_trend": vuln_trend,
                "trend_summary": f"Security score is {score_trend}, vulnerabilities are {vuln_trend}",
            }

        return trend_data

    def generate_compliance_report(self, compliance_data: dict[str, Any]) -> str:
        """Generate compliance report from compliance data.

        Args:
            compliance_data: Compliance data including frameworks and controls.

        Returns:
            Formatted compliance report as HTML/text string.
        """
        report_content = "<html><body><h1>Compliance Report</h1>"

        # Add frameworks section
        if "frameworks" in compliance_data:
            report_content += "<h2>Frameworks</h2>"
            for framework, data in compliance_data["frameworks"].items():
                score = data.get("score", 0)
                status = data.get("status", "unknown")
                report_content += (
                    f"<div>Framework: {framework}, Score: {score}, Status: {status}</div>"
                )

        # Add controls section
        if "controls" in compliance_data:
            report_content += "<h2>Controls</h2>"
            for control, status in compliance_data["controls"].items():
                report_content += f"<div>Control: {control}, Status: {status}</div>"

        report_content += "</body></html>"
        return report_content
