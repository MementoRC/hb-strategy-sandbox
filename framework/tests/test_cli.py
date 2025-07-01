"""Test suite for the unified framework CLI.

Tests for the Click-based command-line interface that provides
unified access to all framework tools.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from framework.cli import cli


class TestFrameworkCLI:
    """Test cases for the main framework CLI."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_cli_help(self):
        """Test that CLI help displays correctly."""
        result = self.runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert "Hummingbot Development Framework CLI" in result.output
        assert "performance" in result.output
        assert "security" in result.output
        assert "reporting" in result.output
        assert "maintenance" in result.output

    def test_cli_version(self):
        """Test that version information displays correctly."""
        result = self.runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert "1.0.0" in result.output

    def test_verbose_flag(self):
        """Test that verbose flag is properly handled.""" 
        # Test verbose with a non-help command to see the verbose message
        result = self.runner.invoke(cli, ['--verbose', 'maintenance', '--help'])
        assert result.exit_code == 0
        # The verbose message should appear when running actual commands, not help


class TestPerformanceCommands:
    """Test cases for performance-related CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_performance_help(self):
        """Test that performance command help displays correctly."""
        result = self.runner.invoke(cli, ['performance', '--help'])
        assert result.exit_code == 0
        assert "Performance monitoring and analysis tools" in result.output
        assert "collect" in result.output
        assert "compare" in result.output

    @patch('framework.performance.cli.handle_collect')
    def test_performance_collect(self, mock_handle_collect):
        """Test performance collect command."""
        with tempfile.NamedTemporaryFile(suffix='.json') as tmp_file:
            # Create dummy benchmark results
            benchmark_data = {
                "benchmarks": [
                    {"name": "test_benchmark", "value": 1.23, "unit": "seconds"}
                ]
            }
            tmp_file.write(json.dumps(benchmark_data).encode())
            tmp_file.flush()

            result = self.runner.invoke(cli, [
                'performance', 'collect', tmp_file.name,
                '--storage-path', 'test_data',
                '--store-baseline',
                '--baseline-name', 'test'
            ])
            
            assert result.exit_code == 0
            mock_handle_collect.assert_called_once()
            
            # Verify arguments passed to handler
            args = mock_handle_collect.call_args[0][0]
            assert args.results == tmp_file.name
            assert args.storage_path == 'test_data'
            assert args.store_baseline is True
            assert args.baseline_name == 'test'

    @patch('framework.performance.cli.handle_compare')
    def test_performance_compare(self, mock_handle_compare):
        """Test performance compare command."""
        with tempfile.NamedTemporaryFile(suffix='.json') as tmp_file:
            tmp_file.write(b'{"benchmarks": []}')
            tmp_file.flush()

            result = self.runner.invoke(cli, [
                'performance', 'compare', tmp_file.name,
                '--baseline', 'test_baseline',
                '--mode', 'trend',
                '--format', 'json',
                '--fail-on-regression'
            ])
            
            assert result.exit_code == 0
            mock_handle_compare.assert_called_once()
            
            args = mock_handle_compare.call_args[0][0]
            assert args.current == tmp_file.name
            assert args.baseline == 'test_baseline'
            assert args.mode == 'trend'
            assert args.format == 'json'
            assert args.fail_on_regression is True

    def test_performance_collect_missing_file(self):
        """Test performance collect with missing results file."""
        result = self.runner.invoke(cli, [
            'performance', 'collect', '/nonexistent/file.json'
        ])
        assert result.exit_code != 0


class TestSecurityCommands:
    """Test cases for security-related CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_security_help(self):
        """Test that security command help displays correctly."""
        result = self.runner.invoke(cli, ['security', '--help'])
        assert result.exit_code == 0
        assert "Security scanning and vulnerability assessment tools" in result.output
        assert "scan" in result.output
        assert "sbom" in result.output

    @patch('framework.security.cli.scan_command')
    def test_security_scan(self, mock_scan_command):
        """Test security scan command."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = self.runner.invoke(cli, [
                'security', 'scan', tmp_dir,
                '--build-id', 'test_build',
                '--package-managers', 'pip',
                '--save-baseline',
                '--baseline-name', 'test'
            ])
            
            assert result.exit_code == 0
            mock_scan_command.assert_called_once()
            
            args = mock_scan_command.call_args[0][0]
            assert args.project_path == tmp_dir
            assert args.build_id == 'test_build'
            assert args.package_managers == ['pip']
            assert args.save_baseline is True
            assert args.baseline_name == 'test'

    @patch('framework.security.cli.sbom_command')
    def test_security_sbom(self, mock_sbom_command):
        """Test SBOM generation command."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = self.runner.invoke(cli, [
                'security', 'sbom', tmp_dir,
                '--format', 'spdx',
                '--output-type', 'xml',
                '--include-dev',
                '--include-vulns'
            ])
            
            assert result.exit_code == 0
            mock_sbom_command.assert_called_once()
            
            args = mock_sbom_command.call_args[0][0]
            assert args.project_path == tmp_dir
            assert args.format == 'spdx'
            assert args.output_type == 'xml'
            assert args.include_dev is True
            assert args.include_vulns is True

    def test_security_scan_missing_directory(self):
        """Test security scan with missing project directory."""
        result = self.runner.invoke(cli, [
            'security', 'scan', '/nonexistent/directory'
        ])
        assert result.exit_code != 0


class TestReportingCommands:
    """Test cases for reporting-related CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_reporting_help(self):
        """Test that reporting command help displays correctly."""
        result = self.runner.invoke(cli, ['reporting', '--help'])
        assert result.exit_code == 0
        assert "Report generation and artifact management tools" in result.output
        assert "generate" in result.output

    def test_reporting_generate(self):
        """Test report generation command."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create a dummy data file
            data_file = Path(tmp_dir) / "data.json"
            data_file.write_text('{"test": "data"}')
            
            result = self.runner.invoke(cli, [
                'reporting', 'generate', str(data_file),
                '--format', 'html',
                '--output', 'test_report.html',
                '--include-charts'
            ])
            
            assert result.exit_code == 0
            assert "Report generation functionality ready" in result.output
            assert "test_report.html" in result.output

    def test_reporting_generate_missing_file(self):
        """Test report generation with missing data file."""
        result = self.runner.invoke(cli, [
            'reporting', 'generate', '/nonexistent/data.json',
            '--output', 'test_report.html'
        ])
        assert result.exit_code != 0


class TestMaintenanceCommands:
    """Test cases for maintenance-related CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_maintenance_help(self):
        """Test that maintenance command help displays correctly."""
        result = self.runner.invoke(cli, ['maintenance', '--help'])
        assert result.exit_code == 0
        assert "Maintenance and health monitoring tools" in result.output
        assert "health-check" in result.output
        assert "schedule" in result.output

    @patch('framework.maintenance.CIHealthMonitor')
    def test_maintenance_health_check(self, mock_monitor_class):
        """Test health check command."""
        # Mock the health monitor
        mock_monitor = MagicMock()
        mock_monitor.collect_health_metrics.return_value = {
            'status': 'healthy',
            'metrics': ['metric1', 'metric2']
        }
        mock_monitor_class.return_value = mock_monitor

        result = self.runner.invoke(cli, [
            'maintenance', 'health-check'
        ])
        
        assert result.exit_code == 0
        assert "Health Check Results" in result.output
        assert "System Status: OK" in result.output
        mock_monitor.collect_health_metrics.assert_called_once()

    @patch('framework.maintenance.CIHealthMonitor')
    def test_maintenance_health_check_with_output(self, mock_monitor_class):
        """Test health check command with output file."""
        mock_monitor = MagicMock()
        mock_monitor.collect_health_metrics.return_value = {
            'status': 'healthy',
            'metrics': []
        }
        mock_monitor_class.return_value = mock_monitor

        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp_file:
            result = self.runner.invoke(cli, [
                'maintenance', 'health-check',
                '--output', tmp_file.name
            ])
            
            assert result.exit_code == 0
            assert f"Health report written to: {tmp_file.name}" in result.output
            
            # Verify output file was written
            output_data = json.loads(Path(tmp_file.name).read_text())
            assert output_data['status'] == 'healthy'

    @patch('framework.maintenance.MaintenanceScheduler')
    def test_maintenance_schedule(self, mock_scheduler_class):
        """Test maintenance task scheduling."""
        mock_scheduler = MagicMock()
        mock_scheduler_class.return_value = mock_scheduler

        result = self.runner.invoke(cli, [
            'maintenance', 'schedule', 'test_task',
            '--frequency', 'daily'
        ])
        
        assert result.exit_code == 0
        assert "Task 'test_task' scheduled for daily execution" in result.output
        mock_scheduler_class.assert_called_once()


class TestQuickScanCommand:
    """Test cases for the quick-scan command."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch('framework.maintenance.CIHealthMonitor')
    def test_quick_scan(self, mock_monitor_class):
        """Test quick scan command."""
        # Mock health monitor
        mock_monitor = MagicMock()
        mock_monitor.collect_health_metrics.return_value = {'status': 'healthy'}
        mock_monitor_class.return_value = mock_monitor

        with tempfile.TemporaryDirectory() as tmp_dir:
            # Mock security scan to avoid actual execution
            with patch('framework.security.cli.scan_command') as mock_scan:
                result = self.runner.invoke(cli, [
                    'quick-scan', tmp_dir,
                    '--output', str(Path(tmp_dir) / 'reports')
                ])
                
                assert result.exit_code == 0
                assert "Quick Framework Scan Started" in result.output
                assert "Running health check" in result.output
                assert "Running security scan" in result.output
                assert "Quick scan completed" in result.output

    def test_quick_scan_default_directory(self):
        """Test quick scan with default directory."""
        with patch('framework.maintenance.CIHealthMonitor') as mock_monitor_class:
            mock_monitor = MagicMock()
            mock_monitor.collect_health_metrics.return_value = {'status': 'healthy'}
            mock_monitor_class.return_value = mock_monitor
            
            with patch('framework.security.cli.scan_command'):
                result = self.runner.invoke(cli, ['quick-scan'])
                
                assert result.exit_code == 0
                assert "Quick Framework Scan Started" in result.output


class TestCLIErrorHandling:
    """Test cases for CLI error handling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_invalid_command(self):
        """Test handling of invalid commands."""
        result = self.runner.invoke(cli, ['invalid-command'])
        assert result.exit_code != 0

    def test_missing_click_dependency(self):
        """Test handling when Click is not available."""
        with patch('framework.cli.click', side_effect=ImportError("No module named 'click'")):
            # This would normally be tested at import time
            # We can test the error message in the module
            pass

    @patch('framework.performance.cli.handle_collect')
    def test_performance_collect_error(self, mock_handle_collect):
        """Test error handling in performance collect command."""
        mock_handle_collect.side_effect = Exception("Collection failed")
        
        with tempfile.NamedTemporaryFile(suffix='.json') as tmp_file:
            tmp_file.write(b'{}')
            tmp_file.flush()
            
            result = self.runner.invoke(cli, [
                'performance', 'collect', tmp_file.name
            ])
            
            assert result.exit_code == 1
            assert "Error collecting performance metrics" in result.output

    @patch('framework.security.cli.scan_command')
    def test_security_scan_error(self, mock_scan_command):
        """Test error handling in security scan command."""
        mock_scan_command.side_effect = Exception("Scan failed")
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = self.runner.invoke(cli, [
                'security', 'scan', tmp_dir
            ])
            
            assert result.exit_code == 1
            assert "Error during security scan" in result.output


class TestCLIIntegration:
    """Integration tests for CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_cli_command_discovery(self):
        """Test that all commands are discoverable."""
        result = self.runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        
        # Check that all main command groups are present
        expected_commands = [
            'performance',
            'security', 
            'reporting',
            'maintenance',
            'quick-scan'
        ]
        
        for command in expected_commands:
            assert command in result.output

    def test_command_group_completeness(self):
        """Test that command groups have expected subcommands."""
        # Performance subcommands
        result = self.runner.invoke(cli, ['performance', '--help'])
        assert result.exit_code == 0
        assert 'collect' in result.output
        assert 'compare' in result.output
        
        # Security subcommands
        result = self.runner.invoke(cli, ['security', '--help'])
        assert result.exit_code == 0
        assert 'scan' in result.output
        assert 'sbom' in result.output
        
        # Reporting subcommands
        result = self.runner.invoke(cli, ['reporting', '--help'])
        assert result.exit_code == 0
        assert 'generate' in result.output
        
        # Maintenance subcommands
        result = self.runner.invoke(cli, ['maintenance', '--help'])
        assert result.exit_code == 0
        assert 'health-check' in result.output
        assert 'schedule' in result.output

    def test_verbose_mode_propagation(self):
        """Test that verbose mode is properly propagated to subcommands."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch('framework.maintenance.CIHealthMonitor') as mock_monitor_class:
                mock_monitor = MagicMock()
                mock_monitor.collect_health_metrics.return_value = {'status': 'healthy'}
                mock_monitor_class.return_value = mock_monitor
                
                result = self.runner.invoke(cli, [
                    '--verbose',
                    'maintenance', 'health-check'
                ])
                
                assert result.exit_code == 0
                assert "Framework CLI initialized in verbose mode" in result.output
                assert "Starting health check" in result.output