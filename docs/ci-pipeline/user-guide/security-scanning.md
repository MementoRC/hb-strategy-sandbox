# Security Scanning Guide

This guide covers the security scanning capabilities of the HB Strategy Sandbox CI pipeline, including dependency analysis, SBOM generation, and vulnerability management.

## Overview

The security scanning system provides:
- **Dependency vulnerability scanning** with multiple tools
- **SBOM (Software Bill of Materials) generation** in industry-standard formats
- **Security dashboard** with risk scoring and recommendations
- **Compliance reporting** for various security frameworks

## Security Components

### Dependency Analysis

The system scans your project dependencies for known vulnerabilities using multiple sources:

#### Supported Package Managers
- **pip/PyPI**: Python package scanning
- **pixi**: Conda-forge package scanning  
- **conda**: Conda package analysis
- **requirements.txt**: Direct dependency file analysis

#### Vulnerability Databases
- **OSV (Open Source Vulnerabilities)**: Comprehensive vulnerability database
- **GitHub Advisory Database**: GitHub's security advisory data
- **PyPA Advisory Database**: Python-specific vulnerability data
- **NVD (National Vulnerability Database)**: NIST vulnerability database

### SBOM Generation

Software Bill of Materials (SBOM) provides a complete inventory of your software components:

#### Supported Formats
- **CycloneDX**: Industry-standard format with rich vulnerability data
- **SPDX**: Linux Foundation standard for compliance
- **Custom JSON**: Enhanced format with additional metadata

#### SBOM Components
- **Direct dependencies**: Packages explicitly declared
- **Transitive dependencies**: Dependencies of dependencies
- **Development dependencies**: Tools and test frameworks
- **License information**: License compatibility analysis
- **Vulnerability mapping**: Security issues linked to components

## Configuration

### Security Scanning Setup

Configure security scanning in your project:

```yaml
# .github/workflows/security.yml
name: Security Scan

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Environment
        uses: prefix-dev/setup-pixi@v0.5.1
        
      - name: Run Security Scan
        run: |
          pixi run security-comprehensive
          
      - name: Generate SBOM
        run: |
          python -m strategy_sandbox.security.sbom_generator \
            --format cyclonedx \
            --output artifacts/sbom.json \
            --include-vulnerabilities
            
      - name: Generate Security Dashboard
        run: |
          python -m strategy_sandbox.security.dashboard_generator \
            --output artifacts/security_dashboard.json
```

### Vulnerability Thresholds

Configure vulnerability handling policies:

```yaml
# strategy_sandbox/security/vulnerability_policy.yaml
vulnerability_policy:
  # Blocking thresholds (fail CI)
  blocking:
    critical: 0    # Block any critical vulnerabilities
    high: 2        # Block if more than 2 high severity
    medium: 10     # Block if more than 10 medium severity
    
  # Warning thresholds (alert but don't fail)
  warning:
    high: 1        # Warn on any high severity
    medium: 5      # Warn if more than 5 medium severity
    low: 20        # Warn if more than 20 low severity

  # Grace period for new vulnerabilities
  grace_period:
    critical: 0    # Fix immediately
    high: 7        # 7 days to fix
    medium: 30     # 30 days to fix
    low: 90        # 90 days to fix

  # Severity scoring
  severity_weights:
    critical: 10.0
    high: 3.0
    medium: 1.0
    low: 0.1

# Allowed vulnerabilities (with justification)
exceptions:
  - id: "CVE-2023-12345"
    package: "example-package"
    reason: "False positive - not exploitable in our usage"
    expires: "2024-06-01"
    approved_by: "security-team"
```

### SBOM Configuration

Customize SBOM generation:

```yaml
# strategy_sandbox/security/sbom_config.yaml
sbom:
  metadata:
    supplier: "Your Organization"
    manufacturer: "Your Organization"
    authors: ["Development Team <dev@yourorg.com>"]
    
  # Component filtering
  include:
    dev_dependencies: false
    test_dependencies: false
    transitive_depth: 3  # Maximum dependency depth
    
  # Vulnerability inclusion
  vulnerabilities:
    include: true
    severity_threshold: "low"  # Include all severities
    include_fixed: false       # Exclude already fixed
    
  # License analysis
  licenses:
    analyze: true
    allowed:
      - "MIT"
      - "Apache-2.0"
      - "BSD-3-Clause"
      - "BSD-2-Clause"
    prohibited:
      - "GPL-3.0"
      - "AGPL-3.0"
    review_required:
      - "LGPL-2.1"
      - "MPL-2.0"

  # Output formats
  formats:
    cyclonedx:
      version: "1.5"
      include_vulnerabilities: true
    spdx:
      version: "2.3"
      document_namespace: "https://yourorg.com/spdx"
```

## Running Security Scans

### Local Execution

Run security scans locally during development:

```bash
# Complete security scan
pixi run security-comprehensive

# Individual scan components
pixi run security-static      # Static analysis with bandit
pixi run security-deps        # Dependency vulnerability scan
pixi run security-audit       # Pip-audit for PyPI packages
pixi run security-secrets     # Secret detection

# Generate SBOM
python -m strategy_sandbox.security.sbom_generator \
  --project-path . \
  --format cyclonedx \
  --output sbom_cyclonedx.json

# Generate security dashboard
python -m strategy_sandbox.security.dashboard_generator \
  --input-files reports/security-*.json \
  --output security_dashboard.json
```

### CI Integration

The pipeline automatically runs security scans:

```yaml
# Pixi task configuration
[tool.pixi.tasks]
security-comprehensive = { depends-on = [
  "security-static", 
  "security-audit", 
  "security-secrets", 
  "security-supply-chain"
] }

security-ci = "mkdir -p reports && pixi run security-comprehensive"
```

## Understanding Security Reports

### Security Dashboard

The security dashboard provides an overview of your project's security posture:

```json
{
  "metadata": {
    "timestamp": "2024-01-15T10:30:00Z",
    "project_name": "hb-strategy-sandbox",
    "scan_version": "1.2.0"
  },
  "summary": {
    "security_score": 85,
    "total_dependencies": 45,
    "vulnerable_dependencies": 3,
    "total_vulnerabilities": 8,
    "vulnerabilities_by_severity": {
      "critical": 0,
      "high": 1,
      "medium": 2,
      "low": 5
    }
  },
  "dependency_health": {
    "outdated_count": 5,
    "license_issues": 0,
    "unmaintained_count": 1,
    "health_score": 78
  },
  "recommendations": [
    {
      "priority": "high",
      "category": "vulnerability",
      "description": "Update requests to version 2.31.0 or later",
      "affected_packages": ["requests==2.28.0"]
    }
  ]
}
```

### Vulnerability Reports

Detailed vulnerability information:

```json
{
  "vulnerabilities": [
    {
      "id": "CVE-2023-32681",
      "package": "requests",
      "version": "2.28.0",
      "severity": "medium",
      "score": 6.1,
      "vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N",
      "description": "Proxy authorization header leak in urllib3",
      "published": "2023-05-26T09:15:00Z",
      "fixed_in": ["2.31.0"],
      "references": [
        "https://github.com/psf/requests/security/advisories/GHSA-j8r2-6x86-q33q"
      ],
      "affected_functions": [
        "requests.adapters.HTTPAdapter.send"
      ]
    }
  ]
}
```

### SBOM Analysis

Software Bill of Materials with component details:

```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.5",
  "metadata": {
    "timestamp": "2024-01-15T10:30:00Z",
    "component": {
      "name": "hb-strategy-sandbox",
      "version": "1.0.0",
      "type": "application"
    }
  },
  "components": [
    {
      "name": "requests",
      "version": "2.28.0",
      "type": "library",
      "supplier": "Python Software Foundation",
      "licenses": [
        {
          "license": {
            "id": "Apache-2.0"
          }
        }
      ],
      "vulnerabilities": [
        {
          "id": "CVE-2023-32681",
          "source": {
            "name": "OSV",
            "url": "https://osv.dev/vulnerability/GHSA-j8r2-6x86-q33q"
          },
          "ratings": [
            {
              "score": 6.1,
              "severity": "medium",
              "method": "CVSSv3",
              "vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N"
            }
          ]
        }
      ]
    }
  ]
}
```

## Security Policy Management

### Vulnerability Triage

Process for handling security vulnerabilities:

#### 1. Detection
- Automated scanning identifies new vulnerabilities
- CI pipeline fails if blocking thresholds are exceeded
- Security dashboard updated with new findings

#### 2. Assessment
- Review vulnerability details and impact
- Determine if vulnerability affects your usage
- Check for available fixes or workarounds

#### 3. Response
```bash
# For critical vulnerabilities - immediate action
# Update affected package
pixi add "package>=fixed_version"

# For false positives - add exception
# Edit vulnerability_policy.yaml to add exception

# For no available fix - implement workaround
# Document mitigation in security documentation
```

#### 4. Verification
```bash
# Re-run security scan to verify fix
pixi run security-comprehensive

# Update baseline if necessary
python -m strategy_sandbox.security.collector \
  --update-baseline \
  --reason "Fixed CVE-2023-32681 in requests"
```

### License Compliance

Monitor license compatibility:

#### License Categories
- **Permitted**: Licenses approved for use
- **Prohibited**: Licenses that cannot be used
- **Review Required**: Licenses requiring legal review

#### License Analysis
```json
{
  "license_analysis": {
    "total_licenses": 15,
    "permitted": 12,
    "prohibited": 1,
    "review_required": 2,
    "compliance_score": 80,
    "issues": [
      {
        "package": "problematic-package",
        "license": "GPL-3.0",
        "status": "prohibited",
        "recommendation": "Find alternative package"
      }
    ]
  }
}
```

## Advanced Security Features

### Supply Chain Security

Verify the integrity of your dependencies:

```bash
# Check package signatures
python -m strategy_sandbox.security.supply_chain \
  --verify-signatures \
  --check-maintainers \
  --analyze-patterns

# Generate supply chain report
python -m strategy_sandbox.security.supply_chain \
  --report-format json \
  --output supply_chain_report.json
```

### Secrets Detection

Prevent accidental secret commits:

```yaml
# .secrets.baseline configuration
{
  "version": "1.4.0",
  "plugins_used": [
    {
      "name": "ArtifactoryDetector"
    },
    {
      "name": "AWSKeyDetector"
    },
    {
      "name": "Base64HighEntropyString",
      "limit": 4.5
    },
    {
      "name": "BasicAuthDetector"
    },
    {
      "name": "GitHubTokenDetector"
    },
    {
      "name": "PrivateKeyDetector"
    }
  ],
  "exclude": {
    "files": "^tests/fixtures/.*",
    "lines": null
  }
}
```

### Container Security

If using containers, scan container images:

```bash
# Build and scan container
pixi run container-build
pixi run container-scan

# Generate container security report
trivy image hb-strategy-sandbox:latest \
  --format json \
  --output reports/container_security.json
```

## Best Practices

### Regular Security Maintenance

#### Daily
- Monitor security dashboard for new vulnerabilities
- Review CI security scan results
- Address critical and high-severity issues

#### Weekly
- Update dependencies to latest secure versions
- Review and triage medium-severity vulnerabilities
- Analyze security trends and patterns

#### Monthly
- Update security baseline and policies
- Review license compliance status
- Conduct security policy review

### Integration with Development Workflow

#### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
```

#### IDE Integration
- Configure IDE security plugins
- Set up real-time vulnerability highlighting
- Enable security-aware code completion

### Security Training

#### For Developers
- Understanding common vulnerabilities
- Secure coding practices
- Dependency management best practices
- License compliance awareness

#### For Security Teams
- SBOM analysis techniques
- Vulnerability prioritization
- Security policy development
- Incident response procedures

## Troubleshooting

### Common Issues

#### False Positives
```
Problem: Vulnerability reported but not applicable
Solution: Add exception to vulnerability_policy.yaml
```

#### Scan Failures
```
Problem: Security scan fails to complete
Solutions:
- Check network connectivity
- Verify package manager configuration
- Review scan tool versions
- Check for corrupted cache files
```

#### License Conflicts
```
Problem: Conflicting license requirements
Solutions:
- Find alternative packages
- Seek legal guidance
- Implement license compatibility matrix
```

### Debugging Security Scans

#### Verbose Logging
```bash
# Run with debug output
python -m strategy_sandbox.security.analyzer \
  --log-level DEBUG \
  --verbose
```

#### Manual Verification
```bash
# Verify specific vulnerability
pip-audit --desc --vuln-id CVE-2023-32681

# Check package details
pixi info package-name
```

For more troubleshooting guidance, see the [Troubleshooting Guide](../troubleshooting.md).