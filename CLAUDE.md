# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a unified Claude Code plugin (`ce`) that provides development workflows, reusable skills, and specialized agents, all under a consistent `ce` namespace.

**The ce plugin provides:**

- **1 Command** - Config audit/bootstrap (setup)
- **17 Skills** - Reusable patterns for testing, debugging, architecture, writing, and more
- **4 Agents** - Expert AI personas (code-reviewer, log-reader, devils-advocate, copywriter)

**Namespace conventions:**

- Commands: `/ce:setup`
- Skills: `@skills/ce:writing-tests`, `@skills/ce:systematic-debugging`, `@skills/ce:architecting-systems`, etc.
- Agents: `@ce:code-reviewer`, `@ce:copywriter`, `@ce:log-reader`, `@ce:devils-advocate`

The `ce:` prefix is automatically added by Claude Code based on the plugin name. Files and YAML frontmatter use simple names without the prefix.

## Plugin Architecture

### Directory Structure

The ce plugin lives in `plugins/ce/` with this structure:

```
plugins/ce/
├── .claude-plugin/
│   └── plugin.json          # Plugin metadata (name: "ce", description, version, author, license)
├── commands/                 # 1 slash command
│   └── setup.md             # Accessed as /ce:setup
├── skills/                   # 17 skills
│   ├── writing-tests/       # Accessed as @skills/ce:writing-tests
│   │   └── SKILL.md         # name: writing-tests (no ce: prefix in file)
│   ├── architecting-systems/    # Accessed as @skills/ce:architecting-systems
│   │   └── SKILL.md             # System architecture and technical docs
│   └── ...                  # Other skills follow same pattern
├── agents/                   # 4 agents
│   ├── code-reviewer.md     # Accessed as @ce:code-reviewer
│   ├── copywriter.md        # Accessed as @ce:copywriter
│   ├── log-reader.md        # Accessed as @ce:log-reader
│   └── devils-advocate.md   # Accessed as @ce:devils-advocate
└── hooks/
    └── hooks.json           # Hook configuration (currently empty)
```

**Key principle**: Files and frontmatter use simple names (e.g., `architecting-systems`, `writing-tests`). Claude Code automatically adds the `ce:` namespace prefix based on the plugin name.

### Plugin Metadata

Every plugin requires `.claude-plugin/plugin.json`:

```json
{
  "name": "plugin-name",
  "description": "What the plugin does",
  "version": "1.0.0",
  "author": {
    "name": "Riley Hilliard"
  },
  "license": "MIT"
}
```

### Marketplace Configuration

The marketplace configuration in `.claude-plugin/marketplace.json` defines the ce plugin.

**Valid plugin fields in marketplace.json:**

- **Metadata**: `name`, `version`, `description`, `author`, `homepage`, `repository`, `license`, `keywords`
- **Component paths**: `commands`, `agents`, `skills`, `hooks`, `mcpServers`
- **Marketplace-specific**: `source`, `category`, `tags`, `strict`

**Important**:

- The `hooks` field, if declared in marketplace.json, must be an **inline object** (not a string path). Alternatively, omit it and let Claude Code auto-discover the `hooks/hooks.json` file in the plugin directory.
- The `references` field is NOT supported in marketplace.json.
- File paths in `commands`, `skills`, and `agents` arrays must NOT include namespace prefixes (e.g., use `./skills/writing-tests` not `./skills/ce:writing-tests`).

### Command Format

Commands in `commands/*.md` use YAML frontmatter:

```markdown
---
description: What the command does
argument-hint: "[optional-args]"
model: sonnet
allowed-tools: Bash, Read, Grep
---

Command instructions here.
Use $ARGUMENTS for user-provided arguments.
```

### Skill Format

Skills in `skills/<skill-name>/SKILL.md` use YAML frontmatter:

```markdown
---
name: skill-name
description: What the skill does and when to use it (max 1024 chars)
---

# Skill Title

Skill instructions using imperative language.
```

**Skill naming conventions:**

- Use gerund form: `writing-tests`, `debugging-code`, `creating-skills`
- Lowercase with hyphens only
- No reserved words ("anthropic", "claude")
- Maximum 64 characters

**Description guidelines:**

- Third person only (injected into system prompt)
- Include WHAT the skill does AND WHEN to use it
- Be specific with key terms and triggers
- Example: "Applies Testing Trophy methodology when writing tests - focuses on behavior over implementation"

### Agent Format

Agents in `agents/*.md` use YAML frontmatter:

```markdown
---
name: agent-name
description: What expertise the agent provides
tools: Read, Grep, Glob, Bash
skills: skill-name-one, skill-name-two
color: blue
---

Agent personality and workflow instructions.
```

Field order: `name, description, tools, model, effort, skills, color`.

- `model` is optional. Omitting it means the agent inherits the session model, which is usually what you want. Pin it only when a specific tier fits the job, as `log-reader` does with `haiku` for grep-driven triage.
- `effort` is optional (`low|medium|high|xhigh|max`). It overrides the session's reasoning effort and is separate from `model`. Omit it by default: capping effort risks under-thinking, so avoid it on agents that review, critique, or hunt for problems.
- `skills` is optional, a comma-separated list of skills the agent should have available.

### Hook Configuration

Hooks in `hooks/hooks.json`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume|clear|compact",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/hooks/script.sh"
          }
        ]
      }
    ]
  }
}
```

## Development Workflow

### Testing Plugin Structure

When making changes to plugin structure:

1. Validate JSON files have correct schema
2. Verify YAML frontmatter is properly formatted
3. Check that hook scripts are executable and have proper shebang
4. Ensure all referenced files exist

### Common Commands

**List plugin structure:**

```bash
find plugins/<plugin-name> -type f
```

**Validate plugin.json:**

```bash
cat plugins/<plugin-name>/.claude-plugin/plugin.json | python -m json.tool
```

**Check hooks configuration:**

```bash
cat plugins/ce/hooks/hooks.json | python -m json.tool
```

**Validate YAML frontmatter in markdown files:**

```bash
head -20 plugins/ce/commands/test.md  # Check frontmatter structure
```

### File Naming Conventions

- Command files: `command-name.md` (kebab-case)
- Skill directories: `skill-name/` (kebab-case)
- Skill files: Always `SKILL.md` (uppercase)
- Reference files: Descriptive names (kebab-case)
- Hook scripts: Descriptive names ending in `.sh`
- Plugin metadata: Always `.claude-plugin/plugin.json`

## Key Design Patterns

### Progressive Disclosure

Skills use three-level progressive disclosure to minimize token usage:

1. **Metadata** - Claude scans name/description first
2. **Markdown body** - Loaded only if skill is selected
3. **Referenced files** - Loaded only when needed during execution

Keep main SKILL.md files under 500 lines. Split larger content into `references/` directory.

### Hooks Output Format

Hooks output JSON to communicate with Claude Code:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "<CRITICAL_USER_INSTRUCTIONS>\n...\n</CRITICAL_USER_INSTRUCTIONS>"
  }
}
```

**Note:** The `additionalContext` field is optional. If there's nothing to inject, omit it from the output.

## Important Constraints

### Plugin Schema Validation

The marketplace validates:

- **Hooks field**: If declared in marketplace.json, must be an inline object with the hook config (not a string path). Hooks are also auto-discovered from `hooks/hooks.json` in the plugin directory.
- **No `references` field**: The `references` key is not allowed in marketplace.json plugin definitions. Reference files can exist in the directory structure but cannot be declared in plugin metadata.
- Valid YAML frontmatter in all markdown files
- JSON files must be valid

### Security

- Hook scripts use `set -euo pipefail` for error safety
- Avoid hardcoded paths (use `${CLAUDE_PLUGIN_ROOT}` for relative paths)
- Shell scripts should handle missing files gracefully

### Shell Script Gotchas

- Tilde (`~`) doesn't expand in all contexts. Use `$HOME` for reliable home directory expansion
- Always quote variables: `"$VAR"` not `$VAR`
- Use `[ -f "$file" ] && [ -s "$file" ]` to check file exists and has content

## Installation

Install the unified ce plugin:

```bash
/plugin marketplace add https://github.com/rileyhilliard/claude-essentials
/plugin install ce
```

## Content Philosophy

- **Commands**: Quick shortcuts for routine tasks (test, commit, review)
- **Skills**: Reusable workflows following proven patterns (testing, debugging, architecture)
- **Agents**: Expert personas for complex multi-step work (code reviewer, log reader)

Skills should focus on teaching patterns, not just executing tasks. Use imperative language and include practical examples with edge cases where relevant.

<!-- DYNAMIC_SKILLS_START -->
### Available Skills (Auto-Generated)

<INSTRUCTION>
Load a skill when the task clearly matches its description. Use Skill(<name>) immediately when you recognize a match — don't wait or evaluate all skills first.

Available skills:

- architecting-systems: Guides clean, scalable system architecture during the build phase. Use when designing modules, defining boundaries, structuring projects, managing dependencies, or preventing tight coupling and brittleness as systems grow.
- design: Enforces precise, minimal design for dashboards and admin interfaces. Use when building SaaS UIs, data-heavy interfaces, or any product needing Jony Ive-level craft.
- executing-plans: Executes implementation plans. Implements directly by default and delegates only for large, genuinely independent tracks of work.
- fixing-flaky-tests: Diagnose and fix tests that pass in isolation but fail when run concurrently. Covers shared state isolation, resource conflicts, and timing-based flakiness.
- handling-errors: Prevents silent failures and context loss in error handling. Use when writing try-catch blocks, designing error propagation, reviewing catch blocks, or implementing Result patterns.
- managing-databases: Guides database architecture for PostgreSQL, DuckDB, Parquet, PGVector, and Neo4j. Use when designing schemas, choosing storage strategies, optimizing queries, configuring vector or graph workloads, or diagnosing performance issues.
- managing-pipelines: Guides GitHub Actions CI/CD architecture, security hardening, and deployment strategies. Use when designing workflows, securing supply chains, optimizing build performance, or configuring deployments.
- optimizing-performance: Measure-first performance optimization that balances gains against complexity. Use when addressing slow code, profiling issues, or evaluating optimization trade-offs.
- planning-products: Defines product features from a PM perspective (JTBD, competitive research, scope negotiation) before technical planning. Use when scoping features, writing product specs, defining user problems, or choosing what to build.
- post-mortem: Review a completed session to extract actionable improvements. Identifies DX friction, documentation gaps, architectural confusion, anti-patterns, process failures, and skill/config improvements. Uses progressive disclosure for targeted investigation types.
- strategy-writer: Produces executive-quality strategic documents in The Economist/HBR style. Use when writing strategy memos, market analysis, business cases, customer research reports, or any document for Product, Design, and Business leaders. Customer-led, evidence-based, narrative-driven.
- structuring-articles: Selects and applies journalistic story structures (WSJ Formula, Inverted Pyramid, Hourglass, Tick-Tock). Use when writing or outlining articles, blog posts, essays, or any narrative prose longer than a few paragraphs.
- systematic-debugging: Debugging framework that finds root causes before proposing fixes. Use when investigating bugs, errors, unexpected behavior, failed tests, or when previous fixes haven't worked.
- visualizing-with-mermaid: Creates professional Mermaid diagrams with semantic styling and visual hierarchy. Use when creating flowcharts, sequence diagrams, state machines, class diagrams, or architecture visualizations.
- writer: Writing style and tone guide for human-sounding content. Use when writing documentation, READMEs, commit messages, PR descriptions, blog posts, LinkedIn posts, social media content, or any user-facing content.
- writing-sql: Staff+ DBA SQL patterns targeting what Claude's defaults miss - multi-column statistics, operator classes, keyset pagination, silent performance anti-patterns. Use when writing complex SQL, reviewing queries, adding indexes, or optimizing slow queries.
- writing-tests: Writes behavior-focused tests using Testing Trophy model with real dependencies. Use when writing tests, choosing test types, or avoiding anti-patterns like testing mocks.
</INSTRUCTION>
<!-- DYNAMIC_SKILLS_END -->
