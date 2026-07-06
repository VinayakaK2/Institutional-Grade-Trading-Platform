# 10. Market Universe

---

## Overview

The Market Universe defines the complete collection of securities that the Institutional Swing Trading Platform is allowed to analyze.

This is one of the most important design decisions of the platform.

A trading strategy is only as good as the quality of the assets it trades.

Even a statistically profitable strategy can fail if applied to illiquid, manipulated, or structurally weak stocks.

Therefore, before discussing indicators, trend analysis, or entries, the platform must first define:

**"Which stocks are eligible for analysis?"**

This document establishes the rules governing the trading universe.

Every downstream module operates only on stocks approved by the Market Universe Engine.

---

# Objective

The objective of the Market Universe is not to maximize the number of tradable stocks.

The objective is to maximize the quality of the stocks entering the analysis pipeline.

The Market Universe Engine should eliminate securities that unnecessarily increase:

- Risk
- Volatility
- Manipulation
- Execution difficulty
- Slippage
- Poor liquidity

before any technical analysis begins.

This dramatically improves the quality of every subsequent trading decision.

---

# Core Philosophy

The platform intentionally follows the following philosophy:

```
Smaller Universe
        │
Higher Quality
        │
Better Decisions
        │
Lower Risk
        │
Higher Consistency
```

Adding more stocks does not necessarily improve performance.

More stocks simply increase:

- Computational cost
- Analysis complexity
- False positives
- Maintenance effort

The objective is not to analyze everything.

The objective is to analyze the right securities.

---

# Initial Trading Universe

Version 1 of the platform shall exclusively analyze:

**Nifty 200 Constituents**

Reasons:

- High liquidity
- Large institutional participation
- Reliable price discovery
- Lower operator manipulation
- Better execution quality
- Lower slippage
- Higher average trading volume
- Better historical data availability

The Market Universe Engine shall automatically maintain the latest Nifty 200 constituents.

Whenever the index composition changes, the platform should update the universe automatically.

---

# Why Not Every Listed Stock?

India has thousands of listed companies.

Analyzing every company introduces several problems.

Examples include:

## Low Liquidity

Many small-cap stocks trade with very low daily volume.

Consequences include:

- Large bid-ask spreads
- Poor fills
- High slippage
- Difficult exits

These characteristics significantly reduce strategy reliability.

---

## Operator Manipulation

Smaller stocks are generally more vulnerable to:

- Artificial price movements
- Pump-and-dump schemes
- Low-float manipulation
- Sudden abnormal volatility

The strategy is designed around institutional participation.

Operator-driven stocks contradict the philosophy of the platform.

---

## Inconsistent Data

Many smaller companies exhibit:

- Large gaps
- Thin trading
- Irregular volume
- Corporate action complexity

These characteristics reduce statistical reliability.

---

# Eligible Asset Types

Version 1 supports only:

- Cash Equity (CNC)
- NSE Listed Stocks
- Daily Timeframe

Everything else remains outside the production scope.

---

# Excluded Asset Types

The following asset classes shall not be analyzed by Version 1.

- Futures
- Options
- Commodities
- Currency
- ETFs
- Mutual Funds
- Bonds
- REITs
- International Stocks
- Penny Stocks
- SME Listings

These exclusions simplify the architecture while aligning with the platform's swing trading philosophy.

---

# Universe Selection Criteria

Every stock inside the Market Universe should satisfy structural quality requirements before entering the Watchlist Engine.

The platform should evaluate:

## Exchange

NSE Listed

---

## Market Segment

Cash Equity

---

## Listing Status

Active

---

## Tradability

Trading Not Suspended

---

## Historical Data Availability

Sufficient historical candles should exist for:

- EMA
- ATR
- Trend Analysis
- Volume Analysis

Newly listed companies lacking sufficient history should be excluded until adequate data becomes available.

---

# Liquidity Requirements

Liquidity is one of the most important characteristics of the trading universe.

Low liquidity increases:

- Slippage
- Execution Risk
- Stop Loss Risk
- Gap Risk

The Market Universe Engine should calculate:

- Average Daily Volume
- Average Daily Turnover
- Bid-Ask Spread (future versions)
- Delivery Percentage (future versions)

Only sufficiently liquid securities should proceed further.

The exact thresholds should remain configurable.

---

# Corporate Action Handling

Corporate actions should never invalidate historical analysis.

The platform should automatically handle:

- Stock Splits
- Bonus Issues
- Dividends
- Symbol Changes
- Mergers
- Demergers

Historical data should remain adjusted to ensure indicator consistency.

---

# Monthly Universe Refresh

The Market Universe should automatically refresh at predefined intervals.

Version 1:

Monthly Refresh

Workflow:

```
Download Latest Nifty 200

↓

Compare Existing Universe

↓

Remove Deleted Symbols

↓

Add New Symbols

↓

Download Historical Data

↓

Initialize Indicators

↓

Store Metadata

↓

Notify Watchlist Engine
```

The refresh process should be completely automatic.

---

# Daily Universe Validation

Although the universe refreshes monthly,

basic validation should occur every trading day.

Daily checks include:

- Symbol Availability
- Trading Suspension
- Data Availability
- Market Data Integrity

Failures should prevent affected symbols from entering downstream analysis.

---

# Universe Metadata

Every stock should maintain metadata including:

- Symbol
- Company Name
- Sector
- Industry
- Exchange
- Index Membership
- Listing Date
- Market Capitalization
- Average Volume
- Data Availability
- Current Status

This information should remain centralized.

---

# Data Flow

The Market Universe Engine sits at the beginning of the complete decision pipeline.

```
Exchange Data

↓

Index Constituents

↓

Corporate Action Processing

↓

Data Validation

↓

Liquidity Validation

↓

Universe Database

↓

Market Scanner

↓

Watchlist Engine
```

No downstream engine should independently decide which stocks belong to the universe.

The Market Universe Engine acts as the single source of truth.

---

# Failure Handling

If the Market Universe Engine encounters failures,

it should behave predictably.

Examples:

### Missing Market Data

Affected stock skipped.

---

### Trading Suspension

Automatically excluded.

---

### Newly Added Stock

Historical data downloaded before eligibility.

---

### Symbol Delisted

Removed from universe.

Historical records retained for research.

---

### Corrupted Historical Data

Stock marked invalid.

Scanner should ignore until repaired.

---

# Configuration

The following parameters should remain configurable.

- Universe Source
- Refresh Frequency
- Minimum Historical Candles
- Minimum Average Volume
- Minimum Turnover
- Supported Exchanges
- Supported Asset Classes

Configuration changes should require version control and audit logging.

---

# Database Design

## Tables

### market_universe

Purpose:

Stores every eligible security.

Columns:

- id
- symbol
- exchange
- company_name
- sector_id
- industry_id
- listing_date
- current_status
- universe_source
- created_at
- updated_at

---

### market_universe_history

Purpose:

Tracks additions and removals.

Columns:

- id
- symbol
- action
- effective_date
- reason
- previous_status
- new_status

---

### corporate_actions

Purpose:

Stores historical corporate actions.

Columns:

- id
- symbol
- action_type
- action_date
- adjustment_factor
- remarks

---

# API Requirements

## GET /market-universe

Returns current universe.

---

## POST /market-universe/refresh

Triggers universe refresh.

---

## GET /market-universe/history

Returns historical membership changes.

---

## GET /market-universe/{symbol}

Returns metadata for a specific security.

---

# System Design

```
Market Data Provider
          │
          ▼
Universe Updater
          │
          ▼
Corporate Action Processor
          │
          ▼
Universe Validator
          │
          ▼
Universe Database
          │
          ▼
Market Scanner
          │
          ▼
Watchlist Engine
```

The Market Universe Engine is the first operational component of the trading platform.

Every subsequent module depends on the quality of this engine.

For this reason, correctness is significantly more important than execution speed.

---

# Future Enhancements

Future versions may support:

- Nifty 500
- Sensex
- ETFs
- Global Markets
- US Equities
- Sector Rotation Universes
- Dynamic Liquidity-Based Universes
- Custom User Universes
- Multi-Exchange Support

These additions should integrate without modifying downstream engines.

Only the Market Universe Engine should change.

---

## Open Questions

1. Should Version 1 remain restricted to Nifty 200, or should Nifty 500 be supported after sufficient backtesting?

2. What minimum liquidity threshold provides the best balance between opportunity and execution quality?

3. Should average turnover be considered more reliable than average volume for universe selection?

4. How should temporarily suspended stocks be reintroduced into the universe?

5. What validation process should run before monthly universe updates become active in production?