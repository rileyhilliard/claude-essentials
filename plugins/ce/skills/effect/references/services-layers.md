# Services and layers

Read when defining a service, composing layers, deciding what a service captures, or running Effect code from a framework that isn't Effect.

## Defining a service

A service is a `Context.Service` class whose layers are static members (illustrative; `UserId`, `User` and `UserNotFound` are application types):

```ts
class Users extends Context.Service<Users, {
  readonly find: (id: UserId) => Effect.Effect<User, UserNotFound>
}>()("app/Users") {
  static readonly layer = Layer.effect(this, Effect.gen(function* () {
    const sql = yield* SqlClient.SqlClient
    return { find: (id) => /* uses sql */ }
  }))
}
```

The second form takes a `make` effect: `class X extends Context.Service<X>()("app/X", { make: Effect.gen(...) }) {}`. It stores the constructor but does not generate a layer; build it yourself with `static readonly layer = Layer.effect(this, this.make)`. Derive the shape from the service (`Context.Service.Shape<typeof X>` or the class's own type) instead of writing a second interface.

Key strings are global: namespace them (`app/Users`). Name layers after what they are (`layer`, `live`, `sql`, `memory`, `test`); the repo's convention wins.

Related patterns already in the installed examples, read when needed: a service with a default value (`Context.Reference`, `ai-docs/src/01_effect/03_services/10_reference.ts`), a layer built from config or an effect (`Layer.unwrap`, `20_layer-unwrap.ts`), a layer that only runs a background task (`Layer.effectDiscard`, `05_resources/20_layer-side-effects.ts`), and keyed dynamic layers (`LayerMap`, `05_resources/30_layer-map.ts`).

## What a service captures

Yield stable dependencies (config, a database client, other application services) once, in the layer's constructor, and close the methods over them. The method signatures then show only what the caller must supply.

Don't capture request-scoped values (the current user, request id, authorization, a request `Scope`) into an application-wide layer. The first request's identity would be shared with every later one. Pass request values as method arguments, or leave the requirement on the method so each call provides it.

Let signatures tell the truth. Don't provide a hidden layer inside a method just to turn its requirements into `never`, and a method that returns a resource owned by its caller keeps `Scope` in its requirements.

A service depends on another through the context. It never provides the other's layer itself, which would build a private copy.

## Composition and memoization

Compose the whole graph once, at the entry point, then provide it. `Layer.provide(dep)` feeds a dependency in and hides it; `Layer.provideMerge(dep)` also keeps the dependency's services in the output.

Layers are memoized by identity (the same layer value) within a memo map. Effect 4 shares that map across nested provides, which Effect 3 did not:

| Situation | Builds |
| --- | --- |
| The same layer value provided twice, nested | once: the inner provide reuses the outer build |
| Two sibling `Effect.provide(L)` calls with no enclosing build | twice |
| Siblings under an enclosing provide or runtime that already built `L` | once, the enclosing instance |
| `Effect.provide(L, { local: true })` | fresh, with its own memo map |
| `Layer.fresh(L)` | fresh every time it's built |
| A factory call, `X.layer(options)` | a new value each call, so a new build |

So "providing a layer per request builds it again" depends on where the request runs: inside a runtime that already built that same value, it reuses the running instance and its state. Mutable state belongs inside the layer constructor (a closure variable, a `Ref`), so its lifetime is the layer's. Use a factory or `Layer.fresh` when each caller needs its own instance.

## Running from a non-Effect framework

When a framework (an HTTP framework, a UI, a job runner) calls into Effect code repeatedly, build one `ManagedRuntime.make(layer)` at the integration's owner and `dispose()` it when that owner shuts down. Don't build a runtime per callback; it rebuilds the whole graph. See `ai-docs/src/04_integration/10_managed-runtime.ts`.

When Effect code hands a callback to foreign code, capture what the callback needs while still in Effect (`const ctx = yield* Effect.context<Needs>()`, then `Effect.provide(ctx)` inside it) rather than reading services from a global or starting a new runtime. Capture only the services the callback needs.

Process entry points use the platform's runner (`NodeRuntime.runMain`, or `Layer.launch` for a server that runs until interrupted, `ai-docs/src/01_effect/06_running/`). A repo with its own exit-code and signal policy keeps its own boundary.
