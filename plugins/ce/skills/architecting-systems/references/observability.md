# Observability

Systems that can't be debugged in production will eventually fail in production. These decisions are painful to retrofit, so get the foundation in early.

## Structured Logging

- **Use structured formats (JSON) from day one.** `{"level":"error","service":"payments","trace_id":"abc","msg":"charge failed"}` is queryable. `ERROR: charge failed` is not.
- **Include correlation IDs in every log.** Request IDs and trace IDs link related entries across services. Without them, debugging distributed issues means grep and guesswork.
- **Log at boundaries, not everywhere.** Log incoming requests, outgoing calls, errors, and business events. Don't log inside tight loops or for every function call.
- **Never log secrets.** Allowlist what gets logged, don't blocklist what doesn't. Mask PII at the application level, not as an afterthought.

## Health Checks

Build health endpoints into every service from the start:

- **Liveness** (`/health/live`): "Is the process running?" Return 200 if the app isn't deadlocked. Don't check dependencies here; a slow database shouldn't cause restarts.
- **Readiness** (`/health/ready`): "Can this instance handle traffic?" Check database connections, cache availability, required downstream services. Failed readiness = stop routing traffic, not restart.
- **Startup** (`/health/startup`): "Has initialization completed?" For slow-starting services (JVM warmup, cache loading). Prevents premature liveness kills during startup.

## Metrics and Traces

- **Instrument at service boundaries.** Request rate, error rate, and duration (RED metrics) for every API endpoint and external call. This covers 80% of debugging needs.
- **Use OpenTelemetry.** It's the industry standard. Start with auto-instrumentation, add manual spans for business-critical paths.
- **Separate telemetry from business logic.** Observability code should be middleware, decorators, or interceptors. Don't litter business logic with metrics calls.
