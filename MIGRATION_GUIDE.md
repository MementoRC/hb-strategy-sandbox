# 🚀 **Framework Migration Guide**

## 📋 **Overview**

This guide helps you transition from the pre-0.2.0 project structure to the new framework-aware architecture introduced in version 0.2.0.

## ✅ **What Changed**

### **Framework Extraction Complete**

Version 0.2.0 completes the **Phase 2: Framework Extraction** migration, moving shared development tools from `strategy_sandbox` to a dedicated `framework` package.

**New Structure:**
```
├── strategy_sandbox/          # 🎯 Business Logic (Strategy Features)
│   ├── core/                 # Core strategy logic
│   ├── balance/              # Balance management
│   ├── markets/              # Market simulation
│   └── events/               # Event system
└── framework/                # 🛠️ Shared Development Tools
    ├── performance/          # Performance monitoring
    ├── security/             # Security scanning  
    ├── reporting/            # Report generation
    └── maintenance/          # System maintenance
```

## 🔄 **Migration Options**

### **Option 1: No Action Required (Recommended for Most Users)**

**✅ Your existing code continues to work unchanged.**

All existing imports remain functional:
```python
# These imports still work exactly as before
from strategy_sandbox.performance.collector import PerformanceCollector
from strategy_sandbox.security.analyzer import DependencyAnalyzer
from strategy_sandbox.reporting.github_reporter import GitHubReporter
from strategy_sandbox.maintenance.health_monitor import CIHealthMonitor
```

### **Option 2: Migrate to Framework Imports (Optional)**

For improved modularity and future-proofing, you can optionally migrate to the new framework imports:

```python
# New framework imports (optional but recommended)
from framework.performance.collector import PerformanceCollector
from framework.security.analyzer import DependencyAnalyzer  
from framework.reporting.github_reporter import GitHubReporter
from framework.maintenance.health_monitor import CIHealthMonitor
```

## 📚 **Migration Examples**

### **Performance Monitoring**

```python
# Before (still works)
from strategy_sandbox.performance.collector import PerformanceCollector
from strategy_sandbox.performance.comparator import PerformanceComparator

# After (optional migration)
from framework.performance.collector import PerformanceCollector
from framework.performance.comparator import PerformanceComparator

# Usage remains identical
collector = PerformanceCollector(storage_path="./metrics")
collector.collect_benchmark_data("test_run", {"execution_time": 1.5})
```

### **Security Scanning**

```python
# Before (still works)
from strategy_sandbox.security.analyzer import DependencyAnalyzer
from strategy_sandbox.security.dashboard_generator import SecurityDashboardGenerator

# After (optional migration)
from framework.security.analyzer import DependencyAnalyzer
from framework.security.dashboard_generator import SecurityDashboardGenerator

# Usage remains identical
analyzer = DependencyAnalyzer(project_path=".")
vulnerabilities = analyzer.scan_dependencies()
```

### **Report Generation**

```python
# Before (still works)
from strategy_sandbox.reporting.github_reporter import GitHubReporter
from strategy_sandbox.reporting.artifact_manager import ArtifactManager

# After (optional migration) 
from framework.reporting.github_reporter import GitHubReporter
from framework.reporting.artifact_manager import ArtifactManager

# Usage remains identical
reporter = GitHubReporter()
report = reporter.generate_performance_report(metrics_data)
```

### **System Maintenance**

```python
# Before (still works)
from strategy_sandbox.maintenance.health_monitor import CIHealthMonitor
from strategy_sandbox.maintenance.scheduler import MaintenanceScheduler

# After (optional migration)
from framework.maintenance.health_monitor import CIHealthMonitor  
from framework.maintenance.scheduler import MaintenanceScheduler

# Usage remains identical
monitor = CIHealthMonitor(base_dir=".")
health_data = monitor.collect_health_metrics()
```

## 🛠️ **Development Benefits**

### **Enhanced Modularity**

The framework package can now be:
- **Reused** across multiple projects
- **Tested** independently 
- **Developed** in isolation
- **Extended** with new capabilities

### **Improved Project Organization**

Clear separation between:
- **🎯 Business Logic**: Strategy-specific functionality in `strategy_sandbox`
- **🛠️ Shared Tools**: Reusable development utilities in `framework`

### **Future-Ready Architecture**

Foundation prepared for:
- Multi-feature workspace development
- Framework ecosystem expansion
- Plugin and extension systems

## 🧪 **Testing Your Migration**

### **Validation Script**

Test both import approaches work correctly:

```python
# test_migration.py
def test_backward_compatibility():
    """Test that old imports still work."""
    from strategy_sandbox.performance.collector import PerformanceCollector
    from strategy_sandbox.security.analyzer import DependencyAnalyzer
    assert PerformanceCollector is not None
    assert DependencyAnalyzer is not None
    print("✅ Backward compatibility confirmed")

def test_framework_imports():
    """Test that new framework imports work."""
    from framework.performance.collector import PerformanceCollector  
    from framework.security.analyzer import DependencyAnalyzer
    assert PerformanceCollector is not None
    assert DependencyAnalyzer is not None
    print("✅ Framework imports confirmed")

if __name__ == "__main__":
    test_backward_compatibility()
    test_framework_imports()
    print("🎉 Migration validation successful!")
```

Run the validation:
```bash
python test_migration.py
```

### **CLI Validation**

Test that CLI tools still work:
```bash
# These commands should work unchanged
hb-performance --help
hb-security --help  
hb-reporting --help
hb-maintenance --help
```

## 📈 **Performance Impact**

### **No Performance Regression**

Migration maintains identical performance characteristics:
- **✅ Import Speed**: No change in import times
- **✅ Memory Usage**: No additional memory overhead  
- **✅ Execution Speed**: Identical runtime performance
- **✅ Test Suite**: All 297 tests pass with same performance

### **Benchmark Results**

Framework components show consistent performance:
```
Performance Benchmarks (v0.2.0):
├── Simulation Throughput: ~127ms mean (unchanged)
├── Order Processing: <1ms per operation (unchanged)  
├── Balance Operations: <0.5ms per operation (unchanged)
└── Event System: <0.1ms per event (unchanged)
```

## 🚨 **Troubleshooting**

### **Import Errors**

If you encounter import errors:

1. **Verify Installation**: Ensure you have version 0.2.0+
   ```bash
   python -c "import strategy_sandbox; print(strategy_sandbox.__version__)"
   ```

2. **Check Import Paths**: Both old and new paths should work
   ```python
   # Both should succeed
   import strategy_sandbox.performance.collector
   import framework.performance.collector
   ```

3. **Clear Cache**: Remove Python cache files
   ```bash
   find . -name "*.pyc" -delete
   find . -name "__pycache__" -type d -exec rm -rf {} + 
   ```

### **Testing Issues**

If tests fail after migration:

1. **Run Full Test Suite**:
   ```bash
   pytest tests/ framework/tests/
   ```

2. **Check Test Dependencies**:
   ```bash
   pip install -e .[dev]  # or pixi install
   ```

3. **Validate Environment**:
   ```bash
   python -c "from framework.performance.collector import PerformanceCollector; print('✅ Framework ready')"
   ```

## 🎯 **Recommended Migration Timeline**

### **Immediate (Required)**
- **✅ Update to version 0.2.0** - No code changes needed

### **Short Term (Optional)**  
- **🔄 Gradually migrate imports** - As you touch code, consider using framework imports
- **📚 Review documentation** - Familiarize with new structure

### **Long Term (Recommended)**
- **🛠️ Adopt framework patterns** - Design code to leverage framework modularity
- **🧪 Extend framework** - Contribute improvements to shared components

## 📞 **Support**

### **Getting Help**

- **📖 Documentation**: See [README.md](README.md) for latest information
- **🐛 Issues**: Report problems on [GitHub Issues](https://github.com/MementoRC/hb-strategy-sandbox/issues)
- **💬 Discussions**: Join conversations on [GitHub Discussions](https://github.com/MementoRC/hb-strategy-sandbox/discussions)

### **Additional Resources**

- **📋 Changelog**: See [CHANGELOG.md](CHANGELOG.md) for detailed changes
- **🏗️ Architecture**: See [WORKSPACE.md](WORKSPACE.md) for overall project structure  
- **📊 Migration Review**: See [MIGRATION_REVIEW.md](MIGRATION_REVIEW.md) for technical details

---

## ✅ **Summary**

The framework extraction migration provides:

- **🔄 Zero Breaking Changes**: Your existing code works unchanged
- **🛠️ Enhanced Architecture**: Clean separation of concerns  
- **📈 Future Benefits**: Foundation for ecosystem expansion
- **📚 Comprehensive Support**: Documentation and migration tools

**No immediate action required** - the migration is designed to be completely transparent to existing users while providing enhanced capabilities for future development.

**Happy coding with the enhanced framework architecture!** 🚀