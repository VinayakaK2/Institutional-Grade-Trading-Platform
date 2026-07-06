# Coding Standards

This document defines the core principles of writing code for the Institutional Swing Trading Platform. Every component must be designed and built according to these principles to ensure robustness, predictability, and long-term maintainability.

## 1. General Coding Principles
- **Clarity over Cleverness:** Code must be easily understandable by any engineer reviewing it. If a block of code requires complex mental gymnastics to understand, it must be refactored.
- **Fail Fast:** Systems must fail explicitly at the first sign of invalid input or state. Silent failures or undefined behaviors are prohibited.
- **Statelessness Where Possible:** State mutations must be minimized and tightly controlled to reduce edge cases and bugs.

## 2. SOLID Principles
Code must adhere strictly to the SOLID principles:
- **Single Responsibility Principle (SRP):** A class or module must have exactly one reason to change.
- **Open-Closed Principle (OCP):** Software entities should be open for extension but closed for modification.
- **Liskov Substitution Principle (LSP):** Subtypes must be substitutable for their base types without altering program correctness.
- **Interface Segregation Principle (ISP):** Clients should not be forced to depend on methods they do not use. Favor smaller, highly cohesive interfaces.
- **Dependency Inversion Principle (DIP):** High-level modules must not depend on low-level modules. Both must depend on abstractions.

## 3. KISS (Keep It Simple, Stupid)
- Do not over-engineer. Solve the exact problem at hand with the simplest viable architecture.
- Abstract only when a pattern repeats, not preemptively.

## 4. DRY (Don't Repeat Yourself)
- Every piece of knowledge must have a single, unambiguous, authoritative representation within a system.
- Shared logic must be centralized, but do not falsely couple concepts that just happen to look similar (accidental duplication).

## 5. YAGNI (You Aren't Gonna Need It)
- Do not implement functionality or abstract structures based on hypothetical future needs. Build only what is required for the current requirement.

## 6. Composition Over Inheritance
- Prefer composing complex behaviors from smaller, interchangeable modules rather than building deep inheritance trees. Deep inheritance leads to fragility and tight coupling.

## 7. Dependency Inversion
- Core business logic must not import implementation details.
- Database clients, API clients, and infrastructure libraries must be injected via interfaces.
- This ensures testability via mocking and prevents the domain from being polluted by framework-specific code.

## 8. Immutability Where Appropriate
- State should be immutable by default. 
- Use immutable data structures and pass copies of data instead of mutating references, minimizing side-effects and race conditions.

## 9. Explicitness Over Magic
- Avoid meta-programming, reflection, or implicit behaviors that obscure the execution path.
- Configuration and behavior should be explicit and traceable. "Magic" frameworks that hide execution details are strongly discouraged.

## 10. Deterministic Behavior
- Given identical inputs and initial state, a system must always produce identical outputs.
- Any necessary randomness, time dependency (e.g., `now()`), or external variability must be explicitly injected so it can be controlled during testing.
