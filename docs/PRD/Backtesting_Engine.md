# 20. Backtesting Engine

---

# Overview

The Backtesting Engine is responsible for validating whether the trading strategy possesses a genuine statistical edge before risking real capital.

The purpose of backtesting is **not** to maximize historical profit.

Instead, its purpose is to determine whether the strategy behaves consistently across different market environments while respecting the platform's philosophy of capital preservation and disciplined execution.

Every modification made to the production strategy must pass through the Backtesting Engine before it can be considered for paper trading or live deployment.

The Backtesting Engine is therefore the bridge between research and production.

---

# Objective

The Backtesting Engine answers one fundamental question.

> **"If this exact strategy had been executed historically using only information available at that point in time, would it have demonstrated a statistically significant positive expectancy?"**

Possible outcomes are:

```
Strategy Validated
```

```
Strategy Rejected
```

```
Requires Further Research
```

The objective is evidence,

not optimism.

---

# Core Philosophy

The platform follows one permanent rule.

> **A strategy that cannot survive historical validation should never receive real capital.**

Historical performance does not guarantee future performance.

However,

a strategy that consistently fails historical testing is unlikely to succeed in production.

Backtesting therefore acts as the minimum validation requirement.

---

# Validation Pipeline

Every strategy follows the same lifecycle.

```
Strategy Definition

↓

Historical Data Selection

↓

Simulation

↓

Trade Generation

↓

Portfolio Simulation

↓

Performance Analysis

↓

Statistical Validation

↓

Backtesting Report

↓

Paper Trading

↓

Production
```

No strategy should skip any stage.

---

# Historical Data Requirements

The Backtesting Engine should use high-quality adjusted historical data.

The dataset should include:

- Daily OHLC
- Volume
- Corporate Actions
- Index Data
- Sector Data

Historical data must be free from:

- Missing candles
- Duplicate records
- Incorrect stock splits
- Incorrect bonus adjustments

Data quality directly influences strategy reliability.

---

# Simulation Philosophy

The Backtesting Engine should simulate trading exactly as the production system behaves.

It must use the same:

- Watchlist rules
- Trend Engine
- Consolidation Engine
- Liquidity Grab Engine
- Entry Engine
- Risk Engine
- Portfolio Engine
- Exit Engine

Backtesting must never simplify production logic.

Otherwise,

results become unrealistic.

---

# Event-Driven Simulation

The simulation progresses one completed trading day at a time.

Example

```
Day 1

↓

Update Market Data

↓

Update Watchlist

↓

Trend Analysis

↓

Consolidation Analysis

↓

Liquidity Grab Detection

↓

Entry Validation

↓

Risk Validation

↓

Portfolio Validation

↓

Execute Orders

↓

Manage Positions

↓

Proceed To Day 2
```

The simulation never accesses future data.

---

# Look-Ahead Bias Prevention

The Backtesting Engine must never use information that would not have been available on the simulated trading date.

Incorrect Example

Using tomorrow's candle to validate today's trade.

Correct Example

Every decision uses only historical information available at that point in time.

Preventing look-ahead bias is mandatory.

---

# Survivorship Bias Prevention

Historical simulations should use the actual market universe that existed during each historical period.

Example

A stock removed from the Nifty 200 in 2022 should still appear when simulating data from 2021.

Similarly,

stocks added later should not appear before they historically existed.

This prevents survivorship bias.

---

# Corporate Action Handling

Historical simulations must correctly account for:

- Stock Splits
- Bonus Issues
- Dividends
- Symbol Changes
- Mergers
- Demergers

Every simulation should operate on adjusted historical prices.

---

# Transaction Cost Simulation

Backtesting should simulate realistic trading costs.

Examples include:

- Brokerage
- STT
- Exchange Charges
- GST
- Stamp Duty
- SEBI Charges

Ignoring transaction costs creates unrealistic profitability.

---

# Slippage Simulation

Execution prices rarely match theoretical prices.

The simulation should estimate realistic slippage.

Possible models include:

- Fixed Slippage
- Percentage Slippage
- Volatility-Based Slippage

The selected model should remain configurable.

---

# Position Management Simulation

Every simulated position should behave exactly like production.

Examples

- Initial Stop Loss
- Partial Profit Booking
- Breakeven Movement
- Staircase Trailing
- Emergency Exit

No shortcuts should be introduced.

---

# Portfolio Simulation

Backtesting should simulate the entire portfolio rather than independent trades.

The simulation continuously evaluates:

- Cash Balance
- Open Positions
- Portfolio Heat
- Sector Exposure
- Correlation
- Capital Allocation

This produces realistic portfolio performance.

---

# Performance Metrics

The Backtesting Engine calculates comprehensive statistics.

Examples

Return Metrics

- Total Return
- Annual Return
- CAGR

Risk Metrics

- Maximum Drawdown
- Average Drawdown
- Portfolio Heat

Trade Metrics

- Win Rate
- Loss Rate
- Average RR
- Expectancy
- Profit Factor

Portfolio Metrics

- Sharpe Ratio
- Sortino Ratio
- Calmar Ratio
- Exposure
- Cash Utilization

Operational Metrics

- Average Holding Period
- Average Recovery Duration
- Trade Frequency

These metrics become the foundation for strategy evaluation.

---

# Walk-Forward Validation

Historical testing alone is insufficient.

The Backtesting Engine should support:

```
Training Period

↓

Parameter Selection

↓

Validation Period

↓

Performance Evaluation

↓

Repeat
```

Walk-forward validation reduces overfitting.

---

# Parameter Optimization

The engine should support controlled experimentation.

Examples

```
EMA

180

↓

190

↓

200

↓

210
```

```
Recovery Window

3 Days

↓

5 Days

↓

7 Days
```

```
Volume Ratio

2.5

↓

3.0

↓

3.5

↓

4.0
```

Every experiment should produce an independent report.

---

# Strategy Versioning

Every backtest should reference:

- Strategy Version
- Configuration Version
- Indicator Version
- Dataset Version

Results should remain reproducible.

---

# Comparative Analysis

Researchers should compare:

- Strategy Version 1 vs Version 2
- Different Market Regimes
- Different Sectors
- Different Parameter Sets

Only statistically meaningful improvements should advance to paper trading.

---

# Backtesting Report

Every completed simulation generates a standardized report.

Example

```
Strategy

Version 1.3

Testing Period

2016–2026

Trades

428

Win Rate

48%

Profit Factor

2.04

Expectancy

Positive

Maximum Drawdown

11.8%

Average RR

2.7

Annual Return

34.2%

Status

Validated
```

This report becomes part of the permanent research archive.

---

# Failure Handling

Examples

### Missing Historical Data

Pause simulation.

Repair dataset.

Restart.

---

### Corporate Action Conflict

Reject affected period until corrected.

---

### Configuration Mismatch

Abort simulation.

Log version conflict.

---

### Invalid Strategy Version

Reject execution.

---

### Corrupted Dataset

Exclude until validated.

---

# Configuration

The following parameters remain configurable.

- Simulation Period
- Initial Capital
- Transaction Cost Model
- Slippage Model
- Walk-Forward Window
- Strategy Version
- Dataset Version
- Portfolio Constraints

Every simulation stores the complete configuration used.

---

# Engineering Decisions

The Backtesting Engine remains completely isolated from production trading.

It does **not**:

- Place live orders.
- Modify production strategies.
- Override trading rules.
- Alter portfolio state.
- Execute broker operations.

Its sole responsibility is objectively evaluating historical performance under production-identical rules.

This separation ensures that research activities cannot accidentally affect live trading while maintaining complete reproducibility.

---

## Open Questions

1. What historical period best represents multiple market regimes for validating the strategy?

2. Which transaction cost and slippage model most accurately reflects real-world execution?

3. How many completed trades are required before considering a strategy statistically reliable?

4. What improvement threshold should justify replacing the current production strategy?

5. How should conflicting results across different market regimes influence strategy approval?

6. Which parameters should remain fixed, and which should be optimized during research?

7. What minimum backtesting standards must be satisfied before a strategy is promoted to Paper Trading?