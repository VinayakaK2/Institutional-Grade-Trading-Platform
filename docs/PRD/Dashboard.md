# 22. Dashboard

---

# Overview

The Dashboard is the primary interface between the trader and the Institutional Swing Trading Platform.

Unlike conventional trading dashboards that primarily display charts and order books, this dashboard is designed around **decision intelligence**.

The user should never be forced to manually analyze hundreds of charts, calculate risk, compare indicators, or determine whether a trade satisfies the strategy.

Every analytical engine inside the platform already performs those responsibilities.

The Dashboard exists to present the outputs of those engines in a clear, explainable, and actionable manner.

The guiding philosophy is simple:

> **Show decisions, not raw data.**

The platform should surface only the information necessary for decision-making while allowing deeper investigation whenever required.

---

# Objective

The Dashboard answers one fundamental question.

> **"What is the current state of the market, my portfolio, and the trading system?"**

The Dashboard should provide complete situational awareness in one place.

It should enable the trader to understand:

- Market Health
- Portfolio Health
- Active Opportunities
- Open Positions
- System Status
- Research Insights

without manually opening charts or reports.

---

# Core Philosophy

The Dashboard follows three permanent principles.

### Principle 1

Clarity before complexity.

---

### Principle 2

Explain decisions instead of displaying indicators.

---

### Principle 3

Surface exceptions, not noise.

If nothing important happened,

the dashboard should remain calm.

If something important happened,

the dashboard should immediately highlight it.

---

# Dashboard Architecture

The Dashboard consists of multiple independent modules.

```
Dashboard

│

├── Market Overview

├── Watchlist

├── Trade Opportunities

├── Active Positions

├── Portfolio

├── Risk Monitor

├── Analytics

├── Learning Center

├── AI Insights

├── Notifications

└── System Health
```

Every widget should operate independently.

Failure of one widget should not affect the remaining dashboard.

---

# Home Dashboard

The Home Dashboard provides an executive summary.

Displayed information includes:

Market Status

Portfolio Value

Available Cash

Today's Watchlist

Open Positions

Pending Opportunities

Portfolio Heat

System Status

Latest Notifications

The trader should understand the complete platform status within a few seconds.

---

# Market Overview

This section summarizes the current market environment.

Displayed information:

- Market Regime
- Index Trend
- Market Breadth
- Volatility
- Sector Performance
- Market Risk Level

Example

```
Market Status

Bullish

Trend Strength

Strong

Market Risk

Low

Top Sector

Banking

Weakest Sector

IT
```

This section provides context for every trading decision.

---

# Watchlist Dashboard

Displays every stock currently being monitored.

Columns include:

- Symbol
- Company Name
- Trend Score
- Watchlist Rank
- Current Status
- Consolidation Status
- Liquidity Grab Status
- Last Updated

Possible statuses:

```
Monitoring
```

```
Trend Failed
```

```
Waiting For Consolidation
```

```
Liquidity Grab Detected
```

```
Entry Candidate
```

The user should immediately understand the progress of every stock.

---

# Opportunity Dashboard

Displays every trade candidate.

Each card should include:

- Symbol
- Entry Price
- Stop Loss
- Risk
- Risk-Reward
- Trend Score
- Liquidity Grab Score
- Market Status
- Approval Status

Example

```
RELIANCE

Trend

92

Liquidity Grab

95

Entry

₹2,856

Risk

₹34

RR

2.8

Status

Approved
```

The dashboard should explain **why** the opportunity exists.

---

# Active Position Dashboard

Displays every open position.

Information includes:

- Entry Price
- Current Price
- Unrealized P&L
- Current Stop Loss
- Breakeven Status
- Trailing Stop
- Holding Period
- Exit Status

Visual indicators should clearly distinguish:

- Winning Positions
- Losing Positions
- Positions Near Stop Loss
- Positions Near Target

---

# Portfolio Dashboard

Displays portfolio-level statistics.

Examples

Portfolio Value

Cash

Invested Capital

Portfolio Heat

Sector Allocation

Exposure

Largest Position

Largest Sector

Daily P&L

Monthly P&L

Annual Return

This dashboard represents the overall health of the trading account.

---

# Risk Dashboard

The Risk Dashboard displays every important portfolio risk metric.

Examples

- Current Portfolio Heat
- Maximum Allowed Heat
- Current Risk Exposure
- Sector Concentration
- Correlation Score
- Cash Reserve
- Open Risk
- Largest Position Risk

Warnings should appear automatically whenever predefined thresholds are exceeded.

---

# Analytics Dashboard

Displays long-term trading statistics.

Examples

- Total Trades
- Win Rate
- Loss Rate
- Profit Factor
- Average RR
- Expectancy
- Drawdown
- Equity Curve
- Holding Period
- Monthly Returns

Charts should emphasize trends rather than isolated numbers.

---

# Learning Dashboard

Displays insights generated by the Learning Engine.

Examples

Recent Observations

```
Short Recovery

↓

Higher Expectancy
```

```
Volume Ratio > 3.5

↓

Improved Performance
```

```
Long Consolidation

↓

Lower Drawdown
```

These observations remain informational.

They never modify production strategy automatically.

---

# AI Dashboard

Displays AI-generated research.

Examples

- Opportunity Rankings
- Feature Importance
- Pattern Reports
- Strategy Recommendations
- Model Confidence
- Research Alerts

Every AI recommendation should include:

- Confidence
- Explanation
- Model Version

The dashboard must clearly distinguish AI recommendations from deterministic production decisions.

---

# Notification Center

Displays chronological platform events.

Examples

```
Watchlist Updated
```

```
New Entry Candidate
```

```
Trade Executed
```

```
Partial Exit Completed
```

```
Emergency Exit Triggered
```

```
Broker Connection Lost
```

Notifications should support:

- Priority
- Category
- Timestamp
- Related Symbol

---

# System Health Dashboard

Displays engineering metrics.

Examples

- Database Status
- API Status
- Broker Connection
- Scheduler Status
- AI Service
- Data Feed Status
- Background Jobs
- Queue Health

Possible states

```
Healthy
```

```
Warning
```

```
Critical
```

This dashboard assists operational monitoring.

---

# Trade Detail Page

Selecting any completed trade should display complete audit information.

Sections include:

Trade Summary

↓

Trend Analysis

↓

Consolidation Analysis

↓

Liquidity Grab Analysis

↓

Risk Analysis

↓

Portfolio State

↓

Execution Timeline

↓

Exit Timeline

↓

Learning Summary

↓

AI Explanation

The trader should be able to reconstruct every decision.

---

# Search & Filtering

Every dashboard should support filtering.

Examples

Filter by:

- Symbol
- Sector
- Status
- Strategy Version
- Date Range
- Trade Result
- Market Regime
- Risk Level

Searching historical information should require only a few seconds.

---

# Real-Time Updates

Although the strategy operates on daily candles,

certain dashboard components should update continuously.

Examples

- Broker Status
- Order Status
- Portfolio Value
- Notifications
- System Health

Analytical components update after market data refresh.

Operational components update in real time.

---

# User Interface Principles

The Dashboard should remain:

- Minimal
- Clean
- Explainable
- Responsive
- Information Dense
- Easy To Navigate

Important information should appear first.

Rarely used information should remain accessible but secondary.

---

# Failure Handling

Examples

### Market Data Delayed

Display warning.

Continue using latest validated data.

---

### Broker Offline

Disable execution widgets.

Maintain analytics.

---

### AI Service Offline

Continue deterministic platform.

Display service warning.

---

### Database Maintenance

Display read-only mode.

---

### Scheduler Failure

Highlight missed jobs.

Notify administrator.

---

# Dashboard Configuration

Configurable settings include:

- Theme
- Widget Layout
- Default Landing Page
- Time Zone
- Notification Preferences
- Currency
- Refresh Frequency
- Advanced View Toggle

User preferences should remain independent of strategy configuration.

---

# Engineering Decisions

The Dashboard intentionally contains **no business logic**.

It never:

- Detects trends.
- Calculates indicators.
- Approves trades.
- Calculates risk.
- Places orders.

Every displayed value originates from specialized backend engines.

The Dashboard acts purely as a presentation layer.

This separation ensures that user interface changes never affect trading logic while allowing frontend development to evolve independently from backend analytical systems.

---

## Open Questions

1. Which dashboard widgets provide the highest decision-making value while minimizing information overload?

2. Which portfolio metrics should always remain visible on the home screen?

3. Should AI insights appear alongside deterministic decisions or within a separate research workspace?

4. How should the dashboard adapt when supporting multiple portfolios or multiple users?

5. Which visualizations most effectively communicate long-term strategy performance and risk?

6. What level of customization should users have over dashboard layouts without compromising usability?

7. Which operational alerts should interrupt the user immediately, and which should remain passive notifications?