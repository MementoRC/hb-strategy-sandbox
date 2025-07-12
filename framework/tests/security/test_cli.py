"""Tests for framework security CLI module."""

import pytest
from unittest.mock import MagicMock, patch, call
from pathlib import Path
import argparse

from framework.security.cli import scan_command, sbom_command, main


class TestSecurityCLI:
    """Test cases for SecurityCLI functions."""

    def test_scan_command_execution(self):
        """Test scan command execution."""
        # Mock arguments
        args = argparse.Namespace(
            project_path="test_project",
            storage_path="test_storage",
            build_id="test_build",
            package_managers=["npm", "pip"],
            save_baseline=False,
            compare_baseline=None,
            output=None
        )
        
        # Mock SecurityCollector
        with patch('framework.security.cli.SecurityCollector') as mock_collector:
            mock_instance = mock_collector.return_value
            mock_metrics = MagicMock()
            mock_metrics.calculate_summary_stats.return_value = {
                'total_dependencies': 10,
                'vulnerable_dependencies': 2,
                'total_vulnerabilities': 3,
                'vulnerability_rate': 30.0,
                'vulnerabilities_by_severity': {'high': 1, 'medium': 2}
            }
            mock_instance.scan_project_security.return_value = mock_metrics
            mock_instance.save_metrics.return_value = "test_metrics.json"
            
            # Should execute without errors
            scan_command(args)
            
            # Verify collector was called
            mock_instance.scan_project_security.assert_called_once()
            mock_instance.save_metrics.assert_called_once()

    def test_scan_command_with_baseline(self):
        """Test scan command with baseline saving."""
        args = argparse.Namespace(
            project_path="test_project",
            storage_path="test_storage",
            build_id="test_build",
            package_managers=["npm"],
            save_baseline=True,
            baseline_name="test_baseline",
            compare_baseline=None,
            output=None
        )
        
        with patch('framework.security.cli.SecurityCollector') as mock_collector:
            mock_instance = mock_collector.return_value
            mock_metrics = MagicMock()
            mock_metrics.calculate_summary_stats.return_value = {
                'total_dependencies': 5,
                'vulnerable_dependencies': 0,
                'total_vulnerabilities': 0,
                'vulnerability_rate': 0.0
            }
            mock_instance.scan_project_security.return_value = mock_metrics
            mock_instance.save_metrics.return_value = "test_metrics.json"
            mock_instance.save_baseline.return_value = "test_baseline.json"
            
            scan_command(args)
            
            # Verify baseline was saved
            mock_instance.save_baseline.assert_called_once()

    def test_scan_command_with_comparison(self):
        """Test scan command with baseline comparison."""
        args = argparse.Namespace(
            project_path="test_project",
            storage_path="test_storage",
            build_id="test_build",
            package_managers=["npm"],
            save_baseline=False,
            compare_baseline="existing_baseline",
            output=None
        )
        
        with patch('framework.security.cli.SecurityCollector') as mock_collector:
            mock_instance = mock_collector.return_value
            mock_metrics = MagicMock()
            mock_metrics.calculate_summary_stats.return_value = {
                'total_dependencies': 5,
                'vulnerable_dependencies': 1,
                'total_vulnerabilities': 1,
                'vulnerability_rate': 20.0
            }
            mock_instance.scan_project_security.return_value = mock_metrics
            mock_instance.save_metrics.return_value = "test_metrics.json"
            mock_instance.compare_with_baseline.return_value = MagicMock()
            
            scan_command(args)
            
            # Verify comparison was performed
            mock_instance.compare_with_baseline.assert_called_once()

    def test_sbom_command_execution(self):
        """Test SBOM command execution."""
        args = argparse.Namespace(
            project_path="test_project",
            output="test_sbom.json",
            format="json",
            include_licenses=True,
            include_hashes=True
        )
        
        # Mock SBOMGenerator
        with patch('framework.security.cli.SBOMGenerator') as mock_generator:
            mock_instance = mock_generator.return_value
            mock_instance.generate_sbom.return_value = {"components": []}
            mock_instance.save_sbom.return_value = "test_sbom.json"
            
            sbom_command(args)
            
            # Verify SBOM was generated
            mock_instance.generate_sbom.assert_called_once()
            mock_instance.save_sbom.assert_called_once()

    def test_security_main_function(self):
        """Test security main function."""
        # Mock sys.argv
        test_args = [
            "security",
            "scan",
            "--project-path", "test_project",
            "--storage-path", "test_storage",
            "--build-id", "test_build"
        ]
        
        with patch('sys.argv', test_args):
            with patch('framework.security.cli.SecurityCollector') as mock_collector:
                mock_instance = mock_collector.return_value
                mock_metrics = MagicMock()
                mock_metrics.calculate_summary_stats.return_value = {
                    'total_dependencies': 10,
                    'vulnerable_dependencies': 2,
                    'total_vulnerabilities': 3,
                    'vulnerability_rate': 30.0
                }
                mock_instance.scan_project_security.return_value = mock_metrics
                mock_instance.save_metrics.return_value = "test_metrics.json"
                
                # Should execute without errors
                try:
                    main()
                except SystemExit:
                    # argparse exits normally
                    pass

    def test_scan_command_error_handling(self):
        """Test scan command error handling."""
        args = argparse.Namespace(
            project_path="nonexistent_project",
            storage_path="test_storage",
            build_id="test_build",
            package_managers=["npm"],
            save_baseline=False,
            compare_baseline=None,
            output=None
        )
        
        with patch('framework.security.cli.SecurityCollector') as mock_collector:
            mock_instance = mock_collector.return_value
            mock_instance.scan_project_security.side_effect = Exception("Project not found")
            
            # Should handle exception gracefully
            with pytest.raises(Exception):
                scan_command(args)

    def test_sbom_command_error_handling(self):
        """Test SBOM command error handling."""
        args = argparse.Namespace(
            project_path="nonexistent_project",
            output="test_sbom.json",
            format="json",
            include_licenses=True,
            include_hashes=True
        )
        
        with patch('framework.security.cli.SBOMGenerator') as mock_generator:
            mock_instance = mock_generator.return_value
            mock_instance.generate_sbom.side_effect = Exception("SBOM generation failed")
            
            # Should handle exception gracefully
            with pytest.raises(Exception):
                sbom_command(args)

    def test_scan_command_with_output_file(self):
        """Test scan command with output file."""
        args = argparse.Namespace(
            project_path="test_project",
            storage_path="test_storage",
            build_id="test_build",
            package_managers=["npm"],
            save_baseline=False,
            compare_baseline=None,
            output="output.json"
        )
        
        with patch('framework.security.cli.SecurityCollector') as mock_collector:
            with patch('builtins.open', create=True) as mock_open:
                mock_instance = mock_collector.return_value
                mock_metrics = MagicMock()
                mock_metrics.calculate_summary_stats.return_value = {
                    'total_dependencies': 10,
                    'vulnerable_dependencies': 2,
                    'total_vulnerabilities': 3,
                    'vulnerability_rate': 30.0
                }
                mock_instance.scan_project_security.return_value = mock_metrics
                mock_instance.save_metrics.return_value = "test_metrics.json"
                
                scan_command(args)
                
                # Verify output file was written
                mock_open.assert_called()

    def test_security_cli_imports(self):
        """Test that all required modules can be imported."""
        # Test imports
        from framework.security.cli import scan_command, sbom_command, main
        
        # Verify functions exist
        assert callable(scan_command)
        assert callable(sbom_command)  
        assert callable(main)

    def test_scan_command_package_managers(self):
        """Test scan command with different package managers."""
        package_managers = ["npm", "pip", "maven", "gradle"]
        
        for pm in package_managers:
            args = argparse.Namespace(
                project_path="test_project",
                storage_path="test_storage",
                build_id="test_build",
                package_managers=[pm],
                save_baseline=False,
                compare_baseline=None,
                output=None
            )
            
            with patch('framework.security.cli.SecurityCollector') as mock_collector:
                mock_instance = mock_collector.return_value
                mock_metrics = MagicMock()
                mock_metrics.calculate_summary_stats.return_value = {
                    'total_dependencies': 5,
                    'vulnerable_dependencies': 0,
                    'total_vulnerabilities': 0,
                    'vulnerability_rate': 0.0
                }
                mock_instance.scan_project_security.return_value = mock_metrics
                mock_instance.save_metrics.return_value = "test_metrics.json"
                
                scan_command(args)
                
                # Verify package manager was passed
                mock_instance.scan_project_security.assert_called_with(
                    project_path="test_project",
                    build_id="test_build",
                    package_managers=[pm]
                )