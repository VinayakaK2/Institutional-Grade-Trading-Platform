# 17. Exit Engine

---

# Overview

The Exit Engine is responsible for managing every open position from the moment a trade is executed until the final share is sold.

The Entry Engine determines **whether** a trade deserves capital.

The Risk Engine determines **how much** capital can be risked.

The Exit Engine determines **how and when** capital leaves the market.

A profitable trading strategy is not determined solely by good entries.

Poor exit decisions can convert profitable trades into losses.

Conversely,

well-designed exit rules allow profitable trades to continue while systematically limiting downside risk.

The Exit Engine therefore treats every open position as a continuously evolving probability distribution rather than a static trade.

Every completed daily candle triggers a complete re-evaluation of the position.

---

# Objective

The Exit Engine answers one question.

> **"Should the platform continue holding this position, partially reduce exposure, or exit completely?"**

Possible outcomes are:

```
Continue Holding
```

```
Partial Exit
```

```
Move Stop Loss
```

```
Trail Stop
```

```
Complete Exit
```

The Exit Engine continuously evaluates every active position until no shares remain.

---

# Core Philosophy

The platform follows three permanent exit principles.

### Principle 1

Protect Capital First.

---

### Principle 2

Allow Profits To Grow.

---

### Principle 3

Never Exit Without A Defined Reason.

Every exit must be traceable to an objective rule.

The platform never exits because:

- Fear
- Hope
- Emotion
- Opinion

Every exit is deterministic.

---

# Exit Lifecycle

Every position follows a predefined lifecycle.

```
Trade Executed

↓

Initial Stop Loss Active

↓

Position Moves In Favor

↓

Target 1 Reached

↓

Partial Profit Booking

↓

Move Stop To Breakeven

↓

Trail Remaining Position

↓

Trend Continues

↓

Repeat Daily Evaluation

↓

Final Exit

↓

Trade Archived
```

---

# Exit Types

The platform supports five independent exit categories.

```
Protective Exit

↓

Profit Exit

↓

Trailing Exit

↓

Emergency Exit

↓

Forced Exit
```

Each category has independent rules.

---

# Protective Exit

Immediately after entry,

every position receives its initial stop-loss calculated by the Risk Engine.

If price reaches the stop-loss,

the platform exits the entire position.

No discretionary override exists.

The purpose of the protective stop is preserving capital,

not maximizing profit.

---

# Partial Profit Exit

The strategy intentionally avoids exiting the complete position at the first target.

Instead,

profits are gradually secured.

Current Version 1 philosophy:

```
Target 1 Reached

↓

Sell

50%

or

75%

↓

Retain Remaining Position
```

The exact percentage remains configurable.

The purpose is balancing:

- Profit Realization
- Trend Participation

---

# Determining Target 1

Target 1 should not be a fixed percentage.

Instead,

the platform identifies the nearest significant resistance generated from historical price structure.

Possible reference points include:

- Previous Swing High
- Historical Resistance
- Major Supply Zone

The target should always satisfy the minimum Risk-to-Reward requirement validated by the Risk Engine.

---

# Breakeven Transition

Immediately after partial profit booking,

the platform removes the possibility of converting the remaining position into a loss.

The stop-loss is moved to:

```
Entry Price
```

This creates a risk-free position.

Once breakeven has been activated,

the stop-loss must never move below the entry price again.

---

# Trailing Stop Philosophy

The remaining position attempts to capture long-term trend continuation.

Instead of using arbitrary percentages,

the platform follows market structure.

Current Version 1 methodology:

```
Higher Low

↓

New Higher Low

↓

Move Stop Below Previous Higher Low
```

This approach is referred to as the **Staircase Method**.

The objective is remaining invested while the market continues producing higher lows.

---

# Staircase Method

Example

```
Entry

↓

Higher Low 1

↓

Higher Low 2

↓

Higher Low 3

↓

Higher Low 4

↓

Trend Break

↓

Exit
```

The stop-loss moves only upward.

It never moves downward.

---

# Daily Position Evaluation

Every completed daily candle triggers a full position review.

The Exit Engine evaluates:

- Trend Status
- Current Stop Loss
- Latest Higher Low
- Volume
- ATR
- Market Regime
- Open Profit
- Remaining Risk

The evaluation occurs only after market close.

Intraday noise is intentionally ignored.

---

# Emergency Exit

Certain situations require immediate liquidation regardless of profit target.

Examples include:

- Extreme bearish reversal.
- Major abnormal volume.
- Structural trend failure.
- Catastrophic market event.
- Unexpected corporate announcement.

Version 1 specifically monitors the following hypothesis.

```
Large Upper Rejection

+

Abnormally High Volume

+

Resistance Area

↓

Possible Distribution
```

If validated,

the platform exits the remaining position immediately.

This rule is intentionally conservative and should be validated through historical testing.

---

# Trend Failure Exit

The platform continuously receives updates from the Trend Engine.

If the long-term trend becomes invalid,

the Exit Engine closes any remaining position regardless of unrealized profit.

The strategy never attempts to hold positions after structural trend failure.

---

# Time-Based Exit

Occasionally,

a trade may remain inactive for an extended period.

Future versions may define:

Maximum Holding Period.

If exceeded,

the platform may voluntarily exit the trade to improve capital efficiency.

Version 1 leaves this configurable.

---

# Forced Exit

Certain external events require immediate exit regardless of technical conditions.

Examples include:

- Stock Delisting
- Trading Suspension
- Broker Risk Controls
- Regulatory Restrictions
- Severe Market Disruptions

These events override every analytical rule.

---

# Exit Decision Pipeline

```
Position Open

↓

Protective Stop Check

↓

Target Evaluation

↓

Partial Exit Evaluation

↓

Breakeven Evaluation

↓

Trailing Stop Evaluation

↓

Emergency Exit Evaluation

↓

Trend Validation

↓

Forced Exit Validation

↓

Continue Holding

OR

Exit
```

---

# Exit Priority

When multiple exit conditions occur simultaneously,

the platform follows a predefined priority hierarchy.

```
Forced Exit

↓

Protective Stop

↓

Emergency Exit

↓

Trend Failure

↓

Partial Exit

↓

Trailing Stop

↓

Continue Holding
```

Higher-priority events always override lower-priority events.

---

# Exit Object

Every exit decision produces a standardized Exit Object.

Example

```
Trade Status

Open

Exit Type

Partial Exit

Shares Sold

50%

Remaining Shares

50%

Current Stop

₹860

Breakeven

Active

Trailing Stop

₹892

Trend

Confirmed

Reason

Target 1 Achieved

Next Evaluation

Next Trading Day
```

This object becomes the official state of the position.

---

# Trade Completion

Once the final share has been sold,

the platform records:

- Entry Price
- Exit Price
- Holding Duration
- Realized Profit
- Maximum Drawdown
- Maximum Favorable Excursion
- Exit Reason
- Strategy Version

The completed trade is forwarded to the Learning Engine.

---

# Failure Handling

Examples

### Market Gap Below Stop

Exit at the first available executable market price.

Record slippage.

---

### Partial Order Failure

Retry according to Execution Engine policy.

---

### Missing Daily Data

Pause non-critical evaluations until validated.

---

### Trading Halt

Maintain current state until exchange resumes trading.

---

### Corporate Action

Adjust position and historical references according to official exchange adjustments.

---

# Configuration

Configurable parameters include:

- Partial Exit Percentage
- Minimum Risk-Reward
- Breakeven Activation Rule
- Trailing Stop Method
- ATR Buffer
- Emergency Exit Thresholds
- Maximum Holding Period
- Daily Evaluation Time

Every completed trade must store the configuration version used during management.

---

# Engineering Decisions

The Exit Engine intentionally does **not**:

- Detect entries.
- Calculate position size.
- Evaluate watchlists.
- Detect liquidity grabs.
- Place broker orders directly.

Its responsibility is limited to deciding **how an already open position should evolve**.

Actual order placement remains the responsibility of the Order Execution Engine.

This strict separation improves reliability, simplifies testing, and allows exit strategies to evolve independently of trade detection logic.

---

## Open Questions

1. What percentage should be booked at Target 1 to maximize long-term expectancy: 50%, 60%, or 75%?

2. Does the Staircase Method outperform ATR-based trailing stops across different market regimes?

3. What objective definition best identifies a "Higher Low" for automated trailing?

4. Which emergency exit conditions consistently improve performance after backtesting?

5. Should maximum holding periods vary by volatility or market regime?

6. Under what conditions should breakeven activation be delayed instead of occurring immediately after partial profit booking?

7. Which combination of partial exits and trailing methodology produces the highest risk-adjusted returns over long historical datasets?