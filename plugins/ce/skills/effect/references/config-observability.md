# Config, logging and tracing

Read when adding settings, reading environment variables, installing or changing a logger, or adding annotations and spans. Examples: `ai-docs/src/08_observability/10_logging.ts` and `20_otlp-tracing.ts`.

## Config

Config constructors are capitalized: `Config.String`, `Config.Int`, `Config.Number`, `Config.Boolean`, `Config.Port`, `Config.Literals`, `Config.LogLevel`, `Config.Redacted`, combined with `Config.all`, `Config.withDefault`, `Config.option`, and `Config.schema(S, name)` for a value decoded by a schema. Keep them in one module so every setting has one reader.

A `ConfigProvider` supplies values and is installed with `ConfigProvider.layer(provider)` at the composition boundary: `ConfigProvider.fromEnv()` in the process entry, `fromEnvRecord({...})` or `fromUnknown({...})` in tests so they never see the developer's environment. Observed in 4.0: an empty string is treated as missing unless the provider is built with `{ preserveEmptyStrings: true }`, so `FOO=` falls through to a default.

Secrets are `Redacted` values (`Config.Redacted`); `Redacted.value` unwraps one only where the integration needs the raw string, and logging a `Redacted` prints a placeholder.

When the config must be decoded lazily (a broken settings file shouldn't stop a diagnostic command from running), read it inside the command that needs it rather than in a layer every command builds.

## Logging

Log with `Effect.logInfo`, `logWarning`, `logError`, `logDebug`, and attach structured fields with `Effect.annotateLogs({ key: value })`, which applies to everything inside the wrapped effect. Spans come from `Effect.fn("name")` and `Effect.withSpan("name", { attributes })`; keep span names fixed and put the variable part in attributes.

`Logger.make((options) => ...)` builds a logger; in 4.0 the options carry `date`, `logLevel`, `message`, `cause` and `fiber`. Annotations are read with `fiber.getRef(References.CurrentLogAnnotations)`; the threshold is `References.MinimumLogLevel`. `Logger.layer([logger])` replaces the default loggers rather than adding to them. Log levels are title case inside Effect (`"Info"`), which a JSON logger may want to lowercase.

`message` and `cause` can hold arbitrary values, including user input and error messages; a logger with a privacy contract builds its record from an allowlist instead of serializing them. Note that `Effect.ignore({ log: true })` and the default unhandled-error logging hand the full `Cause` to the logger.

A logger callback is synchronous inside the fiber. Hand the work to something the logger already owns (a queue drained by a service, a captured file handle); never start a new runtime or `Effect.runPromise` from inside it.

Install loggers and tracing exporters once, at the application's entry or runtime, never inside a library layer.

`ErrorReporter` (unstable) with `Effect.withErrorReporting` forwards non-interruption causes to a monitoring callback; check its module docs before adopting it.
