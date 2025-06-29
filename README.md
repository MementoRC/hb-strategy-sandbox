# Hummingbot Strategy Sandbox

A comprehensive testing and simulation framework for Hummingbot trading strategies.

> **🚀 Framework Extraction Complete**: Phase 2 migration completed! Framework components now available in `framework/` package. See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) and [CHANGELOG.md](CHANGELOG.md) for details.

## Overview

The Hummingbot Strategy Sandbox provides a controlled environment for testing and developing trading strategies without connecting to real exchanges. It simulates market conditions, order execution, and balance management to enable safe strategy development and backtesting.

## Features

- **Complete Market Simulation**: Full order book simulation with realistic market dynamics
- **Balance Management**: Accurate balance tracking for spot and derivatives trading
- **Event System**: Comprehensive event handling for market and system events
- **Protocol-Based Design**: Clean interfaces that mirror real Hummingbot components
- **Performance Metrics**: Detailed performance analysis and reporting
- **Easy Integration**: Simple API for strategy development and testing

## Quick Start

### Installation

```bash
pip install hb-strategy-sandbox
```

### Basic Usage

```python
import asyncio
from decimal import Decimal
from datetime import timedelta
from strategy_sandbox import SandboxEnvironment, SandboxConfiguration

# Create configuration
config = SandboxConfiguration(
    initial_balances={"USDT": Decimal("10000")},
    trading_pairs=["BTC-USDT"],
)

# Create sandbox
sandbox = SandboxEnvironment(config=config)

# Add your strategy
sandbox.add_strategy(my_strategy)

# Run simulation
results = await sandbox.run(duration=timedelta(hours=24))
print(f"PnL: {results['total_pnl']}")
```

## Architecture

The sandbox is built on a clean protocol-based architecture:

- **Core Protocols**: Define interfaces for market, balance, order, and event handling
- **Sandbox Environment**: Central orchestrator for all components
- **Market Simulation**: Realistic exchange behavior simulation
- **Balance Management**: Accurate balance tracking and locking
- **Event System**: Complete event propagation system

### 🏗️ **Workspace Architecture**

This project is organized for multi-feature workspace development:

#### **🎯 Feature Components** (Strategy Sandbox)
Pure business logic for strategy development:
- `strategy_sandbox/core/` - Core strategy logic
- `strategy_sandbox/balance/` - Balance management
- `strategy_sandbox/markets/` - Market simulation
- `strategy_sandbox/events/` - Event system

#### **🛠️ Framework Components** (Shared Tools)
Reusable development and quality tools now available in dedicated `framework/` package:
- `framework/performance/` - Performance monitoring and benchmarking
- `framework/security/` - Security scanning and vulnerability analysis
- `framework/reporting/` - Report generation and artifact management
- `framework/maintenance/` - System maintenance and health monitoring

> **✅ Phase 2 Complete**: Framework components successfully extracted to `framework/` package with full backward compatibility maintained. See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for usage details.

## Examples

See the `examples/` directory for:

- Simple buy-low-sell-high strategy
- Market making strategy simulation
- Arbitrage strategy testing
- Integration with Hummingbot strategies

## Development

### Requirements

- Python 3.10+
- asyncio support
- Decimal precision arithmetic

### Development Setup

```bash
git clone https://github.com/MementoRC/hb-strategy-sandbox.git
cd hb-strategy-sandbox
pixi install
pixi run test
```

### Running Tests

```bash
pixi run test-unit          # Unit tests
pixi run test-integration   # Integration tests
pixi run test-performance   # Performance tests
```

## CI/CD Status

[![CI](https://github.com/MementoRC/hb-strategy-sandbox/workflows/CI/badge.svg)](https://github.com/MementoRC/hb-strategy-sandbox/actions/workflows/ci.yml)
[![Documentation](https://github.com/MementoRC/hb-strategy-sandbox/workflows/Documentation/badge.svg)](https://github.com/MementoRC/hb-strategy-sandbox/actions/workflows/docs.yml)
[![codecov](https://codecov.io/gh/MementoRC/hb-strategy-sandbox/branch/main/graph/badge.svg)](https://codecov.io/gh/MementoRC/hb-strategy-sandbox)

## Roadmap

- [x] **Phase 1**: Basic sandbox functionality with CI/CD
- [x] **Phase 2**: Framework extraction and modular architecture ✅ **COMPLETE**
- [ ] **Phase 3**: Advanced market dynamics and slippage simulation
- [ ] **Phase 4**: Hummingbot Strategy V2 integration
- [ ] **Phase 5**: Historical data replay and backtesting
- [ ] **Phase 6**: Real-time data integration

See [CHANGELOG.md](CHANGELOG.md) for detailed release notes.

## Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests.

## License

Apache 2.0 License - see LICENSE file for details.

## Links

- [Documentation](https://mementorc.github.io/hb-strategy-sandbox)
- [GitHub Repository](https://github.com/MementoRC/hb-strategy-sandbox)
- [Hummingbot Integration Guide](https://docs.hummingbot.org)
