# Workspace Custom Rules: Institutional Swing Trading Platform

These rules have been established based on user feedback and project requirements during Phase 0 and Phase 2.1 development. They are mandatory for all subsequent work in this workspace.

## 1. Modular Monolith & SOLID Principles
- The project follows a strict Modular Monolith architecture.
- **Dependency Injection**: Services must depend on interfaces (Protocols/ABCs), not concrete implementations (e.g. `ProviderRegistry`, `BaseRepository`).
- **Isolation**: Features (`market_data`, `market_calendar`) must not tightly couple their implementations. Interaction happens via interfaces or an Event Bus.
- **Fail Gracefully**: Infrastructure components (Redis, Database) must handle unavailability smoothly. Use Circuit Breakers, Retries, and graceful fallback warnings instead of crashing the system.

## 2. Pydantic & Strict Validation
- Use Pydantic V2 strictly.
- When writing tests or fixtures for Pydantic models with nested structures (like `SymbolReference` containing `ExchangeReference`), construct the entire nested schema completely. Do not use generic strings where objects are expected.
- Strict Type checking (via MyPy) is mandatory. Do not use `# type: ignore` as a crutch without deep justification.

## 3. Strict Testing & 90% Coverage Mandate
- **A bug is NOT considered resolved until a regression test exists.** Every bug fix MUST include an automated test that would fail if the bug reappeared.
- Coverage threshold is strictly **90.0%**. Do not drop below this.
- If mocking is required, respect Pydantic V2 limitations (e.g. `model_dump` cannot be monkeypatched easily; use custom mock classes instead).
- Enum members must be accessed by their exact object (e.g., `Timeframe.H1`), not arbitrary string values.

## 4. Evidence-Based Reporting (CRITICAL)
- **DO NOT summarize verification**. The user requires strict evidence.
- When generating reports (`FINAL_VERIFICATION.md`, `DEBUG_REPORT.md`), they must follow an **Evidence ➔ Verification ➔ Conclusion** format.
- For every verification step, explicitly include:
  - The exact Command executed
  - The Complete terminal output
  - The Exit code
  - The Result (PASS / FAIL)
- **Do not paraphrase** terminal output and do not omit failures.
- **Runtime Verification**: Smoke tests must explicitly output PASS/FAIL for every distinct infrastructure component (e.g., Logger, Config, DB, Redis, EventBus, HealthChecks, Shutdown). If a component degrades gracefully (e.g., Redis offline), log it as a handled failure, not a generic "success".
- **Production Readiness**: Do not blindly state "The project is production ready." State that it satisfies production requirements within the verified scope, supported by a verifiable checklist (Build, AST, Ruff, MyPy, Bandit, Pytest, Coverage).

## 5. Development Mindset
- Think in workflows (input -> processing -> storage -> output -> failure scenarios), not just isolated functions.
- Never write code that works locally but fails in production. Always design for failure tolerance (partial failures should degrade gracefully).
- Execute static analysis (`ruff`, `mypy`, `bandit`) proactively. Fix all warnings immediately.


# Engineering Verification & Debugging Protocol

## Purpose

This skill is automatically invoked after every implementation, refactor, bug fix, optimization, or infrastructure change.

Its objective is to ensure that no implementation is considered complete until it has been fully debugged, verified, tested, and validated using production-grade engineering practices.

This skill is mandatory for every coding task.

---

# Core Principle

Implementation is only the beginning.

A task is complete only after:
- Debugging
- Verification
- Validation
- Regression Testing
- Evidence Collection

have all completed successfully.

Working code is NOT considered finished.

Verified code is.

---

# Automatic Workflow

Every implementation must automatically follow this lifecycle.

```
Understand Requirement
        │
        ▼
Design
        │
        ▼
Implement
        │
        ▼
Build
        │
        ▼
Debug
        │
        ▼
Fix
        │
        ▼
Rebuild
        │
        ▼
Unit Tests
        │
        ▼
Integration Tests
        │
        ▼
Regression Tests
        │
        ▼
Static Analysis
        │
        ▼
Runtime Verification
        │
        ▼
Evidence Collection
        │
        ▼
Final Review
```

Implementation is never considered complete before the final review.

---

# Mandatory Debugging Loop

Whenever any failure occurs, the agent MUST automatically enter the debugging loop.

```
Failure Detected
        │
        ▼
Reproduce
        │
        ▼
Collect Logs
        │
        ▼
Inspect Stack Trace
        │
        ▼
Inspect Runtime State
        │
        ▼
Identify Root Cause
        │
        ▼
Implement Proper Fix
        │
        ▼
Rebuild
        │
        ▼
Re-run Failed Tests
        │
        ▼
Re-run Regression Suite
        │
        ▼
Still Failing?
        │
   Yes ───────────────┐
        │             │
        ▼             │
Repeat Debugging Loop │
        │             │
        └─────────────┘

No

↓

Continue Verification
```

The debugging loop repeats until every blocking issue has been resolved.

Stopping after discovering a bug is prohibited.

---

# Root Cause Analysis

Every issue must be investigated.

Never:
- Guess
- Apply random fixes
- Hide errors
- Ignore warnings
- Disable tests
- Skip validation

Every bug requires:
- Problem
- Root Cause
- Correct Fix
- Verification
- Regression Protection

Fix symptoms only after fixing the root cause.

---

# Testing Requirements

Automatically execute every applicable test.

Examples include:
- Unit Tests
- Integration Tests
- Regression Tests
- Smoke Tests
- Performance Tests
- Security Tests
- Static Analysis
- Type Checking
- Linting

The appropriate set depends on the implementation.

---

# Regression Policy

Every bug fixed today must never reappear.

Whenever a bug is fixed:
1. Create a regression test.
2. Verify the regression test fails before the fix.
3. Apply the fix.
4. Verify the regression test passes.
5. Add it permanently to the regression suite.

---

# Verification Rules

Verification must be based on evidence.

Never claim:
- Production Ready
- Fully Tested
- Verified
- Stable

without objective verification.

Every conclusion must be supported by evidence.

---

# Evidence Collection

Whenever verification is performed, collect evidence such as:
- Build Results
- Test Results
- Static Analysis Results
- Runtime Verification
- Coverage Results
- Health Checks
- Performance Metrics

Summaries are acceptable only when supported by actual outputs.

---

# Runtime Validation

Whenever applicable verify:
- Startup
- Shutdown
- Resource Cleanup
- Error Handling
- Recovery Behaviour
- Configuration Loading
- Dependency Initialization

---

# Definition of Done

A task is complete only when:
- Feature implemented.
- Build succeeds.
- Runtime errors resolved.
- Root causes fixed.
- Appropriate tests pass.
- Regression tests pass.
- Static analysis clean.
- Documentation updated when required.
- No known blocking defects remain.

---

# Failure Policy

Never:
- Stop because tests failed.
- Ignore warnings.
- Bypass failing checks.
- Mark incomplete work as complete.
- Replace proper fixes with workarounds.

Continue until either:
- Every required verification passes
or
- A genuine blocker exists that cannot be resolved, with a complete explanation of the blocker.

---

# Engineering Philosophy

Always think like a production engineer.

Correctness is more important than speed.

Evidence is more valuable than assumptions.

Every completed task should leave the codebase more reliable than before.
