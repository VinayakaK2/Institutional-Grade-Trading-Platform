# 16. Risk Engine

---

# Overview

The Risk Engine is the most important protection mechanism of the Institutional Swing Trading Platform.

Every engine before this point attempts to identify high-quality trading opportunities.

The Risk Engine has a fundamentally different responsibility.

Its responsibility is **not to maximize profit.**

Its responsibility is to ensure that **no single trade can cause unacceptable damage to the trading account.**

The platform follows a permanent hierarchy:

```
Capital Preservation

↓

Risk Management

↓

Opportunity Selection

↓

Profit Generation
```

Notice that profit appears last.

This ordering is intentional and never changes.

Even if a trade has a perfect Liquidity Grab Score, excellent volume confirmation, and a strong trend, it will still be rejected if the associated risk exceeds acceptable limits.

The Risk Engine therefore acts as the final protection layer before capital is exposed.

---

# Objective

The Risk Engine answers one question.

> **"Is the risk associated with this trade acceptable according to the platform's predefined capital preservation rules?"**

If the answer is:

No

↓

Reject Trade.

If the answer is:

Yes

↓

Calculate Position Size.

↓

Forward trade to the Portfolio Engine.

---

# Core Philosophy

The platform never asks:

> "How much money can we make?"

Instead, it asks:

> "How much money can we safely lose if this trade fails?"

This single question governs every risk calculation performed by the engine.

Losses are inevitable.

Large losses are optional.

The Risk Engine exists to prevent the latter.

---

# Risk Hierarchy

Risk is evaluated across multiple levels.

```
Account Risk

↓

Portfolio Risk

↓

Sector Risk

↓

Trade Risk

↓

Execution Risk
```

A trade must satisfy every level before approval.

---

# Principle 1 — Fixed Risk Per Trade

Every trade carries a predefined maximum acceptable loss.

Version 1 Philosophy:

```
Maximum Risk

=

1%

Preferred Maximum

=

2%

of Total Trading Capital
```

Example

```
Trading Capital

₹10,00,000

Maximum Risk

1%

=

₹10,000
```

Regardless of:

- Stock Price
- Position Size
- Confidence Score
- Trend Quality

The maximum loss remains fixed.

This prevents emotional position sizing.

---

# Principle 2 — Risk Is Measured In Currency

The platform never thinks in terms of:

- Shares
- Lots
- Percentage Move

Instead,

risk is measured in absolute currency.

Example

Wrong Thinking

```
Buy

500 Shares
```

Correct Thinking

```
Maximum Loss

₹5,000
```

Quantity is merely the consequence of acceptable risk.

---

# Principle 3 — Stop Loss Before Entry

No trade exists until a stop-loss exists.

Before a trade can be approved,

the platform must know:

- Entry Price
- Stop Loss
- Risk Per Share
- Total Risk

Without these values,

the trade is automatically rejected.

---

# Stop Loss Philosophy

The platform intentionally avoids placing stop-losses at obvious support levels.

Reason:

Many market participants place stop-losses immediately below visible support.

Instead,

the stop-loss is placed below the **lowest wick of the validated Liquidity Grab candle**, with an additional volatility buffer.

This provides breathing room while remaining mathematically defined.

---

# Stop Loss Calculation

The stop-loss is calculated as:

```
Stop Loss

=

Lowest Wick

−

ATR Buffer
```

Where

```
ATR Buffer

=

1 × ATR
```

This formula remains configurable.

Future research may determine more effective volatility buffers.

---

# Risk Per Share

Once the stop-loss has been determined,

the engine calculates:

```
Risk Per Share

=

Entry Price

−

Stop Loss
```

Example

```
Entry

₹860

Stop

₹845

Risk

₹15 per share
```

This value becomes the foundation for position sizing.

---

# Position Size Formula

The platform follows strict risk-based position sizing.

Formula

```
Position Size

=

Maximum Risk Amount

/

Risk Per Share
```

Example

```
Trading Capital

₹10,00,000

Risk

1%

₹10,000

Entry

₹860

Stop

₹845

Risk Per Share

₹15

Quantity

=

10,000

/

15

=

666 Shares
```

The Position Sizing Engine receives this calculation directly.

No manual adjustments should occur.

---

# Minimum Risk-Reward Validation

Every trade must satisfy the platform's minimum Risk-to-Reward requirement.

Current hypothesis:

```
Minimum RR

2 : 1
```

Meaning

Expected Reward

must be at least twice the calculated risk.

Example

Risk

₹20

Minimum Target

₹40

If the required reward cannot reasonably be achieved,

the trade is rejected before execution.

---

# Portfolio Heat

Individual trades cannot be evaluated independently.

The engine continuously monitors:

```
Total Active Risk
```

Example

```
Trade A

1%

Trade B

1%

Trade C

1%

Portfolio Heat

3%
```

A configurable maximum portfolio heat protects the account from excessive simultaneous exposure.

---

# Sector Exposure

The platform should avoid concentrating excessive capital inside one sector.

Example

```
HDFC Bank

ICICI Bank

Axis Bank

Kotak Bank
```

Although these are different stocks,

their correlation is extremely high.

The Risk Engine therefore calculates:

Sector Exposure

before approving new positions.

Future thresholds remain configurable.

---

# Correlation Risk

Sector diversification alone is insufficient.

The platform should also estimate correlation between active positions.

Example

```
Stock A

Highly Correlated

Stock B
```

Opening both positions may unintentionally double portfolio risk.

The engine should reject opportunities that significantly increase correlated exposure.

---

# Gap Risk

Swing trading introduces overnight risk.

The platform recognizes that:

```
Stop Loss

is

not

Guaranteed Exit Price
```

Large overnight gaps may produce losses exceeding the planned amount.

The Risk Engine should therefore estimate:

- Historical Gap Frequency
- Average Gap Size
- Earnings Gap Risk
- Event Risk

This information contributes to overall trade quality.

---

# Earnings Risk

Major corporate announcements frequently produce abnormal volatility.

The platform should avoid initiating new positions immediately before:

- Quarterly Results
- Annual Results
- Major Corporate Announcements

A configurable earnings blackout period should prevent unnecessary exposure.

---

# Market Risk

Even a perfect stock setup should not be traded if the broader market becomes excessively risky.

The Risk Engine incorporates information from the Market Intelligence Engine.

Possible examples include:

- Extremely High Volatility
- Market Panic
- Index Breakdown
- Circuit Events

Market-level risk may override stock-level opportunity.

---

# Risk Approval Pipeline

```
Trade Candidate

↓

Stop Loss Calculation

↓

Risk Per Share

↓

Risk-Reward Validation

↓

Portfolio Heat Check

↓

Sector Exposure Check

↓

Correlation Check

↓

Gap Risk Check

↓

Market Risk Check

↓

Risk Approved

OR

Risk Rejected
```

Every stage acts as an independent safety checkpoint.

---

# Risk Object

If every validation succeeds,

the engine produces a standardized Risk Object.

Example

```
Status

Approved

Capital

₹10,00,000

Maximum Risk

₹10,000

Entry

₹860

Stop

₹845

Risk Per Share

₹15

Risk Reward

2.8

Portfolio Heat

3%

Sector Exposure

Acceptable

Correlation

Low

Eligible

Yes
```

This object becomes the official input for the Portfolio Engine.

---

# Trade Rejection Conditions

The Risk Engine immediately rejects trades under the following conditions.

- Risk exceeds configured limits.
- Stop-loss cannot be calculated.
- Risk-Reward below minimum threshold.
- Portfolio heat exceeded.
- Sector concentration exceeded.
- Correlation exceeds acceptable limits.
- Earnings blackout active.
- Market risk elevated.
- Insufficient available capital.

Every rejection should be recorded for research purposes.

---

# Continuous Risk Monitoring

Risk management does not end after entry.

The engine should continuously monitor:

- Current Portfolio Heat
- Open Position Risk
- Correlation Changes
- Sector Concentration
- Market Volatility
- Gap Risk
- Cash Availability

Changes in portfolio risk may influence future trade approvals.

Existing positions continue to be managed by the Position Management and Exit Engines.

---

# Engineering Decisions

The Risk Engine intentionally remains independent from:

- Trade Detection
- Pattern Recognition
- Broker APIs
- Order Placement
- Exit Logic

Its only responsibility is protecting capital through objective mathematical validation.

Separating risk management from execution simplifies testing, improves maintainability, and ensures that capital preservation rules cannot be bypassed by downstream systems.

---

## Open Questions

1. Should maximum risk per trade remain fixed (1–2%), or adapt based on market volatility?

2. What maximum portfolio heat provides the best balance between opportunity and drawdown?

3. How should overnight gap probability influence position sizing?

4. Should earnings blackout periods vary by company size or historical earnings volatility?

5. What correlation model best represents portfolio risk for swing trading?

6. Should ATR buffers remain fixed at 1× ATR, or adapt according to market regime?

7. Under which market conditions should the Risk Engine temporarily reject **all** new trades, regardless of individual setup quality?