# 25. System Architecture

---

# Overview

The System Architecture defines how every component of the Institutional Swing Trading Platform communicates, scales, and operates together as a single production-grade system.

Unlike traditional trading applications where analysis, execution, and storage are tightly coupled, this platform follows a **modular, event-driven, service-oriented architecture**.

Every engine has one clearly defined responsibility.

Every service communicates through well-defined interfaces.

No engine directly depends upon the internal implementation of another engine.

This architecture ensures:

- High Maintainability
- Scalability
- Reliability
- Testability
- Explainability

The system is designed so that individual engines can evolve independently without affecting the remainder of the platform.

---

# Architectural Philosophy

The platform follows five architectural principles.

## Principle 1

Single Responsibility

Every engine performs exactly one responsibility.

Example

Trend Engine

↓

Trend Analysis

Only.

It does not calculate risk.

It does not place orders.

It does not manage portfolios.

---

## Principle 2

Loose Coupling

Engines communicate through standardized objects rather than direct implementation dependencies.

Example

Instead of:

```
Trend Engine

↓

calls

↓

Risk Engine
```

The architecture follows:

```
Trend Engine

↓

Trend Object

↓

Message/Event

↓

Risk Engine
```

Each engine understands the object,

not the implementation.

---

## Principle 3

Deterministic Core

Production trading decisions remain deterministic.

AI never bypasses deterministic rules.

Research remains isolated from production execution.

---

## Principle 4

Event-Driven Workflow

Every important platform activity generates an event.

Example

```
Watchlist Updated

↓

Trend Analysis Started

↓

Trend Confirmed

↓

Consolidation Created

↓

Liquidity Grab Confirmed

↓

Trade Approved

↓

Risk Approved

↓

Position Opened
```

Events become the backbone of platform communication.

---

## Principle 5

Horizontal Scalability

Every service should scale independently.

Examples

Trend Engine

↓

Multiple Workers

Liquidity Grab Engine

↓

Multiple Workers

Backtesting

↓

Distributed Workers

AI Training

↓

Separate Compute Cluster

---

# High-Level Architecture

```
                    +----------------------+
                    |   Web Dashboard      |
                    +----------+-----------+
                               |
                               |
                    REST / WebSocket API
                               |
                               ▼
                    +----------------------+
                    |      API Gateway     |
                    +----------+-----------+
                               |
      ---------------------------------------------------------
      |            |             |             |               |
      ▼            ▼             ▼             ▼               ▼
+------------+ +------------+ +------------+ +------------+ +------------+
| Auth       | | Trading    | | Portfolio  | | Analytics  | | AI Service |
| Service    | | Service    | | Service    | | Service    | |            |
+------------+ +------------+ +------------+ +------------+ +------------+
                     |
                     ▼
           Strategy Orchestrator
                     |
      --------------------------------------------------------
      |        |         |        |        |        |         |
      ▼        ▼         ▼        ▼        ▼        ▼         ▼
 Universe  Watchlist  Trend  Consolidation Liquidity Entry  Risk
 Engine    Engine     Engine Engine        Grab      Engine Engine
                                             Engine
                     |
                     ▼
              Portfolio Engine
                     |
                     ▼
               Execution Engine
                     |
                     ▼
                Broker Adapter
                     |
                     ▼
              Stock Broker APIs
```

---

# Layered Architecture

The platform follows a layered architecture.

```
Presentation Layer

↓

API Layer

↓

Application Layer

↓

Strategy Layer

↓

Execution Layer

↓

Infrastructure Layer

↓

Data Layer
```

Each layer communicates only with adjacent layers.

---

# Presentation Layer

Responsible for:

- Dashboard
- Portfolio View
- Analytics
- Reports
- Notifications
- Trade History

Technologies

Example

- React
- Next.js
- TailwindCSS
- TradingView Charts

No business logic exists here.

---

# API Layer

Responsible for:

- Authentication
- Authorization
- REST APIs
- WebSockets
- Rate Limiting
- Validation

Acts as the public interface.

---

# Application Layer

Contains:

- User Management
- Notification Engine
- Portfolio Management
- Analytics
- Configuration
- Reporting

Coordinates business workflows.

---

# Strategy Layer

This layer contains every trading engine.

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

Entry

↓

Risk

↓

Portfolio

↓

Execution
```

Each engine remains independent.

---

# Execution Layer

Responsible for:

- Order Creation
- Order Validation
- Broker Communication
- Retry Logic
- Order Tracking
- Position Synchronization

This layer never performs technical analysis.

---

# Infrastructure Layer

Responsible for:

- Background Jobs
- Scheduling
- Queues
- Logging
- Monitoring
- Caching
- Secrets
- Configuration

The infrastructure layer supports the application.

---

# Data Layer

Responsible for persistent storage.

Contains

- PostgreSQL
- Redis
- Object Storage
- Historical Data

Every engine reads and writes through standardized repositories.

---

# Complete System Workflow

```
Market Opens

↓

Market Data Download

↓

Historical Data Update

↓

Market Universe Validation

↓

Watchlist Refresh

↓

Trend Analysis

↓

Consolidation Analysis

↓

Liquidity Grab Detection

↓

Entry Validation

↓

Risk Validation

↓

Portfolio Validation

↓

Order Generation

↓

Broker Execution

↓

Position Monitoring

↓

Exit Management

↓

Trade Completion

↓

Learning Engine

↓

Analytics

↓

Dashboard Update
```

---

# Internal Communication

The platform should primarily use asynchronous communication.

Examples

```
Trend Completed

↓

Publish Event

↓

Consolidation Engine Consumes
```

Advantages

- Loose coupling
- Better scalability
- Independent deployments
- Easier retries
- Better fault isolation

---

# Service Boundaries

Every major service owns its own responsibility.

Example

Authentication Service

Owns

- Users
- Sessions
- Roles

Portfolio Service

Owns

- Positions
- Capital
- Exposure

Analytics Service

Owns

- Reports
- KPIs
- Statistics

No service directly modifies another service's database.

---

# Scheduler

A Scheduler coordinates periodic tasks.

Examples

Daily

- Download Market Data
- Update Indicators
- Refresh Analytics

Monthly

- Refresh Market Universe
- Generate New Watchlist

Weekly

- Generate Reports

Yearly

- Archive Historical Data

The scheduler should support retries and monitoring.

---

# Caching Strategy

Redis (or equivalent) should cache frequently accessed information.

Examples

- Active Watchlist
- Trend Objects
- Current Portfolio
- Dashboard Summary
- Market Status

Historical data should remain inside the primary database.

---

# Logging Architecture

Every service should generate structured logs.

Example

```
Timestamp

Service

Request ID

User ID

Trade ID

Strategy Version

Event

Duration

Status
```

Logs should support debugging and auditing.

---

# Monitoring

The platform should continuously monitor:

Infrastructure

- CPU
- Memory
- Disk
- Network

Application

- API Latency
- Queue Length
- Error Rate

Trading

- Orders
- Portfolio
- Broker Connectivity

Monitoring should remain independent from trading logic.

---

# Fault Tolerance

The architecture should tolerate failures.

Examples

Market Data Failure

↓

Retry

↓

Fallback Provider

↓

Alert

Broker Failure

↓

Retry

↓

Reconnect

↓

Alert

Database Failure

↓

Read Replica

↓

Recovery

↓

Maintenance Mode

Failures should remain isolated.

---

# Security Architecture

Security operates across every layer.

Examples

- JWT Authentication
- Role-Based Access Control
- API Rate Limiting
- Input Validation
- Secrets Management
- Encryption
- Audit Logging

Detailed implementation is described in Chapter 28.

---

# Deployment Architecture

Production deployment consists of multiple independent services.

```
Load Balancer

↓

API Gateway

↓

Application Services

↓

Background Workers

↓

Database Cluster

↓

Redis

↓

Monitoring

↓

Logging

↓

Broker APIs
```

Every service should be independently deployable.

---

# Technology Stack (Proposed)

Backend

- Python (FastAPI)

AI & Research

- Python
- PyTorch
- Scikit-learn
- XGBoost / LightGBM

Frontend

- Next.js
- React
- TailwindCSS

Database

- PostgreSQL

Cache

- Redis

Message Queue

- RabbitMQ / Kafka

Containerization

- Docker

Orchestration

- Kubernetes (Future)

Cloud

- AWS / GCP / Azure

Monitoring

- Prometheus
- Grafana

Logging

- Loki / ELK Stack

---

# Scalability Strategy

The platform should scale horizontally.

Example

```
1 API Server

↓

5 API Servers

↓

20 API Servers
```

Similarly,

multiple workers should process:

- Trend Analysis
- Liquidity Grab Detection
- Backtesting
- AI Training

independently.

No architectural redesign should be required for scaling.

---

# Disaster Recovery

The platform should support:

- Automated Backups
- Point-in-Time Recovery
- Database Replication
- Multi-Zone Deployment
- Service Restart Automation

The objective is minimizing downtime and preventing data loss.

---

# Engineering Decisions

The platform intentionally adopts a **modular microservice-inspired architecture** with clear service boundaries, asynchronous communication, deterministic trading logic, and independently scalable components.

This design prioritizes:

- Reliability
- Scalability
- Maintainability
- Explainability
- Fault Isolation

while ensuring that future additions—such as new trading strategies, AI models, broker integrations, or analytical engines—can be incorporated without requiring fundamental architectural redesign.

---

## Open Questions

1. Should the production platform begin as a modular monolith and later evolve into microservices, or should it adopt microservices from the beginning?

2. Which message broker best suits the expected event volume: RabbitMQ, Kafka, or another alternative?

3. Which cloud architecture provides the best balance between operational complexity and scalability?

4. How should the platform achieve zero-downtime deployments during market hours?

5. Which services require active-active redundancy, and which can tolerate active-passive failover?

6. What disaster recovery objectives (RTO/RPO) should be targeted for production deployments?

7. How should future broker integrations be standardized to minimize changes within the Execution Engine?