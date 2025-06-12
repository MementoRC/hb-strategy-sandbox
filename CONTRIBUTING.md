# Contributing to hb-strategy-sandbox

Thank you for your interest in contributing to the Hummingbot Strategy Sandbox! This document provides guidelines and information for contributors.

## Development Workflow

We follow a GitFlow-inspired workflow with the following branches:

### Branch Structure

- **`main`**: Production-ready code. All releases are tagged from this branch.
- **`development`**: Integration branch for features. All feature branches merge here first.
- **`feature/*`**: Feature development branches (e.g., `feature/add-slippage-simulation`)
- **`bugfix/*`**: Bug fix branches (e.g., `bugfix/fix-balance-calculation`)
- **`hotfix/*`**: Critical fixes that need to go directly to main

### Recommended Workflow

1. **Create Feature Branch**
   ```bash
   git checkout development
   git pull origin development
   git checkout -b feature/your-feature-name
   ```

2. **Develop and Test**
   ```bash
   # Install development environment
   pixi install

   # Run tests during development
   pixi run test-unit
   pixi run lint
   pixi run typecheck

   # Run full test suite before pushing
   pixi run test
   ```

3. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description

   - Detailed description of changes
   - Any breaking changes or important notes

   🤖 Generated with [Claude Code](https://claude.ai/code)
   Co-Authored-By: Your Name <your.email@example.com>"
   ```

4. **Push and Create PR**
   ```bash
   git push -u origin feature/your-feature-name
   # Create PR targeting 'development' branch
   ```

5. **After PR Approval and Merge**
   ```bash
   git checkout development
   git pull origin development
   git branch -d feature/your-feature-name
   ```

## Branch Protection Rules

### For `main` branch:
- Require pull request reviews (1+ reviewers)
- Require status checks to pass:
  - `lint`
  - `test (ubuntu-latest, 3.11)`
  - `build`
- Require branches to be up to date before merging
- Restrict pushes to main (only via PR)
- Allow force pushes: No
- Allow deletions: No

### For `development` branch:
- Require pull request reviews (1+ reviewers)
- Require status checks to pass:
  - `lint`
  - `test (ubuntu-latest, 3.11)`
- Require branches to be up to date before merging
- Allow force pushes: No
- Allow deletions: No

## Development Setup

### Prerequisites

- Python 3.10+
- [Pixi](https://pixi.sh/) (recommended) or pip/conda

### Setup with Pixi (Recommended)

```bash
# Clone repository
git clone https://github.com/MementoRC/hb-strategy-sandbox.git
cd hb-strategy-sandbox

# Install dependencies
pixi install

# Install pre-commit hooks
pixi run -e dev pre-commit install

# Run tests to verify setup
pixi run test
```

### Setup with pip

```bash
# Clone repository
git clone https://github.com/MementoRC/hb-strategy-sandbox.git
cd hb-strategy-sandbox

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest
```

## Testing Guidelines

### Test Types

1. **Unit Tests** (`tests/unit/`): Test individual components in isolation
2. **Integration Tests** (`tests/integration/`): Test component interactions
3. **Performance Tests** (`tests/performance/`): Benchmark critical functionality

### Running Tests

```bash
# Run all tests
pixi run test

# Run specific test types
pixi run test-unit
pixi run test-integration
pixi run test-performance

# Run tests with coverage
pixi run test-unit --cov=strategy_sandbox --cov-report=html

# Run specific test file
pixi run test tests/unit/test_sandbox_environment.py

# Run tests matching pattern
pixi run test -k "test_balance"
```

### Writing Tests

- Use descriptive test names: `test_balance_update_with_insufficient_funds`
- Include docstrings explaining test purpose
- Use fixtures from `conftest.py` for common setup
- Add performance tests for critical paths
- Test both success and failure scenarios

Example test:
```python
@pytest.mark.asyncio
async def test_order_placement_with_insufficient_balance(sandbox):
    \"\"\"Test that orders fail when insufficient balance.\"\"\"
    # Setup: insufficient balance
    sandbox.balance.set_balance("USDT", Decimal("10"))

    # Action: try to place large order
    order = OrderCandidate(
        trading_pair="BTC-USDT",
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        amount=Decimal("1.0"),  # Would cost ~$50k
    )

    # Assert: order placement fails
    order_id = sandbox.order.place_order(order)
    assert order_id is None
```

## Code Quality Standards

### Linting and Formatting

We use Ruff for both linting and formatting:

```bash
# Check and fix linting issues
pixi run lint

# Format code
pixi run format

# Type checking
pixi run typecheck
```

### Code Style

- Follow PEP 8 style guidelines
- Use type hints for all public APIs
- Document classes and functions with docstrings
- Prefer explicit over implicit code
- Use descriptive variable names

### Commit Messages

Follow conventional commit format:

```
type(scope): description

Longer description if needed

- Bullet points for detailed changes
- Breaking changes should be noted

🤖 Generated with [Claude Code](https://claude.ai/code)
Co-Authored-By: Your Name <your.email@example.com>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `ci`

## Performance Considerations

- Use `Decimal` for financial calculations
- Prefer async/await for I/O operations
- Minimize object creation in hot paths
- Add benchmarks for performance-critical code
- Profile before optimizing

## Documentation

- Update docstrings for API changes
- Add examples for new features
- Update README for significant changes
- Consider adding tutorials for complex features

## Release Process

1. **Feature Complete**: All features merged to `development`
2. **Release Branch**: Create `release/v1.x.x` from `development`
3. **Testing**: Run full test suite, fix any issues
4. **Version Bump**: Update `__about__.py` version
5. **PR to Main**: Create PR from release branch to `main`
6. **Tag Release**: After merge, tag the release
7. **Back-merge**: Merge `main` back to `development`

## Getting Help

- **GitHub Issues**: Report bugs and request features
- **GitHub Discussions**: Ask questions and discuss ideas
- **Discord**: Join the Hummingbot community Discord

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code.

Thank you for contributing to hb-strategy-sandbox!
