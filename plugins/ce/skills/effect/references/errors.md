# Errors, defects and causes

Read when wrapping promises, callbacks or throwing code, defining or recovering from errors, or inspecting `Exit` and `Cause`.

## Expected failures and defects

Expected failures live in the error channel and say what the caller can do about them. Defects are bugs and broken invariants; let them stay visible. A `throw` inside `Effect.gen`, `Effect.sync` or a `map` callback becomes a defect, and so does `orDie`. Don't use `orDie` to make an inconvenient error disappear from a signature.

`Schema.TaggedError<X>()("X", fields)` gives an error a tag, fields and a codec. Use it when the error crosses an encoded boundary (an HTTP response, a JSON envelope) or the repo requires it. A purely internal error doesn't need a wire schema; `Data.TaggedError` is enough.

Translate a platform or driver error where its domain meaning becomes known (`mapError`, `catchTag`), choosing the tag by what the caller should do next. Report a failure once, at the boundary that owns it, not at every translation.

`mapError` is the default translator: observed in 4.0.6 it is `catchCause` plus `failCause(causeMap(cause, f))`, so it maps the Fail reasons and keeps Die and Interrupt reasons as they are. A hand-built branch over `Effect.exit` that picks one typed error for any failed `Exit` turns defects and interruption into that error; use it only at a boundary that owns all three outcomes.

## Constructors for foreign code

| Source | Constructor | Failure |
| --- | --- | --- |
| Synchronous, can't fail | `Effect.sync(() => ...)` | a throw is a defect |
| Synchronous, can throw as normal operation | `Effect.try({ try, catch })` | your mapped error |
| Promise | `Effect.tryPromise({ try: (signal) => ..., catch })` | your mapped error |
| Promise, shorthand | `Effect.tryPromise((signal) => ...)` | typed `Cause.UnknownError`, not a defect |
| Callback or event source | `Effect.callback((resume, signal) => { ...; return cleanup })` | whatever `resume` receives |

Start the promise inside the thunk. A promise created outside it has already started, can't be cancelled, and won't re-run under `retry`.

Declare the abort signal as a plain parameter, `(signal) => fetch(url, { signal })`. In 4.0 the constructor checks the thunk's `length` and passes a signal only when it's nonzero, so `(...args) => ...`, `(signal = fallback) => ...` and wrappers that forward rest arguments get `undefined`. Interrupting the Effect stops the external work only if the API observes the signal.

The `catch` mapper returns an error; throwing from it is a defect. `Effect.callback`'s returned Effect runs on interruption, so unregister or cancel the source there.

In pure code, `Result.try` is the failure-as-value equivalent of `Effect.try`.

## Recovering

`catch`, `catchTag`, `catchTags`, `catchIf`, `option`, `orElseSucceed`, `ignore` and `match` see typed failures only. `catchCause` receives the whole cause, defects and interruption included, and `ignoreCause` discards it. `catchDefect` handles defects only: a pure interruption passes through it untouched, so it is not a way to recover cancellation. Observed in 4.0.6, on a mixed cause `catchDefect` hands its handler the first defect and drops the Fail and Interrupt reasons that came with it. Choose the operator by the outcomes the boundary owns.

Errors that wrap a nested `reason` (as Effect's own AI and HTTP errors do) are handled with `Effect.catchReason("Parent", "ReasonTag", ...)` and `catchReasons`, which keep the parent error for unmatched reasons. See `ai-docs/src/01_effect/04_errors/20_reason-errors.ts`.

A cause can hold several reasons at once: a failure plus a defect from its finalizer, or a failure plus an interruption. Typed recovery doesn't reduce that to the first reason. Observed in 4.0.6: typed handlers go through `findRecoverableError`, which, when the cause contains any defect, skips the handler and re-raises only the defects, so a mixed Fail and Die cause is never recovered by a typed handler; a failure alongside an interruption still reaches typed handlers. So a `catch` that "always recovers" can still let the operation fail.

Recover only when the substitute is true. `option`, `orElseSucceed` and `ignore` turn every typed failure into the same default, which is right for genuine absence and wrong for "couldn't look". When discovering something, convert the not-found case to an empty result and propagate a permission or unknown failure; reading a file whose absence has a correct default is the same. In a report, keep "unavailable" distinct from zero. A lookup whose fallback fails closed anyway (a missing directory that then refuses the operation) can stay an `option`. Disposable caches and best-effort telemetry may degrade by the repo's stated policy.

A record, warning or fallback produced while handling a failure must not claim success for the failed operation. A finalizer that writes a run record, a status or a metric from the `Exit` has to treat a defect as a failure, not fill in the missing results as passed or skipped.

`Effect.ignore` takes `{ log: true | level, message }` and logs the full cause when it does. Check the repo's logging contract before using it; many forbid serializing causes.

`ignoreCause` discards defects and interruption too. Keep it, and `catchCause`, for a boundary that owns the policy for typed failures, defects and interruption: a log sink, a fallback error envelope, a best-effort telemetry or output subsystem. Handle the reasons that boundary owns and re-raise the rest; ordinary application work doesn't swallow a defect to look successful.

## Inspecting outcomes

`Effect.result` gives a `Result` of the typed failure (`.success`, `.failure`). `Effect.exit` gives an `Exit` with the whole `Cause` (`.value`, `.cause`). Use `result` for a typed branch and `exit` at a boundary that must see defects and interruption.

A `Cause` is a flat list: iterate `cause.reasons` and test each with `Cause.isFailReason`, `Cause.isDieReason`, `Cause.isInterruptReason`; `Cause.hasInterruptsOnly` tells a pure cancellation apart. At a boundary that classifies causes, handle the reasons it owns and re-raise the rest with `Effect.failCause(cause)`.

Built-in error classes worth recognizing: `Cause.UnknownError` (unmapped `try`/`tryPromise`), `Cause.TimeoutError` (`Effect.timeout`), `Cause.NoSuchElementError` (`Effect.fromOption` on `None`).
