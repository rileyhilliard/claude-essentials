---
name: effect
description: Writes and reviews Effect v4 TypeScript code against the installed release instead of remembered Effect 3 APIs. Use when changing Effect services, layers, errors, schemas, resources, fibers, retries, config, logging, HttpApi or HttpClient, SQL, effect/cli commands or @effect/vitest tests.
---

If the current repo has its own Effect rules (check .claude/rules/, AGENTS.md and CLAUDE.md), those take precedence. Apply this skill where they're silent.

# Effect 4

This skill covers Effect 4 patterns and the traps that models carry over from Effect 3. Where it states a default or a behavior of a specific API, that was observed in 4.0 and is marked so: confirm it in the installed source before relying on it, because minor releases change defaults and unstable modules. A new major needs a fresh review of this skill.

## Where the truth is

Start from Effect's own agent guide, which ships inside the package at `node_modules/effect/AGENTS.md` (resolved from the workspace package you're changing). It's the official entry point: house style for `Effect.gen`, `Effect.fn` and services, plus a topic index that links one runnable example per topic under `node_modules/effect/ai-docs/src/`. It matches the installed release, so it doesn't go stale the way this skill or the web can. This skill adds what that guide doesn't say: the old-major traps and the gotchas below.

Effect 3, the 4.0 prereleases and 4.0 stable are all mixed together in model memory and on the web. In order of authority:

1. The installed declarations (`dist/**/*.d.ts`) for names and signatures, and the source (`src/**/*.ts`) for behavior. Resolve `effect` from the workspace package you're changing, not the repo root; Bun can link it under `node_modules/.bun/`.
2. `node_modules/effect/AGENTS.md` and the `ai-docs/src/` example it links for the task. Read the section and example that match the task, not every example.
3. Context7 (`/effect-ts/effect`) or effect.website v4 docs, when available, for explanation. They track `main`, so confirm anything release-sensitive against step 1.
4. Memory last.

Before writing a name you haven't seen in this repo's code, check it exists (from the package directory):

```bash
node --input-type=module -e 'import { Effect } from "effect"; console.log("catchAll" in Effect)'
```

### Reading the installed docs

Find the package directory with `node -p 'require("path").dirname(require.resolve("effect/package.json"))'` run from the workspace package. Inside it:

| What | Where |
| --- | --- |
| A module's API docs | `src/<Module>.ts` (`src/Effect.ts`, `src/Layer.ts`, `src/Schema.ts`); unstable modules under `src/http/`, `src/http-api/`, `src/sql/`, `src/cli/`, `src/testing/` |
| Signatures only | `dist/<Module>.d.ts`, same layout |
| The vendor's agent guide | `AGENTS.md`, an index of topics with one example file each |
| Runnable examples | `ai-docs/src/<topic>/` |
| Platform and test helpers | the same layout inside `@effect/platform-node` and `@effect/vitest` (`src/`) |

Each export's JSDoc in `src/` has **When to use**, **Details** and **Gotchas** sections, and the Gotchas carry the behavior this skill can only summarize (defaults, interruption, what a recovery skips). To read the docs for one function, search for its declaration and read the comment above it, for example `grep -n "^export const retryTransient" src/http/HttpClient.ts`. To survey a module's traps, `grep -n -A6 "\*\*Gotchas\*\*" src/<Module>.ts`. Source files are large, so read by line range, never whole.

When a name is missing, find the concept in the declarations. Don't add a shim, install `@effect/schema`, or copy an Effect 3 helper.

## Names that don't exist in Effect 4

| Effect 3 or a 4.0 prerelease | Effect 4 |
| --- | --- |
| `Context.Tag`, `Context.GenericTag`, `Effect.Tag`, `Effect.Service`, `ServiceMap` | `class X extends Context.Service<X, Shape>()("app/X")`, or `Context.Service<Shape>("app/X")` |
| `Layer.scoped` | `Layer.effect` (it removes `Scope` from the layer's requirements) |
| `Effect.catchAll`, `catchAllCause`, `catchAllDefect` | `Effect.catch`, `catchCause`, `catchDefect` |
| `Effect.either`, `Either` | `Effect.result`, `Result` (`.success`, `.failure`, `Result.isFailure`) |
| `Effect.async` | `Effect.callback((resume, signal) => ...)`, returning a cleanup Effect |
| `Effect.fork`, `forkDaemon` | `forkChild`, `forkScoped`, `forkIn`, `forkDetach` |
| `Effect.zipRight`, `tapErrorCause` | `Effect.andThen`, `tapCause` |
| `yield* option` or `yield* either` inside `Effect.gen` | `yield* Effect.fromOption(o)` (fails with `Cause.NoSuchElementError`) or `Effect.fromResult(r)`; `Option` and `Result` aren't Effects, and yielding one is a defect |
| `Schedule.intersect`/`both`, `Schedule.union`/`either` | `Schedule.max`, `Schedule.min` |
| `Schema.TaggedErrorClass`, `Schema.ErrorClass` | `Schema.TaggedError<X>()("X", fields)` |
| `@effect/schema`, `Schema.decodeUnknown`, `Schema.parseJson` | `Schema` from `effect`, `decodeUnknownEffect`, `Schema.fromJsonString` |
| `Schema.Union(a, b)`, `Schema.Literal("a", "b")` | `Schema.Union([a, b])`, `Schema.Literals(["a", "b"])` |
| `Schema.filter(...)` | `.check(Schema.makeFilter(...))` or a built-in check (`Schema.isInt()`, `Schema.isPattern(re)`) |
| `Config.string`, `Config.integer`, `Options.boolean` | `Config.String`, `Config.Int`, `Flag.Boolean` (constructors are capitalized) |
| `@effect/platform`, `@effect/cli`, `@effect/sql`, `effect/unstable/http` | `effect/http`, `effect/http-api`, `effect/cli`, `effect/sql`; drivers and runtimes stay in `@effect/platform-*` and `@effect/sql-*` |

Modules imported without `unstable` can still be marked `@stability unstable` (CLI, HTTP, sockets, `Crypto`, `ErrorReporter`). Check the declaration before assuming a shape survives an upgrade.

## Conventions

- `Effect.gen` for inline code. A reusable function returning an Effect is `Effect.fn("name")(function* (...) {...}, ...combinators)` when it's a useful tracing boundary and `Effect.fnUntraced` otherwise. Pass combinators as extra arguments; don't `.pipe` an `Effect.fn`. Annotate with `Effect.fn.Return<A, E, R>`. Pure calculations stay plain functions.
- Fail with `return yield* new SomeError({...})` so TypeScript knows the branch ends.
- Construct lazily: `Effect.succeed(x)` has already evaluated `x`. Use `sync`, `try`, `tryPromise` or `suspend` for work that should happen when the effect runs.
- Every resource and every forked fiber has an owner (a scope, a layer, a `FiberSet`), and some owner observes its failure.
- Effects run only at the application's integration boundaries (process entry, framework adapter, test). No `Effect.runPromise` or `runSync` inside Effect code or inside a callback created by it.

## References

Load the reference that matches the task; load several when work spans them.

| Task | Read |
| --- | --- |
| Wrapping promises, callbacks or throwing code; tagged errors; `catch*`; `Result`, `Exit`, `Cause`; defects; interruption | [references/errors.md](references/errors.md) |
| `Context.Service`, layers, memoization, dependency capture, request-scoped values, `ManagedRuntime` | [references/services-layers.md](references/services-layers.md) |
| Scopes, `acquireRelease`, forks, background workers, `Effect.cached`, `Ref`, locks, timeouts, schedules, retries, Clock, Random, DateTime | [references/resources-concurrency.md](references/resources-concurrency.md) |
| Schema definitions, decoding, encoding, optional keys, transformations, brands, JSON Schema | [references/schema.md](references/schema.md) |
| `@effect/vitest`, TestClock, TestConsole, test layers, asserting failures | [references/testing.md](references/testing.md) |
| `HttpClient`, `HttpApi`, `HttpRouter`, middleware, web handlers | [references/http.md](references/http.md) |
| `SqlClient`, `SqlSchema`, transactions | [references/sql.md](references/sql.md) |
| `effect/cli` commands, flags, parser errors, help | [references/cli.md](references/cli.md) |
| `Config`, `ConfigProvider`, `Redacted`, loggers, annotations, spans | [references/config-observability.md](references/config-observability.md) |

For a topic not listed (streams, PubSub, batching, child processes, AI, cluster), start from the matching entry in `node_modules/effect/AGENTS.md`.
