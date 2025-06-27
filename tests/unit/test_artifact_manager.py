"""Comprehensive tests for ArtifactManager to achieve 100% coverage."""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest

from strategy_sandbox.reporting.artifact_manager import ArtifactManager


class TestArtifactManager:
    """Test cases for ArtifactManager class."""

    def test_initialization_default_path(self):
        """Test ArtifactManager initialization with default path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = Path.cwd()
            try:
                # Change to temp directory to test default path
                import os
                os.chdir(temp_dir)
                
                manager = ArtifactManager()
                
                assert manager.base_path.name == "artifacts"
                assert manager.base_path.exists()
                assert manager.reports_path.exists()
                assert manager.logs_path.exists()
                assert manager.data_path.exists()
                # Test backward compatibility
                assert manager.artifact_path == manager.base_path
            finally:
                os.chdir(original_cwd)

    def test_initialization_custom_path(self):
        """Test ArtifactManager initialization with custom path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_path = Path(temp_dir) / "custom_artifacts"
            manager = ArtifactManager(custom_path)
            
            assert manager.base_path == custom_path.resolve()
            assert manager.base_path.exists()
            assert manager.reports_path.exists()
            assert manager.logs_path.exists()
            assert manager.data_path.exists()

    def test_initialization_with_string_path(self):
        """Test ArtifactManager initialization with string path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_path = str(Path(temp_dir) / "string_artifacts")
            manager = ArtifactManager(custom_path)
            
            assert manager.base_path == Path(custom_path).resolve()
            assert manager.base_path.exists()

    def test_create_artifact_text_content(self):
        """Test creating artifact with text content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ArtifactManager(temp_dir)
            
            content = "This is test content"
            filename = "test.txt"
            
            artifact_path = manager.create_artifact(filename, content)
            
            assert artifact_path.exists()
            assert artifact_path.parent == manager.logs_path  # text/plain goes to logs
            
            with open(artifact_path) as f:
                assert f.read() == content

    def test_create_artifact_bytes_content(self):
        """Test creating artifact with bytes content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ArtifactManager(temp_dir)
            
            content = b"Binary content"
            filename = "test.bin"
            
            artifact_path = manager.create_artifact(filename, content)
            
            assert artifact_path.exists()
            
            with open(artifact_path, "rb") as f:
                assert f.read() == content

    def test_create_artifact_dict_content(self):
        """Test creating artifact with dictionary content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ArtifactManager(temp_dir)
            
            content = {"key": "value", "number": 42}
            filename = "test.json"
            
            artifact_path = manager.create_artifact(filename, content, "application/json")
            
            assert artifact_path.exists()
            
            with open(artifact_path) as f:
                loaded_content = json.load(f)
                assert loaded_content == content

    def test_create_artifact_list_content(self):
        """Test creating artifact with list content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ArtifactManager(temp_dir)
            
            content = [1, 2, 3, "test"]
            filename = "test_list.json"
            
            artifact_path = manager.create_artifact(filename, content)
            
            assert artifact_path.exists()
            
            with open(artifact_path) as f:
                loaded_content = json.load(f)
                assert loaded_content == content

    def test_create_artifact_storage_path_selection(self):
        """Test artifact storage path selection based on filename and content type."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ArtifactManager(temp_dir)
            
            # Test report path
            report_path = manager.create_artifact("report.md", "content", "text/markdown")
            assert report_path.parent == manager.reports_path
            
            # Test logs path
            log_path = manager.create_artifact("log.txt", "content", "text/plain")
            assert log_path.parent == manager.logs_path
            
            # Test data path (json content type)
            data_path = manager.create_artifact("data.json", "{}", "application/json")
            assert data_path.parent == manager.data_path
            
            # Test data path (filename contains 'data' with non-default content type)
            data_path2 = manager.create_artifact("test_data.txt", "content", "application/csv")
            assert data_path2.parent == manager.data_path
            
            # Test base path (default)
            base_path = manager.create_artifact("unknown.ext", "content", "custom/type")
            assert base_path.parent == manager.base_path

    def test_get_artifact_found(self):
        """Test retrieving an existing artifact."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ArtifactManager(temp_dir)
            
            # Create an artifact
            filename = "test_file.txt"
            content = "test content"
            created_path = manager.create_artifact(filename, content)
            
            # Retrieve it
            retrieved_path = manager.get_artifact(filename)
            
            assert retrieved_path == created_path
            assert retrieved_path.exists()

    def test_get_artifact_not_found(self):
        """Test retrieving a non-existent artifact."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ArtifactManager(temp_dir)
            
            result = manager.get_artifact("nonexistent.txt")
            
            assert result is None

    def test_list_artifacts_all(self):
        """Test listing all artifacts."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ArtifactManager(temp_dir)
            
            # Create artifacts in different directories
            manager.create_artifact("report.md", "content", "text/markdown")
            manager.create_artifact("log.txt", "content", "text/plain")
            manager.create_artifact("data.json", "{}", "application/json")
            
            artifacts = manager.list_artifacts()
            
            assert len(artifacts) == 3
            
            # Check artifact structure
            artifact = artifacts[0]
            assert "name" in artifact
            assert "path" in artifact
            assert "type" in artifact
            assert "size" in artifact
            assert "created" in artifact
            
            # Check types are correct
            types = {a["type"] for a in artifacts}
            assert types == {"reports", "logs", "data"}

    def test_list_artifacts_filtered_by_type(self):
        """Test listing artifacts filtered by type."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ArtifactManager(temp_dir)
            
            # Create artifacts in different directories
            manager.create_artifact("report.md", "content", "text/markdown")
            manager.create_artifact("log.txt", "content", "text/plain")
            manager.create_artifact("data.json", "{}", "application/json")
            
            # Test each filter
            reports = manager.list_artifacts("reports")
            assert len(reports) == 1
            assert reports[0]["type"] == "reports"
            
            logs = manager.list_artifacts("logs")
            assert len(logs) == 1
            assert logs[0]["type"] == "logs"
            
            data = manager.list_artifacts("data")
            assert len(data) == 1
            assert data[0]["type"] == "data"

    def test_list_artifacts_empty_directory(self):
        """Test listing artifacts when directories are empty."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ArtifactManager(temp_dir)
            
            artifacts = manager.list_artifacts()
            
            assert artifacts == []

    def test_get_artifact_summary(self):
        """Test getting artifact summary."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ArtifactManager(temp_dir)
            
            # Create artifacts
            manager.create_artifact("report.md", "content", "text/markdown")
            manager.create_artifact("log.txt", "content", "text/plain")
            manager.create_artifact("data.json", "{}", "application/json")
            
            summary = manager.get_artifact_summary()
            
            assert summary["total_count"] == 3
            assert summary["total_size"] > 0
            assert "by_type" in summary
            assert "recent_artifacts" in summary
            
            # Check by_type structure
            assert "reports" in summary["by_type"]
            assert "logs" in summary["by_type"]
            assert "data" in summary["by_type"]
            
            for type_data in summary["by_type"].values():
                assert "count" in type_data
                assert "size" in type_data

    def test_get_artifact_summary_empty(self):
        """Test getting artifact summary when no artifacts exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ArtifactManager(temp_dir)
            
            summary = manager.get_artifact_summary()
            
            assert summary["total_count"] == 0
            assert summary["total_size"] == 0
            assert summary["by_type"] == {}
            assert summary["recent_artifacts"] == []

    def test_cleanup_old_artifacts(self):
        """Test cleaning up old artifacts."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ArtifactManager(temp_dir)
            
            # Create some artifacts
            manager.create_artifact("old1.txt", "content")
            manager.create_artifact("old2.txt", "content")
            
            # Mock the creation time to make them "old"
            from datetime import datetime, timedelta
            old_time = datetime.now() - timedelta(days=10)
            
            with patch('strategy_sandbox.reporting.artifact_manager.datetime') as mock_datetime:
                mock_datetime.now.return_value = datetime.now()
                mock_datetime.fromisoformat = datetime.fromisoformat
                mock_datetime.fromtimestamp = datetime.fromtimestamp
                
                # Simulate old artifacts
                artifacts = manager.list_artifacts()
                for artifact in artifacts:
                    # Mock the created time to be old
                    artifact["created"] = old_time.isoformat()
                
                with patch.object(manager, 'list_artifacts', return_value=artifacts):
                    cleanup_count = manager.cleanup_old_artifacts(5)
                
                assert cleanup_count == 2

    def test_cleanup_old_artifacts_with_error(self):
        """Test cleanup with file deletion errors."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ArtifactManager(temp_dir)
            
            # Create an artifact
            manager.create_artifact("test.txt", "content")
            
            from datetime import datetime, timedelta
            old_time = datetime.now() - timedelta(days=10)
            
            # Mock list_artifacts to return old artifact
            old_artifact = {
                "name": "test.txt", 
                "path": str(manager.logs_path / "test.txt"),
                "type": "logs",
                "size": 7,
                "created": old_time.isoformat()
            }
            
            with patch.object(manager, 'list_artifacts', return_value=[old_artifact]):
                with patch('pathlib.Path.unlink') as mock_unlink:
                    mock_unlink.side_effect = OSError("Permission denied")
                    
                    # Capture print output
                    with patch('builtins.print') as mock_print:
                        cleanup_count = manager.cleanup_old_artifacts(5)
                    
                    assert cleanup_count == 0
                    mock_print.assert_called_once()
                    assert "Error removing artifact" in str(mock_print.call_args)

    def test_archive_artifacts_success(self):
        """Test successful artifact archiving."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ArtifactManager(temp_dir)
            
            # Create some artifacts
            manager.create_artifact("test1.txt", "content1")
            manager.create_artifact("test2.txt", "content2")
            
            archive_path = manager.archive_artifacts("test_archive", "zip")
            
            assert archive_path is not None
            assert archive_path.exists()
            assert archive_path.name == "test_archive.zip"

    def test_archive_artifacts_failure(self):
        """Test archive creation failure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ArtifactManager(temp_dir)
            
            with patch('shutil.make_archive') as mock_archive:
                mock_archive.side_effect = Exception("Archive creation failed")
                
                with patch('builtins.print') as mock_print:
                    archive_path = manager.archive_artifacts("test_archive")
                
                assert archive_path is None
                mock_print.assert_called_once()
                assert "Error creating artifact archive" in str(mock_print.call_args)

    def test_create_report_artifact_json(self):
        """Test creating JSON report artifact."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ArtifactManager(temp_dir)
            
            report_data = {"test": "data", "number": 42}
            
            artifact_path = manager.create_report_artifact("test_report", report_data, "json")
            
            assert artifact_path is not None
            assert artifact_path.exists()
            assert "test_report_" in artifact_path.name
            assert artifact_path.name.endswith(".json")

    def test_create_report_artifact_html(self):
        """Test creating HTML report artifact."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ArtifactManager(temp_dir)
            
            report_data = {"test": "data"}
            
            artifact_path = manager.create_report_artifact("test_report", report_data, "html")
            
            assert artifact_path is not None
            assert artifact_path.exists()
            assert artifact_path.name.endswith(".html")
            
            with open(artifact_path) as f:
                content = f.read()
                assert "<!DOCTYPE html>" in content
                assert "test_report" in content

    def test_create_report_artifact_markdown(self):
        """Test creating Markdown report artifact."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ArtifactManager(temp_dir)
            
            report_data = {"test": "data"}
            
            artifact_path = manager.create_report_artifact("test_report", report_data, "markdown")
            
            assert artifact_path is not None
            assert artifact_path.exists()
            assert artifact_path.name.endswith(".markdown")
            
            with open(artifact_path) as f:
                content = f.read()
                assert "# test_report" in content

    def test_create_report_artifact_unsupported_format(self):
        """Test creating report artifact with unsupported format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ArtifactManager(temp_dir)
            
            report_data = {"test": "data"}
            
            with pytest.raises(ValueError, match="Unsupported format type: xml"):
                manager.create_report_artifact("test_report", report_data, "xml")

    def test_create_log_artifact_success(self):
        """Test successful log artifact creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ArtifactManager(temp_dir)
            
            log_content = "This is a test log message"
            
            log_path = manager.create_log_artifact("test_log", log_content, "info")
            
            assert log_path is not None
            assert log_path.exists()
            assert "test_log_info_" in log_path.name
            assert log_path.name.endswith(".log")
            
            with open(log_path) as f:
                content = f.read()
                assert log_content in content
                assert "[" in content  # Timestamp

    def test_create_log_artifact_with_error(self):
        """Test log artifact creation with file error."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ArtifactManager(temp_dir)
            
            with patch('builtins.open', mock_open()) as mock_file:
                mock_file.side_effect = Exception("File write error")
                
                with patch('builtins.print') as mock_print:
                    log_path = manager.create_log_artifact("test_log", "content")
                
                assert log_path is None
                mock_print.assert_called_once()
                assert "Error creating log artifact" in str(mock_print.call_args)

    def test_create_data_artifact_json(self):
        """Test creating JSON data artifact."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ArtifactManager(temp_dir)
            
            data = {"key": "value", "list": [1, 2, 3]}
            
            data_path = manager.create_data_artifact("test_data", data, "json")
            
            assert data_path is not None
            assert data_path.exists()
            assert "test_data_" in data_path.name
            assert data_path.name.endswith(".json")
            
            with open(data_path) as f:
                loaded_data = json.load(f)
                assert loaded_data == data

    def test_create_data_artifact_csv_with_string(self):
        """Test creating CSV data artifact with string data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ArtifactManager(temp_dir)
            
            csv_data = "col1,col2\nval1,val2"
            
            data_path = manager.create_data_artifact("test_data", csv_data, "csv")
            
            assert data_path is not None
            assert data_path.exists()
            assert data_path.name.endswith(".csv")
            
            with open(data_path) as f:
                content = f.read()
                assert content == csv_data

    def test_create_data_artifact_text_format(self):
        """Test creating text data artifact."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ArtifactManager(temp_dir)
            
            data = {"key": "value"}
            
            data_path = manager.create_data_artifact("test_data", data, "txt")
            
            assert data_path is not None
            assert data_path.exists()
            assert data_path.name.endswith(".txt")
            
            with open(data_path) as f:
                content = f.read()
                assert str(data) in content

    def test_create_data_artifact_with_error(self):
        """Test data artifact creation with file error."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ArtifactManager(temp_dir)
            
            with patch('builtins.open', mock_open()) as mock_file:
                mock_file.side_effect = Exception("File write error")
                
                with patch('builtins.print') as mock_print:
                    data_path = manager.create_data_artifact("test_data", {})
                
                assert data_path is None
                mock_print.assert_called_once()
                assert "Error creating data artifact" in str(mock_print.call_args)

    def test_generate_csv_empty_dict(self):
        """Test CSV generation with empty dictionary."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ArtifactManager(temp_dir)
            
            csv_content = manager._generate_csv({})
            
            assert csv_content == ""

    def test_generate_csv_dict(self):
        """Test CSV generation with dictionary."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ArtifactManager(temp_dir)
            
            data = {"name": "John", "age": 30}
            csv_content = manager._generate_csv(data)
            
            lines = csv_content.split('\n')
            assert "name,age" in lines[0]
            assert "John,30" in lines[1]

    def test_generate_csv_empty_list(self):
        """Test CSV generation with empty list."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ArtifactManager(temp_dir)
            
            csv_content = manager._generate_csv([])
            
            assert csv_content == "[]"

    def test_generate_csv_list_of_non_dicts(self):
        """Test CSV generation with list of non-dictionaries."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ArtifactManager(temp_dir)
            
            data = [1, 2, 3, "test"]
            csv_content = manager._generate_csv(data)
            
            assert csv_content == str(data)

    def test_generate_csv_list_of_dicts(self):
        """Test CSV generation with list of dictionaries."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ArtifactManager(temp_dir)
            
            data = [
                {"name": "John", "age": 30},
                {"name": "Jane", "age": 25},
                {"name": "Bob"}  # Missing age key
            ]
            csv_content = manager._generate_csv(data)
            
            lines = csv_content.split('\n')
            assert "name,age" in lines[0]
            assert "John,30" in lines[1] 
            assert "Jane,25" in lines[2]
            assert "Bob," in lines[3]  # Missing value becomes empty

    def test_generate_csv_other_type(self):
        """Test CSV generation with other data types."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ArtifactManager(temp_dir)
            
            data = "just a string"
            csv_content = manager._generate_csv(data)
            
            assert csv_content == data