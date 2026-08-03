# Project-Specific Skill Template (Optional)

When the project has complex domain patterns (APIs, connectors, data schemas), scaffold a project skill:

**skills/{project}-patterns/SKILL.md:**
```markdown
---
name: {project}-patterns
description: Project-specific patterns for {project}. Use when working with {domain} code or implementing new {features}.
---

# {Project} Development Patterns

## Quick Reference

| Pattern | When to Use | Reference |
|---------|-------------|-----------|
| API endpoints | Adding new routes | [references/api.md](references/api.md) |
| Data models | Changing schemas | [references/models.md](references/models.md) |
| Authentication | Auth-related code | [references/auth.md](references/auth.md) |

## Core Conventions

{Brief conventions here, ~50 lines max}

## Detailed Guides

For specific patterns, read the relevant reference file:
- **API patterns**: See [references/api.md](references/api.md)
- **Data models**: See [references/models.md](references/models.md)
```

**skills/{project}-patterns/references/api.md:**
```markdown
# API Patterns

## Contents
- Endpoint structure
- Request validation
- Response formatting
- Error handling

## Endpoint Structure

{Detailed patterns with code examples}
```

**When to generate project skills:**
- Project has 3+ distinct domains (API, auth, data, etc.)
- Existing codebase has conventions that differ from ce:* skill defaults
- Team has documented patterns that should be enforced

**When NOT to generate:**
- Simple projects where ce:* skills cover all patterns
- Greenfield projects without established conventions
- If it would duplicate ce:* skill content
