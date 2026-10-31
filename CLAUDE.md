# CLAUDE.md

Guidance for working in this repository, the `claude-essentials` marketplace that ships one plugin, `ce`, to Claude Code and to Codex from the same files.

## Layout

```
.claude-plugin/marketplace.json     # Claude Code marketplace catalog: one entry, source ./plugins/ce
.agents/plugins/marketplace.json    # Codex marketplace catalog: the same entry
docs/
  claude-code-best-practices.md     # Current schema and authoring guidance, with source URLs
  extending-for-projects.md         # How a project layers its own .claude/ on top of ce
plugins/ce/
  .claude-plugin/plugin.json        # Claude Code manifest: name, version, description, author, license
  .codex-plugin/plugin.json         # Codex manifest: same name and version, "skills": "./skills/", interface
  skills/<name>/SKILL.md            # 11 skills, each with optional references/, scripts/ and agents/openai.yaml
  agents/<name>.md                  # 4 agents (Claude Code only)
scripts/check-manifests.sh          # Fails when the two manifests' name or version differ
```

Both agents read the same `skills/` tree; only the manifests are per agent. Claude Code auto-discovers `skills/` and `agents/`, so the manifests don't list components. Codex reads `skills/` through its manifest and ignores `agents/`, whose frontmatter is Claude Code's; a Codex delegate can still run an agent's body as a plain prompt. A skill's optional `agents/openai.yaml` holds Codex-only settings: `policy: allow_implicit_invocation: false` keeps a workflow with side effects (`executing-plans`, `post-mortem`) from loading on its own in Codex, where a delegate must not commit or merge. The plugin name adds the `ce:` prefix; file names and frontmatter use bare names (`writing-tests`, not `ce:writing-tests`), including cross-references inside skills and in an agent's `skills:` field.

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
| effect | Effect 4 against the installed release: old-major renames, where the installed docs live, and per-topic references |

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

Versioning: `version` lives in both `plugins/ce/.claude-plugin/plugin.json` and `plugins/ce/.codex-plugin/plugin.json`, and `scripts/check-manifests.sh` fails when they differ. Bump both on every change that should reach installed copies, and bump the major version when a skill, agent or command is removed or renamed.

## Writing skills

- Keep SKILL.md under 500 lines and put detail in `references/`, linked directly from SKILL.md (one level deep). Give reference files over 100 lines a table of contents.
- Write the description the way the user phrases the request. It is the only text the model sees when deciding whether to load the skill.
- Include only what the model wouldn't do unaided: the user's taste, process, and project-specific gotchas. Generic engineering advice costs context and changes nothing.
- Explain the reason behind a rule instead of emphasizing it. ALL-CAPS, "CRITICAL" and "MUST" over-trigger on current models, and self-verification checklists cause over-verification.
- Opinionated skills open with a line deferring to the repo's own `.claude/rules/` and CLAUDE.md.
- Write skills so either agent can follow them: say what to do ("read the file", "search for the declaration"), not which Claude Code tool to call, and put agent-specific settings in frontmatter the other agent ignores or in `agents/openai.yaml`.
- Point at sources that stay current (installed package docs, the vendor's own guides) instead of copying details that change with each release, and mark any remaining version-specific behavior as observed in a named release.
- Prose in this repo follows the writer skill: plain and specific, no marketing language, no emoji, and no em dashes.

## Verifying changes

```bash
claude plugin validate --strict .            # marketplace.json
claude plugin validate --strict plugins/ce   # plugin.json and components
scripts/check-manifests.sh                   # Claude Code and Codex manifests agree
```

Also check that each SKILL.md and agent has valid YAML frontmatter with `name` matching its file or directory, and grep for references to anything removed. Invalid skill frontmatter fails silently: the skill loads with no description and never triggers.

## Installation

```bash
/plugin marketplace add https://github.com/rileyhilliard/claude-essentials
/plugin install ce
```

Codex:

```bash
codex plugin marketplace add rileyhilliard/claude-essentials
codex plugin add ce@claude-essentials
```
