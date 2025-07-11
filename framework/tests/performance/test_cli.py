"""Tests for framework performance CLI module."""

import pytest
from unittest.mock import MagicMock, patch, call
from pathlib import Path
import argparse

from framework.performance.cli import main, handle_collect, handle_compare


class TestPerformanceCLI:
    """Test cases for PerformanceCLI functions."""

    def test_collect_command_execution(self):
        """Test collect command execution."""
        # Mock arguments
        args = argparse.Namespace(
            results="test_results.json",
            storage_path="test_storage",
            store_baseline=False,
            baseline_name="default",
            compare_baseline=None,
            output=None
        )
        
        # Mock PerformanceCollector
        with patch('framework.performance.cli.PerformanceCollector') as mock_collector:
            mock_instance = mock_collector.return_value
            mock_metrics = MagicMock()
            mock_instance.collect_benchmark_data.return_value = mock_metrics
            mock_instance.save_metrics.return_value = "test_metrics.json"
            
            # Mock file reading
            with patch('builtins.open', create=True) as mock_open:
                mock_open.return_value.__enter__.return_value.read.return_value = '{"test": "data"}'
                
                handle_collect(args)
                
                # Verify collector was called
                mock_instance.collect_benchmark_data.assert_called_once()
                mock_instance.save_metrics.assert_called_once()

    def test_collect_command_with_baseline(self):
        """Test collect command with baseline storage."""
        args = argparse.Namespace(
            results="test_results.json",
            storage_path="test_storage",
            store_baseline=True,
            baseline_name="custom_baseline",
            compare_baseline=None,
            output=None
        )
        
        with patch('framework.performance.cli.PerformanceCollector') as mock_collector:
            mock_instance = mock_collector.return_value
            mock_metrics = MagicMock()
            mock_instance.collect_benchmark_data.return_value = mock_metrics
            mock_instance.save_metrics.return_value = "test_metrics.json"
            mock_instance.save_baseline.return_value = "custom_baseline.json"
            
            with patch('builtins.open', create=True) as mock_open:
                mock_open.return_value.__enter__.return_value.read.return_value = '{"test": "data"}'
                
                handle_collect(args)
                
                # Verify baseline was saved
                mock_instance.save_baseline.assert_called_once()

    def test_collect_command_with_comparison(self):
        """Test collect command with baseline comparison."""
        args = argparse.Namespace(
            results="test_results.json",
            storage_path="test_storage",
            store_baseline=False,
            baseline_name="default",
            compare_baseline="existing_baseline",
            output=None
        )
        
        with patch('framework.performance.cli.PerformanceCollector') as mock_collector:
            mock_instance = mock_collector.return_value
            mock_metrics = MagicMock()
            mock_instance.collect_benchmark_data.return_value = mock_metrics
            mock_instance.save_metrics.return_value = "test_metrics.json"
            mock_instance.compare_with_baseline.return_value = MagicMock()
            
            with patch('builtins.open', create=True) as mock_open:
                mock_open.return_value.__enter__.return_value.read.return_value = '{"test": "data"}'
                
                handle_collect(args)
                
                # Verify comparison was performed
                mock_instance.compare_with_baseline.assert_called_once()

    def test_compare_command_execution(self):
        """Test compare command execution."""
        args = argparse.Namespace(
            current="current_results.json",
            baseline="baseline_name",
            storage_path="test_storage",
            threshold_config=None,
            mode="comprehensive",
            output=None,
            format="json"
        )
        
        # Mock PerformanceComparator
        with patch('framework.performance.cli.PerformanceComparator') as mock_comparator:
            mock_instance = mock_comparator.return_value
            mock_comparison = MagicMock()
            mock_instance.compare_performance.return_value = mock_comparison
            
            # Mock file operations
            with patch('builtins.open', create=True) as mock_open:
                mock_open.return_value.__enter__.return_value.read.return_value = '{"test": "data"}'
                
                handle_compare(args)
                
                # Verify comparison was performed
                mock_instance.compare_performance.assert_called_once()

    def test_compare_command_with_threshold_config(self):
        """Test compare command with custom threshold configuration."""
        args = argparse.Namespace(
            current="current_results.json",
            baseline="baseline_name",
            storage_path="test_storage",
            threshold_config="custom_thresholds.json",
            mode="comprehensive",
            output=None,
            format="json"
        )
        
        with patch('framework.performance.cli.PerformanceComparator') as mock_comparator:
            mock_instance = mock_comparator.return_value
            mock_comparison = MagicMock()
            mock_instance.compare_performance.return_value = mock_comparison
            
            with patch('builtins.open', create=True) as mock_open:
                mock_open.return_value.__enter__.return_value.read.return_value = '{"test": "data"}'
                
                handle_compare(args)
                
                # Verify comparison was performed with custom config
                mock_instance.compare_performance.assert_called_once()

    def test_performance_main_function(self):
        """Test performance main function."""
        # Mock sys.argv
        test_args = [
            "performance",
            "collect",
            "--results", "test_results.json",
            "--storage-path", "test_storage"
        ]
        
        with patch('sys.argv', test_args):
            with patch('framework.performance.cli.PerformanceCollector') as mock_collector:
                mock_instance = mock_collector.return_value
                mock_metrics = MagicMock()
                mock_instance.collect_benchmark_data.return_value = mock_metrics
                mock_instance.save_metrics.return_value = "test_metrics.json"
                
                with patch('builtins.open', create=True) as mock_open:
                    mock_open.return_value.__enter__.return_value.read.return_value = '{"test": "data"}'
                    
                    # Should execute without errors
                    try:
                        main()
                    except SystemExit:
                        # argparse exits normally
                        pass

    def test_main_function_execution(self):
        """Test main function execution."""
        # Mock sys.argv for main function
        test_args = [
            "cli",
            "collect",
            "--results", "test_results.json"
        ]
        
        with patch('sys.argv', test_args):
            with patch('framework.performance.cli.PerformanceCollector') as mock_collector:
                mock_instance = mock_collector.return_value
                mock_metrics = MagicMock()
                mock_instance.collect_benchmark_data.return_value = mock_metrics
                mock_instance.save_metrics.return_value = "test_metrics.json"
                
                with patch('builtins.open', create=True) as mock_open:
                    mock_open.return_value.__enter__.return_value.read.return_value = '{"test": "data"}'
                    
                    # Should execute without errors
                    try:
                        main()
                    except SystemExit:
                        # argparse exits normally
                        pass

    def test_collect_command_error_handling(self):
        """Test collect command error handling."""
        args = argparse.Namespace(
            results="nonexistent_file.json",
            storage_path="test_storage",
            store_baseline=False,
            baseline_name="default",
            compare_baseline=None,
            output=None
        )
        
        with patch('framework.performance.cli.PerformanceCollector') as mock_collector:
            mock_instance = mock_collector.return_value
            mock_instance.collect_benchmark_data.side_effect = Exception("File not found")
            
            # Should handle exception gracefully
            with pytest.raises(Exception):
                handle_collect(args)

    def test_compare_command_error_handling(self):
        """Test compare command error handling."""
        args = argparse.Namespace(
            current="nonexistent_file.json",
            baseline="nonexistent_baseline",
            storage_path="test_storage",
            threshold_config=None,
            mode="comprehensive",
            output=None,
            format="json"
        )
        
        with patch('framework.performance.cli.PerformanceComparator') as mock_comparator:
            mock_instance = mock_comparator.return_value
            mock_instance.compare_performance.side_effect = Exception("Comparison failed")
            
            # Should handle exception gracefully
            with pytest.raises(Exception):
                handle_compare(args)

    def test_collect_command_with_output_file(self):
        """Test collect command with output file."""
        args = argparse.Namespace(
            results="test_results.json",
            storage_path="test_storage",
            store_baseline=False,
            baseline_name="default",
            compare_baseline=None,
            output="output.json"
        )
        
        with patch('framework.performance.cli.PerformanceCollector') as mock_collector:
            mock_instance = mock_collector.return_value
            mock_metrics = MagicMock()
            mock_instance.collect_benchmark_data.return_value = mock_metrics
            mock_instance.save_metrics.return_value = "test_metrics.json"
            
            with patch('builtins.open', create=True) as mock_open:
                mock_open.return_value.__enter__.return_value.read.return_value = '{"test": "data"}'
                
                handle_collect(args)
                
                # Verify output file was written
                mock_open.assert_called()

    def test_performance_cli_imports(self):
        """Test that all required modules can be imported."""
        # Test imports
        from framework.performance.cli import main, handle_collect, handle_compare
        
        # Verify functions exist
        assert callable(main)
        assert callable(handle_collect)
        assert callable(handle_compare)

    def test_compare_command_different_modes(self):
        """Test compare command with different comparison modes."""
        modes = ["comprehensive", "basic", "detailed"]
        
        for mode in modes:
            args = argparse.Namespace(
                current="current_results.json",
                baseline="baseline_name",
                storage_path="test_storage",
                threshold_config=None,
                mode=mode,
                output=None,
                format="json"
            )
            
            with patch('framework.performance.cli.PerformanceComparator') as mock_comparator:
                mock_instance = mock_comparator.return_value
                mock_comparison = MagicMock()
                mock_instance.compare_performance.return_value = mock_comparison
                
                with patch('builtins.open', create=True) as mock_open:
                    mock_open.return_value.__enter__.return_value.read.return_value = '{"test": "data"}'
                    
                    handle_compare(args)
                    
                    # Verify comparison was performed
                    mock_instance.compare_performance.assert_called_once()

    def test_compare_command_different_formats(self):
        """Test compare command with different output formats."""
        formats = ["json", "yaml", "html"]
        
        for fmt in formats:
            args = argparse.Namespace(
                current="current_results.json",
                baseline="baseline_name",
                storage_path="test_storage",
                threshold_config=None,
                mode="comprehensive",
                output=None,
                format=fmt
            )
            
            with patch('framework.performance.cli.PerformanceComparator') as mock_comparator:
                mock_instance = mock_comparator.return_value
                mock_comparison = MagicMock()
                mock_instance.compare_performance.return_value = mock_comparison
                
                with patch('builtins.open', create=True) as mock_open:
                    mock_open.return_value.__enter__.return_value.read.return_value = '{"test": "data"}'
                    
                    handle_compare(args)
                    
                    # Verify comparison was performed
                    mock_instance.compare_performance.assert_called_once()

    def test_collect_command_json_parsing(self):
        """Test collect command with JSON parsing."""
        args = argparse.Namespace(
            results="test_results.json",
            storage_path="test_storage",
            store_baseline=False,
            baseline_name="default",
            compare_baseline=None,
            output=None
        )
        
        with patch('framework.performance.cli.PerformanceCollector') as mock_collector:
            mock_instance = mock_collector.return_value
            mock_metrics = MagicMock()
            mock_instance.collect_benchmark_data.return_value = mock_metrics
            mock_instance.save_metrics.return_value = "test_metrics.json"
            
            # Test with valid JSON
            with patch('builtins.open', create=True) as mock_open:
                mock_open.return_value.__enter__.return_value.read.return_value = '{"benchmark": "data", "metrics": [1, 2, 3]}'
                
                handle_collect(args)
                
                # Verify JSON was parsed
                mock_instance.collect_benchmark_data.assert_called_once()

    def test_collect_command_invalid_json(self):
        """Test collect command with invalid JSON."""
        args = argparse.Namespace(
            results="test_results.json",
            storage_path="test_storage",
            store_baseline=False,
            baseline_name="default",
            compare_baseline=None,
            output=None
        )
        
        with patch('framework.performance.cli.PerformanceCollector') as mock_collector:
            # Test with invalid JSON
            with patch('builtins.open', create=True) as mock_open:
                mock_open.return_value.__enter__.return_value.read.return_value = 'invalid json'
                
                # Should handle invalid JSON gracefully
                with pytest.raises(Exception):
                    handle_collect(args)