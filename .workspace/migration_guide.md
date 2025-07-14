# 🚀 **Workspace Migration Guide**

## 📋 **Overview**

This guide provides step-by-step instructions for migrating from single-feature project to multi-feature workspace architecture.

## 🎯 **Migration Phases**

### **✅ Phase 1: Planning and Preparation** (Current)

#### **Completed Tasks**
- [x] Create workspace planning documentation
- [x] Component classification and mapping
- [x] Validation scripts preparation
- [x] Workspace configuration template
- [x] Migration guide creation

#### **Phase 1 Validation**
```bash
# Run validation script to ensure readiness for Phase 2
python .workspace/scripts/validate_current_state.py

# Expected output:
# ✅ Validation complete - project ready for workspace migration!
```

#### **Quality Baseline**
Current project demonstrates excellent quality standards:
- ✅ **337 tests passing** (100% pass rate)
- ✅ **Zero critical violations** (F,E9 linting)
- ✅ **Comprehensive CI/CD** pipeline
- ✅ **Complete documentation** and examples

### **🔄 Phase 2: Framework Extraction** (Next)

#### **Objectives**
- Extract framework components into separate package
- Maintain backward compatibility during transition
- Validate all functionality preserved

#### **Detailed Steps**

##### **Step 2.1: Create Framework Package Structure**
```bash
# Create framework package directory
mkdir -p framework/{performance,security,reporting,maintenance}
mkdir -p framework/tests/{performance,security,reporting,maintenance}

# Create framework __init__.py files
touch framework/__init__.py
touch framework/performance/__init__.py
touch framework/security/__init__.py
touch framework/reporting/__init__.py
touch framework/maintenance/__init__.py
```

##### **Step 2.2: Move Framework Modules**
```bash
# Move performance module
mv strategy_sandbox/performance/ framework/performance/
mv tests/unit/test_performance_*.py framework/tests/performance/

# Move security module
mv strategy_sandbox/security/ framework/security/
mv tests/unit/test_security_*.py framework/tests/security/

# Move reporting module
mv strategy_sandbox/reporting/ framework/reporting/
mv tests/unit/test_*_manager.py framework/tests/reporting/
mv tests/unit/test_*_generator.py framework/tests/reporting/

# Move maintenance module
mv strategy_sandbox/maintenance/ framework/maintenance/
mv tests/unit/test_health_monitor.py framework/tests/maintenance/
mv tests/unit/test_maintenance_*.py framework/tests/maintenance/
```

##### **Step 2.3: Update Framework Package Exports**
```python
# framework/__init__.py
"""Hummingbot Development Framework.

Shared development and quality tools for Hummingbot features.
"""

from .performance import PerformanceCollector, TrendAnalyzer, PerformanceComparator
from .security import SecurityAnalyzer, DashboardGenerator, SBOMGenerator
from .reporting import ReportGenerator, ArtifactManager, TemplateEngine, GitHubReporter
from .maintenance import HealthMonitor, MaintenanceScheduler

__version__ = "1.0.0"
__framework_version__ = "1.0.0"

# Export main framework components
__all__ = [
    # Performance tools
    "PerformanceCollector", "TrendAnalyzer", "PerformanceComparator",
    # Security tools
    "SecurityAnalyzer", "DashboardGenerator", "SBOMGenerator",
    # Reporting tools
    "ReportGenerator", "ArtifactManager", "TemplateEngine", "GitHubReporter",
    # Maintenance tools
    "HealthMonitor", "MaintenanceScheduler"
]
```

##### **Step 2.4: Update Imports for Backward Compatibility**
```python
# strategy_sandbox/__init__.py - Add compatibility imports
"""Strategy Sandbox Feature.

Backward compatibility imports for framework components.
"""

# Feature exports (unchanged)
from .core import SandboxEnvironment, SandboxConfiguration
from .balance import BalanceManager
from .markets import ExchangeSimulator
from .events import SystemEventManager

# Backward compatibility for framework components
try:
    # Import from new framework location
    from framework.performance import PerformanceCollector, TrendAnalyzer
    from framework.security import SecurityAnalyzer, DashboardGenerator
    from framework.reporting import ReportGenerator, ArtifactManager
    from framework.maintenance import HealthMonitor, MaintenanceScheduler
except ImportError:
    # Fallback to old locations (during migration)
    from .performance import PerformanceCollector, TrendAnalyzer
    from .security import SecurityAnalyzer, DashboardGenerator
    from .reporting import ReportGenerator, ArtifactManager
    from .maintenance import HealthMonitor, MaintenanceScheduler

# Add compatibility warning
import warnings
warnings.warn(
    "Importing framework components from strategy_sandbox is deprecated. "
    "Use 'from framework import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)
```

##### **Step 2.5: Update PyProject.toml**
```toml
# Add framework as separate package
[project.optional-dependencies]
framework = [
    "pytest>=7.0.0",
    "pytest-benchmark>=4.0.0",
    "bandit>=1.7.0",
    "safety>=2.0.0",
    "pip-audit>=2.0.0",
    "jinja2>=3.0.0"
]

# Update CLI entry points
[project.scripts]
# Feature CLI (unchanged)
hb-strategy = "strategy_sandbox.cli:main"

# Framework CLI (new)
hb-performance = "framework.performance.cli:main"
hb-security = "framework.security.cli:main"
hb-reporting = "framework.reporting.cli:main"
hb-maintenance = "framework.maintenance.cli:main"

# Add pixi tasks for framework
[tool.pixi.tasks]
# Existing tasks (unchanged)
test = "pytest tests/"
lint = "ruff check strategy_sandbox tests"

# New framework tasks
test-framework = "pytest framework/tests/"
test-all = "pytest tests/ framework/tests/"
lint-framework = "ruff check framework/"
lint-all = "ruff check strategy_sandbox tests framework/"
```

##### **Step 2.6: Validation**
```bash
# Validate framework extraction
python .workspace/scripts/validate_current_state.py

# Run specific validation
pixi run test-all                    # All tests still pass
pixi run lint-all                   # No new lint violations
python -c "from strategy_sandbox.performance import PerformanceCollector"  # Backward compatibility
python -c "from framework.performance import PerformanceCollector"        # New imports work

# Check import warnings work
python -c "
import warnings
warnings.simplefilter('always')
from strategy_sandbox.performance import PerformanceCollector
# Should show deprecation warning
"
```

### **🎯 Phase 3: Feature Isolation** (Future)

#### **Objectives**
- Create clean feature package for strategy sandbox
- Remove framework components from feature dependencies
- Establish feature-specific configuration

#### **Key Steps**
1. Create `features/strategy_sandbox/` package
2. Move pure feature modules (core, balance, markets, events)
3. Create feature-specific pyproject.toml
4. Update feature-specific tests
5. Validate feature independence

### **🚀 Phase 4: Workspace Integration** (Future)

#### **Objectives**
- Implement full workspace structure
- Integrate multiple features (strategy_sandbox + candles_feed)
- Deploy multi-feature CI/CD pipeline
- Create quality dashboard

#### **Key Steps**
1. Create workspace root structure
2. Integrate sister project (candles_feed)
3. Implement multi-feature CI/CD
4. Create cross-feature integration tests
5. Deploy unified quality dashboard

## 🔍 **Validation Checklist**

### **Phase 1 Complete**
- [ ] All classification files created
- [ ] Validation scripts working
- [ ] Workspace templates prepared
- [ ] Migration guide documented
- [ ] Current quality baseline established

### **Phase 2 Complete**
- [ ] Framework package created and working
- [ ] All framework modules moved successfully
- [ ] Backward compatibility maintained
- [ ] All tests still passing
- [ ] No new lint violations

### **Phase 3 Complete**
- [ ] Feature package isolated
- [ ] Feature-specific configuration working
- [ ] Feature tests passing independently
- [ ] Framework dependencies clear

### **Phase 4 Complete**
- [ ] Multi-feature workspace functional
- [ ] Cross-feature integration tests passing
- [ ] CI/CD pipeline handling multiple features
- [ ] Quality dashboard operational

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Import Errors During Migration**
```python
# Problem: ModuleNotFoundError after moving modules
# Solution: Check PYTHONPATH and ensure __init__.py files exist

# Debug imports
import sys
print(sys.path)  # Check if framework is in path

# Verify package structure
import os
print(os.listdir("framework/"))  # Should show performance, security, etc.
```

#### **Test Failures After Module Moves**
```bash
# Problem: Tests can't find modules
# Solution: Update test imports and conftest.py

# Check test discovery
pytest --collect-only tests/

# Update conftest.py to include framework path
# conftest.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "framework"))
```

#### **Circular Import Dependencies**
```python
# Problem: Framework imports feature, feature imports framework
# Solution: Use dependency injection or protocols

# Instead of direct imports, use protocols
from abc import ABC, abstractmethod

class PerformanceProtocol(ABC):
    @abstractmethod
    def collect_metrics(self) -> Dict[str, Any]: ...

# Features depend on protocols, not concrete implementations
```

## 📞 **Support**

### **Getting Help**
- Review `.workspace/component_classification.toml` for module mappings
- Run validation scripts before and after each phase
- Check backward compatibility by testing existing imports
- Refer to sister project (`candles_feed`) for clean feature structure examples

### **Rollback Procedure**
If migration fails, rollback using:
```bash
# Reset to last known good state
git stash  # Save current changes
git reset --hard HEAD  # Reset to last commit
git clean -fd  # Remove untracked files (be careful!)

# Validate rollback
python .workspace/scripts/validate_current_state.py
```

---

**Next**: Run Phase 1 validation, then proceed to Phase 2 framework extraction.
