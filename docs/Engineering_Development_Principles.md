# Engineering Development Principles

## Principle 1 — Foundation First

A weak foundation guarantees future failures.

Infrastructure is always built before business logic.

Examples:

- Configuration
- Logging
- Testing
- Database
- Event Bus
- Observability
- CI/CD

must exist before any trading engine.

---

## Principle 2 — One Feature at a Time

Only one feature may be under development at any time.

No parallel feature implementation.

The objective is minimizing variables during debugging.

---

## Principle 3 — Definition of Done

A feature is NOT complete when the code works.

A feature is complete only when every quality gate passes.

Working code ≠ Finished feature.

---

## Principle 4 — Zero Regression

Previously completed functionality must never break.

Every change must prove that existing behavior remains correct.

Regression failures block development.

---

## Principle 5 — Production Quality from Day One

Temporary code becomes permanent code.

Therefore:

No prototype code.

No "quick fix".

No "we'll refactor later".

Everything merged into the main branch must be production quality.

---

## Principle 6 — Fail Fast

Invalid assumptions should fail immediately.

Silent failures are forbidden.

Every unexpected state must be:

- Logged
- Reported
- Classified
- Handled

---

## Principle 7 — Defensive Engineering

Assume everything can fail.

Examples:

- Network failure
- API timeout
- Invalid data
- Corrupted database
- Missing configuration
- Duplicate events
- Market holidays
- Clock drift
- Broker rejection

The system must remain stable.

---

## Principle 8 — Deterministic Behavior

Given identical input,

the system must produce identical output.

Hidden randomness is prohibited unless explicitly designed.

---

## Principle 9 — Test Before Trust

No feature is trusted because it "looks correct."

Trust is earned through automated testing.

---

## Principle 10 — Freeze Before Expand

Once a feature passes every quality gate,

it becomes Frozen.

Frozen components cannot be modified without passing the complete regression suite.

New development starts only after Freeze.

## Engineering Lifecycle for Every Feature
```
Requirement
      │
      ▼
Research
      │
      ▼
Architecture Review
      │
      ▼
Design
      │
      ▼
Risk Analysis
      │
      ▼
Implementation
      │
      ▼
Static Analysis
      │
      ▼
Unit Tests
      │
      ▼
Integration Tests
      │
      ▼
Edge Case Tests
      │
      ▼
Failure Injection Tests
      │
      ▼
Performance Tests
      │
      ▼
Security Tests
      │
      ▼
Regression Tests
      │
      ▼
Documentation Update
      │
      ▼
Code Review
      │
      ▼
Freeze
      │
      ▼
Next Feature
```

## Quality Gates
A feature cannot move to the next stage until every gate passes.

## Gate 1 — Requirements

✓ PRD updated

✓ Acceptance criteria defined

✓ Edge cases identified

✓ Failure scenarios documented

---

## Gate 2 — Design

✓ Architecture approved

✓ Database impact reviewed

✓ API contract reviewed

✓ Dependency analysis complete

---

## Gate 3 — Implementation

✓ Feature complete

✓ No TODOs

✓ No placeholder logic

✓ Coding standards followed

---

## Gate 4 — Verification

✓ Unit tests pass

✓ Integration tests pass

✓ Edge cases pass

✓ Failure cases pass

✓ Static analysis clean

---

## Gate 5 — Validation

✓ Performance acceptable

✓ Memory acceptable

✓ Security validated

✓ Observability complete

---

## Gate 6 — Regression

✓ Previous features unaffected

✓ Existing APIs unchanged

✓ Existing tests pass

---

## Gate 7 — Documentation

✓ Documentation updated

✓ Architecture updated

✓ Changelog updated

✓ Test evidence recorded

---

## Gate 8 — Freeze

Feature marked immutable until a future change request.

Development proceeds to the next feature.

## Testing Pyramid

```
                    Manual Validation
                           ▲
                    End-to-End Tests
                           ▲
                  Integration Tests
                           ▲
                      Unit Tests
```
Every bug found at a higher layer should result in a lower-layer automated test so it never reappears.

## Regression Policy
```
Every bug fixed must introduce a permanent regression test.

Bug Found

↓

Write Failing Test

↓

Fix Bug

↓

Run Test

↓

Add Test to Regression Suite

↓

Bug Can Never Reappear
```
If the bug comes back later, CI fails immediately.

## Branch Policy
```
main
│
├── Frozen
│
├── Always Deployable
│
└── Protected

↓

feature/<feature-name>

↓

Develop

↓

Test

↓

Review

↓

Merge

↓

Freeze
```
Never develop directly on main.

## Change Control

Changing a Frozen module requires:

1. Change Request
2. Impact Analysis
3. Updated Design
4. Updated Tests
5. Regression Suite
6. Approval
7. Merge

This prevents accidental breakage of stable components.

## Project Success Matric
```
At any point during development:

✅ The project should compile.
✅ All automated tests should pass.
✅ Any completed feature should be releasable.
✅ No feature should rely on "unfinished future work."
✅ The project should be in a deployable state after every successful merge.
```

## MANDATORY DEBUGGING & VERIFICATION LOOP


The implementation is NOT complete until ALL failures are eliminated.

If:

• Compilation fails
• Linting fails
• Static analysis fails
• Unit tests fail
• Integration tests fail
• Regression tests fail
• Performance tests fail
• Security tests fail
• Runtime errors occur
• Unexpected behavior is observed

You MUST:

1. Investigate the root cause.
2. Debug the issue thoroughly.
3. Identify the actual source of the problem.
4. Implement the correct fix.
5. Re-run the failed verification.
6. Re-run all affected tests.
7. Re-run the complete regression suite.
8. Repeat this entire cycle until EVERY check passes.

Never stop after discovering a bug.

Never leave a known issue unresolved.

Never bypass or disable tests to make them pass.

Never apply superficial fixes without identifying the root cause.

Every bug must either:
• be fixed completely, or
• be explicitly reported with a detailed root-cause analysis if it cannot be resolved.

### STOP CONDITION

The task is NOT finished until:
```
✓ Project builds successfully.
✓ No runtime errors remain.
✓ All tests pass.
✓ All regression tests pass.
✓ All identified bugs are debugged and resolved.
✓ No known blocking issues remain.
✓ No workaround has been used in place of a proper fix.
```

## REPORTING

Do not create separate debugging reports unless explicitly requested.

While implementing:

- Debug continuously.
- Fix root causes.
- Re-run all affected verification.
- Repeat until every quality gate passes.

At completion, return only:

1. Files changed
2. Bugs fixed (with one-line RCA)
3. Verification summary
4. Final PASS/FAIL status

Generate detailed reports (DEBUG_REPORT.md, BUG_HISTORY.md,
FINAL_VERIFICATION.md) only for major milestones or when explicitly requested.

## Bug Management

Treat every bug as a specification gap, not just a coding mistake.

Whenever you discover a bug:

1. Update the specification if it was ambiguous.
2. Add a regression test that reproduces the bug.
3. Fix the code.
4. Verify the regression test passes.
5. Freeze the fix.