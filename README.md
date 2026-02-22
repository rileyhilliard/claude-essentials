# Claude Essentials

A unified development plugin for Claude Code with essential commands, skills, and specialized agents, all accessible under the `ce` namespace.

<img src="/assets/hackerman.gif" width="100%" alt="hackerman">

## What's Included

### Commands

Quick workflows for everyday development tasks, accessed with `/ce:` prefix:

| Command                                           | Description                                                        |
| ------------------------------------------------- | ------------------------------------------------------------------ |
| [/ce:test](plugins/ce/commands/test.md)           | Run tests and analyze failures                                     |
| [/ce:explain](plugins/ce/commands/explain.md)     | Break down code or concepts                                        |
| [/ce:debug](plugins/ce/commands/debug.md)         | Launch systematic debugging                                        |
| [/ce:optimize](plugins/ce/commands/optimize.md)   | Find performance bottlenecks                                       |
| [/ce:refactor](plugins/ce/commands/refactor.md)   | Improve code quality                                               |
| [/ce:review](plugins/ce/commands/review.md)       | Code review with tracked findings and fix workflow                  |
| [/ce:commit](plugins/ce/commands/commit.md)       | Preflight checks, semantic commit, auto-fix on hook failure        |
| [/ce:deps](plugins/ce/commands/deps.md)           | Audit and upgrade dependencies                                     |
| [/ce:fix-issue](plugins/ce/commands/fix-issue.md) | Fix a GitHub issue by number                                       |
| [/ce:pr](plugins/ce/commands/pr.md)               | Create a pull request with auto-generated description              |
| [/ce:document](plugins/ce/commands/document.md)   | Create or improve documentation                                    |
| [/ce:plan](plugins/ce/commands/plan.md)           | Create a detailed implementation plan                              |
| [/ce:execute](plugins/ce/commands/execute.md)     | Execute an implementation plan from the plans folder               |
| [/ce:init](plugins/ce/commands/init.md)           | Bootstrap repo with .claude/ config (rules, permissions, settings) |
| [/ce:post-mortem](plugins/ce/commands/post-mortem.md) | Review a session to assess execution and extract improvements  |

### Skills

Reusable development patterns, accessed with `ce:` prefix:

**Testing & Quality:**

| Skill                                                                                          | Description                                        |
| ---------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| [ce:writing-tests](plugins/ce/skills/writing-tests/SKILL.md)                                   | Testing Trophy methodology, behavior-focused tests      |
| [ce:verification-before-completion](plugins/ce/skills/verification-before-completion/SKILL.md) | Verify before claiming success                          |
| [ce:preflight-checks](plugins/ce/skills/preflight-checks/SKILL.md)                             | Auto-detect and run project linters/formatters/checkers |

**Debugging & Problem Solving:**

| Skill                                                                            | Description                                   |
| -------------------------------------------------------------------------------- | --------------------------------------------- |
| [ce:systematic-debugging](plugins/ce/skills/systematic-debugging/SKILL.md)       | Four-phase debugging framework                |
| [ce:fixing-flaky-tests](plugins/ce/skills/fixing-flaky-tests/SKILL.md)           | Diagnose and fix tests that fail concurrently |
| [ce:condition-based-waiting](plugins/ce/skills/condition-based-waiting/SKILL.md) | Replace race conditions with polling          |
| [ce:reading-logs](plugins/ce/skills/reading-logs/SKILL.md)                       | Efficient log analysis using targeted search  |

**Code Quality:**

| Skill                                                                          | Description                                                 |
| ------------------------------------------------------------------------------ | ----------------------------------------------------------- |
| [ce:refactoring-code](plugins/ce/skills/refactoring-code/SKILL.md)             | Behavior-preserving code improvements                       |
| [ce:optimizing-performance](plugins/ce/skills/optimizing-performance/SKILL.md) | Measurement-driven optimization                             |
| [ce:handling-errors](plugins/ce/skills/handling-errors/SKILL.md)               | Error handling best practices                               |
| [ce:migrating-code](plugins/ce/skills/migrating-code/SKILL.md)                 | Safe migration patterns for databases, APIs, and frameworks |

**Planning & Execution:**

| Skill                                                                      | Description                                               |
| -------------------------------------------------------------------------- | --------------------------------------------------------- |
| [ce:writing-plans](plugins/ce/skills/writing-plans/SKILL.md)               | Create implementation plans with devils-advocate review   |
| [ce:executing-plans](plugins/ce/skills/executing-plans/SKILL.md)           | Execute plans with mandatory code review                  |
| [ce:architecting-systems](plugins/ce/skills/architecting-systems/SKILL.md) | Clean, scalable system architecture for the build phase |
| [ce:design](plugins/ce/skills/design/SKILL.md)                             | Frontend design skill                                     |

**Documentation & Writing:**

| Skill                                                                                | Description                                                                                               |
| ------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------- |
| [ce:writer](plugins/ce/skills/writer/SKILL.md)                                       | Writing style guide with 7 personas (Architect, Engineer, PM, Marketer, Educator, Contributor, UX Writer) |
| [ce:strategy-writer](plugins/ce/skills/strategy-writer/SKILL.md)                     | Executive-quality strategic documents in Economist/HBR style                                              |
| [ce:documenting-systems](plugins/ce/skills/documenting-systems/SKILL.md)             | Best practices for writing markdown documentation                                                         |
| [ce:documenting-code-comments](plugins/ce/skills/documenting-code-comments/SKILL.md) | Standards for self-documenting code and inline comments                                                   |

**Data & Infrastructure:**

| Skill                                                                      | Description                                                         |
| -------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| [ce:managing-databases](plugins/ce/skills/managing-databases/SKILL.md)     | PostgreSQL, DuckDB, Parquet, and PGVector architecture              |
| [ce:managing-pipelines](plugins/ce/skills/managing-pipelines/SKILL.md)     | GitHub Actions CI/CD security, performance, and deployment patterns |

**Meta Skills:**

| Skill                                                                              | Description                                      |
| ---------------------------------------------------------------------------------- | ------------------------------------------------ |
| [ce:visualizing-with-mermaid](plugins/ce/skills/visualizing-with-mermaid/SKILL.md) | Create professional technical diagrams              |
| [ce:post-mortem](plugins/ce/skills/post-mortem/SKILL.md)                           | Review sessions to extract actionable improvements  |
| [ce:configuring-claude](plugins/ce/skills/configuring-claude/SKILL.md)             | Best practices for writing skills, rules, CLAUDE.md |

### Agents

Expert AI personas for complex work, accessed with `@ce:` prefix:

| Agent                                                       | Description                                          |
| ----------------------------------------------------------- | ---------------------------------------------------- |
| [@ce:code-reviewer](plugins/ce/agents/code-reviewer.md)     | Comprehensive PR/MR reviews enforcing standards      |
| [@ce:haiku](plugins/ce/agents/haiku.md)                     | Lightweight Haiku agent for simple delegated tasks   |
| [@ce:log-reader](plugins/ce/agents/log-reader.md)           | Efficient log file analysis using targeted search    |
| [@ce:devils-advocate](plugins/ce/agents/devils-advocate.md) | Rigorous critique to find flaws in plans and designs |

### Hooks

- **Session start** - Auto-detects project tooling (linters, formatters, type checkers) and injects available skills
- **Notifications** - Cross-platform alerts when Claude needs input, with git branch info (macOS + Linux)

---

## Installation

### Prerequisites

You need Claude Code installed. If you don't have it yet, head to [claude.com/product/claude-code](https://www.claude.com/product/claude-code).

### Setup

1. Add this marketplace to Claude Code:

```bash
/plugin marketplace add https://github.com/rileyhilliard/claude-essentials
```

2. Install the ce plugin:

```bash
/plugin install ce
```

That's it! You now have access to all commands, skills, and agents under the `ce` namespace.

### Verify Installation

Start Claude Code and try these:

```bash
# Start Claude Code
claude

# Try a quick command
/ce:explain README.md

# Use a skill
ce:writing-tests

# Use a skill
ce:architecting-systems
```

---

## Bootstrapping Your Repository

The `/ce:init` command sets up your repository with Claude Code configuration that follows best practices. This is the recommended first step when starting work on any project.

### What It Does

**Fresh repositories** (no `.claude/` directory):

1. Detects your project stack (Python, TypeScript, Rust, Go, etc.)
2. Generates a complete `.claude/` configuration:

```
.claude/
├── CLAUDE.md           # Project overview, architecture, quick commands
├── settings.json       # Permissions tailored to your stack
└── rules/
    ├── testing.md          # References ce:writing-tests
    ├── error-handling.md   # References ce:handling-errors
    ├── debugging.md        # References ce:systematic-debugging
    ├── verification.md     # References ce:verification-before-completion
    └── {stack}/            # Stack-specific rules (python/, frontend/, etc.)
```

**Existing configurations** (`.claude/` already exists):

1. Audits your current setup against best practices
2. Identifies missing skill references in rules
3. Suggests permission and rule improvements
4. Offers to apply fixes with your confirmation

### Quick Start

```bash
# Initialize a new project
/ce:init

# Audit an existing configuration
/ce:init --audit

# Force regenerate (overwrites existing)
/ce:init --force
```

### Why This Matters

The generated configuration:

- **Progressive disclosure** - Rules stay concise (<100 lines), reference ce:\* skills for depth, use `references/` subdirectories for domain-specific details
- **Rules reference ce:\* skills** - Don't duplicate content, point to proven patterns
- **Permissions are stack-aware** - Python projects get `uv`, `pytest`; Node gets `npm`, `bun`, etc.
- **Safety defaults included** - Blocks `rm -rf`, force pushes, hard resets
- **Path-scoped rules** - Activate only when working in relevant files

**Progressive disclosure structure:**

```
rules/
├── testing.md              # ~50 lines, points to ce:writing-tests
└── api/
    ├── conventions.md      # ~100 lines, overview
    └── references/         # Loaded on-demand
        ├── errors.md       # Detailed error patterns
        └── pagination.md   # Pagination strategies
```

This keeps context small while maintaining depth. Claude loads reference files only when needed.

Based on [Claude platform best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).

---

## Usage Examples

### Typical Workflows

**Bootstrap a new project:**

```bash
cd my-project
/ce:init
# Review the generated config, confirm, done
```

**Fix failing tests:**

```bash
/ce:test
# If complex, escalate:
ce:systematic-debugging
```

**Review before merge:**

```bash
/ce:review
# Review findings are tracked as a checklist, fix issues, then:
/ce:commit
```

**Optimize performance:**

```bash
/ce:optimize src/components/DataTable.tsx
# For deep analysis:
ce:optimizing-performance
```

**Plan a feature:**

```bash
ce:architecting-systems I need to add real-time notifications. We have 10k concurrent users.
# Then create a plan:
ce:writing-plans
```

**Clean up legacy code:**

```bash
/ce:explain src/legacy/payment-processor.js
ce:refactoring-code
```

**Review a session for improvements:**

```bash
/ce:post-mortem
# Analyzes what happened, identifies friction, proposes concrete actions
```

### Understanding the System

**Commands vs Skills vs Agents:**

- **Commands** (`/ce:test`, `/ce:review`) are quick keyboard shortcuts for routine tasks
- **Skills** (`ce:writing-tests`) are reusable workflows that guide specific development patterns
- **Agents** (`@ce:code-reviewer`) are expert personas for complex, multi-step work

Use commands for quick actions, skills for following proven patterns, and agents when you need specialized expertise.

## Customization

All components are just markdown files organized in directories. Want to customize? Edit them directly in `~/.claude/plugins/ce/`.

### Creating Your Own Command

Add a markdown file to `~/.claude/plugins/ce/commands/`:

```markdown
---
description: Your command description
argument-hint: "[optional-arg]"
allowed-tools: Bash, Read
---

Your command instructions here.
```

This will be accessible as `/ce:your-command`.

### Creating Your Own Skill

Add a directory with SKILL.md to `~/.claude/plugins/ce/skills/`:

```markdown
---
name: my-skill
description: What this skill does and when to use it
---

# Skill Instructions

Your skill workflow here.
```

This will be accessible as `ce:my-skill`.

### Creating Your Own Agent

Add a markdown file to `~/.claude/plugins/ce/agents/`:

```markdown
---
name: my-agent
description: Expert at specific domain
tools: Read, Grep, Glob, Bash
color: blue
---

Your agent personality and workflow here.
```

This will be accessible as `@ce:my-agent`.

## Project Structure

```
~/.claude/
├── CLAUDE.md              # Communication guidelines (copy here manually)
└── plugins/
    └── ce/
        ├── .claude-plugin/
        │   └── plugin.json       # Plugin metadata
        ├── commands/             # 15 commands (/ce:test, /ce:plan, /ce:post-mortem, etc.)
        ├── skills/               # 23 skills (ce:writing-tests, ce:preflight-checks, etc.)
        ├── agents/               # 4 agents (@ce:code-reviewer, @ce:haiku, etc.)
        └── hooks/                # Session automation
```

## Tips

**Commands accept arguments:** Most commands work with optional parameters.

```bash
/ce:test pytest tests/unit
/ce:explain AuthController
/ce:optimize src/components/
```

**Skills are for learning:** Invoke a skill to understand a pattern, then apply it.

```bash
ce:writing-tests
# Follow the guidance to write tests
```

**Agents need context:** Give agents rich context for better results.

```bash
# Vague
ce:architecting-systems help with authentication

# Better
ce:architecting-systems We need OAuth2 + JWT authentication for a React SPA with Node backend. 50k users.
```

**Run tests first:** Use `/ce:test` before committing to catch issues early.

## Documentation

- [Extending for Projects](docs/extending-for-projects.md) - How to wrap and extend ce for your specific codebase

## Contributing

Found a bug? Have an idea? Contributions welcome.

1. Fork this repo
2. Create a feature branch
3. Test your changes locally
4. Submit a PR with details

Ideas for contributions:

- New commands for common workflows
- Additional skills for specific patterns
- Specialized agents for other domains
- Documentation improvements

## Resources

- [Claude Code](https://www.claude.com/product/claude-code)
- [Claude API Docs](https://docs.anthropic.com/)
- [Model Context Protocol](https://modelcontextprotocol.io/)

## License

MIT - Use it, share it, make it better.
