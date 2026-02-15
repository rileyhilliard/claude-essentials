---
name: preflight-checks
description: Detect and run project linters, formatters, and type checkers before committing or claiming completion. Auto-detects tools from project config files.
---

# Preflight Checks

Run the project's code quality tools before committing. Catch errors early instead of letting pre-commit hooks catch them.

## Tool Detection

Detect available tools from project config files. Check in this order:

| Config File | Tool | Check Command | Fix Command |
|-------------|------|---------------|-------------|
| `package.json` scripts | npm/yarn/pnpm | Look for `lint`, `typecheck`, `format`, `check` scripts | Run with `--fix` where available |
| `.eslintrc*` / `eslint.config.*` | ESLint | `npx eslint <files>` | `npx eslint --fix <files>` |
| `tsconfig.json` | TypeScript | `npx tsc --noEmit` | Manual fix required |
| `.prettierrc*` / prettier in package.json | Prettier | `npx prettier --check <files>` | `npx prettier --write <files>` |
| `pyproject.toml` with `[tool.ruff]` | Ruff | `ruff check <files>` | `ruff check --fix <files> && ruff format <files>` |
| `pyproject.toml` with `[tool.mypy]` / `mypy.ini` | mypy | `mypy <files>` | Manual fix required |
| `pyproject.toml` with `[tool.black]` | Black | `black --check <files>` | `black <files>` |
| `.flake8` / `setup.cfg` with `[flake8]` | Flake8 | `flake8 <files>` | Manual fix required |
| `go.mod` | Go | `go vet ./...` | `gofmt -w <files>` |
| `Cargo.toml` | Rust | `cargo clippy` | `cargo clippy --fix` |
| `.pre-commit-config.yaml` | pre-commit | `pre-commit run --files <files>` | Runs auto-fix internally |

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

## When to Run

- Before `git commit` (used by `/ce:commit`)
- Before claiming work is complete
- Before creating a PR (used by `/ce:pr`)

## Failure Handling

Distinguish between fixable and non-fixable errors:

**Fixable (auto-fix and move on):**
- Formatting errors (whitespace, trailing commas, import ordering)
- Simple lint errors with auto-fix support

**Needs human decision (report and stop):**
- Type errors (wrong types, missing properties)
- Complex lint errors without auto-fix
- Test failures
- Errors you don't understand

Never silently skip a failing check.
