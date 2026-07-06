# Code Organization Rules

To ensure readability and prevent monolithic anti-patterns, the codebase is governed by strict size and organization limits.

## Size Constraints
- **Maximum file size:** 400 lines of code. If a file grows larger, it is likely violating the Single Responsibility Principle and must be broken down.
- **Maximum function size:** 50 lines of code. Functions should perform a single logical operation.
- **Maximum class responsibility:** 1 Core responsibility. Classes with "Manager", "Helper", or "Util" in their names are red flags and should be heavily scrutinized.

## Import Ordering
Imports must be structured cleanly and predictably:
1. Standard Library / Built-in packages.
2. Third-party packages.
3. Internal project modules (absolute paths preferred).
4. Relative imports (same directory / children).
- Blank lines should separate these groups.

## Ownership Rules
- **Folder ownership:** Every top-level feature module must have a clear, documented purpose. Files belong in the folder of the feature they primarily support.
- **Dependency ownership:** External dependencies must be explicitly justified. Do not add a library if a small, maintainable function can solve the problem natively.

## Code Comments & Documentation Policy
- Code must be written to be self-documenting via clear variable and function naming.
- Inline comments explain **WHY** something is done, not **WHAT** is done.
- Avoid obvious comments (e.g., `// Add 1 to x`).
- Complex algorithms or business rules MUST include an explanatory comment referencing the design document.

## Code Lifecycle Policies
- **Deprecation policy:** Before removing an API, function, or field, it must be marked with a `@deprecated` tag and logged for a minimum of one release cycle.
- **Dead code policy:** Dead code (unused functions, unreachable logic, commented-out blocks) must be deleted immediately. Do not keep it "just in case" – that is what Git history is for.
- **Experimental code policy:** Experimental features must be explicitly guarded behind feature flags. They must not affect standard execution paths.
- **Temporary code policy:** Temporary code is strictly prohibited in `main` and `develop`. There are no "hacks" or "TODOs" allowed in production code.
