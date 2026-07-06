# DATABASE_DESIGN.md

# Institutional Swing Trading Platform

**Version:** 1.0

---

# Overview

The Database is the foundation of the Institutional Swing Trading Platform.

Every trading decision, analytical result, AI prediction, market event, portfolio update, and audit trail ultimately depends on the database.

Unlike traditional CRUD applications, this platform primarily operates on **time-series financial data** combined with **transactional business data**.

Therefore, the database must satisfy five major objectives:

- High Read Performance
- High Write Reliability
- Historical Reproducibility
- AI-Ready Data
- Horizontal Scalability

The database is intentionally designed around business domains instead of application modules.

Each domain owns its own tables while remaining connected through clearly defined relationships.

---

# Database Philosophy

The database follows the following principles.

### Single Source of Truth

Every important business object exists only once.

Duplicate business data should never exist.

---

### Immutable History

Completed trades,

historical candles,

orders,

executions,

analytics,

AI datasets,

must never be modified.

Instead,

new records or versions are created.

---

### Normalize Business Data

Business entities remain normalized.

Analytics may use denormalized materialized views for performance.

---

### Version Everything

Every important record references

- Strategy Version
- Model Version
- Dataset Version
- Configuration Version

This guarantees reproducibility.

---

### Audit Everything

Every important modification generates an audit record.

Nothing important disappears.

---

# Database Architecture

```
                    PostgreSQL

                         │

──────────────────────────────────────────

       auth

       market

       strategy

       portfolio

       execution

       analytics

       learning

       ai

       notification

       system

       audit

──────────────────────────────────────────

                         │

                     Redis Cache

──────────────────────────────────────────

                         │

                Object Storage

          Reports

          AI Models

          Backups

          Historical Exports
```

---

# Core Business Domains

The database is divided into independent domains.

```
Authentication

↓

Market

↓

Strategy

↓

Trading

↓

Portfolio

↓

Execution

↓

Learning

↓

Analytics

↓

AI

↓

Notifications

↓

Audit
```

Every domain owns its own entities.

---

# Entity Relationship

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

────────────────────────

Symbols

│

▼

Daily Candles

│

▼

Trend Analysis

│

▼

Consolidation

│

▼

Liquidity Grab

│

▼

Trade Candidate

│

▼

Risk Analysis

│

▼

Position

────────────────────────

Completed Trades

│

▼

Learning

│

▼

Analytics

│

▼

AI Dataset
```

---

# Primary Tables

The production database primarily consists of the following business entities.

Authentication

- Users
- Sessions
- Roles

Market

- Symbols
- Daily Candles
- Corporate Actions
- Sectors
- Industries

Strategy

- Watchlists
- Trend Analysis
- Consolidations
- Liquidity Grabs
- Trade Candidates
- Risk Analysis

Portfolio

- Portfolios
- Positions
- Position History

Execution

- Orders
- Executions

Learning

- Completed Trades
- Features
- Reports

Analytics

- Daily Statistics
- Monthly Statistics
- Yearly Statistics

AI

- Datasets
- Models
- Predictions

System

- Jobs
- Configurations
- Notifications

Audit

- Audit Logs

---

# Relationship Rules

Examples

One User

↓

Many Portfolios

One Portfolio

↓

Many Positions

One Position

↓

Many Orders

One Order

↓

Many Executions

One Symbol

↓

Many Candles

One Candle

↓

One Trend Analysis

One Trend

↓

One Consolidation

One Consolidation

↓

Many Liquidity Grabs

One Liquidity Grab

↓

One Trade Candidate

One Trade

↓

One Risk Analysis

The database follows strict foreign-key relationships.

---

# Indexing Strategy

Every high-frequency query should be indexed.

Examples

```
symbol

date

status

strategy_version

portfolio_id

order_id

user_id
```

Composite indexes

```
(symbol,date)

(symbol,strategy_version)

(portfolio,status)

(order,status)

(strategy_version,created_at)
```

Indexes should optimize production queries rather than every possible query.

---

# Partition Strategy

Large tables should be partitioned.

Examples

Daily Candles

↓

Yearly

Orders

↓

Monthly

Executions

↓

Monthly

Audit Logs

↓

Monthly

Analytics

↓

Monthly

Historical partitions simplify maintenance.

---

# Time-Series Strategy

Market data is append-only.

Rules

Never Update

Never Delete

Append New Candles

Archive Old Partitions

Historical integrity remains preserved.

---

# Read / Write Pattern

Production

```
Write

↓

Primary Database
```

Analytics

```
Read

↓

Read Replica
```

Dashboard

```
Read

↓

Redis

↓

Replica

↓

Primary
```

Writes always occur through the primary database.

---

# Caching Strategy

Redis stores

- Active Watchlist
- Portfolio Summary
- Dashboard Widgets
- Trend Objects
- User Sessions
- Market Status

Historical records never remain permanently cached.

---

# Transactions

Financial operations execute atomically.

Example

```
Create Order

↓

Create Execution

↓

Update Position

↓

Update Portfolio

↓

Create Audit Log

↓

Commit
```

If any step fails

↓

Rollback Entire Transaction

Financial consistency always takes priority.

---

# Query Optimization

Preferred

- Indexed Queries
- Prepared Statements
- Pagination
- Batch Reads
- Bulk Inserts

Avoid

- Full Table Scans
- N+1 Queries
- Large Joins During Live Trading

Complex analytical queries should execute separately from production.

---

# Materialized Views

Frequently generated reports should use materialized views.

Examples

- Monthly Performance
- Portfolio Summary
- Trade Statistics
- Sector Performance
- Strategy Performance

Views refresh asynchronously.

---

# Data Retention

Never Delete

- Trades
- Orders
- Executions
- Positions
- Audit Logs
- Strategy Versions
- AI Models

Temporary cache data may expire automatically.

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

Every backup should be encrypted and periodically restored in a test environment.

---

# Migration Strategy

Every schema change should use versioned migrations.

```
Migration

↓

Validation

↓

Deployment

↓

Verification

↓

Rollback (if required)
```

Manual schema changes are prohibited.

---

# Database Security

Security measures include

- Row-Level Security
- TLS Encryption
- Encrypted Backups
- Role-Based Permissions
- Parameterized Queries
- Secret Management
- Audit Logging

Application services should never use administrator database credentials.

---

# Performance Targets

| Operation | Target |
|------------|---------|
| Simple Read | <20 ms |
| Indexed Query | <50 ms |
| Insert | <20 ms |
| Batch Insert | <200 ms |
| Transaction | <100 ms |
| Dashboard Query | <100 ms |
| Analytics Query | Background |

Performance targets should be monitored continuously.

---

# Database Maintenance

Scheduled jobs

Daily

- Vacuum
- Analyze
- Backup Validation

Weekly

- Index Health
- Statistics Refresh

Monthly

- Archive Old Partitions
- Storage Optimization

Maintenance should execute outside market hours.

---

# Future Scalability

Future database evolution may include

- Read Replicas
- Multi-Region Replication
- Time-Series Database
- Data Warehouse
- Feature Store
- Distributed Object Storage

The logical schema should remain unchanged as infrastructure scales.

---

# Engineering Decisions

The database is intentionally designed around business domains, immutable historical records, version-controlled analytical data, and append-only market history.

Operational workloads, analytical workloads, and AI workloads remain logically separated while sharing a common source of truth.

This architecture provides deterministic reproducibility, efficient production execution, simplified auditing, scalable historical research, and a solid foundation for future expansion into multiple strategies, brokers, markets, and AI capabilities without requiring fundamental database redesign.