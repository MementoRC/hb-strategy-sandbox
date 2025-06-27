"""Artifact management for GitHub Actions workflow integration."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any


class ArtifactManager:
    """Manages CI/CD artifacts for reporting and analysis.

    This class provides a centralized system for creating, storing, and managing
    various types of artifacts generated during CI/CD pipeline execution.
    It organizes artifacts into categories (reports, logs, data), handles their
    creation in different formats (JSON, HTML, Markdown), and offers utilities
    for listing, summarizing, and cleaning up old artifacts.
    """

    def __init__(self, artifact_path: str | Path | None = None):
        """Initialize the artifact manager.

        :param artifact_path: Base path for storing artifacts. Defaults to `./artifacts`.
        """
        self.base_path = Path(artifact_path or "./artifacts").resolve()
        self.base_path.mkdir(exist_ok=True)

        # Create subdirectories for different artifact types
        self.reports_path = self.base_path / "reports"
        self.logs_path = self.base_path / "logs"
        self.data_path = self.base_path / "data"

        self.reports_path.mkdir(exist_ok=True)
        self.logs_path.mkdir(exist_ok=True)
        self.data_path.mkdir(exist_ok=True)

    def create_artifact(
        self, filename: str, content: str | bytes, content_type: str = "text/plain"
    ) -> Path:
        """Create and save an artifact.

        :param filename: The name of the artifact file.
        :param content: The content of the artifact (string or bytes).
        :param content_type: The MIME type of the content.
        :return: The path to the created artifact.
        """
        # Determine storage path based on content type
        if "report" in filename or "text/markdown" in content_type:
            storage_path = self.reports_path
        elif "log" in filename or "text/plain" in content_type:
            storage_path = self.logs_path
        elif "json" in content_type or "data" in filename:
            storage_path = self.data_path
        else:
            storage_path = self.base_path  # Default to base path

        artifact_file = storage_path / filename

        # Write content to file
        mode = "wb" if isinstance(content, bytes) else "w"
        encoding = None if isinstance(content, bytes) else "utf-8"

        with open(artifact_file, mode, encoding=encoding) as f:
            f.write(content)

        return artifact_file

    def get_artifact(self, filename: str) -> Path | None:
        """Retrieve an artifact by filename.

        :param filename: The name of the artifact to retrieve.
        :return: The path to the artifact, or None if not found.
        """
        for path in [self.reports_path, self.logs_path, self.data_path, self.base_path]:
            artifact_file = path / filename
            if artifact_file.exists():
                return artifact_file
        return None

    def list_artifacts(self, artifact_type: str | None = None) -> list[dict[str, Any]]:
        """List all artifacts, optionally filtering by type.

        :param artifact_type: Optional filter ("reports", "logs", "data").
        :return: A list of dictionaries, each representing an artifact.
        """
        artifacts = []
        paths_to_scan: dict[str, Path] = {}

        if artifact_type:
            if artifact_type == "reports":
                paths_to_scan["reports"] = self.reports_path
            elif artifact_type == "logs":
                paths_to_scan["logs"] = self.logs_path
            elif artifact_type == "data":
                paths_to_scan["data"] = self.data_path
        else:
            paths_to_scan = {
                "reports": self.reports_path,
                "logs": self.logs_path,
                "data": self.data_path,
            }

        for type_name, path in paths_to_scan.items():
            for item in path.iterdir():
                if item.is_file():
                    stat = item.stat()
                    artifacts.append(
                        {
                            "name": item.name,
                            "path": str(item),
                            "type": type_name,
                            "size": stat.st_size,
                            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        }
                    )

        # Sort by creation time (newest first)
        artifacts.sort(key=lambda x: x["created"], reverse=True)
        return artifacts

    def get_artifact_summary(self) -> dict[str, Any]:
        """Get a summary of all stored artifacts.

        :return: A dictionary containing artifact summary statistics.
        """
        all_artifacts = self.list_artifacts()
        summary: dict[str, Any] = {
            "total_count": len(all_artifacts),
            "total_size": sum(a["size"] for a in all_artifacts),
            "by_type": {},
            "recent_artifacts": all_artifacts[:5],  # Show 5 most recent
        }

        # Group by type
        for artifact in all_artifacts:
            artifact_type = artifact["type"]
            if artifact_type not in summary["by_type"]:
                summary["by_type"][artifact_type] = {"count": 0, "size": 0}

            summary["by_type"][artifact_type]["count"] += 1
            summary["by_type"][artifact_type]["size"] += artifact["size"]

        return summary

    def cleanup_old_artifacts(self, max_age_days: int) -> int:
        """Remove artifacts older than a specified number of days.

        :param max_age_days: The maximum age in days for an artifact to be kept.
        :return: The number of artifacts that were cleaned up.
        """
        cleanup_count = 0
        cutoff_time = datetime.now() - timedelta(days=max_age_days)

        all_artifacts = self.list_artifacts()

        for artifact in all_artifacts:
            artifact_path = Path(artifact["path"])
            created_time = datetime.fromisoformat(artifact["created"])

            if created_time < cutoff_time:
                try:
                    artifact_path.unlink()
                    cleanup_count += 1
                except OSError as e:
                    print(f"Error removing artifact {artifact_path}: {e}")

        return cleanup_count

    def archive_artifacts(self, archive_name: str, format: str = "zip") -> Path | None:
        """Create a compressed archive of all artifacts.

        :param archive_name: The name of the archive file (without extension).
        :param format: The archive format (e.g., "zip", "tar").
        :return: The path to the created archive, or None on failure.
        """
        archive_path = self.base_path / archive_name

        try:
            shutil.make_archive(str(archive_path), format, self.base_path)
            return Path(f"{archive_path}.{format}")
        except Exception as e:
            print(f"Error creating artifact archive: {e}")
            return None

    def create_report_artifact(
        self, report_name: str, report_data: dict[str, Any], format_type: str = "json"
    ) -> Path | None:
        """Create a structured report artifact.

        Args:
            report_name: Name of the report.
            report_data: Report data.
            format_type: Output format (json, html, markdown).

        Returns:
            Path to created report artifact.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{report_name}_{timestamp}.{format_type}"

        if format_type == "json":
            return self.create_artifact(filename, report_data, "application/json")
        elif format_type == "html":
            html_content = self._generate_html_report(report_name, report_data)
            return self.create_artifact(filename, html_content, "text/html")
        elif format_type == "markdown":
            md_content = self._generate_markdown_report(report_name, report_data)
            return self.create_artifact(filename, md_content, "text/markdown")
        else:
            raise ValueError(f"Unsupported format type: {format_type}")

    def create_log_artifact(
        self, log_name: str, log_content: str, log_level: str = "info"
    ) -> Path | None:
        """Create a log artifact.

        Args:
            log_name: Name of the log.
            log_content: Log content.
            log_level: Log level (debug, info, warning, error).

        Returns:
            Path to created log artifact.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{log_name}_{log_level}_{timestamp}.log"

        # Add timestamp to log content
        timestamped_content = f"[{datetime.now().isoformat()}] {log_content}\n"

        log_path = self.logs_path / filename
        try:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(timestamped_content)
            return log_path
        except Exception as e:
            print(f"Error creating log artifact {log_name}: {e}")
            return None

    def create_data_artifact(
        self, data_name: str, data: dict | list | str, format_type: str = "json"
    ) -> Path | None:
        """Create a data artifact.

        Args:
            data_name: Name of the data file.
            data: Data to store.
            format_type: Format (json, csv, txt).

        Returns:
            Path to created data artifact.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{data_name}_{timestamp}.{format_type}"

        data_path = self.data_path / filename

        try:
            if format_type == "json":
                with open(data_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, default=str)
            elif format_type == "csv":
                # Simple CSV generation for dict/list data
                csv_content = data if isinstance(data, str) else self._generate_csv(data)
                with open(data_path, "w", encoding="utf-8") as f:
                    f.write(csv_content)
            else:
                # Text format
                with open(data_path, "w", encoding="utf-8") as f:
                    f.write(str(data))

            return data_path

        except Exception as e:
            print(f"Error creating data artifact {data_name}: {e}")
            return None

    def list_artifacts(self, artifact_type: str | None = None) -> list[dict[str, Any]]:
        """List all artifacts.

        Args:
            artifact_type: Filter by type (reports, logs, data).

        Returns:
            List of artifact information.
        """
        artifacts = []

        search_paths = []
        if artifact_type == "reports":
            search_paths = [self.reports_path]
        elif artifact_type == "logs":
            search_paths = [self.logs_path]
        elif artifact_type == "data":
            search_paths = [self.data_path]
        else:
            search_paths = [self.reports_path, self.logs_path, self.data_path]

        for search_path in search_paths:
            for file_path in search_path.glob("*"):
                if file_path.is_file():
                    stat = file_path.stat()
                    artifacts.append(
                        {
                            "name": file_path.name,
                            "path": str(file_path),
                            "type": search_path.name,
                            "size": stat.st_size,
                            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        }
                    )

        # Sort by creation time, newest first
        artifacts.sort(key=lambda x: str(x["created"]), reverse=True)
        return artifacts

    def get_artifact_summary(self) -> dict[str, Any]:
        """Get summary of all artifacts.

        Returns:
            Summary information about artifacts.
        """
        artifacts = self.list_artifacts()

        summary = {
            "total_count": len(artifacts),
            "total_size": sum(a["size"] for a in artifacts),
            "by_type": {},
            "recent_artifacts": artifacts[:5],  # 5 most recent
        }

        # Group by type
        for artifact in artifacts:
            artifact_type = artifact["type"]
            if artifact_type not in summary["by_type"]:
                summary["by_type"][artifact_type] = {"count": 0, "size": 0}

            summary["by_type"][artifact_type]["count"] += 1
            summary["by_type"][artifact_type]["size"] += artifact["size"]

        return summary

    def cleanup_old_artifacts(self, max_age_days: int = 7) -> int:
        """Clean up old artifacts.

        Args:
            max_age_days: Maximum age of artifacts to keep.

        Returns:
            Number of artifacts cleaned up.
        """
        cutoff_time = datetime.now().timestamp() - (max_age_days * 24 * 60 * 60)
        cleaned_count = 0

        for search_path in [self.reports_path, self.logs_path, self.data_path]:
            for file_path in search_path.glob("*"):
                if file_path.is_file() and file_path.stat().st_ctime < cutoff_time:
                    try:
                        file_path.unlink()
                        cleaned_count += 1
                    except Exception as e:
                        print(f"Warning: Failed to delete {file_path}: {e}")

        return cleaned_count

    def _get_artifact_path(self, name: str, content_type: str) -> Path:
        """Determine appropriate path for artifact based on content type."""
        if content_type in ["application/json", "text/html", "text/markdown"]:
            return self.reports_path / name
        elif content_type == "text/plain" and name.endswith(".log"):
            return self.logs_path / name
        elif content_type in ["text/csv", "application/csv"]:
            return self.data_path / name
        elif content_type == "text/plain":
            # Put text files in data directory for listing
            return self.data_path / name
        else:
            return self.artifact_path / name

    def _generate_html_report(self, report_name: str, report_data: dict[str, Any]) -> str:
        """Generate HTML report from data."""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{report_name} Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; }}
        .section {{ margin: 20px 0; }}
        .data {{ background-color: #f9f9f9; padding: 10px; border-radius: 3px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{report_name} Report</h1>
        <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    </div>

    <div class="section">
        <h2>Report Data</h2>
        <div class="data">
            <pre>{json.dumps(report_data, indent=2)}</pre>
        </div>
    </div>
</body>
</html>"""
        return html

    def _generate_markdown_report(self, report_name: str, report_data: dict[str, Any]) -> str:
        """Generate Markdown report from data."""
        markdown = f"""# {report_name} Report

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Report Data

```json
{json.dumps(report_data, indent=2)}
```
"""
        return markdown

    def _generate_csv(self, data: dict | list) -> str:
        """Generate simple CSV from data."""
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            # List of dictionaries
            if not data:
                return ""

            headers = list(data[0].keys())
            csv_lines = [",".join(headers)]

            for row in data:
                values = [str(row.get(header, "")) for header in headers]
                csv_lines.append(",".join(f'"{v}"' for v in values))

            return "\n".join(csv_lines)

        elif isinstance(data, dict):
            # Single dictionary
            headers = ["Key", "Value"]
            csv_lines = [",".join(headers)]

            for key, value in data.items():
                csv_lines.append(f'"{key}","{value}"')

            return "\n".join(csv_lines)

        else:
            # Convert to string
            return str(data)
