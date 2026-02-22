---
name: managing-pipelines
description: Guides CI/CD pipeline architecture, security hardening, and deployment strategies for GitHub Actions. Use when designing workflows, securing supply chains, optimizing build performance, configuring deployments, managing infrastructure as code pipelines, or setting up pipeline observability.
---

# Pipeline Management

Decision guidance for GitHub Actions CI/CD pipelines, deployment strategies, and infrastructure automation.

## Contents

- When to use which pattern
- Security quick reference
- Performance quick reference
- Workflow architecture quick reference
- Deployment quick reference
- Infrastructure as code quick reference
- Observability quick reference
- Cross-pipeline conventions
- Pipeline debugging checklist

## When to use which pattern

| Scenario | Reference | Why |
| --- | --- | --- |
| Hardening against supply chain attacks | Security | SHA pinning, permissions, OIDC |
| Speeding up slow CI builds | Performance | Caching, matrix builds, concurrency |
| DRY-ing up duplicated workflow YAML | Workflow architecture | Reusable workflows vs composite actions |
| Setting up staging/production deploys | Deployment | Environment promotion, protection rules |
| Adding Terraform/OpenTofu to CI | Infrastructure | Plan-on-PR, apply-on-merge, drift detection |
| Tracking pipeline reliability | Observability | OTel, DORA metrics, SLOs |
| Reviewing a PR that modifies workflows | Security + Workflow | Permissions audit, secret exposure review |
| Debugging flaky pipelines | Observability + Performance | Metrics, cache hit rates, concurrency |
| Migrating from Jenkins/CircleCI | Workflow architecture | Action patterns, reusable workflow design |
| Setting up monorepo CI | Performance | Path filtering, selective job execution |

## Security quick reference

**Use for:** Preventing supply chain attacks, minimizing credential exposure, hardening runner environments.

**Key decisions:**

- Pin all third-party actions to full commit SHAs, not tags
- Set org-level default token permissions to read-only
- Use OIDC for cloud auth instead of stored credentials
- Never use `pull_request_target` without understanding the security model

See [references/security-hardening.md](references/security-hardening.md) for attack patterns and mitigations.

## Performance quick reference

**Use for:** Reducing CI times, optimizing runner costs, parallelizing builds.

**Key decisions:**

- Cache dependency installs AND build artifacts (not just `node_modules`)
- Use `fail-fast: false` for CI matrices, `true` for deployment
- Set concurrency groups with `cancel-in-progress: true` for CI, `false` for deploys
- Use path filtering in monorepos to skip irrelevant jobs

See [references/performance-optimization.md](references/performance-optimization.md) for caching strategies and runner selection.

## Workflow architecture quick reference

**Use for:** Structuring reusable CI/CD components, managing action dependencies.

**Key decisions:**

- Reusable workflows for entire pipeline templates; composite actions for shared steps
- Pass secrets explicitly, not with `secrets: inherit`
- Automate SHA pin updates with Dependabot or Renovate
- Restrict allowed actions at the org level

See [references/workflow-architecture.md](references/workflow-architecture.md) for patterns and versioning.

## Deployment quick reference

**Use for:** Environment promotion, deployment gates, progressive delivery.

**Key decisions:**

- Use GitHub Environments with branch restrictions for production
- Release-based promotion gives the cleanest audit trail
- Progressive delivery (canary/blue-green) via Argo Rollouts or Flagger
- Custom deployment protection rules for SLO-gated deployments

See [references/deployment-strategies.md](references/deployment-strategies.md) for promotion patterns and rollback strategies.

## Infrastructure as code quick reference

**Use for:** Terraform/OpenTofu pipelines, drift detection, policy enforcement.

**Key decisions:**

- Always save plan output and apply the saved plan (never plan-then-apply without `-out`)
- Post plan output as PR comments for review
- Segment state by functional boundary, not geography
- Run scheduled drift detection separately from code-triggered deploys

See [references/infrastructure-pipelines.md](references/infrastructure-pipelines.md) for IaC workflow patterns.

## Observability quick reference

**Use for:** Pipeline reliability tracking, incident response, capacity planning.

**Key decisions:**

- Instrument pipelines with OpenTelemetry (runs as traces, jobs as spans)
- Track DORA metrics: deployment frequency, lead time, change failure rate, MTTR
- Set SLOs for pipeline reliability (e.g., 99% main branch build success)
- Monitor cache hit rates and queue times as leading indicators

See [references/pipeline-observability.md](references/pipeline-observability.md) for instrumentation and metrics.

## Cross-pipeline conventions

### Workflow file naming

| Convention | Example | When |
| --- | --- | --- |
| Trigger-based prefix | `ci-test.yml`, `ci-lint.yml` | CI workflows |
| Deploy prefix | `deploy-staging.yml`, `deploy-prod.yml` | Deployment workflows |
| Scheduled prefix | `scheduled-drift.yml`, `scheduled-cleanup.yml` | Cron jobs |
| Reusable prefix | `_reusable-build.yml` | Shared workflow templates |

### Permissions

| Principle | Pattern |
| --- | --- |
| Default to read-only | Set at org/repo level, override per-job |
| Scope per job, not workflow | Each job declares only what it needs |
| OIDC over stored secrets | Short-lived tokens scoped to repo+branch+env |
| Explicit secret passing | Name each secret, avoid `secrets: inherit` |

### Branch protection

| Rule | CI workflows | Deploy workflows |
| --- | --- | --- |
| Required status checks | Yes | Yes |
| Require PR reviews | Yes | Yes (production) |
| Dismiss stale reviews | Yes | Yes |
| Restrict pushes | Optional | Yes (main/release branches) |

## Pipeline debugging checklist

### Slow CI builds

1. Check cache hit rates (low = cold start overhead)
2. Look for sequential jobs that could run in parallel
3. Verify concurrency groups aren't queuing unnecessarily
4. Check runner specs (CPU-bound work on small runners)
5. Look for full-repo checkouts when sparse checkout would work

### Failed deployments

1. Check environment protection rule approvals
2. Verify OIDC token audience and subject claims
3. Check if concurrency group blocked/cancelled the run
4. Review Terraform plan output for unexpected changes
5. Check if deployment protection rules (Datadog, etc.) rejected

### Security incidents

1. Audit recent changes to workflow files and action versions
2. Check for new `pull_request_target` usage
3. Review GITHUB_TOKEN permissions in affected workflows
4. Scan for secrets in workflow logs (step outputs, artifacts)
5. Check if any action SHAs were recently changed

### Flaky pipelines

1. Check if tests have timing dependencies (see `condition-based-waiting` skill)
2. Look for shared state between matrix jobs
3. Verify caches aren't corrupted (clear and rebuild)
4. Check for rate limiting from external services
5. Review runner availability (self-hosted runner capacity)
