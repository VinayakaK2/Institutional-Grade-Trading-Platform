# Error Handling Standards

Errors must be handled explicitly and gracefully. System panics or uncaught exceptions are strictly prohibited in production.

## Expected vs. Unexpected Errors
- **Expected Errors:** Business logic violations, validation errors, or known temporary states (e.g., "Market Closed", "Insufficient Funds"). These should be returned as domain error objects or typed results, not thrown as exceptions.
- **Unexpected Errors:** Hardware failures, out-of-memory errors, corrupted database schemas. These should throw fatal exceptions that are caught by global handlers, logged as `CRITICAL`, and gracefully terminate or fail the specific transaction.

## Validation Failures
- Validation must happen at the edges of the system (e.g., API controllers, message consumers).
- Invalid inputs must be rejected immediately with a `400 Bad Request` or equivalent, providing clear, human-readable reasons for the failure.

## Infrastructure Failures
- Assume external systems (Databases, Redis, Brokers, Market APIs) will fail.
- All external calls must be wrapped in failure-handling mechanisms.

## Retry Policy
- Transient errors (e.g., network timeouts, rate limits) must utilize an Exponential Backoff strategy with jitter.
- Idempotent operations may be retried. Non-idempotent operations must only be retried if safety is mathematically guaranteed.

## Timeout Policy
- Every network request, database query, and asynchronous operation MUST have a strict timeout defined.
- Infinite waits are forbidden.

## Exception Hierarchy Philosophy
- Define a base Application Exception class.
- Subclass specific categories (e.g., `ValidationException`, `InfrastructureException`, `DomainException`).
- Do not create a unique exception class for every single error message, but do categorize them correctly for monitoring.

## Logging Policy for Errors
- Every caught unexpected error must be logged with its full stack trace, context parameters, and correlation ID.
- Expected domain errors should be logged at `INFO` or `WARN` levels without stack traces, as they are part of normal business operation.
