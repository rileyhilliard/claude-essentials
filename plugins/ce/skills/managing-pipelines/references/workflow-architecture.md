# Workflow Architecture

Patterns for structuring reusable CI/CD components, managing action dependencies, and keeping workflow sprawl under control.

## Contents

- Reusable workflows vs composite actions
- Secrets handling
- Versioning internal actions
- Dependency management
- Action restriction policies
- Workflow organization patterns
- Composite action patterns

## Reusable workflows vs composite actions

Two different tools for two different problems. Pick wrong and you fight the abstraction.

| Aspect | Reusable Workflows | Composite Actions |
|--------|-------------------|-------------------|
| Scope | Entire multi-job pipeline | Steps within a job |
| Secrets | Native support, `secrets: inherit` | Must be passed as inputs |
| Matrix | Cannot be called with matrix strategy | Can be used inside matrix jobs |
| Nesting | One level deep only | Unlimited |
| Visibility | Separate workflow run | Inline in calling job |
| Use case | Pipeline templates | Shared task templates |

**The decision is about scope.** Multi-job pipelines with environment gates = reusable workflow. Shared step sequences reused across jobs = composite action.

Gotcha: reusable workflows nest only one level deep. A calls B, but B cannot call C. Composite actions have no such limit.

## Secrets handling

`secrets: inherit` passes ALL repository and org secrets to the called workflow. Violates least privilege, makes auditing impossible.

```yaml
# Prefer: explicit passing creates a contract
jobs:
  deploy:
    uses: ./.github/workflows/deploy.yml
    secrets:
      DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}

# Avoid: inherit passes everything, no audit trail
jobs:
  deploy:
    uses: ./.github/workflows/deploy.yml
    secrets: inherit
```

Composite actions cannot declare `secrets` in inputs. Pass as regular `inputs` and mask immediately with `::add-mask::` as the first step:

```yaml
runs:
  using: composite
  steps:
    - shell: bash
      run: echo "::add-mask::${{ inputs.deploy-key }}"
    - shell: bash
      run: deploy --key "${{ inputs.deploy-key }}"
```

## Versioning internal actions

Tags are mutable (force-pushable). SHAs are immutable. Pin to full SHAs in production, `@main` only during development.

| Change type | Version bump |
|-------------|-------------|
| New optional input | Minor |
| Rename/remove input | Major |
| Change output format | Major |
| New required input | Major |
| Bug fix | Patch |

Maintain a `v1` floating tag pointing to latest v1.x.x. Consumers get patches automatically, opt into `v2` explicitly. Adding a required input breaks every caller, so always use defaults for new inputs:

```yaml
inputs:
  environment: { required: true, type: string }
  notify-slack: { required: false, type: boolean, default: true }  # Non-breaking addition
```

## Dependency management

Dependabot natively updates GitHub Actions SHA pins. The `groups` key batches all updates into a single PR:

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: github-actions
    directory: /
    schedule: { interval: weekly }
    groups:
      actions: { patterns: ["*"] }
```

| Feature | Dependabot | Renovate |
|---------|-----------|----------|
| Cross-platform (GitLab, Bitbucket) | No | Yes |
| Monorepo awareness | Basic | Strong |
| Dependency dashboard | No | Yes |
| Custom regex for non-standard refs | No | Yes |

Renovate's dependency dashboard tracks all pending updates with manual trigger support. For orgs with many repos, that visibility is worth the setup cost.

## Action restriction policies

At the org level, configure action permissions:

1. **Allow all actions** (default, not recommended)
2. **Allow verified creators + specific repos** (practical sweet spot)
3. **Explicit allowlist only** (most secure)

Option 2 works for most orgs. Verified creators are low-risk, add specific repos as teams request them.

Enforce SHA pinning and monitor network egress with StepSecurity Harden-Runner:

```yaml
- uses: step-security/harden-runner@v2
  with:
    egress-policy: audit  # Start with audit, move to block
    allowed-endpoints: >
      github.com:443
      registry.npmjs.org:443
```

Before approving a new third-party action: check `GITHUB_TOKEN` usage, verify no external artifact uploads, confirm it pins its own dependencies, prefer actions with fewer than 3 dependencies.

## Workflow organization patterns

### File naming

| Prefix | Purpose | Example |
|--------|---------|---------|
| `ci-` | PR/push triggers | `ci-test.yml`, `ci-lint.yml` |
| `deploy-` | Deployments | `deploy-staging.yml` |
| `scheduled-` | Cron jobs | `scheduled-drift.yml` |
| `_reusable-` | Called by others | `_reusable-build.yml` |
| `manual-` | workflow_dispatch | `manual-rollback.yml` |

Underscore prefix sorts reusable workflows to the top and signals "don't trigger directly."

### Split vs combine

Split when jobs have different triggers, permissions, or schedules. Combine when they always run together on the same trigger. CI lint + test + build in one file is fine. CI and deploy in separate files even if they share steps.

### Error handling

`continue-on-error` plus conditional rollback lets you clean up before the job fails. Without it, the job stops at the failed step and skips cleanup.

```yaml
jobs:
  deploy:
    timeout-minutes: 15  # Always set. Default is 360 (6 hours).
    steps:
      - id: deploy
        continue-on-error: true
        run: ./deploy.sh
      - if: steps.deploy.outcome == 'failure'
        run: ./rollback.sh
      - if: steps.deploy.outcome == 'failure'
        run: exit 1  # Fail the job after rollback completes
```

### Job dependency graphs

```yaml
jobs:
  lint:    { ... }
  test:    { ... }
  build:   { needs: [lint, test] }
  deploy:  { needs: build }
  notify:  { needs: deploy, if: always() }
```

`if: always()` on notification jobs is critical. Without it, upstream failures skip downstream jobs and you never get notified.

## Composite action patterns

### Input validation

Fail fast with clear errors, not silent wrong results:

```yaml
runs:
  using: composite
  steps:
    - shell: bash
      run: |
        if [[ ! "${{ inputs.environment }}" =~ ^(staging|production)$ ]]; then
          echo "::error::Invalid environment '${{ inputs.environment }}'."
          exit 1
        fi
```

### Sharing outputs between steps

Use `$GITHUB_OUTPUT` to pass data between composite action steps:

```yaml
steps:
  - id: build
    shell: bash
    run: echo "version=$(git describe --tags)" >> "$GITHUB_OUTPUT"
  - shell: bash
    run: docker tag app:latest app:${{ steps.build.outputs.version }}
```

### Pre/post cleanup

Composite actions don't support `pre:`/`post:` lifecycle hooks (only JS and Docker actions do). Use `if: always()` for teardown. Without it, test failure skips cleanup and leaves containers running.

```yaml
steps:
  - shell: bash
    run: docker compose up -d
  - id: task
    continue-on-error: true
    shell: bash
    run: ./run-integration-tests.sh
  - if: always()
    shell: bash
    run: docker compose down -v
  - if: steps.task.outcome == 'failure'
    shell: bash
    run: exit 1
```
