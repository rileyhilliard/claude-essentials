---
name: writing-tests
description: Writes behavior-focused tests using the Testing Trophy model with real dependencies and minimal mocking. Use when writing or reviewing tests, choosing between unit, integration and E2E, deciding what to mock, replacing sleeps with proper waits, or fixing flaky tests that fail only alongside other tests.
---

If the current repo has its own testing rules or skills (check .claude/rules/ and the repo CLAUDE.md), those take precedence. Apply this skill where they're silent.

# Writing Tests

Test what a user or caller can observe, using real dependencies, so tests survive refactoring and fail only when behavior breaks.

## Which kind of test

| Situation | Test type |
| --- | --- |
| Most code: several units working together | Integration, with a real test database and real internal modules |
| A complete user workflow | E2E |
| A pure function with no side effects | Unit |

Integration is the default because it gives the most confidence per test. Isolated unit tests of code with dependencies usually end up testing the mocks.

## Mocking

Mock only what you don't own or can't control: external HTTP APIs, third-party services (payments, email), time and randomness. Use the real database, real internal modules and real business logic. When a mock is needed, make it match the real API's shape, including error responses.

## Assertions

| Context | Assert on | Not on |
| --- | --- | --- |
| UI | Visible text, roles, labels | CSS classes, component state |
| API | Status and response body | Rows in the database behind it |
| Library | Return values and raised errors | Private methods |

## Anti-patterns

| Pattern | Instead |
| --- | --- |
| Asserting a mock was called | Assert the outcome the call produced |
| Test-only methods in production code | Put helpers in test utilities |
| `sleep(500)` before an assertion | Wait for the condition (`findBy`, `waitFor`, Playwright auto-wait, polling helpers) |
| Asserting internal state | Assert observable output |

Name tests after the behavior they check, and cover the error paths as well as the happy path.

## References

| Need | Read |
| --- | --- |
| TypeScript and React (Testing Library, MSW, Vitest/Jest) | [references/typescript-react.md](references/typescript-react.md) |
| Python (pytest, fixtures, async) | [references/python.md](references/python.md) |
| Go | [references/go.md](references/go.md) |
| Async waiting in TypeScript | [references/waiting-typescript.md](references/waiting-typescript.md) |
| Async waiting in Python | [references/waiting-python.md](references/waiting-python.md) |
| Tests that pass alone and fail in the suite, or fail intermittently | [references/flaky-tests.md](references/flaky-tests.md) |
