---
name: writing-tests
description: Writes behavior-focused tests using the Testing Trophy model with real dependencies and minimal mocking. Use when writing or reviewing tests, choosing between unit, integration and E2E, deciding what to mock, replacing sleeps with proper waits, fixing flaky tests that fail only alongside other tests, or speeding up slow tests that time out under load or on CI.
---

If the current repo has its own testing rules or skills (check .claude/rules/ and the repo CLAUDE.md), those take precedence. Apply this skill where they're silent.

# Writing Tests

Test what a user or caller can observe, using real dependencies, so tests survive refactoring and fail only when behavior breaks.

## Which kind of test

Most tests should be integration tests written as behavior tests (the Testing Trophy: integration is the widest layer, with fewer unit and E2E tests around it). Enter through an interface a user or caller really uses, such as an HTTP route, a CLI command, a rendered component or a service's public function. Run it against the real database and real internal modules, then assert on the observable result. Name each test for the behavior ("rejects a duplicate email"), not the function it calls.

Integration is the default because it covers the wiring between units, which is where most bugs live, and it survives refactoring because it knows nothing about internals. Isolated unit tests of code with dependencies mostly end up testing the mocks.

Reach for another type only when it fits:

| Type | Use it for | Don't use it for |
| --- | --- | --- |
| Unit | Pure logic with no I/O or dependencies: parsers, calculations, formatters, validators, state machines. It pays off when many input combinations are cheap to run | Anything that needs a mock of your own module to run. Write an integration test instead |
| E2E / acceptance | A handful of critical journeys (sign-up, checkout, login) through the deployed stack in a real browser, and behavior only the full stack shows: browser quirks, deployment wiring, third-party redirects | Edge cases and error branches. Cover those at the integration level, where tests are faster and less flaky |

When unsure, write the integration test.

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
| Slow tests, or tests that time out only under load or on CI | [references/slow-tests.md](references/slow-tests.md) |
