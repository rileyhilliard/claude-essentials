# DX Friction Investigation

Investigate what makes the codebase harder to work in than it needs to be. This covers friction the agent hit, but also friction that any developer (or future agent session) would encounter. The goal is identifying things that could be smoother through better tooling, automation, refactoring, or conventions.

## What to Look For

**Discovery friction** - Hard to find what you need:
- Searched in wrong directories or files
- Didn't know where a type of code lives (services? utils? helpers?)
- Couldn't find existing utilities and reinvented something
- File or function names didn't communicate their purpose

**Convention friction** - Unwritten rules that trip people up:
- Used a pattern that doesn't match the rest of the codebase
- Named things inconsistently with existing conventions
- Put code in the wrong layer or module
- Used the wrong abstraction level

**Observability friction** - Poor feedback from the system:
- Missing or unhelpful log messages (no context about what failed or why)
- Confusing log output (wall of text, no structure, hard to grep)
- Logs missing easily-added context (request ID, user ID, operation name)
- No logging at critical decision points (silent failures)
- Poorly formatted error messages that don't help with debugging
- Missing health checks or status endpoints

**API friction** - Interfaces that confuse or mislead:
- Endpoints that don't follow REST conventions (wrong HTTP verbs, inconsistent URL patterns)
- Confusing request/response shapes (nested where flat would work, inconsistent naming)
- Missing or wrong API documentation (spec doesn't match implementation)
- No input validation feedback (400 errors with no detail about what's wrong)
- Inconsistent error response formats across endpoints

**Unnecessary manual steps** - Things that took N steps but could take fewer:
- Manual type definitions that could be auto-generated from a spec (e.g., Orval, openapi-typescript)
- Hand-written API clients when codegen is available
- Manual format/lint fixes that a pre-commit hook or editor config would handle
- Copy-paste patterns that should be a shared utility or abstraction
- Manual environment setup steps that could be scripted
- Repeated test boilerplate that could be a fixture or factory

**Missing automation** - Friction that tooling could eliminate:
- No auto-formatting (developers waste time on style decisions)
- No type generation from API specs (frontend writes non-compliant API calls)
- No CI checks for common issues (bugs ship that linting would catch)
- No database migration tooling (manual schema changes)
- No code generation for boilerplate (repetitive files created by hand)

**Tooling friction** - Fighting the toolchain:
- Pre-commit hooks caught issues that should have been prevented earlier
- Build/test commands were wrong or needed flags the agent didn't know about
- Environment setup was missing or undocumented
- Dependencies missing or version-mismatched without clear error messages

**Onboarding and setup friction** - Time-to-first-commit:
- Clone-to-running takes too many manual steps (should be clone, configure, run)
- Missing or outdated setup instructions
- Environment dependencies not documented (required services, env vars, tools)
- No seed data or fixtures for local development
- No emulators or mocks for external service dependencies

**Feedback loop friction** - Slow iteration cycles:
- Build times that break flow state (waiting > 10s for feedback)
- Test suite too slow to run frequently during development
- CI pipeline takes too long for reasonable iteration
- No watch mode for local development (manual restart after every change)
- Deployment takes too long to verify changes in a realistic environment

**Cognitive load friction** - Too much context required:
- Making a small change requires understanding distant parts of the system
- Implicit dependencies between modules (changing A breaks B with no obvious connection)
- Configuration scattered across multiple files and formats
- No single source of truth (same information in multiple places, potentially conflicting)
- Cross-cutting concerns (auth, logging, error handling) implemented differently everywhere

**Technical debt drag** - Accumulated friction from deferred work:
- Workarounds that everyone knows about but nobody fixes
- TODO/FIXME/HACK comments that have been there for months
- Deprecated patterns still in use alongside their replacements
- Dead code that makes searching and understanding harder
- Dependencies with known vulnerabilities or end-of-life status

## Root Cause Questions

For each friction point:
1. Is there a convention that exists but isn't documented in CLAUDE.md or a skill?
2. Is the project structure self-documenting, or does it require tribal knowledge?
3. Could a session-start hook have provided the missing context?
4. Could a tool, library, or framework eliminate this friction automatically?
5. Is this a one-time annoyance or something that will bite every session?
6. How many steps did this take vs how many should it have taken?
7. Does this hurt feedback loop speed? Could caching, parallelism, or watch mode help?
8. How much unrelated context did you need to hold in your head for this change?

## Typical Actions

**Automation and tooling (highest leverage):**
- Add codegen for types/clients from API specs (Orval, openapi-typescript, etc.)
- Add pre-commit hooks for formatting and linting
- Add editor configs (`.editorconfig`, `.prettierrc`) so formatting is automatic
- Script environment setup steps
- Add shared test fixtures/factories to reduce boilerplate

**Observability improvements:**
- Add structured logging with context (request ID, operation, duration)
- Improve error messages to include what was expected vs what was received
- Add log levels appropriately (debug vs info vs error)
- Add health check endpoints

**API improvements:**
- Align endpoints with REST conventions
- Standardize error response format across the API
- Add input validation with descriptive error messages
- Generate and publish API specs (OpenAPI)

**Feedback loops and iteration speed:**
- Add watch mode for local development (nodemon, air, watchfiles)
- Parallelize or cache slow test suites
- Split tests into fast unit vs slower integration tiers
- Add hot reload for frontend development
- Optimize CI pipeline (parallelize stages, cache dependencies)

**Reducing cognitive load:**
- Colocate related code (feature folders over type folders)
- Make dependencies explicit (dependency injection, imports over globals)
- Consolidate configuration into fewer files
- Standardize cross-cutting concerns (one way to do auth, logging, errors)
- Document the "why" for non-obvious architectural decisions

**Technical debt cleanup:**
- Audit and address long-standing TODO/FIXME comments
- Remove dead code and unused dependencies
- Migrate deprecated patterns to current conventions
- Update vulnerable or end-of-life dependencies

**Documentation and conventions:**
- Add project conventions to CLAUDE.md (naming, file placement, patterns)
- Add common commands to CLAUDE.md (test commands, build commands, lint flags)
- Update session-start hook to inject project-specific context
- Rename files/directories to be more self-documenting
- Add barrel exports or index files to make discovery easier
- Document setup steps as a script, not just a README list
