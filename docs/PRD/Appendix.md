# 33. Appendix

---

# Overview

The Appendix serves as the permanent reference section of the Institutional Swing Trading Platform PRD.

Unlike previous chapters that describe architecture and implementation, this chapter defines the common terminology, formulas, workflows, conventions, standards, assumptions, and references used throughout the platform.

Every engineer, researcher, AI model, tester, or future contributor should be able to understand the platform consistently by referring to this appendix.

The Appendix functions as the project's shared vocabulary and technical reference.

---

# Glossary

## ATR (Average True Range)

A volatility indicator that measures the average daily price movement over a specified number of periods.

Used for:

- Stop Loss Buffer
- Volatility Measurement
- Position Risk

---

## 200 EMA

The 200-day Exponential Moving Average.

Used to determine the primary trend.

Rules

```
Price > 200 EMA

↓

Bullish Trend
```

```
Price < 200 EMA

↓

No Long Trades
```

---

## Consolidation

A period where price trades inside a relatively narrow range.

Characteristics

- Low Volatility
- Stable Support
- Stable Resistance
- Reduced Momentum

This represents the area where institutions may accumulate positions.

---

## Liquidity Grab

A temporary breakdown below support intended to trigger retail stop-losses before price recovers back into the consolidation range.

Required characteristics:

- Support Breakdown
- Recovery
- Elevated Volume
- Institutional Confirmation

This is the primary edge of Version 1.

---

## Recovery

The movement where price returns back above the original support after a liquidity grab.

Recovery may occur:

- Same Candle
- Multiple Candles Later

There is no fixed recovery duration.

---

## Trend Score

A normalized score representing overall trend quality.

Possible inputs

- EMA Alignment
- EMA Slope
- Relative Strength
- Higher Highs
- Higher Lows

Higher values indicate stronger trends.

---

## Portfolio Heat

The total percentage of portfolio capital currently at risk.

Example

```
Trade A

1%

Trade B

1%

Trade C

1%

↓

Portfolio Heat

3%
```

---

## Risk-Reward Ratio (RR)

```
Reward

────────────

Risk
```

Version 1 Minimum

```
1 : 2
```

Trades below this threshold are rejected.

---

## Breakeven

Moving the stop-loss to the entry price.

Purpose

Remove downside risk while allowing trend continuation.

---

## Staircase Trailing

A trailing stop methodology.

```
Higher Low

↓

Move Stop

↓

Higher Low

↓

Move Stop
```

The stop-loss only moves upward.

Never downward.

---

## Market Regime

Classification of overall market behavior.

Possible values

- Bullish
- Bearish
- Sideways
- High Volatility
- Low Volatility

Market regime influences opportunity quality.

---

# Mathematical Formula Reference

## Position Size

```
Quantity

=

Risk Amount

────────────────────────────

Entry Price − Stop Loss
```

---

## Risk Amount

```
Capital

×

Risk Percentage
```

Example

```
Capital

₹10,00,000

Risk

1%

↓

₹10,000
```

---

## Risk Reward

```
Reward

────────

Risk
```

Example

```
Entry

100

Stop

95

Target

110

Risk

5

Reward

10

RR

2
```

---

## Portfolio Heat

```
Trade Risk 1

+

Trade Risk 2

+

Trade Risk 3
```

---

## Profit Factor

```
Gross Profit

──────────────

Gross Loss
```

---

## Expectancy

```
Average Win × Win Rate

−

Average Loss × Loss Rate
```

Positive expectancy is required.

---

## CAGR

```
Ending Value

──────────────

Beginning Value

^(1 / Years)

−1
```

---

## Maximum Drawdown

Largest percentage decline from portfolio peak.

Used to measure downside risk.

---

# Platform Workflow

Complete production workflow.

```
Market Data

↓

Universe Filtering

↓

Watchlist Generation

↓

Trend Analysis

↓

Consolidation Detection

↓

Liquidity Grab Detection

↓

Entry Validation

↓

Risk Validation

↓

Portfolio Validation

↓

Order Execution

↓

Position Monitoring

↓

Exit Management

↓

Learning Engine

↓

Analytics

↓

Dashboard
```

Every production trade follows this workflow.

---

# Event Lifecycle

```
Market Data Updated

↓

Watchlist Updated

↓

Trend Confirmed

↓

Consolidation Created

↓

Liquidity Grab Confirmed

↓

Trade Candidate

↓

Risk Approved

↓

Portfolio Approved

↓

Order Executed

↓

Position Open

↓

Position Closed

↓

Learning

↓

Analytics
```

Events form the communication backbone of the platform.

---

# State Machines

## Watchlist

```
Rejected

↓

Candidate

↓

Watchlisted

↓

Monitoring

↓

Entry Candidate

↓

Executed

↓

Archived
```

---

## Position

```
Pending

↓

Open

↓

Partial Exit

↓

Breakeven

↓

Trailing

↓

Closed

↓

Archived
```

---

## Order

```
Created

↓

Submitted

↓

Accepted

↓

Partially Filled

↓

Filled

↓

Cancelled

↓

Rejected
```

---

# Naming Conventions

Tables

```
snake_case
```

Example

```
trade_candidates
```

---

Columns

```
snake_case
```

Example

```
entry_price
```

---

API

```
kebab-case

or

REST Resource Naming
```

Example

```
/trade-candidates
```

---

Variables

Backend

```
snake_case
```

Frontend

```
camelCase
```

Classes

```
PascalCase
```

---

# Time Standards

The platform stores all timestamps in UTC.

The Dashboard converts timestamps into the user's configured timezone.

Benefits

- Consistency
- Simpler Analytics
- Easier Multi-Region Expansion

---

# Currency Standards

Primary Currency

```
Indian Rupee (INR)
```

Future versions may support:

- USD
- EUR
- GBP
- JPY

---

# Precision Standards

Prices

```
2 Decimal Places
```

Percentages

```
4 Decimal Places
```

Ratios

```
2 Decimal Places
```

Performance Metrics

```
4 Decimal Places
```

---

# Logging Standards

Every log should include:

- Timestamp
- Request ID
- User ID
- Strategy Version
- Service
- Severity
- Event
- Duration

Logs should remain machine-readable.

---

# Error Code Standards

Examples

```
AUTH_001

Authentication Failed
```

```
RISK_002

Risk Limit Exceeded
```

```
ENTRY_004

Entry Validation Failed
```

```
BROKER_005

Broker Timeout
```

```
SYSTEM_001

Unexpected Error
```

Every error code should be unique.

---

# Versioning Standards

Every important object references:

- Platform Version
- Strategy Version
- API Version
- AI Model Version
- Configuration Version
- Database Schema Version

Historical reproducibility depends on complete version tracking.

---

# Documentation Standards

Every production module should include:

- Overview
- Inputs
- Outputs
- Dependencies
- Configuration
- Failure Modes
- Tests
- Version History

Documentation evolves alongside code.

---

# Design Assumptions

Version 1 assumes:

- Daily Timeframe Only
- Indian Equity Cash Market
- Nifty 200 Universe
- Long Positions Only
- Swing Trading
- Deterministic Trading Rules
- Human-Supervised Production
- Single Primary Strategy

Future versions may expand these assumptions.

---

# Out of Scope (Version 1)

The following are intentionally excluded.

- Intraday Trading
- Options Trading
- Futures Trading
- Leverage
- Margin Trading
- High-Frequency Trading
- Automatic Strategy Evolution
- AI-Controlled Order Execution
- Social Trading
- Copy Trading
- Multi-Exchange Support
- Multi-Currency Support

These items belong to future roadmap phases.

---

# Key Engineering Principles

The platform is built upon the following principles.

- Capital Preservation First
- Deterministic Decision Making
- Explainability
- Modularity
- Event-Driven Architecture
- Version Everything
- Immutable Historical Records
- Research Before Production
- AI Assists, Rules Decide
- Security By Design
- Test Automation
- Horizontal Scalability
- Observability Everywhere

These principles should guide every future engineering decision.

---

# Reference Architecture Summary

```
Frontend

↓

API Gateway

↓

Authentication

↓

Trading Engines

↓

Portfolio

↓

Execution

↓

Broker

↓

Learning

↓

Analytics

↓

AI

↓

Dashboard
```

Every module remains independently replaceable.

---

# Document Revision History

| Version | Date | Description |
|----------|------|-------------|
| 1.0 | Initial Release | Complete Institutional Swing Trading Platform PRD |
| Future | TBD | Subsequent revisions and feature additions |

---

# Final Statement

This Product Requirements Document defines the complete vision, architecture, engineering standards, trading philosophy, research methodology, operational workflows, and implementation blueprint for the **Institutional Swing Trading Platform**.

The platform is intentionally designed as a deterministic, explainable, research-driven trading system where **capital preservation takes precedence over profit maximization**.

Every trading decision originates from objective rules, every system action is auditable, every historical outcome contributes to learning, and every future improvement must pass through research, backtesting, validation, and controlled deployment before reaching production.

This document serves as the authoritative specification for designing, developing, testing, deploying, operating, and evolving the platform. Any future enhancements, architectural modifications, or strategic changes should remain aligned with the engineering principles, governance processes, and product philosophy established throughout this PRD.

The long-term objective is not simply to automate trading, but to build an institutional-grade quantitative trading and research platform that combines disciplined risk management, deterministic execution, explainable AI, continuous learning, and production-grade software engineering into a unified, scalable, and maintainable system.