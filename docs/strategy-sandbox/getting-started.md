# Getting Started with HB Strategy Sandbox

This guide will walk you through setting up your development environment and running your first basic simulation with the HB Strategy Sandbox.

## Installation

To get started, you'll need to install the project dependencies. We recommend using `pixi` for environment management, but `pip` is also supported.

### Using Pixi (Recommended)

If you have `pixi` installed, navigate to the project root directory and run:

```bash
pixi install
```

This command will set up a virtual environment and install all necessary dependencies as defined in `pixi.lock`.

### Using Pip

Alternatively, you can install the dependencies using `pip`:

```bash
pip install -e .
```

This will install the project in editable mode, allowing you to make changes to the source code directly.

## Your First Simulation: A Simple Strategy

Let's create a very basic strategy that simply logs the current market price at each simulation tick. This will demonstrate the core components of the sandbox.

1.  **Create a Strategy File:**

    Create a new Python file, for example, `my_first_strategy.py`, in your project directory with the following content:

    ```python
    from decimal import Decimal
    import logging

    from strategy_sandbox.core.protocols import StrategyProtocol, SandboxProtocol, PriceType

    # Configure logging for your strategy
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    class MyFirstStrategy(StrategyProtocol):
        """A simple strategy that logs the mid-price at each tick."""

        def __init__(self):
            self.sandbox: SandboxProtocol | None = None

        def initialize(self, sandbox: SandboxProtocol) -> None:
            """Initializes the strategy with the sandbox environment."""
            self.sandbox = sandbox
            logger.info("MyFirstStrategy initialized.")

        async def on_tick(self, timestamp: float) -> None:
            """Called on each simulation tick."""
            if self.sandbox:
                # Get the current mid-price for BTC-USDT
                btc_usdt_price = self.sandbox.market.get_price("BTC-USDT", PriceType.MID)
                logger.info(f"Timestamp: {timestamp:.2f}, BTC-USDT Mid Price: {btc_usdt_price}")

        def on_order_filled(self, order) -> None:
            """Called when an order is filled."""
            logger.info(f"Order Filled: {order.order_id} - {order.amount} @ {order.price}")

        def on_balance_updated(self, asset: str, balance: Decimal) -> None:
            """Called when a balance is updated."""
            logger.info(f"Balance Updated: {asset} - {balance}")

        def cleanup(self) -> None:
            """Cleans up strategy resources."""
            logger.info("MyFirstStrategy cleaned up.")
    ```

2.  **Run the Simulation:**

    Now, create another Python file, e.g., `run_simulation.py`, to set up and run your simulation:

    ```python
    import asyncio
    from datetime import timedelta
    from decimal import Decimal

    from strategy_sandbox.core.environment import SandboxEnvironment, SandboxConfiguration
    from my_first_strategy import MyFirstStrategy

    async def main():
        # Configure the sandbox
        config = SandboxConfiguration(
            initial_balances={"USDT": Decimal("10000"), "BTC": Decimal("1")}, # Start with some BTC and USDT
            trading_pairs=["BTC-USDT"],
            tick_interval=60.0,  # Simulate every 60 seconds
        )

        # Initialize the sandbox environment
        env = SandboxEnvironment(config=config)
        await env.initialize()

        # Add your strategy to the sandbox
        strategy = MyFirstStrategy()
        env.add_strategy(strategy)

        # Run the simulation for 1 hour
        print("Starting simulation...")
        performance_metrics = await env.run(duration=timedelta(hours=1))
        print("Simulation finished.")

        # Print performance metrics
        print("\nPerformance Metrics:")
        for key, value in performance_metrics.items():
            print(f"  {key}: {value}")

    if __name__ == "__main__":
        asyncio.run(main())
    ```

3.  **Execute the Simulation:**

    Run `run_simulation.py` from your terminal:

    ```bash
    python run_simulation.py
    ```

    You should see log messages from your strategy indicating the simulated mid-price of BTC-USDT at each tick, along with final performance metrics.

## Interpreting Basic Results

After the simulation runs, `run_simulation.py` will print `performance_metrics`. These metrics provide a high-level overview of your strategy's performance during the simulation:

*   `duration_seconds`: The total duration of the simulation in seconds.
*   `initial_balances`: The starting balances of your assets.
*   `final_balances`: The ending balances of your assets after the simulation.
*   `total_pnl`: Your total profit and loss (PnL) across all assets (simplified in this basic example).
*   `order_statistics`: Basic statistics about orders placed and filled during the simulation.
*   `simulation_end_time`: The timestamp when the simulation concluded.

This is just the beginning! The Strategy Sandbox offers much more detailed analysis capabilities, which you'll explore in subsequent sections.
