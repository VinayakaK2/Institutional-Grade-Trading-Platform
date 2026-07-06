# 14. Liquidity Grab Engine

---

# Overview

The Liquidity Grab Engine is the core intelligence of the Institutional Swing Trading Platform.

Every engine discussed previously exists for one purpose:

To prepare the market until this engine becomes active.

The Market Universe Engine identifies high-quality stocks.

↓

The Watchlist Engine continuously monitors them.

↓

The Trend Engine validates long-term direction.

↓

The Consolidation Engine identifies equilibrium.

↓

Only then does the Liquidity Grab Engine begin its work.

This engine determines whether the market has produced the specific behavior upon which the entire trading philosophy is built.

Unlike conventional trading systems that buy immediately after breakouts, this platform intentionally waits for a temporary breakdown below support followed by objective confirmation that the breakdown has failed.

The engine never assumes institutional activity.

Instead, it detects a measurable sequence of price and volume behavior that is consistent with the liquidity-grab hypothesis.

---

# Objective

The Liquidity Grab Engine answers one question.

> **"Has the stock produced a statistically valid false breakdown that satisfies every predefined confirmation rule?"**

If the answer is:

No

↓

Continue Monitoring.

If the answer is:

Yes

↓

Create a Liquidity Grab Object.

↓

Notify the Entry Engine.

---

# Core Philosophy

The strategy is based upon one important assumption.

Retail traders generally place stop-losses below obvious support levels.

When price temporarily breaks support, many stop-loss orders are executed.

This creates temporary liquidity.

Sometimes,

price immediately recovers back inside the previous consolidation.

The platform does not claim to know why this happens.

It simply detects this objectively measurable market behavior.

Therefore,

the engine does **not** detect institutions.

It detects a price sequence that resembles a false breakdown followed by strong recovery.

---

# Position Inside Trading Pipeline

```
Market Universe

↓

Watchlist

↓

Trend

↓

Consolidation

↓

Liquidity Grab

↓

Entry Validation

↓

Risk Engine

↓

Execution
```

Without Liquidity Grab,

there is never an entry.

---

# Liquidity Grab Lifecycle

```
Confirmed Trend

↓

Valid Consolidation

↓

Support Break

↓

Stop Loss Sweep

↓

Recovery Starts

↓

Recovery Completes

↓

Volume Confirmation

↓

Liquidity Grab Confirmed

↓

Entry Engine Activated
```

Every stage must occur in this order.

---

# Phase 1 — Support Break Detection

The first responsibility is detecting when price closes below the previously validated consolidation support.

Important:

The support level is obtained directly from the Consolidation Engine.

The Liquidity Grab Engine never recalculates support.

Once price closes below support,

the engine enters monitoring mode.

No trade occurs.

---

# Phase 2 — Breakdown Validation

Not every support break is meaningful.

The engine evaluates:

- Breakdown Depth
- Breakdown Strength
- Price Structure
- Candle Characteristics

The purpose is distinguishing:

Normal Trend Failure

from

Possible Liquidity Grab.

---

# Phase 3 — Recovery Monitoring

This is one of the defining characteristics of the strategy.

After support breaks,

the platform waits.

Recovery is not required to occur immediately.

The platform continuously monitors subsequent completed daily candles.

Possible outcomes

```
Support Break

↓

1 Candle Recovery
```

or

```
Support Break

↓

2 Candle Recovery
```

or

```
Support Break

↓

5 Candle Recovery
```

or

```
Support Break

↓

7 Candle Recovery
```

Recovery duration should remain configurable.

The important requirement is that price eventually returns inside the original consolidation.

---

# Recovery Philosophy

Many retail systems assume:

Support Break

↓

Bearish.

Our platform intentionally waits for evidence that the bearish move has failed.

Only after failure of the breakdown do we begin evaluating long opportunities.

---

# Phase 4 — Re-Entry Into Consolidation

Recovery alone is insufficient.

Price must return back inside the original consolidation boundaries.

Example

```
Resistance

──────────────

Consolidation

──────────────

Support

──────────────

False Breakdown

↓

Recovery

↓

Back Inside Box

↓

Continue Analysis
```

If recovery fails,

the setup is rejected.

---

# Phase 5 — Volume Confirmation

This stage provides objective confirmation.

The recovery should occur with significantly higher participation than normal consolidation activity.

The platform calculates:

Recovery Volume

/

Average Consolidation Volume

Example

Average Volume

1 Million

Recovery Volume

3.8 Million

Volume Ratio

3.8

Current research hypothesis

Approximately

3x–4x

average volume.

Exact thresholds remain configurable until validated through historical testing.

---

# Phase 6 — Recovery Candle Analysis

The recovery candle should demonstrate strong buying pressure.

Possible characteristics include:

- Strong bullish body.
- Close near candle high.
- Small lower rejection after recovery.
- Strong momentum.

This engine evaluates objective candle statistics.

It does not rely upon subjective candlestick names.

Example

Instead of

"Looks bullish"

the engine evaluates measurable candle properties.

---

# Phase 7 — Trend Revalidation

The breakdown should not invalidate the larger trend.

The engine therefore verifies:

- Trend still active.
- 200 EMA intact.
- Trend Score acceptable.

If the larger trend has already failed,

the liquidity grab hypothesis is rejected.

---

# Phase 8 — Liquidity Grab Validation

If every stage succeeds,

the engine creates a validated Liquidity Grab Object.

This object becomes the official input to the Entry Engine.

The Liquidity Grab Engine itself never places trades.

---

# Liquidity Grab Object

Example

```
Status

Confirmed

Support

₹845

Lowest Wick

₹832

Recovery Candle

2026-08-18

Recovery Duration

4 Days

Volume Ratio

3.7

Recovery Strength

91

Trend Status

Confirmed

Quality Score

94

Eligible

Yes
```

This standardized object prevents downstream engines from repeating calculations.

---

# Liquidity Grab Quality Score

Every liquidity grab receives a quality score.

Possible contributors include:

- Breakdown Quality
- Recovery Speed
- Recovery Strength
- Volume Ratio
- Trend Quality
- Consolidation Quality
- Market Strength
- Relative Strength

The score helps rank opportunities.

It does not approve trades.

---

# Immediate Rejection Conditions

The engine immediately rejects the setup if:

- Trend fails.
- Recovery never occurs.
- Recovery remains below support.
- Volume confirmation absent.
- Consolidation becomes invalid.
- Data integrity failure.
- Corporate action pending adjustment.

Rejected setups should still be stored for future research.

---

# Continuous Monitoring

Once a stock enters Liquidity Grab monitoring,

every completed daily candle updates the evaluation.

Possible states

```
Waiting

↓

Breakdown Detected

↓

Monitoring Recovery

↓

Recovery Confirmed

↓

Volume Confirmed

↓

Validated
```

or

```
Waiting

↓

Breakdown

↓

Continued Decline

↓

Rejected
```

---

# Data Flow

```
Consolidation Engine

↓

Support Boundary

↓

Breakdown Detector

↓

Recovery Monitor

↓

Volume Analyzer

↓

Trend Revalidation

↓

Quality Scoring

↓

Liquidity Grab Database

↓

Entry Engine
```

---

# Future Enhancements

Future versions may include:

- Multi-stage liquidity grab classification.
- Relative volume normalization by sector.
- AI-assisted recovery quality analysis.
- Wyckoff Spring classification.
- Volume Profile integration.
- Institutional footprint probability estimation.
- Adaptive recovery windows based on volatility.
- Machine learning quality ranking.

These enhancements should improve detection accuracy without changing the deterministic role of the Liquidity Grab Engine.

---

## Open Questions

1. What maximum recovery window produces the highest long-term expectancy?

2. Is a fixed volume ratio superior to a volatility-adjusted volume model?

3. How should multiple consecutive false breakdowns inside the same consolidation be handled?

4. What mathematical definition of recovery strength best predicts successful follow-through?

5. Should recovery quality be weighted more heavily than breakdown depth during quality scoring?