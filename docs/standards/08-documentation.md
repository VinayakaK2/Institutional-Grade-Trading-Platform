# Documentation Standards

Documentation is just as important as code. Without documentation, institutional memory is lost.

## General Formatting
- Use standard Markdown (GitHub Flavored Markdown).
- Keep formatting clean, utilizing appropriate headers, lists, and code blocks.

## Architecture Decision Records (ADR)
- Every significant architectural choice must be documented as an ADR in `docs/adr/`.
- Format must include: Title, Status, Context, Decision, Consequences.

## API Documentation
- APIs must be self-documenting via OpenAPI (Swagger) specs.
- Specs are the source of truth and should be generated from code or meticulously maintained alongside it.

## Database Documentation
- The database schema must be documented in a central location or via an automated schema-generation tool.
- Relationships and constraints must be explicitly described.

## Engineering Decisions
- "Why" a specific algorithmic approach or trading logic was chosen belongs in the PRD or feature specification document.

## Changelogs
- Maintain a `CHANGELOG.md` following the Keep a Changelog format.
- Group changes by Added, Changed, Deprecated, Removed, Fixed, and Security.

## Inline Documentation
- Complex business logic inside functions must be preceded by a block comment explaining the mathematical or strategic reasoning.
- Javadoc/Docstring style comments are required for public classes, interfaces, and methods.

## README Format
- Every major subsystem folder should have a localized `README.md` explaining its purpose, how to run it locally, and its dependencies.
