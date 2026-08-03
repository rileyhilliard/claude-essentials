---
description: Audit or bootstrap Claude Code configuration for a repository
argument-hint: "[--audit | --force]"
allowed-tools: Bash, Read, Write, Glob, Grep, AskUserQuestion, Skill
---

Audit an existing `.claude/` configuration, or bootstrap one for a repository that has none.

**Audit-first:** Most repos this command runs in already have a `.claude/` setup. When the existing configuration is already developed (CLAUDE.md with real content plus rules or settings), bail out early with a short summary of what exists and only the suggestions that are genuinely high-value — report what actually matters, don't pad the list — do NOT regenerate or restructure a working setup. Full generation only happens on repos with no `.claude/` or with `--force`.

**Before generating or auditing any files**, review the project's existing `.claude/` structure and follow Claude Code best practices for writing rules, CLAUDE.md, and skills.

Arguments:

- `$ARGUMENTS`: Optional flags
  - `--audit`: Only analyze existing config, report improvements
  - `--force`: Overwrite existing files without confirmation

## Mode Detection

1. Check if `.claude/` directory exists
2. If exists AND no `--force`: Run **Audit Mode**
   - If the config is developed (non-trivial CLAUDE.md and rules/ or settings.json), summarize and stop after Step 3's report — apply fixes only if the user asks
3. If not exists OR `--force`: Run **Fresh Init Mode**

> Note: this command was previously `/ce:init`. It was renamed to `/ce:setup` to avoid colliding with Claude Code's built-in `/init`.

---

## Configuration Best Practices

All generated files (rules, CLAUDE.md, skills) should follow these principles:

- Rules reference ce:* skills rather than duplicating skill content
- Main files stay concise; split large content into `references/` subdirectories
- References are always one level deep (no nested references)

---

## Fresh Init Mode

### Step 1: Detect Stack

Check for manifest files in the repository root:

| File | Stack | Test Framework |
|------|-------|----------------|
| `pyproject.toml` or `requirements.txt` | Python | pytest |
| `package.json` | Node.js/TypeScript | vitest, jest |
| `Cargo.toml` | Rust | cargo test |
| `go.mod` | Go | go test |
| `pom.xml` or `build.gradle` | Java/Kotlin | JUnit |
| `Gemfile` | Ruby | RSpec |

For Node.js projects, also check:
- `tsconfig.json` -> TypeScript
- `package.json` dependencies for `react` -> React
- `vite.config.*` -> Vite
- `next.config.*` -> Next.js

For monorepos, check:
- `packages/` or `apps/` directories
- `workspaces` field in package.json
- Multiple manifest files in subdirectories

### Step 2: Read Project Metadata

Extract from detected manifest:
- Project name
- Description
- Scripts/commands (test, lint, build)
- Dependencies (for framework detection)

### Step 3: Build Generation Plan

Based on detected stack, prepare:

**CLAUDE.md** content:
- Project name and description
- Architecture section (if monorepo or multiple directories)
- Quick commands from package scripts
- Prerequisites (detected package managers)

**settings.json** content:
- `_readme` explaining the file
- `permissions.allow` based on stack (see Permission Mappings below)
- `permissions.ask` with safety defaults

**rules/** content:
- Universal rules (always generate)
- Stack-specific rules (based on detection)

### Step 4: Present Plan and Confirm

Show the user what will be created:

**Simple project (minimal structure):**
```
Detected stack: Python + pytest

Will create:
  .claude/
  ├── CLAUDE.md                 # Project overview
  ├── settings.json             # Permissions for: uv, pytest, git
  └── rules/
      ├── testing.md            # -> ce:writing-tests
      ├── error-handling.md     # -> ce:handling-errors
      ├── debugging.md          # -> ce:systematic-debugging
      └── python/
          └── testing.md        # pytest patterns
```

**Complex project (with references for progressive disclosure):**
```
Detected stack: TypeScript + React + FastAPI backend

Will create:
  .claude/
  ├── CLAUDE.md                 # Project overview, architecture
  ├── settings.json             # Permissions for: npm, uv, pytest, git
  └── rules/
      ├── testing.md            # -> ce:writing-tests
      ├── error-handling.md     # -> ce:handling-errors
      ├── debugging.md          # -> ce:systematic-debugging
      ├── frontend/
      │   ├── testing.md        # vitest + msw patterns
      │   └── react.md          # component patterns
      └── api/
          ├── conventions.md    # API patterns overview
          └── references/       # Detailed docs (loaded on-demand)
              ├── errors.md     # Error response formats
              └── endpoints.md  # Endpoint patterns
```

Use `AskUserQuestion` to confirm before writing files.

### Step 5: Generate Files

Write all files using the templates in the Templates section below.

---

## Audit Mode

### Step 1: Read Existing Configuration

- Read `.claude/CLAUDE.md`
- Read `.claude/settings.json`
- Glob `.claude/rules/**/*.md`

### Step 2: Analyze Against Best Practices

Use Claude Code best practices as the baseline for what "good" looks like. Check for:

**Missing skill references in rules:**
- Rules should reference ce:* skills for detailed guidance
- Example: testing.md should mention `ce:writing-tests`

**Permission gaps:**
- Compare allowed commands against detected stack
- Check for missing common patterns

**Missing universal rules:**
- testing.md, error-handling.md, debugging.md

**Missing stack-specific rules:**
- Python project without python/testing.md
- TypeScript project without frontend/testing.md

**Progressive disclosure violations:**
- Files over 500 lines that should be split into references/
- Nested references (references pointing to other references)
- Duplicated content that should reference a ce:* skill instead
- Large inline code examples that should be in references/

### Step 3: Generate Audit Report

```
Audit of .claude/ configuration:

Good:
  + CLAUDE.md exists with project overview
  + settings.json has reasonable permissions
  + Rules properly reference ce:* skills

Suggestions:
  - rules/testing.md: Add reference to ce:writing-tests skill
  - Missing: rules/python/testing.md for detected Python code
  - settings.json: Add "Bash(uv run pytest:*)" to allow list

Progressive disclosure issues:
  - rules/api/endpoints.md: 847 lines, consider splitting into references/
  - rules/frontend/components.md: Duplicates ce:design skill content
  - skills/my-skill/references/nested/deep.md: References should be one level deep

Apply suggestions? [Y/n/select]
```

### Step 4: Apply Fixes (if confirmed)

For each accepted suggestion, make the appropriate edit or create the missing file.

---

## Templates

Load the relevant reference when generating or applying files:

| Generating... | Load | File |
|----------------|------|------|
| CLAUDE.md, settings.json, universal or stack-specific rules, rules with references | **Rule Templates** | `references/rule-templates.md` |
| An optional project-specific skill (complex domains only) | **Project Skill Template** | `references/project-skill-template.md` |

---

## Permission Mappings

| Stack | Permissions to Add |
|-------|-------------------|
| Python | `Bash(uv:*)`, `Bash(uv run:*)`, `Bash(python:*)`, `Bash(python3:*)`, `Bash(pip:*)` |
| Node.js | `Bash(npm:*)`, `Bash(npx:*)`, `Bash(node:*)` |
| Bun | `Bash(bun:*)`, `Bash(bunx:*)` |
| Yarn | `Bash(yarn:*)` |
| pnpm | `Bash(pnpm:*)`, `Bash(pnpx:*)` |
| Rust | `Bash(cargo:*)`, `Bash(rustc:*)` |
| Go | `Bash(go:*)` |
| Docker | `Bash(docker:*)`, `Bash(docker-compose:*)` |

---

## Examples

| Command | Result |
|---------|--------|
| `/ce:setup` on new Python project | Creates .claude/ with Python rules |
| `/ce:setup` on developed config | Summarizes existing setup, bails with top suggestions |
| `/ce:setup --force` on existing config | Overwrites with fresh config |
| `/ce:setup --audit` | Only reports issues, no changes |
