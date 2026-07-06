# Logging Standards

Observability is a foundational requirement. Logs must be structured, searchable, and secure.

## Log Levels
- **FATAL / CRITICAL:** The application is completely down or data is actively being corrupted. Wakes up engineers.
- **ERROR:** A specific operation failed unexpectedly (e.g., unable to save trade to DB). Requires investigation.
- **WARN:** An unexpected state occurred, but the system recovered (e.g., 3rd party API timeout, retry succeeded).
- **INFO:** Significant business events (e.g., `OrderPlaced`, `SystemStarted`, `MarketOpened`).
- **DEBUG:** Verbose information useful for troubleshooting in development. Disabled in production.

## Structured Logging
- All logs must be written in a structured format (JSON).
- Logs must include timestamp, severity, message, and contextual metadata.
- Never concatenate strings to build log messages.

## Correlation IDs & Trace IDs
- **Correlation ID:** Every incoming request or triggered event must generate a unique Correlation ID. This ID must be passed through all layers and included in every log entry associated with that request.
- **Trace ID:** Used across distributed systems boundaries if applicable.

## Sensitive Data Masking
- **PII / Financial Data:** Personally Identifiable Information, auth tokens, passwords, and raw API keys MUST NEVER be logged.
- The logging framework must automatically sanitize fields like `password`, `token`, `secret`, `api_key`.

## Log Categories
Logs should include a `category` or `module` tag to easily filter by subsystem (e.g., `category: RiskEngine`, `category: Database`).

## Log Retention Philosophy
- Application logs (INFO/DEBUG) are retained for 30 days.
- Audit logs (Financial transactions, configuration changes) are retained indefinitely in cold storage.
- ERROR logs are retained for 90 days.
