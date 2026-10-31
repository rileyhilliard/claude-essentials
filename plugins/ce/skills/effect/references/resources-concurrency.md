# Resources, fibers, state and time

Read when acquiring resources, forking work, keeping state or caches in a service, adding timeouts or retries, or reading time and randomness.

## Contents

- Scopes and acquisition
- Fibers: lifetime versus observation
- State and caching
- Timeouts, retries and schedules
- Time, randomness and ids

## Scopes and acquisition

Acquire a resource inside the scope that owns its lifetime: `Effect.acquireRelease(acquire, (value, exit) => release)` or `Effect.addFinalizer((exit) => ...)`, closed by `Effect.scoped` or by the layer that built it. JavaScript `Disposable`/`AsyncDisposable` objects go through `Effect.acquireDisposable`.

The release is registered only after `acquire` succeeds. For acquisition in several stages, acquire each stage with its own `acquireRelease` so an earlier stage is released when a later one fails; one release attached after the whole acquisition can't undo a half-finished one. Partial work inside a single stage must be undone by that stage before it fails.

Acquisition is uninterruptible by default, so keep it short; `acquireRelease(acquire, release, { interruptible: true })` allows interruption when partial acquisition is safe. `Effect.uninterruptibleMask((restore) => ...)` protects a short transition (registering ownership, settling output) while `restore(...)` keeps the ordinary work inside it cancellable.

Release runs on every exit. Rollback is a release that reads `exit` and undoes only on failure or interruption; a successful commit must not trigger it.

## Fibers: lifetime versus observation

Prefer combinators that own their fibers: `Effect.all`, `Effect.forEach` with `{ concurrency }`, `Effect.race`, `raceAll`. Fork only for work that runs alongside the current fiber.

| Fork | Owner |
| --- | --- |
| `Effect.forkChild` | the current fiber; interrupted when it ends |
| `Effect.forkScoped` | the `Scope` in context |
| `Effect.forkIn(scope)` | an explicitly chosen scope |
| `Effect.forkDetach` | nobody; needs a deliberate application-level owner |
| `FiberSet.run`, `FiberMap.run(key)`, `FiberHandle.run` | a scoped collection; `FiberMap` and `FiberHandle` replace the previous fiber for the same key |

Ending a fiber's scope stops it from leaking. It does not make its failure reach anyone: a forked fiber that fails while its owner stays alive fails silently. `Fiber.join` re-raises the failure in the joiner; `Fiber.await` returns the `Exit` for the owner to inspect. A background worker ends in a cause-level handler that reports the failure and decides whether to stop or restart. Work that outlives an HTTP response is forked into an application scope, not the request's.

## State and caching

Allocate mutable state when the layer is built, so its lifetime matches the service's. Module-level `let`, `Map` or arrays outlive every layer and leak between tests and invocations.

A closure variable is fine for synchronous updates. `Ref` gives atomic pure updates (`Ref.update`, `modify`). When a read-modify-write step includes effects that can interleave, use `SynchronizedRef.modifyEffect` or a `Semaphore` (`Semaphore.make(1)`, `withPermits(1)`), and don't hold the permit across unrelated work.

`Effect.cached(effect)` returns an effect that runs once and replays its `Exit` (observed in 4.0):

- Failures and defects are cached for the cache's lifetime. A transient failure during initialization stays failed. `Effect.cachedWithTTL(effect, (exit) => duration)` can pick the TTL from the outcome, for example zero for failures; `cachedInvalidateWithTTL` adds manual invalidation.
- Interruption is never cached; the next call starts a fresh run.
- Concurrent callers share the in-flight run, which is interrupted only when every waiting caller has been.
- The body runs in the first caller's context: that caller's services, log annotations and clock. Later callers get that result, even if they provided different services. Don't cache a computation that reads request-scoped services; resolve them before caching or keep them as arguments.

Allocate the cached effect once, in the owner's constructor. Calling `Effect.cached` inside a method creates a new cache per call.

For keyed caches with capacity and TTL, use `Cache` or `ScopedCache`; for reference-counted keyed resources, `RcMap`.

## Timeouts, retries and schedules

`Effect.timeout(d)` interrupts the source when the timer wins and fails with `Cause.TimeoutError` (`timeoutOption` and `timeoutOrElse` return instead). Interruption is cooperative: uninterruptible regions and finalizers can delay it, and foreign work stops only if it observes its abort signal.

Placement decides the budget:

```ts
attempt.pipe(Effect.retry(policy), Effect.timeout("2 seconds")) // attempts and waits share one budget
attempt.pipe(Effect.timeout("500 millis"), Effect.retry(policy)) // each attempt gets its own; the policy must decide whether TimeoutError is retryable
```

`Effect.retry` takes a `Schedule` or `{ times, schedule, while, until }`. With `times: n` the effect runs up to n + 1 times. `Schedule.upTo({ times, duration })` bounds a schedule; its duration is checked between attempts, so it doesn't interrupt an attempt in progress.

Schedule constructors in 4.0: `exponential`, `fibonacci`, `spaced`, `fixed`, `recurs`, `forever`, `once`, `during`, `windowed`, `cron`, plus `jittered`, `upTo`, `while`, `addDelay`, `modifyDelay`. Effect 3's `intersect`/`both` is `Schedule.max` (continue while all continue, longer delay) and `union`/`either` is `Schedule.min` (while any continues, shorter delay). Examples: `ai-docs/src/06_schedule/10_schedules.ts`.

Retry an operation only when repeating it is safe; for HTTP, see `retryTransient` in http.md.

## Time, randomness and ids

Read the current time through `Clock` (`Clock.currentTimeMillis`, `DateTime.now`), wait with `Effect.sleep`, and draw random values from `Random`, so `TestClock` and seeded randomness control them in tests. `Date.now()`, `new Date()`, `setTimeout` and `Math.random()` bypass that. Use `DateTime` over `Date` for parsing, formatting and zones (`ai-docs/src/07_datetime/`).

Effect 4 has a `Crypto` service (unstable) with `randomUUIDv4`, `randomUUIDv7`, `randomBytes` and `digest`, supplied by the platform layer (`NodeServices` provides it) and by `TestCrypto` from `effect/testing`. Without a provided implementation, yielding it fails.
