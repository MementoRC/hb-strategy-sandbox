"""Advanced trend analysis and alerting system for performance data."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, TypedDict

import numpy as np

from .comparator import AlertSeverity, PerformanceAlert


class BenchmarkData(TypedDict):
    """Type definition for benchmark data storage."""

    values: list[float]
    timestamps: list[datetime]


@dataclass
class TrendData:
    """Historical trend data for a specific metric."""

    metric_name: str
    benchmark_name: str
    values: list[float] = field(default_factory=list)
    timestamps: list[datetime] = field(default_factory=list)
    correlation: float = 0.0
    trend_direction: str = "stable"  # "increasing", "decreasing", "stable"
    moving_average: list[float] = field(default_factory=list)
    anomaly_scores: list[float] = field(default_factory=list)


@dataclass
class AlertCooldown:
    """Cooldown tracking for alert generation."""

    benchmark_name: str
    metric_name: str
    last_alert_time: datetime
    severity: AlertSeverity


@dataclass
class TrendAlert(PerformanceAlert):
    """Extended performance alert with trend analysis data."""

    trend_direction: str = "unknown"
    trend_strength: float = 0.0
    anomaly_score: float = 0.0
    historical_context: str = ""
    root_cause_indicators: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


class TrendAnalyzer:
    """Analyzes performance trends from historical benchmark data.

    This class provides functionality to analyze performance trends over time
    from a collection of historical benchmark results. It uses statistical methods
    like linear regression to determine the direction and strength of trends
    for various performance metrics (e.g., execution time, memory usage, throughput).
    It can help identify performance degradations or improvements that occur gradually
    across multiple builds.
    """

    def __init__(
        self, historical_data: list[dict[str, Any]] = None, alert_config_path: str | Path = None
    ):
        """Initialize the trend analyzer.

        :param historical_data: A list of historical benchmark results. Defaults to empty list.
        :param alert_config_path: Path to alert configuration file (for backward compatibility).
        """
        self.historical_data = historical_data or []
        self.alert_config_path = alert_config_path

    def analyze(self) -> str:
        """Basic analysis method for backward compatibility.

        :return: Simple analysis summary.
        """
        if not self.historical_data:
            return "no historical data"
        else:
            return f"{len(self.historical_data)} data point{'s' if len(self.historical_data) != 1 else ''}"

    def analyze_metric_trend(self, metric_name: str) -> dict[str, Any] | None:
        """Analyze the trend of a specific performance metric.

        :param metric_name: The name of the metric to analyze (e.g., 'execution_time').
        :return: A dictionary with trend analysis results, or None if not enough data.
        """
        # Extract metric values from historical data
        metric_values = []
        for data_point in self.historical_data:
            # Assuming data is structured with a top-level key for each benchmark
            for _benchmark_name, benchmark_data in data_point.items():
                if isinstance(benchmark_data, dict) and metric_name in benchmark_data:
                    metric_values.append(benchmark_data[metric_name])

        if len(metric_values) < 3:
            return None  # Not enough data for meaningful trend analysis

        # Calculate trend using linear regression
        x = np.arange(len(metric_values))
        y = np.array(metric_values)

        # Fit a linear model (y = mx + c)
        slope, _ = np.polyfit(x, y, 1)

        # Determine trend direction
        if abs(slope) < 0.01 * np.mean(y):  # Threshold for stability
            trend_direction = "stable"
        elif slope > 0:
            trend_direction = "increasing"  # Worsening for time/memory, improving for throughput
        else:
            trend_direction = "decreasing"

        # Calculate percentage change
        first_value = metric_values[0]
        last_value = metric_values[-1]
        if first_value != 0:
            percentage_change = ((last_value - first_value) / first_value) * 100
        else:
            percentage_change = 0

        # Calculate volatility (standard deviation as a percentage of the mean)
        volatility = (np.std(y) / np.mean(y)) * 100 if np.mean(y) != 0 else 0

        return {
            "metric_name": metric_name,
            "trend_direction": trend_direction,
            "slope": slope,
            "percentage_change": percentage_change,
            "volatility_percent": volatility,
            "historical_values": metric_values,
            "mean": np.mean(y),
            "median": np.median(y),
            "std_dev": np.std(y),
        }

    def generate_trend_summary(self) -> dict[str, Any]:
        """Generate a summary of trends for all key metrics.

        :return: A dictionary containing trend summaries for key metrics.
        """
        if not self.historical_data:
            return {}

        # Identify all unique metrics from the historical data
        key_metrics: set[str] = set()
        for data_point in self.historical_data:
            for benchmark_data in data_point.values():
                if isinstance(benchmark_data, dict):
                    key_metrics.update(benchmark_data.keys())

        trend_summary = {}
        for metric in key_metrics:
            trend = self.analyze_metric_trend(metric)
            if trend:
                trend_summary[metric] = trend

        return trend_summary
