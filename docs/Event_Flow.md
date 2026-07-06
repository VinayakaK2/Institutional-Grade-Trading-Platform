# EVENT_FLOW.md

# Institutional Swing Trading Platform

**Version:** 1.0

---

# Overview

The Event Flow defines how information moves throughout the Institutional Swing Trading Platform.

Instead of tightly coupling engines together through direct function calls, every major activity inside the platform generates standardized events.

Each engine publishes events after completing its responsibility, and downstream engines subscribe only to the events they require.

This event-driven architecture ensures:

- Loose Coupling
- Independent Scaling
- Easy Debugging
- Event Replay
- Fault Isolation
- Complete Auditability

Every important business action becomes an event.

Nothing important happens silently.

---

# Event Lifecycle

Every event follows the same lifecycle.

```
Business Action

↓

Generate Event

↓

Validate Event

↓

Publish Event

↓

Store Event

↓

Consume Event

↓

Execute Business Logic

↓

Generate Next Event

↓

Archive
```

Every event receives:

- Event ID
- Timestamp
- Event Type
- Correlation ID
- Strategy Version
- Payload
- Status

This enables complete reconstruction of every trading decision.

---

# Complete Trading Event Flow

```
Market Closed

↓

Market Data Downloaded

↓

Market Data Validated

↓

Market Data Stored

↓

Universe Generated

↓

Watchlist Updated

↓

Trend Generated

↓

Consolidation Generated

↓

Liquidity Grab Detected

↓

Trade Candidate Created

↓

Risk Approved

↓

Portfolio Approved

↓

Order Created

↓

Order Submitted

↓

Order Filled

↓

Position Opened

↓

Target Reached

↓

Partial Exit

↓

Breakeven Activated

↓

Trailing Stop Updated

↓

Position Closed

↓

Trade Archived

↓

Learning Updated

↓

Analytics Updated

↓

Dashboard Updated

↓

Notifications Sent
```

Every stage publishes exactly one standardized event.

---

# Market Data Events

### MarketDataDownloaded

Generated after successful download.

Consumers

- Validation Engine

---

### MarketDataValidated

Consumers

- Universe Engine

---

### MarketDataRejected

Generated if corrupted data is detected.

Consumers

- Monitoring
- Notification Engine

---

### MarketDataStored

Consumers

- Indicator Workers
- Strategy Pipeline

---

# Universe Events

### UniverseGenerated

Payload

- Symbols
- Count
- Timestamp

Consumers

- Watchlist Engine

---

### UniverseFailed

Consumers

- Monitoring
- Scheduler

---

# Watchlist Events

### WatchlistGenerated

Contains

- Eligible Symbols
- Ranking
- Market Regime

Consumers

- Trend Engine

---

### WatchlistUpdated

Generated whenever a stock enters or leaves the watchlist.

Consumers

- Dashboard
- Notifications

---

# Trend Events

### TrendCalculated

Contains

- Trend Score
- EMA Values
- Relative Strength

Consumers

- Consolidation Engine

---

### TrendRejected

Consumers

- Analytics
- Dashboard

Rejected trades remain historically available.

---

# Consolidation Events

### ConsolidationDetected

Contains

- Support
- Resistance
- Duration
- ATR Compression

Consumers

- Liquidity Grab Engine

---

### ConsolidationRejected

Consumers

- Analytics

---

# Liquidity Grab Events

### LiquidityGrabDetected

Contains

- Recovery
- Volume Ratio
- Recovery Duration
- Quality Score

Consumers

- Trade Validation Engine

---

### LiquidityGrabRejected

Consumers

- Analytics

---

# Trade Validation Events

### TradeCandidateCreated

Contains

- Entry
- Stop Loss
- Target
- RR
- Trade Score

Consumers

- Risk Engine

---

### TradeRejected

Contains

Reason

Examples

- Low RR
- Weak Trend
- Poor Volume
- Invalid Structure

Consumers

- Analytics

---

# Risk Events

### RiskApproved

Contains

- Quantity
- Position Size
- Risk Amount

Consumers

- Portfolio Engine

---

### RiskRejected

Examples

- Risk Too High
- Invalid Position Size

Consumers

- Dashboard
- Analytics

---

# Portfolio Events

### PortfolioApproved

Consumers

- Execution Engine

---

### PortfolioRejected

Examples

- Portfolio Heat
- Sector Exposure
- Correlation

Consumers

- Dashboard

---

# Order Events

### OrderCreated

↓

### OrderSubmitted

↓

### OrderAccepted

↓

### OrderFilled

↓

### OrderPartiallyFilled

↓

### OrderRejected

↓

### OrderCancelled

Consumers

- Position Engine
- Dashboard
- Notifications

---

# Position Events

### PositionOpened

Generated after successful execution.

Consumers

- Exit Engine

---

### PositionUpdated

Generated whenever

- Price
- Stop
- Target
- Quantity

changes.

---

### PositionClosed

Consumers

- Learning
- Analytics

---

# Exit Events

### PartialExitExecuted

↓

### BreakevenActivated

↓

### TrailingStopUpdated

↓

### EmergencyExitExecuted

↓

### PositionClosed

Consumers

- Portfolio
- Learning
- Dashboard

---

# Learning Events

### TradeLearned

Generated after feature extraction.

Consumers

- AI Engine

---

### LearningReportGenerated

Consumers

- Dashboard

---

# Analytics Events

### AnalyticsUpdated

Generated whenever KPIs change.

Consumers

- Dashboard

---

### MonthlyReportGenerated

↓

### YearlyReportGenerated

↓

### StrategyReportGenerated

Consumers

- Notification Engine

---

# AI Events

### DatasetPrepared

↓

### ModelTrainingStarted

↓

### ModelTrainingCompleted

↓

### PredictionGenerated

↓

### ResearchCompleted

AI events never affect production execution directly.

---

# Notification Events

Notification Engine subscribes to nearly every major business event.

Examples

```
Trade Approved

↓

Send Notification
```

```
Order Filled

↓

Send Notification
```

```
Portfolio Heat High

↓

Critical Alert
```

Notification delivery remains asynchronous.

---

# Dashboard Events

Dashboard subscribes to

- Watchlist
- Orders
- Portfolio
- Analytics
- Notifications
- Learning

The UI becomes reactive instead of polling every service.

---

# Event Payload Standard

Every event follows a common structure.

```json
{
  "event_id": "UUID",
  "event_type": "TrendCalculated",
  "timestamp": "...",
  "correlation_id": "...",
  "strategy_version": "1.0",
  "symbol": "RELIANCE",
  "payload": {},
  "status": "SUCCESS"
}
```

This standardization simplifies debugging and replay.

---

# Event Ordering

Events should always preserve causal order.

Example

Correct

```
Order Created

↓

Order Submitted

↓

Order Filled

↓

Position Opened
```

Incorrect

```
Position Opened

↓

Order Filled
```

Ordering guarantees system consistency.

---

# Event Retry Strategy

Infrastructure failures

↓

Retry

Business rule failures

↓

No Retry

Duplicate events

↓

Ignore

Unknown failures

↓

Dead Letter Queue

This prevents infinite processing loops.

---

# Dead Letter Queue (DLQ)

Events that repeatedly fail processing are moved to a DLQ.

Examples

- Corrupted Payload
- Unknown Event Type
- Unexpected Processing Failure

DLQ events require investigation before replay.

---

# Event Replay

Historical events can be replayed for:

- Debugging
- Backtesting
- Analytics Recalculation
- Disaster Recovery

Replay should never modify historical records.

Instead, new outputs should be generated.

---

# Event Versioning

Every event includes

- Event Version
- Strategy Version
- Configuration Version

Future changes remain backward compatible through versioned event contracts.

---

# Event Monitoring

Metrics

- Events Published
- Events Consumed
- Failed Events
- Retry Count
- Queue Latency
- Processing Time

These metrics help identify bottlenecks.

---

# Event Storage

Every important event should be persisted.

Benefits

- Auditability
- Replay
- Historical Analysis
- AI Dataset Generation
- Compliance

Old events may be archived but never silently discarded.

---

# Failure Handling

Examples

Event Processing Failed

↓

Retry

↓

DLQ

↓

Alert

Missing Consumer

↓

Log Warning

↓

Continue

Duplicate Event

↓

Ignore

↓

Log

Every failure path should be deterministic.

---

# Engineering Decisions

The platform adopts a **fully event-driven architecture** where every business action is represented as a standardized event flowing through independent engines.

This approach decouples analytical logic from execution logic, enables horizontal scalability, simplifies debugging through complete event history, supports replay for research and disaster recovery, and ensures every trading decision remains fully traceable from market data ingestion to final portfolio analytics.

By treating events as first-class system objects, the platform gains resilience, extensibility, and long-term maintainability while preserving deterministic trading behavior.