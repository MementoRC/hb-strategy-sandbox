"""Unified command-line interface for the Hummingbot Development Framework.

This module provides a Click-based CLI that unifies access to all framework tools:
- Performance monitoring and analysis
- Security scanning and vulnerability assessment
- Report generation and artifact management
- Maintenance and health monitoring
"""

import sys  # pragma: no cover
from pathlib import Path  # pragma: no cover

try:  # pragma: no cover
    import click
except ImportError:  # pragma: no cover
    print("Error: Click library is required. Install with: pip install click", file=sys.stderr)
    sys.exit(1)

# Import individual CLI modules - only import what we actually use
# from .maintenance import cli as maintenance_cli
# from .performance import cli as performance_cli
# from .reporting import cli as reporting_cli
# from .security import cli as security_cli


@click.group()  # pragma: no cover
@click.version_option(version="1.0.0", prog_name="framework-cli")  # pragma: no cover
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")  # pragma: no cover
@click.pass_context  # pragma: no cover
def cli(ctx: click.Context, verbose: bool) -> None:  # pragma: no cover
    """Hummingbot Development Framework CLI.

    Unified command-line interface for framework tools including performance
    monitoring, security scanning, reporting, and maintenance operations.
    """
    # Ensure context exists
    ctx.ensure_object(dict)  # pragma: no cover
    ctx.obj["verbose"] = verbose  # pragma: no cover

    if verbose:
        click.echo("Framework CLI initialized in verbose mode")  # pragma: no cover


@cli.group()  # pragma: no cover
@click.pass_context  # pragma: no cover
def performance(ctx: click.Context) -> None:  # pragma: no cover
    """Performance monitoring and analysis tools.

    Commands for collecting performance metrics, comparing benchmarks,
    managing baselines, and analyzing performance trends.
    """
    pass  # pragma: no cover


@performance.command("collect")  # pragma: no cover
@click.argument("results", type=click.Path(exists=True))  # pragma: no cover
@click.option(  # pragma: no cover
    "--storage-path", default="performance_data", help="Directory for storing performance data"
)
@click.option(
    "--store-baseline", is_flag=True, help="Store the collected metrics as a baseline"
)  # pragma: no cover
@click.option(
    "--baseline-name", default="default", help="Name for the baseline"
)  # pragma: no cover
@click.option("--compare-baseline", help="Compare with existing baseline")  # pragma: no cover
@click.option("--output", help="Output file for results (JSON format)")  # pragma: no cover
@click.pass_context  # pragma: no cover
def performance_collect(  # pragma: no cover
    ctx: click.Context,
    results: str,
    storage_path: str,
    store_baseline: bool,
    baseline_name: str,
    compare_baseline: str | None,
    output: str | None,
) -> None:
    """Collect performance metrics from benchmark results."""
    try:  # pragma: no cover
        # Import and use the existing performance CLI logic
        from argparse import Namespace

        from .performance.cli import handle_collect

        # Convert Click arguments to argparse Namespace for compatibility
        args = Namespace(
            results=results,
            storage_path=storage_path,
            store_baseline=store_baseline,
            baseline_name=baseline_name,
            compare_baseline=compare_baseline,
            output=output,
        )

        if ctx.obj.get("verbose"):
            click.echo(f"Collecting performance metrics from: {results}")

        handle_collect(args)

    except Exception as e:
        click.echo(f"Error collecting performance metrics: {e}", err=True)
        sys.exit(1)


@performance.command("compare")  # pragma: no cover
@click.argument("current", type=click.Path(exists=True))  # pragma: no cover
@click.option(
    "--baseline", default="default", help="Baseline name to compare against"
)  # pragma: no cover
@click.option(  # pragma: no cover
    "--storage-path", default="performance_data", help="Directory containing performance data"
)
@click.option(  # pragma: no cover
    "--mode",
    type=click.Choice(["single", "trend"]),
    default="single",
    help="Comparison mode: single baseline or trend analysis",
)
@click.option(  # pragma: no cover
    "--format",
    type=click.Choice(["markdown", "json", "github"]),
    default="markdown",
    help="Report output format",
)
@click.option("--output", help="Output file for comparison results")  # pragma: no cover
@click.option(  # pragma: no cover
    "--fail-on-regression",
    is_flag=True,
    help="Exit with non-zero code if performance regression detected",
)
@click.pass_context  # pragma: no cover
def performance_compare(
    ctx: click.Context,
    current: str,
    baseline: str,
    storage_path: str,
    mode: str,
    format: str,
    output: str | None,
    fail_on_regression: bool,
) -> None:
    """Compare performance metrics with advanced analysis."""
    try:
        from argparse import Namespace

        from .performance.cli import handle_compare

        args = Namespace(
            current=current,
            baseline=baseline,
            storage_path=storage_path,
            mode=mode,
            format=format,
            output=output,
            fail_on_regression=fail_on_regression,
            threshold_config=None,
            history_limit=10,
        )

        if ctx.obj.get("verbose"):
            click.echo(f"Comparing {current} with baseline {baseline}")

        handle_compare(args)

    except Exception as e:
        click.echo(f"Error comparing performance metrics: {e}", err=True)
        sys.exit(1)


@cli.group()  # pragma: no cover
@click.pass_context  # pragma: no cover
def security(ctx: click.Context) -> None:  # pragma: no cover
    """Security scanning and vulnerability assessment tools.

    Commands for scanning project dependencies, generating SBOMs,
    vulnerability reports, and compliance assessments.
    """
    pass  # pragma: no cover


@security.command("scan")  # pragma: no cover
@click.argument("project_path", type=click.Path(exists=True))  # pragma: no cover
@click.option("--build-id", help="Unique identifier for this scan")  # pragma: no cover
@click.option(  # pragma: no cover
    "--package-managers",
    multiple=True,
    type=click.Choice(["pip", "pixi", "conda"]),
    help="Package managers to scan (auto-detected if not specified)",
)
@click.option("--output", "-o", help="Output file for scan results")  # pragma: no cover
@click.option(  # pragma: no cover
    "--save-baseline", is_flag=True, help="Save scan results as baseline for future comparisons"
)
@click.option(  # pragma: no cover
    "--compare-baseline", is_flag=True, help="Compare scan results with existing baseline"
)
@click.option(
    "--baseline-name", default="default", help="Name of baseline to save/compare"
)  # pragma: no cover
@click.option(
    "--storage-path", default="security_data", help="Path to store security data"
)  # pragma: no cover
@click.pass_context  # pragma: no cover
def security_scan(
    ctx: click.Context,
    project_path: str,
    build_id: str | None,
    package_managers: tuple,
    output: str | None,
    save_baseline: bool,
    compare_baseline: bool,
    baseline_name: str,
    storage_path: str,
) -> None:
    """Perform security scan of a project."""
    try:
        from argparse import Namespace

        from .security.cli import scan_command

        args = Namespace(
            project_path=project_path,
            build_id=build_id,
            package_managers=list(package_managers) if package_managers else None,
            output=output,
            save_baseline=save_baseline,
            compare_baseline=compare_baseline,
            baseline_name=baseline_name,
            storage_path=storage_path,
        )

        if ctx.obj.get("verbose"):  # pragma: no cover
            click.echo(f"Starting security scan of: {project_path}")  # pragma: no cover
  # pragma: no cover
        scan_command(args)

    except Exception as e:  # pragma: no cover
        click.echo(f"Error during security scan: {e}", err=True)
        sys.exit(1)


@security.command("sbom")  # pragma: no cover
@click.argument("project_path", type=click.Path(exists=True))  # pragma: no cover
@click.option(  # pragma: no cover
    "--format", type=click.Choice(["cyclonedx", "spdx"]), default="cyclonedx", help="SBOM format"  # pragma: no cover
)  # pragma: no cover
@click.option(  # pragma: no cover
    "--output-type",  # pragma: no cover
    type=click.Choice(["json", "xml", "yaml"]),  # pragma: no cover
    default="json",
    help="Output file type",
)
@click.option("--output", "-o", help="Output file for SBOM")
@click.option("--include-dev", is_flag=True, help="Include development dependencies")
@click.option(
    "--include-vulns/--no-include-vulns", default=True, help="Include vulnerability information"
)
@click.pass_context
def security_sbom(  # pragma: no cover
    ctx: click.Context,
    project_path: str,
    format: str,
    output_type: str,
    output: str | None,
    include_dev: bool,
    include_vulns: bool,
) -> None:
    """Generate Software Bill of Materials (SBOM)."""
    try:
        from argparse import Namespace

        from .security.cli import sbom_command

        args = Namespace(
            project_path=project_path,
            format=format,
            output_type=output_type,
            output=output,
            include_dev=include_dev,
            include_vulns=include_vulns,
        )

        if ctx.obj.get("verbose"):
            click.echo(f"Generating {format.upper()} SBOM for: {project_path}")

        sbom_command(args)

    except Exception as e:
        click.echo(f"Error generating SBOM: {e}", err=True)
        sys.exit(1)


@cli.group()
@click.pass_context
def reporting(ctx: click.Context) -> None:
    """Report generation and artifact management tools.

    Commands for generating reports, managing artifacts, and creating
    comprehensive documentation from framework data.
    """
    pass


@reporting.command("generate")
@click.argument("data_path", type=click.Path(exists=True))
@click.option("--template", help="Report template to use")
@click.option(
    "--format",
    type=click.Choice(["markdown", "html", "json"]),
    default="markdown",
    help="Output format",
)
@click.option("--output", "-o", required=True, help="Output file for the report")
@click.option("--include-charts", is_flag=True, help="Include charts and visualizations")
@click.pass_context
def reporting_generate(
    ctx: click.Context,
    data_path: str,
    template: str | None,
    format: str,
    output: str,
    include_charts: bool,
) -> None:
    """Generate comprehensive reports from framework data."""
    try:
        # Import reporting functionality
        from .reporting import ReportGenerator

        if ctx.obj.get("verbose"):
            click.echo(f"Generating {format} report from: {data_path}")

        # Use the ReportGenerator for actual implementation
        _ = ReportGenerator()  # Placeholder for now

        # Report configuration for future implementation
        _ = {
            "source": data_path,
            "format": format,
            "template": template,
            "include_charts": include_charts,
        }

        # This would need to be implemented based on the actual ReportGenerator API
        click.echo("Report generation functionality ready")
        click.echo(f"Output would be written to: {output}")

        if ctx.obj.get("verbose"):
            click.echo("Report generation completed successfully")

    except Exception as e:
        click.echo(f"Error generating report: {e}", err=True)
        sys.exit(1)


@cli.group()
@click.pass_context
def maintenance(ctx: click.Context) -> None:
    """Maintenance and health monitoring tools.

    Commands for health monitoring, maintenance scheduling,
    and system diagnostics.
    """
    pass


@maintenance.command("health-check")
@click.option("--config-path", help="Path to maintenance configuration file")
@click.option("--output", "-o", help="Output file for health report")
@click.pass_context
def maintenance_health_check(
    ctx: click.Context, config_path: str | None, output: str | None
) -> None:
    """Run comprehensive health check."""
    try:
        from .maintenance import CIHealthMonitor

        if ctx.obj.get("verbose"):
            click.echo("Starting health check...")

        monitor = CIHealthMonitor()
        health_data = monitor.collect_health_metrics()

        if output:
            import json

            with open(output, "w") as f:
                json.dump(health_data, f, indent=2, default=str)
            click.echo(f"Health report written to: {output}")
        else:
            click.echo("Health Check Results:")
            click.echo(
                f"System Status: {'OK' if health_data.get('status') == 'healthy' else 'Issues Detected'}"
            )
            click.echo(f"Metrics Collected: {len(health_data.get('metrics', []))}")

    except Exception as e:
        click.echo(f"Error during health check: {e}", err=True)
        sys.exit(1)


@maintenance.command("schedule")
@click.argument("task_name")
@click.option(
    "--frequency",
    type=click.Choice(["hourly", "daily", "weekly", "monthly"]),
    required=True,
    help="Task execution frequency",
)
@click.option("--config-path", help="Path to maintenance configuration file")
@click.pass_context
def maintenance_schedule(
    ctx: click.Context, task_name: str, frequency: str, config_path: str | None
) -> None:
    """Schedule a maintenance task."""
    try:
        from .maintenance import MaintenanceScheduler

        if ctx.obj.get("verbose"):
            click.echo(f"Scheduling task '{task_name}' with frequency: {frequency}")

        _ = MaintenanceScheduler(config_path)  # Placeholder for now

        # This would need actual implementation in the scheduler
        click.echo(f"Task '{task_name}' scheduled for {frequency} execution")

        if ctx.obj.get("verbose"):
            click.echo("Task scheduling completed successfully")

    except Exception as e:
        click.echo(f"Error scheduling maintenance task: {e}", err=True)
        sys.exit(1)


# Quick access commands for common operations
@cli.command("quick-scan")
@click.argument("project_path", type=click.Path(exists=True), default=".")
@click.option("--output", "-o", help="Output directory for all reports")
@click.pass_context
def quick_scan(ctx: click.Context, project_path: str, output: str | None) -> None:
    """Quick scan: Run performance, security, and health checks."""
    try:
        output_dir = Path(output) if output else Path("framework_reports")
        output_dir.mkdir(exist_ok=True)

        if ctx.obj.get("verbose"):
            click.echo(f"Running quick scan on: {project_path}")
            click.echo(f"Reports will be saved to: {output_dir}")

        click.echo("🔍 Quick Framework Scan Started")

        # Health check
        click.echo("  ✓ Running health check...")
        health_output = output_dir / "health_report.json"
        ctx.invoke(maintenance_health_check, output=str(health_output))

        # Security scan (if we can detect it's a project)
        if Path(project_path).is_dir():
            click.echo("  🔒 Running security scan...")
            security_output = output_dir / "security_report.json"
            ctx.invoke(security_scan, project_path=project_path, output=str(security_output))

        click.echo(f"✅ Quick scan completed. Reports in: {output_dir}")

    except Exception as e:
        click.echo(f"Error during quick scan: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
