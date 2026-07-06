# Repository Standards

## Naming Conventions
- **Directories:** kebab-case (e.g., `feature-name`)
- **Files:** kebab-case for generic files, PascalCase for classes/components depending on language specifics.
- **Variables/Functions:** camelCase (or snake_case, depending on the language chosen later).
- **Constants:** SCREAMING_SNAKE_CASE.

## Folder Conventions
- Code is organized by feature, following a Modular Monolith architecture.
- Clean Architecture principles dictate the separation of Domain, Application, and Infrastructure layers.

## Commit Message Conventions
We enforce Conventional Commits:
- `feat:` A new feature
- `fix:` A bug fix
- `docs:` Documentation only changes
- `style:` Changes that do not affect the meaning of the code
- `refactor:` A code change that neither fixes a bug nor adds a feature
- `perf:` A code change that improves performance
- `test:` Adding missing tests or correcting existing tests
- `chore:` Changes to the build process or auxiliary tools

## Pull Request Rules
- All PRs must target `develop` (unless it's a hotfix or release).
- A PR must have a clear description of the change, linking to any relevant issue.
- All automated checks (Static Analysis, Unit Tests, Integration Tests) must pass.

## Code Review Rules
- Reviewers must ensure the code meets all Quality Gates defined in the Engineering Principles.
- Code must be defensive, robust, and free of "TODO" placeholders.
- A minimum of one approval from a core maintainer is required.
