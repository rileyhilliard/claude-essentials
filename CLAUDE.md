# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a unified Claude Code plugin (`ce`) that provides development workflows, reusable skills, and specialized agents, all under a consistent `ce` namespace.

**The ce plugin provides:**

- **1 Command** - Project initialization (init)
- **22 Skills** - Reusable patterns for testing, debugging, architecture, planning, writing, and more
- **5 Agents** - Expert AI personas (code-reviewer, haiku, log-reader, devils-advocate, copywriter)
- **Session Hooks** - Automatic project configuration on startup

**Namespace conventions:**

- Commands: `/ce:init`
- Skills: `@skills/ce:writing-tests`, `@skills/ce:systematic-debugging`, `@skills/ce:architecting-systems`, etc.
- Agents: `@ce:code-reviewer`, `@ce:copywriter`, `@ce:haiku`, `@ce:log-reader`, `@ce:devils-advocate`

The `ce:` prefix is automatically added by Claude Code based on the plugin name. Files and YAML frontmatter use simple names without the prefix.

## Plugin Architecture

### Directory Structure

The ce plugin lives in `plugins/ce/` with this structure:

```
plugins/ce/
├── .claude-plugin/
│   └── plugin.json          # Plugin metadata (name: "ce", description, version, author, license)
├── commands/                 # 1 slash command
│   └── init.md              # Accessed as /ce:init
├── skills/                   # 22 skills
│   ├── writing-tests/       # Accessed as @skills/ce:writing-tests
│   │   └── SKILL.md         # name: writing-tests (no ce: prefix in file)
│   ├── architecting-systems/    # Accessed as @skills/ce:architecting-systems
│   │   └── SKILL.md             # System architecture and technical docs
│   └── ...                  # Other skills follow same pattern
├── agents/                   # 5 agents
│   ├── code-reviewer.md     # Accessed as @ce:code-reviewer
│   ├── copywriter.md        # Accessed as @ce:copywriter
│   ├── haiku.md             # Accessed as @ce:haiku
│   ├── log-reader.md        # Accessed as @ce:log-reader
│   └── devils-advocate.md   # Accessed as @ce:devils-advocate
└── hooks/                    # Session hooks
    ├── hooks.json           # Hook configuration
    └── session-start.sh     # Session startup hook
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
model: sonnet
color: blue
---

Agent personality and workflow instructions.
```

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

**Test hook scripts:**

```bash
bash -n plugins/ce/hooks/session-start.sh  # Syntax check
chmod +x plugins/ce/hooks/session-start.sh  # Ensure executable
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

Keep main SKILL.md files under 4,000 words. Split larger content into `references/` directory.

### Session Start Hook

The `ce` plugin includes a `session-start.sh` hook that:

- Loads user instructions from `~/.claude/CLAUDE.md` if present
- Injects instructions as additional context via JSON output
- Uses progressive disclosure (skills loaded on-demand via Skill tool)

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
- condition-based-waiting: Fixes flaky tests by replacing arbitrary timeouts with condition polling. Use when tests fail intermittently, have setTimeout delays, or involve async operations that need proper wait conditions.
- executing-plans: Executes implementation plans autonomously with wave-based parallel subagents. Analyzes task dependencies, parallelizes independent work, auto-recovers from errors, and verifies at completion.
- handling-errors: Error handling best practices - no hiding, no swallowing, no boolean returns. Use when implementing try-catch blocks, designing error propagation, or reviewing error handling patterns.
- optimizing-performance: Measure-first performance optimization - balance gains against complexity. Use when addressing slow code, profiling performance issues, or evaluating optimization trade-offs.
- reading-logs: Efficient log analysis using targeted search, filtering, and iterative refinement. Use when investigating errors, analyzing patterns, or debugging incidents through application logs.
- systematic-debugging: Four-phase debugging framework with root cause tracing - understand the source before proposing fixes. Use when investigating bugs, errors, unexpected behavior, or failed tests.
- visualizing-with-mermaid: Create professional Mermaid diagrams with proper styling and visual hierarchy. Use when creating flowcharts, sequence diagrams, state machines, class diagrams, or architecture visualizations.
- writer: Writing style and tone guide for human-sounding content. Use when writing documentation, READMEs, commit messages, PR descriptions, blog posts, or any user-facing content.
- writing-plans: Create comprehensive, context-aware implementation plans using TDD and Spec-Driven patterns.
- writing-tests: Write behavior-focused tests following Testing Trophy model with real dependencies, avoiding common anti-patterns like testing mocks and polluting production code.
</INSTRUCTION>
<!-- DYNAMIC_SKILLS_END -->
