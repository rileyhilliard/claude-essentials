---
name: preflight-checks
description: Detect and run project linters, formatters, and type checkers before committing or claiming completion. Auto-detects tools from project config files.
---

# Preflight Checks

Run the project's code quality tools before committing. Catch errors early instead of letting pre-commit hooks catch them.

## Execution Order

Run tools in this order. Each step can change code that later steps check.

1. **Formatters** (auto-fix): prettier, black, ruff format, gofmt
2. **Linters** (auto-fix where possible): eslint --fix, ruff check --fix
3. **Type checkers** (manual fix): tsc, mypy, pyright

## Scope

Only check files that are staged or modified. Don't run checks on the entire codebase.

```bash
# Staged files
git diff --cached --name-only --diff-filter=ACM

# Unstaged modified files
git diff --name-only --diff-filter=ACM
```

Filter to relevant extensions for each tool (e.g., only `.ts`/`.tsx` for tsc, only `.py` for ruff).

## Auto-Fix Protocol

1. Run the formatter/linter with its fix flag
2. Re-stage any files that were modified: `git add <fixed-files>`
3. Report what was changed: "Fixed 3 formatting issues in src/auth/login.ts"

