# 27. API Design & Specifications

---

# Overview

The API Layer is the communication backbone of the Institutional Swing Trading Platform.

Every frontend application, mobile application, AI service, analytics service, broker adapter, scheduler, and background worker communicates through standardized APIs.

The API layer should never contain trading logic.

Its responsibility is to expose the capabilities of the platform in a secure, versioned, consistent, and scalable manner.

The guiding philosophy is simple:

> **Business logic belongs inside the Engines. APIs only expose that logic.**

This separation ensures maintainability, testability, and future extensibility.

---

# API Design Principles

The platform follows the following API principles.

## Principle 1

Stateless APIs

Each request must contain everything required for execution.

No request should depend upon previous API calls.

---

## Principle 2

Versioned APIs

Every production API should be versioned.

Example

```
/api/v1/
```

Future versions

```
/api/v2/
```

Older clients should continue functioning after upgrades.

---

## Principle 3

Consistent Responses

Every endpoint should return a standardized response format.

Example

```json
{
  "success": true,
  "message": "Trade candidate retrieved successfully.",
  "data": {},
  "meta": {},
  "timestamp": "2026-08-18T09:30:00Z"
}
```

---

## Principle 4

REST for Commands

WebSockets for Events.

REST

↓

User Requests

WebSocket

↓

Real-Time Updates

---

## Principle 5

Every Request Is Auditable

Every API request should generate:

- Request ID
- User ID
- Timestamp
- IP Address
- Processing Time
- Status Code

---

# API Architecture

```
Frontend

↓

API Gateway

↓

Authentication

↓

Validation

↓

Rate Limiting

↓

Application Services

↓

Trading Engines

↓

Database
```

---

# API Categories

The platform APIs are grouped into logical domains.

```
Authentication APIs

User APIs

Market APIs

Watchlist APIs

Trend APIs

Consolidation APIs

Liquidity APIs

Trade APIs

Risk APIs

Portfolio APIs

Execution APIs

Analytics APIs

Learning APIs

AI APIs

Notification APIs

System APIs
```

---

# Authentication APIs

Base URL

```
/api/v1/auth
```

---

## Login

```
POST

/login
```

Request

```json
{
  "email": "user@example.com",
  "password": "********"
}
```

Response

```json
{
  "access_token": "...",
  "refresh_token": "...",
  "expires_in": 3600
}
```

---

## Refresh Token

```
POST

/refresh
```

---

## Logout

```
POST

/logout
```

---

## Current User

```
GET

/me
```

---

# Market APIs

```
GET

/api/v1/market/symbols
```

Returns all supported symbols.

---

```
GET

/api/v1/market/candle/{symbol}
```

Returns historical candles.

Parameters

```
from

to

timeframe
```

---

```
GET

/api/v1/market/sectors
```

Returns sector information.

---

```
GET

/api/v1/market/status
```

Returns current market regime.

---

# Watchlist APIs

```
GET

/watchlists/current
```

Returns current watchlist.

---

```
POST

/watchlists/refresh
```

Triggers refresh.

---

```
GET

/watchlists/history
```

Returns historical watchlists.

---

```
GET

/watchlists/{symbol}
```

Returns watchlist information.

---

# Trend APIs

```
GET

/trend/{symbol}
```

Returns latest trend analysis.

---

```
POST

/trend/recalculate
```

Recalculates trend.

---

```
GET

/trend/history/{symbol}
```

Historical trend analysis.

---

# Consolidation APIs

```
GET

/consolidations/{symbol}
```

---

```
GET

/consolidations/current
```

---

```
POST

/consolidations/recalculate
```

---

# Liquidity Grab APIs

```
GET

/liquidity-grabs/current
```

---

```
GET

/liquidity-grabs/{symbol}
```

---

```
GET

/liquidity-grabs/history/{symbol}
```

---

# Entry APIs

```
GET

/trades/candidates
```

Returns approved trade candidates.

---

```
GET

/trades/{trade_id}
```

Returns trade details.

---

# Risk APIs

```
GET

/risk/{trade_id}
```

Returns risk calculations.

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

Current portfolio.

---

```
GET

/portfolio/positions
```

Open positions.

---

```
GET

/portfolio/history
```

Closed positions.

---

```
GET

/portfolio/performance
```

Performance statistics.

---

# Execution APIs

```
POST

/orders
```

Create new order.

---

```
GET

/orders/{id}
```

Order status.

---

```
DELETE

/orders/{id}
```

Cancel order.

---

```
GET

/executions
```

Execution history.

---

# Analytics APIs

```
GET

/analytics/dashboard
```

Dashboard metrics.

---

```
GET

/analytics/performance
```

---

```
GET

/analytics/trades
```

---

```
GET

/analytics/risk
```

---

```
GET

/analytics/portfolio
```

---

# Learning APIs

```
GET

/learning/reports
```

---

```
GET

/learning/features
```

---

```
GET

/learning/recommendations
```

---

# AI APIs

```
GET

/ai/models
```

---

```
GET

/ai/predictions
```

---

```
GET

/ai/explanations/{trade}
```

---

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

---

```
PUT

/notifications/{id}/read
```

---

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

Returns health status.

---

```
GET

/system/jobs
```

---

```
GET

/system/logs
```

(Admin)

---

```
GET

/system/config
```

---

# WebSocket APIs

The platform uses WebSockets for real-time communication.

Connection

```
ws://server/ws
```

Events

```
watchlist.updated
```

```
trade.approved
```

```
order.executed
```

```
position.updated
```

```
portfolio.updated
```

```
notification.created
```

```
market.updated
```

```
system.alert
```

Example

```json
{
    "event": "trade.approved",
    "timestamp": "...",
    "payload": {}
}
```

---

# API Authentication

Every protected endpoint requires:

```
Authorization

Bearer <JWT>
```

Authentication middleware validates:

- Token
- Expiration
- User
- Roles
- Permissions

---

# Authorization

Supported Roles

```
Admin

Researcher

Trader

Viewer
```

Role examples

Admin

↓

Everything

Trader

↓

Trading

Portfolio

Analytics

Viewer

↓

Read Only

---

# Pagination

Large datasets should support pagination.

Example

```
GET

/trades?page=2&limit=50
```

Response

```json
{
  "data": [],
  "meta": {
      "page":2,
      "limit":50,
      "total":1042
  }
}
```

---

# Filtering

Supported filters

```
date

strategy_version

symbol

sector

status

market_regime

portfolio

risk_level
```

Example

```
GET

/trades?symbol=RELIANCE&status=OPEN
```

---

# Sorting

Example

```
?sort=created_at

?order=desc
```

---

# Error Response Format

Every API should return consistent errors.

Example

```json
{
    "success":false,
    "error":{
        "code":"TRADE_NOT_FOUND",
        "message":"Trade does not exist."
    },
    "request_id":"abc123"
}
```

---

# HTTP Status Codes

```
200

OK
```

```
201

Created
```

```
204

No Content
```

```
400

Bad Request
```

```
401

Unauthorized
```

```
403

Forbidden
```

```
404

Not Found
```

```
409

Conflict
```

```
422

Validation Error
```

```
429

Rate Limited
```

```
500

Internal Server Error
```

---

# API Rate Limiting

Examples

Anonymous

```
30 requests/minute
```

Authenticated

```
300 requests/minute
```

Admin

```
Higher configurable limits
```

Critical endpoints should implement stricter protection.

---

# Idempotency

Order creation APIs should support idempotency.

Example

```
Idempotency-Key

xxxxxxxx
```

Repeated identical requests must not create duplicate orders.

---

# API Logging

Every request logs:

- Request ID
- Endpoint
- User
- Response Time
- Status Code
- Client IP
- Strategy Version (where applicable)

Logs feed into the Analytics and Audit systems.

---

# API Versioning

Every endpoint belongs to a version.

Example

```
/api/v1/trades
```

Future versions remain backward compatible whenever practical.

Deprecated APIs should provide migration periods before removal.

---

# API Documentation

The platform should provide interactive documentation.

Preferred tools

- OpenAPI 3.1
- Swagger UI
- ReDoc

Documentation should include:

- Request Examples
- Response Examples
- Authentication
- Error Codes
- Rate Limits
- Example Workflows

Documentation must be generated automatically from the source whenever possible.

---

# Engineering Decisions

The API layer is intentionally designed as a thin communication interface.

It does **not**:

- Perform trading analysis.
- Calculate indicators.
- Approve trades.
- Calculate risk.
- Execute AI models.

Its responsibility is limited to validating requests, enforcing authentication and authorization, routing requests to the appropriate services, and returning standardized responses.

This architecture ensures a clean separation between communication and business logic while allowing multiple clients—including web applications, mobile applications, research tools, AI services, and future third-party integrations—to interact with the platform consistently.

---

## Open Questions

1. Should future broker integrations expose REST APIs, WebSockets, or both?

2. Which endpoints should support bulk operations for large-scale research workflows?

3. How should API version deprecation be managed to minimize client disruption?

4. Which API calls should remain synchronous, and which should transition to asynchronous job-based execution?

5. What rate limits best balance platform protection with research productivity?

6. Should external developers be allowed to build against a public API, or should the platform remain private?

7. How should API compatibility be maintained as new trading engines and strategy versions are introduced?