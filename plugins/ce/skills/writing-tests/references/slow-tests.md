# Slow Tests

For tests that are slow, or that pass alone and time out when the suite runs on a busy machine or a 2-core CI runner. A timeout under load is usually a test doing more work than it needs, so the fix is to remove the work, not to raise the timeout.

## Measure under load first

A test that takes 2 seconds alone can take 15 inside a parallel suite on a small runner. Time the test alone, then again with the CPU busy (its file together with a heavy file, more workers than cores, or a few busy-loop processes), and find where the seconds go: process startup, fixture setup, network fakes, or the code under test.

## Patterns that make tests slow

| Pattern | What it costs | Instead |
| --- | --- | --- |
| Copying a whole fixture tree (a data directory, a registry, a repo) for a test that reads one entry | I/O that grows with the fixture, per test | Build or copy only what the test touches. Share a read-only fixture across tests in `beforeAll`; give a test its own copy only when it mutates it |
| A fake that returns invalid data, so the code under test retries with real backoff | Seconds of sleeping per test, invisible in the assertions | Make the fake return a valid response unless the test is about the failure. When it is, inject the clock or set the retry delay to zero |
| Spawning a process to call code the test could call in-process | Interpreter or binary startup, every call | Call the entry point in-process. Spawn only when the process boundary is what's under test (signals, exit codes, a fresh process's state), and once per test, not once per assertion |
| A matrix that tests the same artifact once per consumer (every service that uses a shared wrapper, every stack that ships the same hook) | Rows that grow with the number of consumers while testing nothing new | Deduplicate by the artifact: one row per distinct template, script or config shape, plus the cases where a consumer differs |
| Many slow operations in a loop inside one test | One timeout shared by all of them; the failure doesn't say which case broke | One row per case (`test.each`, `pytest.mark.parametrize`), so each has its own timeout and a failure names its case |
| A fixed timeout unrelated to the work, on a test whose cost grows with its data | It passes until the data grows past it, then fails as a "flake" | Derive the timeout from the work: if the test allows a budget per run and runs it three times, its timeout is three budgets plus slack |
| Cleanup that deletes a temp directory while a child process is still writing | Intermittent `ENOTEMPTY` or missing-file errors in teardown | Track every child the test starts and wait for it to exit before cleanup |
| A process under test that exits before reading its stdin while the test writes to it | Intermittent `EPIPE` in the test's write, worse with large payloads | Have the program drain stdin on every exit path; test it with an input larger than a pipe buffer (256 KiB) |

## Catching them before they flake

Slow tests rarely fail on the day they're written; they fail weeks later on a loaded runner. Make cost visible so it's caught when the test lands:

- Show per-test durations in the normal run and read the slowest few after adding tests: Vitest flags tests over `slowTestThreshold` (set it, e.g. 300 ms, in the config), Jest has `--verbose` and `slowTestThreshold`, pytest has `--durations=10`, Go has `go test -v` timings.
- Keep the default per-test timeout short (5 s or less) so an expensive test has to declare its timeout and its reason, rather than hiding inside a generous global default.
- When adding a test file, compare the suite's wall time before and after. A file that adds more than a few seconds needs the patterns above checked.
- In review, treat a raised timeout, a `beforeAll` that copies a large tree, a fake with retries enabled, or a test that spawns a process per case as a finding to justify, the same as a skipped assertion.
- For the inherently slow tests, assert a budget where the cost is the point (a CPU or wall-time budget derived from the input size), so growth fails a named test instead of turning into timeouts elsewhere.

## When a long timeout is right

Some tests are slow by nature: a full build, a real database migration, an end-to-end run. Keep them, give each an explicit timeout sized from a measurement under load (about three times the loaded duration), and say in a one-line comment what it runs and why it takes that long. A bare raised timeout with no measurement hides the next regression.

## Confirming the fix

Report the test's duration before and after, alone and under load, and run it several times in the configuration that failed. A test that went from 3 seconds to 0.4 no longer depends on the machine being idle.
