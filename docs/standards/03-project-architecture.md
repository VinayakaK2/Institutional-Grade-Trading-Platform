# Project Architecture Rules

The platform adheres to a Modular Monolith architecture based heavily on Clean Architecture. The rules below dictate how code is structured and decoupled.

## 1. Clean Architecture & Layer Separation
- Code is divided into distinct, isolated layers: **Domain**, **Application**, **Interface/Adapters**, and **Infrastructure**.
- **Domain:** Contains pure business logic and trading rules. Has zero external dependencies.
- **Application:** Orchestrates use cases and domain objects. Depends on Domain.
- **Interface:** Controllers, API handlers, CLI entry points.
- **Infrastructure:** Database implementation, external API clients, message queue adapters.

## 2. Dependency Direction
- Dependencies must **always point inwards** toward the Domain layer. 
- Infrastructure depends on the Domain. The Domain depends on absolutely nothing.

## 3. Domain Isolation
- The Domain must not contain any technology-specific logic (e.g., no SQL, no HTTP clients, no ORM decorators).
- It must consist purely of business entities, value objects, and domain services.

## 4. No Circular Dependencies
- Circular dependencies between modules, classes, or files are strictly prohibited. They indicate architectural flaws and tight coupling.

## 5. Single Responsibility Principle (Architecture Level)
- Each module or micro-component should do one thing. 
- Example: The Risk Engine calculates risk; it does not place trades or query historical market data directly.

## 6. Controller Constraints
- **No business logic inside controllers.**
- Controllers are responsible only for receiving requests, validating input formats, invoking an Application Use Case, and returning a formatted response.

## 7. UI / Interface Constraints
- **No database queries inside the Interface layer.** 
- All data access must occur through Application layers calling Repository interfaces.

## 8. Infrastructure Constraints
- **No infrastructure leakage into the domain.** 
- If an ORM is used, domain models and ORM models must be cleanly separated, or mapped via repositories. The domain model should not inherit from an ORM base class.

## 9. Shared Module Rules
- A `shared` or `common` module may exist for highly generic utilities (e.g., date formatting, generic error classes).
- It must **not** contain business-specific logic. Do not dump code into `shared` simply to bypass dependency rules.
