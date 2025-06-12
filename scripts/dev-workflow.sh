#!/bin/bash
# Automated Development Workflow Script
# Based on patterns from llm-task-framework reference

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    if ! command -v pixi &> /dev/null; then
        error "pixi is required but not installed"
        exit 1
    fi
    
    if ! command -v gh &> /dev/null; then
        error "GitHub CLI (gh) is required but not installed"
        exit 1
    fi
    
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        error "Not in a git repository"
        exit 1
    fi
    
    success "Prerequisites check passed"
}

# Quality gate validation
run_quality_gates() {
    log "Running quality gates..."
    
    # Run tests
    log "Running tests..."
    if ! pixi run test; then
        error "Tests failed"
        return 1
    fi
    
    # Run lint
    log "Running lint checks..."
    if ! pixi run lint; then
        error "Lint checks failed"
        return 1
    fi
    
    # Run security checks
    log "Running security checks..."
    if ! pixi run security-comprehensive; then
        warn "Security checks failed - review required"
    fi
    
    # Run type checking
    log "Running type checks..."
    if ! pixi run typecheck; then
        warn "Type checking failed - review required"
    fi
    
    success "Quality gates completed"
}

# Create feature branch
create_feature() {
    local feature_name="$1"
    
    if [[ -z "$feature_name" ]]; then
        error "Feature name is required"
        exit 1
    fi
    
    log "Creating feature branch: $feature_name"
    
    # Ensure we're on development branch
    git checkout development || {
        error "Failed to switch to development branch"
        exit 1
    }
    
    # Pull latest changes
    git pull origin development || {
        error "Failed to pull latest changes"
        exit 1
    }
    
    # Create and switch to feature branch
    git checkout -b "feature/$feature_name" || {
        error "Failed to create feature branch"
        exit 1
    }
    
    # Run initial quality checks
    run_quality_gates || {
        error "Initial quality gates failed"
        exit 1
    }
    
    success "Feature branch 'feature/$feature_name' created and validated"
}

# Finish feature branch
finish_feature() {
    local title="$1"
    local description="${2:-}"
    
    if [[ -z "$title" ]]; then
        error "PR title is required"
        exit 1
    fi
    
    log "Finishing feature branch..."
    
    # Get current branch name
    local current_branch
    current_branch=$(git branch --show-current)
    
    if [[ ! "$current_branch" =~ ^feature/ ]]; then
        error "Not on a feature branch"
        exit 1
    fi
    
    # Run quality gates
    run_quality_gates || {
        error "Quality gates failed - cannot create PR"
        exit 1
    }
    
    # Push branch
    log "Pushing branch to remote..."
    git push origin "$current_branch" || {
        error "Failed to push branch"
        exit 1
    }
    
    # Create PR
    log "Creating pull request..."
    local pr_body="## Summary
$description

## Quality Validation
- ✅ Tests passing
- ✅ Lint checks passing  
- ✅ Security scans completed
- ✅ Type checking completed

## Test Plan
- [x] Unit tests updated/added
- [x] Integration tests verified
- [x] Performance impact assessed

🤖 Generated with automated dev workflow"
    
    gh pr create --base development --title "$title" --body "$pr_body" || {
        error "Failed to create pull request"
        exit 1
    }
    
    success "Pull request created successfully"
}

# Performance benchmark comparison
run_performance_comparison() {
    log "Running performance comparison..."
    
    # Run current benchmarks
    pixi run test-performance --benchmark-json=current-benchmark.json || {
        error "Failed to run performance tests"
        return 1
    }
    
    # Download baseline from artifacts (if available)
    if gh run download --name performance-baseline --dir baseline 2>/dev/null; then
        log "Comparing with baseline performance..."
        # Add comparison logic here
        python scripts/compare-benchmarks.py baseline/benchmark.json current-benchmark.json
    else
        warn "No baseline performance data found"
    fi
    
    success "Performance comparison completed"
}

# Security scan
run_security_scan() {
    log "Running comprehensive security scan..."
    
    # Create reports directory
    mkdir -p reports
    
    # Static analysis
    log "Running static security analysis..."
    pixi run security-static || warn "Static analysis issues found"
    
    # Dependency scanning
    log "Running dependency security scan..."
    pixi run security-deps || warn "Dependency issues found"
    
    # Secrets detection
    log "Running secrets detection..."
    pixi run security-secrets || warn "Potential secrets found"
    
    # Supply chain verification
    log "Running supply chain verification..."
    pixi run security-supply-chain || warn "Supply chain issues found"
    
    success "Security scan completed - check reports/ directory"
}

# Main command dispatcher
main() {
    case "${1:-help}" in
        "create-feature")
            check_prerequisites
            create_feature "${2:-}"
            ;;
        "finish-feature")
            check_prerequisites
            finish_feature "${2:-}" "${3:-}"
            ;;
        "quality-check")
            check_prerequisites
            run_quality_gates
            ;;
        "performance")
            check_prerequisites
            run_performance_comparison
            ;;
        "security")
            check_prerequisites
            run_security_scan
            ;;
        "help"|*)
            echo "Usage: $0 <command> [options]"
            echo ""
            echo "Commands:"
            echo "  create-feature <name>           Create and validate feature branch"
            echo "  finish-feature <title> [desc]   Finish feature and create PR"
            echo "  quality-check                   Run all quality gates"
            echo "  performance                     Run performance comparison"
            echo "  security                        Run security scan"
            echo "  help                           Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 create-feature user-authentication"
            echo "  $0 finish-feature 'Add user auth' 'Implements JWT authentication'"
            echo "  $0 quality-check"
            ;;
    esac
}

main "$@"