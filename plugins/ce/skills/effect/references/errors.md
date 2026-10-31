# Errors, defects and causes

Read when wrapping promises, callbacks or throwing code, defining or recovering from errors, or inspecting `Exit` and `Cause`.

## Expected failures and defects

Expected failures live in the error channel and say what the caller can do about them. Defects are bugs and broken invariants; let them stay visible. A `throw` inside `Effect.gen`, `Effect.sync` or a `map` callback becomes a defect, and so does `orDie`. Don't use `orDie` to make an inconvenient error disappear from a signature.

`Schema.TaggedError<X>()("X", fields)` gives an error a tag, fields and a codec. Use it when the error crosses an encoded boundary (an HTTP response, a JSON envelope) or the repo requires it. A purely internal error doesn't need a wire schema; `Data.TaggedError` is enough.

Translate a platform or driver error where its domain meaning becomes known (`mapError`, `catchTag`), choosing the tag by what the caller should do next. Report a failure once, at the boundary that owns it, not at every translation.

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

`catch`, `catchTag`, `catchTags`, `catchIf`, `orElseSucceed` and `ignore` see typed failures only. `catchCause`, `ignoreCause` and `catchDefect` also see defects and interruption.

Errors that wrap a nested `reason` (as Effect's own AI and HTTP errors do) are handled with `Effect.catchReason("Parent", "ReasonTag", ...)` and `catchReasons`, which keep the parent error for unmatched reasons. See `ai-docs/src/01_effect/04_errors/20_reason-errors.ts`.

A cause can hold several reasons at once: a failure plus a defect from its finalizer, or a failure plus an interruption. Typed recovery doesn't reduce that to the first reason. Observed in 4.0: when the cause contains a defect, typed handlers are skipped and the typed errors are converted to defects; a failure alongside an interruption still reaches typed handlers. So a `catch` that "always recovers" can still let the operation fail.

`Effect.ignore` takes `{ log: true | level, message }` and logs the full cause when it does. Check the repo's logging contract before using it; many forbid serializing causes.

`ignoreCause` discards defects and interruption too. Keep it for best-effort work whose loss can't change the result (writing to a log sink, a fallback error envelope).

## Inspecting outcomes

`Effect.result` gives a `Result` of the typed failure (`.success`, `.failure`). `Effect.exit` gives an `Exit` with the whole `Cause` (`.value`, `.cause`). Use `result` for a typed branch and `exit` at a boundary that must see defects and interruption.

A `Cause` is a flat list: iterate `cause.reasons` and test each with `Cause.isFailReason`, `Cause.isDieReason`, `Cause.isInterruptReason`; `Cause.hasInterruptsOnly` tells a pure cancellation apart. At a boundary that classifies causes, handle the reasons it owns and re-raise the rest with `Effect.failCause(cause)`.

Built-in error classes worth recognizing: `Cause.UnknownError` (unmapped `try`/`tryPromise`), `Cause.TimeoutError` (`Effect.timeout`), `Cause.NoSuchElementError` (`Effect.fromOption` on `None`).
