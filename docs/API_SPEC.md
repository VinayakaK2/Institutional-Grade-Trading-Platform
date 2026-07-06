# API_SPEC.md

# Institutional Swing Trading Platform

**Version:** 1.0

---

# Overview

The API Specification defines how every external component communicates with the Institutional Swing Trading Platform.

The API layer is intentionally designed as a thin communication layer.

It never performs trading analysis.

It never calculates indicators.

It never makes trading decisions.

Instead, it validates requests, authenticates users, routes requests to the correct service, and returns standardized responses.

Every business decision remains inside the backend engines.

This separation ensures:

- Maintainability
- Scalability
- Security
- Versioning
- Consistency

---

# API Architecture

```
Client

↓

API Gateway

↓

Authentication

↓

Authorization

↓

Validation

↓

Application Service

↓

Trading Engine

↓

Database

↓

Standard Response
```

Every request follows the same pipeline.

---

# API Categories

The platform exposes APIs through logical domains.

```
Authentication

Market

Watchlist

Trading

Portfolio

Orders

Analytics

Learning

AI

Notifications

Administration

System
```

Every category owns its own endpoints.

---

# Standard API Response

Every endpoint returns the same response structure.

Success

```json
{
    "success": true,
    "message": "Trade created successfully",
    "data": {},
    "meta": {},
    "timestamp": "2026-01-01T10:00:00Z"
}
```

Failure

```json
{
    "success": false,
    "error": {
        "code": "TRADE_NOT_FOUND",
        "message": "Trade does not exist."
    },
    "request_id": "abc123"
}
```

No endpoint should return inconsistent structures.

---

# Authentication APIs

## Login

```
POST

/api/v1/auth/login
```

Returns

- Access Token
- Refresh Token
- User

---

## Refresh Token

```
POST

/api/v1/auth/refresh
```

---

## Logout

```
POST

/api/v1/auth/logout
```

---

## Current User

```
GET

/api/v1/auth/me
```

---

# Market APIs

Retrieve market information.

Examples

```
GET

/api/v1/market/status
```

```
GET

/api/v1/market/symbols
```

```
GET

/api/v1/market/candles
```

Parameters

- Symbol
- Date Range
- Timeframe

---

# Watchlist APIs

```
GET

/watchlist
```

Returns current watchlist.

---

```
POST

/watchlist/refresh
```

Triggers manual refresh.

---

```
GET

/watchlist/history
```

Returns historical watchlists.

---

# Trade APIs

Retrieve opportunities.

```
GET

/trades
```

```
GET

/trades/{id}
```

```
POST

/trades/validate
```

```
DELETE

/trades/{id}
```

Trade APIs never bypass Risk Engine.

---

# Risk APIs

```
GET

/risk/{trade}
```

Returns

- Risk
- Quantity
- Stop Loss
- RR

---

```
POST

/risk/recalculate
```

---

# Portfolio APIs

```
GET

/portfolio
```

```
GET

/portfolio/positions
```

```
GET

/portfolio/history
```

```
GET

/portfolio/performance
```

---

# Order APIs

```
POST

/orders
```

Create Order.

---

```
GET

/orders/{id}
```

Order Status.

---

```
DELETE

/orders/{id}
```

Cancel Order.

---

```
GET

/orders/history
```

---

# Analytics APIs

```
GET

/analytics/dashboard
```

```
GET

/analytics/performance
```

```
GET

/analytics/reports
```

```
GET

/analytics/risk
```

---

# Learning APIs

```
GET

/learning/reports
```

```
GET

/learning/features
```

```
GET

/learning/statistics
```

---

# AI APIs

```
GET

/ai/models
```

```
GET

/ai/predictions
```

```
GET

/ai/explanations
```

```
POST

/ai/retrain
```

(Admin Only)

---

# Notification APIs

```
GET

/notifications
```

```
PUT

/notifications/{id}/read
```

```
DELETE

/notifications/{id}
```

---

# System APIs

```
GET

/system/health
```

```
GET

/system/jobs
```

```
GET

/system/version
```

```
GET

/system/config
```

---

# WebSocket APIs

Real-time events use WebSockets.

```
ws://server/ws
```

Supported Events

```
Watchlist Updated

Trade Approved

Order Filled

Portfolio Updated

Notification Created

Analytics Updated

Learning Updated

System Alert
```

The dashboard updates instantly without polling.

---

# Authentication

Protected APIs require

```
Authorization

Bearer <JWT>
```

Every request validates

- Token
- Expiration
- User
- Role
- Permissions

---

# Authorization

Roles

```
Administrator

Trader

Researcher

Viewer
```

Every endpoint declares required permissions.

Example

```
POST

/orders

↓

Trader Only
```

---

# Validation

Every request validates

- Required Fields
- Data Types
- Business Rules
- Permissions

Validation occurs before business logic.

---

# Pagination

Large datasets support pagination.

Example

```
?page=2

&limit=50
```

Response

```
Total Records

Current Page

Total Pages
```

---

# Filtering

Supported Filters

- Symbol
- Date
- Strategy Version
- Status
- Portfolio
- Sector
- Trade Result

Example

```
GET

/trades?symbol=RELIANCE&status=OPEN
```

---

# Sorting

Supported

```
sort

order
```

Example

```
?sort=created_at

&order=desc
```

---

# Rate Limiting

Anonymous

```
30 req/min
```

Authenticated

```
300 req/min
```

Administrative

Configurable

Critical endpoints receive stricter protection.

---

# Idempotency

Order APIs support

```
Idempotency-Key
```

Repeated requests never create duplicate orders.

---

# API Versioning

Every endpoint belongs to

```
/api/v1/
```

Future versions

```
/api/v2/
```

Older clients continue functioning until officially deprecated.

---

# API Logging

Every request stores

- Request ID
- User
- Endpoint
- Method
- Latency
- Status Code
- Client IP
- Strategy Version

Logs support debugging and auditing.

---

# Error Codes

Examples

```
AUTH_001

Invalid Token
```

```
TRADE_002

Trade Not Found
```

```
RISK_003

Risk Limit Exceeded
```

```
ORDER_004

Broker Rejected
```

```
SYSTEM_001

Internal Server Error
```

Errors remain standardized across all APIs.

---

# Security

Every endpoint implements

- JWT Authentication
- RBAC
- Input Validation
- Rate Limiting
- Audit Logging
- TLS Encryption

Administrative endpoints additionally require elevated privileges.

---

# Performance Targets

| Operation | Target |
|-----------|---------|
| Authentication | <300 ms |
| Standard API | <200 ms |
| Dashboard API | <500 ms |
| Portfolio API | <300 ms |
| Analytics API | <1 sec |
| Order Submission | Network Dependent |
| WebSocket Broadcast | <100 ms |

---

# Engineering Decisions

The API layer is intentionally lightweight and stateless.

All trading intelligence remains inside dedicated engines, while the API layer focuses exclusively on secure communication, validation, routing, authentication, authorization, and standardized responses.

This architecture enables multiple clients—including web applications, mobile applications, AI services, research tools, and future third-party integrations—to interact with the platform consistently without exposing internal implementation details.

Future API versions can evolve independently while preserving backward compatibility and maintaining strict separation between communication and business logic.