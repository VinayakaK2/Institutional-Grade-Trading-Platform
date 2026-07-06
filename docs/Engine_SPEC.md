# ENGINE_SPEC.md

# Institutional Swing Trading Platform

**Version:** 1.0

---

# Overview

The Engine Specification defines the internal execution logic of every analytical and operational engine inside the Institutional Swing Trading Platform.

The platform is intentionally divided into independent engines rather than one large monolithic algorithm.

Each engine has a single responsibility.

Each engine receives standardized input, performs deterministic computation, produces standardized output, and publishes an event for the next engine.

This architecture provides:

- High Maintainability
- Easy Testing
- Independent Scalability
- Loose Coupling
- Easier Debugging
- Explainable Decisions
- Future Strategy Expansion

No engine is allowed to directly modify another engine's logic.

Every engine behaves like an independent micro-decision system.

---

# Complete Engine Pipeline

```
                Market Data
                     │
                     ▼
          Market Universe Engine
                     │
                     ▼
            Watchlist Engine
                     │
                     ▼
              Trend Engine
                     │
                     ▼
         Consolidation Engine
                     │
                     ▼
        Liquidity Grab Engine
                     │
                     ▼
       Trade Validation Engine
                     │
                     ▼
              Risk Engine
                     │
                     ▼
           Portfolio Engine
                     │
                     ▼
        Order Execution Engine
                     │
                     ▼
      Position Management Engine
                     │
                     ▼
              Exit Engine
                     │
                     ▼
            Learning Engine
                     │
                     ▼
           Analytics Engine
```

Every engine must complete successfully before the next engine begins.

If any engine rejects the trade, the pipeline terminates immediately.

---

# Common Engine Contract

Every engine follows the same lifecycle.

```
Receive Input

↓

Validate Input

↓

Load Required Data

↓

Calculate Metrics

↓

Apply Rules

↓

Generate Decision

↓

Generate Metadata

↓

Store Result

↓

Publish Event

↓

Finish
```

Every engine returns one of three states.

```
APPROVED

REJECTED

WAITING
```

No engine returns ambiguous results.

---

# Engine Communication

Engines never call each other directly.

Communication occurs only through standardized events.

Example

```
Trend Engine

↓

TrendGenerated

↓

Consolidation Engine
```

Benefits

- Loose Coupling
- Retry Support
- Event Replay
- Better Logging
- Easier Scaling

---

# 1. Market Universe Engine

## Purpose

Determine which stocks are eligible for analysis.

### Input

- Complete Market Data

### Processing

- Remove suspended stocks
- Remove illiquid stocks
- Apply Nifty 200 filter
- Validate historical data
- Validate minimum candle history

### Output

```
Eligible Market Universe
```

If a stock fails here,

it never enters the system.

---

# 2. Watchlist Engine

## Purpose

Build the monthly watchlist.

### Processing

Checks

- Last 8+ closes above 200 EMA
- Rising 200 EMA
- Relative Strength
- Liquidity
- Average Volume
- Trend Stability

### Output

```
Watchlist Candidate
```

Monthly

Refresh Watchlist

Daily

Validate Existing Watchlist

A stock may remain in the watchlist but become temporarily ineligible.

---

# 3. Trend Engine

## Purpose

Verify long-term trend.

### Calculates

- EMA50
- EMA200
- EMA Slope
- Higher Highs
- Higher Lows
- Relative Strength
- Trend Score

### Decision

```
Trend Valid

↓

Continue
```

or

```
Trend Failed

↓

Reject
```

Trend Engine never looks for entries.

---

# 4. Consolidation Engine

## Purpose

Identify accumulation zones.

### Detects

- Support
- Resistance
- ATR Compression
- Range Width
- Range Duration
- Flat Price Structure
- Volume Compression

### Output

```
Consolidation Object
```

This becomes the foundation for the Liquidity Grab Engine.

---

# 5. Liquidity Grab Engine

## Purpose

Detect false breakdown recovery.

### Detects

- Support Break
- Recovery
- Recovery Window
- Volume Spike
- Strong Close
- Trend Confirmation

### Calculates

- Recovery Score
- Breakdown Quality
- Volume Ratio
- Recovery Strength

### Output

```
Liquidity Grab Object
```

This engine never decides whether to trade.

It only validates the setup.

---

# 6. Trade Validation Engine

## Purpose

Determine whether the complete setup qualifies as an executable trade.

### Validates

- Trend
- Consolidation
- Liquidity Grab
- Minimum RR
- Entry Zone
- Market Regime
- Sector Strength
- Earnings Window
- Trade Quality Score

If every mandatory rule passes,

```
Trade Candidate
```

Otherwise

```
Reject
```

No exceptions.

---

# 7. Risk Engine

## Purpose

Calculate financial risk.

### Calculates

- Entry Price
- Stop Loss
- ATR Buffer
- Position Size
- Risk Amount
- Risk Percentage
- Expected Reward
- Risk Reward Ratio

Formula

```
Quantity

=

Risk Amount

───────────────

Entry − Stop
```

Output

```
Risk Approved Trade
```

The Risk Engine never executes trades.

---

# 8. Portfolio Engine

## Purpose

Protect portfolio-level capital.

### Checks

- Available Cash
- Portfolio Heat
- Sector Exposure
- Correlation
- Open Positions
- Daily Risk
- Monthly Risk
- Maximum Allocation

Example

```
Risk Valid

↓

Approve
```

```
Sector Overloaded

↓

Reject
```

Portfolio safety always overrides strategy quality.

---

# 9. Order Execution Engine

## Purpose

Execute approved trades.

### Responsibilities

- Create Orders
- Submit Orders
- Verify Execution
- Retry Failed Requests
- Handle Partial Fills
- Synchronize Broker Status

Execution Layer

```
Trade

↓

Execution Engine

↓

Broker Adapter

↓

Broker API
```

This engine contains no trading logic.

---

# 10. Position Management Engine

## Purpose

Manage open trades.

### Monitors

- Current Price
- Unrealized P&L
- Holding Days
- ATR
- Stop Loss
- Target
- Trailing Stop
- Corporate Actions

Runs continuously until position closes.

---

# 11. Exit Engine

## Purpose

Determine when positions should close.

### Exit Types

Target Exit

↓

Partial Exit

↓

Breakeven

↓

Trailing Stop

↓

Emergency Exit

↓

Trend Failure Exit

The Exit Engine continuously reevaluates every open position.

---

# 12. Learning Engine

## Purpose

Learn from historical executions.

Every completed trade stores

- Market State
- Sector
- Indicators
- Trend
- Risk
- Entry
- Exit
- Profit
- Holding Period

Produces

- Performance Reports
- Strategy Statistics
- Research Dataset

Learning never modifies production rules automatically.

---

# 13. Analytics Engine

## Purpose

Measure platform performance.

Calculates

- Win Rate
- CAGR
- Drawdown
- Sharpe Ratio
- Sortino Ratio
- Profit Factor
- Expectancy
- Monthly Performance
- Sector Performance

Analytics supports research,

not execution.

---

# Engine Dependency Graph

```
Universe

↓

Watchlist

↓

Trend

↓

Consolidation

↓

Liquidity Grab

↓

Trade Validation

↓

Risk

↓

Portfolio

↓

Execution

↓

Position Management

↓

Exit

↓

Learning

↓

Analytics
```

Dependencies flow in one direction only.

Circular dependencies are prohibited.

---

# Failure Handling

Every engine should classify failures.

### Validation Failure

Trade Rejected

### Data Failure

Retry

### External Failure

Retry With Backoff

### Broker Failure

Pause Execution

### Unknown Failure

Escalate

No engine should silently fail.

---

# Retry Strategy

Only infrastructure failures are retried.

Examples

Retry

- Database Timeout
- Redis Timeout
- Broker Timeout
- Network Failure

Do Not Retry

- Invalid Trade
- Failed Trend
- Failed Risk
- Failed Portfolio Validation

Business rule failures are final.

---

# Engine Configuration

Every engine should expose configurable parameters.

Examples

Trend Engine

- EMA Length
- Trend Threshold

Consolidation Engine

- Minimum Candles
- Maximum Range

Liquidity Engine

- Recovery Window
- Volume Ratio

Risk Engine

- Maximum Risk
- ATR Multiplier

Configuration must be version controlled.

---

# Engine State Management

Each engine should remain stateless wherever possible.

Persistent information belongs in the database.

Temporary computations remain in memory only during execution.

Benefits

- Horizontal Scaling
- Simpler Recovery
- Easier Testing
- Predictable Behavior

---

# Logging Standard

Every engine logs

- Engine Name
- Execution Time
- Input Version
- Output Status
- Symbol
- Strategy Version
- Errors
- Latency

This enables complete trade reconstruction.

---

# Performance Targets

Recommended targets

| Engine | Target |
|----------|---------|
| Universe | < 5 sec |
| Watchlist | < 10 sec |
| Trend | < 100 ms / stock |
| Consolidation | < 150 ms / stock |
| Liquidity Grab | < 150 ms / stock |
| Trade Validation | < 50 ms |
| Risk | < 20 ms |
| Portfolio | < 20 ms |
| Execution | Network Dependent |
| Exit | Continuous |
| Learning | Background |
| Analytics | Background |

---

# Future Expansion

The engine architecture intentionally supports adding new strategies.

Future example

```
Trend Engine

↓

Strategy A

Strategy B

Strategy C

↓

Shared Risk Engine

↓

Shared Portfolio Engine

↓

Shared Execution Engine
```

Only strategy-specific engines change.

Everything after Trade Validation remains reusable.

---

# Engineering Decisions

The platform follows a **pipeline-based deterministic engine architecture** where every responsibility is isolated into an independent engine with clearly defined inputs, outputs, and validation rules.

Each engine owns exactly one stage of the trading lifecycle and communicates exclusively through standardized events, ensuring loose coupling, high observability, and horizontal scalability.

Business logic, risk management, portfolio protection, execution, and analytics remain completely separated, allowing the platform to evolve with additional strategies, brokers, AI models, and markets without requiring changes to the core execution pipeline.

This architecture ensures that every trade is fully explainable, reproducible, testable, and auditable while maintaining strict capital-preservation principles and production-grade engineering standards.