# 4. Non Goals

---

## Overview

Clearly defining what the platform **will not do** is as important as defining what it will do.

One of the biggest reasons software projects become overly complex, delayed, and difficult to maintain is uncontrolled scope expansion (Scope Creep).

Without clearly defined non-goals, new ideas continuously get added during development, eventually transforming the project into something completely different from its original vision.

This section establishes the permanent boundaries of Version 1 (v1.0) of the Institutional Swing Trading Platform.

Any functionality listed here is intentionally excluded unless a future version explicitly introduces it after proper research, validation, and engineering review.

---

# Product Scope Boundary

The objective of this platform is to build a highly specialized quantitative swing trading platform.

It is **not** intended to become a universal trading application supporting every possible trading style.

The platform is optimized for one strategy executed exceptionally well rather than many strategies executed poorly.

---

# Non Goal 1 — Intraday Trading

The platform will not support intraday trading.

Reasons include:

- High market noise.
- Extremely short decision windows.
- Higher emotional pressure.
- Increased brokerage and transaction costs.
- Higher false breakout frequency.
- Significantly different strategy requirements.

Intraday trading requires a completely different architecture, including:

- Tick data processing
- Low latency execution
- Order book analytics
- Real-time streaming infrastructure
- Millisecond execution optimization

These requirements are intentionally outside the scope of this project.

---

# Non Goal 2 — Scalping

The platform will not perform scalping.

Scalping focuses on capturing very small price movements over seconds or minutes.

Supporting scalping would require:

- Ultra-low latency systems
- High-frequency market feeds
- Tick-by-tick data
- Order book prediction
- Co-located infrastructure

These engineering requirements conflict with the objectives of a swing trading platform.

---

# Non Goal 3 — Futures Trading

Version 1 will not trade futures contracts.

Reasons:

- Leverage introduces additional risk.
- Margin requirements differ significantly.
- Expiry management increases complexity.
- Overnight margin calculations become necessary.
- Risk models require redesign.

The platform is intentionally designed around cash equity swing trading.

---

# Non Goal 4 — Options Trading

The platform will not support options.

Options require independent analytical systems including:

- Implied Volatility
- Greeks
- Time Decay
- Volatility Surface Analysis
- Expiry Selection
- Strike Selection

These concepts are unrelated to the current strategy.

Future versions may introduce options as a completely independent strategy module.

---

# Non Goal 5 — Margin Trading

The platform will never intentionally use leverage or margin financing.

Trades shall only use available cash capital.

Reasons:

- Interest costs reduce profitability.
- Margin calls increase portfolio risk.
- Leverage magnifies losses.
- Capital preservation becomes more difficult.

The project philosophy explicitly prioritizes long-term survival over aggressive capital growth.

---

# Non Goal 6 — Predicting Market Direction

The platform does not attempt to predict the future.

It does not forecast:

- Tomorrow's market movement.
- Next week's trend.
- Future resistance.
- Future support.

Instead, it reacts to objective evidence already present in market data.

The platform behaves as a confirmation-based system rather than a prediction engine.

---

# Non Goal 7 — Buying Every Breakout

This platform is intentionally **not** a breakout trading system.

Example:

Resistance breaks.

Price rallies.

No liquidity grab occurs.

Decision:

No Trade.

The platform only participates after predefined confirmation criteria have been satisfied.

Missing opportunities is considered acceptable.

---

# Non Goal 8 — Maximum Trade Frequency

Trade frequency is not a performance metric.

The system is never optimized to produce:

- Daily trades
- Weekly trades
- Monthly trade targets

Some months may produce:

0 trades.

Other months may produce:

8 trades.

The only requirement is that every trade satisfies all predefined validation rules.

---

# Non Goal 9 — High Win Rate

The objective is not achieving the highest possible win rate.

A strategy with:

90% win rate

can still lose money.

A strategy with:

45% win rate

may generate superior long-term returns if:

- Risk management is disciplined.
- Average reward exceeds average risk.
- Drawdowns remain controlled.

The platform therefore optimizes expectancy rather than win percentage.

---

# Non Goal 10 — AI Controlled Trading

Artificial Intelligence will never receive unrestricted authority to execute trades.

AI responsibilities include:

- Pattern recognition
- Trade explanation
- Historical analysis
- Confidence estimation
- Ranking opportunities

Trade execution remains controlled by deterministic rule engines.

This prevents hallucinated decisions and improves reproducibility.

---

# Non Goal 11 — Black Box Decisions

Every decision produced by the platform must be explainable.

The platform will never generate responses such as:

- Buy because AI recommends it.
- Strong stock detected.
- High confidence trade.

Instead, every recommendation must include measurable evidence supporting the decision.

Explainability is a mandatory engineering requirement.

---

# Non Goal 12 — Manual Decision Dependency

The platform should not require continuous human interpretation.

The objective is to minimize subjective judgment.

Human involvement should primarily consist of:

- Monitoring.
- Reviewing analytics.
- Updating configuration.
- Validating strategy improvements.

Routine trading decisions should remain automated.

---

# Non Goal 13 — Indicator Collection

The platform is not intended to become an indicator library.

Only indicators that directly improve decision quality will be implemented.

Indicators without measurable contribution should be excluded regardless of popularity.

Every indicator must satisfy a clearly defined responsibility within the decision pipeline.

---

# Non Goal 14 — Overfitting Historical Data

Historical performance alone does not validate a strategy.

The platform will never optimize solely to maximize historical profitability.

Every optimization must also satisfy:

- Walk-forward validation.
- Out-of-sample testing.
- Paper trading validation.
- Live consistency.

This reduces the probability of building strategies that fail under future market conditions.

---

# Non Goal 15 — Frequent Strategy Changes

The production strategy should remain stable.

Individual losing trades should never trigger immediate strategy modifications.

Changes should only occur after statistically significant evidence demonstrates improvement.

Strategy evolution should be research-driven rather than emotion-driven.

---

# Non Goal 16 — Becoming a General Stock Screener

Although the platform scans the market, its purpose is not to become another generic stock screener.

Traditional screeners answer questions such as:

- Which stocks gained today?
- Which stocks have high volume?
- Which stocks crossed an EMA?

This platform answers a different question:

"Which stocks currently satisfy every requirement of our quantitative swing trading framework?"

The scanner exists solely to support the strategy.

---

# Non Goal 17 — Supporting Every Broker

Version 1 should integrate with a limited number of carefully selected broker APIs.

Supporting dozens of brokers from the beginning increases engineering complexity without improving trading performance.

Broker integrations should expand only after the core platform has reached production stability.

---

# Non Goal 18 — Real-Time Millisecond Processing

The platform is designed around end-of-day swing trading.

It does not require:

- Microsecond execution.
- High-frequency networking.
- Tick-by-tick optimization.
- Order book prediction.
- Ultra-low latency infrastructure.

Engineering effort should instead focus on analysis quality, reliability, and risk management.

---

# Non Goal 19 — Replacing Quantitative Research

The platform assists quantitative research.

It does not replace it.

Every new hypothesis must still undergo:

- Research
- Statistical validation
- Historical testing
- Walk-forward testing
- Paper trading

before becoming part of the production strategy.

---

# Non Goal 20 — Guaranteeing Profit

No trading system can guarantee profits.

Financial markets are probabilistic.

The objective of this platform is not certainty.

The objective is improving probability while controlling downside risk.

The platform seeks positive long-term expectancy rather than guaranteed outcomes.

Any strategy modifications should continue respecting this principle.

---

## Engineering Implications

The non-goals defined in this document directly influence future engineering decisions.

Examples include:

- No tick-data database is required.
- No high-frequency execution engine is required.
- No options pricing engine is required.
- No derivatives risk engine is required.
- No leverage management module is required.
- No discretionary decision interface is required.

These exclusions significantly simplify the architecture and allow engineering effort to focus on the core strengths of the platform.

---

## Open Questions

1. Which future capabilities provide enough strategic value to justify expanding beyond the current scope?

2. Under what conditions should options or futures become separate strategy modules rather than extensions of the existing platform?

3. Which additional features can be introduced without violating the core philosophy of simplicity, explainability, and capital preservation?

4. At what stage should multi-market support (international exchanges, ETFs, commodities) be considered?

5. How should future versions balance feature expansion against long-term maintainability and architectural simplicity?