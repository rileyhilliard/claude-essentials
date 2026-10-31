# HTTP clients and HttpApi servers

Read when calling HTTP services with `HttpClient`, or defining, serving, testing or consuming an `HttpApi`. Imports are `effect/http` and `effect/http-api` (both marked unstable, so check declarations after upgrades); Node servers come from `@effect/platform-node`. Examples: `ai-docs/src/50_http-client/10_basics.ts`, `51_http-server/10_basics.ts` and `20_testing.ts`.

## Contents

- HttpClient
- Defining an HttpApi
- Serving and middleware
- Testing and clients

## HttpClient

Get the client from the context (`yield* HttpClient.HttpClient`) and supply the transport at the edge (`FetchHttpClient.layer`, or the Node client). `FetchHttpClient.Fetch` injects the fetch function, which is how a browser-side test supplies a fake transport.

A non-2xx response is not a failure until you say so: add `HttpClient.filterStatusOk` (or `filterStatus`). Decode bodies with the response's schema helpers instead of casting `json`.

`HttpClient.retryTransient` has defaults that are easy to ship by accident (observed in 4.0; read its JSDoc in `src/http/HttpClient.ts`):

- With no `schedule` and no `times`, it retries forever with no delay.
- It retries any method, POST included; the caller decides whether replay is safe.
- It treats transport errors, `TimeoutError` and transient statuses (408, 429, 5xx) as retryable, responses included by default (`retryOn: "errors-and-responses"`).
- A `Retry-After` header sets the minimum delay, with no upper cap.
- The `while` predicate is ignored in `"response-only"` mode.

Always pass `times` or a bounded, jittered schedule, and put an `Effect.timeout` around the whole call so a long `Retry-After` can't stall the caller. Turn off any retry built into an SDK underneath, so there is one retry policy.

## Defining an HttpApi

`HttpApi.make("api").add(group)`, `HttpApiGroup.make("Users").add(endpoint)`, `HttpApiEndpoint.get("get", "/users/:id", { params, query, success, error })`. The endpoint schemas are the router, the request decoder, the response encoder, the OpenAPI document and the typed client, so handlers never decode or pick statuses by hand. `HttpApiBuilder.group(Api, "Users", (h) => h.handle("get", ...))` implements a group; `HttpApiBuilder.layer(Api, { openapiPath })` registers routes.

Statuses and headers are declared on schemas: `HttpApiSchema.status(201)`, `HttpApiSchema.NoContent` or `asNoContent` for bodyless responses, `WithHeaders` for response headers. Returning a raw `HttpServerResponse` from a handler bypasses the encoder and the OpenAPI document; keep that for streams and files.

Traps observed in 4.0 (check the builder source before relying on them):

- `HttpApiBuilder.layer` requires `HttpPlatform`, `FileSystem`, `Path` and `Etag` even for JSON-only APIs; the platform's server layer supplies them.
- The builder turns schema failures into defects carrying an `HttpApiSchemaError` whose kind says where it came from. Params, Query, Headers and Payload kinds are bad client input; Body and ResponseHeaders kinds are the server failing to encode its own response. A boundary that maps "decode failed" to 400 has to inspect the cause and the kind, or it will report server bugs as client errors.
- An empty `Schema.Struct({})` query accepts arbitrary keys even with strict parse options; use `Schema.Record(Schema.String, Schema.Never)` to allow none.
- Strict excess-key checking is set with `Api.annotate(HttpApi.QueryParseOptions, { onExcessProperty: "error" })`. Scope it to queries; applied to headers it rejects every real request.

## Serving and middleware

`HttpRouter.serve(appLayer, options)` serves through an `HttpServer` layer (`NodeHttpServer.layer(createServer, { port })`); `HttpRouter.toWebHandler(appLayer, options)` returns `{ handler, dispose }`, and `dispose` must be called.

Install middleware at the level whose responses it must see. In 4.0, the middleware option of `serve`/`toWebHandler` wraps sending the response, so edits to the response there don't reach the client. `HttpRouter.middleware(fn, { global: true })` wraps every request inside routing, including route misses and responses the framework builds before a handler runs, so a request-id, logging or error-envelope boundary goes there. A route-level middleware never sees misses or static files. Pass `{ disableLogger: true }` to the serve helpers when the application logs requests itself, or each request logs twice.

Work that must outlive the response is forked into an application scope, not the request's.

## Testing and clients

`NodeHttpServer.layerTest` serves on an ephemeral port and provides an `HttpClient` pointed at it: real HTTP, global middleware included. `HttpApiTest.groups(api, [...])` builds the API layer in process without the router's global middleware, so it can't test request boundaries. `HttpApi.reflect(Api, { onGroup, onEndpoint })` walks every declared endpoint, which suits tests over the whole contract. A web handler under test captures logs when the logger layer is merged into its app layer with `Layer.provideMerge(Logger.layer([...]))`.

`HttpApiClient.make(Api, { baseUrl })` returns a typed client that needs an `HttpClient`. Error schemas decode error responses back into the tagged errors, so client code handles them with `catchTag`.
