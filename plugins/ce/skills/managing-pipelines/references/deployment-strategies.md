# Deployment Strategies

Environment promotion patterns, protection rules, progressive delivery, and rollback approaches for GitHub Actions pipelines.

## Contents

- Environment promotion patterns
- GitHub environment protection rules
- Progressive delivery
- Rollback strategies
- Deployment anti-patterns

## Environment promotion patterns

Three models dominate. Pick based on how your team thinks about releases.

### Folder-based promotion

Different directories on the same branch represent environments. Promotion means copying config from `envs/staging/` to `envs/production/`.

```yaml
# Simplified structure
envs/
  staging/
    values.yaml
  production/
    values.yaml
```

Works fine for GitOps tools like Argo CD or Flux where the directory structure maps directly to clusters. The downside: you lose Git's merge semantics entirely. Promotion is a file copy, not a merge. Diff review is possible but less natural.

### Branch per environment

Each long-lived branch deploys to its corresponding environment. Merge `develop` into `staging` to promote. Merge `staging` into `main` to hit production.

```yaml
on:
  push:
    branches:
      - staging   # deploys to staging
      - main      # deploys to production
```

Plays nicely with GitHub's branch protection rules since each branch can have independent review requirements. The trap: branch drift. If someone hotfixes `main` without backporting to `staging`, the branches diverge and merge conflicts pile up.

### Release-based promotion

PRs to `main` auto-deploy to staging. Publishing a GitHub Release promotes to production. SemVer tags create a clean audit trail.

```yaml
on:
  push:
    branches: [main]  # -> staging
  release:
    types: [published]  # -> production
```

This is the cleanest model for most teams. The release object captures what changed, who approved it, and when. GitHub's release notes auto-generation pulls from PR titles, which means your changelog writes itself if PRs are well-named.

### Promotion model decision table

| Factor | Folder-based | Branch per env | Release-based |
| --- | --- | --- | --- |
| Git semantics | None (file copy) | Full (merge) | Partial (tag) |
| Audit trail | Weak | Moderate | Strong (SemVer) |
| Branch protection fit | Poor | Strong | Strong |
| Drift risk | Low | High | Low |
| GitOps tool fit | Native | Workable | Good |
| Team complexity ceiling | Small | Medium | Any |
| Rollback clarity | Revert files | Revert merge | Redeploy previous tag |

Release-based wins for most teams. Branch-per-environment works when you need per-environment branch protection with different reviewer sets. Folder-based makes sense when Argo CD or Flux is already wired to a directory structure.

## GitHub environment protection rules

Most teams configure environments and stop at "require a reviewer." There's a lot more here.

### Required reviewers

Up to 6 people or teams. Only one reviewer needs to approve, not all of them. Enable "prevent self-review" for production so the person who triggered the deploy can't rubber-stamp their own work.

### Wait timers

Force a delay between approval and deployment. Useful for bake time after staging deploys. Set 30-60 minutes on production so staging has time to surface issues before production rolls out.

### Branch restrictions

Lock production to `main` only. No feature branches, no hotfix branches deploying directly to production. If you need emergency deploys, create an explicit process rather than loosening restrictions.

### Custom deployment protection rules

The feature most teams don't know exists. Integrate third-party gates from Datadog, Honeycomb, PagerDuty, or ServiceNow. The gate auto-approves or rejects based on external criteria like SLO health, open incidents, or change management tickets. Up to 6 rules per environment.

This turns "did staging actually work?" from a human judgment call into an automated check against real metrics.

### Protection rules in practice

```yaml
jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@<sha>
      - name: Deploy to staging
        run: ./deploy.sh staging

  smoke-test:
    needs: deploy-staging
    runs-on: ubuntu-latest
    steps:
      - name: Run smoke tests against staging
        run: ./smoke-tests.sh https://staging.myapp.com

  deploy-production:
    needs: smoke-test
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://myapp.com
    steps:
      - uses: actions/checkout@<sha>
      - name: Deploy to production
        run: ./deploy.sh production
```

The `environment` key triggers all configured protection rules. The `needs` chain ensures staging deploys and passes smoke tests before production is even eligible. The `url` on the production environment shows up in the GitHub deployments UI, which is small but useful for quick status checks.

## Progressive delivery

For anything running on Kubernetes, GitHub Actions should not own the deployment lifecycle directly. It should trigger it.

### The handoff pattern

GitHub Actions builds and pushes the container image, then updates the GitOps repo with the new image tag. From there:

1. Argo CD detects the manifest change and syncs the cluster
2. Argo Rollouts (or Flagger) manages the traffic shift incrementally
3. Analysis templates query Prometheus/Datadog during the canary window
4. If metrics stay healthy, traffic shifts continue to 100%
5. If SLO violations occur, automatic rollback to the previous ReplicaSet

```yaml
# In your GitHub Actions workflow
jobs:
  build-and-push:
    runs-on: ubuntu-latest
    outputs:
      image-tag: ${{ steps.meta.outputs.tags }}
    steps:
      - uses: actions/checkout@<sha>
      - name: Build and push
        run: |
          docker build -t myapp:${{ github.sha }} .
          docker push registry.example.com/myapp:${{ github.sha }}

  update-gitops:
    needs: build-and-push
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@<sha>
        with:
          repository: my-org/gitops-manifests
          token: ${{ secrets.GITOPS_TOKEN }}
      - name: Update image tag
        run: |
          cd apps/myapp/overlays/production
          kustomize edit set image myapp=registry.example.com/myapp:${{ github.sha }}
      - name: Commit and push
        run: |
          git commit -am "deploy: myapp ${{ github.sha }}"
          git push
```

### Why the separation matters

Argo Rollouts can pause, analyze, and rollback without GitHub Actions involvement. If your CI system is down, rollbacks still work. If a canary fails at 3am, nobody needs to re-run a GitHub Actions workflow. The deployment controller handles it autonomously.

Flagger works similarly but integrates with service mesh traffic splitting (Istio, Linkerd) rather than managing ReplicaSets directly. Pick Argo Rollouts for most cases. Flagger when you already have a service mesh.

## Rollback strategies

Different failure modes need different rollback approaches. Don't default to "just redeploy the old version."

### Rollback approach decision table

| Failure mode | Strategy | Speed | Risk |
| --- | --- | --- | --- |
| Bad application code | GitOps revert | Minutes | Low (proven previous state) |
| Bad config/environment | Image tag rollback | Minutes | Low |
| Bad feature, good code | Feature flag disable | Seconds | Lowest (no deploy needed) |
| Database migration broke queries | Forward-fix migration | Variable | Medium (new migration needed) |
| Cascading downstream failures | Feature flag + traffic drain | Seconds to minutes | Medium |

### GitOps revert

Revert the commit in the GitOps manifests repo. Argo CD picks up the revert and syncs back to the previous known-good state. Cleanest approach because the entire desired state is version-controlled and the revert is itself an auditable commit.

### Image tag rollback

Point the deployment back to the previous known-good image tag. Faster than a full GitOps revert if you just need the old binary running. Works when the infrastructure and config haven't changed, only the application code.

### Feature flag rollback

Disable the feature without redeploying anything. This is the fastest rollback possible and the only one that doesn't require a deployment pipeline to be healthy. Requires investment in a feature flag system (LaunchDarkly, Unleash, Flipt, or even a config map), but the operational payoff is significant.

### Database-aware rollbacks

You cannot roll back a destructive database migration by redeploying old code. The schema has already changed. The pattern that works:

- All migrations must be backward-compatible with the previous application version
- Separate "expand" (add new columns/tables) from "contract" (drop old ones) by at least one deploy cycle
- Never rename columns directly. Add the new name, backfill, deploy code that reads from both, then drop the old name

Forward-only migrations with backward-compatible schemas make application rollbacks safe regardless of database state.

## Deployment anti-patterns

### Deploying without environment gates

Pushing straight to production from CI without environment protection rules means any green build ships. No human review, no automated SLO check, no wait timer for staging bake time. One bad merge and you're live.

### Using `latest` tags for container images

`latest` is mutable. Two different builds can both be `latest`. When Kubernetes pulls `latest`, you have no guarantee which version you get. Always tag with the commit SHA or a build-specific identifier. Immutable tags make rollbacks deterministic.

### Manual deployments alongside automated ones

If some deploys go through the pipeline and others happen via SSH or kubectl, your GitOps state drifts from reality. Argo CD calls this "out of sync" and will either fight the manual change or ignore it depending on your sync policy. Pick one deployment path and enforce it.

### No deployment observability

You deployed successfully (the pipeline is green) but did it actually work? Without post-deploy health checks, error rate monitoring, or canary analysis, a "successful" deploy can silently degrade your service. Every deploy should have an automated signal that confirms the new version is healthy.

### Coupling database migrations to application deployments

Running migrations in the same deployment step as the application rollout means you can't roll back the app without rolling back the database. Since database rollbacks are risky or impossible for destructive changes, this coupling removes your ability to recover quickly. Run migrations as a separate, pre-deployment step with their own success criteria.
