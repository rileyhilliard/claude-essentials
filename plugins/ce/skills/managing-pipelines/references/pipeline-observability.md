# Pipeline Observability

GitHub Actions gives you run logs and a green/red badge. That is not observability. Most teams fly blind until something is very broken.

## Contents

- The observability gap
- OpenTelemetry for CI/CD
- Key metrics to track
- SLOs for CI/CD
- Commercial options
- Alerting patterns
- Dashboard design

## The observability gap

GitHub Actions has no built-in trend analysis, no anomaly detection, and no SLO tracking. You get per-run logs and a status badge. That is it.

Pipeline degradation is invisible until it is catastrophic. Build times creep up by 30 seconds a week for six months and nobody notices until the feedback loop is 20 minutes. You would never run a production service without metrics and alerts.

## OpenTelemetry for CI/CD

The emerging standard for pipeline telemetry. Every workflow run becomes a trace, every job a span, every step a child span. Same distributed tracing mental model you already use for production services.

Three approaches with different tradeoffs:

| Approach | How it works | Granularity | Workflow changes | Best for |
|----------|-------------|-------------|------------------|----------|
| Webhook-based | GitHub webhooks for `workflow_run` and `workflow_job` events to an OTel Collector with a GitHub Receiver | Job-level | None | Org-wide instrumentation without touching workflows |
| In-workflow actions | Actions like `krzko/run-with-telemetry` wrap `run` steps | Step-level | Every workflow | Targeted deep visibility into specific pipelines |
| Post-run collection | GitHub API to collect workflow/job timing data, emit as OTel metrics | Job-level | None | Retroactive instrumentation of existing workflows |

### Webhook-based (recommended starting point)

Configure org-level webhooks for `workflow_run` and `workflow_job` events, pointed at an OTel Collector running the GitHub Receiver. Zero workflow modifications.

```yaml
# otel-collector-config.yaml
receivers:
  githubevents:
    endpoint: 0.0.0.0:19419
    path: /events
    secret: ${WEBHOOK_SECRET}

exporters:
  otlp:
    endpoint: your-backend:4317

service:
  pipelines:
    traces:
      receivers: [githubevents]
      exporters: [otlp]
```

The limitation is job-level granularity. You see that a job took 8 minutes but not which step was responsible.

### In-workflow instrumentation

For step-level visibility, wrap individual steps:

```yaml
steps:
  - uses: krzko/run-with-telemetry@v1
    with:
      span-name: "npm-test"
      run: npm test
    env:
      OTEL_EXPORTER_OTLP_ENDPOINT: ${{ secrets.OTEL_ENDPOINT }}
```

Requires modifying every workflow you want to instrument. Use this selectively on pipelines where you need step-level breakdown.

## Key metrics to track

Categorize by what they tell you:

| Category | Metric | What it indicates | Target |
|----------|--------|-------------------|--------|
| Reliability | Workflow success rate | Pipeline "availability" | >98% on main |
| Reliability | Flaky test rate | Tests failing intermittently | <2% of test runs |
| Speed | Mean time to feedback | Push to test results | <10 min |
| Speed | Deploy lead time | Commit to production | <1 hour |
| Efficiency | Cache hit rate | Build efficiency proxy | >80% |
| Capacity | Runner queue time | Waiting for a runner | <30 sec |
| Capacity | Concurrent job count | Runner pool utilization | Below pool max |
| Delivery | Deployment frequency | How often you ship | Daily or better |
| Delivery | Change failure rate | Deploys that cause incidents | <5% |
| Recovery | Mean time to recovery | Incident to resolution | <1 hour |

The last four are DORA metrics. Track them weekly or monthly, not per-commit. They are trend indicators, not real-time signals.

### The metric that matters most

Flaky test rate. When developers stop trusting test results, they stop reading failures, and real bugs slip through. A 5% flaky rate sounds low until you realize developers mentally dismiss 1 in 20 red builds.

## SLOs for CI/CD

Treat your pipeline like a production service. Define SLOs, track error budgets, alert when things degrade.

```yaml
# pipeline-slos.yaml
slos:
  - name: main-branch-reliability
    sli:
      type: availability
      filter: "workflow.branch == 'main' AND workflow.conclusion != 'cancelled'"
      good: "workflow.conclusion == 'success'"
    objective: 0.99
    window: 30d
  - name: feedback-latency
    sli:
      type: latency
      filter: "workflow.name == 'CI' AND workflow.branch != 'main'"
      threshold: 600  # 10 minutes
    objective: 0.95
    window: 30d
```

### Error budget burn rate alerting

The useful signal is not "a build failed" but "we are burning through our error budget faster than expected."

```python
monthly_budget = total_runs * (1 - slo_target)  # e.g., 1000 * 0.01 = 10 failures allowed
current_failures = count_failures(last_30_days)
burn_rate = current_failures / expected_failures_at_this_point

if burn_rate > 6.0:   # 6x burn = budget gone in 5 days
    alert(severity="critical", message="Pipeline SLO burn rate critical")
elif burn_rate > 3.0:  # 3x burn = budget gone in 10 days
    alert(severity="warning", message="Pipeline SLO burn rate elevated")
```

### Correlation IDs

Tie pipeline runs to deployments to runtime logs with correlation IDs:

```yaml
- name: Deploy
  run: |
    CORRELATION_ID="${GITHUB_RUN_ID}-${GITHUB_RUN_ATTEMPT}"
    echo "correlation_id=$CORRELATION_ID" >> "$GITHUB_OUTPUT"
    deploy --tag "${{ github.sha }}" --correlation-id "$CORRELATION_ID"
```

When an incident fires, search your runtime logs for the correlation ID to trace back to the exact build that introduced the problem.

## Commercial options

| Tool | Strengths | Best for |
|------|-----------|----------|
| Datadog CI Visibility | Job-level tracking, alerting, APM correlation | Teams already on Datadog |
| Sentry | Failure tracking with stack trace linking | Error-focused debugging |
| Mergify | Flaky test detection, merge queue optimization | PR throughput |
| Buildkite Analytics | Test suite analytics, flaky detection | Build performance tuning |

Datadog CI Visibility is the most complete if you are already paying for Datadog. Budget-constrained? The webhook-to-OTel-Collector approach with Grafana gives you 80% of the value at zero licensing cost.

## Alerting patterns

### Alert on burn rate, not individual failures

Individual build failures are noise. A single flaky test, a transient network issue, a runner hiccup. Alerting on every failure trains people to ignore alerts.

### Route alerts to workflow owners

Pipeline alerts should go to the team that owns the workflow, not a central ops channel. A central channel becomes a wall of noise nobody reads.

### Severity levels

| Signal | Severity | Action |
|--------|----------|--------|
| Error budget burn rate >6x | Critical | Fix now, pipeline is broken |
| Error budget burn rate >3x | Warning | Investigate this week |
| Build duration P95 up >20% | Info | Track, investigate if trend continues |
| Cache hit rate dropped >10% | Info | Check cache key configuration |
| Runner queue time >2 min | Warning | Scale runner pool or optimize concurrency |

## Dashboard design

Answer three questions at a glance: is the pipeline healthy, is it getting better or worse, and where are the bottlenecks.

### Top row: current health

- Pipeline success rate (last 24h, last 7d)
- Current runner queue depth
- Active/queued workflow runs

### Middle row: trends

- Build duration P50/P95 over time (catch gradual degradation)
- Success rate weekly rolling average
- Cache hit rate trend
- Flaky test count over time

### Bottom row: delivery metrics

- DORA metrics weekly/monthly rollup
- Change failure rate and deploy frequency trends

Start with five panels. Add more only when you have a specific question the existing panels cannot answer.
