"""Tests for the security analyzer functionality."""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from strategy_sandbox.security.analyzer import DependencyAnalyzer
from strategy_sandbox.security.models import DependencyInfo


class TestDependencyAnalyzer:
    """Test suite for the DependencyAnalyzer class."""

    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)

            # Create pyproject.toml to simulate a Python project
            pyproject_content = """
[project]
name = "test-project"
dependencies = ["requests", "numpy"]
"""
            (project_path / "pyproject.toml").write_text(pyproject_content)

            yield project_path

    @pytest.fixture
    def analyzer(self, temp_project):
        """Create a DependencyAnalyzer instance for testing."""
        return DependencyAnalyzer(temp_project)

    def test_detect_package_managers_pip(self, temp_project):
        """Test detection of pip package manager."""
        analyzer = DependencyAnalyzer(temp_project)
        managers = analyzer.detect_package_managers()
        assert "pip" in managers

    def test_detect_package_managers_pixi(self, temp_project):
        """Test detection of pixi package manager."""
        # Create pixi.toml file
        (temp_project / "pixi.toml").write_text("[project]\nname = 'test'")

        analyzer = DependencyAnalyzer(temp_project)
        managers = analyzer.detect_package_managers()
        assert "pixi" in managers

    def test_detect_package_managers_conda(self, temp_project):
        """Test detection of conda package manager."""
        # Create environment.yml file
        (temp_project / "environment.yml").write_text("name: test\ndependencies:\n  - python")

        analyzer = DependencyAnalyzer(temp_project)
        managers = analyzer.detect_package_managers()
        assert "conda" in managers

    @patch("subprocess.run")
    def test_scan_pip_dependencies_success(self, mock_run, analyzer):
        """Test successful pip dependency scanning."""
        # Mock pip-audit output
        mock_audit_output = {
            "dependencies": [
                {
                    "name": "requests",
                    "version": "2.28.0",
                    "vulns": [
                        {
                            "id": "CVE-2023-32681",
                            "severity": "medium",
                            "description": "Test vulnerability",
                            "fix_versions": ["2.31.0"],
                            "aliases": ["GHSA-j8r2-6x86-q33q"],
                        }
                    ],
                },
                {"name": "numpy", "version": "1.24.0", "vulns": []},
            ]
        }

        mock_run.return_value = Mock(returncode=0, stdout=json.dumps(mock_audit_output))

        dependencies = analyzer.scan_pip_dependencies()

        assert len(dependencies) == 2
        assert dependencies[0].name == "requests"
        assert dependencies[0].version == "2.28.0"
        assert dependencies[0].package_manager == "pip"
        assert len(dependencies[0].vulnerabilities) == 1
        assert dependencies[0].vulnerabilities[0].id == "CVE-2023-32681"
        assert dependencies[0].vulnerabilities[0].severity == "medium"

        assert dependencies[1].name == "numpy"
        assert len(dependencies[1].vulnerabilities) == 0

    @patch("subprocess.run")
    def test_scan_pip_dependencies_fallback(self, mock_run, analyzer):
        """Test pip dependency scanning fallback when pip-audit fails."""
        # Mock FileNotFoundError to trigger fallback
        mock_run.side_effect = [
            FileNotFoundError("pip-audit not found"),
            Mock(
                returncode=0,
                stdout=json.dumps(
                    [
                        {"name": "requests", "version": "2.28.0"},
                        {"name": "numpy", "version": "1.24.0"},
                    ]
                ),
            ),
        ]

        dependencies = analyzer.scan_pip_dependencies()

        assert len(dependencies) == 2
        assert dependencies[0].name == "requests"
        assert dependencies[0].version == "2.28.0"
        assert dependencies[0].package_manager == "pip"
        assert len(dependencies[0].vulnerabilities) == 0  # No vulnerability data in fallback

    @patch("subprocess.run")
    def test_scan_pixi_dependencies(self, mock_run, analyzer):
        """Test pixi dependency scanning."""
        mock_pixi_output = {
            "default": {
                "dependencies": {
                    "python": {
                        "version": "3.11.*",
                        "channel": "conda-forge",
                        "depends": ["libpython"],
                    },
                    "numpy": {"version": "1.24.*", "channel": "conda-forge", "depends": ["blas"]},
                }
            }
        }

        mock_run.return_value = Mock(returncode=0, stdout=json.dumps(mock_pixi_output))

        dependencies = analyzer.scan_pixi_dependencies()

        assert len(dependencies) == 2
        python_dep = next(dep for dep in dependencies if dep.name == "python")
        assert python_dep.version == "3.11.*"
        assert python_dep.package_manager == "pixi"
        assert python_dep.source == "conda-forge"
        assert "libpython" in python_dep.dependencies

    def test_normalize_severity(self, analyzer):
        """Test severity normalization."""
        assert analyzer._normalize_severity("LOW") == "low"
        assert analyzer._normalize_severity("minor") == "low"
        assert analyzer._normalize_severity("MEDIUM") == "medium"
        assert analyzer._normalize_severity("moderate") == "medium"
        assert analyzer._normalize_severity("HIGH") == "high"
        assert analyzer._normalize_severity("major") == "high"
        assert analyzer._normalize_severity("CRITICAL") == "critical"
        assert analyzer._normalize_severity("severe") == "critical"
        assert analyzer._normalize_severity("unknown") == "medium"

    def test_scan_dependencies_integration(self, analyzer):
        """Test the full scan_dependencies method."""
        with (
            patch.object(analyzer, "scan_pip_dependencies") as mock_pip,
            patch.object(analyzer, "scan_pixi_dependencies") as mock_pixi,
        ):
            mock_pip.return_value = [
                DependencyInfo(name="requests", version="2.28.0", package_manager="pip")
            ]
            mock_pixi.return_value = [
                DependencyInfo(name="numpy", version="1.24.0", package_manager="pixi")
            ]

            # Test with specified package managers
            deps = analyzer.scan_dependencies(["pip", "pixi"])
            assert len(deps) == 2
            assert any(dep.name == "requests" for dep in deps)
            assert any(dep.name == "numpy" for dep in deps)

    @patch("subprocess.run")
    def test_generate_dependency_tree(self, mock_run, analyzer):
        """Test dependency tree generation."""
        # Mock pip-audit response
        mock_run.return_value = Mock(
            returncode=0,
            stdout=json.dumps(
                {"dependencies": [{"name": "requests", "version": "2.28.0", "vulns": []}]}
            ),
        )

        tree = analyzer.generate_dependency_tree()

        assert "project_path" in tree
        assert "package_managers" in tree
        assert "dependencies" in tree
        assert "summary" in tree
        assert tree["summary"]["total_dependencies"] == 1
        assert tree["summary"]["vulnerable_dependencies"] == 0

