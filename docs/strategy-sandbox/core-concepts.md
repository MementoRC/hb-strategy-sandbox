# Core Concepts of HB Strategy Sandbox

Understanding the core components and their interactions is crucial for effectively developing and testing strategies within the HB Strategy Sandbox. This section details the main building blocks of the simulation environment.

## 1. SandboxEnvironment

The `SandboxEnvironment` is the central orchestrator of the entire simulation. It initializes and manages all other components, advances the simulation time, and provides the interface for strategies to interact with the simulated market.

*   **Purpose:** Coordinates the simulation flow, manages component lifecycles, and exposes a unified API to strategies.
*   **Key Responsibilities:**
    *   Initialization of market, balance, and event systems.
    *   Advancing simulation time step-by-step.
    *   Notifying strategies of market events and ticks.
    *   Collecting and reporting overall simulation performance metrics.

## 2. ExchangeSimulator

The `ExchangeSimulator` is a sophisticated component that mimics the behavior of a real cryptocurrency exchange. It manages order books, processes order placements and cancellations, and simulates trade fills with realistic slippage and market dynamics.

*   **Purpose:** Provides a realistic, isolated trading environment for strategies.
*   **Key Features:**
    *   **Order Book Management:** Maintains bid and ask order books for configured trading pairs.
    *   **Order Execution:** Processes market and limit orders, simulating fills based on order book depth.
    *   **Slippage Simulation:** Applies configurable slippage models (linear, logarithmic, square root) to trade executions.
    *   **Market Dynamics:** Simulates price volatility, trends, and market regimes to create dynamic market conditions.
    *   **Latency Simulation:** Introduces realistic delays in order processing.

## 3. SandboxBalanceManager

The `SandboxBalanceManager` handles all asset balances within the simulation. It tracks total, available, and locked balances for each asset, ensuring that strategies operate within their simulated capital constraints.

*   **Purpose:** Manages and validates asset holdings for accurate financial simulation.
*   **Key Responsibilities:**
    *   Tracking asset balances (e.g., USDT, BTC).
    *   Locking and unlocking funds for active orders.
    *   Updating balances based on trade fills and other financial operations.

## 4. SandboxEventSystem

The `SandboxEventSystem` is the communication backbone of the sandbox. It implements a publish-subscribe pattern, allowing different components and strategies to emit and listen for various market and system events.

*   **Purpose:** Facilitates asynchronous communication and reactive programming within the simulation.
*   **Key Features:**
    *   **Event Emission:** Components can emit predefined `MarketEvent` types (e.g., `ORDER_FILLED`, `BALANCE_UPDATED`).
    *   **Event Subscription:** Strategies and other components can subscribe to specific event types and register callback functions.
    *   **Asynchronous Processing:** Events are processed asynchronously to avoid blocking the simulation flow.

## 5. Key Protocols

The sandbox components adhere to a set of Python `Protocol` definitions, ensuring clear interfaces and promoting modularity and testability. Strategies interact with the sandbox primarily through these protocols.

*   **:py:class:`~strategy_sandbox.core.protocols.MarketProtocol`:** Defines the interface for market data access (e.g., `get_price`, `get_order_book`, `get_trading_pairs`).
*   **:py:class:`~strategy_sandbox.core.protocols.BalanceProtocol`:** Defines the interface for balance management (e.g., `get_balance`, `lock_balance`, `update_balance`).
*   **:py:class:`~strategy_sandbox.core.protocols.OrderProtocol`:** Defines the interface for order management (e.g., `place_order`, `cancel_order`, `get_open_orders`).
*   **:py:class:`~strategy_sandbox.core.protocols.EventProtocol`:** Defines the interface for event subscription and emission (e.g., `emit_event`, `subscribe`).
*   **:py:class:`~strategy_sandbox.core.protocols.StrategyProtocol`:** Defines the interface that all trading strategies must implement to be compatible with the sandbox (e.g., `on_tick`, `on_order_filled`).
*   **:py:class:`~strategy_sandbox.core.protocols.SlippageConfig`:** Configuration dataclass for defining slippage simulation parameters.
*   **:py:class:`~strategy_sandbox.core.protocols.MarketDynamicsConfig`:** Configuration dataclass for defining market behavior parameters like volatility and trend.

By understanding these core concepts, you can effectively design, implement, and test your trading strategies within the HB Strategy Sandbox.
