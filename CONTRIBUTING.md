# Contributing Guidelines

We follow a strict Engineering Development Lifecycle (EDL).

## Principles
- **Foundation First:** Infrastructure is built before business logic.
- **One Feature at a Time:** Minimize variables during debugging.
- **Zero Regression:** Existing behavior must remain correct.
- **Production Quality:** No prototypes or placeholder code.

## Workflow
1. Ensure there is an approved issue or feature request.
2. Create a feature branch from `develop`.
3. Implement the feature according to our Quality Gates.
4. Ensure all static analysis, unit tests, and integration tests pass.
5. Create a Pull Request against `develop`.
6. Obtain approval from at least one reviewer.

Please refer to the [Repository Standards](docs/repository-standards.md) and [Branch Strategy](docs/branch-strategy.md) for more details.
