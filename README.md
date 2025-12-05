# Claude Essentials

A unified development plugin for Claude Code with essential commands, skills, and specialized agents, all accessible under the `ce` namespace.

<img src="/assets/hackerman.gif" width="100%" alt="hackerman">

## What's Included

### Commands

Quick workflows for everyday development tasks, accessed with `/ce:` prefix:

| Command                                           | Description                                           |
| ------------------------------------------------- | ----------------------------------------------------- |
| [/ce:test](plugins/ce/commands/test.md)           | Run tests and analyze failures                        |
| [/ce:explain](plugins/ce/commands/explain.md)     | Break down code or concepts                           |
| [/ce:debug](plugins/ce/commands/debug.md)         | Launch systematic debugging                           |
| [/ce:optimize](plugins/ce/commands/optimize.md)   | Find performance bottlenecks                          |
| [/ce:refactor](plugins/ce/commands/refactor.md)   | Improve code quality                                  |
| [/ce:review](plugins/ce/commands/review.md)       | Get comprehensive code review                         |
| [/ce:commit](plugins/ce/commands/commit.md)       | Generate semantic commit messages                     |
| [/ce:deps](plugins/ce/commands/deps.md)           | Audit and upgrade dependencies                        |
| [/ce:fix-issue](plugins/ce/commands/fix-issue.md) | Fix a GitHub issue by number                          |
| [/ce:pr](plugins/ce/commands/pr.md)               | Create a pull request with auto-generated description |
| [/ce:document](plugins/ce/commands/document.md)   | Create or improve documentation                       |
| [/ce:plan](plugins/ce/commands/plan.md)           | Create a detailed implementation plan                 |

### Skills

Reusable development patterns, accessed with `ce:` prefix:

**Testing & Quality:**

| Skill                                                                                          | Description                                        |
| ---------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| [ce:writing-tests](plugins/ce/skills/writing-tests/SKILL.md)                                   | Testing Trophy methodology, behavior-focused tests |
| [ce:verification-before-completion](plugins/ce/skills/verification-before-completion/SKILL.md) | Verify before claiming success                     |

**Debugging & Problem Solving:**

| Skill                                                                            | Description                                  |
| -------------------------------------------------------------------------------- | -------------------------------------------- |
| [ce:systematic-debugging](plugins/ce/skills/systematic-debugging/SKILL.md)       | Four-phase debugging framework               |
| [ce:condition-based-waiting](plugins/ce/skills/condition-based-waiting/SKILL.md) | Replace race conditions with polling         |
| [ce:reading-logs](plugins/ce/skills/reading-logs/SKILL.md)                       | Efficient log analysis using targeted search |

**Code Quality:**

| Skill                                                                          | Description                                                 |
| ------------------------------------------------------------------------------ | ----------------------------------------------------------- |
| [ce:refactoring-code](plugins/ce/skills/refactoring-code/SKILL.md)             | Behavior-preserving code improvements                       |
| [ce:optimizing-performance](plugins/ce/skills/optimizing-performance/SKILL.md) | Measurement-driven optimization                             |
| [ce:handling-errors](plugins/ce/skills/handling-errors/SKILL.md)               | Error handling best practices                               |
| [ce:migrating-code](plugins/ce/skills/migrating-code/SKILL.md)                 | Safe migration patterns for databases, APIs, and frameworks |

**Planning & Execution:**

| Skill                                                            | Description                          |
| ---------------------------------------------------------------- | ------------------------------------ |
| [ce:writing-plans](plugins/ce/skills/writing-plans/SKILL.md)     | Create detailed implementation plans |
| [ce:executing-plans](plugins/ce/skills/executing-plans/SKILL.md) | Execute plans in controlled batches  |

**Documentation:**

| Skill                                                                                | Description                                             |
| ------------------------------------------------------------------------------------ | ------------------------------------------------------- |
| [ce:documenting-systems](plugins/ce/skills/documenting-systems/SKILL.md)             | Best practices for writing markdown documentation       |
| [ce:documenting-code-comments](plugins/ce/skills/documenting-code-comments/SKILL.md) | Standards for self-documenting code and inline comments |

**Meta Skills:**

| Skill                                                                              | Description                            |
| ---------------------------------------------------------------------------------- | -------------------------------------- |
| [ce:visualizing-with-mermaid](plugins/ce/skills/visualizing-with-mermaid/SKILL.md) | Create professional technical diagrams |

### Agents

Expert AI personas for complex work, accessed with `@ce:` prefix:

| Agent                                                             | Description                                             |
| ----------------------------------------------------------------- | ------------------------------------------------------- |
| [@ce:architect](plugins/ce/agents/architect.md)                   | System design and architectural planning with diagrams  |
| [@ce:code-reviewer](plugins/ce/agents/code-reviewer.md)           | Comprehensive PR/MR reviews enforcing standards         |
| [@ce:commit](plugins/ce/agents/commit.md)                         | Autonomous git specialist for semantic commit messages  |
| [@ce:complex-doc-writer](plugins/ce/agents/complex-doc-writer.md) | Multi-file markdown documentation and architecture docs |
| [@ce:code-commenter](plugins/ce/agents/code-commenter.md)         | Single-file code comment auditing and cleanup           |
| [@ce:log-reader](plugins/ce/agents/log-reader.md)                 | Efficient log file analysis using targeted search       |

### Reference Templates

| Template                                                      | Description                   |
| ------------------------------------------------------------- | ----------------------------- |
| [ADR](plugins/ce/references/adr.md)                           | Architecture Decision Record  |
| [PRD](plugins/ce/references/prd.md)                           | Product Requirements Document |
| [Technical Design](plugins/ce/references/technical-design.md) | Technical Design Document     |

### Hooks

- **Session startup** - Loads user instructions and project context automatically
- **Notifications** - Cross-platform alerts when Claude needs input (macOS + Linux)

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

# Invoke an agent
@ce:architect
```

## Usage Examples

### Typical Workflows

**Fix failing tests:**

```bash
/ce:test
# If complex, escalate:
ce:systematic-debugging
```

**Review before merge:**

```bash
/ce:review
git add .
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
@ce:architect I need to add real-time notifications. We have 10k concurrent users.
# Then create a plan:
ce:writing-plans
```

**Clean up legacy code:**

```bash
/ce:explain src/legacy/payment-processor.js
ce:refactoring-code
```

### Understanding the System

**Commands vs Skills vs Agents:**

- **Commands** (`/ce:test`, `/ce:review`) are quick keyboard shortcuts for routine tasks
- **Skills** (`ce:writing-tests`) are reusable workflows that guide specific development patterns
- **Agents** (`@ce:architect`) are expert personas for complex, multi-step work

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
        ├── commands/             # 12 commands (/ce:test, /ce:plan, etc.)
        ├── skills/               # 14 skills (ce:writing-tests, etc.)
        ├── agents/               # 6 agents (@ce:architect, @ce:commit, etc.)
        ├── hooks/                # Session automation
        └── references/           # Document templates (ADR, PRD, Technical Design)
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
@ce:architect help with authentication

# Better
@ce:architect We need OAuth2 + JWT authentication for a React SPA with Node backend. 50k users.
```

**Run tests first:** Use `/ce:test` before committing to catch issues early.

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
