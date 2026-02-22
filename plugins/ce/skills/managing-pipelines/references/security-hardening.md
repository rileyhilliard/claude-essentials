# CI/CD Security Hardening

Pipeline security is where supply chain attacks actually happen. These patterns address the real attack vectors that have burned real teams, not theoretical risks.

## Contents

- SHA pinning (and the tj-actions catastrophe)
- Least-privilege GITHUB_TOKEN permissions
- The pull_request_target trap
- OIDC keyless cloud authentication
- Artifact attestation and SLSA provenance
- Self-hosted runner security
- Non-obvious attack vectors

## SHA pinning

### The tj-actions supply chain attack (CVE-2025-30066)

Attackers compromised a reviewdog maintainer, pivoted into `tj-actions/changed-files`, and retroactively modified every version tag (v1.0.0 through v44.5.1) to point to malicious code that dumped CI runner memory to workflow logs. Secrets exposed in plaintext. 23,000+ repos impacted, CISA advisory issued.

Tags are mutable pointers. Anyone with write access can move one to a different commit. A SHA is immutable.

### Bad vs good

```yaml
# BAD: tag is a mutable pointer, can be silently moved to malicious code
- uses: actions/checkout@v4

# GOOD: SHA is immutable, comment preserves readability
- uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1
```

Even if the tag moves, your workflow runs the exact commit you audited.

### Automating SHA pin updates

Manually tracking SHA updates is not realistic. Use Dependabot or Renovate.

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: github-actions
    directory: "/"
    schedule:
      interval: weekly
```

Renovate works too and also pins Docker image digests in workflow files.

## Least-privilege GITHUB_TOKEN permissions

### Set org/repo default to read-only

Set Settings > Actions > General > Workflow permissions to "Read repository contents and packages permissions." Then grant explicitly per job.

```yaml
permissions: {}  # Top-level: deny all by default

jobs:
  test:
    runs-on: ubuntu-latest
    permissions:
      contents: read       # Clone the repo
    steps:
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1

  deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write      # Push container image
      id-token: write      # OIDC token for cloud auth
    steps:
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1
```

Job-level permissions override the top-level block entirely. Setting `contents: read` at the job level means the job inherits nothing else from the top level. Forces you to be explicit.

### The fork token pitfall

`pull_request` events from forks get read-only tokens with no secret access. Safe by design. But `pull_request_target` runs in the base repo context with full secret access, even when triggered by a fork PR. This distinction is the root cause of many privilege escalations.

## The pull_request_target trap

This trigger exists so workflows can label PRs, post comments, or update status checks on fork contributions. The problem is people use it to also check out and run the forked code.

### Dangerous: checking out fork code with base repo secrets

```yaml
on: pull_request_target

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      # THIS IS THE VULNERABILITY
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1
        with:
          ref: ${{ github.event.pull_request.head.sha }}
      # Attacker's code now runs with access to base repo secrets
      - run: npm install  # package.json postinstall scripts execute here
```

The attacker submits a PR with a malicious `postinstall` script or test config. The workflow checks out their code and runs it with base repo secrets available.

### Safe alternative 1: split workflows

Use `pull_request` (unprivileged) to run fork code and upload artifacts. Use `workflow_run` (privileged) to consume those artifacts, treating them as untrusted data. The privileged workflow never checks out fork code.

```yaml
# ci.yml: runs on fork code, no secrets
on: pull_request
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1
      - run: npm test
      - uses: actions/upload-artifact@65c4c4a1ddee5b72f698fdd19549f0f0fb45cf08 # v4.6.0
        with: { name: test-results, path: results.json }
```

### Safe alternative 2: label gating

```yaml
on:
  pull_request_target:
    types: [labeled]

jobs:
  integration:
    if: contains(github.event.label.name, 'safe to test')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1
        with:
          ref: ${{ github.event.pull_request.head.sha }}
```

A maintainer with write access reviews the PR diff and applies the label. Not bulletproof (the code could change after labeling), but dramatically reduces attack surface.

## OIDC keyless cloud authentication

Long-lived cloud credentials in GitHub secrets are a liability. They don't expire, they can be exfiltrated, and they grant access from anywhere. OIDC tokens solve all three.

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      id-token: write  # Required for OIDC
      contents: read
    steps:
      - uses: aws-actions/configure-aws-credentials@e3dd6a429d7300a6a4c196c26e071d42e0343502 # v4.0.2
        with:
          role-to-assume: arn:aws:iam::123456789:role/deploy-prod
          aws-region: us-west-2
```

### Granular IAM scoping

The OIDC token includes claims for repository, branch, environment, and workflow. Your IAM policy can enforce all of them:

```json
{
  "Condition": {
    "StringEquals": {
      "token.actions.githubusercontent.com:sub": "repo:myorg/myapp:ref:refs/heads/main:environment:production"
    }
  }
}
```

Only `main` branch of `myorg/myapp` in the `production` environment can assume the deploy role. Compromised feature branches or other repos in the org get nothing.

## Artifact attestation and SLSA provenance

GitHub's artifact attestation uses Sigstore to cryptographically bind build artifacts to their source and build process. Default is SLSA v1.0 Build Level 2 (hosted build service, signed provenance).

```yaml
- uses: actions/attest-build-provenance@1c608d11d69870c2092266b3f9a6f3abbf17002c # v1.4.3
  with:
    subject-path: dist/myapp.tar.gz
```

Consumers verify with:

```bash
gh attestation verify dist/myapp.tar.gz --owner myorg
```

### Reaching Build Level 3

Combine attestation with reusable workflows. When the build runs inside a reusable workflow that callers cannot modify, the build definition is isolated from the triggering project, achieving Build Level 3.

```yaml
jobs:
  build:
    uses: myorg/build-templates/.github/workflows/build.yml@main
    with:
      artifact-name: myapp
```

## Self-hosted runner security

### Never use self-hosted runners with public repos

Anyone can fork a public repo, submit a PR, and execute arbitrary code on your runner. This is not a misconfiguration, it is how the system works. No workaround exists.

### Ephemeral runners are mandatory

Persistent runners accumulate state between jobs. A compromised job can install a backdoor that affects all subsequent jobs. Use ephemeral (single-use) runners that get destroyed after each job. Actions Runner Controller (ARC) on Kubernetes is GitHub's recommended approach.

### Container build isolation

| Approach | Security | Why |
|----------|----------|-----|
| Docker-in-Docker (privileged) | Bad | Privileged pods effectively remove container isolation. The inner Docker daemon has root on the host. |
| kaniko | Good | Builds images in userspace, no daemon, no privileges required |
| buildah | Good | Daemonless, rootless builds. Runs entirely in user namespace |

### Other runner hardening

- Run as non-root user
- Network egress controls (only required registries and APIs)
- Runner groups by trust level (production deploys separate from PR checks)
- Mount workspace as `noexec` where possible

## Non-obvious attack vectors

### GITHUB_ENV and GITHUB_PATH poisoning

Writing to `$GITHUB_ENV` or `$GITHUB_PATH` in one step affects all subsequent steps. If an attacker controls earlier step output (compromised action, malicious PR content interpolated into a `run:` block, poisoned dependency), they can inject:

- `LD_PRELOAD` values that load malicious shared libraries
- `PATH` entries that shadow system binaries with attacker-controlled scripts

Never interpolate untrusted input directly into `run:` blocks. Use intermediate environment variables with explicit sanitization.

### Living off the pipeline

Config files for linters, test runners, and security scanners often execute arbitrary code during initialization. A PR that adds a malicious `.eslintrc.js`, `conftest.py`, `jest.config.ts`, or `.rubocop.yml` achieves code execution without touching any "real" source file. Reviewers rarely scrutinize tooling configs.

### Credential leakage from actions/checkout

Always set `persist-credentials: false` on `actions/checkout`. The default stores git credentials in local git config, readable by any subsequent step or action.

```yaml
- uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1
  with:
    persist-credentials: false
```

### Cache poisoning

The Actions cache is scoped by branch but shared across workflows. A compromised action in a low-privilege workflow (like a linter) can poison the cache. When a higher-privilege workflow (like deploy) restores it, the attacker's payload executes. Treat cache contents as untrusted.

### secrets: inherit leaks everything

```yaml
# BAD: passes ALL org and repo secrets to the called workflow
jobs:
  deploy:
    uses: ./.github/workflows/deploy.yml
    secrets: inherit

# GOOD: explicit secret passing limits blast radius
jobs:
  deploy:
    uses: ./.github/workflows/deploy.yml
    secrets:
      DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
```
