# Quality Standards

Institutional-grade software is defined by its rigorous quality gates. 

## Code Coverage Goals
- Minimum 90% statement coverage for the Domain and Application layers.
- Minimum 80% coverage for the Infrastructure layer.
- Coverage metrics are enforced by CI/CD. PRs dropping coverage below these thresholds will be automatically rejected.

## Linting Requirements
- A strict linter must be configured and integrated into the IDE and CI pipeline.
- There are zero warnings allowed in production code. A warning must either be fixed or explicitly suppressed with a documented justification.

## Formatting Rules
- Code formatting must be 100% automated (e.g., Prettier, Black, gofmt).
- No manual arguments over formatting are permitted in Code Reviews. The formatter's output is the law.

## Static Analysis Requirements
- Static Application Security Testing (SAST) and advanced static analysis tools must run on every PR.
- Cyclomatic complexity must be kept under 10 for any single function.

## Performance Expectations
- Latency-sensitive paths (e.g., Trade Execution) must have defined SLAs (e.g., < 50ms).
- N+1 database query problems are strictly prohibited.
- Performance regressions must be caught via automated benchmark testing.

## Security Expectations
- Principle of Least Privilege applies to all database users, network roles, and container environments.
- Dependency vulnerability scanning (e.g., Dependabot, Snyk) must be enabled. Known critical vulnerabilities block deployments.

## Maintainability Expectations
- Code must be written for the next engineer. Complex logic must be broken down and commented.
- Magic numbers are banned. All constants must be extracted and named.

## Technical Debt Policy
- Technical debt is only permitted if it is formally documented, time-boxed, and tracked in the issue tracker.
- Unintentional technical debt (e.g., "we rushed it and it's messy") is not tolerated and violates the 'Production Quality from Day One' principle.
