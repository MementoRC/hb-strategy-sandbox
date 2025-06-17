"""Tests for security dashboard generator."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from strategy_sandbox.reporting.github_reporter import GitHubReporter
from strategy_sandbox.security.dashboard_generator import SecurityDashboardGenerator
from strategy_sandbox.security.sbom_generator import SBOMGenerator


class TestSecurityDashboardGenerator:
    """Test cases for SecurityDashboardGenerator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_sbom_generator = MagicMock(spec=SBOMGenerator)
        self.mock_github_reporter = MagicMock(spec=GitHubReporter)
        self.dashboard_generator = SecurityDashboardGenerator(
            self.mock_sbom_generator, self.mock_github_reporter
        )

    def test_init(self):
        """Test SecurityDashboardGenerator initialization."""
        assert self.dashboard_generator.sbom_generator == self.mock_sbom_generator
        assert self.dashboard_generator.github_reporter == self.mock_github_reporter

    def test_generate_security_dashboard_basic(self):
        """Test basic security dashboard generation."""
        # Mock SBOM data
        mock_sbom_data = {
            "components": [
                {"name": "package1", "licenses": [{"license": {"name": "MIT"}}]},
                {"name": "package2", "licenses": []},
            ],
            "vulnerabilities": [
                {
                    "id": "CVE-2023-0001",
                    "affects": [{"ref": "pip:package1@1.0.0"}],
                }
            ],
        }

        # Mock vulnerability data
        mock_vulnerability_data = {
            "summary": {
                "total_dependencies": 10,
                "vulnerable_dependencies": 2,
                "total_vulnerabilities": 3,
                "severity_breakdown": {"critical": 1, "high": 1, "medium": 1, "low": 0},
            },
            "vulnerable_packages": [
                {
                    "name": "package1",
                    "vulnerabilities": [
                        {
                            "id": "CVE-2023-0001",
                            "severity": "critical",
                            "fix_versions": ["2.0.0"],
                        }
                    ],
                }
            ],
            "recommendations": ["Update package1 to 2.0.0"],
        }

        self.mock_sbom_generator.generate_sbom.return_value = mock_sbom_data
        self.mock_sbom_generator.generate_vulnerability_report.return_value = (
            mock_vulnerability_data
        )
        self.mock_github_reporter.add_to_summary.return_value = True
        self.mock_github_reporter.create_detailed_report_artifact.return_value = (
            Path(tempfile.gettempdir()) / "artifact.json"
        )

        result = self.dashboard_generator.generate_security_dashboard()

        # Verify result structure
        assert "dashboard_data" in result
        assert "summary_added" in result
        assert "artifact_created" in result
        assert "dashboard_content" in result

        # Verify dashboard data
        dashboard_data = result["dashboard_data"]
        assert "security_score" in dashboard_data
        assert "vulnerability_summary" in dashboard_data
        assert "dependency_health" in dashboard_data
        assert "recommendations" in dashboard_data
        assert "generated_at" in dashboard_data

        # Verify method calls
        self.mock_sbom_generator.generate_sbom.assert_called_once()
        self.mock_sbom_generator.generate_vulnerability_report.assert_called_once()
        self.mock_github_reporter.add_to_summary.assert_called_once()
        self.mock_github_reporter.create_detailed_report_artifact.assert_called_once()

    def test_calculate_security_score_no_vulnerabilities(self):
        """Test security score calculation with no vulnerabilities."""
        vulnerability_data = {
            "summary": {
                "total_dependencies": 10,
                "vulnerable_dependencies": 0,
                "total_vulnerabilities": 0,
                "severity_breakdown": {"critical": 0, "high": 0, "medium": 0, "low": 0},
            }
        }

        score_data = self.dashboard_generator._calculate_security_score(vulnerability_data)

        assert score_data["score"] == 100
        assert score_data["category"] == "excellent"
        assert score_data["trend"] == "🟢"
        assert score_data["total_vulnerabilities"] == 0

    def test_calculate_security_score_critical_vulnerabilities(self):
        """Test security score calculation with critical vulnerabilities."""
        vulnerability_data = {
            "summary": {
                "total_dependencies": 10,
                "vulnerable_dependencies": 3,
                "total_vulnerabilities": 5,
                "severity_breakdown": {"critical": 2, "high": 1, "medium": 2, "low": 0},
            }
        }

        score_data = self.dashboard_generator._calculate_security_score(vulnerability_data)

        # 2*40 + 1*20 + 2*10 = 120 penalty, but capped and adjusted for vuln ratio
        assert score_data["score"] < 50  # Should be in poor category
        assert score_data["category"] == "poor"
        assert score_data["trend"] == "🔴"
        assert score_data["total_vulnerabilities"] == 5

    def test_calculate_security_score_medium_risk(self):
        """Test security score calculation with medium risk profile."""
        vulnerability_data = {
            "summary": {
                "total_dependencies": 20,
                "vulnerable_dependencies": 2,
                "total_vulnerabilities": 3,
                "severity_breakdown": {"critical": 0, "high": 1, "medium": 2, "low": 0},
            }
        }

        score_data = self.dashboard_generator._calculate_security_score(vulnerability_data)

        # 0*40 + 1*20 + 2*10 = 40 penalty, base_score = 60
        # With vuln_ratio = 2/20 = 0.1, vulnerability_factor = 0.9
        # final_score = 60 * 0.9 = 54
        assert 50 <= score_data["score"] <= 70
        assert score_data["category"] in ["good", "fair"]
        assert score_data["trend"] in ["🟡", "🟠"]

    def test_analyze_dependency_health_perfect(self):
        """Test dependency health analysis with perfect health."""
        sbom_data = {
            "components": [
                {"name": "package1", "licenses": [{"license": {"name": "MIT"}}]},
                {"name": "package2", "licenses": [{"license": {"name": "Apache-2.0"}}]},
            ],
            "vulnerabilities": [],
        }

        health_data = self.dashboard_generator._analyze_dependency_health(sbom_data)

        assert health_data["health_score"] == 100
        assert health_data["total_components"] == 2
        assert health_data["licensed_components"] == 2
        assert health_data["license_compliance_percent"] == 100.0
        assert health_data["vulnerable_components"] == 0
        assert health_data["vulnerability_exposure_percent"] == 0.0
        assert health_data["health_category"] == "excellent"

    def test_analyze_dependency_health_poor(self):
        """Test dependency health analysis with poor health."""
        sbom_data = {
            "components": [
                {"name": "package1", "licenses": []},
                {"name": "package2", "licenses": []},
                {"name": "package3", "licenses": [{"license": {"name": "MIT"}}]},
            ],
            "vulnerabilities": [
                {"affects": [{"ref": "pip:package1@1.0.0"}]},
                {"affects": [{"ref": "pip:package2@1.0.0"}]},
            ],
        }

        health_data = self.dashboard_generator._analyze_dependency_health(sbom_data)

        assert health_data["health_score"] < 50
        assert health_data["total_components"] == 3
        assert health_data["licensed_components"] == 1
        assert health_data["license_compliance_percent"] == pytest.approx(33.3, rel=0.1)
        assert health_data["vulnerable_components"] == 2
        assert health_data["vulnerability_exposure_percent"] == pytest.approx(66.7, rel=0.1)
        assert health_data["health_category"] in ["poor", "fair"]

    def test_get_health_category(self):
        """Test health category determination."""
        assert self.dashboard_generator._get_health_category(95) == "excellent"
        assert self.dashboard_generator._get_health_category(80) == "good"
        assert self.dashboard_generator._get_health_category(60) == "fair"
        assert self.dashboard_generator._get_health_category(30) == "poor"

    def test_generate_recommendations_no_vulnerabilities(self):
        """Test recommendation generation with no vulnerabilities."""
        vulnerability_data = {
            "summary": {
                "total_vulnerabilities": 0,
                "severity_breakdown": {"critical": 0, "high": 0, "medium": 0, "low": 0},
            },
            "recommendations": [],
        }

        recommendations = self.dashboard_generator._generate_recommendations(vulnerability_data)

        assert len(recommendations) == 1
        assert "Excellent security posture" in recommendations[0]

    def test_generate_recommendations_with_vulnerabilities(self):
        """Test recommendation generation with various vulnerability severities."""
        vulnerability_data = {
            "summary": {
                "total_vulnerabilities": 5,
                "severity_breakdown": {"critical": 1, "high": 2, "medium": 2, "low": 0},
            },
            "recommendations": ["Update package1 to 2.0.0", "Update package2 to 1.5.0"],
        }

        recommendations = self.dashboard_generator._generate_recommendations(vulnerability_data)

        # Check for critical, high, medium recommendations
        critical_rec = next(
            (r for r in recommendations if "URGENT" in r and "1 critical" in r), None
        )
        high_rec = next(
            (r for r in recommendations if "HIGH PRIORITY" in r and "2 high-severity" in r), None
        )
        medium_rec = next(
            (r for r in recommendations if "MEDIUM PRIORITY" in r and "2 medium-severity" in r),
            None,
        )

        assert critical_rec is not None
        assert high_rec is not None
        assert medium_rec is not None

        # Check for specific package recommendations
        package_recs = [r for r in recommendations if r.startswith("📦")]
        assert len(package_recs) == 2

    def test_summarize_vulnerabilities(self):
        """Test vulnerability summary creation."""
        vulnerability_data = {
            "summary": {"severity_breakdown": {"critical": 1, "high": 2, "medium": 0, "low": 1}},
            "vulnerable_packages": [
                {
                    "vulnerabilities": [
                        {"severity": "critical", "fix_versions": ["2.0.0"]},
                        {"severity": "high", "fix_versions": []},
                        {"severity": "high", "fix_versions": ["1.5.0"]},
                        {"severity": "low", "fix_versions": ["1.1.0"]},
                    ]
                }
            ],
        }

        summary = self.dashboard_generator._summarize_vulnerabilities(vulnerability_data)

        assert len(summary) == 4  # critical, high, medium, low

        # Find critical entry
        critical_entry = next(s for s in summary if s["severity"] == "Critical")
        assert critical_entry["count"] == 1
        assert critical_entry["fixed_available"] == 1
        assert critical_entry["emoji"] == "🔴"

        # Find high entry
        high_entry = next(s for s in summary if s["severity"] == "High")
        assert high_entry["count"] == 2
        assert high_entry["fixed_available"] == 1  # Only one has fix_versions

        # Find medium entry
        medium_entry = next(s for s in summary if s["severity"] == "Medium")
        assert medium_entry["count"] == 0
        assert medium_entry["fixed_available"] == 0

    def test_get_severity_emoji(self):
        """Test severity emoji mapping."""
        assert self.dashboard_generator._get_severity_emoji("critical") == "🔴"
        assert self.dashboard_generator._get_severity_emoji("high") == "🟠"
        assert self.dashboard_generator._get_severity_emoji("medium") == "🟡"
        assert self.dashboard_generator._get_severity_emoji("low") == "🟢"
        assert self.dashboard_generator._get_severity_emoji("unknown") == "⚪"

    def test_format_dashboard(self):
        """Test dashboard markdown formatting."""
        dashboard_data = {
            "security_score": {
                "score": 75,
                "category": "good",
                "trend": "🟡",
                "total_vulnerabilities": 3,
                "vulnerable_dependencies": 2,
                "total_dependencies": 10,
            },
            "dependency_health": {
                "health_score": 80,
                "health_category": "good",
                "total_components": 10,
                "license_compliance_percent": 90.0,
                "licensed_components": 9,
                "vulnerability_exposure_percent": 20.0,
                "vulnerable_components": 2,
            },
            "vulnerability_summary": [
                {"severity": "Critical", "count": 1, "fixed_available": 1, "emoji": "🔴"},
                {"severity": "High", "count": 2, "fixed_available": 0, "emoji": "🟠"},
            ],
            "recommendations": ["Update package1", "Enable automated updates"],
            "generated_at": "2023-01-01T12:00:00",
        }

        dashboard_content = self.dashboard_generator._format_dashboard(dashboard_data)

        # Check key sections are present
        assert "🛡️ Security Dashboard" in dashboard_content
        assert "Security Score: 75/100 🟡 (good)" in dashboard_content
        assert "📊 Vulnerability Summary" in dashboard_content
        assert "🏥 Dependency Health: 80/100 (good)" in dashboard_content
        assert "🎯 Top Security Recommendations" in dashboard_content
        assert "📈 Security Metrics" in dashboard_content

        # Check vulnerability table
        assert "🔴 Critical | 1 | 1 | ❌" in dashboard_content
        assert "🟠 High | 2 | 0 | ❌" in dashboard_content

        # Check recommendations
        assert "1. Update package1" in dashboard_content
        assert "2. Enable automated updates" in dashboard_content

    def test_generate_security_trend_data_no_history(self):
        """Test security trend generation with no historical data."""
        # Mock current dashboard data
        current_dashboard_data = {
            "dashboard_data": {
                "security_score": {"score": 85, "total_vulnerabilities": 2},
                "generated_at": "2023-01-01T12:00:00",
            }
        }

        with patch.object(
            self.dashboard_generator,
            "generate_security_dashboard",
            return_value=current_dashboard_data,
        ):
            trend_data = self.dashboard_generator.generate_security_trend_data()

        assert trend_data["current_score"] == 85
        assert trend_data["current_vulnerabilities"] == 2
        assert trend_data["historical_scores"] == []
        assert trend_data["historical_vulnerabilities"] == []
        assert trend_data["trend_analysis"] == {}

    def test_generate_security_trend_data_with_history(self):
        """Test security trend generation with historical data."""
        # Mock current dashboard data
        current_dashboard_data = {
            "dashboard_data": {
                "security_score": {"score": 85, "total_vulnerabilities": 2},
                "generated_at": "2023-01-03T12:00:00",
            }
        }

        # Mock historical data
        historical_data = [
            {
                "security_score": {"score": 70, "total_vulnerabilities": 5},
                "generated_at": "2023-01-01T12:00:00",
            },
            {
                "security_score": {"score": 75, "total_vulnerabilities": 4},
                "generated_at": "2023-01-02T12:00:00",
            },
        ]

        with patch.object(
            self.dashboard_generator,
            "generate_security_dashboard",
            return_value=current_dashboard_data,
        ):
            trend_data = self.dashboard_generator.generate_security_trend_data(historical_data)

        assert trend_data["current_score"] == 85
        assert trend_data["current_vulnerabilities"] == 2
        assert len(trend_data["historical_scores"]) == 2
        assert len(trend_data["historical_vulnerabilities"]) == 2

        # Check trend analysis
        assert trend_data["trend_analysis"]["score_trend"] == "improving"  # 70 -> 85
        assert trend_data["trend_analysis"]["vulnerability_trend"] == "decreasing"  # 5 -> 2

    @patch("tempfile.mkdtemp")
    def test_integration_with_real_components(self, mock_mkdtemp):
        """Test integration with real SBOMGenerator and GitHubReporter components."""
        # Create temporary directory for test
        temp_dir = tempfile.mkdtemp()
        mock_mkdtemp.return_value = temp_dir

        try:
            # Create real GitHubReporter (but without GitHub environment)
            github_reporter = GitHubReporter(artifact_path=temp_dir)

            # Create mock SBOMGenerator with realistic data
            mock_sbom = MagicMock(spec=SBOMGenerator)
            mock_sbom.generate_sbom.return_value = {
                "components": [
                    {"name": "requests", "licenses": [{"license": {"name": "Apache-2.0"}}]},
                    {"name": "urllib3", "licenses": []},
                ],
                "vulnerabilities": [],
            }
            mock_sbom.generate_vulnerability_report.return_value = {
                "summary": {
                    "total_dependencies": 2,
                    "vulnerable_dependencies": 0,
                    "total_vulnerabilities": 0,
                    "severity_breakdown": {"critical": 0, "high": 0, "medium": 0, "low": 0},
                },
                "vulnerable_packages": [],
                "recommendations": [],
            }

            # Create dashboard generator with real reporter
            dashboard_gen = SecurityDashboardGenerator(mock_sbom, github_reporter)

            # Generate dashboard
            result = dashboard_gen.generate_security_dashboard()

            # Verify basic structure
            assert result["dashboard_data"]["security_score"]["score"] == 100
            assert result["summary_added"] is False  # No GITHUB_STEP_SUMMARY set
            assert result["artifact_created"] is not None  # Artifact should be created

            # Verify artifact was created
            artifact_path = result["artifact_created"]
            assert artifact_path.exists()

            # Load and verify artifact content
            with open(artifact_path, encoding="utf-8") as f:
                artifact_data = json.load(f)

            assert artifact_data["report_type"] == "security_dashboard"
            assert "data" in artifact_data
            assert "github_context" in artifact_data

        finally:
            # Cleanup
            import shutil

            shutil.rmtree(temp_dir, ignore_errors=True)
