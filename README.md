# Claude Essentials

A unified development plugin for Claude Code with essential commands, skills, and specialized agents, all accessible under the `ce` namespace.

## What This Is

This is a single, comprehensive plugin (`ce`) that provides:

- **7 Commands** - Quick workflows accessible as `/ce:test`, `/ce:explain`, `/ce:commit`, etc.
- **12 Skills** - Reusable development patterns accessed via `ce:writing-tests`, `ce:systematic-debugging`, etc.
- **3 Agents** - Expert AI personas invoked as `@ce:architect`, `@ce:code-reviewer`, `@ce:documentation-writer`
- **Session Hooks** - Automatic project configuration on startup
- **Reference Templates** - ADR, PRD, and technical design templates

Everything unified under the `ce` namespace for clean, consistent developer experience.

## Quick Start

### Prerequisites

You need Claude Code installed. If you don't have it yet, head to [claude.com/product/claude-code](https://www.claude.com/product/claude-code).

### Installation

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

## What's Included

### Commands

Quick workflows for everyday development tasks, accessed with `/ce:` prefix:

- `/ce:test [command]` - Run tests and analyze failures
- `/ce:explain <target>` - Break down code or concepts
- `/ce:debug` - Launch systematic debugging
- `/ce:optimize <target>` - Find performance bottlenecks
- `/ce:refactor <target>` - Improve code quality
- `/ce:review` - Get comprehensive code review
- `/ce:commit` - Generate semantic commit messages

### Skills

Reusable development patterns, accessed with `ce:` prefix:

**Testing & Quality:**
- `ce:writing-tests` - Testing Trophy methodology, behavior-focused tests
- `ce:verification-before-completion` - Verify before claiming success

**Debugging & Problem Solving:**
- `ce:systematic-debugging` - Four-phase debugging framework
- `ce:condition-based-waiting` - Replace race conditions with polling

**Code Quality:**
- `ce:refactoring-code` - Behavior-preserving code improvements
- `ce:optimizing-performance` - Measurement-driven optimization
- `ce:handling-errors` - Error handling best practices

**Planning & Execution:**
- `ce:writing-plans` - Create detailed implementation plans
- `ce:executing-plans` - Execute plans in controlled batches

**Meta Skills:**
- `ce:creating-claude-skills` - Best practices for authoring skills
- `ce:dispatching-parallel-agents` - Investigate independent problems concurrently
- `ce:visualizing-with-mermaid` - Create professional technical diagrams

### Agents

Expert AI personas for complex work, accessed with `@ce:` prefix:

- `@ce:architect` - System design and architectural planning with diagrams
- `@ce:code-reviewer` - Comprehensive PR/MR reviews enforcing standards
- `@ce:documentation-writer` - Clear, practical documentation

### Reference Templates

- ADR (Architecture Decision Record)
- PRD (Product Requirements Document)
- Technical Design Document

### Hooks

- **Session startup** - Loads user instructions and project context automatically
- **Notifications** - Cross-platform alerts when Claude needs input (macOS + Linux)

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
        ├── commands/             # 7 commands (/ce:test, /ce:explain, etc.)
        ├── skills/               # 12 skills (ce:writing-tests, etc.)
        ├── agents/               # 3 agents (@ce:architect, etc.)
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
