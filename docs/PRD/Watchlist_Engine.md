# 11. Watchlist Engine

---

## Overview

The Watchlist Engine is the first intelligent decision-making component of the Institutional Swing Trading Platform.

After the Market Universe has been finalized, the Watchlist Engine determines **which stocks deserve continuous monitoring**.

It is important to understand that the Watchlist Engine does **not** generate trading signals.

Instead, it continuously answers a single question:

> **"Among all eligible stocks, which ones currently deserve our attention?"**

This distinction is extremely important.

A stock appearing in the watchlist does **not** imply that it should be bought.

It simply means that the stock has successfully passed the first stage of quality filtering and now qualifies for continuous observation by the downstream engines.

The Watchlist Engine significantly reduces computational complexity by allowing the expensive analytical engines to focus only on high-quality candidates rather than the complete market universe.

---

# Objectives

The Watchlist Engine has five primary objectives.

1. Identify strong long-term trending stocks.

2. Eliminate structurally weak stocks.

3. Reduce the number of continuously monitored securities.

4. Ensure every monitored stock satisfies minimum quality standards.

5. Produce a clean candidate list for the Trend Engine.

---

# Philosophy

The Watchlist Engine follows a simple philosophy.

```
Market Universe

↓

Reject Weak Stocks

↓

Keep Strong Stocks

↓

Monitor Continuously

↓

Wait Patiently

↓

Trade Only If Setup Appears
```

Notice that the Watchlist Engine never attempts to predict future movement.

It simply prepares the platform for future opportunities.

---

# Why a Watchlist Exists

Without a Watchlist Engine, every downstream module would need to analyze every stock every day.

Example

```
Nifty 200

↓

Trend Engine

↓

Consolidation Engine

↓

Liquidity Engine

↓

Risk Engine

↓

Portfolio Engine
```

Although technically possible, this is inefficient.

Instead,

the platform performs two stages of filtering.

Stage 1

Monthly Structural Filtering

↓

Stage 2

Daily Opportunity Detection

This dramatically reduces unnecessary computation.

---

# Watchlist Lifecycle

Every stock inside the watchlist passes through a lifecycle.

```
Market Universe

↓

Eligibility Check

↓

Watchlist Candidate

↓

Continuous Monitoring

↓

Trade Opportunity

↓

Trade Executed

↓

Remain in Watchlist

OR

↓

Removed During Refresh
```

A stock is **not removed after a trade**.

If the structural trend remains valid,

the stock continues to remain inside the watchlist.

---

# Watchlist Refresh Strategy

The Watchlist is refreshed using two independent processes.

## Monthly Structural Refresh

Purpose

Rebuild the watchlist using long-term structural conditions.

The engine performs:

- Universe Scan
- Trend Validation
- Ranking
- Candidate Selection
- Watchlist Generation

This creates a fresh watchlist for the upcoming month.

---

## Daily Validation

Daily validation does **not** rebuild the watchlist.

Instead,

it checks whether existing watchlist members remain structurally valid.

Examples

- Price still above 200 EMA?
- Data available?
- Trading suspended?
- Delisted?
- Corporate Action?

If a stock temporarily violates a condition,

it becomes **Inactive**

rather than immediately disappearing.

This preserves historical continuity.

---

# Watchlist Selection Rules

Version 1 uses deterministic rules.

Every stock must satisfy every mandatory rule.

---

## Rule 1

Stock must belong to the Market Universe.

---

## Rule 2

Stock must have sufficient historical data.

---

## Rule 3

Closing Price must remain above the 200 EMA for at least

**8 consecutive daily candles.**

Important:

The engine checks

Daily Close.

Not

Intraday High.

Not

Intraday Low.

Not

Candle Wick.

Only confirmed daily closing prices.

---

## Rule 4

200 EMA should demonstrate a positive slope.

A completely flat or declining long-term trend should not qualify.

The exact slope calculation will be defined in the Trend Engine.

---

## Rule 5

Minimum liquidity requirements must remain satisfied.

---

## Rule 6

Trading must remain active.

Suspended stocks cannot enter the watchlist.

---

## Rule 7

Historical data must pass integrity validation.

Missing candles,

incorrect adjustments,

or corrupted datasets automatically reject the stock.

---

# Why 8 Consecutive Closes?

This rule deserves explanation because it is one of the foundational assumptions of the platform.

A single close above the 200 EMA provides weak evidence.

Two or three closes may simply represent temporary strength.

Requiring multiple consecutive closes demonstrates that the stock has maintained strength over multiple trading sessions.

The objective is not finding the earliest trend.

The objective is filtering for stable trends.

The value "8" is currently treated as the initial research hypothesis.

Future research may determine that another threshold produces superior statistical expectancy.

Until validated,

the value remains configurable.

---

# Watchlist Size

The platform intentionally limits the size of the active watchlist.

Monitoring too many securities reduces focus.

Monitoring too few may reduce opportunities.

Version 1 target

```
Minimum

5 Stocks

Preferred

5–10 Stocks

Maximum

15 Stocks
```

If more than fifteen stocks satisfy all requirements,

the Ranking Engine determines which candidates remain active.

---

# Ranking Engine

The Watchlist Engine contains an internal ranking component.

Its purpose is **not** to generate buy signals.

Instead,

it prioritizes which stocks deserve the highest monitoring priority.

Example ranking factors

- Trend Strength
- Relative Strength
- Liquidity
- Average Volume
- Trend Stability
- Historical Volatility
- Data Quality

Future versions may include additional factors.

The exact scoring model is intentionally separated from the watchlist selection rules.

---

# Continuous Monitoring

Once a stock enters the watchlist,

it is analyzed every trading session.

The Watchlist Engine continuously updates:

- Latest Close
- EMA
- Trend Status
- Ranking Score
- Liquidity Status
- Data Integrity
- Eligibility Status

The engine itself does **not** search for liquidity grabs.

That responsibility belongs to the Consolidation and Liquidity Grab Engines.

---

# Watchlist Status

Every watchlist stock should maintain one of the following states.

## Active

Eligible for downstream analysis.

---

## Monitoring

Currently being analyzed for setup formation.

---

## Trade Candidate

Passed structural validation.

Awaiting downstream confirmation.

---

## Inactive

Temporarily failed eligibility validation.

May return automatically.

---

## Removed

No longer satisfies long-term structural requirements.

Excluded during refresh.

---

# Watchlist History

Historical watchlists should never be deleted.

Maintaining historical snapshots enables:

- Backtesting
- Research
- Strategy Evaluation
- Auditability
- Performance Attribution

Example

```
June Watchlist

↓

July Watchlist

↓

August Watchlist

↓

September Watchlist
```

Researchers can later evaluate whether specific watchlist compositions consistently outperform others.

---

# Data Flow

```
Market Universe

↓

Universe Validation

↓

Trend Qualification

↓

Liquidity Qualification

↓

Ranking

↓

Watchlist Generation

↓

Continuous Monitoring

↓

Trend Engine

↓

Consolidation Engine
```

The Watchlist Engine acts as the bridge between structural market filtering and opportunity detection.

---

# Failure Handling

Examples

### Missing Historical Data

Reject stock.

---

### Insufficient Consecutive Closes

Reject stock.

---

### 200 EMA Declining

Reject stock.

---

### Trading Suspended

Deactivate immediately.

---

### Corporate Action Pending Adjustment

Temporarily pause analysis until historical data has been adjusted.

---

### Watchlist Refresh Failure

Retain previous validated watchlist until refresh succeeds.

The platform should never operate with an incomplete watchlist.

---

# Configuration

The following parameters should remain configurable.

- Consecutive Close Requirement
- Maximum Watchlist Size
- Minimum Watchlist Size
- Refresh Schedule
- EMA Period
- Minimum Historical Candles
- Liquidity Threshold
- Ranking Formula Version

Every configuration change must be version-controlled.

---

# Database Design

## Table

### watchlists

Purpose

Stores every generated watchlist.

Columns

- id
- generated_at
- strategy_version
- market_status
- notes

---

### watchlist_items

Purpose

Stores every stock belonging to a watchlist.

Columns

- id
- watchlist_id
- symbol
- ranking_score
- watchlist_status
- added_at
- removed_at

---

### watchlist_metrics

Purpose

Stores calculated structural metrics.

Columns

- id
- symbol
- ema200
- ema200_slope
- consecutive_closes
- liquidity_score
- trend_score
- relative_strength
- updated_at

---

### watchlist_history

Purpose

Maintains historical additions and removals.

Columns

- id
- symbol
- action
- timestamp
- reason

---

# API Requirements

## GET /watchlists

Returns all historical watchlists.

---

## GET /watchlists/current

Returns the active watchlist.

---

## POST /watchlists/refresh

Triggers manual refresh.

---

## GET /watchlists/{symbol}

Returns watchlist history for a stock.

---

## GET /watchlists/rankings

Returns ranking information.

---

# System Design

```
Market Universe
        │
        ▼
Eligibility Validator
        │
        ▼
Trend Qualification
        │
        ▼
Liquidity Qualification
        │
        ▼
Ranking Engine
        │
        ▼
Watchlist Database
        │
        ▼
Continuous Monitor
        │
        ▼
Trend Engine
```

The Watchlist Engine is intentionally lightweight.

Its purpose is **candidate selection**, not **trade generation**.

This separation of responsibilities keeps the architecture modular and allows downstream engines to specialize in increasingly sophisticated analysis.

---

# Future Enhancements

Future versions may introduce:

- Dynamic watchlist sizing based on market regime.
- Sector-balanced watchlists.
- AI-assisted ranking.
- Relative strength percentile ranking.
- Institutional ownership filters.
- Fundamental quality filters.
- Multi-timeframe structural validation.
- Adaptive refresh frequency.

These enhancements should improve candidate quality without changing the core responsibility of the Watchlist Engine.

---

## Open Questions

1. Is 8 consecutive closes above the 200 EMA the optimal structural filter, or does another threshold improve long-term expectancy?

2. Should the watchlist size remain fixed, or should it adapt to changing market conditions?

3. Which ranking factors contribute most to downstream trading performance?

4. Should inactive stocks remain visible in the dashboard for research purposes?

5. What historical watchlist metrics should be retained to maximize future research and strategy evolution?