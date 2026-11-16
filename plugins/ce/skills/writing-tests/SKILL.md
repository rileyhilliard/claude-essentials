---
name: writing-tests
description: Writes behavior-focused tests using the Testing Trophy model with real dependencies and minimal mocking. Use when writing or reviewing tests, choosing between unit, integration and E2E, deciding what to mock, replacing sleeps with proper waits, fixing flaky tests that fail only alongside other tests, speeding up slow tests that time out under load or on CI, or trimming a suite whose tests repeat each other.
---

If the current repo has its own testing rules or skills (check .claude/rules/ and the repo CLAUDE.md), those take precedence. Apply this skill where they're silent.

# Writing Tests

Test what a user or caller can observe, using real dependencies, so tests survive refactoring and fail only when behavior breaks.

The check for any test: a refactor that improves the code without changing what the app does must leave it passing, so the same test proves the behavior is unchanged before and after. A test that breaks on such a refactor hard-codes or stubs an assumption about the internals, which is the usual failure of unit tests.

## Which kind of test

Most tests should be integration tests written as behavior tests (the Testing Trophy: integration is the widest layer, with fewer unit and E2E tests around it). Enter through an interface a user or caller really uses, such as an HTTP route, a CLI command, a rendered component or a service's public function. Run it against the real database and real internal modules, then assert on the observable result. Name each test for the behavior ("rejects a duplicate email"), not the function it calls.

Integration is the default because it covers the wiring between units, which is where most bugs live, and it survives refactoring because it knows nothing about internals. Isolated unit tests of code with dependencies mostly end up testing the mocks.

Reach for another type only when it fits:

| Type | Use it for | Don't use it for |
| --- | --- | --- |
| Unit | Edge cases a behavior test can't reach, and pure logic (parsers, calculations, validators, state machines) whose input combinations are too many to run through the interface | Cases a behavior test already covers, and anything that needs a mock of your own module to run. Write an integration test instead |
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

## Cover behavior realistically

A behavior test is not only the happy path. Drive the real entry point through the combinations and edge cases real use produces: inputs in the order and shapes callers send them, chained and mixed operations, state left over from an earlier step, failures of the things it depends on, and the near misses it must not get wrong. One realistic flow often exercises what several contrived single-function tests would, and it keeps doing so through a refactor. Give each realistic case its own row so a failure names it.

There are two ways to get a test to the state an edge case starts from:

1. Reproduce the steps a user takes to get there: click the button, fill the form, submit, have the API fail, then check what the UI shows.
2. Set the state up directly: give the component or function the realistic data those steps would have produced (rows in the real database, files on disk, the props a parent would pass), have the API fail, then check what the UI shows.

Prefer the first. It survives a refactor of anything between the entry point and the state, because it knows only what the user does. Use the second when the steps are impractical to replay (they take days of simulated time, or need a system you can't drive), and keep the data as realistic as what the steps would produce.

Reach for a unit-style test only when a behavior test can't reach the edge case either way, or when the combinations of a pure function are too many to run through the interface. Don't add one to repeat what a flow already covers.

Size the suite to the behaviors, not the inputs: one case per rule, branch or contract, plus one near miss per kind of false positive. Rows that run another spelling of the same input down the same path, or repeat every case across an independent dimension, add cost and make the behavior expensive to change. Before trimming a suite, prove each deleted test is redundant by breaking the code and its config one rule at a time and checking something still fails; [references/test-value.md](references/test-value.md) has the method.

## Keep tests fast

A slow test is a flaky test waiting for a busy machine: the suite runs in parallel on small CI runners, and a test that takes seconds alone times out there. Write each test so its cost is what it asserts and nothing more:

- Set up only what the test reads. Share read-only fixtures across tests; copy a fixture only when the test mutates it.
- Make fakes return valid responses unless the test is about the failure, so the code's retry and backoff never run by accident.
- Call code in-process; spawn a process only when the process boundary is the behavior under test.
- Test a shared artifact (a template, a wrapper, a config shape) once, not once per consumer of it.
- Give each slow case its own row, and size any explicit timeout from the work it covers.
- Wait for every child process and server a test starts before its cleanup runs.

Check the cost when you add tests: run the file with per-test durations shown and look at the slowest. [references/slow-tests.md](references/slow-tests.md) has the patterns in detail and how to catch them in the suite.

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
| How many tests a behavior needs, trimming a suite that repeats itself, sharding a slow one | [references/test-value.md](references/test-value.md) |
