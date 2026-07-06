# Git Standards

Version control practices ensure codebase stability and traceability.

## Commit Rules
- Use Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`).
- Commits should be atomic. Do not bundle unrelated changes into a single commit.
- Commit messages must clearly explain *what* changed and *why*.

## Branch Naming
- `feature/{issue-number}-short-desc`
- `fix/{issue-number}-short-desc`
- `hotfix/{issue-number}-short-desc`
- `release/vX.Y.Z`

## Merge Strategy
- **Squash and Merge:** Feature branches should be squashed into a single commit when merging to `develop`. This keeps the main history linear and clean.
- **Merge Commits:** Used only when merging `develop` into `main` for a release, preserving the release history.

## Pull Request (PR) Checklist
- PR title follows Conventional Commits.
- Description links to the relevant issue.
- Code implements the feature exactly as designed.
- Unit and Integration tests are included.
- Documentation is updated.
- No unused code or TODOs remain.

## Code Review Checklist
- Reviewers must verify logic, edge cases, and adherence to these exact Repository Standards.
- Look for security flaws, performance bottlenecks, and missing error handling.
- Approve only if the code meets all Quality Gates.

## Definition of Ready
- Requirements are fully documented, understood, and agreed upon.
- Architectural impact has been assessed.
- Acceptance criteria are clear.

## Definition of Done
- Code is written and peer-reviewed.
- All automated tests pass (100% success rate required).
- Deployed successfully to staging.
- Product owner / Lead architect has signed off.

## Lifecycle Policies
- **Feature Freeze:** Before a release, `develop` is frozen. Only critical bug fixes are allowed.
- **Hotfix Policy:** Hotfixes branch directly from `main`, are tested, and merge back into BOTH `main` and `develop`.
- **Release Policy:** Releases are tagged using Semantic Versioning. A changelog is automatically generated based on Conventional Commits.
