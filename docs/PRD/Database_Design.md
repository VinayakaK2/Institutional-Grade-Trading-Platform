# 26. Database Design

---

# Overview

The Database is the single source of truth for the entire Institutional Swing Trading Platform.

Every trading decision, market event, portfolio update, strategy evaluation, AI observation, and historical record ultimately depends on the quality of the database design.

Unlike traditional CRUD applications where the database primarily stores user information, this platform continuously processes massive amounts of time-series market data, analytical results, portfolio information, and research datasets.

Therefore, the database must be designed for:

- High Performance
- High Reliability
- Horizontal Scalability
- Historical Auditability
- Version Control
- Research
- Analytics
- AI Training

The database should never merely store data.

It should preserve the complete history of every decision made by the platform.

---

# Database Philosophy

The platform follows five permanent database principles.

## Principle 1

Never lose historical information.

Every completed trade,

every rejected opportunity,

every indicator,

every AI prediction,

every strategy version,

must remain reproducible.

---

## Principle 2

Production data is immutable.

Historical trades should never change.

If corrections become necessary,

new versions should be created.

---

## Principle 3

Every important object has an audit trail.

Nothing should disappear.

Everything should be traceable.

---

## Principle 4

Normalize business entities.

Denormalize analytical datasets only where performance requires it.

---

## Principle 5

Operational databases and analytical databases should remain logically separated.

---

# Database Architecture

```
                   PostgreSQL

        ┌────────────────────────────┐
        │        Master DB           │
        └─────────────┬──────────────┘
                      │
      ┌───────────────┼────────────────┐
      ▼               ▼                ▼
 Operational      Analytics       AI Features
    Schema          Schema          Schema
```

Future versions may introduce:

- Read Replicas
- Data Warehouse
- OLAP Database
- Feature Store

---

# Database Schemas

The database should be divided into logical schemas.

```
auth

market

watchlist

strategy

risk

portfolio

execution

analytics

learning

ai

system

audit
```

Each schema owns one domain.

---

# AUTH SCHEMA

Stores user authentication and authorization.

---

## users

```
id (PK)

email

password_hash

full_name

role

status

timezone

created_at

updated_at
```

---

## sessions

```
id

user_id

refresh_token

device

ip_address

expires_at

created_at
```

---

## roles

```
id

role_name

permissions
```

---

# MARKET SCHEMA

Stores raw market information.

---

## symbols

```
id

symbol

exchange

company_name

sector_id

industry_id

listing_date

status
```

---

## daily_candles

```
id

symbol_id

date

open

high

low

close

volume

adjusted_close

created_at
```

Indexes

```
(symbol_id, date)
```

Partition

```
Yearly
```

---

## corporate_actions

```
id

symbol_id

action_type

ratio

effective_date

remarks
```

---

## sectors

```
id

sector_name
```

---

## industries

```
id

industry_name

sector_id
```

---

# WATCHLIST SCHEMA

---

## watchlists

```
id

generated_date

strategy_version

market_regime

created_at
```

---

## watchlist_items

```
id

watchlist_id

symbol_id

rank

status

added_at

removed_at
```

---

# STRATEGY SCHEMA

This schema stores every analytical engine output.

---

## trend_analysis

```
id

symbol_id

analysis_date

trend_score

ema50

ema200

ema_slope

relative_strength

status
```

---

## consolidations

```
id

symbol_id

support

resistance

duration

range_width

atr

quality_score
```

---

## liquidity_grabs

```
id

symbol_id

consolidation_id

support_price

lowest_wick

recovery_date

volume_ratio

quality_score

status
```

---

## trade_candidates

```
id

symbol_id

liquidity_grab_id

entry_price

status

created_at
```

---

# RISK SCHEMA

---

## risk_analysis

```
id

trade_candidate_id

capital

risk_amount

risk_percent

stop_loss

risk_reward

approved

created_at
```

---

## portfolio_heat

```
id

date

heat

sector_exposure

correlation_score
```

---

# PORTFOLIO SCHEMA

---

## portfolios

```
id

name

currency

capital

status
```

---

## positions

```
id

portfolio_id

symbol_id

entry_price

quantity

remaining_quantity

average_price

status

opened_at

closed_at
```

---

## position_history

```
id

position_id

event

price

quantity

timestamp
```

---

# EXECUTION SCHEMA

---

## orders

```
id

position_id

broker_order_id

order_type

side

price

quantity

status

placed_at

filled_at
```

---

## executions

```
id

order_id

fill_price

filled_quantity

slippage

broker_timestamp
```

---

# ANALYTICS SCHEMA

---

## daily_statistics

```
id

date

portfolio_value

cash

drawdown

heat

daily_return
```

---

## monthly_statistics

```
id

month

return

drawdown

profit_factor

win_rate
```

---

## yearly_statistics

```
id

year

cagr

max_drawdown

sharpe

sortino
```

---

# LEARNING SCHEMA

---

## completed_trades

```
id

position_id

entry_price

exit_price

holding_days

profit

exit_reason

strategy_version
```

---

## extracted_features

```
id

trade_id

feature_name

feature_value
```

---

## learning_reports

```
id

generated_at

title

summary

version
```

---

# AI SCHEMA

---

## datasets

```
id

version

created_at

samples

status
```

---

## models

```
id

model_name

version

accuracy

precision

recall

f1_score

created_at
```

---

## predictions

```
id

model_id

symbol_id

prediction

confidence

generated_at
```

---

# SYSTEM SCHEMA

---

## jobs

```
id

job_name

status

started_at

completed_at

duration
```

---

## notifications

```
id

user_id

title

priority

category

status

created_at
```

---

## configurations

```
id

key

value

version

updated_at
```

---

# AUDIT SCHEMA

Every critical change is stored here.

---

## audit_logs

```
id

user_id

entity

entity_id

action

old_value

new_value

timestamp

ip_address
```

---

# Entity Relationship Overview

```
Users
   │
   ▼
Portfolios
   │
   ▼
Positions
   │
   ▼
Orders
   │
   ▼
Executions

Symbols
   │
   ▼
Daily Candles
   │
   ▼
Trend Analysis
   │
   ▼
Consolidations
   │
   ▼
Liquidity Grabs
   │
   ▼
Trade Candidates
   │
   ▼
Risk Analysis
   │
   ▼
Positions
```

---

# Indexing Strategy

Every frequently queried column must be indexed.

Examples

```
symbol_id

date

status

created_at

strategy_version

portfolio_id

position_id

broker_order_id
```

Composite indexes should be used for:

```
(symbol_id, date)

(portfolio_id, status)

(strategy_version, created_at)
```

---

# Partitioning Strategy

Large tables should be partitioned.

Examples

```
daily_candles

↓

Yearly
```

```
orders

↓

Monthly
```

```
audit_logs

↓

Monthly
```

```
analytics

↓

Monthly
```

This prevents extremely large tables.

---

# Time-Series Strategy

Historical market data is append-only.

Rules

- Never Update
- Never Delete
- Append New Candles
- Archive Old Data

This significantly improves consistency.

---

# Versioning Strategy

Every important entity references:

```
Strategy Version

Configuration Version

Model Version

Dataset Version

Indicator Version
```

This guarantees reproducibility.

---

# Database Transactions

Critical operations should execute atomically.

Examples

Trade Execution

```
Create Order

↓

Create Execution

↓

Update Position

↓

Update Portfolio

↓

Commit
```

Failure anywhere

↓

Rollback Everything

---

# Backup Strategy

Daily

Incremental Backup

Weekly

Full Backup

Monthly

Archive Backup

Yearly

Cold Storage

Backups should be encrypted.

---

# Read / Write Separation

Future architecture

```
Primary DB

↓

Writes

Read Replicas

↓

Dashboard

Analytics

Reports
```

Improves scalability.

---

# Data Retention

Never delete:

- Trades
- Orders
- Positions
- Analytics
- Audit Logs
- Strategy Versions

Temporary cache data may expire.

---

# Database Security

- Row-Level Security
- Encryption At Rest
- TLS In Transit
- Role-Based Access
- Secret Management
- Audit Logging

Detailed security implementation is covered in Chapter 28.

---

# Engineering Decisions

The database is intentionally designed around **domain-driven schemas**, immutable historical records, append-only market data, comprehensive audit logging, and version-controlled analytical outputs.

This architecture ensures:

- Complete reproducibility
- High-performance historical research
- Efficient production execution
- AI-ready datasets
- Scalable long-term growth

while preserving the integrity of every trading decision ever made by the platform.

---

## Open Questions

1. Should historical market data remain entirely within PostgreSQL, or should older data be archived to a dedicated time-series database?

2. At what scale should read replicas become mandatory?

3. Which analytical tables should remain normalized, and which should be denormalized for performance?

4. Should AI feature storage evolve into a dedicated Feature Store as dataset size increases?

5. What partitioning strategy best balances query performance with operational simplicity?

6. Which database maintenance operations should execute automatically outside market hours?

7. How should long-term archival be managed while preserving complete reproducibility for historical backtesting?