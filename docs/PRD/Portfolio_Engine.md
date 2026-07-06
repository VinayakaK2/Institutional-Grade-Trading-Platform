# 18. Portfolio Engine

---

# Overview

The Portfolio Engine is responsible for managing the trading account as a **single portfolio** rather than a collection of independent trades.

This distinction is critical.

Most retail traders evaluate trades individually.

The Institutional Swing Trading Platform evaluates every new trade relative to the entire portfolio.

A trade that appears excellent in isolation may significantly increase overall portfolio risk because of:

- Sector concentration
- Correlation
- Excessive capital allocation
- High portfolio heat
- Reduced liquidity

Therefore, before any approved trade reaches the Order Execution Engine, the Portfolio Engine performs portfolio-level validation.

The Portfolio Engine is the final capital allocation authority of the platform.

---

# Objective

The Portfolio Engine answers one question.

> **"Does adding this trade improve the portfolio without violating portfolio-level risk constraints?"**

Possible outcomes are:

```
Approve Position
```

```
Reduce Allocation
```

```
Delay Entry
```

```
Reject Trade
```

The engine protects the portfolio,

not individual trades.

---

# Core Philosophy

The platform does not own stocks.

The platform owns **risk**.

Every new position consumes a portion of the portfolio's available risk budget.

Therefore,

the Portfolio Engine manages:

- Capital
- Risk
- Diversification
- Exposure

instead of merely counting positions.

---

# Portfolio Hierarchy

```
Capital

↓

Available Cash

↓

Available Risk

↓

Sector Allocation

↓

Correlation

↓

Individual Position

↓

Trade Execution
```

Every level must remain healthy.

---

# Portfolio Structure

The portfolio consists of three primary components.

```
Cash

+

Open Positions

+

Reserved Capital
```

Every rupee inside the account belongs to exactly one category.

The Portfolio Engine continuously tracks all three.

---

# Principle 1 — Capital Preservation

The Portfolio Engine never attempts to maximize capital deployment.

Remaining in cash is considered a valid portfolio decision.

Example

```
Available Capital

₹10,00,000

Suitable Trades

None

↓

Cash Allocation

100%
```

No trade is preferable to a poor-quality trade.

---

# Principle 2 — Portfolio Heat

Portfolio Heat represents the total active risk currently present inside the portfolio.

Example

```
Position A

1%

Position B

1%

Position C

1%

Portfolio Heat

3%
```

Before approving a new trade,

the engine verifies:

```
Current Portfolio Heat

+

New Trade Risk

≤

Maximum Portfolio Heat
```

If exceeded,

the trade is rejected.

---

# Principle 3 — Position Limits

The platform limits the number of simultaneously active positions.

Purpose:

- Improve monitoring.
- Reduce complexity.
- Prevent over-diversification.
- Preserve capital.

Version 1 configuration example

```
Minimum

0

Preferred

5–8

Maximum

10 Active Positions
```

Future values remain configurable.

---

# Principle 4 — Capital Allocation

Every position receives mathematically calculated capital.

The Portfolio Engine verifies:

- Available Cash
- Reserved Margin (if future versions support it)
- Pending Orders
- Existing Exposure

Capital should never exceed available cash.

The platform never borrows capital.

---

# Principle 5 — Sector Diversification

Sector concentration increases portfolio risk.

Example

```
HDFC Bank

ICICI Bank

Axis Bank

Kotak Bank

SBI
```

Although these are different companies,

they largely represent the same economic exposure.

The Portfolio Engine therefore limits:

Maximum Capital

per Sector

Maximum Active Trades

per Sector

Future thresholds remain configurable.

---

# Principle 6 — Correlation Control

Diversification based solely on sector classification is insufficient.

Example

```
TCS

Infosys

Wipro
```

These companies may move similarly despite different fundamentals.

The Portfolio Engine estimates position correlation before approving additional trades.

Highly correlated positions increase effective portfolio risk.

---

# Principle 7 — Cash Management

Cash represents optionality.

Maintaining available cash enables participation in future opportunities.

The platform should therefore avoid exhausting all available capital.

Example

```
Portfolio Value

₹10,00,000

Capital Invested

₹6,50,000

Cash

₹3,50,000
```

Holding cash is not considered inefficiency.

It is considered strategic flexibility.

---

# Principle 8 — Dynamic Portfolio State

The portfolio continuously evolves.

Examples

```
Trade Opens

↓

Capital Decreases

↓

Portfolio Heat Changes

↓

Sector Allocation Changes

↓

Available Cash Changes

↓

Future Decisions Change
```

Every new trade recalculates the complete portfolio state.

---

# Portfolio States

The Portfolio Engine maintains several portfolio-level states.

```
Empty

↓

Building

↓

Balanced

↓

Fully Allocated

↓

High Risk

↓

Restricted
```

Each state influences future trade approvals.

---

# Position Lifecycle

Every position progresses through the following stages.

```
Approved

↓

Pending Order

↓

Open

↓

Partially Closed

↓

Trailing

↓

Closed

↓

Archived
```

The Portfolio Engine continuously updates the portfolio after every transition.

---

# Portfolio Approval Pipeline

```
Receive Approved Trade

↓

Cash Validation

↓

Portfolio Heat Validation

↓

Sector Exposure Validation

↓

Correlation Validation

↓

Maximum Position Check

↓

Allocation Validation

↓

Portfolio Approved

OR

Portfolio Rejected
```

Every stage acts as an independent portfolio safety check.

---

# Portfolio Object

Example

```
Portfolio Value

₹10,00,000

Cash

₹3,80,000

Invested

₹6,20,000

Open Positions

6

Portfolio Heat

4%

Largest Position

14%

Largest Sector

Banking

Cash Available

Yes

Eligible

Yes
```

The Portfolio Object becomes the official portfolio state consumed by downstream systems.

---

# Rebalancing Philosophy

Version 1 intentionally avoids automatic portfolio rebalancing.

Reasons:

- Swing positions naturally expire.
- Frequent rebalancing increases transaction costs.
- The strategy is event-driven rather than allocation-driven.

Future versions may introduce:

- Volatility-weighted portfolios.
- Risk parity.
- Kelly optimization.
- Adaptive capital allocation.

---

# Daily Portfolio Evaluation

Every completed trading session updates:

- Portfolio Value
- Cash Balance
- Unrealized Profit
- Realized Profit
- Active Risk
- Sector Distribution
- Correlation Matrix
- Exposure
- Performance Statistics

The portfolio therefore remains synchronized with every trading decision.

---

# Performance Metrics

The Portfolio Engine continuously calculates:

- Total Return
- Annualized Return
- Unrealized P&L
- Realized P&L
- Portfolio Heat
- Maximum Drawdown
- Sharpe Ratio
- Sortino Ratio
- Exposure
- Cash Utilization

These metrics are forwarded to the Analytics Engine.

---

# Failure Handling

Examples

### Insufficient Cash

Reject trade.

---

### Portfolio Heat Exceeded

Reject trade.

---

### Maximum Positions Reached

Reject or queue trade.

---

### Correlation Too High

Reject trade.

---

### Sector Exposure Exceeded

Reject trade.

---

### Broker Position Mismatch

Pause new approvals until reconciliation completes.

---

# Configuration

The following parameters remain configurable.

- Maximum Portfolio Heat
- Maximum Open Positions
- Maximum Sector Allocation
- Maximum Single Position Allocation
- Minimum Cash Reserve
- Correlation Threshold
- Portfolio Valuation Frequency
- Portfolio Version

Every configuration change should be version-controlled.

---

# Engineering Decisions

The Portfolio Engine intentionally remains independent from:

- Market Analysis
- Trend Detection
- Liquidity Grab Detection
- Entry Logic
- Exit Logic
- Order Execution

Its sole responsibility is protecting portfolio integrity while optimizing capital allocation.

The engine evaluates every trade within the context of the complete portfolio rather than as an isolated opportunity.

This separation allows portfolio management rules to evolve independently of trading strategy logic.

---

## Open Questions

1. What maximum portfolio heat provides the best balance between capital utilization and drawdown?

2. What is the optimal maximum number of simultaneous positions?

3. Which correlation methodology produces the most reliable portfolio diversification?

4. Should sector exposure limits remain fixed or adapt according to market regime?

5. How much cash should always remain available for future opportunities?

6. Should future versions support dynamic capital allocation based on strategy confidence?

7. Under which market conditions should the Portfolio Engine intentionally increase cash allocation instead of opening new positions?