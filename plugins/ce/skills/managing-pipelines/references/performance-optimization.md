# Performance Optimization

Patterns for cutting CI times and runner costs in GitHub Actions. Everything here assumes you've already identified which jobs are actually slow (profile first, optimize second).

## Contents

- Caching strategies
- Matrix builds and test sharding
- Concurrency groups
- Monorepo path filtering
- Runner selection and cost
- Workflow optimization patterns

## Caching strategies

### The actions/cache pattern

```yaml
- uses: actions/cache@v4
  with:
    path: |
      ~/.npm
      node_modules
    key: node-${{ runner.os }}-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      node-${{ runner.os }}-
```

Always include `restore-keys`. A stale-but-close cache with an incremental update beats a full rebuild every time. The prefix match finds the most recent entry when the exact key misses.

### What to cache per ecosystem

Don't just cache your package manager's download directory. Profile what actually takes the longest and cache that.

| Ecosystem | Cache path | Key includes | Often missed |
|-----------|-----------|-------------|-------------|
| Node | `~/.npm`, `node_modules` | `package-lock.json` | Native addon compilation (`node_modules/.cache`) |
| Python | `~/.cache/pip`, `.venv` | `requirements.txt` or `poetry.lock` | Compiled wheels for C extensions |
| Go | `~/go/pkg/mod`, `~/.cache/go-build` | `go.sum` | Build cache (`~/.cache/go-build`) is the big win |
| Rust | `~/.cargo/registry`, `target` | `Cargo.lock` | `target/` directory dwarfs everything else |
| Docker | Docker layer cache | Dockerfile hash | Use `docker/build-push-action` with `cache-from`/`cache-to` |
| Terraform | `~/.terraform.d/plugin-cache` | `.terraform.lock.hcl` | Provider binaries are 100MB+ each |

### Cache limits and security

GitHub enforces a 10GB per-repo cache limit and evicts entries not accessed in 7 days. If you're hitting the limit, your cache keys are probably too specific (include fewer volatile inputs in the key hash).

Caches are shared across branches within a repo. A malicious PR branch can write a poisoned cache entry that main later restores. If your threat model includes untrusted contributors, scope cache keys to include `github.ref`.

## Matrix builds and test sharding

### Basic matrix strategy

```yaml
strategy:
  fail-fast: false
  matrix:
    node: [18, 20, 22]
    os: [ubuntu-latest, windows-latest]
    exclude:
      - node: 18
        os: windows-latest
```

`fail-fast: false` for CI (see all failures), `true` for deployment (bail on first failure). Use `exclude` and `include` to shape the matrix instead of testing every combination.

### Test sharding for parallelism

Combine Jest's built-in sharding with a matrix index to split tests across parallel jobs without any third-party tooling:

```yaml
jobs:
  test:
    strategy:
      fail-fast: false
      matrix:
        shard: [1, 2, 3, 4]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npx jest --shard=${{ matrix.shard }}/4
```

This gives you 4x parallelism for free. Works with Vitest (`--shard`), pytest (`pytest-split`), and most modern test runners. Profile your shard distribution to make sure work is evenly split.

## Concurrency groups

### CI pattern: cancel stale runs

```yaml
concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true
```

You only care about the latest push. Three quick commits? Cancel the first two runs.

### Deployment pattern: never interrupt

```yaml
concurrency:
  group: deploy-production
  cancel-in-progress: false
```

Never cancel a running deployment. An interrupted deploy can leave infrastructure partially applied. With `cancel-in-progress: false`, GitHub queues the new run and starts it after the current one finishes. At most one running and one pending job per group.

### Choosing the group key

| Scenario | Group key | cancel-in-progress |
|----------|-----------|-------------------|
| PR CI checks | `ci-${{ github.ref }}` | `true` |
| Main branch CI | `ci-main` | `false` (or `true` if builds are independent) |
| Staging deploy | `deploy-staging` | `false` |
| Production deploy | `deploy-production` | `false` |
| Scheduled jobs | `scheduled-${{ github.workflow }}` | `false` |

## Monorepo path filtering

Built-in `paths` filters only work at the workflow trigger level. You can't conditionally skip individual jobs based on changed files. For job-level granularity, use dorny/paths-filter.

```yaml
jobs:
  changes:
    runs-on: ubuntu-latest
    outputs:
      api: ${{ steps.filter.outputs.api }}
      web: ${{ steps.filter.outputs.web }}
      shared: ${{ steps.filter.outputs.shared }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            api:
              - 'packages/api/**'
              - 'packages/shared/**'
            web:
              - 'packages/web/**'
              - 'packages/shared/**'
            shared:
              - 'packages/shared/**'

  test-api:
    needs: changes
    if: ${{ needs.changes.outputs.api == 'true' }}
    runs-on: ubuntu-latest
    steps:
      - run: echo "Running API tests"

  test-web:
    needs: changes
    if: ${{ needs.changes.outputs.web == 'true' }}
    runs-on: ubuntu-latest
    steps:
      - run: echo "Running web tests"
```

This reduces CI times by 70-90% in large monorepos. Changes to `packages/shared/` trigger both downstream jobs, handling cross-package dependencies.

For deeper dependency awareness, combine with Turborepo (`turbo run test --filter=...[HEAD^]`) or Nx (`nx affected --target=test`). These tools understand your package graph and only build/test what's actually affected.

## Runner selection and cost

### ARM64 vs x86

ARM64 runners are significantly cheaper per minute than their x86 equivalents at every size tier.

| Runner | x86 (per min) | ARM64 (per min) | Savings |
|--------|---------------|-----------------|---------|
| Linux 2-core | $0.006 | $0.005 | 17% |
| Linux 8-core | $0.024 | $0.020 | 17% |
| Linux 32-core | $0.096 | $0.080 | 17% |
| Linux 64-core | $0.192 | $0.098 | 49% |

The 17% savings is consistent across most tiers, jumping to 49% at 64-core. If your workload runs on ARM (most do unless you depend on x86-specific binaries), switching is free money.

### Runner sizing decision table

| Workload | Runner choice | Why |
|----------|--------------|-----|
| Linting, type checking | Standard 2-core | CPU-light, not worth paying more |
| Unit tests (fast suite) | Standard 2-core | Finishes quickly regardless |
| Unit tests (large suite, shardable) | Standard 2-core x N shards | Parallelism via matrix is cheaper than bigger runners |
| Compilation (Rust, C++, Go) | 8-16 core | CPU-bound, scales linearly with cores |
| Docker builds | 4-8 core | I/O + CPU mix, diminishing returns past 8 cores |
| E2E / browser tests | 4-core + memory | Chrome/Playwright need RAM more than CPU |
| Terraform plan/apply | Standard 2-core | Provider API calls are the bottleneck, not CPU |

Larger runners have no idle cost. A 4x larger runner finishing in 1/4 the time costs roughly the same but delivers results 4x faster. When wall-clock time matters, go bigger.

### 2026 pricing changes

GitHub restructured Actions pricing in 2026: hosted runners dropped up to 39% (January 2026), and a $0.002/minute platform charge now applies to self-hosted runners in private repos (March 2026). Public repos remain free.

For high-volume orgs ($5K+/month on Actions), evaluate third-party providers like RunsOn, WarpBuild, or Blacksmith. They run on your cloud account with 2-5x cost savings.

## Workflow optimization patterns

### Sparse checkout

For large repos, only check out the files you need:

```yaml
- uses: actions/checkout@v4
  with:
    sparse-checkout: |
      packages/api
      packages/shared
    sparse-checkout-cone-mode: true
```

Skips downloading the entire repo tree. Particularly impactful in monorepos with large assets or many packages.

### Conditional step execution

Skip expensive steps when they're not needed:

```yaml
- name: Build Docker image
  if: github.event_name == 'push' && github.ref == 'refs/heads/main'
  run: docker build -t myapp .
```

### Job dependency graph

Independent jobs run concurrently by default. Only add `needs` when a job genuinely depends on another's output:

```yaml
jobs:
  lint:                             # runs immediately
  typecheck:                        # parallel with lint
  unit-test:                        # parallel with both
  build:
    needs: [lint, typecheck]        # waits for quality gates
  deploy:
    needs: [unit-test, build]       # waits for all
```

### Artifacts vs checkout in downstream jobs

| Approach | Pros | Cons |
|----------|------|------|
| Pass artifacts between jobs | No rebuild, exact same output | Upload/download time, 10GB artifact limit |
| Checkout + rebuild in each job | Simple, no artifact management | Duplicate work, possible inconsistency |
| Cache + checkout | Fast restore, no artifact overhead | Cache miss = full rebuild |

For build outputs under 500MB, artifacts are the right call. For larger outputs or when downstream jobs only need source code, use caching with checkout. Don't rebuild the same thing in multiple jobs just to avoid artifact management.
