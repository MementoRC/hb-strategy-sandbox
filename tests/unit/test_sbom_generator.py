"""Tests for the SBOM generator functionality."""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from strategy_sandbox.security.analyzer import DependencyAnalyzer
from strategy_sandbox.security.models import DependencyInfo, VulnerabilityInfo
from strategy_sandbox.security.sbom_generator import SBOMGenerator


class TestSBOMGenerator:
    """Test suite for the SBOMGenerator class."""

    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies for testing."""
        vuln1 = VulnerabilityInfo(
            id="CVE-2023-12345",
            package_name="requests",
            package_version="2.28.0",
            severity="medium",
            description="Test vulnerability in requests",
            fix_versions=["2.31.0"],
            aliases=["GHSA-test-1234"],
            advisory_url="https://example.com/advisory",
        )

        dep1 = DependencyInfo(
            name="requests",
            version="2.28.0",
            package_manager="pip",
            source="https://pypi.org/simple/requests/",
            license="Apache-2.0",
            vulnerabilities=[vuln1],
            dependencies=["urllib3", "certifi"],
        )

        dep2 = DependencyInfo(
            name="numpy",
            version="1.24.0",
            package_manager="pip",
            license="BSD-3-Clause",
            vulnerabilities=[],
            dependencies=[],
        )

        dep3 = DependencyInfo(
            name="pytest",
            version="7.4.0",
            package_manager="pip",
            license="MIT",
            vulnerabilities=[],
            dependencies=["pluggy", "packaging"],
        )

        return [dep1, dep2, dep3]

    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / "pyproject.toml").write_text("[project]\nname = 'test-project'")
            yield project_path

    @pytest.fixture
    def mock_analyzer(self, temp_project, mock_dependencies):
        """Create a mock dependency analyzer."""
        analyzer = Mock(spec=DependencyAnalyzer)
        analyzer.project_path = temp_project
        analyzer.scan_dependencies.return_value = mock_dependencies
        return analyzer

    @pytest.fixture
    def sbom_generator(self, mock_analyzer):
        """Create an SBOM generator instance for testing."""
        return SBOMGenerator(mock_analyzer)

    def test_init_with_analyzer(self, mock_analyzer):
        """Test SBOM generator initialization with provided analyzer."""
        generator = SBOMGenerator(mock_analyzer)
        assert generator.dependency_analyzer == mock_analyzer
        assert generator.supported_formats == ["cyclonedx", "spdx"]

    def test_init_without_analyzer(self):
        """Test SBOM generator initialization without analyzer."""
        generator = SBOMGenerator()
        assert isinstance(generator.dependency_analyzer, DependencyAnalyzer)

    def test_generate_cyclonedx_json(self, sbom_generator):
        """Test CycloneDX JSON SBOM generation."""
        sbom = sbom_generator.generate_sbom(
            output_format="cyclonedx",
            output_type="json",
            include_dev_dependencies=False,  # Explicitly exclude dev dependencies
        )

        # Validate CycloneDX structure
        assert sbom["bomFormat"] == "CycloneDX"
        assert sbom["specVersion"] == "1.4"
        assert "serialNumber" in sbom
        assert sbom["version"] == 1

        # Check metadata
        assert "metadata" in sbom
        assert "timestamp" in sbom["metadata"]
        assert sbom["metadata"]["component"]["type"] == "application"

        # Check components
        assert "components" in sbom
        assert len(sbom["components"]) == 2  # requests and numpy (pytest filtered as dev)

        # Validate component structure
        component = sbom["components"][0]
        assert component["type"] == "library"
        assert "bom-ref" in component
        assert component["name"] in ["requests", "numpy"]
        assert "version" in component
        assert "purl" in component

        # Check vulnerabilities
        assert "vulnerabilities" in sbom
        assert len(sbom["vulnerabilities"]) == 1  # Only requests has vulnerability

        vuln = sbom["vulnerabilities"][0]
        assert vuln["id"] == "CVE-2023-12345"
        assert vuln["ratings"][0]["severity"] == "MEDIUM"

    def test_generate_cyclonedx_include_dev_dependencies(self, sbom_generator):
        """Test CycloneDX generation including dev dependencies."""
        sbom = sbom_generator.generate_sbom(
            output_format="cyclonedx", output_type="json", include_dev_dependencies=True
        )

        # Should include all 3 components including pytest
        assert len(sbom["components"]) == 3

    def test_generate_cyclonedx_exclude_vulnerabilities(self, sbom_generator):
        """Test CycloneDX generation without vulnerabilities."""
        sbom = sbom_generator.generate_sbom(
            output_format="cyclonedx", output_type="json", include_vulnerabilities=False
        )

        # Should not have vulnerabilities section
        assert "vulnerabilities" not in sbom

    def test_generate_spdx_json(self, sbom_generator):
        """Test SPDX JSON SBOM generation."""
        sbom = sbom_generator.generate_sbom(
            output_format="spdx",
            output_type="json",
            include_dev_dependencies=False,  # Explicitly exclude dev dependencies
        )

        # Validate SPDX structure
        assert sbom["spdxVersion"] == "SPDX-2.3"
        assert sbom["dataLicense"] == "CC0-1.0"
        assert "SPDXID" in sbom
        assert "documentNamespace" in sbom

        # Check creation info
        assert "creationInfo" in sbom
        assert "created" in sbom["creationInfo"]
        assert len(sbom["creationInfo"]["creators"]) == 1

        # Check packages (root + dependencies)
        assert "packages" in sbom
        assert len(sbom["packages"]) == 3  # root + requests + numpy (pytest filtered)

        # Validate package structure
        dep_packages = [pkg for pkg in sbom["packages"] if pkg["SPDXID"] != "SPDXRef-Package-Root"]
        package = dep_packages[0]
        assert package["name"] in ["requests", "numpy"]
        assert "versionInfo" in package
        assert package["filesAnalyzed"] is False

        # Check relationships
        assert "relationships" in sbom
        assert len(sbom["relationships"]) >= 2  # At least root -> deps

        # Check annotations for vulnerabilities
        assert "annotations" in sbom
        vuln_annotations = [
            ann for ann in sbom["annotations"] if "Vulnerability:" in ann["annotationComment"]
        ]
        assert len(vuln_annotations) == 1  # Only requests has vulnerability

    def test_generate_purl(self, sbom_generator, mock_dependencies):
        """Test Package URL generation."""
        requests_dep = mock_dependencies[0]
        purl = sbom_generator._generate_purl(requests_dep)
        assert purl == "pkg:pypi/requests@2.28.0"

        # Test conda package
        conda_dep = DependencyInfo(name="python", version="3.11.0", package_manager="conda")
        purl = sbom_generator._generate_purl(conda_dep)
        assert purl == "pkg:conda/python@3.11.0"

        # Test generic package
        generic_dep = DependencyInfo(
            name="custom-package", version="1.0.0", package_manager="unknown"
        )
        purl = sbom_generator._generate_purl(generic_dep)
        assert purl == "pkg:generic/custom-package@1.0.0"

    def test_is_dev_dependency(self, sbom_generator):
        """Test development dependency detection."""
        # Development dependencies
        pytest_dep = DependencyInfo(name="pytest", version="7.4.0", package_manager="pip")
        assert sbom_generator._is_dev_dependency(pytest_dep) is True

        mypy_dep = DependencyInfo(name="mypy", version="1.5.0", package_manager="pip")
        assert sbom_generator._is_dev_dependency(mypy_dep) is True

        # Production dependencies
        requests_dep = DependencyInfo(name="requests", version="2.28.0", package_manager="pip")
        assert sbom_generator._is_dev_dependency(requests_dep) is False

        numpy_dep = DependencyInfo(name="numpy", version="1.24.0", package_manager="pip")
        assert sbom_generator._is_dev_dependency(numpy_dep) is False

    def test_save_sbom_json(self, sbom_generator, tmp_path):
        """Test saving SBOM as JSON."""
        sbom_data = sbom_generator.generate_sbom(output_format="cyclonedx")
        output_path = tmp_path / "sbom.json"

        saved_path = sbom_generator.save_sbom(
            sbom_data, output_path, output_format="cyclonedx", output_type="json"
        )

        assert saved_path == output_path
        assert output_path.exists()

        # Verify content
        with open(output_path, encoding="utf-8") as f:
            loaded_data = json.load(f)
        assert loaded_data["bomFormat"] == "CycloneDX"

    def test_save_sbom_yaml(self, sbom_generator, tmp_path):
        """Test saving SBOM as YAML (SPDX only)."""
        sbom_data = sbom_generator.generate_sbom(output_format="spdx")
        output_path = tmp_path / "sbom.yaml"

        saved_path = sbom_generator.save_sbom(
            sbom_data, output_path, output_format="spdx", output_type="yaml"
        )

        assert saved_path == output_path
        assert output_path.exists()

        # Verify it's valid YAML
        import yaml

        with open(output_path, encoding="utf-8") as f:
            loaded_data = yaml.safe_load(f)
        assert loaded_data["spdxVersion"] == "SPDX-2.3"

    def test_save_sbom_xml(self, sbom_generator, tmp_path):
        """Test saving SBOM as XML (CycloneDX only)."""
        sbom_data = sbom_generator.generate_sbom(output_format="cyclonedx")
        output_path = tmp_path / "sbom.xml"

        saved_path = sbom_generator.save_sbom(
            sbom_data, output_path, output_format="cyclonedx", output_type="xml"
        )

        assert saved_path == output_path
        assert output_path.exists()

        # Verify XML content
        content = output_path.read_text(encoding="utf-8")
        assert content.startswith('<?xml version="1.0" encoding="UTF-8"?>')
        assert "<bom>" in content

    def test_invalid_format_combinations(self, sbom_generator):
        """Test error handling for invalid format combinations."""
        # Invalid SBOM format
        with pytest.raises(ValueError, match="Unsupported SBOM format"):
            sbom_generator.generate_sbom(output_format="invalid")

        # Invalid output type for CycloneDX
        with pytest.raises(ValueError, match="CycloneDX supports json and xml"):
            sbom_generator.generate_sbom(output_format="cyclonedx", output_type="yaml")

        # Invalid output type for SPDX
        with pytest.raises(ValueError, match="SPDX supports json and yaml"):
            sbom_generator.generate_sbom(output_format="spdx", output_type="xml")

    def test_generate_vulnerability_report(self, sbom_generator, tmp_path):
        """Test vulnerability report generation."""
        report_path = tmp_path / "vulnerability_report.json"

        report = sbom_generator.generate_vulnerability_report(
            output_path=report_path, include_fix_recommendations=True
        )

        # Validate report structure
        assert report["report_type"] == "vulnerability_analysis"
        assert "generated_at" in report
        assert "summary" in report

        # Check summary
        summary = report["summary"]
        assert summary["total_dependencies"] == 3
        assert summary["vulnerable_dependencies"] == 1
        assert summary["total_vulnerabilities"] == 1
        assert summary["severity_breakdown"]["medium"] == 1

        # Check vulnerable packages
        assert len(report["vulnerable_packages"]) == 1
        vuln_pkg = report["vulnerable_packages"][0]
        assert vuln_pkg["name"] == "requests"
        assert len(vuln_pkg["vulnerabilities"]) == 1

        # Check recommendations
        assert len(report["recommendations"]) == 1
        assert "Update requests from 2.28.0 to 2.31.0" in report["recommendations"][0]

        # Verify file was saved
        assert report_path.exists()

    def test_generate_compliance_report(self, sbom_generator, tmp_path):
        """Test compliance report generation."""
        report_path = tmp_path / "compliance_report.json"

        report = sbom_generator.generate_compliance_report(
            compliance_frameworks=["NIST", "SOX"], output_path=report_path
        )

        # Validate report structure
        assert report["report_type"] == "compliance_analysis"
        assert "generated_at" in report
        assert report["frameworks"] == ["NIST", "SOX"]

        # Check compliance status
        assert "compliance_status" in report
        assert "NIST" in report["compliance_status"]
        assert "SOX" in report["compliance_status"]

        # Validate compliance assessment
        nist_status = report["compliance_status"]["NIST"]
        assert "compliance_level" in nist_status
        assert "risk_score" in nist_status
        assert nist_status["vulnerable_dependencies"] == 1

        # Check findings
        assert "findings" in report
        assert len(report["findings"]) >= 1

        # Verify file was saved
        assert report_path.exists()

    def test_assess_compliance_framework(self, sbom_generator, mock_dependencies):
        """Test compliance framework assessment."""
        # Test NIST assessment
        nist_assessment = sbom_generator._assess_compliance_framework(mock_dependencies, "NIST")
        assert nist_assessment["vulnerable_dependencies"] == 1
        assert nist_assessment["compliance_level"] in ["low", "medium", "high"]
        assert 0 <= nist_assessment["risk_score"] <= 100

        # Test SOX assessment
        sox_assessment = sbom_generator._assess_compliance_framework(mock_dependencies, "SOX")
        assert sox_assessment["vulnerable_dependencies"] == 1
        assert sox_assessment["compliance_level"] in ["low", "medium", "high"]

    def test_dict_to_xml_conversion(self, sbom_generator):
        """Test dictionary to XML conversion."""
        test_data = {
            "name": "test",
            "version": "1.0",
            "components": [
                {"name": "comp1", "version": "1.1"},
                {"name": "comp2", "version": "1.2"},
            ],
        }

        xml_result = sbom_generator._dict_to_xml(test_data, "root")

        assert "<root>" in xml_result
        assert "</root>" in xml_result
        assert "<name>test</name>" in xml_result
        assert "<version>1.0</version>" in xml_result
        assert "<name>comp1</name>" in xml_result

    @patch.object(SBOMGenerator, "_generate_cyclonedx")
    def test_generate_sbom_calls_correct_method(self, mock_cyclonedx, sbom_generator):
        """Test that generate_sbom calls the correct format method."""
        mock_cyclonedx.return_value = {"test": "data"}

        result = sbom_generator.generate_sbom(output_format="cyclonedx")

        mock_cyclonedx.assert_called_once()
        assert result == {"test": "data"}

    def test_vulnerability_report_without_vulnerabilities(self, sbom_generator):
        """Test vulnerability report with no vulnerabilities."""
        # Mock analyzer to return dependencies without vulnerabilities
        clean_deps = [
            DependencyInfo(name="requests", version="2.31.0", package_manager="pip"),
            DependencyInfo(name="numpy", version="1.24.0", package_manager="pip"),
        ]
        sbom_generator.dependency_analyzer.scan_dependencies.return_value = clean_deps

        report = sbom_generator.generate_vulnerability_report()

        assert report["summary"]["vulnerable_dependencies"] == 0
        assert report["summary"]["total_vulnerabilities"] == 0
        assert len(report["vulnerable_packages"]) == 0
        assert len(report["recommendations"]) == 0

    def test_compliance_report_custom_frameworks(self, sbom_generator):
        """Test compliance report with custom frameworks."""
        custom_frameworks = ["Custom1", "Custom2"]

        report = sbom_generator.generate_compliance_report(compliance_frameworks=custom_frameworks)

        assert report["frameworks"] == custom_frameworks
        assert "Custom1" in report["compliance_status"]
        assert "Custom2" in report["compliance_status"]
