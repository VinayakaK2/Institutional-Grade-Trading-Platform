# Naming Conventions

Consistency in naming is critical for codebase navigation and maintainability. These conventions must be followed strictly across all system components.

## Infrastructure & Filesystem
- **Folders:** `kebab-case` (e.g., `trading-engine`, `data-ingestion`).
- **Files:** `kebab-case` (e.g., `user-repository.ts`, `trade-execution-service.py`). 
  - *Exception:* If language standards strictly dictate otherwise (e.g., Go package structures, Java Class names matching file names), those language standards take precedence.

## Code Entities
- **Classes:** `PascalCase` (e.g., `TradeExecutionEngine`, `MarketDataParser`).
- **Interfaces:** `PascalCase` (e.g., `IRepository` or `TradeExecutor` depending on language norms. Avoid `I` prefix if the language allows clean abstractions).
- **Functions:** `camelCase` (e.g., `calculateRisk`, `validateOrder`).
- **Methods:** `camelCase` (e.g., `executeTrade`, `rollbackTransaction`).
- **Variables:** `camelCase` (e.g., `tradeAmount`, `currentUser`).
- **Constants:** `SCREAMING_SNAKE_CASE` (e.g., `MAX_RETRY_COUNT`, `DEFAULT_TIMEOUT_MS`).
- **Enums:** `PascalCase` for the Enum name, `PascalCase` or `SCREAMING_SNAKE_CASE` for members (e.g., `OrderState.Pending` or `OrderState.PENDING`).

## Database
- **Database tables:** `snake_case`, pluralized (e.g., `users`, `trade_executions`, `market_snapshots`).
- **Database columns:** `snake_case` (e.g., `id`, `created_at`, `order_status`).

## Environment & Configuration
- **Environment variables:** `SCREAMING_SNAKE_CASE` (e.g., `DATABASE_URL`, `REDIS_PORT`).
- **Configuration keys:** Hierarchical `kebab-case` or `camelCase` depending on format (e.g., `database.max-connections` for YAML/JSON).

## Messaging & Events
- **Events:** `PascalCase` representing past tense actions (e.g., `OrderExecuted`, `MarketDataReceived`).
- **Message names:** `PascalCase` for commands representing intent (e.g., `ExecuteOrderCommand`, `CancelTradeCommand`).

## APIs & Networking
- **API endpoints:** Plural nouns, `kebab-case` (e.g., `/api/v1/trade-orders`, `/api/v1/market-data`).
- **Routes:** Same as API endpoints. No trailing slashes.

## Version Control
- **Branches:** `{type}/{issue-number}-{short-description}` (e.g., `feat/123-add-risk-engine`, `fix/456-timeout-issue`).
- **Git tags:** Semantic versioning with `v` prefix (e.g., `v1.2.0`, `v0.1.0-alpha`).
- **Version numbers:** Semantic Versioning format `MAJOR.MINOR.PATCH` (e.g., `1.0.0`).
