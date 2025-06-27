"""Artifact management for GitHub Actions workflow integration."""

import json
import shutil
from datetime import datetime, timedelta
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
        self.artifact_path = self.base_path  # For backward compatibility
        self.base_path.mkdir(exist_ok=True)

        # Create subdirectories for different artifact types
        self.reports_path = self.base_path / "reports"
        self.logs_path = self.base_path / "logs"
        self.data_path = self.base_path / "data"

        self.reports_path.mkdir(exist_ok=True)
        self.logs_path.mkdir(exist_ok=True)
        self.data_path.mkdir(exist_ok=True)

    def create_artifact(
        self, filename: str, content: str | bytes | dict | Any, content_type: str = "text/plain"
    ) -> Path:
        """Create and save an artifact.

        :param filename: The name of the artifact file.
        :param content: The content of the artifact (string, bytes, dict, or any serializable object).
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

        # Handle content serialization
        if isinstance(content, dict | list) or (
            content_type == "application/json" and not isinstance(content, str | bytes)
        ):
            # Serialize JSON content
            content = json.dumps(content, indent=2, default=str)

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
        artifacts.sort(key=lambda x: str(x["created"]), reverse=True)
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

    def _generate_html_report(self, report_name: str, report_data: dict[str, Any]) -> str:
        """Generate HTML report from data.

        Args:
            report_name: Name of the report.
            report_data: Report data.

        Returns:
            HTML content.
        """
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>{report_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f4f4f4; padding: 10px; border-radius: 5px; }}
        .data {{ margin: 20px 0; }}
        pre {{ background-color: #f8f8f8; padding: 10px; border-radius: 3px; overflow-x: auto; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{report_name}</h1>
        <p>Generated: {datetime.now().isoformat()}</p>
    </div>
    <div class="data">
        <h2>Report Data</h2>
        <pre>{json.dumps(report_data, indent=2, default=str)}</pre>
    </div>
</body>
</html>"""
        return html_content

    def _generate_markdown_report(self, report_name: str, report_data: dict[str, Any]) -> str:
        """Generate Markdown report from data.

        Args:
            report_name: Name of the report.
            report_data: Report data.

        Returns:
            Markdown content.
        """
        md_content = f"""# {report_name}

**Generated:** {datetime.now().isoformat()}

## Report Data

```json
{json.dumps(report_data, indent=2, default=str)}
```
"""
        return md_content

    def _generate_csv(self, data: dict | list) -> str:
        """Generate CSV content from data.

        Args:
            data: Data to convert to CSV.

        Returns:
            CSV content.
        """
        if isinstance(data, dict):
            # Convert dict to CSV with keys as headers
            if not data:
                return ""
            headers = list(data.keys())
            values = [str(data[key]) for key in headers]
            return ",".join(headers) + "\n" + ",".join(values)
        elif isinstance(data, list):
            # Convert list of dicts to CSV
            if not data or not isinstance(data[0], dict):
                return str(data)
            headers = list(data[0].keys())
            csv_lines = [",".join(headers)]
            for row in data:
                values = [str(row.get(key, "")) for key in headers]
                csv_lines.append(",".join(values))
            return "\n".join(csv_lines)
        else:
            return str(data)
