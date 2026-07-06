# Institutional Swing Trading Platform

# System Design Document

**Version:** 1.0

---

# Overview

The Institutional Swing Trading Platform is designed as a modular, event-driven, deterministic trading platform for Indian equity swing trading.

Unlike conventional trading bots that continuously search for trades and execute immediately, this platform behaves more like an institutional research desk.

Every trading decision passes through multiple independent analytical engines before capital is deployed.

The platform is intentionally built around one core philosophy:

> **Capital Preservation First. Profit Generation Second.**

Every subsystem exists to either

- reduce risk,
- improve decision quality,
- increase explainability,
- or improve long-term performance.

No engine is allowed to bypass another engine.

Every decision is deterministic, reproducible, auditable, and version-controlled.

---

# Core Design Principles

The complete system is built around the following engineering principles.

## Single Responsibility

Every engine performs one responsibility only.

Examples

Trend Engine

↓

Only trend detection.

Risk Engine

↓

Only risk calculation.

Portfolio Engine

↓

Only portfolio-level decisions.

No engine performs another engine's responsibility.

---

## Event Driven

The platform communicates through events instead of tightly coupled services.

Instead of

```
Trend Engine

↓

calls

↓

Entry Engine
```

the system follows

```
Trend Engine

↓

Trend Generated Event

↓

Entry Engine Consumes Event
```

This architecture provides

- Loose Coupling
- Easier Scaling
- Better Fault Isolation
- Independent Development

---

## Deterministic Trading

Production trading decisions are entirely deterministic.

AI may assist,

but AI never overrides production rules.

Every live trade should always be explainable using mathematical rules.

---

## Immutable History

Nothing important is deleted.

Every

trade,

signal,

indicator,

AI prediction,

strategy,

portfolio,

configuration,

and model

remains historically reproducible.

---

# High Level Architecture

```
                    USER

                     │

                     ▼

              Next.js Dashboard

                     │

REST API + WebSocket │

                     ▼

                API Gateway

                     │

──────────────────────────────────────────

                     │

        Authentication & Authorization

                     │

──────────────────────────────────────────

                     │

            Strategy Orchestrator

                     │

──────────────────────────────────────────

                     ▼

       Market Data Service

                     │

                     ▼

        Universe Engine

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

         Entry Engine

                     │

                     ▼

          Risk Engine

                     │

                     ▼

      Portfolio Engine

                     │

                     ▼

      Execution Engine

                     │

                     ▼

        Broker Adapter

                     │

                     ▼

        Broker APIs

──────────────────────────────────────────

                     │

                     ▼

       Learning Engine

                     │

                     ▼

         Analytics

                     │

                     ▼

          AI Engine

                     │

                     ▼

          Dashboard
```

---

# Complete Daily Workflow

The entire platform executes as a daily pipeline.

```
Market Closed

↓

Download Latest Market Data

↓

Validate Data

↓

Update Database

↓

Update Indicators

↓

Universe Filtering

↓

Generate Watchlist

↓

Trend Analysis

↓

Consolidation Detection

↓

Liquidity Grab Detection

↓

Entry Validation

↓

Risk Calculation

↓

Portfolio Validation

↓

Order Generation

↓

Broker Execution

↓

Position Monitoring

↓

Exit Evaluation

↓

Trade Completion

↓

Learning Engine

↓

Analytics Engine

↓

Dashboard Refresh

↓

Notifications
```

Every stage produces standardized outputs.

Those outputs become inputs for downstream engines.

---

# Component Responsibilities

## Market Data Service

Responsibilities

- Download Daily OHLCV
- Corporate Actions
- Adjust Historical Data
- Data Validation
- Missing Candle Detection

Output

```
Validated Market Dataset
```

---

## Universe Engine

Filters entire market.

Rules

- Nifty 200
- High Liquidity
- Eligible Securities
- Tradable Stocks

Output

```
Market Universe
```

---

## Watchlist Engine

Scans every eligible stock.

Checks

- Price Above 200 EMA
- Last 8–9 Candles Above EMA
- Trend Stability
- Relative Strength

Output

```
Monthly Watchlist
```

---

## Trend Engine

Calculates

- EMA50
- EMA200
- EMA Slope
- Trend Score
- Relative Strength

Output

```
Trend Object
```

---

## Consolidation Engine

Detects

- Support
- Resistance
- Range Width
- ATR Compression
- Consolidation Duration
- Consolidation Quality

Output

```
Consolidation Object
```

---

## Liquidity Grab Engine

Detects

- Support Breakdown
- Recovery
- Volume Spike
- Trap Quality
- Recovery Duration

Output

```
Liquidity Grab Object
```

---

## Entry Engine

Verifies

- Trend
- Consolidation
- Liquidity Grab
- RR
- Entry Zone

Output

```
Trade Candidate
```

---

## Risk Engine

Calculates

- Position Size
- Risk
- ATR Buffer
- Stop Loss
- Reward
- Quantity

Output

```
Risk Approved Trade
```

---

## Portfolio Engine

Checks

- Cash
- Portfolio Heat
- Sector Allocation
- Correlation
- Position Limits

Output

```
Approved Position
```

---

## Execution Engine

Responsible for

- Order Creation
- Retry
- Idempotency
- Broker Communication
- Position Sync

Output

```
Executed Position
```

---

## Exit Engine

Monitors

- Target
- Breakeven
- Staircase Trailing
- Emergency Exit
- Trend Failure

Output

```
Completed Trade
```

---

## Learning Engine

Processes

Completed Trades

↓

Feature Extraction

↓

Statistical Learning

↓

Recommendations

Output

```
Knowledge Base
```

---

## Analytics Engine

Calculates

- CAGR
- Win Rate
- Profit Factor
- Drawdown
- Portfolio Growth
- Strategy Metrics

---

## AI Engine

Uses

Historical Data

↓

Feature Engineering

↓

Model Training

↓

Opportunity Ranking

↓

Explainability

↓

Research Reports

AI never directly trades.

---

# Event Driven Architecture

Every engine communicates using events.

Example

```
Market Data Updated

↓

Universe Created

↓

Watchlist Updated

↓

Trend Generated

↓

Consolidation Generated

↓

Liquidity Grab Confirmed

↓

Trade Candidate Created

↓

Risk Approved

↓

Portfolio Approved

↓

Order Created

↓

Order Filled

↓

Position Opened

↓

Partial Exit

↓

Position Closed

↓

Trade Archived

↓

Learning Updated

↓

Analytics Updated
```

Every event contains

- Event ID
- Timestamp
- Symbol
- Strategy Version
- Payload

---

# Worker Architecture

Independent workers perform heavy computations.

```
Scheduler

↓

Market Worker

↓

Trend Workers

↓

Consolidation Workers

↓

Liquidity Workers

↓

Analytics Workers

↓

AI Workers

↓

Notification Workers
```

Workers never communicate directly.

Communication occurs through the event bus.

---

# Scheduler

The scheduler controls periodic execution.

Daily

- Market Data
- Indicator Update
- Strategy Scan
- Analytics

Weekly

- Reports
- Learning Summary

Monthly

- Watchlist Refresh
- Universe Refresh

Yearly

- Data Archive
- Database Optimization

---

# Database Architecture

Primary Database

```
PostgreSQL
```

Stores

- Market Data
- Trades
- Orders
- Portfolio
- Analytics
- Audit Logs

Redis

Stores

- Dashboard Cache
- Watchlist
- Sessions
- Frequently Used Objects

Object Storage

Stores

- Reports
- AI Models
- Historical Exports
- Backups

---

# API Architecture

Frontend communicates only with the API Gateway.

```
Dashboard

↓

API Gateway

↓

Authentication

↓

Application Services

↓

Trading Engines

↓

Database
```

No frontend communicates directly with the database.

---

# Broker Architecture

Broker communication is isolated.

```
Execution Engine

↓

Broker Adapter

↓

Zerodha

↓

Future Brokers
```

Every broker implements the same interface.

Changing brokers never changes business logic.

---

# Cache Architecture

Redis caches

- Portfolio
- Dashboard
- Watchlist
- Trend Objects
- User Sessions

Cache invalidation occurs automatically after updates.

---

# Queue Architecture

Long-running jobs execute asynchronously.

Examples

- Backtesting
- AI Training
- Report Generation
- Historical Imports

Queues prevent blocking APIs.

---

# Security Flow

Every request follows

```
Request

↓

JWT Validation

↓

Permission Validation

↓

Input Validation

↓

Business Logic

↓

Database

↓

Audit Log

↓

Response
```

Every important action is logged.

---

# Logging

Every service generates structured logs.

```
Timestamp

Request ID

Service

Event

Trade ID

User ID

Duration

Status
```

Logs feed into centralized monitoring.

---

# Monitoring

Infrastructure

- CPU
- Memory
- Disk

Application

- API Latency
- Queue Length
- Error Rate

Trading

- Orders
- Broker Status
- Portfolio

AI

- Training
- Prediction

---

# Deployment

```
Git

↓

CI Pipeline

↓

Tests

↓

Docker Build

↓

Staging

↓

Validation

↓

Production

↓

Monitoring
```

Every deployment is versioned.

Rollback is always supported.

---

# Trade Lifecycle

```
Stock Added To Universe

↓

Added To Watchlist

↓

Trend Confirmed

↓

Consolidation Found

↓

Liquidity Grab Detected

↓

Entry Approved

↓

Risk Approved

↓

Portfolio Approved

↓

Order Submitted

↓

Order Filled

↓

Position Opened

↓

Target 1

↓

Breakeven

↓

Trailing

↓

Exit

↓

Trade Archived

↓

Learning Updated

↓

Analytics Updated
```

---

# Technology Stack

Frontend

- Next.js
- React
- TailwindCSS
- TradingView Charts

Backend

- Python
- FastAPI

Database

- PostgreSQL

Cache

- Redis

Queue

- RabbitMQ

AI

- PyTorch
- LightGBM
- Scikit-learn

Monitoring

- Prometheus
- Grafana

Logging

- Loki

Deployment

- Docker
- Kubernetes (Future)

Cloud

- AWS / GCP

---

# Engineering Decisions

The platform intentionally separates **analysis**, **decision-making**, **execution**, **learning**, and **analytics** into independent engines connected through an event-driven architecture.

Each engine owns a single responsibility, publishes standardized outputs, and consumes standardized inputs, allowing the system to remain modular, testable, horizontally scalable, and resilient to failures.

Deterministic trading rules remain the foundation of production execution, while AI operates exclusively as a research and decision-support layer. This separation preserves explainability, simplifies auditing, and ensures that every production trade can be reproduced exactly using the strategy version, configuration version, and historical market data that existed at the time of execution.

The resulting architecture provides a scalable foundation capable of supporting additional strategies, brokers, markets, AI models, and research workflows without requiring fundamental architectural redesign.