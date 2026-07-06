# 12. Trend Engine

---

## Overview

The Trend Engine is the first analytical engine of the Institutional Swing Trading Platform.

After the Watchlist Engine identifies structurally strong stocks, the Trend Engine determines whether those stocks are currently in a healthy long-term trend that is suitable for our strategy.

This engine is intentionally conservative.

Its objective is **not** to identify every trend.

Its objective is to eliminate weak trends before they consume computational resources inside the more expensive analytical engines.

The Trend Engine answers one question:

> **"Is this stock trending strongly enough for us to even consider searching for a liquidity-grab setup?"**

If the answer is **No**, every downstream engine immediately stops processing that stock.

---

# Objective

The Trend Engine exists to:

- Confirm long-term bullish structure.
- Reject weak or deteriorating trends.
- Remove sideways markets.
- Remove early-stage uncertain trends.
- Provide objective trend measurements.
- Generate standardized trend scores.

The output of this engine is consumed directly by:

- Consolidation Engine
- Liquidity Grab Engine
- Portfolio Engine
- Analytics Engine

---

# Core Philosophy

Trend is considered the market's long-term direction.

The platform intentionally trades **with** the dominant trend.

It never attempts to predict trend reversals.

Instead, it waits until a trend has already become established.

The philosophy is simple.

```
No Trend

↓

No Trade
```

This rule never changes.

---

# Why Trade Only With The Trend?

Every trading strategy has a statistical edge.

Our edge does not come from predicting reversals.

Our edge comes from waiting for:

Established Trend

+

Liquidity Grab

+

Recovery

Therefore,

the trend is not merely another indicator.

It is the environment within which the entire strategy operates.

Without trend,

our strategy hypothesis no longer exists.

---

# Trend Validation Pipeline

Every stock entering the Trend Engine follows the same workflow.

```
Watchlist Stock

↓

Historical Data Validation

↓

EMA Calculation

↓

Trend Strength Calculation

↓

Structure Validation

↓

Relative Strength Validation

↓

Trend Score Calculation

↓

Approved

OR

Rejected
```

Every stage must pass.

Failure at any stage immediately rejects the stock.

---

# Trend Definition

For Version 1,

a stock is considered to be in a valid long-term uptrend only when every mandatory rule is satisfied.

No individual rule alone is sufficient.

Trend is treated as a combination of independent confirmations.

---

# Mandatory Rule 1

## Price Above 200 EMA

The stock must remain above its 200 EMA.

The 200 EMA represents long-term institutional trend direction.

Our strategy assumes that institutional accumulation is more likely to continue when the dominant trend remains positive.

Price trading below the 200 EMA automatically invalidates the setup.

---

# Mandatory Rule 2

## Consecutive Daily Closes

The closing price must remain above the 200 EMA for at least:

```
8 Consecutive Daily Candles
```

Important:

The engine evaluates:

Daily Closing Price

Only.

Not:

- Intraday High
- Intraday Low
- Candle Wick

Daily closing prices represent confirmed market consensus.

---

# Mandatory Rule 3

## Positive EMA Slope

A stock may trade above the 200 EMA while the EMA itself remains flat or declining.

Such situations generally indicate weakening trend quality.

Therefore,

the platform evaluates the slope of the 200 EMA.

```
Positive Slope

↓

Trend Healthy

Flat

↓

Trend Weakening

Negative

↓

Trend Rejected
```

The exact mathematical slope calculation will be defined later inside the Mathematical Specification.

---

# Mandatory Rule 4

## Medium-Term Trend Alignment

The 50 EMA should remain above the 200 EMA.

Purpose:

Confirm that medium-term momentum aligns with the long-term trend.

This reduces situations where price temporarily trades above the 200 EMA despite an overall deteriorating structure.

---

# Mandatory Rule 5

## Price Structure

Price should demonstrate healthy market structure.

Characteristics include:

- Higher Highs
- Higher Lows

The objective is not to detect perfect textbook trends.

Instead,

the engine should verify that the market structure generally supports institutional accumulation.

---

# Mandatory Rule 6

## Relative Strength

A stock should outperform the broader market.

Example:

If Nifty gains:

5%

while a stock gains:

1%

the stock demonstrates relative weakness.

The platform prefers stocks showing leadership.

Relative strength improves the probability of participating in stronger trends.

---

# Mandatory Rule 7

## Liquidity Validation

Trend alone is insufficient.

The stock must continue satisfying liquidity requirements defined by the Market Universe.

A strong trend inside an illiquid stock remains unacceptable.

---

# Trend Score

Passing every mandatory rule determines eligibility.

Beyond that,

the Trend Engine calculates a Trend Score.

Purpose:

Rank the quality of different trends.

Higher scores indicate healthier long-term structure.

Possible contributing factors include:

- EMA Distance
- EMA Slope
- Relative Strength
- Structure Quality
- Trend Stability
- Volatility Stability

Trend Score **does not approve trades.**

It only provides additional information.

---

# Trend Stability

Strong trends generally exhibit stability.

Characteristics include:

- Controlled pullbacks.
- Healthy retracements.
- Respect for moving averages.
- Limited abnormal volatility.

Extremely unstable trends receive lower quality scores.

---

# Trend Strength vs Momentum

Trend and momentum are not identical.

Example:

A stock may rise:

20%

in two days.

Momentum is strong.

However,

if this move occurs below the 200 EMA,

our platform still rejects it.

Conversely,

a stock slowly climbing above the 200 EMA for several months may demonstrate:

Moderate Momentum

Strong Trend

The platform prioritizes trend quality over short-term momentum.

---

# Trend Lifecycle

Every stock progresses through defined trend states.

```
No Trend

↓

Emerging Trend

↓

Confirmed Trend

↓

Strong Trend

↓

Weakening Trend

↓

Trend Failure
```

Version 1 primarily trades:

Confirmed Trend

and

Strong Trend

Future versions may classify these states more precisely.

---

# Daily Trend Evaluation

Trend evaluation occurs once every completed trading session.

The platform intentionally avoids intraday trend changes.

Reason:

Daily closing prices reduce noise.

Trend status remains constant throughout the next trading session unless new daily data becomes available.

---

# Trend Invalidations

The Trend Engine immediately rejects stocks under the following conditions.

## Condition 1

Close below 200 EMA.

---

## Condition 2

Insufficient consecutive closes.

---

## Condition 3

Negative EMA slope.

---

## Condition 4

Weak market structure.

---

## Condition 5

Relative weakness.

---

## Condition 6

Liquidity deterioration.

---

# Trend Recovery

If a rejected stock later satisfies every mandatory rule again,

the Trend Engine automatically restores eligibility.

No manual intervention is required.

The platform continuously adapts to changing market conditions.

---

# Data Flow

```
Watchlist Engine

↓

Historical Market Data

↓

EMA Calculator

↓

Trend Validator

↓

Structure Validator

↓

Relative Strength Calculator

↓

Trend Score Calculator

↓

Trend Database

↓

Consolidation Engine
```

The Trend Engine produces standardized outputs consumed by every downstream analytical engine.

---

# Output

Each evaluated stock should produce a structured Trend Object.

Example:

```
Trend Status

Confirmed

Trend Score

87

EMA 200

Above

EMA Slope

Positive

EMA 50

Above EMA 200

Structure

Healthy

Relative Strength

Strong

Eligible

Yes
```

This object becomes the primary input for the Consolidation Engine.

---

# Database Design

## Table

### trend_analysis

Purpose

Stores daily trend evaluation.

Columns

- id
- symbol
- analysis_date
- trend_status
- trend_score
- ema_50
- ema_200
- ema_slope
- consecutive_closes
- relative_strength
- structure_status
- liquidity_status
- created_at

---

### trend_history

Purpose

Stores historical trend transitions.

Columns

- id
- symbol
- previous_status
- current_status
- changed_at
- reason

---

# API Requirements

## GET /trend/{symbol}

Returns latest trend analysis.

---

## GET /trend/history/{symbol}

Returns historical trend transitions.

---

## POST /trend/recalculate

Triggers trend recalculation.

---

## GET /trend/eligible

Returns all currently trend-qualified stocks.

---

# System Design

```
Watchlist Engine
        │
        ▼
EMA Calculator
        │
        ▼
Trend Validator
        │
        ▼
Structure Validator
        │
        ▼
Relative Strength Engine
        │
        ▼
Trend Score Calculator
        │
        ▼
Trend Database
        │
        ▼
Consolidation Engine
```

The Trend Engine should remain completely independent from:

- Entry Logic
- Risk Management
- Portfolio Decisions
- Order Execution

Its only responsibility is determining whether the structural trend is healthy enough for further analysis.

---

# Future Enhancements

Future versions may introduce:

- Multi-timeframe trend validation.
- Sector-relative trend scoring.
- Adaptive EMA periods.
- Market regime-aware trend thresholds.
- Institutional ownership trends.
- Trend persistence probability.
- Machine learning-assisted trend ranking.

These enhancements should improve trend quality without changing the deterministic responsibilities of the Trend Engine.

---

## Open Questions

1. Is the combination of 50 EMA and 200 EMA sufficient, or do additional structural filters improve long-term expectancy?

2. What is the optimal mathematical definition of EMA slope for this strategy?

3. Which relative strength calculation provides the most robust results across different market regimes?

4. Should trend quality decay gradually or immediately after mandatory rule violations?

5. Which trend characteristics contribute most strongly to successful liquidity-grab trades during historical backtesting?