# Infrastructure as Code Pipelines

Terraform/OpenTofu pipeline patterns that prevent the disasters you don't see coming until `terraform apply` runs against production.

## Contents

- Plan-on-PR, apply-on-merge workflow
- Drift detection
- IaC security scanning layers
- State management gotchas
- Module management
- Anti-patterns

## Plan-on-PR, apply-on-merge workflow

This is the canonical IaC pipeline pattern. Everything else is a variation.

```
PR opened/updated -> fmt/validate/plan -> Plan posted as PR comment -> Review
PR merged to main -> apply (using saved plan artifact) -> Notify
```

The critical rule: save the plan and apply that exact plan. Never run `terraform plan` followed by `terraform apply` without `-out`. The world changes between plan and apply. Another PR merges, an auto-scaler adjusts, someone click-ops a change. Applying without a saved plan means applying something you never reviewed.

### Complete workflow

```yaml
name: Terraform
on:
  pull_request:
    paths: ['infra/**']
  push:
    branches: [main]
    paths: ['infra/**']

permissions: {}

jobs:
  plan:
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
      id-token: write
    steps:
      - uses: actions/checkout@SHA # v4
        with: { persist-credentials: false }
      - uses: hashicorp/setup-terraform@SHA # v3
      - uses: aws-actions/configure-aws-credentials@SHA # v4
        with:
          role-to-assume: ${{ vars.TF_PLAN_ROLE_ARN }}
          aws-region: us-west-2
      - name: Init and validate
        working-directory: infra
        run: |
          terraform init -input=false
          terraform fmt -check -recursive
          terraform validate
      - name: Plan
        working-directory: infra
        run: terraform plan -input=false -out=tfplan
      - uses: actions/upload-artifact@SHA # v4
        with:
          name: tfplan-${{ github.event.pull_request.number }}
          path: infra/tfplan
          retention-days: 5
      - uses: dflook/terraform-github-actions/terraform-plan@v1
        # Post plan as PR comment so reviewers see what changes

  apply:
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    permissions: { contents: read, id-token: write }
    environment: production
    concurrency:
      group: terraform-apply
      cancel-in-progress: false  # Never cancel an in-progress apply
    steps:
      - uses: actions/checkout@SHA # v4
        with: { persist-credentials: false }
      - uses: hashicorp/setup-terraform@SHA # v3
      - uses: aws-actions/configure-aws-credentials@SHA # v4
        with:
          role-to-assume: ${{ vars.TF_APPLY_ROLE_ARN }}
          aws-region: us-west-2
      - name: Init, plan, and apply
        working-directory: infra
        run: |
          terraform init -input=false
          terraform plan -input=false -out=tfplan
          terraform apply -input=false tfplan
```

The apply job re-plans rather than downloading the PR plan artifact. The merge commit is a different ref than the PR head, so the artifact may not match. The PR plan is for human review; the apply plan is for execution.

### State segmentation

Segment state by functional boundary, not geography. "networking", "compute", "database" rather than "us-west", "us-east". Infrastructure changes rarely align to regions. A networking change hits every region. A database schema change is one module regardless of where replicas live.

## Drift detection

Run scheduled workflows that plan against your state and alert when reality doesn't match config. Catches click-ops, manual hotfixes, and changes from other tools.

```yaml
name: Drift Detection
on:
  schedule:
    - cron: '0 2 * * *'

permissions: {}

jobs:
  drift-check:
    runs-on: ubuntu-latest
    permissions: { contents: read, id-token: write }
    strategy:
      matrix:
        module: [networking, compute, database]
    steps:
      - uses: actions/checkout@SHA # v4
      - uses: hashicorp/setup-terraform@SHA # v3
      - name: Check for drift
        working-directory: infra/${{ matrix.module }}
        run: |
          terraform init -input=false
          terraform plan -detailed-exitcode -input=false
          # Exit 0 = no changes | Exit 1 = error | Exit 2 = drift detected
      - if: failure()
        run: echo "Drift detected in ${{ matrix.module }}"
        # Post to Slack, PagerDuty, or create a GitHub issue
```

`-detailed-exitcode` is doing the heavy lifting. Exit code 2 means "plan has changes," which triggers the failure alert. For drift detection with automatic remediation, look at Terramate and env0.

## IaC security scanning layers

Stack these in order. Each catches different problem classes.

| Tool | What it catches |
|------|----------------|
| `terraform fmt -check` | Formatting consistency |
| `terraform validate` | Syntax and provider schema validation |
| Checkov | Misconfigurations (public S3, unencrypted EBS, open security groups) |
| tfsec (now Trivy) | Security-specific static analysis |
| Terrascan | Compliance violations (CIS benchmarks, SOC2, HIPAA) |
| OPA/Conftest | Custom policy-as-code rules for your org |

### Layered scanning workflow

```yaml
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@SHA # v4
      - uses: hashicorp/setup-terraform@SHA # v3
      - name: Format and validate
        working-directory: infra
        run: |
          terraform fmt -check -recursive
          terraform init -input=false -backend=false
          terraform validate
      - uses: bridgecrewio/checkov-action@v12
        with: { directory: infra, quiet: true, framework: terraform }
      - name: Custom policies
        run: |
          terraform -chdir=infra show -json tfplan > plan.json
          conftest test plan.json --policy policy/
```

Conftest with OPA enforces org-specific rules: "no public subnets without approval," "all RDS must use encryption," "tags must include cost-center." Built-in scanners catch generic misconfigs; Conftest catches yours.

## State management gotchas

### Remote backend locking

Multiple CI runs against the same state will corrupt it. Not theoretical. Happens the first time two PRs merge close together.

| Backend | Locking mechanism |
|---------|-------------------|
| S3 | DynamoDB table (must configure separately) |
| GCS | Native object locking |
| Azure Blob | Native blob leasing |
| Terraform Cloud/HCP | Built-in |

If you're on S3 without DynamoDB locking, stop reading and go set that up.

### State contains secrets

State files store resource attributes in plaintext. Database passwords, API keys, TLS private keys, all right there. Encrypt at rest (S3 SSE, GCS CMEK), restrict access with IAM, and never commit state to version control.

### Importing existing resources

`terraform import` brings a resource under management but doesn't generate config. You write the HCL by hand and iterate until `plan` shows no changes. Since Terraform 1.5, `terraform plan -generate-config-out=generated.tf` generates much better initial config. Not perfect, but saves real time.

### State file size

Large monolithic states slow every operation. A 50MB state file means every `plan` downloads, parses, and diffs 50MB. Break into smaller root modules by functional boundary. Each gets its own state, its own lock, and its own blast radius.

## Module management

### Version pinning is non-negotiable

```hcl
# Bad: tracks whatever main points to right now
module "vpc" {
  source = "git::https://github.com/myorg/terraform-aws-vpc.git"
}

# Good: pinned to a specific release
module "vpc" {
  source = "git::https://github.com/myorg/terraform-aws-vpc.git?ref=v2.1.0"
}
```

Unpinned modules are a supply chain risk. A force-push to `main` in the module repo changes what every consumer gets on next `terraform init`. Pin to tags, treat updates as conscious decisions.

### Registry and testing

- Private module registry (Terraform Cloud, Artifactory, S3-backed) for internal modules. Git refs work but lack version discovery.
- Semver for releases. Breaking changes get a major bump.
- Test with Terratest or `terraform-exec` before publishing. At minimum, `terraform plan` against example configs in CI.

## Anti-patterns

| Anti-pattern | Why it's bad | Do this instead |
|-------------|-------------|-----------------|
| Secrets in Terraform variables | State stores them in plaintext | Inject from Vault, Secrets Manager, or `data` sources |
| `apply -auto-approve` on PRs | Applies unreviewed changes | Only on merge to main, only with saved plan |
| Approval before seeing plan | Rubber-stamp without knowing impact | Require approval after plan is posted |
| No targeted planning | Every PR plans every module | Path filtering to plan only modified modules |
| Click-ops alongside IaC | Drift guaranteed | All changes through code, drift detection enforces |
| Monolithic root module | Blast radius is everything | Split by boundary with separate state per module |
