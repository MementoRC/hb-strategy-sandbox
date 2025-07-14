"""Test suite for the security models module."""

from datetime import datetime

import pytest

from strategy_sandbox.security.models import DependencyInfo, SecurityMetrics, VulnerabilityInfo


class TestVulnerabilityInfo:
    """Test cases for the VulnerabilityInfo class."""

    @pytest.fixture
    def sample_vulnerability(self):
        """Create a sample vulnerability for testing."""
        return VulnerabilityInfo(
            id="CVE-2023-1234",
            package_name="test-package",
            package_version="1.0.0",
            severity="high",
            description="Test vulnerability description",
            fix_versions=["1.0.1", "1.1.0"],
            aliases=["GHSA-1234", "PYSEC-2023-1"],
            advisory_url="https://example.com/advisory",
            metadata={"source": "test"},
        )

    def test_vulnerability_creation(self, sample_vulnerability):
        """Test basic vulnerability creation."""
        vuln = sample_vulnerability
        assert vuln.id == "CVE-2023-1234"
        assert vuln.package_name == "test-package"
        assert vuln.package_version == "1.0.0"
        assert vuln.severity == "high"
        assert vuln.description == "Test vulnerability description"
        assert vuln.fix_versions == ["1.0.1", "1.1.0"]
        assert vuln.aliases == ["GHSA-1234", "PYSEC-2023-1"]
        assert vuln.advisory_url == "https://example.com/advisory"
        assert vuln.metadata == {"source": "test"}

    def test_vulnerability_creation_minimal(self):
        """Test vulnerability creation with minimal required fields."""
        vuln = VulnerabilityInfo(
            id="CVE-2023-5678",
            package_name="minimal-package",
            package_version="2.0.0",
            severity="medium",
            description="Minimal vulnerability",
        )
        assert vuln.id == "CVE-2023-5678"
        assert vuln.fix_versions == []
        assert vuln.aliases == []
        assert vuln.advisory_url is None
        assert vuln.metadata == {}
        assert isinstance(vuln.timestamp, float)

    def test_vulnerability_to_dict(self, sample_vulnerability):
        """Test vulnerability to_dict method."""
        vuln_dict = sample_vulnerability.to_dict()

        assert vuln_dict["id"] == "CVE-2023-1234"
        assert vuln_dict["package_name"] == "test-package"
        assert vuln_dict["package_version"] == "1.0.0"
        assert vuln_dict["severity"] == "high"
        assert vuln_dict["description"] == "Test vulnerability description"
        assert vuln_dict["fix_versions"] == ["1.0.1", "1.1.0"]
        assert vuln_dict["aliases"] == ["GHSA-1234", "PYSEC-2023-1"]
        assert vuln_dict["advisory_url"] == "https://example.com/advisory"
        assert vuln_dict["metadata"] == {"source": "test"}
        assert "timestamp" in vuln_dict

    def test_vulnerability_from_dict(self, sample_vulnerability):
        """Test vulnerability from_dict method."""
        vuln_dict = sample_vulnerability.to_dict()
        recreated_vuln = VulnerabilityInfo.from_dict(vuln_dict)

        assert recreated_vuln.id == sample_vulnerability.id
        assert recreated_vuln.package_name == sample_vulnerability.package_name
        assert recreated_vuln.package_version == sample_vulnerability.package_version
        assert recreated_vuln.severity == sample_vulnerability.severity
        assert recreated_vuln.description == sample_vulnerability.description
        assert recreated_vuln.fix_versions == sample_vulnerability.fix_versions
        assert recreated_vuln.aliases == sample_vulnerability.aliases
        assert recreated_vuln.advisory_url == sample_vulnerability.advisory_url
        assert recreated_vuln.metadata == sample_vulnerability.metadata

    def test_vulnerability_from_dict_minimal(self):
        """Test vulnerability from_dict with minimal data."""
        minimal_dict = {
            "id": "CVE-2023-9999",
            "package_name": "minimal",
            "package_version": "1.0.0",
            "severity": "low",
            "description": "Minimal test",
        }

        vuln = VulnerabilityInfo.from_dict(minimal_dict)
        assert vuln.id == "CVE-2023-9999"
        assert vuln.fix_versions == []
        assert vuln.aliases == []
        assert vuln.advisory_url is None
        assert vuln.metadata == {}


class TestDependencyInfo:
    """Test cases for the DependencyInfo class."""

    @pytest.fixture
    def sample_vulnerabilities(self):
        """Create sample vulnerabilities for testing."""
        return [
            VulnerabilityInfo(
                id="CVE-2023-1",
                package_name="test-dep",
                package_version="1.0.0",
                severity="high",
                description="High severity vuln",
            ),
            VulnerabilityInfo(
                id="CVE-2023-2",
                package_name="test-dep",
                package_version="1.0.0",
                severity="medium",
                description="Medium severity vuln",
            ),
            VulnerabilityInfo(
                id="CVE-2023-3",
                package_name="test-dep",
                package_version="1.0.0",
                severity="low",
                description="Low severity vuln",
            ),
        ]

    @pytest.fixture
    def sample_dependency(self, sample_vulnerabilities):
        """Create a sample dependency for testing."""
        return DependencyInfo(
            name="test-dependency",
            version="1.0.0",
            package_manager="pip",
            source="https://pypi.org/simple",
            license="MIT",
            vulnerabilities=sample_vulnerabilities,
            dependencies=["sub-dep-1", "sub-dep-2"],
            metadata={"installed_by": "requirements.txt"},
        )

    def test_dependency_creation(self, sample_dependency):
        """Test basic dependency creation."""
        dep = sample_dependency
        assert dep.name == "test-dependency"
        assert dep.version == "1.0.0"
        assert dep.package_manager == "pip"
        assert dep.source == "https://pypi.org/simple"
        assert dep.license == "MIT"
        assert len(dep.vulnerabilities) == 3
        assert dep.dependencies == ["sub-dep-1", "sub-dep-2"]
        assert dep.metadata == {"installed_by": "requirements.txt"}

    def test_dependency_creation_minimal(self):
        """Test dependency creation with minimal required fields."""
        dep = DependencyInfo(name="minimal-dep", version="2.0.0", package_manager="conda")
        assert dep.name == "minimal-dep"
        assert dep.version == "2.0.0"
        assert dep.package_manager == "conda"
        assert dep.source is None
        assert dep.license is None
        assert dep.vulnerabilities == []
        assert dep.dependencies == []
        assert dep.metadata == {}

    def test_has_vulnerabilities_property(self, sample_dependency):
        """Test has_vulnerabilities property."""
        assert sample_dependency.has_vulnerabilities is True

        clean_dep = DependencyInfo(name="clean-dep", version="1.0.0", package_manager="pip")
        assert clean_dep.has_vulnerabilities is False

    def test_vulnerability_count_by_severity(self, sample_dependency):
        """Test vulnerability_count_by_severity property."""
        counts = sample_dependency.vulnerability_count_by_severity

        assert counts["high"] == 1
        assert counts["medium"] == 1
        assert counts["low"] == 1
        assert counts["critical"] == 0

    def test_vulnerability_count_by_severity_empty(self):
        """Test vulnerability_count_by_severity with no vulnerabilities."""
        dep = DependencyInfo(name="clean-dep", version="1.0.0", package_manager="pip")
        counts = dep.vulnerability_count_by_severity

        assert counts["high"] == 0
        assert counts["medium"] == 0
        assert counts["low"] == 0
        assert counts["critical"] == 0

    def test_vulnerability_count_by_severity_unknown_severity(self):
        """Test vulnerability_count_by_severity with unknown severity levels."""
        vuln = VulnerabilityInfo(
            id="CVE-2023-999",
            package_name="test-dep",
            package_version="1.0.0",
            severity="unknown",  # Unknown severity
            description="Unknown severity vuln",
        )

        dep = DependencyInfo(
            name="test-dep", version="1.0.0", package_manager="pip", vulnerabilities=[vuln]
        )

        counts = dep.vulnerability_count_by_severity
        # Unknown severity should be ignored
        assert counts["high"] == 0
        assert counts["medium"] == 0
        assert counts["low"] == 0
        assert counts["critical"] == 0

    def test_dependency_to_dict(self, sample_dependency):
        """Test dependency to_dict method."""
        dep_dict = sample_dependency.to_dict()

        assert dep_dict["name"] == "test-dependency"
        assert dep_dict["version"] == "1.0.0"
        assert dep_dict["package_manager"] == "pip"
        assert dep_dict["source"] == "https://pypi.org/simple"
        assert dep_dict["license"] == "MIT"
        assert len(dep_dict["vulnerabilities"]) == 3
        assert dep_dict["dependencies"] == ["sub-dep-1", "sub-dep-2"]
        assert dep_dict["metadata"] == {"installed_by": "requirements.txt"}
        assert "vulnerability_summary" in dep_dict

    def test_dependency_from_dict(self, sample_dependency):
        """Test dependency from_dict method."""
        dep_dict = sample_dependency.to_dict()
        recreated_dep = DependencyInfo.from_dict(dep_dict)

        assert recreated_dep.name == sample_dependency.name
        assert recreated_dep.version == sample_dependency.version
        assert recreated_dep.package_manager == sample_dependency.package_manager
        assert recreated_dep.source == sample_dependency.source
        assert recreated_dep.license == sample_dependency.license
        assert len(recreated_dep.vulnerabilities) == len(sample_dependency.vulnerabilities)
        assert recreated_dep.dependencies == sample_dependency.dependencies
        assert recreated_dep.metadata == sample_dependency.metadata

    def test_dependency_from_dict_minimal(self):
        """Test dependency from_dict with minimal data."""
        minimal_dict = {"name": "minimal-dep", "version": "1.0.0", "package_manager": "pip"}

        dep = DependencyInfo.from_dict(minimal_dict)
        assert dep.name == "minimal-dep"
        assert dep.version == "1.0.0"
        assert dep.package_manager == "pip"
        assert dep.source is None
        assert dep.license is None
        assert dep.vulnerabilities == []
        assert dep.dependencies == []
        assert dep.metadata == {}


class TestSecurityMetrics:
    """Test cases for the SecurityMetrics class."""

    @pytest.fixture
    def sample_dependencies(self):
        """Create sample dependencies for testing."""
        vuln1 = VulnerabilityInfo(
            id="CVE-2023-1",
            package_name="dep1",
            package_version="1.0.0",
            severity="high",
            description="High vuln",
        )

        vuln2 = VulnerabilityInfo(
            id="CVE-2023-2",
            package_name="dep2",
            package_version="2.0.0",
            severity="medium",
            description="Medium vuln",
        )

        dep1 = DependencyInfo(
            name="vulnerable-dep-1", version="1.0.0", package_manager="pip", vulnerabilities=[vuln1]
        )

        dep2 = DependencyInfo(
            name="vulnerable-dep-2",
            version="2.0.0",
            package_manager="conda",
            vulnerabilities=[vuln2],
        )

        dep3 = DependencyInfo(name="clean-dep", version="3.0.0", package_manager="pip")

        return [dep1, dep2, dep3]

    @pytest.fixture
    def sample_metrics(self, sample_dependencies):
        """Create sample security metrics for testing."""
        return SecurityMetrics(
            build_id="test-build-123",
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            dependencies=sample_dependencies,
            scan_config={"tool": "test-scanner", "version": "1.0"},
            environment={"python": "3.12", "os": "linux"},
            scan_duration=45.5,
        )

    def test_security_metrics_creation(self, sample_metrics):
        """Test basic security metrics creation."""
        metrics = sample_metrics
        assert metrics.build_id == "test-build-123"
        assert metrics.timestamp == datetime(2023, 1, 1, 12, 0, 0)
        assert len(metrics.dependencies) == 3
        assert metrics.scan_config == {"tool": "test-scanner", "version": "1.0"}
        assert metrics.environment == {"python": "3.12", "os": "linux"}
        assert metrics.scan_duration == 45.5

    def test_security_metrics_creation_minimal(self):
        """Test security metrics creation with minimal fields."""
        metrics = SecurityMetrics(build_id="minimal-build", timestamp=datetime.now())
        assert metrics.build_id == "minimal-build"
        assert metrics.dependencies == []
        assert metrics.scan_config == {}
        assert metrics.environment == {}
        assert metrics.scan_duration is None

    def test_add_dependency(self, sample_metrics):
        """Test add_dependency method."""
        new_dep = DependencyInfo(name="new-dep", version="1.0.0", package_manager="pip")

        initial_count = len(sample_metrics.dependencies)
        sample_metrics.add_dependency(new_dep)

        assert len(sample_metrics.dependencies) == initial_count + 1
        assert sample_metrics.dependencies[-1] == new_dep

    def test_get_dependency(self, sample_metrics):
        """Test get_dependency method."""
        dep = sample_metrics.get_dependency("vulnerable-dep-1")
        assert dep is not None
        assert dep.name == "vulnerable-dep-1"

        nonexistent_dep = sample_metrics.get_dependency("nonexistent-dep")
        assert nonexistent_dep is None

    def test_get_vulnerable_dependencies(self, sample_metrics):
        """Test get_vulnerable_dependencies method."""
        vulnerable_deps = sample_metrics.get_vulnerable_dependencies()

        assert len(vulnerable_deps) == 2
        vulnerable_names = [dep.name for dep in vulnerable_deps]
        assert "vulnerable-dep-1" in vulnerable_names
        assert "vulnerable-dep-2" in vulnerable_names
        assert "clean-dep" not in vulnerable_names

    def test_calculate_summary_stats(self, sample_metrics):
        """Test calculate_summary_stats method."""
        stats = sample_metrics.calculate_summary_stats()

        assert stats["total_dependencies"] == 3
        assert stats["vulnerable_dependencies"] == 2
        assert stats["vulnerability_free_dependencies"] == 1
        assert stats["total_vulnerabilities"] == 2
        assert stats["vulnerabilities_by_severity"]["high"] == 1
        assert stats["vulnerabilities_by_severity"]["medium"] == 1
        assert stats["vulnerabilities_by_severity"]["low"] == 0
        assert stats["vulnerabilities_by_severity"]["critical"] == 0
        assert stats["package_managers"]["pip"] == 2
        assert stats["package_managers"]["conda"] == 1
        assert stats["vulnerability_rate"] == 66.67  # 2/3 * 100

    def test_calculate_summary_stats_empty(self):
        """Test calculate_summary_stats with no dependencies."""
        metrics = SecurityMetrics(build_id="empty-build", timestamp=datetime.now())

        stats = metrics.calculate_summary_stats()

        assert stats["total_dependencies"] == 0
        assert stats["vulnerable_dependencies"] == 0
        assert stats["vulnerability_free_dependencies"] == 0
        assert stats["total_vulnerabilities"] == 0
        assert stats["vulnerability_rate"] == 0

    def test_security_metrics_to_dict(self, sample_metrics):
        """Test security metrics to_dict method."""
        metrics_dict = sample_metrics.to_dict()

        assert metrics_dict["build_id"] == "test-build-123"
        assert metrics_dict["timestamp"] == "2023-01-01T12:00:00"
        assert len(metrics_dict["dependencies"]) == 3
        assert metrics_dict["scan_config"] == {"tool": "test-scanner", "version": "1.0"}
        assert metrics_dict["environment"] == {"python": "3.12", "os": "linux"}
        assert metrics_dict["scan_duration"] == 45.5
        assert "summary_stats" in metrics_dict

    def test_security_metrics_from_dict(self, sample_metrics):
        """Test security metrics from_dict method."""
        metrics_dict = sample_metrics.to_dict()
        recreated_metrics = SecurityMetrics.from_dict(metrics_dict)

        assert recreated_metrics.build_id == sample_metrics.build_id
        assert recreated_metrics.timestamp == sample_metrics.timestamp
        assert len(recreated_metrics.dependencies) == len(sample_metrics.dependencies)
        assert recreated_metrics.scan_config == sample_metrics.scan_config
        assert recreated_metrics.environment == sample_metrics.environment
        assert recreated_metrics.scan_duration == sample_metrics.scan_duration

    def test_security_metrics_from_dict_minimal(self):
        """Test security metrics from_dict with minimal data."""
        minimal_dict = {"build_id": "minimal-build", "timestamp": "2023-01-01T12:00:00"}

        metrics = SecurityMetrics.from_dict(minimal_dict)
        assert metrics.build_id == "minimal-build"
        assert metrics.timestamp == datetime(2023, 1, 1, 12, 0, 0)
        assert metrics.dependencies == []
        assert metrics.scan_config == {}
        assert metrics.environment == {}
        assert metrics.scan_duration is None
