"""Comprehensive tests for TemplateEngine to achieve 100% coverage."""

import pytest

from strategy_sandbox.reporting.template_engine import TemplateEngine


class TestTemplateEngine:
    """Test cases for TemplateEngine class."""

    def test_initialization(self):
        """Test TemplateEngine initialization."""
        engine = TemplateEngine()
        assert engine is not None

    def test_render_build_status_basic(self):
        """Test basic build status rendering."""
        engine = TemplateEngine()
        
        context = {
            "build_status": "success",
            "test_results": {"total": 100, "passed": 95, "failed": 5},
            "performance_data": {"results": []},
            "security_data": {"bandit_results": {}},
            "github_env": {
                "GITHUB_WORKFLOW": "CI",
                "GITHUB_RUN_NUMBER": "123",
                "GITHUB_SHA": "abcd1234efgh5678"
            },
            "timestamp": "2024-01-01T12:00:00Z"
        }
        
        result = engine.render_build_status(context)
        
        assert "Build Status Report" in result
        assert "Success" in result
        assert "CI" in result
        assert "#123" in result
        assert "abcd1234" in result
        assert "🧪 Test Results" in result

    def test_render_build_status_with_workflow_url(self):
        """Test build status rendering with workflow URL."""
        engine = TemplateEngine()
        
        context = {
            "build_status": "failure",
            "workflow_url": "https://github.com/user/repo/actions/runs/123",
            "github_env": {},
            "timestamp": "2024-01-01T12:00:00Z"
        }
        
        result = engine.render_build_status(context)
        
        assert "View Run" in result
        assert "https://github.com/user/repo/actions/runs/123" in result

    def test_render_build_status_with_performance_data(self):
        """Test build status rendering with performance data."""
        engine = TemplateEngine()
        
        context = {
            "build_status": "success",
            "performance_data": {
                "results": [
                    {"name": "test1", "execution_time": 0.1, "throughput": 100}
                ]
            },
            "github_env": {},
            "timestamp": "2024-01-01T12:00:00Z"
        }
        
        result = engine.render_build_status(context)
        
        assert "⚡ Performance Metrics" in result

    def test_render_build_status_with_security_data(self):
        """Test build status rendering with security data."""
        engine = TemplateEngine()
        
        context = {
            "build_status": "warning",
            "security_data": {
                "bandit_results": {"metrics": {"_totals": {"SEVERITY.HIGH": 1}}}
            },
            "github_env": {},
            "timestamp": "2024-01-01T12:00:00Z"
        }
        
        result = engine.render_build_status(context)
        
        assert "🔒 Security Scan" in result

    def test_render_performance_summary_basic(self):
        """Test basic performance summary rendering."""
        engine = TemplateEngine()
        
        context = {
            "metrics": {
                "results": [
                    {
                        "name": "api_test",
                        "execution_time": 0.125,
                        "throughput": 1500,
                        "memory_usage": 75.5
                    }
                ]
            },
            "timestamp": "2024-01-01T12:00:00Z"
        }
        
        result = engine.render_performance_summary(context)
        
        assert "Performance Benchmark Report" in result
        assert "api_test" in result
        assert "0.1250s" in result
        assert "1500 ops/sec" in result
        assert "75.5 MB" in result

    def test_render_performance_summary_with_regressions(self):
        """Test performance summary with regression detection."""
        engine = TemplateEngine()
        
        context = {
            "metrics": {
                "regressions_detected": True,
                "regression_details": {
                    "slow_test": {
                        "status": "regression",
                        "severity": "high",
                        "ratio": 2.5
                    },
                    "warning_test": {
                        "status": "warning",
                        "severity": "medium",
                        "ratio": 1.3
                    }
                }
            },
            "timestamp": "2024-01-01T12:00:00Z"
        }
        
        result = engine.render_performance_summary(context)
        
        assert "🚨 Performance Regressions Detected" in result
        assert "slow_test" in result
        assert "high regression" in result
        assert "2.5x slower" in result
        assert "warning_test" in result
        assert "medium performance warning" in result

    def test_render_performance_summary_with_summary_stats(self):
        """Test performance summary with summary statistics."""
        engine = TemplateEngine()
        
        context = {
            "metrics": {
                "summary_stats": {
                    "average_execution_time": 0.125,
                    "total_throughput": 5000,
                    "memory_peak": 100.5
                }
            },
            "timestamp": "2024-01-01T12:00:00Z"
        }
        
        result = engine.render_performance_summary(context)
        
        assert "Summary Statistics" in result
        assert "Average Execution Time" in result
        assert "0.1250" in result
        assert "Total Throughput" in result
        assert "5000" in result

    def test_render_performance_summary_with_baseline_comparison(self):
        """Test performance summary with baseline comparison."""
        engine = TemplateEngine()
        
        context = {
            "metrics": {},
            "comparison": {
                "comparisons": [
                    {
                        "name": "api_test",
                        "execution_time": {
                            "change_direction": "regression",
                            "change_percent": 25.0,
                            "current": 0.125,
                            "baseline": 0.100
                        },
                        "memory_usage": {
                            "change_direction": "improvement",
                            "change_percent": -10.0,
                            "current": 90.0,
                            "baseline": 100.0
                        },
                        "throughput": {
                            "change_direction": "stable",
                            "change_percent": 0.0,
                            "current": 1000.0,
                            "baseline": 1000.0
                        }
                    }
                ]
            },
            "timestamp": "2024-01-01T12:00:00Z"
        }
        
        result = engine.render_performance_summary(context)
        
        assert "📊 Baseline Comparison" in result
        assert "api_test" in result
        assert "🔴" in result  # Regression icon
        assert "🟢" in result  # Improvement icon
        assert "⚪" in result  # Stable icon
        assert "25.0%" in result
        assert "-10.0%" in result

    def test_render_security_summary_basic(self):
        """Test basic security summary rendering."""
        engine = TemplateEngine()
        
        context = {
            "bandit_results": {
                "metrics": {
                    "_totals": {
                        "SEVERITY.HIGH": 2,
                        "SEVERITY.MEDIUM": 3,
                        "SEVERITY.LOW": 1
                    }
                },
                "results": [
                    {
                        "issue_severity": "HIGH",
                        "issue_confidence": "HIGH",
                        "issue_text": "Use of insecure MD5 hash",
                        "filename": "test.py",
                        "line_number": 42
                    }
                ]
            },
            "timestamp": "2024-01-01T12:00:00Z"
        }
        
        result = engine.render_security_summary(context)
        
        assert "Security Scan Report" in result
        assert "Static Code Analysis" in result
        assert "🔴 High | 2" in result
        assert "🟡 Medium | 3" in result
        assert "🟢 Low | 1" in result
        assert "⚠️ **High severity issues found!**" in result
        assert "Use of insecure MD5 hash" in result
        assert "test.py:42" in result

    def test_render_security_summary_with_vulnerabilities(self):
        """Test security summary with dependency vulnerabilities."""
        engine = TemplateEngine()
        
        context = {
            "pip_audit_results": {
                "dependencies": [
                    {
                        "name": "vulnerable-package",
                        "version": "1.0.0",
                        "vulns": [
                            {
                                "id": "CVE-2024-1234",
                                "description": "Critical vulnerability in package",
                                "fix_versions": ["1.1.0", "2.0.0"]
                            }
                        ]
                    },
                    {
                        "name": "safe-package",
                        "version": "2.0.0",
                        "vulns": []
                    }
                ]
            },
            "timestamp": "2024-01-01T12:00:00Z"
        }
        
        result = engine.render_security_summary(context)
        
        assert "Dependency Vulnerabilities" in result
        assert "⚠️ **1 vulnerable dependencies found!**" in result
        assert "vulnerable-package v1.0.0" in result
        assert "CVE-2024-1234" in result
        assert "Critical vulnerability in package" in result
        assert "Fix available in: 1.1.0, 2.0.0" in result

    def test_render_security_summary_no_vulnerabilities(self):
        """Test security summary with no vulnerabilities found."""
        engine = TemplateEngine()
        
        context = {
            "pip_audit_results": {
                "dependencies": [
                    {"name": "safe-package1", "vulns": []},
                    {"name": "safe-package2", "vulns": []}
                ]
            },
            "timestamp": "2024-01-01T12:00:00Z"
        }
        
        result = engine.render_security_summary(context)
        
        assert "✅ **No vulnerabilities found in 2 dependencies.**" in result

    def test_render_security_summary_many_issues(self):
        """Test security summary with many issues (truncation)."""
        engine = TemplateEngine()
        
        # Create more than 5 bandit results
        bandit_results = []
        for i in range(7):
            bandit_results.append({
                "issue_severity": "MEDIUM",
                "issue_confidence": "HIGH",
                "issue_text": f"Issue {i}",
                "filename": f"file{i}.py",
                "line_number": i
            })
        
        # Create more than 5 vulnerable dependencies
        vulnerable_deps = []
        for i in range(7):
            vulnerable_deps.append({
                "name": f"package{i}",
                "version": "1.0.0",
                "vulns": [{"id": f"CVE-2024-{i}", "description": f"Vulnerability {i}"}]
            })
        
        context = {
            "bandit_results": {
                "metrics": {"_totals": {"SEVERITY.MEDIUM": 7}},
                "results": bandit_results
            },
            "pip_audit_results": {
                "dependencies": vulnerable_deps
            },
            "timestamp": "2024-01-01T12:00:00Z"
        }
        
        result = engine.render_security_summary(context)
        
        assert "... and 2 more issues" in result
        assert "... and 2 more vulnerable dependencies" in result

    def test_render_test_results_comprehensive(self):
        """Test comprehensive test results rendering."""
        engine = TemplateEngine()
        
        test_results = {
            "total": 120,
            "passed": 100,
            "failed": 15,
            "skipped": 5,
            "duration": 45.67
        }
        
        result = engine._render_test_results(test_results)
        
        assert "**Total Tests**: 120" in result
        assert "**Passed**: ✅ 100" in result
        assert "**Failed**: ❌ 15" in result
        assert "**Skipped**: ⏭️ 5" in result
        assert "**Duration**: 45.67s" in result
        assert "**Pass Rate**: 83.3%" in result

    def test_render_test_results_empty(self):
        """Test test results rendering with empty data."""
        engine = TemplateEngine()
        
        result = engine._render_test_results({})
        
        assert "*No test results available.*" in result

    def test_render_test_results_no_failures_or_skipped(self):
        """Test test results rendering without failures or skipped tests."""
        engine = TemplateEngine()
        
        test_results = {
            "total": 100,
            "passed": 100,
            "failed": 0,
            "skipped": 0,
            "duration": 30.0
        }
        
        result = engine._render_test_results(test_results)
        
        assert "**Failed**" not in result
        assert "**Skipped**" not in result
        assert "**Pass Rate**: 100.0%" in result

    def test_render_performance_summary_helper(self):
        """Test performance summary helper method."""
        engine = TemplateEngine()
        
        performance_data = {
            "results": [
                {"name": "test1", "execution_time": 0.1, "throughput": 1000},
                {"name": "test2", "execution_time": 0.2},
                {"name": "test3", "execution_time": 0.3, "throughput": 500},
                {"name": "test4", "execution_time": 0.4}  # This should be truncated
            ]
        }
        
        result = engine._render_performance_summary(performance_data)
        
        assert "test1" in result
        assert "test2" in result 
        assert "test3" in result
        assert "... and 1 more benchmarks" in result
        assert "test4" not in result

    def test_render_performance_summary_empty(self):
        """Test performance summary with empty data."""
        engine = TemplateEngine()
        
        result = engine._render_performance_summary({})
        
        assert "*No performance data available.*" in result

    def test_render_performance_summary_no_results(self):
        """Test performance summary with no results."""
        engine = TemplateEngine()
        
        performance_data = {"results": []}
        
        result = engine._render_performance_summary(performance_data)
        
        assert "*No benchmark results available.*" in result

    def test_render_security_summary_helper(self):
        """Test security summary helper method."""
        engine = TemplateEngine()
        
        security_data = {
            "bandit_results": {
                "metrics": {
                    "_totals": {
                        "SEVERITY.HIGH": 1,
                        "SEVERITY.MEDIUM": 2,
                        "SEVERITY.LOW": 3
                    }
                }
            },
            "pip_audit_results": {
                "dependencies": [
                    {"name": "pkg1", "vulns": [{"id": "CVE-1"}]},
                    {"name": "pkg2", "vulns": []},
                    {"name": "pkg3", "vulns": [{"id": "CVE-2"}, {"id": "CVE-3"}]}
                ]
            }
        }
        
        result = engine._render_security_summary(security_data)
        
        assert "⚠️ 1 high, 2 medium, 3 low severity issues" in result
        assert "⚠️ 2 vulnerable packages" in result

    def test_render_security_summary_medium_only(self):
        """Test security summary with only medium severity issues."""
        engine = TemplateEngine()
        
        security_data = {
            "bandit_results": {
                "metrics": {
                    "_totals": {
                        "SEVERITY.HIGH": 0,
                        "SEVERITY.MEDIUM": 2,
                        "SEVERITY.LOW": 1
                    }
                }
            }
        }
        
        result = engine._render_security_summary(security_data)
        
        assert "⚠️ 2 medium, 1 low severity issues" in result

    def test_render_security_summary_clean(self):
        """Test security summary with no issues."""
        engine = TemplateEngine()
        
        security_data = {
            "bandit_results": {
                "metrics": {
                    "_totals": {
                        "SEVERITY.HIGH": 0,
                        "SEVERITY.MEDIUM": 0,
                        "SEVERITY.LOW": 1
                    }
                }
            },
            "pip_audit_results": {
                "dependencies": [
                    {"name": "pkg1", "vulns": []},
                    {"name": "pkg2", "vulns": []}
                ]
            }
        }
        
        result = engine._render_security_summary(security_data)
        
        assert "✅ No high/medium severity issues" in result
        assert "✅ 2 packages scanned, no vulnerabilities" in result

    def test_render_security_summary_empty(self):
        """Test security summary with empty data."""
        engine = TemplateEngine()
        
        result = engine._render_security_summary({})
        
        assert "*No security scan data available.*" in result

    def test_get_status_info_all_statuses(self):
        """Test status info for all status types."""
        engine = TemplateEngine()
        
        success_info = engine._get_status_info("success")
        assert success_info["emoji"] == "✅"
        assert "success-brightgreen" in success_info["badge"]
        
        failure_info = engine._get_status_info("failure")
        assert failure_info["emoji"] == "❌"
        assert "failure-red" in failure_info["badge"]
        
        warning_info = engine._get_status_info("warning")
        assert warning_info["emoji"] == "⚠️"
        assert "warning-orange" in warning_info["badge"]
        
        unknown_info = engine._get_status_info("unknown")
        assert unknown_info["emoji"] == "❓"
        assert "unknown-lightgrey" in unknown_info["badge"]

    def test_get_performance_icon(self):
        """Test performance change icons."""
        engine = TemplateEngine()
        
        assert engine._get_performance_icon("improvement") == "🟢"
        assert engine._get_performance_icon("regression") == "🔴"
        assert engine._get_performance_icon("stable") == "⚪"
        assert engine._get_performance_icon("unknown") == "⚪"

    def test_get_severity_icon(self):
        """Test security severity icons."""
        engine = TemplateEngine()
        
        assert engine._get_severity_icon("HIGH") == "🔴"
        assert engine._get_severity_icon("MEDIUM") == "🟡"
        assert engine._get_severity_icon("LOW") == "🟢"
        assert engine._get_severity_icon("UNKNOWN") == "⚪"

    def test_format_timestamp_valid(self):
        """Test timestamp formatting with valid timestamp."""
        engine = TemplateEngine()
        
        timestamp = "2024-01-01T12:00:00Z"
        result = engine._format_timestamp(timestamp)
        
        assert "2024-01-01" in result
        assert "12:00:00" in result
        assert "UTC" in result

    def test_format_timestamp_empty(self):
        """Test timestamp formatting with empty timestamp."""
        engine = TemplateEngine()
        
        result = engine._format_timestamp("")
        
        assert result == "Unknown"

    def test_format_timestamp_invalid(self):
        """Test timestamp formatting with invalid timestamp."""
        engine = TemplateEngine()
        
        invalid_timestamp = "not-a-timestamp"
        result = engine._format_timestamp(invalid_timestamp)
        
        assert result == invalid_timestamp

    def test_format_timestamp_isoformat_without_z(self):
        """Test timestamp formatting with ISO format without Z."""
        engine = TemplateEngine()
        
        timestamp = "2024-01-01T12:00:00+00:00"
        result = engine._format_timestamp(timestamp)
        
        assert "2024-01-01" in result
        assert "12:00:00" in result
        assert "UTC" in result