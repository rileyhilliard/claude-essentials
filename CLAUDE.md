# CLAUDE.md

Guidance for working in this repository, the `claude-essentials` marketplace that ships one Claude Code plugin, `ce`.

## Layout

```
.claude-plugin/marketplace.json     # Marketplace catalog: one entry, source ./plugins/ce
docs/
  claude-code-best-practices.md     # Current schema and authoring guidance, with source URLs
  extending-for-projects.md         # How a project layers its own .claude/ on top of ce
plugins/ce/
  .claude-plugin/plugin.json        # name, version, description, author, license
  skills/<name>/SKILL.md            # 10 skills, each with optional references/ and scripts/
  agents/<name>.md                  # 4 agents
```

Claude Code auto-discovers `skills/` and `agents/`, so the manifests don't list components. The plugin name adds the `ce:` prefix; file names and frontmatter use bare names (`writing-tests`, not `ce:writing-tests`), including cross-references inside skills and in an agent's `skills:` field.

## Inventory

| Skill | Purpose |
| --- | --- |
| executing-plans | Plan to merged result: DA review, grouped subagents, tests, code review, local merge |
| post-mortem | Session and multi-session reviews; `scripts/extract-friction.py` builds the transcript digest |
| writer | Voice guide, ten personas, AI-tell catalog in `references/forbidden-patterns.md` |
| structuring-articles | Story structures for long-form prose |
| design | Product UI direction and craft, CSS and Tailwind references |
| planning-products | Product definition before technical planning |
| architecting-systems | Structure, boundaries, coupling, concurrency, observability |
| writing-tests | Testing Trophy, waiting patterns, flaky-test diagnosis |
| handling-errors | Error propagation and logging without silent failures |
| managing-databases | Postgres, DuckDB, Parquet, PGVector, Neo4j, SQL and index patterns |

| Agent | Model | Purpose |
| --- | --- | --- |
| code-reviewer | opus | Flat fix list for a branch diff; preloads handling-errors, writing-tests, architecting-systems |
| devils-advocate | opus | Plan and design critique checked against the code |
| copywriter | opus | Long-form drafting; preloads structuring-articles and writer |
| log-reader | sonnet | Filtered investigation of large logs |

When adding, removing or renaming a component, update both tables here and the tables in README.md, and grep the repo for the old name.

## Formats

Skill frontmatter:

```yaml
---
name: writing-tests          # lowercase, digits, hyphens; max 64; must match the directory
description: Writes ... Use when ...   # third person, what it does and when; max 1024 chars
---
```

Optional fields worth knowing: `disable-model-invocation: true` for workflows with side effects that should only run by hand, `user-invocable: false` for background knowledge, `allowed-tools`, `model`, `effort`, `argument-hint`. Custom commands have been merged into skills, so new workflows go in `skills/`, not `commands/`.

Agent frontmatter:

```yaml
---
name: code-reviewer
description: What it returns and when to use it
tools: Bash, Glob, Grep, Read
model: opus                  # set explicitly: opus for judgment work, sonnet for mechanical work
skills: handling-errors      # preloads the full skill content on every run, so keep it short
color: red                   # red, blue, green, yellow, purple, orange, pink, cyan
---
```

Plugin agents ignore `hooks`, `mcpServers` and `permissionMode`.

Versioning: `version` lives only in `plugins/ce/.claude-plugin/plugin.json`. Bump it on every change that should reach installed copies, and bump the major version when a skill, agent or command is removed or renamed.

## Writing skills

- Keep SKILL.md under 500 lines and put detail in `references/`, linked directly from SKILL.md (one level deep). Give reference files over 100 lines a table of contents.
- Write the description the way the user phrases the request. It is the only text the model sees when deciding whether to load the skill.
- Include only what the model wouldn't do unaided: the user's taste, process, and project-specific gotchas. Generic engineering advice costs context and changes nothing.
- Explain the reason behind a rule instead of emphasizing it. ALL-CAPS, "CRITICAL" and "MUST" over-trigger on current models, and self-verification checklists cause over-verification.
- Opinionated skills open with a line deferring to the repo's own `.claude/rules/` and CLAUDE.md.
- Prose in this repo follows the writer skill: plain and specific, no marketing language, no emoji, and no em dashes.

## Verifying changes

```bash
claude plugin validate --strict .            # marketplace.json
claude plugin validate --strict plugins/ce   # plugin.json and components
```

Also check that each SKILL.md and agent has valid YAML frontmatter with `name` matching its file or directory, and grep for references to anything removed. Invalid skill frontmatter fails silently: the skill loads with no description and never triggers.

## Installation

```bash
/plugin marketplace add https://github.com/rileyhilliard/claude-essentials
/plugin install ce
```
