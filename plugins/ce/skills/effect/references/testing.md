# Testing Effect code

Read when writing tests with `@effect/vitest`, controlling time, or asserting failures. General testing philosophy belongs to the repo's testing rules and `writing-tests`; this covers the Effect mechanics. Examples: `ai-docs/src/09_testing/10_effect-tests.ts` and `20_layer-tests.ts`.

## Test helpers

`it.effect(name, () => Effect.gen(...))` runs the test in a scope with the test services: `TestClock` and, observed in 4.0, `TestConsole`. So `Console.log` output under `it.effect` is captured rather than printed; a test that expects terminal output, or a helper that relies on framework help printing through `Console`, needs `it.live` or its own Console. `it.live` uses the live clock and console. `it.effect` also supplies a `Scope`, so finalizers run when the test ends.

`it.prop` and `it.effect.prop` take schemas (or arbitraries) as generators.

`layer(L)(...)` (and `it.layer`) builds `L` once and shares it across every test in the block. That suits an expensive, stateless fixture. For a stateful service, build a fresh layer in each test so state can't leak between them.

`@effect/vitest` versions peer a specific Vitest major; check its `package.json` before upgrading either.

## Virtual time

Fork the work that sleeps, advance the clock, then join (illustrative; `program` and `expected` come from the test):

```ts
it.effect("retries after a minute", () =>
  Effect.gen(function* () {
    const fiber = yield* Effect.forkChild(program)
    yield* TestClock.adjust("1 minute")
    const result = yield* Fiber.join(fiber)
    assert.strictEqual(result, expected)
  }))
```

`TestClock` comes from `effect/testing`. It controls only the runtime that received the test services. A separately started runtime, HTTP server, child process or `ManagedRuntime` uses live time, so a request to a real server inside the test isn't driven by `TestClock.adjust`. Where real I/O is involved, wait on an observed condition (a log line, a response, a port) instead of sleeping for a guessed duration.

## Asserting outcomes

Assert expected failures as values: `const exit = yield* Effect.exit(program)` then check `Exit.isFailure` and the reasons in `exit.cause.reasons` (or `Effect.flip` for the typed error alone). Defects, interruption and finalizer failures show up only in the `Cause`, so test cleanup on failure and cancellation through `Exit` when the code owns resources.

## Configuration and services in tests

Give tests an explicit config provider (`ConfigProvider.fromUnknown({...})` or `fromEnvRecord({...})` through `ConfigProvider.layer`) so they never read the developer's environment. Replace a service with a test layer only for things the test can't own (a third-party API, the wall clock); a real implementation over a temporary resource tests more.

Dispose what a helper creates, from inside the helper, with Vitest's `onTestFinished` (a web handler's `dispose`, a scope's `close`).
