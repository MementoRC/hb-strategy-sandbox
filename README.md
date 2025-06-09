# Hummingbot Strategy Sandbox

A comprehensive testing and simulation framework for Hummingbot trading strategies.

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
- [ ] **Phase 2**: Advanced market dynamics and slippage simulation
- [ ] **Phase 3**: Hummingbot Strategy V2 integration
- [ ] **Phase 4**: Historical data replay and backtesting
- [ ] **Phase 5**: Real-time data integration

## Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests.

## License

Apache 2.0 License - see LICENSE file for details.

## Links

- [Documentation](https://mementorc.github.io/hb-strategy-sandbox)
- [GitHub Repository](https://github.com/MementoRC/hb-strategy-sandbox)
- [Hummingbot Integration Guide](https://docs.hummingbot.org)