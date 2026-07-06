# Branch Strategy

We follow a strict branch management policy to ensure that the repository remains in a releasable state.

## Branches

- **`main`**: Represents the current production release. Immutable except for controlled merges.
- **`develop`**: The integration branch for new features. Must always be deployable.
- **`feature/*`**: Used for developing new features. Branched from `develop` and merged back into `develop`.
- **`hotfix/*`**: Used for urgent production fixes. Branched from `main` and merged into both `main` and `develop`.
- **`release/*`**: Used for preparing a new production release. Branched from `develop` and merged into `main`.

## Process
1. Never develop directly on `main` or `develop`.
2. All feature branches must pass the complete regression suite before merging.
3. Frozen components cannot be modified without a formal Change Request and Impact Analysis.
