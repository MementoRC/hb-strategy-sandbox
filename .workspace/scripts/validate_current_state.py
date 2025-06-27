#!/usr/bin/env python3
"""
🔍 Validate Current Project State for Workspace Migration

This script validates the current project state and creates a baseline
for workspace migration. It checks:
- Module structure and dependencies
- Test coverage and quality metrics  
- Import patterns and API usage
- Configuration consistency

Run this before starting Phase 2 migration.
"""

import sys
import importlib
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import tomllib


@dataclass
class ValidationResult:
    """Results of project state validation."""
    component: str
    status: str  # "pass", "warn", "fail"
    message: str
    details: Optional[Dict[str, Any]] = None


class ProjectStateValidator:
    """Validates current project state for workspace migration."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.results: List[ValidationResult] = []
        
        # Load component classification
        classification_file = project_root / ".workspace" / "component_classification.toml"
        if classification_file.exists():
            with open(classification_file, "rb") as f:
                self.classification = tomllib.load(f)
        else:
            raise FileNotFoundError("Component classification file not found")
    
    def validate_all(self) -> Dict[str, Any]:
        """Run all validation checks."""
        print("🔍 Starting project state validation...")
        
        # Core validation checks
        self._validate_module_structure()
        self._validate_import_patterns()
        self._validate_test_coverage()
        self._validate_quality_metrics()
        self._validate_configuration()
        
        # Generate summary
        summary = self._generate_summary()
        self._save_results(summary)
        
        return summary
    
    def _validate_module_structure(self):
        """Validate that all classified modules exist and are importable."""
        print("📁 Validating module structure...")
        
        # Check feature components
        feature_modules = self.classification["classification"]["feature_components"]["modules"]
        for module_name, config in feature_modules.items():
            try:
                module = importlib.import_module(module_name)
                self.results.append(ValidationResult(
                    component=module_name,
                    status="pass",
                    message="Module exists and importable",
                    details={"target": config["target"], "priority": config["priority"]}
                ))
            except ImportError as e:
                self.results.append(ValidationResult(
                    component=module_name,
                    status="fail", 
                    message=f"Module import failed: {e}",
                    details={"target": config["target"]}
                ))
        
        # Check framework components
        framework_modules = self.classification["classification"]["framework_components"]["modules"]
        for module_name, config in framework_modules.items():
            try:
                module = importlib.import_module(module_name)
                self.results.append(ValidationResult(
                    component=module_name,
                    status="pass",
                    message="Framework module exists and importable",
                    details={"target": config["target"], "dependencies": config.get("dependencies", [])}
                ))
            except ImportError as e:
                self.results.append(ValidationResult(
                    component=module_name,
                    status="fail",
                    message=f"Framework module import failed: {e}",
                    details={"target": config["target"]}
                ))
    
    def _validate_import_patterns(self):
        """Validate current import patterns for backward compatibility."""
        print("🔗 Validating import patterns...")
        
        required_imports = self.classification["validation"]["backward_compatibility"]["required_imports"]
        
        for import_stmt in required_imports:
            try:
                # Execute the import statement
                exec(import_stmt)
                self.results.append(ValidationResult(
                    component="import_compatibility",
                    status="pass",
                    message=f"Import works: {import_stmt}",
                    details={"import": import_stmt}
                ))
            except Exception as e:
                self.results.append(ValidationResult(
                    component="import_compatibility", 
                    status="fail",
                    message=f"Import failed: {import_stmt} - {e}",
                    details={"import": import_stmt, "error": str(e)}
                ))
    
    def _validate_test_coverage(self):
        """Validate test coverage and count."""
        print("🧪 Validating test coverage...")
        
        try:
            # Run pytest to get test count
            result = subprocess.run(
                ["python", "-m", "pytest", "--collect-only", "-q"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                # Count tests from output - count lines with "::"
                test_count = result.stdout.count("::")
                
                min_required = self.classification["validation"]["quality_gates"]["min_test_count"]
                
                if test_count >= min_required:
                    self.results.append(ValidationResult(
                        component="test_coverage",
                        status="pass",
                        message=f"Test count {test_count} meets minimum {min_required}",
                        details={"test_count": test_count, "minimum": min_required}
                    ))
                else:
                    self.results.append(ValidationResult(
                        component="test_coverage",
                        status="fail",
                        message=f"Test count {test_count} below minimum {min_required}",
                        details={"test_count": test_count, "minimum": min_required}
                    ))
            else:
                self.results.append(ValidationResult(
                    component="test_coverage",
                    status="fail",
                    message="Failed to collect tests",
                    details={"error": result.stderr}
                ))
                
        except Exception as e:
            self.results.append(ValidationResult(
                component="test_coverage",
                status="fail",
                message=f"Test validation failed: {e}",
                details={"error": str(e)}
            ))
    
    def _validate_quality_metrics(self):
        """Validate code quality metrics."""
        print("✨ Validating quality metrics...")
        
        try:
            # Run critical linting
            result = subprocess.run(
                ["python", "-m", "ruff", "check", "--select=F,E9", "strategy_sandbox", "tests"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            max_violations = self.classification["validation"]["quality_gates"]["max_critical_violations"]
            
            if result.returncode == 0:
                self.results.append(ValidationResult(
                    component="quality_metrics",
                    status="pass", 
                    message="No critical lint violations found",
                    details={"violations": 0, "max_allowed": max_violations}
                ))
            else:
                # Count violations from output
                violation_count = result.stdout.count("F401") + result.stdout.count("E9")
                
                if violation_count <= max_violations:
                    self.results.append(ValidationResult(
                        component="quality_metrics",
                        status="warn",
                        message=f"Found {violation_count} violations (within limit)",
                        details={"violations": violation_count, "max_allowed": max_violations}
                    ))
                else:
                    self.results.append(ValidationResult(
                        component="quality_metrics",
                        status="fail",
                        message=f"Found {violation_count} violations (exceeds limit {max_violations})",
                        details={"violations": violation_count, "max_allowed": max_violations}
                    ))
                    
        except Exception as e:
            self.results.append(ValidationResult(
                component="quality_metrics",
                status="fail",
                message=f"Quality validation failed: {e}",
                details={"error": str(e)}
            ))
    
    def _validate_configuration(self):
        """Validate configuration files and dependencies."""
        print("⚙️ Validating configuration...")
        
        # Check pyproject.toml exists and is valid
        pyproject_file = self.project_root / "pyproject.toml"
        if pyproject_file.exists():
            try:
                with open(pyproject_file, "rb") as f:
                    config = tomllib.load(f)
                
                self.results.append(ValidationResult(
                    component="configuration",
                    status="pass",
                    message="pyproject.toml is valid",
                    details={"project_name": config.get("project", {}).get("name")}
                ))
            except Exception as e:
                self.results.append(ValidationResult(
                    component="configuration",
                    status="fail",
                    message=f"pyproject.toml validation failed: {e}",
                    details={"error": str(e)}
                ))
        else:
            self.results.append(ValidationResult(
                component="configuration",
                status="fail",
                message="pyproject.toml not found",
                details={}
            ))
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate validation summary."""
        summary = {
            "validation_date": "2025-06-27",
            "project_root": str(self.project_root),
            "total_checks": len(self.results),
            "results": {
                "pass": len([r for r in self.results if r.status == "pass"]),
                "warn": len([r for r in self.results if r.status == "warn"]), 
                "fail": len([r for r in self.results if r.status == "fail"])
            },
            "details": [asdict(result) for result in self.results],
            "workspace_ready": len([r for r in self.results if r.status == "fail"]) == 0
        }
        
        return summary
    
    def _save_results(self, summary: Dict[str, Any]):
        """Save validation results to file."""
        results_file = self.project_root / ".workspace" / "validation_results.json"
        results_file.parent.mkdir(exist_ok=True)
        
        with open(results_file, "w") as f:
            json.dump(summary, f, indent=2)
        
        print(f"📄 Validation results saved to {results_file}")
    
    def print_summary(self, summary: Dict[str, Any]):
        """Print human-readable summary."""
        print("\n" + "="*60)
        print("🔍 PROJECT STATE VALIDATION SUMMARY")
        print("="*60)
        
        print(f"📊 Total Checks: {summary['total_checks']}")
        print(f"✅ Passed: {summary['results']['pass']}")
        print(f"⚠️  Warnings: {summary['results']['warn']}")
        print(f"❌ Failed: {summary['results']['fail']}")
        
        if summary['workspace_ready']:
            print("\n🎯 WORKSPACE READY: Project can proceed to Phase 2 migration")
        else:
            print("\n⚠️  ISSUES FOUND: Fix failures before proceeding to Phase 2")
            
            # Show failures
            failures = [r for r in self.results if r.status == "fail"]
            if failures:
                print("\n❌ Failures to fix:")
                for failure in failures:
                    print(f"   • {failure.component}: {failure.message}")
        
        print("="*60)


def main():
    """Main validation entry point."""
    project_root = Path(__file__).parent.parent.parent
    
    validator = ProjectStateValidator(project_root)
    summary = validator.validate_all()
    validator.print_summary(summary)
    
    # Exit with appropriate code
    if not summary['workspace_ready']:
        sys.exit(1)
    
    print("✅ Validation complete - project ready for workspace migration!")


if __name__ == "__main__":
    main()