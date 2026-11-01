# Rust Error Handling

Rust conventions that are easy to miss when the code compiles and the tests pass. The
basics (`?`, `Result`, thiserror for libraries, anyhow for applications, no `unwrap` in
production paths) are assumed.

## Contents

- [Display or source, not both](#display-or-source-not-both)
- [A `#[from]` per operation, not per error type](#a-from-per-operation-not-per-error-type)
- [Logging keeps the chain](#logging-keeps-the-chain)
- [Silent discards](#silent-discards)
- [Panics at boundaries](#panics-at-boundaries)
- [Public error types](#public-error-types)

## Display or source, not both

An error's `Display` describes its own failure. The cause goes in `source()`. Reporters
(anyhow's `{:#}`, `tracing`, eyre) walk the chain and print each layer's `Display`, so a
message that also embeds the cause prints it twice:

```rust
// Bad: `{0}` repeats the source that #[from] also exposes
#[error("io error: {0}")]
Io(#[from] io::Error),
// anyhow {:#} prints: loading config: io error: disk gone: disk gone

// Good: the variant adds meaning, the cause stays in source()
#[error("reading {path}")]
Read { path: PathBuf, #[source] source: io::Error },

// Good: the variant adds nothing, so it forwards Display and source() unchanged
#[error(transparent)]
Other(#[from] Box<dyn Error + Send + Sync + 'static>),
```

Messages follow std style: lowercase, no trailing period, no "failed to" (the reporter
already says it is an error).

## A `#[from]` per operation, not per error type

`#[from] io::Error` lets `?` turn every I/O failure in the crate into the same variant,
so "opening the socket" and "writing the cache" become indistinguishable, and the path is
gone. Prefer one variant per operation that carries its inputs, built with `map_err` at
the call site:

```rust
std::fs::read_to_string(&path).map_err(|source| LoadError::Read { path, source })?;
```

Keep `#[from]` for a wrapped error whose meaning doesn't depend on where it happened
(a whole sub-operation's error type, or `transparent` forwarding). Define error types
next to the operations that return them, one per operation or group of operations that
fail the same way, rather than one crate-wide `Error` enum every function returns.

## Logging keeps the chain

The common forms drop everything below the top layer:

| Form | Prints |
| --- | --- |
| `tracing::warn!(error = %e)` | top `Display` only |
| `format!("{e}")` on `anyhow::Error` | outermost context only |
| `format!("{e:#}")` on `anyhow::Error` | full chain, `: `-separated |
| `format!("{e:?}")` on `anyhow::Error` | full chain plus backtrace, multi-line |
| `tracing::warn!(error = &e as &dyn Error)` | `error=... error.sources=[...]` with `tracing-subscriber`'s fmt layer |

Record errors in `tracing` as `&dyn Error` (for anyhow, `&*e as &dyn Error`, since
`anyhow::Error` doesn't implement `Error` itself). Use `{:#}` when formatting anyhow into
a string, a UI message or a `CommandError`.

## Silent discards

`.ok()`, `let _ =`, `.unwrap_or_default()` and `if let Ok(..)` without an `else` all
discard the error with no trace. Use them only where the failure changes nothing
(best-effort cleanup, a send to a receiver that may be gone), and log otherwise.
`Result::inspect_err` logs without consuming the value:

```rust
let cfg = load(path)
    .inspect_err(|e| tracing::warn!(error = e as &dyn Error, "using defaults"))
    .unwrap_or_default();
```

Spawned work hides failures too:

- A `tokio::spawn`ed task that panics or returns `Err` reports it only through its
  `JoinHandle`. Dropping the handle (or never awaiting it) loses both. Hold the handle or
  use a `JoinSet`, and check `JoinError::is_panic()`.
- `std::thread::spawn` is the same: `join()` returns `Err` with the panic payload.
- A `Mutex` whose holder panicked is poisoned, and `.lock().unwrap()` then panics in every
  later caller. Decide deliberately: propagate, or recover with
  `.unwrap_or_else(PoisonError::into_inner)` when the guarded data stays valid.

## Panics at boundaries

- A panic that unwinds out of an `extern "C"` function aborts the process (guaranteed
  since Rust 1.81). Callbacks handed to C (IOKit, SQLite hooks, signal handlers) wrap
  their body in `std::panic::catch_unwind` and turn a panic into an error code.
- `catch_unwind` does nothing under `panic = "abort"`; check the release profile before
  relying on it.
- `.expect()` messages state the expectation, not the failure:
  `.expect("config is loaded before the server starts")`, not `.expect("failed to get config")`.
  The panic output already says it failed.
- `fn main() -> Result<(), E>` prints `E`'s `Debug` on error. With a derived `Debug` that
  is a struct dump; return `anyhow::Result<()>` (which prints the chain) or handle the
  error and return an `ExitCode`.

## Public error types

These apply to crates other people depend on, where changing the error type is a semver
break:

- Mark public error enums and structs `#[non_exhaustive]` so adding a variant or field
  isn't breaking.
- Don't put a dependency's error type in a public variant (`#[from] reqwest::Error`);
  upgrading the dependency then breaks your API. Wrap it in your own type or store it as
  `Box<dyn Error + Send + Sync + 'static>`.
- Boxed errors need `Send + Sync + 'static`. Plain `Box<dyn Error>` can't cross threads,
  can't be held across an `.await` in a `Send` future, and won't convert into
  `anyhow::Error`.
- Box large variants. `Result<T, E>` is at least as big as `E`, so one big variant
  inflates every return on the happy path; `clippy::result_large_err` flags errors over
  128 bytes.
